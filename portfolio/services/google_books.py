import requests
from django.conf import settings

class GoogleBooksClient:
    BASE_URL = "https://www.googleapis.com/books/v1"
    
    def __init__(self):
        self.api_key = settings.GOOGLE_BOOKS_API_KEY

    def search_books(self, query, max_results=40):
        """Search for books using the Google Books API."""
        url = f"{self.BASE_URL}/volumes"
        params = {
            'q': query,
            'maxResults': max_results,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an error for bad status codes
            
            if response.status_code == 200:
                data = response.json()
                print(f"API Response: {data}")  # Debug print
                return [self._format_book_data(item) for item in data.get('items', [])]
        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")  # Debug print
            return []
        return []

    def get_book_details(self, book_id):
        """Get detailed information about a specific book."""
        url = f"{self.BASE_URL}/volumes/{book_id}"
        params = {'key': self.api_key}
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return self._format_book_data(response.json())
        return None

    def _format_book_data(self, book_data):
        """Format the book data into a consistent structure."""
        volume_info = book_data.get('volumeInfo', {})
        
        image_links = volume_info.get('imageLinks', {})
        
        # Use higher resolution image if available
        image_url = (
            image_links.get('thumbnail', '')
            .replace('zoom=1', 'zoom=2')  # Try to get higher resolution
            .replace('http://', 'https://')  # Ensure HTTPS
        )
        
        return {
            'id': book_data.get('id'),
            'title': volume_info.get('title', 'Unknown Title'),
            'authors': volume_info.get('authors', ['Unknown Author']),
            'description': volume_info.get('description', ''),
            'published_date': volume_info.get('publishedDate', ''),
            'page_count': volume_info.get('pageCount'),
            'categories': volume_info.get('categories', []),
            'rating': volume_info.get('averageRating'),
            'ratings_count': volume_info.get('ratingsCount', 0),
            'image_url': image_url,
            'language': volume_info.get('language', ''),
            'preview_link': volume_info.get('previewLink', ''),
            'info_link': volume_info.get('infoLink', ''),
            'isbn': next((id['identifier'] for id in volume_info.get('industryIdentifiers', []) 
                         if id['type'] in ['ISBN_13', 'ISBN_10']), None)
        } 