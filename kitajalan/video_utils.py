# video_utils.py
import re
from django.utils.safestring import mark_safe
from django.conf import settings

def extract_youtube_id(url):
    """
    Extract YouTube video ID from various URL formats
    """
    if not url:
        return None
    
    # Pola-pola URL YouTube yang umum
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*[&?]v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Fallback: coba ekstrak dengan regex sederhana
    match = re.search(r"v=([\w-]+)", url)
    if match:
        return match.group(1)
    
    match = re.search(r"youtu\.be/([\w-]+)", url)
    if match:
        return match.group(1)
    
    match = re.search(r"embed/([\w-]+)", url)
    if match:
        return match.group(1)
    
    return None

def get_youtube_embed_html(video_id, request=None):
    """
    Generate YouTube embed HTML with proper parameters to avoid Error 153
    """
    # Parameter untuk YouTube embed
    params = {
        'rel': '0',  # Tidak menampilkan video terkait
        'modestbranding': '1',  # Minimal branding
        'iv_load_policy': '3',  # Tidak ada anotasi
        'enablejsapi': '1',  # Enable JavaScript API
        'playsinline': '1',  # Play inline di mobile
    }
    
    # Tambahkan origin jika ada request (untuk development)
    if request:
        origin = request.build_absolute_uri('/')[:-1]
        params['origin'] = origin
    
    # Bangun query string
    query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
    
    # Gunakan youtube-nocookie.com untuk privasi lebih baik
    embed_url = f"https://www.youtube-nocookie.com/embed/{video_id}?{query_string}"
    
    return mark_safe(f'''
<div class="video-wrapper" data-video-id="{video_id}">
    <div class="video-loading" style="display: none; text-align: center; padding: 50px;">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Memuat video...</p>
    </div>
    <iframe 
        src="{embed_url}"
        class="youtube-embed"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen
        referrerpolicy="strict-origin-when-cross-origin"
        loading="lazy"
        onload="this.parentElement.classList.add('loaded')"
        onerror="handleVideoError(this)">
    </iframe>
</div>
    ''')

def get_video_error_html(url):
    """
    Generate error HTML when video cannot be loaded
    """
    return mark_safe(f'''
<div class="video-error-container">
    <div class="alert alert-warning">
        <i class="fas fa-exclamation-triangle me-2"></i>
        <strong>Video tidak dapat dimuat</strong>
        <p class="mt-2 mb-0 small">
            Jika video tidak muncul, Anda dapat 
            <a href="{url}" target="_blank" class="alert-link">
                menontonnya langsung di YouTube
            </a>
        </p>
    </div>
</div>
    ''')

def extract_vimeo_id(url):
    """
    Extract Vimeo video ID (tambahan jika diperlukan)
    """
    if not url:
        return None
    
    match = re.search(r'vimeo\.com/(\d+)', url)
    if match:
        return match.group(1)
    
    match = re.search(r'vimeo\.com/(\d+)/?', url)
    if match:
        return match.group(1)
    
    return None

def get_vimeo_embed_html(video_id):
    """
    Generate Vimeo embed HTML (tambahan jika diperlukan)
    """
    return mark_safe(f'''
<div class="video-wrapper">
    <iframe 
        src="https://player.vimeo.com/video/{video_id}?title=0&byline=0&portrait=0"
        frameborder="0"
        allow="autoplay; fullscreen; picture-in-picture"
        allowfullscreen
        loading="lazy">
    </iframe>
</div>
    ''')
