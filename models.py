from app import db
from datetime import datetime

class Movie(db.Model):
    """Movie/TV Show model for storing Netflix content information"""
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.String(20), unique=True, nullable=False)  # Netflix show ID like 's1'
    content_type = db.Column(db.String(20), nullable=False)  # 'Movie' or 'TV Show'
    title = db.Column(db.String(500), nullable=False)
    director = db.Column(db.Text)  # Director(s)
    cast = db.Column(db.Text)  # Cast members
    country = db.Column(db.String(500))  # Country/countries
    date_added = db.Column(db.String(50))  # Date added to Netflix
    release_year = db.Column(db.Integer)  # Release year
    rating = db.Column(db.String(20))  # Content rating (PG, TV-MA, etc.)
    duration = db.Column(db.String(50))  # Duration (e.g., '90 min' or '2 Seasons')
    listed_in = db.Column(db.Text)  # Genres/categories (comma-separated)
    description = db.Column(db.Text)  # Plot description
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Movie {self.title}>'
    
    def to_dict(self):
        """Convert content to dictionary"""
        return {
            'id': self.id,
            'show_id': self.show_id,
            'type': self.content_type,
            'title': self.title,
            'director': self.director,
            'cast': self.cast,
            'country': self.country,
            'date_added': self.date_added,
            'release_year': self.release_year,
            'rating': self.rating,
            'duration': self.duration,
            'genres': self.listed_in.split(',') if self.listed_in else [],
            'description': self.description
        }
