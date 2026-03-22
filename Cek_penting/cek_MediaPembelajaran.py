# cek_MediaPembelajaran.py
import os
import django

# SETUP DJANGO - WAJIB!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

# Sekarang baru import models
from kitajalan import models
from django.db import connection

print("="*50)
print("CHECKING MODELS IN KITAJALAN")
print("="*50)

# Cek model apa saja yang ada
model_list = []
for name in dir(models):
    if name[0].isupper() and name not in ['User', 'Model']:
        model_list.append(name)
        print(f"✅ {name}")

print("\n" + "="*50)
print("CHECKING MEDIA PEMBELAJARAN MODEL")
print("="*50)

if hasattr(models, 'MediaPembelajaran'):
    print("✅ Model MediaPembelajaran ADA di models.py")
    
    # Cek tabel di database
    tables = connection.introspection.table_names()
    if 'kitajalan_mediapembelajaran' in tables:
        print("✅ Tabel kitajalan_mediapembelajaran ADA di database")
        
        # Tampilkan field-fieldnya
        model = models.MediaPembelajaran
        print(f"\nFields in MediaPembelajaran:")
        for field in model._meta.fields:
            print(f"  - {field.name}: {field.get_internal_type()}")
            
    else:
        print("❌ Tabel kitajalan_mediapembelajaran TIDAK ADA di database")
        print("\nSOLUSI: Jalankan migrasi:")
        print("  python manage.py makemigrations kitajalan")
        print("  python manage.py migrate kitajalan")
else:
    print("❌ Model MediaPembelajaran TIDAK ADA di models.py")
    print("\nSOLUSI: Tambahkan model MediaPembelajaran ke models.py")

print("\n" + "="*50)