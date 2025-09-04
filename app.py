import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///movies.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models and create tables
    import models
    from recommendation_engine import RecommendationEngine
    from data_loader import DataLoader
    
    db.create_all()
    
    # Initialize recommendation engine
    rec_engine = RecommendationEngine()
    data_loader = DataLoader()
    
    # Load initial data if database is empty
    if models.Movie.query.count() == 0:
        logging.info("Loading initial Netflix data...")
        data_loader.load_netflix_data()

@app.route('/')
def index():
    """Homepage with movie search and selection"""
    return render_template('index.html')

@app.route('/group')
def group():
    """Group recommendation page"""
    return render_template('group.html')

@app.route('/api/movies/search')
def search_movies():
    """Search movies by title"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Query parameter q is required'}), 400
        
        movies = models.Movie.query.filter(
            models.Movie.title.ilike(f'%{query}%')
        ).limit(10).all()
        
        results = []
        for movie in movies:
            results.append({
                'id': movie.id,
                'title': movie.title,
                'type': movie.content_type,
                'director': movie.director,
                'cast': movie.cast,
                'country': movie.country,
                'release_year': movie.release_year,
                'rating': movie.rating,
                'duration': movie.duration,
                'genres': movie.listed_in.split(',') if movie.listed_in else [],
                'description': movie.description
            })
        
        return jsonify({'results': results})
    
    except Exception as e:
        logging.error(f"Error searching movies: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/recommend')
def recommend():
    """Get recommendations based on a movie title"""
    try:
        title = request.args.get('title', '').strip()
        if not title:
            return jsonify({'error': 'Title parameter is required'}), 400
        
        # Find the content
        movie = models.Movie.query.filter(
            models.Movie.title.ilike(f'%{title}%')
        ).first()
        
        if not movie:
            return jsonify({'error': f'Movie "{title}" not found'}), 404
        
        # Get recommendations
        recommendations = rec_engine.get_content_based_recommendations(movie.id, limit=5)
        
        results = []
        for rec_movie in recommendations:
            results.append({
                'id': rec_movie.id,
                'title': rec_movie.title,
                'type': rec_movie.content_type,
                'director': rec_movie.director,
                'cast': rec_movie.cast,
                'country': rec_movie.country,
                'release_year': rec_movie.release_year,
                'rating': rec_movie.rating,
                'duration': rec_movie.duration,
                'genres': rec_movie.listed_in.split(',') if rec_movie.listed_in else [],
                'description': rec_movie.description
            })
        
        return jsonify({
            'source_movie': {
                'id': movie.id,
                'title': movie.title,
                'type': movie.content_type,
                'director': movie.director,
                'cast': movie.cast,
                'country': movie.country,
                'release_year': movie.release_year,
                'rating': movie.rating,
                'duration': movie.duration,
                'genres': movie.listed_in.split(',') if movie.listed_in else [],
                'description': movie.description
            },
            'recommendations': results
        })
    
    except Exception as e:
        logging.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/group_recommend', methods=['POST'])
def group_recommend():
    """Get group recommendations based on multiple movie titles"""
    try:
        data = request.get_json()
        if not data or 'titles' not in data:
            return jsonify({'error': 'JSON body with titles array is required'}), 400
        
        titles = data['titles']
        if not isinstance(titles, list) or len(titles) == 0:
            return jsonify({'error': 'titles must be a non-empty array'}), 400
        
        # Find movies
        movie_ids = []
        found_movies = []
        
        for title in titles:
            movie = models.Movie.query.filter(
                models.Movie.title.ilike(f'%{title}%')
            ).first()
            
            if movie:
                movie_ids.append(movie.id)
                found_movies.append({
                    'id': movie.id,
                    'title': movie.title,
                    'poster_url': movie.poster_url
                })
        
        if not movie_ids:
            return jsonify({'error': 'No movies found for the provided titles'}), 404
        
        # Get group recommendations
        recommendations = rec_engine.get_group_recommendations(movie_ids, limit=5)
        
        results = []
        for rec_movie in recommendations:
            results.append({
                'id': rec_movie.id,
                'title': rec_movie.title,
                'type': rec_movie.content_type,
                'director': rec_movie.director,
                'cast': rec_movie.cast,
                'country': rec_movie.country,
                'release_year': rec_movie.release_year,
                'rating': rec_movie.rating,
                'duration': rec_movie.duration,
                'genres': rec_movie.listed_in.split(',') if rec_movie.listed_in else [],
                'description': rec_movie.description
            })
        
        return jsonify({
            'source_movies': found_movies,
            'recommendations': results
        })
    
    except Exception as e:
        logging.error(f"Error getting group recommendations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/recommendations')
def recommendations_page():
    """Recommendations results page"""
    return render_template('recommendations.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
