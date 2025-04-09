import requests
from bs4 import BeautifulSoup
import json
import re
from io import BytesIO
from PIL import Image as PILImage
from urllib.parse import urlencode, urlparse, parse_qs
import time
import random
from django.conf import settings
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)

def is_transparent(image_url):
    """Check if an image has transparency"""
    try:
        response = requests.get(image_url, stream=True, timeout=5)
        if response.status_code == 200:
            img = PILImage.open(BytesIO(response.content))
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                return True
    except Exception as e:
        logger.error(f"Error checking transparency: {e}")
    return False

def get_image_metadata(image_url):
    """Get image metadata like dimensions and file size"""
    metadata = {
        'width': None,
        'height': None,
        'file_size': None,
        'file_type': None
    }
    
    try:
        # Get file size from headers
        response = requests.head(image_url, timeout=5)
        if response.status_code == 200:
            metadata['file_size'] = int(response.headers.get('Content-Length', 0))
            
            # Get file type from Content-Type header
            content_type = response.headers.get('Content-Type', '')
            if 'image/' in content_type:
                metadata['file_type'] = content_type.split('/')[-1]
        
        # If file type not determined from headers, try from URL
        if not metadata['file_type']:
            parsed_url = urlparse(image_url)
            path = parsed_url.path.lower()
            if path.endswith('.jpg') or path.endswith('.jpeg'):
                metadata['file_type'] = 'jpeg'
            elif path.endswith('.png'):
                metadata['file_type'] = 'png'
            elif path.endswith('.gif'):
                metadata['file_type'] = 'gif'
            elif path.endswith('.webp'):
                metadata['file_type'] = 'webp'
            elif path.endswith('.svg'):
                metadata['file_type'] = 'svg'
        
        # Get dimensions by downloading the image
        img_response = requests.get(image_url, stream=True, timeout=5)
        if img_response.status_code == 200:
            img = PILImage.open(BytesIO(img_response.content))
            metadata['width'], metadata['height'] = img.size
            
            # Check transparency while we have the image open
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                metadata['is_transparent'] = True
            else:
                metadata['is_transparent'] = False
                
    except Exception as e:
        logger.error(f"Error getting image metadata: {e}")
    
    return metadata

def download_image(image_url, image_id):
    """Download image and save to media directory"""
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        if response.status_code == 200:
            # Determine file extension
            content_type = response.headers.get('Content-Type', '')
            if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                ext = 'jpg'
            elif 'image/png' in content_type:
                ext = 'png'
            elif 'image/gif' in content_type:
                ext = 'gif'
            elif 'image/webp' in content_type:
                ext = 'webp'
            elif 'image/svg+xml' in content_type:
                ext = 'svg'
            else:
                # Default to jpg if can't determine
                ext = 'jpg'
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'images'), exist_ok=True)
            
            # Save the image
            file_path = os.path.join(settings.MEDIA_ROOT, 'images', f"{image_id}.{ext}")
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Return the relative path for database storage
            return f"images/{image_id}.{ext}"
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
    
    return None

def scrape_images(query, copyright_filter=None, transparent_only=False, max_results=20):
    """Scrape images from Google with filters"""
    print(f"DEBUG: Starting scrape_images with query='{query}', copyright_filter='{copyright_filter}', transparent_only={transparent_only}")
    images = []
    
    # Build Google Images search URL with filters
    search_params = {
        'q': query,
        'tbm': 'isch',  # Image search
    }
    
    tbs_params = []
    
    # Add copyright filter
    if copyright_filter:
        if copyright_filter == 'free':
            tbs_params.append('il:cl')  # Creative Commons licenses
        elif copyright_filter == 'commercial':
            tbs_params.append('il:ol')  # Commercial & other licenses
        elif copyright_filter == 'noncommercial':
            tbs_params.append('il:cl')  # Creative Commons licenses
        elif copyright_filter == 'modification':
            tbs_params.append('il:cl')  # Creative Commons licenses with modification
    
    # Add transparent filter if needed
    if transparent_only:
        tbs_params.append('ic:trans')  # Transparent background
    
    # Combine tbs parameters
    if tbs_params:
        search_params['tbs'] = ','.join(tbs_params)
    
    search_url = f"https://www.google.com/search?{urlencode(search_params)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # Add a delay to avoid being blocked
        time.sleep(random.uniform(0.5, 1.5))
        
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find script tags containing image data
        scripts = soup.find_all('script')
        image_data = []
        
        for script in scripts:
            if script.string and 'AF_initDataCallback' in script.string:
                # Extract the JSON data
                json_str = re.search(r'AF_initDataCallback$$({.*?})$$;', script.string, re.DOTALL)
                if json_str:
                    try:
                        data = json.loads(json_str.group(1))
                        if 'data' in data and isinstance(data['data'], list):
                            # The structure of Google's JSON can change, so we need to find the right data array
                            for item in data['data']:
                                if isinstance(item, list) and len(item) > 1:
                                    for subitem in item:
                                        if isinstance(subitem, list) and len(subitem) > 1:
                                            # This is likely the image data array
                                            image_data = extract_image_data(subitem)
                                            if image_data:
                                                break
                    except json.JSONDecodeError:
                        continue
        
        # Process the extracted image data
        for img in image_data[:max_results]:
            # Skip if we don't have a URL
            if 'url' not in img:
                continue
                
            # Get metadata for the image
            metadata = get_image_metadata(img['url'])
            img.update(metadata)
            
            # Skip if transparent filter is on but image is not transparent
            if transparent_only and not img.get('is_transparent', False):
                continue
                
            # Set copyright status based on filter
            if copyright_filter:
                img['copyright_status'] = copyright_filter
            else:
                img['copyright_status'] = 'unknown'
                
            images.append(img)
            
            # Break if we have enough images
            if len(images) >= max_results:
                break
                
    except Exception as e:
        logger.error(f"Error scraping images: {e}")
    
    return images

