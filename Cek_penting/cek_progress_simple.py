# cek_progress_simple.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from django.contrib.auth.models import User
from kitajalan.models import HalamanMateri, ProgressHalaman

print("="*50)
print("CEK PROGRESS USER")
print("="*50)

# Ganti dengan data Anda
username = "siswa101"
halaman_slug = "apa-itu-django"

try:
    user = User.objects.get(username=username)
    print(f"✅ User: {user.username}")
except:
    print(f"❌ User {username} tidak ditemukan!")
    exit()

try:
    halaman = HalamanMateri.objects.get(slug=halaman_slug)
    print(f"✅ Halaman: {halaman.judul} (ID: {halaman.id})")
except:
    print(f"❌ Halaman {halaman_slug} tidak ditemukan!")
    exit()

# Cek progress
progress = ProgressHalaman.objects.filter(user=user, halaman=halaman).first()

if progress:
    print(f"\n📊 Progress sudah ada:")
    print(f"   - Status: {'✅ Selesai' if progress.is_done else '❌ Belum'}")
else:
    print(f"\n📊 Belum ada progress, membuat baru...")
    progress = ProgressHalaman.objects.create(
        user=user,
        halaman=halaman,
        is_done=False
    )
    print(f"✅ Progress dibuat!")

# Tandai selesai
progress.is_done = True
progress.save()
print(f"\n✅ Halaman '{halaman.judul}' telah ditandai SELESAI!")

# Tampilkan semua progress
print(f"\n📋 Semua progress untuk materi {halaman.materi.judul}:")
semua = ProgressHalaman.objects.filter(
    user=user,
    halaman__materi=halaman.materi
)
for p in semua:
    status = "✅" if p.is_done else "❌"
    print(f"   {status} {p.halaman.judul}")

print("\n" + "="*50)
print("SILAHKAN REFRESH HALAMAN!")
print("="*50)