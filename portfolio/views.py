from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Book, Show, LifeEvent, About
from .services.tmdb import TMDBClient
from .forms import LifeEventForm
from datetime import date, datetime
from django.contrib.auth import login, logout, authenticate
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.text import slugify
from .services.google_books import GoogleBooksClient
from .utils import get_random_quote

def home(request):
    about = About.objects.first()
    recent_events = LifeEvent.objects.order_by('-date')[:3]
    return render(request, 'portfolio/home.html', {
        'about': about,
        'recent_events': recent_events
    })

def about(request):
    about = About.objects.first()
    return render(request, 'portfolio/about.html', {'about': about})

def life_events(request):
    # Start with all events
    # By default, exclude show-related events unless specifically viewing a show's date
    event_list = LifeEvent.objects.all()
    specific_date = request.GET.get('date')
    
    if not specific_date:
        event_list = event_list.filter(show__isnull=True)
    
    # Apply date filters if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if specific_date:
        event_list = event_list.filter(date=specific_date)
    if start_date:
        event_list = event_list.filter(date__gte=start_date)
    if end_date:
        event_list = event_list.filter(date__lte=end_date)
    
    # Sort the filtered results
    event_list = event_list.order_by('-date', '-created_at')
    
    # Set up pagination
    paginator = Paginator(event_list, 5)  # Show 5 events per page
    page = request.GET.get('page')
    events = paginator.get_page(page)
    
    return render(request, 'portfolio/life_events.html', {'events': events})

def books(request):
    current_books = Book.objects.filter(status='reading').order_by('-date_added')
    read_books = Book.objects.filter(status='read').order_by('-date_added')
    wishlist_books = Book.objects.filter(status='want_to_read').order_by('-date_added')
    return render(request, 'portfolio/books.html', {
        'current_books': current_books,
        'read_books': read_books,
        'wishlist_books': wishlist_books
    })

def search_books(request):
    if request.method == 'GET' and 'q' in request.GET:
        client = GoogleBooksClient()
        books = client.search_books(request.GET['q'])
        print(f"Found {len(books)} books")  # Debug print
        return JsonResponse({'books': books})
    return render(request, 'portfolio/search_books.html')

@login_required
@staff_member_required
@require_POST
def add_book(request, book_id):
    client = GoogleBooksClient()
    book_data = client.get_book_details(book_id)
    
    if book_data:
        book, created = Book.objects.get_or_create(
            google_books_id=book_id,
            defaults={
                'title': book_data['title'],
                'authors': ', '.join(book_data['authors']),
                'description': book_data['description'],
                'published_date': book_data['published_date'],
                'page_count': book_data['page_count'],
                'categories': ', '.join(book_data['categories']),
                'rating': book_data['rating'],
                'ratings_count': book_data['ratings_count'],
                'image_url': book_data['image_url'],
                'language': book_data['language'],
                'isbn': book_data['isbn'],
                'status': request.POST.get('status', 'want_to_read')
            }
        )
        
        if not created:
            book.status = request.POST.get('status', 'want_to_read')
            book.save()
        
        if book.status in ['reading', 'read']:
            LifeEvent.objects.create(
                title=f"📚 Started reading {book.title}" if book.status == 'reading'
                      else f"📖 Finished reading {book.title}",
                description=f"Started a new book: {book.title} by {book.authors}",
                date=timezone.now().date(),
                book=book
            )
    
    return redirect('portfolio:books')

@require_POST
def vote_show(request, show_id):
    if not request.is_ajax():
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    show = get_object_or_404(Show, id=show_id)
    show.votes += 1
    show.save()
    
    return JsonResponse({
        'votes': show.votes,
        'show_id': show_id
    })

@require_POST
def downvote_show(request, show_id):
    if not request.is_ajax():
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    show = get_object_or_404(Show, id=show_id)
    show.votes = max(0, show.votes - 1)  # Ensure votes don't go below 0
    show.save()
    
    return JsonResponse({
        'votes': show.votes,
        'show_id': show_id
    })

