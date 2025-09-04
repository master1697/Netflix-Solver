import os
import requests
import logging
from models import Movie
from app import db

class DataLoader:
    """Load movie data from TMDB API"""
    
    def __init__(self):
        self.api_key = os.environ.get('TMDB_API_KEY', 'your_tmdb_api_key_here')
        self.base_url = 'https://api.themoviedb.org/3'
        self.image_base_url = 'https://image.tmdb.org/t/p/w500'
    
    def load_tmdb_data(self, pages=5):
        """Load popular movies from TMDB"""
        try:
            for page in range(1, pages + 1):
                logging.info(f"Loading page {page} from TMDB...")
                
                # Get popular movies
                url = f"{self.base_url}/movie/popular"
                params = {
                    'api_key': self.api_key,
                    'page': page,
                    'language': 'en-US'
                }
                
                response = requests.get(url, params=params)
                if response.status_code != 200:
                    logging.error(f"TMDB API error: {response.status_code}")
                    continue
                
                data = response.json()
                movies = data.get('results', [])
                
                for movie_data in movies:
                    self._save_movie(movie_data)
                
                db.session.commit()
                logging.info(f"Saved page {page} movies to database")
                
        except Exception as e:
            logging.error(f"Error loading TMDB data: {str(e)}")
            # Add some sample data as fallback
            self._add_sample_data()
    
    def _save_movie(self, movie_data):
        """Save individual movie to database"""
        try:
            # Check if movie already exists
            existing_movie = Movie.query.filter_by(tmdb_id=movie_data['id']).first()
            if existing_movie:
                return
            
            # Get detailed movie information including keywords
            details = self._get_movie_details(movie_data['id'])
            
            # Extract genres
            genres = []
            if 'genre_ids' in movie_data:
                genre_names = self._get_genre_names(movie_data['genre_ids'])
                genres = genre_names
            elif details and 'genres' in details:
                genres = [genre['name'] for genre in details['genres']]
            
            # Extract keywords
            keywords = []
            if details and 'keywords' in details:
                keywords = [keyword['name'] for keyword in details['keywords']['keywords']]
            
            # Create movie object
            movie = Movie(
                tmdb_id=movie_data['id'],
                title=movie_data.get('title', ''),
                overview=movie_data.get('overview', ''),
                genres=','.join(genres),
                keywords=','.join(keywords),
                release_date=movie_data.get('release_date', ''),
                vote_average=movie_data.get('vote_average', 0),
                vote_count=movie_data.get('vote_count', 0),
                popularity=movie_data.get('popularity', 0),
                poster_url=self._get_poster_url(movie_data.get('poster_path')),
                backdrop_url=self._get_backdrop_url(movie_data.get('backdrop_path'))
            )
            
            db.session.add(movie)
            
        except Exception as e:
            logging.error(f"Error saving movie {movie_data.get('title', 'Unknown')}: {str(e)}")
    
    def _get_movie_details(self, movie_id):
        """Get detailed movie information including keywords"""
        try:
            url = f"{self.base_url}/movie/{movie_id}"
            params = {
                'api_key': self.api_key,
                'append_to_response': 'keywords'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        
        except Exception as e:
            logging.error(f"Error getting movie details for {movie_id}: {str(e)}")
        
        return None
    
    def _get_genre_names(self, genre_ids):
        """Convert genre IDs to names"""
        genre_map = {
            28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy',
            80: 'Crime', 99: 'Documentary', 18: 'Drama', 10751: 'Family',
            14: 'Fantasy', 36: 'History', 27: 'Horror', 10402: 'Music',
            9648: 'Mystery', 10749: 'Romance', 878: 'Science Fiction',
            10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western'
        }
        
        return [genre_map.get(genre_id, f'Genre_{genre_id}') for genre_id in genre_ids]
    
    def _get_poster_url(self, poster_path):
        """Get full poster URL"""
        if poster_path:
            return f"{self.image_base_url}{poster_path}"
        return None
    
    def _get_backdrop_url(self, backdrop_path):
        """Get full backdrop URL"""
        if backdrop_path:
            return f"https://image.tmdb.org/t/p/w1280{backdrop_path}"
        return None
    
    def _add_sample_data(self):
        """Add sample movie data as fallback"""
        sample_movies = [
            {
                'tmdb_id': 1,
                'title': 'The Shawshank Redemption',
                'overview': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
                'genres': 'Drama',
                'keywords': 'prison,friendship,hope,redemption',
                'release_date': '1994-09-23',
                'vote_average': 9.3,
                'vote_count': 2000000,
                'popularity': 95.0
            },
            {
                'tmdb_id': 2,
                'title': 'The Godfather',
                'overview': 'The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.',
                'genres': 'Crime,Drama',
                'keywords': 'mafia,family,crime,power',
                'release_date': '1972-03-24',
                'vote_average': 9.2,
                'vote_count': 1500000,
                'popularity': 90.0
            },
            {
                'tmdb_id': 3,
                'title': 'The Dark Knight',
                'overview': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests.',
                'genres': 'Action,Crime,Drama',
                'keywords': 'batman,joker,superhero,crime',
                'release_date': '2008-07-18',
                'vote_average': 9.0,
                'vote_count': 2200000,
                'popularity': 85.0
            },
            {
                'tmdb_id': 4,
                'title': 'Pulp Fiction',
                'overview': 'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.',
                'genres': 'Crime,Drama',
                'keywords': 'crime,violence,redemption,hitman',
                'release_date': '1994-10-14',
                'vote_average': 8.9,
                'vote_count': 1800000,
                'popularity': 80.0
            },
            {
                'tmdb_id': 5,
                'title': 'Forrest Gump',
                'overview': 'The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate and other historical events unfold from the perspective of an Alabama man.',
                'genres': 'Drama,Romance',
                'keywords': 'history,life,journey,love',
                'release_date': '1994-07-06',
                'vote_average': 8.8,
                'vote_count': 1900000,
                'popularity': 88.0
            }
        ]
        
        try:
            for movie_data in sample_movies:
                existing_movie = Movie.query.filter_by(tmdb_id=movie_data['tmdb_id']).first()
                if not existing_movie:
                    movie = Movie(**movie_data)
                    db.session.add(movie)
            
            db.session.commit()
            logging.info("Added sample movie data")
            
        except Exception as e:
            logging.error(f"Error adding sample data: {str(e)}")
