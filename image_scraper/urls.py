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
    LoginAPIView,
    UserInfoAPIView,
    SearchOptionsAPIView,
    AdvancedSearchAPIView,
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
    path('api/users/register/', RegisterAPIView.as_view(), name='api-register'),
    path('api/users/login/', LoginAPIView.as_view(), name='api-login'),
    path('api/users/me/', UserInfoAPIView.as_view(), name='api-user-info'),
    path('api/users/profile/', ProfileAPIView.as_view(), name='api-profile'),
    # Search options endpoint
    path('api/search/options/', SearchOptionsAPIView.as_view(), name='api-search-options'),
    # Token auth endpoint - redirect to login view
    path('api/api-token-auth/', LoginAPIView.as_view(), name='api-token-auth'),
    # Advanced search endpoint
    path('api/advanced-search/', AdvancedSearchAPIView.as_view(), name='api-advanced-search'),
    # CRUD and custom actions
    path('api/', include(router.urls)),  # API endpoints
    # Comment endpoint via ModelViewSet action
    # enable likes via /api/images/{id}/like/
    path('', include('scraper.urls')),  # Web views
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', signup, name='signup'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
