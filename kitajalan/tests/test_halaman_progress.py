from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from kitajalan.models import (
    Kursus,
    Materi,
    HalamanMateri,
    ProgressHalaman,
    ProgressMateri,
    Enrollment
)


class HalamanProgressTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            password="12345"
        )

        self.kursus = Kursus.objects.create(
             nama="Django Dasar",
            slug="django-dasar",
            deskripsi="Belajar Django"
        )


        Enrollment.objects.create(
            user=self.user,
            kursus=self.kursus
        )

        self.materi = Materi.objects.create(
            kursus=self.kursus,
            judul="Materi 1",
            slug="materi-1",
            urutan=1
        )

        self.halaman1 = HalamanMateri.objects.create(
            materi=self.materi,
            judul="Halaman 1",
            slug="halaman-1",
            konten="Isi halaman 1",
            urutan=1
        )

        self.halaman2 = HalamanMateri.objects.create(
            materi=self.materi,
            judul="Halaman 2",
            slug="halaman-2",
            konten="Isi halaman 2",
            urutan=2
        )

        self.client.login(
            username="testuser",
            password="12345"
        )

    def test_progress_halaman_created(self):

        url = reverse(
            "tandai_halaman_selesai",
            args=[self.halaman1.id]
        )

        self.client.post(url)

        exists = ProgressHalaman.objects.filter(
            user=self.user,
            halaman=self.halaman1,
            is_done=True
        ).exists()

        self.assertTrue(exists)


    def test_progress_materi_created_if_all_halaman_done(self):

        # selesai halaman 1
        self.client.post(
            reverse("tandai_halaman_selesai", args=[self.halaman1.id])
        )

        # selesai halaman 2
        self.client.post(
            reverse("tandai_halaman_selesai", args=[self.halaman2.id])
        )

        exists = ProgressMateri.objects.filter(
            user=self.user,
            materi=self.materi,
            is_done=True
        ).exists()

        self.assertTrue(exists)
