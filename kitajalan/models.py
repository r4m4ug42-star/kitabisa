from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from .video_utils import extract_youtube_id, get_youtube_embed_html, get_video_error_html
import markdown
from django.utils.safestring import mark_safe
from django.utils.html import escape
import re
import os

User = settings.AUTH_USER_MODEL


# =========================
# KURSUS
# =========================

class Kursus(models.Model):
    nama = models.CharField(max_length=225)
    slug = models.SlugField(unique=True, blank=True)
    deskripsi = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    peserta = models.ManyToManyField(
        User,
        through='Enrollment',
        related_name='kursus_diikuti',
        blank=True
    )

    class Meta:
        ordering = ['nama']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nama)
            slug = base_slug
            counter = 1
            while Kursus.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama


# =========================
# ENROLLMENT
# =========================

class Enrollment(models.Model):

    STATUS_CHOICES = (
        ("pending", "Menunggu Verifikasi"),
        ("active", "Aktif"),
        ("completed", "Selesai"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    kursus = models.ForeignKey(Kursus, on_delete=models.CASCADE)

    joined_at = models.DateTimeField(default=timezone.now)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'kursus'],
                name='unique_user_kursus'
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.kursus.nama} ({self.status})"

# =========================
# MATERI
# =========================

class Materi(models.Model):
    kursus = models.ForeignKey(
        Kursus,
        on_delete=models.CASCADE,
        related_name='materi'
    )

    judul = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    urutan = models.PositiveIntegerField(default=0)
    konten = models.TextField()

    class Meta:
        ordering = ['urutan']
        constraints = [
            models.UniqueConstraint(
                fields=['kursus', 'slug'],
                name='unique_slug_per_kursus'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.judul)
            slug = base_slug
            counter = 1

            while Materi.objects.filter(kursus=self.kursus, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul


# =========================
# HALAMAN MATERI
# =========================

class HalamanMateri(models.Model):
    materi = models.ForeignKey(
        Materi,
        on_delete=models.CASCADE,
        related_name='halaman'
    )

    judul = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    urutan = models.PositiveIntegerField(default=0)

    konten = models.TextField()
    konten_html = models.TextField(blank=True, editable=False)

    class Meta:
        ordering = ['urutan']
        constraints = [
            models.UniqueConstraint(
                fields=['materi', 'slug'],
                name='unique_slug_per_materi'
            )
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.judul)
            slug = base_slug
            counter = 1

            while Materi.objects.filter(kursus=self.kursus, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.materi.judul} - {self.judul}"

# =========================
# PROGRESS MATERI
# =========================

class ProgressMateri(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    materi = models.ForeignKey(Materi, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)           # Halaman selesai
    is_quiz_passed = models.BooleanField(default=False)    # Kuis lulus
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'materi'], name='unique_progress_materi')
        ]

    def __str__(self):
        status = []
        if self.is_done:
            status.append("📖")
        if self.is_quiz_passed:
            status.append("✅")
        return f"{self.user.username} - {self.materi.judul} {' '.join(status)}"


# =========================
# PROGRESS HALAMAN
# =========================

class ProgressHalaman(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    halaman = models.ForeignKey(HalamanMateri, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'halaman'],
                name='unique_progress_halaman'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.halaman.judul} - {'✓' if self.is_done else '○'}"

# =========================
# BLOK HALAMAN (VERSI PALING SEDERHANA DULU)
# =========================

# =========================
# BLOK HALAMAN
# =========================

