# cek_sesi.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from django.contrib.auth.models import User
from kitajalan.models import SesiKuis

user = User.objects.get(username='siswa101')
print(f"User: {user.username}")

# Lihat sesi kuis yang ada
sesi_list = SesiKuis.objects.filter(user=user).order_by('-started_at')
print(f"Total sesi: {sesi_list.count()}")

for sesi in sesi_list:
    print(f"\nID: {sesi.id}")
    print(f"Status: {sesi.status}")
    print(f"Dibuat: {sesi.started_at}")
    print(f"Materi: {sesi.materi}")
    print(f"Percobaan ke: {sesi.percobaan_ke}")