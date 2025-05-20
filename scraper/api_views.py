from django.contrib.auth import get_user_model, authenticate
from rest_framework import viewsets  # Add viewsets import
from rest_framework.decorators import action  # For custom viewset actions
from rest_framework.permissions import AllowAny, IsAuthenticated  # Added IsAuthenticated
from rest_framework.response import Response  # Added Response
from rest_framework.views import APIView  # Added APIView import
from rest_framework.authtoken.models import Token
from .models import Image, Like, Comment, SearchHistory  # Ensure models imported
from django.db import IntegrityError
from django.db.models import Q  # For fallback database searches in advanced search
from rest_framework.pagination import PageNumberPagination  # For paginating search history
from .serializers import ImageSerializer, CommentSerializer, LikeSerializer, SearchHistorySerializer  # Add missing serializers
from .utils import download_image
from .google_scraper import scrape_google_images

User = get_user_model()

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'detail': 'Username and password required.'}, status=400)
        try:
            user = User.objects.create_user(username=username, password=password)
        except IntegrityError:
            return Response(
                {'detail': 'Username already taken', 'error_type': 'username_exists'},
                status=400
            )
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'id': user.id, 'username': user.username})

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Log the received data for debugging (removing password for security)
        print(f"Login attempt for username: {username}")
        print(f"Request data: {request.data}")
        
        if not username or not password:
            return Response({'detail': 'Username and password required.'}, status=400)
        
        # Attempt authentication
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'id': user.id, 'username': user.username})
        
        # Enhanced error response
        return Response({
            'detail': 'Invalid credentials',
            'username_exists': User.objects.filter(username=username).exists(),
            'error_type': 'authentication_failed'
        }, status=400)

class UserInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'id': request.user.id,
            'username': request.user.username,
        })

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # get liked images
        likes = Like.objects.filter(user=request.user)
        liked_images = [like.image for like in likes]
        liked_data = ImageSerializer(liked_images, many=True).data
        # comments
        user_comments = Comment.objects.filter(user=request.user)
        comments_data = CommentSerializer(user_comments, many=True).data
        # search history
        history = SearchHistory.objects.filter(user=request.user)
        history_data = SearchHistorySerializer(history, many=True).data
        return Response({
            'user': {'id': request.user.id, 'username': request.user.username},
            'liked_images': liked_data,
            'comments': comments_data,
            'search_history': history_data,
        })

# CRUD ViewSets for resources
class CustomPagination(PageNumberPagination):
    """Paginate results with `items` and `pagination` keys"""
    page_size = 8
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'items': data,
            'pagination': {
                'total': self.page.paginator.count,
                'page': self.page.number,
                'pages': self.page.paginator.num_pages,
            }
        })

class ImageViewSet(viewsets.ModelViewSet):
    # Default to newest images first
    queryset = Image.objects.all().order_by('-created_at')
    serializer_class = ImageSerializer
    pagination_class = CustomPagination  # Use custom pagination for frontend

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        image = self.get_object()
        # Toggle like
        like_obj, created = Like.objects.get_or_create(user=request.user, image=image)
        if not created:
            # Already liked: unlike
            like_obj.delete()
            liked = False
        else:
            liked = True
        # Count current likes
        likes_count = Like.objects.filter(image=image).count()
        return Response({'liked': liked, 'likes_count': likes_count})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        """Add a comment to an image"""
        image = self.get_object()
        text = request.data.get('text')
        if not text:
            return Response({'detail': 'Comment text is required.'}, status=400)
        # Create comment
        comment = Comment.objects.create(user=request.user, image=image, text=text)
        # Serialize and return the new comment
        serialized = CommentSerializer(comment)
        return Response(serialized.data)
    
    def retrieve(self, request, *args, **kwargs):
        # Override retrieve to include comments, like count, and userLiked
        image = self.get_object()
        # Base image data
        data = ImageSerializer(image).data
        # Comments list
        comments_list = Comment.objects.filter(image=image).order_by('-created_at')
        comments_data = CommentSerializer(comments_list, many=True).data
        # Likes count
        likes_count = Like.objects.filter(image=image).count()
        # Has current user liked?
        user_liked = False
        if request.user and request.user.is_authenticated:
            user_liked = Like.objects.filter(image=image, user=request.user).exists()
        # Inject into response with camelCase keys
        data['comments'] = comments_data
        data['commentsCount'] = comments_list.count()
        data['likesCount'] = likes_count
        data['userLiked'] = user_liked
        return Response(data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 100

class SearchHistoryViewSet(viewsets.ModelViewSet):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
    pagination_class = StandardResultsSetPagination  # Paginate search history

class SearchOptionsAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Return search options like supported categories, sizes, etc.
        return Response({
            'categories': ['nature', 'people', 'technology', 'animals', 'food', 'travel'],
            'sizes': ['small', 'medium', 'large'],
            'orientations': ['portrait', 'landscape', 'square'],
            'colors': ['red', 'green', 'blue', 'yellow', 'black', 'white']
        })
 
class AdvancedSearchAPIView(APIView):
    """API view for advanced image search"""
    permission_classes = [AllowAny]
    def get(self, request):
        query = request.GET.get('query')
        if not query:
            return Response({'detail': 'Query parameter is required.'}, status=400)
        try:
            max_results = int(request.GET.get('max_results', 20))
        except ValueError:
            max_results = 20
        transparent_only = request.GET.get('transparent_only', 'false').lower() == 'true'
        copyright_filter = request.GET.get('copyright_filter')
        # Log search history if authenticated
        if request.user and request.user.is_authenticated:
            SearchHistory.objects.create(
                user=request.user,
                query=query,
                filters={
                    'copyright_filter': copyright_filter,
                    'transparent_only': transparent_only
                }
            )
        # Perform scraping
        scraped = scrape_google_images(query, copyright_filter, transparent_only, max_results=max_results)
        images = []
        for data in scraped:
            obj = Image.objects.filter(url=data['url']).first()
            if not obj:
                obj = Image.objects.create(
                    title=data.get('title', ''),
                    url=data['url'],
                    source_url=data.get('source_url', ''),
                    thumbnail_url=data.get('thumbnail_url', ''),
                    is_transparent=data.get('is_transparent', False),
                    copyright_status=data.get('copyright_status', 'unknown'),
                    width=data.get('width'),
                    height=data.get('height'),
                    file_size=data.get('file_size'),
                    file_type=data.get('file_type')
                )
                local = download_image(data['url'], obj.id)
                if local:
                    obj.local_path = local
                    obj.save()
            images.append(obj)
        # Fallback to database search if none
        if not images:
            qs = Image.objects.filter(
                Q(title__icontains=query) | Q(url__icontains=query)
            )
            if transparent_only:
                qs = qs.filter(is_transparent=True)
            if copyright_filter:
                qs = qs.filter(copyright_status=copyright_filter)
            images = list(qs.order_by('-created_at')[:max_results])
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)
