from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('image/<int:image_id>/', views.image_detail, name='image_detail'),
    path('image/<int:image_id>/like/', views.like_image, name='like_image'),
    path('image/<int:image_id>/comment/', views.add_comment, name='add_comment'),
    path('profile/', views.user_profile, name='user_profile'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),
    path('signup/', views.signup, name='signup'),
]
