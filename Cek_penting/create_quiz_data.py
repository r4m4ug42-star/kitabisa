# create_quiz_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitabisa.settings')
django.setup()

from kitajalan.models import Kursus, Materi, BankSoal

def create_sample_questions():
    """Buat contoh soal untuk testing"""
    
    # Ambil kursus Django Dasar
    try:
        kursus = Kursus.objects.get(slug='django-dasar')
        print(f"Kursus ditemukan: {kursus.nama}")
    except Kursus.DoesNotExist:
        print("Kursus 'django-dasar' tidak ditemukan!")
        return
    
    # Ambil materi Pengenalan Django
    try:
        materi = Materi.objects.get(kursus=kursus, slug='pengenalan-django')
        print(f"Materi ditemukan: {materi.judul}")
    except Materi.DoesNotExist:
        print("Materi 'pengenalan-django' tidak ditemukan!")
        materi = None
    
    # Soal untuk kuis materi
    if materi:
        soal_materi = [
            {
                "pertanyaan": "Apa itu Django?",
                "pilihan_a": "Framework PHP untuk web",
                "pilihan_b": "Framework Python untuk web",
                "pilihan_c": "Database management system",
                "pilihan_d": "Bahasa pemrograman",
                "jawaban": "B"
            },
            {
                "pertanyaan": "Django menggunakan arsitektur?",
                "pilihan_a": "MVC",
                "pilihan_b": "MVVM",
                "pilihan_c": "MTV (Model-Template-View)",
                "pilihan_d": "Singleton",
                "jawaban": "C"
            },
            {
                "pertanyaan": "Perintah untuk membuat project Django baru?",
                "pilihan_a": "django startproject",
                "pilihan_b": "django-admin startproject",
                "pilihan_c": "python django create",
                "pilihan_d": "new django project",
                "jawaban": "B"
            },
            {
                "pertanyaan": "File apa yang berisi konfigurasi project Django?",
                "pilihan_a": "config.py",
                "pilihan_b": "settings.py",
                "pilihan_c": "django.conf",
                "pilihan_d": "app.py",
                "jawaban": "B"
            },
            {
                "pertanyaan": "Apa fungsi models.py di Django?",
                "pilihan_a": "Mengatur routing URL",
                "pilihan_b": "Mendefinisikan struktur database",
                "pilihan_c": "Mengatur template HTML",
                "pilihan_d": "Menjalankan server",
                "jawaban": "B"
            }
        ]
        
        for soal in soal_materi:
            BankSoal.objects.create(
                tipe='materi',
                materi=materi,
                kursus=kursus,
                pertanyaan=soal["pertanyaan"],
                pilihan_a=soal["pilihan_a"],
                pilihan_b=soal["pilihan_b"],
                pilihan_c=soal["pilihan_c"],
                pilihan_d=soal["pilihan_d"],
                jawaban_benar=soal["jawaban"],
                bobot=20,
                is_active=True
            )
        print(f"✅ {len(soal_materi)} soal materi berhasil dibuat!")
    
    # Soal untuk final test
    soal_final = [
        {
            "pertanyaan": "Apa kepanjangan dari ORM di Django?",
            "pilihan_a": "Object Relational Mapping",
            "pilihan_b": "Object Request Model",
            "pilihan_c": "Online Resource Manager",
            "pilihan_d": "Open Response Module",
            "jawaban": "A"
        },
        {
            "pertanyaan": "Perintah untuk menjalankan server Django?",
            "pilihan_a": "python server.py",
            "pilihan_b": "django run",
            "pilihan_c": "python manage.py runserver",
            "pilihan_d": "start django",
            "jawaban": "C"
        },
        {
            "pertanyaan": "Apa fungsi migrations di Django?",
            "pilihan_a": "Menjalankan server",
            "pilihan_b": "Membuat backup database",
            "pilihan_c": "Menyinkronkan model dengan database",
            "pilihan_d": "Menginstall package",
            "jawaban": "C"
        },
        {
            "pertanyaan": "Tag template Django untuk menampilkan variabel?",
            "pilihan_a": "{{ variabel }}",
            "pilihan_b": "{% variabel %}",
            "pilihan_c": "[[ variabel ]]",
            "pilihan_d": "<?= variabel ?>",
            "jawaban": "A"
        },
        {
            "pertanyaan": "Apa itu virtual environment?",
            "pilihan_a": "Server virtual",
            "pilihan_b": "Environment terisolasi untuk project Python",
            "pilihan_c": "Database virtual",
            "pilihan_d": "Browser virtual",
            "jawaban": "B"
        }
    ]
    
    for soal in soal_final:
        BankSoal.objects.create(
            tipe='final',
            materi=None,
            kursus=kursus,
            pertanyaan=soal["pertanyaan"],
            pilihan_a=soal["pilihan_a"],
            pilihan_b=soal["pilihan_b"],
            pilihan_c=soal["pilihan_c"],
            pilihan_d=soal["pilihan_d"],
            jawaban_benar=soal["jawaban"],
            bobot=20,
            is_active=True
        )
    print(f"✅ {len(soal_final)} soal final test berhasil dibuat!")

if __name__ == '__main__':
    create_sample_questions()