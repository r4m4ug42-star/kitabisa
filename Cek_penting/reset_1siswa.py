# reset_siswa101.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from django.contrib.auth.models import User
from kitajalan.models import (
    ProgressHalaman, 
    ProgressMateri, 
    ProgressKuis,
    SesiKuis,
    JawabanKuis
)

def reset_user_progress(username):
    try:
        user = User.objects.get(username=username)
        print(f"🔄 Mereset progress untuk: {user.username}")
        
        # Hapus progress kuis
        sesi_list = SesiKuis.objects.filter(user=user)
        print(f"  - Menghapus {sesi_list.count()} sesi kuis")
        sesi_list.delete()
        
        # Hapus jawaban kuis
        jawaban = JawabanKuis.objects.filter(sesi__user=user)
        print(f"  - Menghapus {jawaban.count()} jawaban kuis")
        jawaban.delete()
        
        # Hapus progress kuis
        progress_kuis = ProgressKuis.objects.filter(user=user)
        print(f"  - Menghapus {progress_kuis.count()} progress kuis")
        progress_kuis.delete()
        
        # Hapus progress halaman
        progress_halaman = ProgressHalaman.objects.filter(user=user)
        print(f"  - Menghapus {progress_halaman.count()} progress halaman")
        progress_halaman.delete()
        
        # Hapus progress materi
        progress_materi = ProgressMateri.objects.filter(user=user)
        print(f"  - Menghapus {progress_materi.count()} progress materi")
        progress_materi.delete()
        
        print(f"✅ Progress {username} berhasil direset!")
        print(f"   User sekarang bisa memulai dari awal dengan aturan baru.")
        
    except User.DoesNotExist:
        print(f"❌ User {username} tidak ditemukan!")

if __name__ == '__main__':
    reset_user_progress('siswa101')