class HalamanBlok(models.Model):

    TIPE_CHOICES = (
        ("text", "Text"),
        ("code", "Code"),
        ("image", "Image"),
        ("video", "Video"),
        ("local_image", "Gambar Lokal"),
        ("local_video", "Video Lokal"),
    )

    halaman = models.ForeignKey(
        "HalamanMateri",
        on_delete=models.CASCADE,
        related_name="blok",
    )

    tipe = models.CharField(
        max_length=20,
        choices=TIPE_CHOICES,
    )

    konten = models.TextField(
        blank=True,
        null=True,
    )

    urutan = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["urutan"]

    def __str__(self):
        return f"{self.halaman} - {self.tipe} ({self.urutan})"

    # =========================
    # RENDER KONTEN UTAMA
    # =========================
    def render_konten(self, request=None):
        """Render konten berdasarkan tipe"""
        if not self.konten:
            return ""

            if self.tipe == "text":
                html = markdown.markdown(self.konten, extensions=['fenced_code', 'codehilite', 'tables'])
                return mark_safe(html)

        elif self.tipe == "code":
                safe_code = escape(self.konten)
                return mark_safe(f'<pre><code>{safe_code}</code></pre>')
        
        elif self.tipe == "image":
                    return mark_safe(f'<img src="{self.konten}" style="max-width:100%; height:auto;">')

        elif self.tipe == "video":
                    return self.render_video(request)

        elif self.tipe == "local_image":
                return self.render_local_image()

        elif self.tipe == "local_video":
                return self.render_local_video()

        return mark_safe("<p>Konten tidak dikenali</p>")

    # =========================
    # RENDER VIDEO YOUTUBE
    # =========================
    def render_video(self, request=None):
        """Render video YouTube"""
        if not self.konten:
            return ""

        from .video_utils import extract_youtube_id

        video_id = extract_youtube_id(self.konten)

        if video_id:
            return mark_safe(f'''
            <div class="blok-video" style="width:100%; max-width:100%; margin:20px 0; overflow:hidden;">
                <div class="video-wrapper" style="position:relative; padding-bottom:56.25%; height:0; overflow:hidden; background:#000; border-radius:12px; width:100%; max-width:100%;">
                    <iframe 
                        src="https://www.youtube-nocookie.com/embed/{video_id}?rel=0&modestbranding=1&iv_load_policy=3&enablejsapi=1"
                        style="position:absolute; top:0; left:0; width:100%; height:100%; border:0; max-width:100%;"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowfullscreen
                        referrerpolicy="strict-origin-when-cross-origin"
                        loading="lazy">
                    </iframe>
                </div>
            </div>
                        ''')
        else:
            return mark_safe(f'''
            <div class="video-error" style="background:#fff3f3; border:1px solid #ffcdd2; border-radius:12px; padding:30px 20px; margin:20px 0; text-align:center;">
                <i class="fas fa-exclamation-triangle" style="font-size:48px; color:#ef5350;"></i>
                <h4 style="color:#b71c1c;">Video Tidak Dapat Dimuat</h4>
                <p>URL video tidak valid: {self.konten}</p>
                <a href="{self.konten}" target="_blank" class="btn" style="display:inline-block; padding:10px 24px; background:#ef5350; color:white; text-decoration:none; border-radius:6px;">
                    Tonton di YouTube
                </a>
            </div>
                     ''')

    # =========================
    # RENDER GAMBAR LOKAL
    # =========================
    def render_local_image(self):
        """Render gambar dari media lokal"""
        if not self.konten:
            return ""

        from django.conf import settings

        konten = self.konten.lstrip('/')
        if konten.startswith('media/'):
            konten = konten[6:]

        return mark_safe(f'''
        <div style="margin:20px 0; text-align:center;">
            <img src="{settings.MEDIA_URL}{konten}" 
                style="max-width:100%; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1);"
                alt="Gambar">
        </div>
                ''')

    # =========================
    # RENDER VIDEO LOKAL
    # =========================
    def render_local_video(self):
        """Render video dari media lokal (production-safe)"""
        if not self.konten:
                return ""

        #from django.conf import settings

        konten = self.konten.lstrip('/')
        if konten.startswith('media/'):
            konten = konten[6:]

        video_url = f"{settings.MEDIA_URL}{konten}"

        ext = os.path.splitext(konten)[1].lower()
        mime_type = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.ogg': 'video/ogg',
        }.get(ext, 'video/mp4')

        return mark_safe(f'''
            <div style="margin:20px 0;">
                <video controls style="width:100%; border-radius:8px;" preload="metadata">
                     <source src="{video_url}" type="{mime_type}">
                    Browser tidak mendukung video.
                </video>
            </div>
        ''')
        

# =========================
# BANK SOAL
# =========================

class BankSoal(models.Model):
    """
    Bank soal yang bisa digunakan berulang kali
    """
    TIPE_CHOICES = (
        ('materi', 'Kuis Materi'),
        ('final', 'Final Test'),
    )
    
    tipe = models.CharField(max_length=10, choices=TIPE_CHOICES)
    materi = models.ForeignKey(
        'Materi', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Kosongkan jika untuk final test"
    )
    kursus = models.ForeignKey(
        'Kursus', 
        on_delete=models.CASCADE,
        help_text="Kursus tempat soal ini digunakan"
    )
    
    pertanyaan = models.TextField()
    pilihan_a = models.CharField(max_length=255)
    pilihan_b = models.CharField(max_length=255)
    pilihan_c = models.CharField(max_length=255)
    pilihan_d = models.CharField(max_length=255)
    
    jawaban_benar = models.CharField(
        max_length=1, 
        choices=[('A','A'), ('B','B'), ('C','C'), ('D','D')]
    )
    
    bobot = models.IntegerField(default=20)  # Bobot dalam persen
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.materi:
            return f"[{self.materi.judul}] {self.pertanyaan[:50]}"
        return f"[FINAL] {self.pertanyaan[:50]}"