def shows(request):
    current_shows = Show.objects.filter(status='watching').order_by('-votes', '-date_added')
    watched_shows = Show.objects.filter(status='watched').order_by('-votes', '-date_added')
    wishlist_shows = Show.objects.filter(status='want_to_watch').order_by('-votes', '-date_added')
    
    context = {
        'current_shows': current_shows,
        'watched_shows': watched_shows,
        'wishlist_shows': wishlist_shows,
        'empty_watching_quote': get_random_quote('movie'),
        'empty_watched_quote': get_random_quote('movie'),
        'empty_wishlist_quote': get_random_quote('movie'),
    }
    
    return render(request, 'portfolio/shows.html', context)

def search_shows(request):
    print("Search request received")  # Debug print
    query = request.GET.get('q', '')
    media_type = request.GET.get('type', 'all')
    print(f"Query: {query}, Type: {media_type}")  # Debug print
    results = []
    
    if query:
        tmdb_client = TMDBClient()
        results = tmdb_client.search_multi(query, media_type)
        print(f"Found {len(results)} results")  # Debug print
    
    return render(request, 'portfolio/add_show.html', {
        'results': results,
        'query': query,
        'media_type': media_type
    })

def add_show(request, media_type, tmdb_id):
    if request.method == 'POST':
        tmdb_client = TMDBClient()
        show_data = tmdb_client.get_details(media_type, tmdb_id)
        
        # Check if show already exists with different status
        existing_show = Show.objects.filter(tmdb_id=tmdb_id).first()
        if existing_show:
            # Update status of existing show
            existing_show.status = request.POST.get('status', 'want_to_watch')
            existing_show.save()
            
            # Create life event for status change
            if existing_show.status in ['watching', 'watched']:
                LifeEvent.objects.create(
                    title=f"🎬 Started watching {existing_show.title}" if existing_show.status == 'watching' 
                          else f"✅ Finished watching {existing_show.title}",
                    description=f"Started a new {existing_show.show_type}: {existing_show.title}",
                    date=timezone.now().date(),
                    show=existing_show
                )
            
            return redirect('portfolio:shows')
        
        # Parse release date
        release_date_str = show_data.get('release_date') or show_data.get('first_air_date')
        try:
            release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date() if release_date_str else None
        except (ValueError, TypeError):
            release_date = None
        
        # Create new show
        show = Show(
            title=show_data['title'],
            original_title=show_data.get('original_title', ''),
            tmdb_id=tmdb_id,
            show_type='movie' if media_type == 'movie' else 'series',
            status=request.POST.get('status', 'want_to_watch'),
            overview=show_data.get('overview', ''),
            image_url=show_data['image_url'],
            backdrop_url=show_data.get('backdrop_path', ''),
            rating=show_data['rating'],
            release_date=release_date,
            genres=','.join(g['name'] for g in show_data.get('genres', [])),
            runtime=show_data.get('runtime') or show_data.get('episode_run_time', [0])[0],
            language=show_data.get('original_language', ''),
            production_companies=','.join(
                pc['name'] for pc in show_data.get('production_companies', [])[:3]
            ),
        )
        
        # Get credits data
        credits = tmdb_client.get_credits(media_type, tmdb_id)
        if credits:
            show.cast = ','.join(
                cast['name'] for cast in credits.get('cast', [])[:5]
            )
            # Find director (movie) or creators (TV series)
            if media_type == 'movie':
                directors = [
                    crew['name'] for crew in credits.get('crew', [])
                    if crew['job'] == 'Director'
                ]
                show.director = ','.join(directors[:2])
            else:
                show.director = ','.join(
                    creator['name'] for creator in show_data.get('created_by', [])
                )
        
        # Add TV series specific data
        if media_type != 'movie':
            show.season_count = show_data.get('number_of_seasons', 0)
            show.episode_count = show_data.get('number_of_episodes', 0)
        
        show.save()
        
        # Create life event for new show
        if show.status in ['watching', 'watched']:
            LifeEvent.objects.create(
                title=f"Started watching {show.title}" if show.status == 'watching' 
                      else f"Finished watching {show.title}",
                description=f"**{show.title}** ({show.release_date.year if show.release_date else 'N/A'})\n\n{show.overview}",
                date=timezone.now().date(),
                show=show
            )
        
        messages.success(request, f'Added "{show.title}" to your {show.get_status_display()} list!')
        return redirect('portfolio:shows')
    
    return render(request, 'portfolio/add_show.html', {
        'media_type': media_type,
        'tmdb_id': tmdb_id
    })

