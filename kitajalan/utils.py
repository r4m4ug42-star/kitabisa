# kitajalan/utils.py
from .models import ProgressHalaman, ProgressKuis

def can_access_halaman(user, halaman):
    """
    Cek apakah user bisa mengakses halaman tertentu
    Halaman bisa diakses jika:
    1. Ini adalah halaman pertama dalam materi, ATAU
    2. Semua halaman sebelumnya dalam materi ini sudah selesai
    """
    if not user.is_authenticated:
        return False
    
    materi = halaman.materi
    
    # Ambil semua halaman dalam materi ini, urut berdasarkan urutan
    semua_halaman = materi.halaman.all().order_by('urutan')
    
    # Cari posisi halaman ini
    try:
        index = list(semua_halaman).index(halaman)
    except ValueError:
        return False
    
    # Jika ini halaman pertama (index 0), boleh diakses
    if index == 0:
        return True
    
    # Cek apakah semua halaman SEBELUMnya sudah selesai
    halaman_sebelumnya = semua_halaman[:index]
    for h in halaman_sebelumnya:
        if not ProgressHalaman.objects.filter(user=user, halaman=h, is_done=True).exists():
            return False
    
    return True

def can_access_materi(user, materi):
    """
    Cek apakah user bisa mengakses materi tertentu
    Materi bisa diakses jika semua materi sebelumnya sudah lulus kuis
    """
    if not user.is_authenticated:
        return False
    
    kursus = materi.kursus
    
    # Ambil semua materi dalam kursus, urut berdasarkan urutan
    semua_materi = kursus.materi.all().order_by('urutan')
    
    # Cari posisi materi ini
    try:
        index = list(semua_materi).index(materi)
    except ValueError:
        return False
    
    # Jika ini materi pertama (index 0), boleh diakses
    if index == 0:
        return True
    
    # Cek apakah semua materi SEBELUMnya sudah lulus kuis
    materi_sebelumnya = semua_materi[:index]
    for m in materi_sebelumnya:
        try:
            progress = ProgressKuis.objects.get(user=user, materi=m, kursus=kursus)
            if not progress.sudah_lulus:
                return False
        except ProgressKuis.DoesNotExist:
            return False
    
    return True