// Global variables
let selectedMovies = [];
let searchTimeout;

// Utility functions
function showLoading() {
    document.getElementById('loadingState').style.display = 'block';
    hideError();
}

function hideLoading() {
    document.getElementById('loadingState').style.display = 'none';
}

function showError(message) {
    const errorState = document.getElementById('errorState');
    const errorMessage = document.getElementById('errorMessage');
    if (errorState && errorMessage) {
        errorMessage.textContent = message;
        errorState.style.display = 'block';
    }
    hideLoading();
}

function hideError() {
    const errorState = document.getElementById('errorState');
    if (errorState) {
        errorState.style.display = 'none';
    }
}

function createMovieCard(movie, includeSelectButton = false) {
    const posterUrl = movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster';
    const genres = Array.isArray(movie.genres) ? movie.genres.join(', ') : movie.genres || 'Unknown';
    const overview = movie.overview || 'No description available.';
    const rating = movie.vote_average ? movie.vote_average.toFixed(1) : 'N/A';
    
    return `
        <div class="col-md-6 col-lg-4 mb-4">
            <div class="card h-100 movie-card">
                <img src="${posterUrl}" class="card-img-top" alt="${movie.title}" style="height: 300px; object-fit: cover;">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">${movie.title}</h5>
                    <p class="card-text text-muted mb-2">
                        <i class="fas fa-star text-warning me-1"></i>${rating}
                        ${movie.release_date ? ` • ${movie.release_date.split('-')[0]}` : ''}
                    </p>
                    <p class="card-text"><small class="text-muted">${genres}</small></p>
                    <p class="card-text flex-grow-1">${overview.length > 120 ? overview.substring(0, 120) + '...' : overview}</p>
                    ${includeSelectButton ? `
                        <button class="btn btn-primary mt-auto" onclick="selectMovie(${movie.id}, '${movie.title.replace(/'/g, "\\'")}')">
                            <i class="fas fa-check me-2"></i>Select This Movie
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function createSmallMovieCard(movie, showRemoveButton = false) {
    const posterUrl = movie.poster_url || 'https://via.placeholder.com/100x150?text=No+Poster';
    
    return `
        <div class="col-md-3 mb-3">
            <div class="card">
                <div class="row g-0">
                    <div class="col-4">
                        <img src="${posterUrl}" class="card-img" alt="${movie.title}" style="height: 100px; object-fit: cover;">
                    </div>
                    <div class="col-8">
                        <div class="card-body p-2">
                            <h6 class="card-title mb-1">${movie.title}</h6>
                            <p class="card-text">
                                <small class="text-muted">
                                    ${movie.release_date ? movie.release_date.split('-')[0] : 'Unknown'}
                                </small>
                            </p>
                            ${showRemoveButton ? `
                                <button class="btn btn-sm btn-outline-danger" onclick="removeSelectedMovie(${movie.id})">
                                    <i class="fas fa-times"></i>
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Search functionality
async function searchMovies(query) {
    if (!query.trim()) {
        document.getElementById('searchResults').style.display = 'none';
        return;
    }

    try {
        const response = await fetch(`/api/movies/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Search failed');
        }

        displaySearchResults(data.results);
    } catch (error) {
        console.error('Search error:', error);
        showError('Failed to search movies. Please try again.');
    }
}

function displaySearchResults(movies) {
    const resultsContainer = document.getElementById('searchResultsList');
    const resultsSection = document.getElementById('searchResults');

    if (!movies || movies.length === 0) {
        resultsSection.style.display = 'none';
        return;
    }

    let html = '';
    movies.forEach(movie => {
        html += createMovieCard(movie, true);
    });

    resultsContainer.innerHTML = html;
    resultsSection.style.display = 'block';
}

// Movie selection for individual recommendations
function selectMovie(movieId, movieTitle) {
    // Store selected movie info
    const selectedMovie = {
        id: movieId,
        title: movieTitle
    };

    // Hide search results
    document.getElementById('searchResults').style.display = 'none';
    
    // Show selected movie section
    showSelectedMovie(selectedMovie);
}

function showSelectedMovie(movie) {
    const selectedMovieSection = document.getElementById('selectedMovie');
    const selectedMovieCard = document.getElementById('selectedMovieCard');

    if (selectedMovieCard) {
        selectedMovieCard.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                Selected: <strong>${movie.title}</strong>
            </div>
        `;
    }

    if (selectedMovieSection) {
        selectedMovieSection.style.display = 'block';
    }
}

// Recommendations functionality
async function loadRecommendations(title) {
    showLoading();
    hideError();

    try {
        const response = await fetch(`/api/recommend?title=${encodeURIComponent(title)}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to get recommendations');
        }

        displayRecommendations(data);
    } catch (error) {
        console.error('Recommendations error:', error);
        showError(error.message || 'Failed to get recommendations. Please try again.');
    } finally {
        hideLoading();
    }
}

function displayRecommendations(data) {
    const sourceSection = document.getElementById('sourceMovieSection');
    const sourceCard = document.getElementById('sourceMovieCard');
    const recommendationsSection = document.getElementById('recommendationsSection');
    const recommendationsList = document.getElementById('recommendationsList');
    const emptyState = document.getElementById('emptyState');

    // Show source movie
    if (sourceCard && data.source_movie) {
        sourceCard.innerHTML = createSmallMovieCard(data.source_movie);
        sourceSection.style.display = 'block';
    }

    // Show recommendations
    if (data.recommendations && data.recommendations.length > 0) {
        let html = '';
        data.recommendations.forEach(movie => {
            html += createMovieCard(movie);
        });

        recommendationsList.innerHTML = html;
        recommendationsSection.style.display = 'block';
        
        if (emptyState) {
            emptyState.style.display = 'none';
        }
    } else {
        if (emptyState) {
            emptyState.style.display = 'block';
        }
        recommendationsSection.style.display = 'none';
    }
}

// Group recommendations functionality
function initializeGroupMode() {
    const movieInput = document.getElementById('movieInput');
    const addMovieBtn = document.getElementById('addMovieBtn');
    const getGroupRecommendationsBtn = document.getElementById('getGroupRecommendationsBtn');

    if (movieInput) {
        movieInput.addEventListener('input', handleGroupMovieSearch);
        movieInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
            }
        });
    }

    if (addMovieBtn) {
        addMovieBtn.addEventListener('click', handleAddMovie);
    }

    if (getGroupRecommendationsBtn) {
        getGroupRecommendationsBtn.addEventListener('click', getGroupRecommendations);
    }

    updateGroupUI();
}

function handleGroupMovieSearch() {
    const query = document.getElementById('movieInput').value.trim();
    
    clearTimeout(searchTimeout);
    
    if (query.length < 2) {
        document.getElementById('addMovieResults').style.display = 'none';
        return;
    }

    searchTimeout = setTimeout(() => {
        searchMoviesForGroup(query);
    }, 300);
}

async function searchMoviesForGroup(query) {
    try {
        const response = await fetch(`/api/movies/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Search failed');
        }

        displayGroupSearchResults(data.results);
    } catch (error) {
        console.error('Group search error:', error);
    }
}

function displayGroupSearchResults(movies) {
    const resultsContainer = document.getElementById('addMovieResultsList');
    const resultsSection = document.getElementById('addMovieResults');

    if (!movies || movies.length === 0) {
        resultsSection.style.display = 'none';
        return;
    }

    // Filter out already selected movies
    const filteredMovies = movies.filter(movie => 
        !selectedMovies.some(selected => selected.id === movie.id)
    );

    if (filteredMovies.length === 0) {
        resultsSection.style.display = 'none';
        return;
    }

    let html = '<div class="list-group">';
    filteredMovies.slice(0, 5).forEach(movie => {
        const posterUrl = movie.poster_url || 'https://via.placeholder.com/50x75?text=No+Poster';
        html += `
            <div class="list-group-item list-group-item-action d-flex align-items-center" 
                 onclick="addMovieToGroup(${movie.id}, '${movie.title.replace(/'/g, "\\'")}', '${movie.poster_url || ''}', '${movie.release_date || ''}')">
                <img src="${posterUrl}" alt="${movie.title}" class="me-3" style="width: 50px; height: 75px; object-fit: cover;">
                <div>
                    <h6 class="mb-1">${movie.title}</h6>
                    <small class="text-muted">${movie.release_date ? movie.release_date.split('-')[0] : 'Unknown'}</small>
                </div>
            </div>
        `;
    });
    html += '</div>';

    resultsContainer.innerHTML = html;
    resultsSection.style.display = 'block';
}

function addMovieToGroup(id, title, posterUrl, releaseDate) {
    // Check if movie is already selected
    if (selectedMovies.some(movie => movie.id === id)) {
        return;
    }

    // Add movie to selected list
    selectedMovies.push({
        id: id,
        title: title,
        poster_url: posterUrl,
        release_date: releaseDate
    });

    // Clear input and hide results
    document.getElementById('movieInput').value = '';
    document.getElementById('addMovieResults').style.display = 'none';

    updateGroupUI();
}

function removeSelectedMovie(movieId) {
    selectedMovies = selectedMovies.filter(movie => movie.id !== movieId);
    updateGroupUI();
}

function updateGroupUI() {
    const container = document.getElementById('selectedMoviesContainer');
    const getRecommendationsBtn = document.getElementById('getGroupRecommendationsBtn');

    if (selectedMovies.length === 0) {
        container.innerHTML = '<p class="text-muted">No movies selected yet. Start by searching for movies above.</p>';
        getRecommendationsBtn.disabled = true;
    } else {
        let html = '<div class="row">';
        selectedMovies.forEach(movie => {
            html += createSmallMovieCard(movie, true);
        });
        html += '</div>';
        
        container.innerHTML = html;
        getRecommendationsBtn.disabled = false;
    }
}

async function getGroupRecommendations() {
    if (selectedMovies.length === 0) {
        showError('Please select at least one movie first.');
        return;
    }

    showLoading();
    hideError();

    try {
        const titles = selectedMovies.map(movie => movie.title);
        
        const response = await fetch('/api/group_recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ titles: titles })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to get group recommendations');
        }

        displayGroupRecommendations(data);
    } catch (error) {
        console.error('Group recommendations error:', error);
        showError(error.message || 'Failed to get group recommendations. Please try again.');
    } finally {
        hideLoading();
    }
}

function displayGroupRecommendations(data) {
    const sourceSection = document.getElementById('sourceMoviesSection');
    const sourceContainer = document.getElementById('sourceMoviesContainer');
    const recommendationsSection = document.getElementById('groupRecommendationsSection');
    const recommendationsList = document.getElementById('groupRecommendationsList');

    // Show source movies
    if (sourceContainer && data.source_movies) {
        let html = '';
        data.source_movies.forEach(movie => {
            html += createSmallMovieCard(movie);
        });

        sourceContainer.innerHTML = html;
        sourceSection.style.display = 'block';
    }

    // Show recommendations
    if (data.recommendations && data.recommendations.length > 0) {
        let html = '';
        data.recommendations.forEach(movie => {
            html += createMovieCard(movie);
        });

        recommendationsList.innerHTML = html;
        recommendationsSection.style.display = 'block';
    } else {
        showError('No group recommendations found. Try adding different movies.');
    }
}

function handleAddMovie() {
    const input = document.getElementById('movieInput');
    const query = input.value.trim();
    
    if (query) {
        searchMoviesForGroup(query);
    }
}

// Initialize main page functionality
document.addEventListener('DOMContentLoaded', function() {
    const movieSearch = document.getElementById('movieSearch');
    const searchBtn = document.getElementById('searchBtn');
    const getRecommendationsBtn = document.getElementById('getRecommendationsBtn');

    // Main search functionality
    if (movieSearch) {
        movieSearch.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                document.getElementById('searchResults').style.display = 'none';
                return;
            }

            searchTimeout = setTimeout(() => {
                searchMovies(query);
            }, 300);
        });

        movieSearch.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = this.value.trim();
                if (query) {
                    searchMovies(query);
                }
            }
        });
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            const query = movieSearch.value.trim();
            if (query) {
                searchMovies(query);
            }
        });
    }

    if (getRecommendationsBtn) {
        getRecommendationsBtn.addEventListener('click', function() {
            const selectedMovie = document.querySelector('#selectedMovieCard strong');
            if (selectedMovie) {
                const title = selectedMovie.textContent;
                window.location.href = `/recommendations?title=${encodeURIComponent(title)}`;
            }
        });
    }
});
