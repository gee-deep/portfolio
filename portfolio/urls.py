from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('life/', views.life_events, name='life_events'),
    path('books/', views.books, name='books'),
    path('books/search/', views.search_books, name='search_books'),
    path('books/add/<str:book_id>/', views.add_book, name='add_book'),
    path('books/update/<int:book_id>/', views.update_book_status, name='update_book_status'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),
    path('books/vote/<int:book_id>/', views.vote_book, name='vote_book'),
    path('shows/', views.shows, name='shows'),
    path('shows/vote/<int:show_id>/', views.vote_show, name='vote_show'),
    path('shows/search/', views.search_shows, name='search_shows'),
    path('shows/add/', views.search_shows, name='search_shows'),
    path('shows/add/<str:media_type>/<int:tmdb_id>/', views.add_show, name='add_show'),
    path('shows/delete/<int:show_id>/', views.delete_show, name='delete_show'),
    path('shows/downvote/<int:show_id>/', views.downvote_show, name='downvote_show'),
    path('life/add/', views.add_life_event, name='add_life_event'),
    path('life/edit/<int:event_id>/', views.edit_life_event, name='edit_life_event'),
    path('life/delete/<int:event_id>/', views.delete_life_event, name='delete_life_event'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('shows/update-status/<int:show_id>/', views.update_show_status, name='update_show_status'),
] 