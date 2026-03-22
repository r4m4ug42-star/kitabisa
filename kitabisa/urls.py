from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect  # tambah ini
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 👉 ROOT URL (INI KUNCI NYA)
    path('', lambda request: redirect('daftar_kursus')),

    path('', include('kitajalan.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)