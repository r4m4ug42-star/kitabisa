# kitajalan/templatetags/kuis_tags.py
from django import template
from ..models import ProgressKuis, ProgressHalaman
from ..utils import can_access_halaman as util_can_access_halaman
from ..utils import can_access_materi as util_can_access_materi

register = template.Library()

@register.filter
def get_progress_kuis(user, materi):
    """Get progress kuis untuk user dan materi tertentu"""
    try:
        return ProgressKuis.objects.get(
            user=user,
            materi=materi,
            kursus=materi.kursus
        )
    except ProgressKuis.DoesNotExist:
        return None

@register.filter
def can_take_quiz(user, materi):
    """Cek apakah user bisa mengikuti kuis"""
    halaman_list = materi.halaman.all()
    if not halaman_list:
        return False
    
    total_halaman = halaman_list.count()
    selesai = ProgressHalaman.objects.filter(
        user=user,
        halaman__in=halaman_list,
        is_done=True
    ).count()
    
    return total_halaman > 0 and selesai == total_halaman

@register.filter
def can_take_final(user, kursus):
    """Cek apakah user bisa mengikuti final test"""
    materi_list = kursus.materi.all()
    if not materi_list:
        return False
    
    for materi in materi_list:
        try:
            progress = ProgressKuis.objects.get(
                user=user,
                materi=materi,
                kursus=kursus
            )
            if not progress.sudah_lulus:
                return False
        except ProgressKuis.DoesNotExist:
            return False
    
    return True

# ===== FILTER UNTUK AKSES HALAMAN - PAKAI FUNGSI DARI UTILS =====
@register.filter
def can_access_halaman(user, halaman):
    """Filter untuk cek akses halaman"""
    return util_can_access_halaman(user, halaman)  # ← PANGGIL DARI UTILS

@register.filter
def can_access_materi(user, materi):
    """Filter untuk cek akses materi"""
    return util_can_access_materi(user, materi)    # ← PANGGIL DARI UTILS