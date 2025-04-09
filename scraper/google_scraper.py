import requests
import json
import re
import time
import random
import logging
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from .utils import get_image_metadata

# Set up logging
logger = logging.getLogger(__name__)

def scrape_google_images(query, copyright_filter=None, transparent_only=False, max_results=20):
    """Scrape images from Google with a more robust approach"""
    print(f"DEBUG: Iniciando scraping real de Google con query='{query}'")
    images = []
    
    # Build Google Images search URL with filters
    search_params = {
        'q': query,
        'tbm': 'isch',  # Image search
    }
    
    # Add copyright filter if specified
    if copyright_filter:
        if copyright_filter == 'free':
            search_params['tbs'] = 'il:cl'  # Creative Commons licenses
        elif copyright_filter == 'commercial':
            search_params['tbs'] = 'sur:fc'  # Commercial licenses
    
    # Add transparent filter if specified
    if transparent_only:
        if 'tbs' in search_params:
            search_params['tbs'] += ',ic:trans'  # Transparent images
        else:
            search_params['tbs'] = 'ic:trans'
    
    search_url = "https://www.google.com/search?" + urlencode(search_params)
    print(f"DEBUG: URL de búsqueda: {search_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        print("DEBUG: Enviando solicitud a Google...")
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"DEBUG: Respuesta recibida, código: {response.status_code}")
        
        if response.status_code != 200:
            print(f"DEBUG: Error en la respuesta: {response.status_code}")
            return images
        
        # Usamos una estrategia más robusta para extraer la información de las imágenes
        print("DEBUG: Analizando respuesta HTML...")
        
        # Método 1: Buscar data-src en las etiquetas img
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            try:
                if img.get('data-src') and 'google' not in img.get('data-src'):
                    img_url = img.get('data-src')
                    
                    # Si encontramos una URL de imagen válida
                    if img_url:
                        # Intenta obtener el título de la imagen
                        parent_div = img.find_parent('div')
                        title = 'Imagen para: ' + query  # Título predeterminado
                        
                        if parent_div:
                            title_elem = parent_div.find('h3')
                            if title_elem:
                                title = title_elem.get_text()
                        
                        # Crea el objeto de imagen
                        img_data = {
                            'title': title,
                            'url': img_url,
                            'thumbnail_url': img_url,  # Usamos la misma URL como miniatura
                            'source_url': search_url,  # Por defecto, usamos la URL de búsqueda
                            'width': None,
                            'height': None,
                            'file_size': None,
                            'file_type': 'jpg' if '.jpg' in img_url else ('png' if '.png' in img_url else 'unknown'),
                            'copyright_status': copyright_filter or 'unknown',
                            'is_transparent': transparent_only
                        }
                        
                        # Intentamos obtener metadatos adicionales
                        try:
                            metadata = get_image_metadata(img_url)
                            img_data.update(metadata)
                        except Exception as e:
                            print(f"DEBUG: Error obteniendo metadatos: {str(e)}")
                        
                        images.append(img_data)
                        print(f"DEBUG: Imagen encontrada (método 1): {img_url[:50]}...")
                        
                        if len(images) >= max_results:
                            break
            except Exception as e:
                continue
        
        # Si no encontramos suficientes imágenes, probamos el método 2: JSON en scripts
        if len(images) < max_results:
            print("DEBUG: Probando método 2 - búsqueda JSON...")
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string and 'AF_initDataCallback' in script.string:
                    try:
                        # Intentamos extraer un bloque JSON válido
                        matches = re.findall(r'(\["https?://[^"]+?\.(?:jpg|jpeg|png|gif|webp)",[^]]+\])', script.string)
                        
                        for match in matches:
                            try:
                                data = json.loads('[' + match + ']')
                                
                                if isinstance(data, list) and len(data) > 0:
                                    for item in data:
                                        if isinstance(item, list) and len(item) > 0:
                                            # El primer elemento suele ser la URL
                                            for element in item:
                                                if isinstance(element, str) and element.startswith('http') and ('jpg' in element or 'jpeg' in element or 'png' in element or 'gif' in element):
                                                    img_url = element
                                                    
                                                    img_data = {
                                                        'title': f"Resultado para: {query}",
                                                        'url': img_url,
                                                        'thumbnail_url': img_url,
                                                        'source_url': search_url,
                                                        'width': None,
                                                        'height': None,
                                                        'file_size': None,
                                                        'file_type': 'jpg' if '.jpg' in img_url else ('png' if '.png' in img_url else 'unknown'),
                                                        'copyright_status': copyright_filter or 'unknown',
                                                        'is_transparent': transparent_only
                                                    }
                                                    
                                                    # No agregar duplicados
                                                    if not any(img['url'] == img_url for img in images):
                                                        images.append(img_data)
                                                        print(f"DEBUG: Imagen encontrada (método 2): {img_url[:50]}...")
                                                        
                                                        if len(images) >= max_results:
                                                            break
                            except:
                                continue
                    except:
                        continue
        
        # Método 3: Como último recurso, buscar URLs directamente en el HTML
        if len(images) < max_results:
            print("DEBUG: Probando método 3 - extracción de URLs...")
            # Buscar URLs de imágenes en el HTML
            img_urls = re.findall(r'https?://[^"\']+\.(?:jpg|jpeg|png|gif|webp)', response.text)
            
            for img_url in img_urls:
                # Filtrar URLs de Google y duplicados
                if 'google' not in img_url and not any(img['url'] == img_url for img in images):
                    img_data = {
                        'title': f"Resultado para: {query}",
                        'url': img_url,
                        'thumbnail_url': img_url,
                        'source_url': search_url,
                        'width': None,
                        'height': None,
                        'file_size': None,
                        'file_type': 'jpg' if '.jpg' in img_url else ('png' if '.png' in img_url else 'unknown'),
                        'copyright_status': copyright_filter or 'unknown',
                        'is_transparent': transparent_only
                    }
                    
                    images.append(img_data)
                    print(f"DEBUG: Imagen encontrada (método 3): {img_url[:50]}...")
                    
                    if len(images) >= max_results:
                        break
        
        print(f"DEBUG: Scraping completado. Se encontraron {len(images)} imágenes.")
    
    except Exception as e:
        print(f"DEBUG: Error durante el scraping: {str(e)}")
    
    return images[:max_results]
