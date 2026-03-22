# cek_progress_lengkap.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from django.contrib.auth.models import User
from kitajalan.models import Materi, ProgressHalaman, ProgressKuis

def cek_progress_user(username='siswa101', materi_judul='Pengenalan Django'):
    try:
        user = User.objects.get(username=username)
        print(f"✅ User: {user.username}")
    except User.DoesNotExist:
        print(f"❌ User {username} tidak ditemukan")
        return
    
    try:
        materi = Materi.objects.get(judul=materi_judul)
        print(f"✅ Materi: {materi.judul} (ID: {materi.id})")
    except Materi.DoesNotExist:
        print(f"❌ Materi {materi_judul} tidak ditemukan")
        return
    
    print("\n📊 STATUS HALAMAN:")
    semua_halaman = materi.halaman.all().order_by('urutan')
    total_halaman = semua_halaman.count()
    selesai_halaman = 0
    
    for halaman in semua_halaman:
        progress = ProgressHalaman.objects.filter(user=user, halaman=halaman).first()
        status = "✅" if progress and progress.is_done else "❌"
        if progress and progress.is_done:
            selesai_halaman += 1
        print(f"  {status} {halaman.urutan}. {halaman.judul}")
    
    print(f"\n📈 PROGRESS HALAMAN: {selesai_halaman}/{total_halaman}")
    
    # Cek progress kuis
    try:
        progress_kuis = ProgressKuis.objects.get(user=user, materi=materi)
        print(f"\n📋 PROGRESS KUIS:")
        print(f"  - Sudah lulus: {progress_kuis.sudah_lulus}")
        print(f"  - Nilai tertinggi: {progress_kuis.nilai_tertinggi}")
        print(f"  - Total percobaan: {progress_kuis.total_percobaan}")
    except ProgressKuis.DoesNotExist:
        print(f"\n📋 PROGRESS KUIS: Belum pernah mencoba")
    
    # Cek apakah semua halaman selesai
    if selesai_halaman == total_halaman:
        print(f"\n✅ SEMUA HALAMAN SELESAI! Tombol kuis harusnya muncul.")
    else:
        print(f"\n❌ BELUM SELESAI! Kurang {total_halaman - selesai_halaman} halaman lagi.")

if __name__ == '__main__':
    cek_progress_user()