import requests
import json
import logging
import os
import random
from urllib.parse import urlencode
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)

# You should get your own API key from https://pixabay.com/api/docs/
PIXABAY_API_KEY = "YOUR_PIXABAY_API_KEY_HERE"  # Reemplaza con tu API key

def search_images_api(query, copyright_filter=None, transparent_only=False, max_results=20):
    """
    Search for images using Pixabay API instead of scraping Google
    """
    print(f"DEBUG: Starting API search with query='{query}', copyright_filter='{copyright_filter}', transparent_only={transparent_only}")
    images = []
    
    # Configure Pixabay API parameters
    search_params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": max_results
    }
    
    # Apply filters
    if transparent_only:
        search_params["image_type"] = "transparent"
    
    # Set copyright filter (Pixabay has different options)
    if copyright_filter:
        # All Pixabay images are free for commercial use with attribution
        # But we can still map our filter categories
        if copyright_filter in ['free', 'commercial', 'modification']:
            search_params["safesearch"] = "true"
    
    api_url = "https://pixabay.com/api/"
    
    print(f"DEBUG: API URL (without key): {api_url}?{urlencode({k:v for k,v in search_params.items() if k != 'key'})}")
    
    try:
        # Make the API request
        response = requests.get(api_url, params=search_params)
        print(f"DEBUG: API Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"DEBUG: API returned {len(data.get('hits', []))} results")
            
            # Process each image
            for item in data.get("hits", []):
                img_data = {
                    "title": item.get("tags", "Untitled Image").split(",")[0],
                    "url": item.get("largeImageURL"),
                    "source_url": item.get("pageURL"),
                    "thumbnail_url": item.get("previewURL"),
                    "width": item.get("imageWidth"),
                    "height": item.get("imageHeight"),
                    "file_size": None,  # Pixabay doesn't provide file size
                    "file_type": "jpg",  # Default to jpg, could parse from URL
                    "is_transparent": transparent_only,
                    "copyright_status": copyright_filter or "free"  # All Pixabay images are free to use
                }
                
                images.append(img_data)
                
                # For debugging, just show the first one
                if len(images) == 1:
                    print(f"DEBUG: First image data: {img_data}")
        else:
            print(f"DEBUG: API error response: {response.text}")
    
    except Exception as e:
        print(f"DEBUG: Exception in API call: {str(e)}")
        logger.error(f"Error searching images from API: {e}")
    
    return images

# Esta es una implementación de reserva que usa Pexels en lugar de Pixabay (por si acaso)
def search_images_pexels(query, max_results=20):
    """Search for images using Pexels API"""
    # Pexels API documentation: https://www.pexels.com/api/documentation/
    API_KEY = "YOUR_PEXELS_API_KEY_HERE"  # Reemplaza con tu API key
    headers = {
        "Authorization": API_KEY
    }
    
    search_url = f"https://api.pexels.com/v1/search?query={query}&per_page={max_results}"
    
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            images = []
            
            for photo in data.get("photos", []):
                img_data = {
                    "title": photo.get("alt", "Image from Pexels"),
                    "url": photo["src"]["original"],
                    "source_url": photo["url"],
                    "thumbnail_url": photo["src"]["medium"],
                    "width": photo["width"],
                    "height": photo["height"],
                    "file_size": None,
                    "file_type": "jpg",
                    "is_transparent": False,
                    "copyright_status": "free"
                }
                images.append(img_data)
                
            return images
    except Exception as e:
        logger.error(f"Error searching images from Pexels: {e}")
    
    return []

# Implementación de demo que retorna imágenes de muestra (por si no tienes API keys)
def demo_images(query, max_results=20):
    """Return demo images for testing purposes"""
    images = []
    
    # Crear URLs de imágenes demo
    for i in range(min(10, max_results)):
        width = random.choice([800, 1024, 1200, 1600])
        height = random.choice([600, 768, 900, 1200])
        
        img_data = {
            "title": f"Demo Image for '{query}' #{i+1}",
            "url": f"https://picsum.photos/{width}/{height}?random={i}",
            "source_url": "https://picsum.photos/",
            "thumbnail_url": f"https://picsum.photos/200/150?random={i}",
            "width": width,
            "height": height,
            "file_size": None,
            "file_type": "jpg",
            "is_transparent": False,
            "copyright_status": "free"
        }
        
        images.append(img_data)
    
    print(f"DEBUG: Returning {len(images)} demo images")
    return images
