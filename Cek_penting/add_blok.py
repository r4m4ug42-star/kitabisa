# add_blok.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from kitajalan.models import HalamanMateri, HalamanBlok

def add_blok_to_halaman(halaman_slug):
    try:
        # Ambil halaman
        halaman = HalamanMateri.objects.get(slug=halaman_slug)
        print(f"\n📄 Halaman: {halaman.judul}")
        
        # Cek blok yang sudah ada
        blok_count = HalamanBlok.objects.filter(halaman=halaman).count()
        print(f"📊 Blok yang sudah ada: {blok_count}")
        
        if blok_count == 0:
            # Tambah blok text
            blok_text = HalamanBlok.objects.create(
                halaman=halaman,
                tipe='text',
                konten='''# Apa Itu Django

Django adalah web framework Python tingkat tinggi yang mendorong pengembangan cepat dan desain yang bersih.

## Fitur Utama Django

- **Cepat**: Django dirancang untuk membantu pengembang membuat aplikasi secepat mungkin
- **Aman**: Django membantu pengembang menghindari banyak kesalahan keamanan umum
- **Skalabilitas**: Beberapa situs tersibuk di dunia menggunakan Django
- **Lengkap**: Django menyediakan hampir semua yang Anda butuhkan
''',
                urutan=1
            )
            print("✅ Blok text ditambahkan")
            
            # Tambah blok video
            blok_video = HalamanBlok.objects.create(
                halaman=halaman,
                tipe='video',
                konten='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                urutan=2
            )
            print("✅ Blok video ditambahkan")
            
            return True
        else:
            print("⏩ Halaman sudah memiliki blok, tidak perlu ditambah")
            return False
            
    except HalamanMateri.DoesNotExist:
        print(f"❌ Halaman dengan slug '{halaman_slug}' tidak ditemukan")
        return False

if __name__ == '__main__':
    # Daftar halaman yang perlu ditambah blok
    halaman_list = [
        'apa-itu-django',
        'install-django',
        'kelebihan-django',
        'sejarah-dan-perkembangan-django'
    ]
    
    print("="*50)
    print("MULAI MENAMBAH BLOK KE HALAMAN")
    print("="*50)
    
    for slug in halaman_list:
        add_blok_to_halaman(slug)
        print("-"*30)
    
    print("\n✅ SELESAI! Semua halaman telah diproses.")