from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Kursus, Enrollment


def enrollment_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        kursus_slug = kwargs.get('kursus_slug')

        kursus = get_object_or_404(Kursus, slug=kursus_slug)

        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            kursus=kursus
        ).exists()

        if not is_enrolled:
            return redirect('daftar_kursus')

        return view_func(request, *args, **kwargs)

    return _wrapped_view
