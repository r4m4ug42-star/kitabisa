# reset_all_users.py
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

def reset_all_users():
    users = User.objects.exclude(is_superuser=True)  # Kecuali admin
    print(f"🔄 Akan mereset {users.count()} user...")
    
    for user in users:
        # Hapus semua data progress user ini
        SesiKuis.objects.filter(user=user).delete()
        JawabanKuis.objects.filter(sesi__user=user).delete()
        ProgressKuis.objects.filter(user=user).delete()
        ProgressHalaman.objects.filter(user=user).delete()
        ProgressMateri.objects.filter(user=user).delete()
        
        print(f"  ✅ {user.username} direset")
    
    print(f"\n✅ Semua user telah direset!")

if __name__ == '__main__':
    confirm = input("Yakin ingin mereset SEMUA user? (y/n): ")
    if confirm.lower() == 'y':
        reset_all_users()
    else:
        print("Dibatalkan.")