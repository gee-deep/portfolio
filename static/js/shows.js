console.log('Script loaded'); // Debug print

function slideToIndex(dotElement, index) {
    const gallery = dotElement.closest('.shows-section').querySelector('.gallery');
    const card = gallery.querySelector('.show-card');
    const cardWidth = card.offsetWidth + parseInt(getComputedStyle(card).marginRight);
    const containerWidth = gallery.offsetWidth;
    const visibleCards = Math.floor(containerWidth / cardWidth);
    
    const scrollPosition = cardWidth * index;
    
    gallery.scrollTo({
        left: scrollPosition,
        behavior: 'smooth'
    });

    // Update dots
    const dots = dotElement.parentElement.querySelectorAll('.dot');
    dots.forEach(dot => dot.classList.remove('active'));
    dotElement.classList.add('active');
}

// Add voting functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded'); // Debug print
    const voteButtons = document.querySelectorAll('.vote-button');
    console.log('Vote buttons found:', voteButtons.length); // Debug print
    
    voteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const showId = this.dataset.showId;
            fetch(`/shows/vote/${showId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                console.log('Vote registered:', data); // Debug print
            });
        });
    });

    // Initialize search modal
    const searchModal = new bootstrap.Modal(document.getElementById('searchModal'));
    const searchForm = document.getElementById('searchForm');
    const searchResults = document.getElementById('searchResults');

    // Handle search form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = document.getElementById('searchQuery').value;
        const mediaType = document.getElementById('mediaType').value;
        
        if (query.trim()) {
            // Show loading state
            searchResults.innerHTML = `
                <div class="col-12 text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            `;

            const searchUrl = searchForm.dataset.searchUrl;
            fetch(`${searchUrl}?q=${encodeURIComponent(query)}&type=${mediaType}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                searchResults.innerHTML = data.results.map(result => `
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="row g-0">
                                <div class="col-md-4">
                                    ${result.poster_path ? 
                                        `<img src="${result.poster_path}" class="img-fluid rounded-start" alt="${result.title}">` :
                                        `<div class="no-poster">
                                            <i class="fas fa-film"></i>
                                         </div>`
                                    }
                                </div>
                                <div class="col-md-8">
                                    <div class="card-body">
                                        <h5 class="card-title">${result.title}</h5>
                                        <p class="card-text">
                                            <small class="text-muted">
                                                ${result.media_type.toUpperCase()} 
                                                ${result.release_date ? `(${result.release_date.slice(0,4)})` : ''}
                                            </small>
                                        </p>
                                        <form method="post" action="/portfolio/shows/add/${result.media_type}/${result.id}/">
                                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                                            <select name="status" class="form-select form-select-sm mb-2">
                                                <option value="watching">Currently Watching</option>
                                                <option value="watched">Finished Watching</option>
                                                <option value="want_to_watch">Want to Watch</option>
                                            </select>
                                            <button type="submit" class="btn btn-primary btn-sm">Add to List</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
            })
            .catch(error => {
                console.error('Error:', error);
                searchResults.innerHTML = `
                    <div class="col-12">
                        <div class="alert alert-danger">
                            Failed to fetch results. Please try again.
                        </div>
                    </div>
                `;
            });
        }
    });

    // Handle real-time search
    let searchTimeout;
    document.getElementById('searchQuery').addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            if (this.value.trim()) {
                searchForm.dispatchEvent(new Event('submit'));
            }
        }, 500);
    });

    // Filter form handling
    const filterForm = document.getElementById('showFilterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyFilters();
        });

        filterForm.addEventListener('reset', function() {
            setTimeout(() => {
                applyFilters();
            }, 0);
        });
    }

    // Vote button handling
    document.querySelectorAll('.vote-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const showId = this.dataset.showId;
            const voteCount = this.querySelector('.vote-count');
            
            fetch(`/portfolio/shows/vote/${showId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                voteCount.textContent = data.votes;
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

function applyFilters() {
    const formData = new FormData(document.getElementById('showFilterForm'));
    const params = new URLSearchParams(formData);
    
    fetch(`/portfolio/shows/filter/?${params}`)
        .then(response => response.json())
        .then(data => {
            updateShowsSection('watching-shows', data.current_shows);
            updateShowsSection('watched-shows', data.watched_shows);
            updateShowsSection('wishlist-shows', data.wishlist_shows);
        })
        .catch(error => console.error('Error:', error));
}

function updateShowsSection(sectionId, shows) {
    const section = document.getElementById(sectionId);
    if (shows.length === 0) {
        section.innerHTML = '<div class="col-12"><p class="text-muted text-center">No shows found.</p></div>';
    } else {
        section.innerHTML = shows.map(show => createShowCard(show)).join('');
    }
}

function createShowCard(show) {
    return `
        <div class="col-md-6 col-lg-4">
            <div class="card show-card h-100">
                ${show.image_url ? `<img src="${show.image_url}" class="card-img-top" alt="${show.title}">` : ''}
                <div class="card-body">
                    <h5 class="card-title">${show.title}</h5>
                    <p class="card-subtitle mb-2">
                        <span class="badge bg-primary">${show.show_type}</span>
                        ${show.rating ? `
                            <span class="badge bg-warning text-dark">
                                <i class="fas fa-star"></i> ${show.rating}
                            </span>
                        ` : ''}
                    </p>
                    ${show.review ? `<p class="card-text">${show.review}</p>` : ''}
                    <div class="vote-controls">
                        <button class="btn btn-sm btn-outline-primary vote-btn" data-show-id="${show.id}">
                            <i class="fas fa-thumbs-up"></i>
                            <span class="vote-count">${show.votes}</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 