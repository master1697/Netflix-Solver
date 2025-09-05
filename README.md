# Overview

MovieFlix is a movie recommendation web application built with Flask that provides personalized movie suggestions using content-based filtering. The app allows users to search for movies they've enjoyed and receive recommendations based on similar content, genres, and keywords. It features both individual and group recommendation modes, with data sourced from The Movie Database (TMDB) API.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for development with configurable database URL support
- **Models**: Single Movie model storing TMDB data including genres, keywords, ratings, and metadata
- **Recommendation Engine**: Content-based filtering using scikit-learn's TF-IDF vectorization and cosine similarity
- **Data Loading**: Automated TMDB API integration for populating movie database

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **UI Components**: Responsive design with movie cards, search interfaces, and recommendation displays
- **JavaScript**: Vanilla JS for search functionality, AJAX requests, and dynamic content loading
- **Styling**: Custom CSS with hover effects and loading states

## Recommendation Algorithm
- **Content-Based Filtering**: Uses TF-IDF vectorization on combined movie genres, keywords, and overviews
- **Similarity Calculation**: Cosine similarity matrix for finding related movies
- **Group Mode**: Supports multiple movie inputs for group recommendations (implementation pending)

## API Integration
- **TMDB Integration**: Fetches popular movies with metadata including posters, ratings, and descriptions
- **Error Handling**: Fallback to sample data when API is unavailable
- **Rate Limiting**: Pagination support for loading movie data in batches

## Data Management
- **Movie Storage**: Comprehensive movie metadata with TMDB IDs, ratings, popularity scores
- **Content Processing**: Automated text processing for recommendation features
- **Database Initialization**: Automatic table creation and data loading on first run

# External Dependencies

## Third-Party APIs
- **The Movie Database (TMDB) API**: Primary data source for movie information, requires API key configuration

## Python Libraries
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and query management
- **scikit-learn**: Machine learning algorithms for recommendations (TF-IDF, cosine similarity)
- **pandas**: Data manipulation for recommendation processing
- **requests**: HTTP client for TMDB API calls

## Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme support
- **Font Awesome**: Icon library for UI elements
- **Vanilla JavaScript**: Client-side interactivity and AJAX

## Infrastructure
- **SQLite**: Default database (configurable for production)
- **Environment Variables**: Configuration for database URL, TMDB API key, and session secrets
