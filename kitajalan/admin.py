# kitajalan/admin.py
from django.contrib import admin
from .models import (
    Kursus, Materi, HalamanMateri, HalamanBlok,
    Enrollment, ProgressMateri, ProgressHalaman,
    BankSoal, SesiKuis, JawabanKuis, ProgressKuis,
    MediaPembelajaran
)

class HalamanBlokInline(admin.TabularInline):
    model = HalamanBlok
    extra = 1
    fields = ['tipe', 'konten', 'urutan']
    ordering = ['urutan']

# PASTIKAN HANYA SATU REGISTRASI UNTUK HalamanMateri
@admin.register(HalamanMateri)
class HalamanMateriAdmin(admin.ModelAdmin):
    list_display = ['judul', 'materi', 'urutan']
    list_filter = ['materi__kursus', 'materi']
    prepopulated_fields = {'slug': ('judul',)}
    search_fields = ['judul']
    inlines = [HalamanBlokInline]

@admin.register(HalamanBlok)
class HalamanBlokAdmin(admin.ModelAdmin):
    list_display = ['id', 'halaman', 'tipe', 'urutan', 'konten_preview']
    list_filter = ['tipe', 'halaman__materi__kursus']
    search_fields = ['konten']
    list_editable = ['urutan']
    raw_id_fields = ['halaman']
    
    def konten_preview(self, obj):
        return obj.konten[:50] + '...' if obj.konten else '-'
    konten_preview.short_description = 'Preview'

@admin.register(Kursus)
class KursusAdmin(admin.ModelAdmin):
    list_display = ['nama', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('nama',)}
    search_fields = ['nama']

@admin.register(Materi)
class MateriAdmin(admin.ModelAdmin):
    list_display = ['judul', 'kursus', 'urutan']
    list_filter = ['kursus']
    prepopulated_fields = {'slug': ('judul',)}

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'kursus', 'status', 'joined_at']
    list_filter = ['kursus', 'status']
    search_fields = ("user__username", "kursus__nama")
    raw_id_fields = ['user', 'kursus']

@admin.register(ProgressMateri)
class ProgressMateriAdmin(admin.ModelAdmin):
    list_display = ['user', 'materi', 'is_done', 'is_quiz_passed', 'updated_at']
    list_filter = ['is_done', 'is_quiz_passed']
    raw_id_fields = ['user', 'materi']

@admin.register(ProgressHalaman)
class ProgressHalamanAdmin(admin.ModelAdmin):
    list_display = ['user', 'halaman', 'is_done']
    list_filter = ['is_done']
    raw_id_fields = ['user', 'halaman']

@admin.register(BankSoal)
class BankSoalAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipe', 'materi', 'kursus', 'pertanyaan_preview', 'is_active']
    list_filter = ['tipe', 'is_active', 'kursus']
    search_fields = ['pertanyaan']
    raw_id_fields = ['materi', 'kursus']
    
    def pertanyaan_preview(self, obj):
        return obj.pertanyaan[:50] + '...' if obj.pertanyaan else '-'
    pertanyaan_preview.short_description = 'Pertanyaan'

@admin.register(SesiKuis)
class SesiKuisAdmin(admin.ModelAdmin):
    list_display = ['user', 'kursus', 'materi', 'tipe', 'status', 'nilai', 'percobaan_ke']
    list_filter = ['status', 'tipe']
    raw_id_fields = ['user', 'materi', 'kursus']

@admin.register(JawabanKuis)
class JawabanKuisAdmin(admin.ModelAdmin):
    list_display = ['sesi', 'soal', 'jawaban_user', 'is_benar']
    list_filter = ['is_benar']
    raw_id_fields = ['sesi', 'soal']

@admin.register(ProgressKuis)
class ProgressKuisAdmin(admin.ModelAdmin):
    list_display = ['user', 'kursus', 'materi', 'sudah_lulus', 'nilai_tertinggi']
    list_filter = ['sudah_lulus']
    raw_id_fields = ['user', 'materi', 'kursus']

@admin.register(MediaPembelajaran)
class MediaPembelajaranAdmin(admin.ModelAdmin):
    list_display = ['judul', 'tipe', 'file', 'uploaded_by', 'uploaded_at']
    list_filter = ['tipe']
    search_fields = ['judul']
    raw_id_fields = ['uploaded_by']

# ========================
# Cahtbot faq admin ======
# ========================

from .models import FAQChatbot


@admin.register(FAQChatbot)
class FAQChatbotAdmin(admin.ModelAdmin):

    list_display = (
        "pertanyaan",
        "kata_kunci",
        "urutan",
        "aktif",
        "dibuat"
    )

    list_filter = ("aktif",)

    search_fields = (
        "pertanyaan",
        "kata_kunci",
        "jawaban"
    )

    ordering = ("urutan",)