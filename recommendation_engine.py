import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from models import Movie
from app import db

class RecommendationEngine:
    """Content-based recommendation engine using cosine similarity"""
    
    def __init__(self):
        self.movies_df = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self._load_data()
    
    def _load_data(self):
        """Load movie data and compute similarity matrix"""
        try:
            # Get all movies from database
            movies = Movie.query.all()
            
            if not movies:
                logging.warning("No movies found in database")
                return
            
            # Create DataFrame
            movie_data = []
            for movie in movies:
                # Combine genres and description for content-based filtering
                content = ""
                if movie.listed_in:
                    content += movie.listed_in.replace(',', ' ')
                if movie.description:
                    content += " " + movie.description
                if movie.cast:
                    content += " " + movie.cast.replace(',', ' ')
                if movie.director:
                    content += " " + movie.director
                
                movie_data.append({
                    'id': movie.id,
                    'title': movie.title,
                    'content': content.strip(),
                    'genres': movie.listed_in or '',
                    'type': movie.content_type or '',
                    'release_year': movie.release_year or 0
                })
            
            self.movies_df = pd.DataFrame(movie_data)
            
            if len(self.movies_df) < 2:
                logging.warning("Not enough movies for recommendations")
                return
            
            # Create TF-IDF matrix
            self.tfidf_matrix = self.vectorizer.fit_transform(self.movies_df['content'])
            
            # Compute cosine similarity matrix
            self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
            
            logging.info(f"Loaded {len(self.movies_df)} movies for recommendations")
            
        except Exception as e:
            logging.error(f"Error loading recommendation data: {str(e)}")
    
    def get_content_based_recommendations(self, movie_id, limit=5):
        """Get content-based recommendations for a movie"""
        if self.movies_df is None or self.cosine_sim is None:
            self._load_data()
            
        if self.movies_df is None or self.cosine_sim is None or len(self.movies_df) < 2:
            return []
        
        try:
            # Find movie index
            movie_idx = self.movies_df[self.movies_df['id'] == movie_id].index
            
            if len(movie_idx) == 0:
                logging.warning(f"Movie with id {movie_id} not found")
                return []
            
            movie_idx = movie_idx[0]
            
            # Get similarity scores
            sim_scores = list(enumerate(self.cosine_sim[movie_idx]))
            
            # Sort by similarity (excluding the movie itself)
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:limit+1]
            
            # Get recommended movie IDs
            recommended_ids = [int(self.movies_df.iloc[i[0]]['id']) for i in sim_scores]
            
            # Fetch movies from database
            recommended_movies = Movie.query.filter(Movie.id.in_(recommended_ids)).all()
            
            # Sort by original similarity order
            id_to_movie = {movie.id: movie for movie in recommended_movies}
            sorted_movies = [id_to_movie[movie_id] for movie_id in recommended_ids if movie_id in id_to_movie]
            
            return sorted_movies
            
        except Exception as e:
            logging.error(f"Error getting recommendations: {str(e)}")
            return []
    
    def get_group_recommendations(self, movie_ids, limit=5):
        """Get recommendations based on multiple movies (group preferences)"""
        if self.movies_df is None or self.cosine_sim is None:
            self._load_data()
            
        if self.movies_df is None or self.cosine_sim is None or len(self.movies_df) < 2:
            return []
        
        try:
            # Find indices for all movies
            movie_indices = []
            for movie_id in movie_ids:
                idx = self.movies_df[self.movies_df['id'] == movie_id].index
                if len(idx) > 0:
                    movie_indices.append(idx[0])
            
            if not movie_indices:
                return []
            
            # Calculate average similarity scores across all input movies
            avg_sim_scores = None
            
            for idx in movie_indices:
                sim_scores = self.cosine_sim[idx]
                if avg_sim_scores is None:
                    avg_sim_scores = sim_scores.copy()
                else:
                    avg_sim_scores += sim_scores
            
            # Average the scores
            if avg_sim_scores is not None:
                avg_sim_scores = avg_sim_scores / len(movie_indices)
            else:
                return []
            
            # Get recommendations (excluding input movies)
            sim_scores_with_idx = list(enumerate(avg_sim_scores))
            
            # Filter out input movies
            filtered_scores = [
                (idx, score) for idx, score in sim_scores_with_idx 
                if idx not in movie_indices
            ]
            
            # Sort by similarity
            filtered_scores = sorted(filtered_scores, key=lambda x: x[1], reverse=True)[:limit]
            
            # Get recommended movie IDs
            recommended_ids = [int(self.movies_df.iloc[i[0]]['id']) for i in filtered_scores]
            
            # Fetch movies from database
            recommended_movies = Movie.query.filter(Movie.id.in_(recommended_ids)).all()
            
            # Sort by original similarity order
            id_to_movie = {movie.id: movie for movie in recommended_movies}
            sorted_movies = [id_to_movie[movie_id] for movie_id in recommended_ids if movie_id in id_to_movie]
            
            return sorted_movies
            
        except Exception as e:
            logging.error(f"Error getting group recommendations: {str(e)}")
            return []
    
    def refresh_data(self):
        """Refresh the recommendation data"""
        self._load_data()
