# create_sample_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from kitajalan.models import Kursus, Materi, HalamanMateri, HalamanBlok

def create_sample_data():
    # Ambil kursus
    kursus = Kursus.objects.get(slug='django-dasar')
    
    # Buat materi
    materi = Materi.objects.create(
        kursus=kursus,
        judul='Pengenalan Django',
        urutan=1,
        konten='# Pengenalan Django\n\nDjango adalah web framework Python...'
    )
    print(f"✅ Materi dibuat: {materi.judul}")
    
    # Buat halaman
    halaman = HalamanMateri.objects.create(
        materi=materi,
        judul='Apa Itu Django',
        urutan=1,
        konten='# Apa Itu Django\n\nDjango adalah...'
    )
    print(f"✅ Halaman dibuat: {halaman.judul}")
    
    # Buat blok text
    blok1 = HalamanBlok.objects.create(
        halaman=halaman,
        tipe='text',
        konten='Django adalah framework Python tingkat tinggi yang memungkinkan pengembangan web dengan cepat.',
        urutan=1
    )
    print(f"✅ Blok text dibuat")
    
    # Buat blok video (contoh)
    blok2 = HalamanBlok.objects.create(
        halaman=halaman,
        tipe='video',
        konten='https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        urutan=2
    )
    print(f"✅ Blok video dibuat")
    
    print(f"\n🎉 Sample data berhasil dibuat!")

if __name__ == '__main__':
    create_sample_data()