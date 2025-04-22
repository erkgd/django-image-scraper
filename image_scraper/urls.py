from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from scraper.views import signup
from rest_framework.routers import DefaultRouter
from scraper.api_views import (
    ImageViewSet,
    CommentViewSet,
    LikeViewSet,
    SearchHistoryViewSet,
    RegisterAPIView,
    ProfileAPIView,
)

# API router setup
router = DefaultRouter()
router.register(r'images', ImageViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'history', SearchHistoryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # User API endpoints
    path('api/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/profile/', ProfileAPIView.as_view(), name='api-profile'),
    # CRUD and custom actions
    path('api/', include(router.urls)),  # API endpoints
    path('', include('scraper.urls')),  # Web views
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', signup, name='signup'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
