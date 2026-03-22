# check_sejarah_content.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from kitajalan.models import HalamanMateri, HalamanBlok

def check_halaman_content(slug):
    print(f"\n{'='*60}")
    print(f"CHECKING HALAMAN: {slug}")
    print('='*60)
    
    try:
        halaman = HalamanMateri.objects.get(slug=slug)
        print(f"✅ Halaman: {halaman.judul}")
        print(f"   ID: {halaman.id}")
        print(f"   Materi: {halaman.materi.judul}")
        print(f"   Slug: {halaman.slug}")
        print(f"   Urutan: {halaman.urutan}")
        print(f"   Konten Text (field konten): {halaman.konten[:100]}..." if halaman.konten else "   Konten Text: (kosong)")
        
        # Cek blok
        blok_list = HalamanBlok.objects.filter(halaman=halaman).order_by('urutan')
        print(f"\n📦 BLOK KONTEN: {blok_list.count()} blok")
        
        for i, blok in enumerate(blok_list, 1):
            print(f"\n   Blok #{i}:")
            print(f"   - ID: {blok.id}")
            print(f"   - Tipe: {blok.tipe}")
            print(f"   - Urutan: {blok.urutan}")
            print(f"   - Konten: {blok.konten[:200]}..." if blok.konten and len(blok.konten) > 200 else f"   - Konten: {blok.konten}")
            
            # Test render
            rendered = blok.render_konten()
            print(f"   - Hasil render: {rendered[:100]}..." if rendered else "   - Hasil render: (kosong)")
            
    except HalamanMateri.DoesNotExist:
        print(f"❌ Halaman dengan slug '{slug}' TIDAK DITEMUKAN!")

if __name__ == '__main__':
    check_halaman_content('sejarah-dan-perkembangan-django')