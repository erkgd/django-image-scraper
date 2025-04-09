import json
import requests
from bs4 import BeautifulSoup
from PIL import Image as PILImage
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q

from .models import Image, Like, Comment, SearchHistory
from .forms import SearchForm, CommentForm, SignUpForm
from .utils import download_image, get_similar_images
from .google_scraper import scrape_google_images

def index(request):
    print("DEBUG: Index view called - Method:", request.method)
    form = SearchForm()
    images = []
    
    if request.method == 'GET' and 'query' in request.GET:
        print("DEBUG: Les", request.GET.get('query'))
        print("DEBUG: Search query detected:", request.GET.get('query'))
        form = SearchForm(request.GET)
        print("DEBUG: Form valid status:", form.is_valid())
        if form.is_valid():
            query = form.cleaned_data['query']
            copyright_filter = form.cleaned_data['copyright_filter']
            transparent_only = form.cleaned_data['transparent_only']
            print(f"DEBUG: Search parameters - Query: {query}, Copyright filter: {copyright_filter}, Transparent only: {transparent_only}")
            
            # Save search history
            if request.user.is_authenticated:
                SearchHistory.objects.create(
                    user=request.user,
                    query=query,
                    filters={
                        'copyright_filter': copyright_filter,
                        'transparent_only': transparent_only
                    }
                )
            
            # Use our improved Google Images scraper
            print(f"DEBUG: Calling scrape_google_images with query: {query}")
            scraped_images = scrape_google_images(query, copyright_filter, transparent_only, max_results=20)
            print(f"DEBUG: scrape_google_images returned {len(scraped_images)} results")
            
            # Save images to database
            for img_data in scraped_images:
                # Check if image already exists
                existing = Image.objects.filter(url=img_data['url']).first()
                print(f"DEBUG: Image URL: {img_data['url'][:30]}... - Exists in DB: {existing is not None}")
                if not existing:
                    # Create new image
                    image = Image.objects.create(
                        title=img_data['title'],
                        url=img_data['url'],
                        source_url=img_data['source_url'],
                        thumbnail_url=img_data['thumbnail_url'],
                        is_transparent=img_data.get('is_transparent', False),
                        copyright_status=img_data.get('copyright_status', 'unknown'),
                        width=img_data.get('width'),
                        height=img_data.get('height'),
                        file_size=img_data.get('file_size'),
                        file_type=img_data.get('file_type')
                    )
                    
                    # Download the image to local storage
                    local_path = download_image(img_data['url'], image.id)
                    if local_path:
                        image.local_path = local_path
                        image.save()
                    
                    images.append(image)
                else:
                    images.append(existing)
            
            # If no images were scraped, try to find from database
            if not images:
                images = Image.objects.filter(
                    Q(title__icontains=query) | 
                    Q(url__icontains=query)
                )
                
                if copyright_filter:
                    images = images.filter(copyright_status=copyright_filter)
                
                if transparent_only:
                    images = images.filter(is_transparent=True)
    
    # Get recent images if no search is performed
    if not images:
        images = Image.objects.all().order_by('-created_at')[:20]
    
    paginator = Paginator(images, 12)  # Show 12 images per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get trending images (most liked)
    trending_images = Image.objects.annotate(
        likes_count=Count('like')
    ).order_by('-likes_count')[:8]
    
    return render(request, 'scraper/index.html', {
        'form': form,
        'page_obj': page_obj,
        'trending_images': trending_images,
        'search_performed': 'query' in request.GET,
    })

def image_detail(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    comments = Comment.objects.filter(image=image).order_by('-created_at')
    user_liked = False
    
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, image=image).exists()
    
    comment_form = CommentForm()
    
    # Get similar images
    similar_images = Image.objects.filter(
        Q(copyright_status=image.copyright_status) |
        Q(is_transparent=image.is_transparent)
    ).exclude(id=image.id).order_by('?')[:6]
    
    # If we don't have enough similar images, try to find more
    if similar_images.count() < 6:
        # Try to find similar images by scraping
        scraped_similar = get_similar_images(image.url, max_results=6)
        
        # Save new similar images to database
        for img_data in scraped_similar:
            # Check if image already exists
            existing = Image.objects.filter(url=img_data['url']).first()
            if not existing:
                # Create new image
                new_image = Image.objects.create(
                    title=img_data['title'],
                    url=img_data['url'],
                    source_url=img_data['source_url'],
                    thumbnail_url=img_data['thumbnail_url'],
                    is_transparent=img_data.get('is_transparent', False),
                    copyright_status=img_data.get('copyright_status', 'unknown'),
                    width=img_data.get('width'),
                    height=img_data.get('height'),
                    file_size=img_data.get('file_size'),
                    file_type=img_data.get('file_type')
                )
                
                # Download the image to local storage
                local_path = download_image(img_data['url'], new_image.id)
                if local_path:
                    new_image.local_path = local_path
                    new_image.save()
        
        # Get updated similar images
        similar_images = Image.objects.filter(
            Q(copyright_status=image.copyright_status) |
            Q(is_transparent=image.is_transparent)
        ).exclude(id=image.id).order_by('?')[:6]
    
    return render(request, 'scraper/image_detail.html', {
        'image': image,
        'comments': comments,
        'user_liked': user_liked,
        'comment_form': comment_form,
        'similar_images': similar_images,
    })

@login_required
@require_POST
def like_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    like, created = Like.objects.get_or_create(user=request.user, image=image)
    
    if not created:
        # User already liked the image, so unlike it
        like.delete()
        liked = False
    else:
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': image.likes_count
    })

@login_required
@require_POST
def add_comment(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.image = image
        comment.save()
        
        return HttpResponseRedirect(reverse('image_detail', args=[image_id]))
    
    messages.error(request, 'Error adding comment. Please try again.')
    return HttpResponseRedirect(reverse('image_detail', args=[image_id]))

@login_required
def user_profile(request):
    liked_images = Image.objects.filter(like__user=request.user).order_by('-like__created_at')
    comments = Comment.objects.filter(user=request.user).order_by('-created_at')
    search_history = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    return render(request, 'scraper/profile.html', {
        'liked_images': liked_images,
        'comments': comments,
        'search_history': search_history,
    })

def download_image_view(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    
    # If we have a local copy, serve that
    if image.local_path:
        return redirect(image.local_path.url)
    
    # Otherwise redirect to the original URL
    return redirect(image.url)

def advanced_search(request):
    form = SearchForm()
    
    return render(request, 'scraper/advanced_search.html', {
        'form': form,
    })

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')
    else:
        form = SignUpForm()
    
    return render(request, 'scraper/signup.html', {
        'form': form
    })