def extract_image_data(data):
    """Extract image data from Google's JSON structure"""
    images = []
    
    try:
        for item in data:
            if isinstance(item, list) and len(item) > 1:
                # Try to find image information in this subarray
                img_data = {}
                
                # Look for image URL
                for subitem in item:
                    if isinstance(subitem, str) and subitem.startswith('http') and ('jpg' in subitem or 'jpeg' in subitem or 'png' in subitem or 'gif' in subitem):
                        img_data['url'] = subitem
                        break
                
                # Skip if no URL found
                if 'url' not in img_data:
                    continue
                
                # Look for title
                for subitem in item:
                    if isinstance(subitem, str) and not subitem.startswith('http'):
                        img_data['title'] = subitem
                        break
                
                if 'title' not in img_data:
                    img_data['title'] = 'Untitled Image'
                
                # Look for source URL
                for subitem in item:
                    if isinstance(subitem, str) and subitem.startswith('http') and not (subitem.endswith('.jpg') or subitem.endswith('.jpeg') or subitem.endswith('.png') or subitem.endswith('.gif')):
                        img_data['source_url'] = subitem
                        break
                
                if 'source_url' not in img_data:
                    img_data['source_url'] = img_data['url']
                
                # Use the same URL for thumbnail
                img_data['thumbnail_url'] = img_data['url']
                
                images.append(img_data)
    except Exception as e:
        logger.error(f"Error extracting image data: {e}")
    
    return images

def get_similar_images(image_url, max_results=12):
    """Find similar images based on an existing image URL"""
    images = []
    
    search_params = {
        'tbs': 'simg:CAQSgAIJnvqRvGYV4UEa9AELELCMpwgaOgo4CAQSFP0l_1TtJO0k-iXtJO0k_1T9JP0kGhoIAxIUCecF5wXnBecF5wXnBecF5wXnBRoHsgQDCAQgBg',
        'tbm': 'isch',
        'sa': 'X',
        'ved': '2ahUKEwjX0eLQ0oLvAhUC_RoKHYeQDMsQ2A4oAXoECAEQMw',
        'biw': '1903',
        'bih': '969'
    }
    
    # Add the image URL as the search query
    search_params['q'] = f"similar to:{image_url}"
    
    search_url = f"https://www.google.com/search?{urlencode(search_params)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # Add a delay to avoid being blocked
        time.sleep(random.uniform(0.5, 1.5))
        
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        # Use the same extraction logic as in scrape_images
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.string and 'AF_initDataCallback' in script.string:
                json_str = re.search(r'AF_initDataCallback$$({.*?})$$;', script.string, re.DOTALL)
                if json_str:
                    try:
                        data = json.loads(json_str.group(1))
                        if 'data' in data and isinstance(data['data'], list):
                            for item in data['data']:
                                if isinstance(item, list) and len(item) > 1:
                                    for subitem in item:
                                        if isinstance(subitem, list) and len(subitem) > 1:
                                            image_data = extract_image_data(subitem)
                                            if image_data:
                                                images.extend(image_data[:max_results])
                                                break
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        logger.error(f"Error finding similar images: {e}")
    
    return images[:max_results]
