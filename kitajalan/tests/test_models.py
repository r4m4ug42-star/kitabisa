from django.test import TestCase
from django.contrib.auth import get_user_model
from kitajalan.models import Kursus, Materi, Enrollment

User = get_user_model()


class ModelTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            password="12345"
        )

        self.kursus = Kursus.objects.create(
            nama="Django Dasar",
            deskripsi="deskripsi"
        )

        self.materi = Materi.objects.create(
            kursus=self.kursus,
            judul="Intro Django",
            konten="isi materi",
            urutan=1
        )

        self.enrollment = Enrollment.objects.create(
            user=self.user,
            kursus=self.kursus
        )

    def test_kursus_created(self):
        self.assertEqual(self.kursus.nama, "Django Dasar")

    def test_materi_created(self):
        self.assertEqual(self.materi.judul, "Intro Django")

    def test_enrollment_created(self):
        self.assertEqual(self.enrollment.user.username, "testuser")