@login_required
@staff_member_required
@require_POST
def delete_show(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    title = show.title
    show.delete()
    messages.success(request, f'Removed "{title}" from your list')
    return redirect('portfolio:shows')

def add_life_event(request):
    if request.method == 'POST':
        form = LifeEventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event added successfully!')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('portfolio:life_events')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        form = LifeEventForm(initial={'date': date.today()})
    
    return render(request, 'portfolio/add_life_event.html', {'form': form})

def login_view(request):
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('portfolio:home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:  # Check if user is staff/admin
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('portfolio:home')
        else:
            messages.error(request, 'Invalid admin credentials.')
    
    return render(request, 'portfolio/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('portfolio:home')

@login_required
@staff_member_required
def profile_view(request):
    return render(request, 'portfolio/profile.html')

@login_required
@staff_member_required
def edit_life_event(request, event_id):
    event = get_object_or_404(LifeEvent, id=event_id)
    
    if request.method == 'POST':
        form = LifeEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('portfolio:life_events')
    else:
        form = LifeEventForm(instance=event)
    
    return render(request, 'portfolio/add_life_event.html', {
        'form': form,
        'edit_mode': True,
        'event': event
    })

@login_required
@staff_member_required
def delete_life_event(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(LifeEvent, id=event_id)
        event.delete()
        messages.success(request, 'Event deleted successfully!')
    return redirect('portfolio:life_events')

@login_required
@staff_member_required
@require_POST
def update_show_status(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    new_status = request.POST.get('new_status')
    
    if new_status in ['watching', 'watched']:
        old_status = show.status
        show.status = new_status
        
        # Update dates based on status change
        if new_status == 'watching':
            show.watch_status = 'started'
            if not show.last_watched:
                show.last_watched = timezone.make_aware(datetime(2025, 1, 1))
            # Create life event for starting to watch
            LifeEvent.objects.create(
                title=f"🎬 Started watching {show.title}",
                description=f"Started a new {show.show_type}: {show.title}",
                date=timezone.now().date(),
                show=show
            )
        elif new_status == 'watched':
            show.watch_status = 'completed'
            show.last_watched = timezone.now()
            if old_status == 'watching':
                show.watch_count += 1
            # Create life event for finishing the show
            LifeEvent.objects.create(
                title=f"✅ Finished watching {show.title}",
                description=f"Completed watching {show.title}",
                date=timezone.now().date(),
                show=show
            )
        
        show.save()
    
    return redirect('portfolio:shows')

@login_required
@staff_member_required
@require_POST
def update_book_status(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    new_status = request.POST.get('new_status')
    
    if new_status in ['reading', 'read']:
        old_status = book.status
        book.status = new_status
        book.save()
        
        # Create life event for status change
        if new_status in ['reading', 'read']:
            LifeEvent.objects.create(
                title=f"📚 Started reading {book.title}" if new_status == 'reading'
                      else f"📖 Finished reading {book.title}",
                description=f"{'Started' if new_status == 'reading' else 'Finished'} reading {book.title} by {book.authors}",
                date=timezone.now().date(),
                book=book
            )
    
    return redirect('portfolio:books')

@login_required
@staff_member_required
@require_POST
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    title = book.title
    book.delete()
    messages.success(request, f'Removed "{title}" from your list')
    return redirect('portfolio:books')

@require_POST
def vote_book(request, book_id):
    if not request.is_ajax():
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    book = get_object_or_404(Book, id=book_id)
    book.votes += 1
    book.save()
    
    return JsonResponse({
        'votes': book.votes,
        'book_id': book_id
    }) 