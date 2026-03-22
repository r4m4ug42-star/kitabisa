from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Kursus, Materi, Enrollment


class LMSTestCase(TestCase):

    def setUp(self):
        # buat user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # buat kursus
        self.kursus = Kursus.objects.create(
            judul='Django Dasar',
            slug='django-dasar',
            deskripsi='Test kursus'
        )

        # buat materi
        self.materi = Materi.objects.create(
            kursus=self.kursus,
            judul='Pengenalan Django',
            slug='pengenalan-django',
            urutan=1
        )

        self.client = Client()

    # =====================================
    # TEST LOGIN
    # =====================================

    def test_user_login(self):
        login = self.client.login(
            username='testuser',
            password='testpass123'
        )
        self.assertTrue(login)

    # =====================================
    # TEST DASHBOARD ACCESS
    # =====================================

    def test_dashboard_access(self):

        self.client.login(
            username='testuser',
            password='testpass123'
        )

        response = self.client.get(
            reverse('dashboard')
        )

        self.assertEqual(response.status_code, 200)

    # =====================================
    # TEST AUTO ENROLLMENT
    # =====================================

    def test_auto_enrollment(self):

        self.client.login(
            username='testuser',
            password='testpass123'
        )

        url = reverse(
            'materi_detail',
            args=[self.kursus.slug, self.materi.slug]
        )

        self.client.get(url)

        enrolled = Enrollment.objects.filter(
            user=self.user,
            kursus=self.kursus
        ).exists()

        self.assertTrue(enrolled)

    # =====================================
    # TEST MATERI ACCESS
    # =====================================

    def test_materi_access(self):

        self.client.login(
            username='testuser',
            password='testpass123'
        )

        url = reverse(
            'materi_detail',
            args=[self.kursus.slug, self.materi.slug]
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    # =====================================
    # TEST URL REVERSE WORKS
    # =====================================

    def test_url_reverse(self):

        url = reverse(
            'materi_detail',
            args=[self.kursus.slug, self.materi.slug]
        )

        self.assertEqual(
            url,
            f'/kursus/{self.kursus.slug}/{self.materi.slug}/'
        )