# =========================
# SESI KUIS (DENGAN TIMER & COOLDOWN)
# =========================

class SesiKuis(models.Model):
    """
    Menyimpan sesi kuis per user dengan fitur timer dan cooldown
    """
    STATUS_CHOICES = (
        ('mulai', 'Mulai'),
        ('sedang', 'Sedang Mengerjakan'),
        ('selesai', 'Selesai'),
        ('lulus', 'Lulus'),
        ('gagal', 'Gagal'),
        ('waktu_habis', 'Waktu Habis'),  # TAMBAHKAN STATUS BARU
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    materi = models.ForeignKey(
        'Materi', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    kursus = models.ForeignKey('Kursus', on_delete=models.CASCADE)
    tipe = models.CharField(max_length=10, choices=BankSoal.TIPE_CHOICES)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='mulai')
    percobaan_ke = models.IntegerField(default=1)
    
    total_soal = models.IntegerField(default=5)
    jawaban_benar = models.IntegerField(default=0)
    nilai = models.IntegerField(default=0)  # 0-100
    
    # TIMER FIELDS - TAMBAHKAN INI
    waktu_mulai = models.DateTimeField(null=True, blank=True)
    waktu_selesai = models.DateTimeField(null=True, blank=True)
    batas_waktu = models.IntegerField(default=300)  # 300 detik = 5 menit
    cooldown_until = models.DateTimeField(null=True, blank=True)  # Kapan bisa coba lagi
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        if self.materi:
            return f"{self.user.username} - {self.materi.judul} (P{self.percobaan_ke})"
        return f"{self.user.username} - FINAL (P{self.percobaan_ke})"
    
    # =========================
    # METHOD UNTUK TIMER
    # =========================
    
    def sisa_waktu(self):
        """Hitung sisa waktu dalam detik"""
        if not self.waktu_mulai:
            return self.batas_waktu
        
        from django.utils import timezone
        elapsed = (timezone.now() - self.waktu_mulai).total_seconds()
        remaining = self.batas_waktu - elapsed
        return max(0, int(remaining))
    
    def is_waktu_habis(self):
        """Cek apakah waktu sudah habis"""
        return self.sisa_waktu() <= 0
    
    def dalam_cooldown(self):
        """Cek apakah masih dalam masa cooldown"""
        if not self.cooldown_until:
            return False
        from django.utils import timezone
        return timezone.now() < self.cooldown_until
    
    def sisa_cooldown(self):
        """Hitung sisa cooldown dalam detik"""
        if not self.cooldown_until:
            return 0
        from django.utils import timezone
        remaining = (self.cooldown_until - timezone.now()).total_seconds()
        return max(0, int(remaining))
    
    def format_waktu(self, detik):
        """Format detik ke MM:SS"""
        minutes = detik // 60
        seconds = detik % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    # =========================
    # METHOD ORIGINAL (DENGAN PENYESUAIAN)
    # =========================
    
    def hitung_nilai(self):
        """Hitung nilai berdasarkan jawaban benar"""
        if self.total_soal > 0:
            self.nilai = int((self.jawaban_benar / self.total_soal) * 100)
            self.save()
        return self.nilai
    
    def cek_kelulusan(self):
        """Cek apakah user lulus (minimal 80%)"""
        self.hitung_nilai()
        if self.nilai >= 80:
            self.status = 'lulus'
            self.completed_at = timezone.now()
            self.waktu_selesai = timezone.now()
            self.save()
            
            # Jika lulus final test, tandai kursus selesai
            if self.tipe == 'final':
                ProgressMateri.objects.filter(
                    user=self.user,
                    materi__kursus=self.kursus
                ).update(is_done=True)
            
            return True
        else:
            self.status = 'gagal'
            self.completed_at = timezone.now()
            self.waktu_selesai = timezone.now()
            self.save()
            return False
    
    def tandai_waktu_habis(self):
        """Tandai kuis gagal karena waktu habis"""
        self.status = 'waktu_habis'
        self.completed_at = timezone.now()
        self.waktu_selesai = timezone.now()
        self.nilai = self.hitung_nilai()
        self.save()
        
    def get_info_waktu(self):
        """Mendapatkan info waktu untuk ditampilkan di template"""
        return {
            'sisa_waktu': self.sisa_waktu(),
            'sisa_waktu_format': self.format_waktu(self.sisa_waktu()),
            'batas_waktu': self.batas_waktu,
            'batas_waktu_format': self.format_waktu(self.batas_waktu),
            'waktu_habis': self.is_waktu_habis(),
            'dalam_cooldown': self.dalam_cooldown(),
            'sisa_cooldown': self.sisa_cooldown(),
            'sisa_cooldown_format': self.format_waktu(self.sisa_cooldown()),
        }


# =========================
# JAWABAN KUIS
# =========================

class JawabanKuis(models.Model):
    """
    Menyimpan jawaban user per sesi
    """
    sesi = models.ForeignKey(SesiKuis, on_delete=models.CASCADE, related_name='jawaban')
    soal = models.ForeignKey(BankSoal, on_delete=models.CASCADE)
    
    jawaban_user = models.CharField(max_length=1, choices=[('A','A'), ('B','B'), ('C','C'), ('D','D')])
    is_benar = models.BooleanField(default=False)
    
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('sesi', 'soal')
    
    def __str__(self):
        return f"{self.sesi.user.username} - Soal {self.soal.id}"


# =========================
# PROGRESS KUIS
# =========================

class ProgressKuis(models.Model):
    """
    Menyimpan progress kuis user per materi/kursus
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    materi = models.ForeignKey(
        'Materi', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    kursus = models.ForeignKey('Kursus', on_delete=models.CASCADE)
    
    sudah_lulus = models.BooleanField(default=False)
    nilai_tertinggi = models.IntegerField(default=0)
    total_percobaan = models.IntegerField(default=0)
    
    last_attempt = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'materi'],name='unique_progress_kuis_materi')              
        ]
        
        
    
    def __str__(self):
        if self.materi:
            return f"{self.user.username} - {self.materi.judul}"
        return f"{self.user.username} - FINAL {self.kursus.nama}"

# kitajalan/models.py

class MediaPembelajaran(models.Model):
    """Model untuk menyimpan file media lokal"""
    
    JUDUL = 'judul'
    VIDEO = 'video'
    GAMBAR = 'gambar'
    FILE = 'file'
    
    TIPE_CHOICES = (
        (VIDEO, 'Video'),
        (GAMBAR, 'Gambar'),
        (FILE, 'File Dokumen'),
    )
    
    judul = models.CharField(max_length=200)
    tipe = models.CharField(max_length=10, choices=TIPE_CHOICES)
    
    # FileField bisa untuk semua jenis file [citation:3][citation:7]
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',  # Akan terorganisir per tanggal
        help_text="Upload video, gambar, atau dokumen"
    )
    
    # Khusus gambar bisa pakai ImageField (perlu Pillow)
    # gambar = models.ImageField(upload_to='images/', blank=True, null=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.judul
    
    def extension(self):
        """Mendapatkan ekstensi file [citation:7]"""
        import os
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()
    
    def get_file_type(self):
        """Mendeteksi tipe file dari ekstensi [citation:7]"""
        ext = self.extension()
        video_ext = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
        image_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
        
        if ext in video_ext:
            return 'video'
        elif ext in image_ext:
            return 'image'
        else:
            return 'file'


# =========================
# Chatbot FAQ (untuk API chatbot)
# =========================

class FAQChatbot(models.Model):

    pertanyaan = models.CharField(
        max_length=255,
        help_text="Pertanyaan utama"
    )

    kata_kunci = models.CharField(
        max_length=255,
        help_text="Pisahkan dengan koma. Contoh: daftar, registrasi"
    )

    jawaban = models.TextField()

    urutan = models.PositiveIntegerField(
        default=0,
        help_text="Prioritas jawaban (angka lebih kecil lebih prioritas)"
    )

    aktif = models.BooleanField(default=True)

    dibuat = models.DateTimeField(auto_now_add=True)

    diupdate = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["urutan", "pertanyaan"]
        verbose_name = "FAQ Chatbot"
        verbose_name_plural = "FAQ Chatbot"

    def __str__(self):
        return self.pertanyaan    