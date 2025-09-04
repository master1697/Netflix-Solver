from app import db
from datetime import datetime

class Movie(db.Model):
    """Movie model for storing movie information"""
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    overview = db.Column(db.Text)
    genres = db.Column(db.String(500))  # Comma-separated genre names
    keywords = db.Column(db.Text)  # Comma-separated keywords
    release_date = db.Column(db.String(10))  # YYYY-MM-DD format
    vote_average = db.Column(db.Float, default=0.0)
    vote_count = db.Column(db.Integer, default=0)
    popularity = db.Column(db.Float, default=0.0)
    poster_url = db.Column(db.String(500))
    backdrop_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Movie {self.title}>'
    
    def to_dict(self):
        """Convert movie to dictionary"""
        return {
            'id': self.id,
            'tmdb_id': self.tmdb_id,
            'title': self.title,
            'overview': self.overview,
            'genres': self.genres.split(',') if self.genres else [],
            'keywords': self.keywords.split(',') if self.keywords else [],
            'release_date': self.release_date,
            'vote_average': self.vote_average,
            'vote_count': self.vote_count,
            'popularity': self.popularity,
            'poster_url': self.poster_url,
            'backdrop_url': self.backdrop_url
        }
