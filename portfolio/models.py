from django.db import models
from django.utils import timezone

class Book(models.Model):
    STATUS_CHOICES = [
        ('want_to_read', 'Want to Read'),
        ('reading', 'Currently Reading'),
        ('read', 'Read')
    ]

    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True)  # Store as comma-separated string
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='want_to_read')
    date_added = models.DateTimeField(auto_now_add=True)
    google_books_id = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    published_date = models.CharField(max_length=20, blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    categories = models.CharField(max_length=500, blank=True)  # Store as comma-separated string
    rating = models.FloatField(null=True, blank=True)
    ratings_count = models.IntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True)
    language = models.CharField(max_length=10, blank=True)
    isbn = models.CharField(max_length=50, blank=True)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Show(models.Model):
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200, blank=True)
    tmdb_id = models.IntegerField(db_index=True)
    show_type = models.CharField(max_length=50, choices=[
        ('movie', 'Movie'),
        ('series', 'TV Series'),
        ('anime', 'Anime')
    ])
    STATUS_CHOICES = [
        ('want_to_watch', 'Want to Watch'),
        ('watching', 'Currently Watching'),
        ('watched', 'Finished Watching'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    overview = models.TextField(blank=True)  # Plot summary
    review = models.TextField(blank=True)
    personal_rating = models.IntegerField(null=True, blank=True, choices=[
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ])
    votes = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True)  # For movie/show poster
    backdrop_url = models.URLField(blank=True)  # Background image
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)  # TMDB rating
    release_date = models.DateField(null=True, blank=True)
    genres = models.CharField(max_length=200, blank=True)  # Store as comma-separated values
    runtime = models.IntegerField(null=True, blank=True)  # In minutes
    language = models.CharField(max_length=10, blank=True)
    production_companies = models.CharField(max_length=200, blank=True)
    cast = models.TextField(blank=True)  # Store top cast members
    director = models.CharField(max_length=200, blank=True)
    season_count = models.IntegerField(null=True, blank=True)  # For TV shows
    episode_count = models.IntegerField(null=True, blank=True)  # For TV shows
    WATCH_STATUS_CHOICES = [
        ('', 'Not Started'),
        ('started', 'Started Watching'),
        ('completed', 'Completed'),
    ]
    watch_status = models.CharField(
        max_length=50, 
        choices=WATCH_STATUS_CHOICES,
        default='',
        blank=True
    )
    last_watched = models.DateTimeField(null=True, blank=True)
    watch_count = models.IntegerField(default=0)  # How many times watched

    class Meta:
        ordering = ['-votes', '-date_added']  # Order by votes first, then date
        constraints = [
            models.UniqueConstraint(
                fields=['tmdb_id', 'status'],
                name='unique_show_status'
            )
        ]

    def __str__(self):
        return self.title

    def get_genres_list(self):
        return self.genres.split(',') if self.genres else []

    def get_cast_list(self):
        return self.cast.split(',') if self.cast else []

    def get_companies_list(self):
        return self.production_companies.split(',') if self.production_companies else []

class LifeEvent(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField()
    image = models.ImageField(upload_to='life_events/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    show = models.ForeignKey(
        Show,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='life_events'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='life_events'
    )

    def __str__(self):
        return f"{self.date}: {self.title}"

class About(models.Model):
    bio = models.TextField()
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    skills = models.TextField()
    interests = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "About"

    def __str__(self):
        return "About Me" 