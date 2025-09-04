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
        movies_loaded = False
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
                movies_loaded = True
                
        except Exception as e:
            logging.error(f"Error loading TMDB data: {str(e)}")
        
        # Add sample data if no movies were loaded from TMDB
        if not movies_loaded:
            logging.info("TMDB data loading failed, adding sample data...")
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
            movie = Movie()
            movie.tmdb_id = movie_data['id']
            movie.title = movie_data.get('title', '')
            movie.overview = movie_data.get('overview', '')
            movie.genres = ','.join(genres)
            movie.keywords = ','.join(keywords)
            movie.release_date = movie_data.get('release_date', '')
            movie.vote_average = movie_data.get('vote_average', 0)
            movie.vote_count = movie_data.get('vote_count', 0)
            movie.popularity = movie_data.get('popularity', 0)
            movie.poster_url = self._get_poster_url(movie_data.get('poster_path'))
            movie.backdrop_url = self._get_backdrop_url(movie_data.get('backdrop_path'))
            
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
            },
            {
                'tmdb_id': 6,
                'title': 'Inception',
                'overview': 'A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.',
                'genres': 'Action,Sci-Fi,Thriller',
                'keywords': 'dreams,heist,reality,science fiction',
                'release_date': '2010-07-16',
                'vote_average': 8.8,
                'vote_count': 2100000,
                'popularity': 83.0
            },
            {
                'tmdb_id': 7,
                'title': 'The Matrix',
                'overview': 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.',
                'genres': 'Action,Sci-Fi',
                'keywords': 'virtual reality,hacker,simulation,action',
                'release_date': '1999-03-31',
                'vote_average': 8.7,
                'vote_count': 1900000,
                'popularity': 80.0
            },
            {
                'tmdb_id': 8,
                'title': 'Goodfellas',
                'overview': 'The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners.',
                'genres': 'Biography,Crime,Drama',
                'keywords': 'mafia,crime,biography,gangster',
                'release_date': '1990-09-21',
                'vote_average': 8.7,
                'vote_count': 1000000,
                'popularity': 75.0
            },
            {
                'tmdb_id': 9,
                'title': 'Titanic',
                'overview': 'A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious, ill-fated R.M.S. Titanic.',
                'genres': 'Drama,Romance',
                'keywords': 'ship,love,disaster,romance',
                'release_date': '1997-12-19',
                'vote_average': 7.8,
                'vote_count': 1100000,
                'popularity': 85.0
            },
            {
                'tmdb_id': 10,
                'title': 'Avatar',
                'overview': 'A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.',
                'genres': 'Action,Adventure,Fantasy,Sci-Fi',
                'keywords': 'alien,future,planet,environment',
                'release_date': '2009-12-18',
                'vote_average': 7.6,
                'vote_count': 1200000,
                'popularity': 90.0
            },
            {
                'tmdb_id': 11,
                'title': 'The Lion King',
                'overview': 'A Lion cub crown prince is tricked by a treacherous uncle into thinking he caused his father\'s death and flees into exile in despair.',
                'genres': 'Animation,Adventure,Drama,Family,Musical',
                'keywords': 'lion,africa,animals,family',
                'release_date': '1994-06-24',
                'vote_average': 8.5,
                'vote_count': 800000,
                'popularity': 88.0
            },
            {
                'tmdb_id': 12,
                'title': 'Star Wars',
                'overview': 'Luke Skywalker joins forces with a Jedi Knight, a cocky pilot, a Wookiee and two droids to save the galaxy from the Empire\'s world-destroying battle station.',
                'genres': 'Adventure,Fantasy,Sci-Fi',
                'keywords': 'space,jedi,empire,rebellion',
                'release_date': '1977-05-25',
                'vote_average': 8.6,
                'vote_count': 1300000,
                'popularity': 92.0
            },
            {
                'tmdb_id': 13,
                'title': 'Jurassic Park',
                'overview': 'A pragmatic paleontologist touring an almost complete theme park on an island in Central America is tasked with protecting a couple of kids after a power failure causes the park\'s cloned dinosaurs to run loose.',
                'genres': 'Adventure,Sci-Fi,Thriller',
                'keywords': 'dinosaurs,island,science,adventure',
                'release_date': '1993-06-11',
                'vote_average': 8.1,
                'vote_count': 1400000,
                'popularity': 89.0
            },
            {
                'tmdb_id': 14,
                'title': 'The Avengers',
                'overview': 'Earth\'s mightiest heroes must come together and learn to fight as a team if they are going to stop the mischievous Loki and his alien army from enslaving humanity.',
                'genres': 'Action,Adventure,Sci-Fi',
                'keywords': 'superhero,team,action,marvel',
                'release_date': '2012-05-04',
                'vote_average': 8.0,
                'vote_count': 1500000,
                'popularity': 94.0
            },
            {
                'tmdb_id': 15,
                'title': 'Toy Story',
                'overview': 'A cowboy doll is profoundly threatened and jealous when a new spaceman figure supplants him as top toy in a boy\'s room.',
                'genres': 'Animation,Adventure,Comedy,Family',
                'keywords': 'toys,friendship,animation,adventure',
                'release_date': '1995-11-22',
                'vote_average': 8.3,
                'vote_count': 900000,
                'popularity': 87.0
            }
        ]
        
        try:
            for movie_data in sample_movies:
                existing_movie = Movie.query.filter_by(tmdb_id=movie_data['tmdb_id']).first()
                if not existing_movie:
                    movie = Movie()
                    movie.tmdb_id = movie_data['tmdb_id']
                    movie.title = movie_data['title']
                    movie.overview = movie_data['overview']
                    movie.genres = movie_data['genres']
                    movie.keywords = movie_data['keywords']
                    movie.release_date = movie_data['release_date']
                    movie.vote_average = movie_data['vote_average']
                    movie.vote_count = movie_data['vote_count']
                    movie.popularity = movie_data['popularity']
                    movie.poster_url = None
                    movie.backdrop_url = None
                    db.session.add(movie)
            
            db.session.commit()
            logging.info("Added sample movie data")
            
        except Exception as e:
            logging.error(f"Error adding sample data: {str(e)}")
