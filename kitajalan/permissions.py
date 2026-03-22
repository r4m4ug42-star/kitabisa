from .models import Enrollment

def user_is_enrolled(user, kursus):
    if not user.is_authenticated:
        return False

    return Enrollment.objects.filter(
        user=user,
        kursus=kursus
    ).exists()
