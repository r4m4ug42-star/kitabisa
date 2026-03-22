# cek_tabel.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from django.db import connection

print("="*50)
print("TABLES IN DATABASE")
print("="*50)

tables = connection.introspection.table_names()
for table in sorted(tables):
    print(f"  - {table}")

print("\n" + "="*50)
print("CHECKING MEDIA TABLE")
print("="*50)

if 'kitajalan_mediapembelajaran' in tables:
    print("✅ Tabel kitajalan_mediapembelajaran ADA!")
    
    # Cek struktur tabel
    from django.apps import apps
    model = apps.get_model('kitajalan', 'MediaPembelajaran')
    print(f"\nFields in MediaPembelajaran:")
    for field in model._meta.fields:
        print(f"  - {field.name}: {field.get_internal_type()}")
        
else:
    print("❌ Tabel kitajalan_mediapembelajaran TIDAK ADA!")
    
print("\n" + "="*50)