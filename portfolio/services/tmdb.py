import requests
from django.conf import settings

class TMDBClient:
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = 'https://api.themoviedb.org/3'
        self.image_base_url = 'https://image.tmdb.org/t/p'

    def _make_request(self, endpoint, params=None):
        """Helper method to make API requests"""
        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        # Add API key to all requests
        params['api_key'] = self.api_key
        
        try:
            print(f"Making request to: {url}")
            print(f"With params: {params}")
            
            response = requests.get(url, params=params)
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text[:500]}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {e}")
            return {'results': []}

    def search_movies(self, query):
        """Search for movies"""
        params = {
            'query': query,
            'language': 'en-US',
            'page': 1,
            'include_adult': False
        }
        data = self._make_request('search/movie', params)
        
        results = []
        for item in data.get('results', []):
            result = {
                'id': item['id'],
                'title': item['title'],
                'media_type': 'movie',
                'release_date': item.get('release_date', ''),
                'rating': item.get('vote_average'),
                'image_url': f"{self.image_base_url}{item.get('poster_path')}" if item.get('poster_path') else None,
                'overview': item.get('overview', '')
            }
            results.append(result)
        return results

    def search_tv(self, query):
        """Search for TV shows"""
        params = {
            'query': query,
            'language': 'en-US',
            'page': 1,
            'include_adult': False
        }
        data = self._make_request('search/tv', params)
        
        results = []
        for item in data.get('results', []):
            result = {
                'id': item['id'],
                'title': item['name'],
                'media_type': 'tv',
                'release_date': item.get('first_air_date', ''),
                'rating': item.get('vote_average'),
                'image_url': f"{self.image_base_url}{item.get('poster_path')}" if item.get('poster_path') else None,
                'overview': item.get('overview', '')
            }
            results.append(result)
        return results

    def search_multi(self, query, media_type='all'):
        """Search for movies and TV shows"""
        if media_type == 'all':
            endpoint = 'search/multi'
        else:
            endpoint = f'search/{media_type}'
            
        params = {
            'api_key': self.api_key,
            'query': query,
            'page': 1
        }
        
        response = requests.get(f'{self.base_url}/{endpoint}', params=params)
        if response.ok:
            results = response.json().get('results', [])
            formatted_results = []
            
            for item in results:
                # Add media_type if not present (when searching specific type)
                if 'media_type' not in item:
                    item['media_type'] = media_type
                
                if item['media_type'] in ['movie', 'tv']:
                    formatted_results.append({
                        'id': item['id'],
                        'title': item.get('title') or item.get('name'),
                        'media_type': item['media_type'],
                        'release_date': item.get('release_date') or item.get('first_air_date', ''),
                        'overview': item.get('overview', ''),
                        'poster_path': f'{self.image_base_url}/w500{item["poster_path"]}' if item.get('poster_path') else '',
                        'vote_average': item.get('vote_average', 0)
                    })
            
            return formatted_results
        return []

    def get_details(self, media_type, tmdb_id):
        """Get detailed information about a movie or TV show"""
        endpoint = f'/{media_type}/{tmdb_id}'
        params = {
            'api_key': self.api_key,
            'append_to_response': 'credits,videos,images'
        }
        
        response = requests.get(f'{self.base_url}{endpoint}', params=params)
        if response.ok:
            data = response.json()
            return {
                'title': data.get('title') or data.get('name'),
                'original_title': data.get('original_title') or data.get('original_name'),
                'overview': data.get('overview', ''),
                'image_url': f'{self.image_base_url}/w500{data.get("poster_path")}' if data.get('poster_path') else '',
                'backdrop_url': f'{self.image_base_url}/original{data.get("backdrop_path")}' if data.get('backdrop_path') else '',
                'rating': data.get('vote_average'),
                'release_date': data.get('release_date') or data.get('first_air_date'),
                'genres': data.get('genres', []),
                'runtime': data.get('runtime') or (data.get('episode_run_time', [0])[0] if data.get('episode_run_time') else 0),
                'language': data.get('original_language', ''),
                'production_companies': data.get('production_companies', []),
                'created_by': data.get('created_by', []),  # For TV shows
                'number_of_seasons': data.get('number_of_seasons'),  # For TV shows
                'number_of_episodes': data.get('number_of_episodes'),  # For TV shows
                'credits': data.get('credits', {})
            }
        return None

    def get_credits(self, media_type, tmdb_id):
        """Get cast and crew information"""
        endpoint = f'/{media_type}/{tmdb_id}/credits'
        params = {'api_key': self.api_key}
        
        response = requests.get(f'{self.base_url}{endpoint}', params=params)
        if response.ok:
            return response.json()
        return None

    def _format_image_url(self, path, size='w500'):
        """Helper method to format image URLs"""
        if not path:
            return ''
        return f'{self.image_base_url}/{size}{path}' 