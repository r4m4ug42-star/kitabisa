from .models import ProgressHalaman, ProgressMateri

def hitung_progress_materi(user, materi):
    total = materi.halaman.count()
    selesai = ProgressHalaman.objects.filter(
        user=user,
        halaman__materi=materi,
        is_done=True
    ).count()

    if total == 0:
        return 0

    return int((selesai / total) * 100)
