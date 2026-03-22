from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from kitajalan.models import (
    Kursus,
    Materi,
    HalamanMateri,
    Enrollment
)

User = get_user_model()


class ViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        # buat user
        self.user = User.objects.create_user(
            username="testuser",
            password="password123"
        )

        self.user2 = User.objects.create_user(
            username="user2",
            password="password123"
        )

        # buat kursus
        self.kursus = Kursus.objects.create(
            nama="Django Dasar",
            deskripsi="Belajar Django"
        )

        # buat materi
        self.materi = Materi.objects.create(
            kursus=self.kursus,
            judul="Pengenalan Django",
            konten="Isi materi"
        )

        # buat halaman
        self.halaman = HalamanMateri.objects.create(
            materi=self.materi,
            judul="Halaman 1",
            konten="Isi halaman"
        )

        # enroll user
        Enrollment.objects.create(
            user=self.user,
            kursus=self.kursus
        )

    # =========================
    # DASHBOARD TEST
    # =========================

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_logged_in(self):
        self.client.login(username="testuser", password="password123")

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django Dasar")

    # =========================
    # MATERI DETAIL TEST
    # =========================

    def test_materi_detail_requires_login(self):
        url = reverse("materi_detail", args=[
            self.kursus.slug,
            self.materi.slug
        ])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_materi_detail_enrolled_user(self):
        self.client.login(username="testuser", password="password123")

        url = reverse("materi_detail", args=[
            self.kursus.slug,
            self.materi.slug
        ])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pengenalan Django")

    def test_materi_detail_not_enrolled_user(self):
        self.client.login(username="user2", password="password123")

        url = reverse("materi_detail", args=[
            self.kursus.slug,
            self.materi.slug
        ])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)
