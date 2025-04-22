from django.contrib.auth import get_user_model
from rest_framework import viewsets  # Add viewsets import
from rest_framework.permissions import AllowAny, IsAuthenticated  # Added IsAuthenticated
from rest_framework.response import Response  # Added Response
from rest_framework.views import APIView  # Added APIView import
from .models import Image, Like, Comment, SearchHistory  # Ensure models imported
from .serializers import ImageSerializer, CommentSerializer, LikeSerializer, SearchHistorySerializer  # Add missing serializers

User = get_user_model()

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'detail': 'Username and password required.'}, status=400)
        user = User.objects.create_user(username=username, password=password)
        return Response({'id': user.id, 'username': user.username})

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
class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

class SearchHistoryViewSet(viewsets.ModelViewSet):
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer
