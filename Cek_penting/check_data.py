# check_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from kitajalan.models import Kursus, Materi, HalamanMateri, HalamanBlok

def check_course_data(kursus_slug):
    print(f"\n{'='*60}")
    print(f"CHECKING DATA FOR KURSUS: {kursus_slug}")
    print('='*60)
    
    try:
        kursus = Kursus.objects.get(slug=kursus_slug)
        print(f"✅ Kursus: {kursus.nama} (ID: {kursus.id})")
    except Kursus.DoesNotExist:
        print(f"❌ Kursus dengan slug '{kursus_slug}' tidak ditemukan!")
        return
    
    # Cek materi
    materi_list = Materi.objects.filter(kursus=kursus).order_by('urutan')
    print(f"\n📚 MATERI ({materi_list.count()} total):")
    
    for i, materi in enumerate(materi_list, 1):
        print(f"\n  {i}. {materi.judul} (slug: {materi.slug}, ID: {materi.id})")
        
        # Cek halaman
        halaman_list = HalamanMateri.objects.filter(materi=materi).order_by('urutan')
        print(f"     📄 Halaman: {halaman_list.count()}")
        
        for j, halaman in enumerate(halaman_list, 1):
            print(f"        {j}. {halaman.judul} (slug: {halaman.slug})")
            
            # Cek blok
            blok_list = HalamanBlok.objects.filter(halaman=halaman).order_by('urutan')
            print(f"           🧩 Blok: {blok_list.count()}")
            
            for k, blok in enumerate(blok_list, 1):
                preview = blok.konten[:30] + "..." if len(blok.konten or "") > 30 else blok.konten
                print(f"              - {blok.tipe}: {preview}")

if __name__ == '__main__':
    # Ganti dengan slug kursus Anda
    check_course_data('django-dasar')