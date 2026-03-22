# update_video.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from kitajalan.models import HalamanMateri, HalamanBlok

def update_video_url(halaman_slug, new_url):
    try:
        halaman = HalamanMateri.objects.get(slug=halaman_slug)
        print(f"\n📄 Halaman: {halaman.judul}")
        
        blok_video = HalamanBlok.objects.filter(
            halaman=halaman, 
            tipe='video'
        ).first()
        
        if blok_video:
            old_url = blok_video.konten
            blok_video.konten = new_url
            blok_video.save()
            print(f"  ✅ Video updated!")
            print(f"     Old: {old_url}")
            print(f"     New: {blok_video.konten}")
        else:
            print(f"  ❌ Tidak ada blok video untuk halaman ini")
            
    except HalamanMateri.DoesNotExist:
        print(f"❌ Halaman '{halaman_slug}' tidak ditemukan")

if __name__ == '__main__':
    # Update video untuk halaman Install Django
    update_video_url(
        halaman_slug='install-django',
        new_url='https://www.youtube.com/watch?v=F5mRW0jo-U4'
    )
    
    # Update juga untuk halaman lain jika perlu
    update_video_url(
        halaman_slug='apa-itu-django',
        new_url='https://www.youtube.com/watch?v=rHux0gMZ3Eg'
    )