# kitabisa/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),

    # Debug URL ping → pasti jalan
    path('ping/', lambda request: HttpResponse("OK")),

    # Sertakan semua URL app kitajalan di bawah root
    path('', include('kitajalan.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)