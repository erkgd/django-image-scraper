from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from scraper.views import signup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('scraper.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', signup, name='signup'),  # Agregamos la ruta signup al sistema de autenticación
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
