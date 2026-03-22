# fix_image_paths.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from kitajalan.models import HalamanBlok

def fix_image_paths():
    blok_gambar = HalamanBlok.objects.filter(tipe='local_image')
    
    for blok in blok_gambar:
        old_path = blok.konten
        if 'http://' in old_path or 'https://' in old_path:
            # Ambil path setelah /media/
            if '/media/' in old_path:
                new_path = old_path.split('/media/')[-1]
            else:
                new_path = old_path.split('/')[-1]
                new_path = f"uploads/2026/03/07/{new_path}"
            
            blok.konten = new_path
            blok.save()
            print(f"✅ Fixed: {old_path} -> {new_path}")

if __name__ == '__main__':
    fix_image_paths()