from django.test import TestCase
from django.contrib.auth.models import User
from kitajalan.models import Kursus, Materi, ProgressMateri
from django.contrib.auth import get_user_model

from kitajalan.models import (
    Kursus,
    Materi,
    HalamanMateri,
    ProgressHalaman,
    ProgressMateri,
    Enrollment
)

User = get_user_model()


class ProgressTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.kursus = Kursus.objects.create(
            nama="Django Dasar",   # ← PERBAIKAN DI SINI
            slug="django-dasar",
            deskripsi="Belajar Django"
        )

        self.materi = Materi.objects.create(
            kursus=self.kursus,
            judul="Pengenalan Django",
            slug="pengenalan-django",
            urutan=1,
            konten="Isi materi"
        )

    def test_progress_materi_created(self):

        progress = ProgressMateri.objects.create(
            user=self.user,
            materi=self.materi,
            is_done=True
        )

        self.assertEqual(progress.user.username, "testuser")
        self.assertEqual(progress.materi.judul, "Pengenalan Django")
        self.assertTrue(progress.is_done)

    def test_unique_progress_materi(self):

        ProgressMateri.objects.create(
            user=self.user,
            materi=self.materi,
            is_done=True
        )

        with self.assertRaises(Exception):
            ProgressMateri.objects.create(
                user=self.user,
                materi=self.materi,
                is_done=True
            )