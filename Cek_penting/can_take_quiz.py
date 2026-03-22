# cek_can_take_quiz.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from django.contrib.auth.models import User
from kitajalan.models import Materi, ProgressHalaman
from kitajalan.templatetags.kuis_tags import can_take_quiz

def cek_progress_user(username='siswa101', materi_slug='pengenalan-django'):
    try:
        user = User.objects.get(username=username)
        print(f"✅ User ditemukan: {user.username}")
    except User.DoesNotExist:
        print(f"❌ User '{username}' tidak ditemukan!")
        return
    
    try:
        materi = Materi.objects.get(slug=materi_slug)
        print(f"✅ Materi ditemukan: {materi.judul}")
    except Materi.DoesNotExist:
        print(f"❌ Materi '{materi_slug}' tidak ditemukan!")
        return
    
    print(f"\n📊 STATISTIK:")
    print(f"Total halaman dalam materi: {materi.halaman.count()}")
    
    # Hitung halaman yang sudah selesai
    halaman_selesai = ProgressHalaman.objects.filter(
        user=user,
        halaman__materi=materi,
        is_done=True
    ).count()
    
    print(f"Halaman selesai: {halaman_selesai}")
    
    if halaman_selesai == materi.halaman.count():
        print("✅ SEMUA HALAMAN SELESAI!")
        
        # Cek can_take_quiz
        can_quiz = can_take_quiz(user, materi)
        print(f"can_take_quiz: {can_quiz}")
        
        if can_quiz:
            print("🎯 User BISA mengikuti kuis!")
        else:
            print("❌ User TIDAK BISA mengikuti kuis (padahal semua halaman selesai)")
            print("   Kemungkinan masalah di fungsi can_take_quiz")
    else:
        print(f"❌ BELUM SELESAI! Kurang {materi.halaman.count() - halaman_selesai} halaman lagi:")
        
        # Tampilkan halaman yang belum selesai
        for h in materi.halaman.all().order_by('urutan'):
            if not ProgressHalaman.objects.filter(user=user, halaman=h, is_done=True).exists():
                print(f"   - {h.urutan}. {h.judul} (ID: {h.id})")
    
    # Tampilkan semua progress halaman
    print(f"\n📋 DETAIL PROGRESS HALAMAN:")
    for h in materi.halaman.all().order_by('urutan'):
        status = ProgressHalaman.objects.filter(user=user, halaman=h, is_done=True).exists()
        icon = "✅" if status else "❌"
        print(f"   {icon} {h.urutan}. {h.judul}")

if __name__ == '__main__':
    # Bisa ganti username dan materi_slug sesuai kebutuhan
    cek_progress_user('siswa101', 'pengenalan-django')
    
    # Tambahan: cek semua user
    print("\n" + "="*50)
    print("CEK SEMUA USER:")
    for user in User.objects.all():
        print(f"\nUser: {user.username}")
        cek_progress_user(user.username, 'pengenalan-django')