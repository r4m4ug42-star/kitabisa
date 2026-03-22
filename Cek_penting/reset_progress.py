# reset_progress.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from django.contrib.auth.models import User
from kitajalan.models import ProgressMateri, ProgressHalaman, SesiKuis, JawabanKuis, ProgressKuis

def reset_user_progress(username):
    """Reset semua progress untuk user tertentu"""
    try:
        user = User.objects.get(username=username)
        print(f"Mereset progress untuk user: {username}")
        
        # Hapus progress kuis
        deleted_sesi = SesiKuis.objects.filter(user=user).delete()
        print(f"  - Sesi kuis dihapus: {deleted_sesi[0]}")
        
        deleted_jawaban = JawabanKuis.objects.filter(sesi__user=user).delete()
        print(f"  - Jawaban kuis dihapus: {deleted_jawaban[0]}")
        
        deleted_progress_kuis = ProgressKuis.objects.filter(user=user).delete()
        print(f"  - Progress kuis dihapus: {deleted_progress_kuis[0]}")
        
        # Hapus progress materi dan halaman
        deleted_progress_materi = ProgressMateri.objects.filter(user=user).delete()
        print(f"  - Progress materi dihapus: {deleted_progress_materi[0]}")
        
        deleted_progress_halaman = ProgressHalaman.objects.filter(user=user).delete()
        print(f"  - Progress halaman dihapus: {deleted_progress_halaman[0]}")
        
        print(f"✅ Progress user {username} telah direset!")
        return True
        
    except User.DoesNotExist:
        print(f"❌ User {username} tidak ditemukan!")
        return False

if __name__ == '__main__':
    username = input("Masukkan username yang akan direset: ")
    reset_user_progress(username)