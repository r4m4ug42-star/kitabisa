from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

import markdown
import bleach

from .models import (
    Kursus, Materi, HalamanMateri, HalamanBlok,
    ProgressMateri, ProgressHalaman,
    Enrollment, BankSoal, SesiKuis,
    JawabanKuis, ProgressKuis, MediaPembelajaran,
    FAQChatbot
)

from .permissions import user_is_enrolled
from .services import hitung_progress_materi
from .decorators import enrollment_required
from reportlab.pdfgen import canvas
from .forms import JawabanKuisForm
import random
import traceback
import datetime

import logging
logger = logging.getLogger(__name__)

logger.info("Ini info")
logger.error("Ini error")

# =========================
# FUNGSI HELPER CEK AKSES
# =========================

def can_access_halaman(user, halaman):
    """
    Cek apakah user bisa mengakses halaman tertentu
    Halaman bisa diakses jika:
    1. Ini adalah halaman pertama dalam materi, ATAU
    2. Semua halaman sebelumnya dalam materi ini sudah selesai
    """
    if not user.is_authenticated:
        return False
    
    materi = halaman.materi
    
    # Ambil semua halaman dalam materi ini, urut berdasarkan urutan
    semua_halaman = materi.halaman.all().order_by('urutan')
    
    # Cari posisi halaman ini
    try:
        index = list(semua_halaman).index(halaman)
    except ValueError:
        return False
    
    # Jika ini halaman pertama (index 0), boleh diakses
    if index == 0:
        return True
    
    # Cek apakah semua halaman SEBELUMnya sudah selesai
    halaman_sebelumnya = semua_halaman[:index]
    for h in halaman_sebelumnya:
        if not ProgressHalaman.objects.filter(user=user, halaman=h, is_done=True).exists():
            return False
    
    return True

def can_access_materi(user, materi):
    """
    Cek apakah user bisa mengakses materi tertentu
    Materi bisa diakses jika semua materi sebelumnya sudah lulus kuis
    """
    if not user.is_authenticated:
        return False
    
    kursus = materi.kursus
    
    # Ambil semua materi dalam kursus, urut berdasarkan urutan
    semua_materi = kursus.materi.all().order_by('urutan')
    
    # Cari posisi materi ini
    try:
        index = list(semua_materi).index(materi)
    except ValueError:
        return False
    
    # Jika ini materi pertama (index 0), boleh diakses
    if index == 0:
        return True
    
    # Cek apakah semua materi SEBELUMnya sudah lulus kuis
    materi_sebelumnya = semua_materi[:index]
    for m in materi_sebelumnya:
        try:
            progress = ProgressKuis.objects.get(user=user, materi=m, kursus=kursus)
            if not progress.sudah_lulus:
                return False
        except ProgressKuis.DoesNotExist:
            return False
    
    return True

def get_halaman_pertama_belum(user, materi):
    """
    Mendapatkan halaman pertama dalam materi yang belum selesai
    """
    semua_halaman = materi.halaman.all().order_by('urutan')
    for halaman in semua_halaman:
        if not ProgressHalaman.objects.filter(user=user, halaman=halaman, is_done=True).exists():
            return halaman
    return None

def get_materi_pertama_belum_lulus(user, kursus):
    """
    Mendapatkan materi pertama dalam kursus yang belum lulus kuis
    """
    semua_materi = kursus.materi.all().order_by('urutan')
    for materi in semua_materi:
        try:
            progress = ProgressKuis.objects.get(user=user, materi=materi, kursus=kursus)
            if not progress.sudah_lulus:
                return materi
        except ProgressKuis.DoesNotExist:
            return materi
    return None


# =========================
# PREVIEW MARKDOWN (AJAX)
# =========================

def preview_markdown(request):
    konten = request.POST.get('konten', '')

    html = markdown.markdown(
        konten,
        extensions=['fenced_code', 'codehilite', 'tables']
    )

    allowed_tags = bleach.sanitizer.ALLOWED_TAGS + [
        'p', 'pre', 'code', 'span',
        'h1','h2','h3','h4',
        'ul','ol','li',
        'img','iframe'
    ]

    html = bleach.clean(html, tags=allowed_tags, strip=True)

    return JsonResponse({'html': html})


# =========================
# DAFTAR KURSUS
# =========================

def daftar_kursus(request):
    kursus_list = Kursus.objects.all()

    enrolled_kursus = []
    if request.user.is_authenticated:
        enrolled_kursus = Enrollment.objects.filter(
            user=request.user
        ).values_list('kursus_id', flat=True)

    return render(request, 'daftar_kursus.html', {
        'kursus_list': kursus_list,
        'enrolled_kursus': enrolled_kursus
    })


# =========================
# DAFTAR MATERI (DENGAN REDIRECT OTOMATIS)
# =========================

@login_required
def daftar_materi(request, kursus_slug, materi_slug=None, halaman_slug=None):
    """
    View yang menangani tampilan kursus dengan sidebar dan konten dalam satu halaman
    """
    try:
        logger.info("\n" + "="*60)
        logger.info("DEBUG: Masuk ke daftar_materi")
        logger.info(f"Path: {request.path}")
        logger.info(f"kursus_slug: {kursus_slug}")
        logger.info(f"materi_slug: {materi_slug}")
        logger.info(f"halaman_slug: {halaman_slug}")
        
        # Deteksi apakah ini debug mode
        is_debug = 'debug' in request.path
        logger.info(f"Debug mode: {is_debug}")
        
        # 1. Ambil kursus
        kursus = get_object_or_404(Kursus, slug=kursus_slug)
        logger.info(f"Kursus ditemukan: {kursus.nama}")
        
        # 2. Cek enrollment
        is_enrolled = Enrollment.objects.filter(
            user=request.user, 
            kursus=kursus
        ).exists()
        logger.info(f"User terdaftar: {is_enrolled}")
        
        if not is_enrolled:
            logger.info("User tidak terdaftar, redirect ke daftar_kursus")
            return redirect('daftar_kursus')
        
        # 3. Ambil semua materi dengan prefetch halaman
        materi_list = kursus.materi.all().prefetch_related('halaman')
        logger.info(f"Jumlah materi: {materi_list.count()}")
        
        # Jika tidak ada materi, kembalikan ke daftar kursus
        if not materi_list.exists():
            messages.warning(request, "Belum ada materi dalam kursus ini")
            return redirect('daftar_kursus')
        
        # 4. Inisialisasi variabel
        materi_aktif = None
        halaman_aktif = None
        blok_list = []
        progress_halaman = []
        prev_halaman = None
        next_halaman = None
        progress_map = {}
        total_halaman = 0
        total_selesai = 0
        
        # 5. Jika ada materi_slug
        if materi_slug:
            try:
                materi_aktif = Materi.objects.get(kursus=kursus, slug=materi_slug)
                logger.info(f"Materi aktif: {materi_aktif.judul}")
                
                # ===== CEK AKSES MATERI =====
                if not can_access_materi(request.user, materi_aktif):
                    messages.error(request, "Anda harus menyelesaikan materi sebelumnya terlebih dahulu")
                    # Redirect ke materi pertama yang belum lulus kuis
                    materi_pertama_belum = get_materi_pertama_belum_lulus(request.user, kursus)
                    if materi_pertama_belum:
                        halaman_pertama = materi_pertama_belum.halaman.first()
                        if halaman_pertama:
                            return redirect('halaman_detail',
                                      kursus_slug=kursus.slug,
                                      materi_slug=materi_pertama_belum.slug,
                                      halaman_slug=halaman_pertama.slug)
                # ===== END CEK AKSES =====

                # 6. Jika ada halaman_slug
                if halaman_slug:
                    try:
                        halaman_aktif = HalamanMateri.objects.get(
                            materi=materi_aktif, 
                            slug=halaman_slug
                        )
                        logger.info(f"Halaman aktif: {halaman_aktif.judul}")
                        
                        # Ambil blok
                        blok_list = halaman_aktif.blok.all().order_by('urutan')
                        logger.info(f"Jumlah blok: {blok_list.count()}")
                        
                        # Ambil progress halaman user
                        progress_halaman = ProgressHalaman.objects.filter(
                            user=request.user,
                            halaman__materi=materi_aktif,
                            is_done=True
                        ).values_list('halaman_id', flat=True)
                        
                        # Navigasi
                        halaman_list = list(materi_aktif.halaman.all().order_by('urutan'))
                        if halaman_aktif in halaman_list:
                            current_index = halaman_list.index(halaman_aktif)
                            if current_index > 0:
                                prev_halaman = halaman_list[current_index - 1]
                            if current_index < len(halaman_list) - 1:
                                next_halaman = halaman_list[current_index + 1]
                                
                    except HalamanMateri.DoesNotExist:
                        logger.info(f"Halaman dengan slug {halaman_slug} tidak ditemukan")
                        # Redirect ke halaman pertama materi ini
                        halaman_pertama = materi_aktif.halaman.first()
                        if halaman_pertama:
                            return redirect('halaman_detail',
                                          kursus_slug=kursus.slug,
                                          materi_slug=materi_aktif.slug,
                                          halaman_slug=halaman_pertama.slug)
                        
            except Materi.DoesNotExist:
                logger.info(f"Materi dengan slug {materi_slug} tidak ditemukan")
                # Redirect ke materi pertama
                materi_pertama = materi_list.first()
                if materi_pertama:
                    halaman_pertama = materi_pertama.halaman.first()
                    if halaman_pertama:
                        return redirect('halaman_detail',
                                      kursus_slug=kursus.slug,
                                      materi_slug=materi_pertama.slug,
                                      halaman_slug=halaman_pertama.slug)
        
        # Jika tidak ada materi_slug, redirect ke materi pertama
        if not materi_aktif:
            materi_pertama = materi_list.first()
            if materi_pertama:
                halaman_pertama = materi_pertama.halaman.first()
                if halaman_pertama:
                    return redirect('halaman_detail',
                                  kursus_slug=kursus.slug,
                                  materi_slug=materi_pertama.slug,
                                  halaman_slug=halaman_pertama.slug)
        
        # 7. Hitung progress untuk semua materi
        for materi in materi_list:
            progress, _ = ProgressMateri.objects.get_or_create(
                user=request.user,
                materi=materi
            )
            progress_map[materi.id] = progress.is_done
            
            h_list = materi.halaman.all()
            total_halaman += h_list.count()
            total_selesai += ProgressHalaman.objects.filter(
                user=request.user,
                halaman__in=h_list,
                is_done=True
            ).count()
        
        progress_percent = 0
        if total_halaman > 0:
            progress_percent = int((total_selesai / total_halaman) * 100)
        
        # 8. Siapkan context
        context = {
            'kursus': kursus,
            'materi_list': materi_list,
            'materi_aktif': materi_aktif,
            'halaman_aktif': halaman_aktif,
            'blok_list': blok_list,
            'progress_map': progress_map,
            'progress_halaman': progress_halaman,
            'prev_halaman': prev_halaman,
            'next_halaman': next_halaman,
            'total_halaman': total_halaman,
            'total_selesai': total_selesai,
            'progress_percent': progress_percent,
            'debug_mode': is_debug,
        }
        
        logger.info("Context siap dikirim ke template")
        logger.info(f"materi_aktif: {materi_aktif}")
        logger.info(f"halaman_aktif: {halaman_aktif}")
        logger.info(f"blok_list count: {len(blok_list)}")
        logger.info("="*60)
        
        # 9. Pilih template berdasarkan mode
        if is_debug:
            template_name = 'daftar_materi_sederhana.html'
        else:
            template_name = 'daftar_materi.html'
        
        return render(request, template_name, context)
        
    except Exception as e:
        logger.info(f"ERROR: {str(e)}")
        traceback.print_exc()
        messages.error(request, f"Terjadi kesalahan: {str(e)}")
        return redirect('daftar_kursus')

# ============================
# daftar halaman
# =========================

@login_required
def daftar_halaman(request, kursus_slug, materi_slug):
    """
    View khusus untuk menampilkan daftar halaman dalam suatu materi
    (TANPA menampilkan konten halaman)
    """
    kursus = get_object_or_404(Kursus, slug=kursus_slug)
    
    # Cek enrollment
    if not Enrollment.objects.filter(user=request.user, kursus=kursus).exists():
        messages.error(request, "Anda harus terdaftar di kursus ini")
        return redirect('daftar_kursus')
    
    materi = get_object_or_404(Materi, slug=materi_slug, kursus=kursus)
    
    # Ambil semua materi untuk sidebar
    materi_list = kursus.materi.all().prefetch_related('halaman')
    
    # Progress untuk semua materi
    progress_map = {}
    total_halaman = 0
    total_selesai = 0
    
    for m in materi_list:
        progress, _ = ProgressMateri.objects.get_or_create(
            user=request.user,
            materi=m
        )
        progress_map[m.id] = progress.is_done
        
        h_list = m.halaman.all()
        total_halaman += h_list.count()
        total_selesai += ProgressHalaman.objects.filter(
            user=request.user,
            halaman__in=h_list,
            is_done=True
        ).count()
    
    progress_percent = int((total_selesai / total_halaman) * 100) if total_halaman > 0 else 0
    
    context = {
        'kursus': kursus,
        'materi_list': materi_list,
        'materi_aktif': materi,
        'halaman_aktif': None,  # TIDAK ADA halaman aktif
        'blok_list': [],  # KOSONG
        'progress_map': progress_map,
        'progress_halaman': [],  # KOSONG
        'prev_halaman': None,
        'next_halaman': None,
        'total_halaman': total_halaman,
        'total_selesai': total_selesai,
        'progress_percent': progress_percent,
        'debug_mode': 'debug' in request.path,
    }
    
    template_name = 'daftar_materi.html'
    return render(request, template_name, context)


# =========================
# DETAIL HALAMAN (BERDASARKAN SLUG)
# =========================

@login_required
def halaman_detail_slug(request, kursus_slug, materi_slug, halaman_slug):
    """
    View untuk menampilkan detail halaman berdasarkan slug
    """
    try:
        logger.info("\n" + "="*50)
        logger.info("MASUK KE HALAMAN_DETAIL_SLUG")
        logger.info(f"kursus_slug: {kursus_slug}")
        logger.info(f"materi_slug: {materi_slug}")
        logger.info(f"halaman_slug: {halaman_slug}")
        
        # 1. Ambil kursus
        kursus = get_object_or_404(Kursus, slug=kursus_slug)
        logger.info(f"Kursus ditemukan: {kursus.nama}")
        
        # 2. Cek enrollment
        if not Enrollment.objects.filter(user=request.user, kursus=kursus).exists():
            logger.info("User tidak terdaftar!")
            messages.error(request, "Anda harus terdaftar di kursus ini")
            return redirect('daftar_kursus')
        
        # 3. Ambil materi
        materi = get_object_or_404(Materi, slug=materi_slug, kursus=kursus)
        logger.info(f"Materi ditemukan: {materi.judul}")
        
        # 4. Ambil halaman
        halaman = get_object_or_404(HalamanMateri, slug=halaman_slug, materi=materi)
        logger.info(f"Halaman ditemukan: {halaman.judul}")
        
        # 5. CEK AKSES HALAMAN (apakah halaman sebelumnya sudah selesai)
        if not can_access_halaman(request.user, halaman):
            logger.info(f"User tidak bisa mengakses halaman {halaman.judul} karena halaman sebelumnya belum selesai")
            messages.warning(request, "Anda harus menyelesaikan halaman sebelumnya terlebih dahulu")
            
            # Redirect ke halaman pertama yang belum selesai
            halaman_pertama_belum = get_halaman_pertama_belum(request.user, materi)
            if halaman_pertama_belum:
                return redirect('halaman_detail', 
                                kursus_slug=kursus.slug, 
                                materi_slug=materi.slug, 
                                halaman_slug=halaman_pertama_belum.slug)
            else:
                # Jika semua halaman sudah selesai, redirect ke materi detail
                return redirect('materi_detail', kursus_slug=kursus.slug, materi_slug=materi.slug)
        
        # 6. Ambil semua halaman dalam materi untuk navigasi
        halaman_list = HalamanMateri.objects.filter(materi=materi).order_by('urutan')
        
        # 7. Ambil blok konten
        blok_list = HalamanBlok.objects.filter(halaman=halaman).order_by('urutan')
        logger.info(f"Jumlah blok: {blok_list.count()}")
        
        # 8. Ambil progress halaman user
        progress_halaman = ProgressHalaman.objects.filter(
            user=request.user,
            halaman__in=halaman_list,
            is_done=True
        ).values_list('halaman_id', flat=True)
        
        logger.info(f"Progress halaman: {list(progress_halaman)}")
        logger.info(f"Halaman ini ID: {halaman.id}, Selesai? {halaman.id in progress_halaman}")
        
        # 9. Cari posisi halaman sekarang untuk navigasi
        halaman_array = list(halaman_list)
        try:
            index = halaman_array.index(halaman)
        except ValueError:
            logger.error(f"Halaman {halaman.id} tidak ditemukan dalam list")
            messages.error(request, "Halaman tidak valid")
            return redirect('materi_detail', kursus_slug=kursus.slug, materi_slug=materi.slug)
        
        # 10. Prev/Next halaman
        prev_halaman = halaman_array[index - 1] if index > 0 else None
        next_halaman = halaman_array[index + 1] if index < len(halaman_array) - 1 else None
        
        # 11. Progress untuk semua materi (untuk sidebar)
        progress_map = {}
        for m in kursus.materi.all():
            progress, _ = ProgressMateri.objects.get_or_create(
                user=request.user,
                materi=m
            )
            progress_map[m.id] = progress.is_done
        
        # 12. Hitung total progress kursus
        total_halaman = HalamanMateri.objects.filter(materi__kursus=kursus).count()
        total_selesai = ProgressHalaman.objects.filter(
            user=request.user,
            halaman__materi__kursus=kursus,
            is_done=True
        ).count()
        progress_percent = int((total_selesai / total_halaman) * 100) if total_halaman > 0 else 0
        
        logger.info(f"Total halaman: {total_halaman}, Selesai: {total_selesai}")
        logger.info("="*50)
        
        # 13. Siapkan context
        context = {
            'kursus': kursus,
            'materi_list': kursus.materi.all().prefetch_related('halaman'),
            'materi_aktif': materi,
            'halaman_aktif': halaman,
            'blok_list': blok_list,
            'progress_map': progress_map,
            'progress_halaman': progress_halaman,
            'prev_halaman': prev_halaman,
            'next_halaman': next_halaman,
            'total_halaman': total_halaman,
            'total_selesai': total_selesai,
            'progress_percent': progress_percent,
        }
        
        # 14. Render template
        return render(request, 'kitajalan/halaman_detail.html', context)
    
    except Exception as e:
        logger.error(f"ERROR di halaman_detail_slug: {str(e)}")
        traceback.print_exc()
        messages.error(request, f"Terjadi kesalahan: {str(e)}")
        return redirect('daftar_kursus')

# =========================
# TANDAI HALAMAN SELESAI
# =========================

@login_required
def tandai_halaman_selesai(request, halaman_id):
    """
    Tandai halaman selesai dan return JSON response untuk AJAX
    """
    try:
        halaman = get_object_or_404(HalamanMateri, id=halaman_id)
        materi = halaman.materi
        kursus = materi.kursus
        
        # Cek enrollment
        if not Enrollment.objects.filter(user=request.user, kursus=kursus).exists():
            return JsonResponse({'success': False, 'error': 'Not enrolled'}, status=403)
        
        # Tandai halaman selesai
        progress, created = ProgressHalaman.objects.update_or_create(
            user=request.user,
            halaman=halaman,
            defaults={"is_done": True}
        )
        
        # Hitung progress materi
        halaman_list = materi.halaman.all().order_by("urutan")
        total_halaman = halaman_list.count()
        total_selesai = ProgressHalaman.objects.filter(
            user=request.user,
            halaman__materi=materi,
            is_done=True
        ).count()
        
        # Tandai materi selesai jika semua halaman selesai
        materi_selesai = False
        if total_halaman > 0 and total_halaman == total_selesai:
            ProgressMateri.objects.update_or_create(
                user=request.user,
                materi=materi,
                defaults={"is_done": True}
            )
            materi_selesai = True
        
        # Cari halaman berikutnya yang BELUM selesai
        next_halaman = None
        for h in halaman_list:
            if not ProgressHalaman.objects.filter(user=request.user, halaman=h, is_done=True).exists():
                next_halaman = h
                break
        
        return JsonResponse({
            'success': True,
            'materi_selesai': materi_selesai,
            'total_selesai': total_selesai,
            'total_halaman': total_halaman,
            'next_halaman_slug': next_halaman.slug if next_halaman else None,
            'next_halaman_judul': next_halaman.judul if next_halaman else None,
        })
        
    except Exception as e:
        logger.info(f"Error in tandai_halaman_selesai: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =========================
# API KONTEN HALAMAN (AJAX)
# =========================

@login_required
@require_GET
def api_konten_halaman(request, kursus_slug, materi_slug, halaman_slug):
    """
    API endpoint untuk mengambil konten halaman via AJAX
    """
    try:
        kursus = get_object_or_404(Kursus, slug=kursus_slug)
        materi = get_object_or_404(Materi, kursus=kursus, slug=materi_slug)
        halaman = get_object_or_404(HalamanMateri, materi=materi, slug=halaman_slug)
        
        # Cek enrollment
        if not Enrollment.objects.filter(user=request.user, kursus=kursus).exists():
            return HttpResponse("Unauthorized", status=403)
        
        # Ambil blok konten
        blok_list = halaman.blok.all().order_by('urutan')
        
        # Ambil semua halaman dalam materi
        halaman_list = list(materi.halaman.all().order_by('urutan'))
        
        # Progress halaman
        progress_halaman = ProgressHalaman.objects.filter(
            user=request.user,
            halaman__in=halaman_list,
            is_done=True
        ).values_list('halaman_id', flat=True)
        
        # Navigasi
        current_index = halaman_list.index(halaman)
        prev_halaman = halaman_list[current_index - 1] if current_index > 0 else None
        next_halaman = halaman_list[current_index + 1] if current_index < len(halaman_list) - 1 else None
        
        # Render ke HTML
        html = render_to_string('includes/halaman_content.html', {
            'kursus': kursus,
            'materi_aktif': materi,
            'halaman_aktif': halaman,
            'blok_list': blok_list,
            'progress_halaman': progress_halaman,
            'prev_halaman': prev_halaman,
            'next_halaman': next_halaman,
        }, request=request)
        
        return HttpResponse(html)
        
    except Exception as e:
        logger.info(f"Error in api_konten_halaman: {e}")
        return HttpResponse("Error", status=500)


# =========================
# TEST VIEW
# =========================

def test_daftar_materi(request, kursus_slug):
    """View sederhana untuk testing"""
    kursus = get_object_or_404(Kursus, slug=kursus_slug)
    materi_list = kursus.materi.all()
    
    return render(request, 'daftar_materi_simple.html', {
        'kursus': kursus,
        'materi_list': materi_list,
        'debug_info': 'Ini test view'
    })


# =========================
# UPLOAD MEDIA
# =========================

@login_required
def upload_media(request):
    """View untuk upload file media"""
    if request.method == 'POST':
        judul = request.POST.get('judul')
        tipe = request.POST.get('tipe')
        file = request.FILES.get('file')
        
        if file and judul and tipe:
            media = MediaPembelajaran.objects.create(
                judul=judul,
                tipe=tipe,
                file=file,
                uploaded_by=request.user
            )
            messages.success(request, f'File "{judul}" berhasil diupload!')
            return redirect('daftar_media')
    
    return render(request, 'upload_media.html')

# =========================
# DOWNLOAD SERTIFIKAT
# =========================

@login_required
def download_sertifikat(request, slug):
    kursus = get_object_or_404(Kursus, slug=slug)

    # Cek enrollment
    if not Enrollment.objects.filter(user=request.user, kursus=kursus).exists():
        return HttpResponse("Kamu belum terdaftar.", status=403)

    total_materi = kursus.materi.count()
    selesai = ProgressMateri.objects.filter(
        user=request.user,
        materi__kursus=kursus,
        is_done=True
    ).count()

    progress = int((selesai / total_materi) * 100) if total_materi > 0 else 0

    if progress < 100:
        return HttpResponse("Kursus belum selesai.", status=403)

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sertifikat_{kursus.slug}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(300, 750, "SERTIFIKAT KELULUSAN")

    p.setFont("Helvetica", 14)
    p.drawCentredString(300, 700, f"Diberikan kepada:")
    p.drawCentredString(300, 670, request.user.username)

    p.drawCentredString(300, 630, "Atas penyelesaian kursus:")
    p.drawCentredString(300, 600, kursus.nama)

    p.drawCentredString(300, 550, "Selamat dan sukses!")

    p.showPage()
    p.save()

    return response

# =========================
# ENROLL KURSUS
# =========================

@login_required
def enroll_kursus(request, slug):
    kursus = get_object_or_404(Kursus, slug=slug)

    Enrollment.objects.get_or_create(
        user=request.user,
        kursus=kursus
    )

    return redirect('dashboard')


# =========================
# DASHBOARD
# =========================

@login_required
def dashboard(request):
    kursus_list = Kursus.objects.all()
    data = []

    for kursus in kursus_list:
        total_materi = Materi.objects.filter(kursus=kursus).count()
        selesai = ProgressMateri.objects.filter(
            user=request.user,
            materi__kursus=kursus,
            is_done=True
        ).count()

        progress = 0
        if total_materi > 0:
            progress = int((selesai / total_materi) * 100)

        materi_pertama = Materi.objects.filter(
            kursus=kursus
        ).order_by("urutan").first()

        data.append({
            "kursus": kursus,
            "total_materi": total_materi,
            "selesai": selesai,
            "progress": progress,
            "materi_pertama": materi_pertama,
        })

    return render(request, "kitajalan/dashboard.html", {
        "data": data
    })


# =========================
# MULAI KUIS (DENGAN TIMER)
# =========================

@login_required
def mulai_kuis(request, kursus_slug, materi_slug=None):
    """
    Memulai sesi kuis baru (per materi atau final) dengan timer
    """
    
    kursus = get_object_or_404(Kursus, slug=kursus_slug)
    
    # Cek enrollment
    if not Enrollment.objects.filter(user=request.user, kursus=kursus).exists():
        messages.error(request, "Anda harus terdaftar di kursus ini")
        return redirect('daftar_kursus')
    
    # CEK APAKAH INI FINAL TEST ATAU KUIS MATERI
    if materi_slug:
        # KUIS MATERI
        materi = get_object_or_404(Materi, kursus=kursus, slug=materi_slug)
        tipe = 'materi'
        title = f"Kuis: {materi.judul}"
        materi_obj = materi
        
        # CEK PROGRESS - HARUS 100%
        halaman_list = materi.halaman.all()
        total_halaman = halaman_list.count()
        selesai = ProgressHalaman.objects.filter(
            user=request.user,
            halaman__in=halaman_list,
            is_done=True
        ).count()
        
        print(f"DEBUG: total_halaman={total_halaman}, selesai={selesai}")
        
        if selesai < total_halaman:
            messages.error(request, f"Selesaikan semua halaman materi terlebih dahulu. Progress: {selesai}/{total_halaman}")
            return redirect('materi_detail', kursus_slug, materi_slug)
    else:
        # FINAL TEST
        materi = None
        tipe = 'final'
        title = f"Final Test: {kursus.nama}"
        materi_obj = None
        
        # CEK SEMUA MATERI SUDAH LULUS KUIS
        for m in kursus.materi.all():
            try:
                progress = ProgressKuis.objects.get(
                    user=request.user,
                    materi=m,
                    kursus=kursus
                )
                if not progress.sudah_lulus:
                    messages.error(request, f"Selesaikan kuis {m.judul} terlebih dahulu")
                    return redirect('materi_detail', kursus_slug, m.slug)
            except ProgressKuis.DoesNotExist:
                messages.error(request, f"Selesaikan kuis {m.judul} terlebih dahulu")
                return redirect('materi_detail', kursus_slug, m.slug)
    
    # CEK COOLDOWN
    cooldown_sesi = SesiKuis.objects.filter(
        user=request.user,
        kursus=kursus,
        materi=materi_obj,
        status__in=['gagal', 'waktu_habis']
    ).order_by('-completed_at').first()
    
    if cooldown_sesi and cooldown_sesi.dalam_cooldown():
        sisa = cooldown_sesi.sisa_cooldown()
        messages.error(request, f"Anda harus menunggu {sisa} detik sebelum mencoba lagi")
        if materi_slug:
            return redirect('materi_detail', kursus_slug, materi_slug)
        else:
            return redirect('daftar_materi', kursus_slug)
    
    # CEK PERCOBAAN SEBELUMNYA
    sesi_sebelumnya = SesiKuis.objects.filter(
        user=request.user,
        kursus=kursus,
        materi=materi_obj,
        tipe=tipe
    ).order_by('-percobaan_ke')
    
    if sesi_sebelumnya.exists():
        sesi_terakhir = sesi_sebelumnya.first()
        percobaan_ke = sesi_terakhir.percobaan_ke + 1
        
        if percobaan_ke > 50:
            messages.error(request, "Anda telah mencapai batas maksimal percobaan (50x)")
            if materi_slug:
                return redirect('materi_detail', kursus_slug, materi_slug)
            else:
                return redirect('daftar_materi', kursus_slug)
        
        # AMBIL 2 SOAL SALAH DARI SESI SEBELUMNYA
        soal_dari_sebelumnya = []
        if sesi_terakhir.status == 'gagal':
            jawaban_salah = JawabanKuis.objects.filter(
                sesi=sesi_terakhir,
                is_benar=False
            ).select_related('soal')
            
            for jawaban in jawaban_salah:
                if jawaban.soal.is_active and len(soal_dari_sebelumnya) < 2:
                    soal_dari_sebelumnya.append(jawaban.soal)
    else:
        percobaan_ke = 1
        soal_dari_sebelumnya = []
    
    # AMBIL SOAL BARU
    if materi_slug:
        bank_soal = BankSoal.objects.filter(
            kursus=kursus,
            materi=materi,
            tipe='materi',
            is_active=True
        )
    else:
        bank_soal = BankSoal.objects.filter(
            kursus=kursus,
            tipe='final',
            is_active=True
        )
    
    excluded_ids = [s.id for s in soal_dari_sebelumnya]
    soal_baru = list(bank_soal.exclude(id__in=excluded_ids))
    random.shuffle(soal_baru)
    
    # TOTAL 5 SOAL
    soal_terpilih = soal_dari_sebelumnya + soal_baru[:5 - len(soal_dari_sebelumnya)]
    random.shuffle(soal_terpilih)
    
    # BUAT SESI BARU
    sesi = SesiKuis.objects.create(
    user=request.user,
    kursus=kursus,
    materi=materi_obj,
    tipe=tipe,
    percobaan_ke=percobaan_ke,
    total_soal=len(soal_terpilih),
    status='sedang',
    waktu_mulai=timezone.now(),
    batas_waktu=300
    )

    # SIMPAN DI SESSION
    request.session['sesi_kuis_id'] = sesi.id
    request.session['soal_terpilih'] = [s.id for s in soal_terpilih]
    request.session['soal_saat_ini'] = 0

    # TAMBAHKAN PRINT UNTUK DEBUG
    #print(f"✅ SESI KUIS DIBUAT DENGAN ID: {sesi.id}")
    #print(f"✅ REDIRECT KE: kerjakan_kuis dengan ID: {sesi.id}")

    # PASTIKAN REDIRECT INI YANG DIPAKAI
    return redirect('kerjakan_kuis', sesi_id=sesi.id)


# =========================
# KERJAKAN KUIS (PER SOAL) - DENGAN TIMER
# =========================

@login_required
def kerjakan_kuis(request, sesi_id):
    """
    Mengerjakan kuis satu per satu dengan timer
    """
    from django.utils import timezone
    
    sesi = get_object_or_404(SesiKuis, id=sesi_id, user=request.user)
    
    # CEK APAKAH WAKTU HABIS
    if sesi.is_waktu_habis():
        sesi.tandai_waktu_habis()
        messages.error(request, "Waktu pengerjaan kuis habis!")
        return redirect('hasil_kuis', sesi_id=sesi.id)
    
    if sesi.status != 'sedang':
        return redirect('hasil_kuis', sesi_id=sesi.id)
    
    # AMBIL DATA DARI SESSION
    soal_ids = request.session.get('soal_terpilih', [])
    soal_saat_ini = request.session.get('soal_saat_ini', 0)
    
    # VALIDASI
    if not soal_ids:
        messages.error(request, "Terjadi kesalahan. Silakan mulai kuis ulang.")
        if sesi.materi:
            return redirect('materi_detail', sesi.kursus.slug, sesi.materi.slug)
        else:
            return redirect('daftar_materi', sesi.kursus.slug)
    
    if soal_saat_ini >= len(soal_ids):
        return redirect('selesai_kuis', sesi_id=sesi.id)
    
    # AMBIL SOAL
    try:
        soal = get_object_or_404(BankSoal, id=soal_ids[soal_saat_ini])
    except (BankSoal.DoesNotExist, IndexError):
        messages.error(request, "Soal tidak ditemukan.")
        return redirect('hasil_kuis', sesi_id=sesi.id)
    
    nomor = soal_saat_ini + 1
    progress = int((soal_saat_ini / len(soal_ids)) * 100)
    
    form = JawabanKuisForm(soal=soal)
    
    if request.method == 'POST':
        form = JawabanKuisForm(request.POST, soal=soal)
        if form.is_valid():
            jawaban = form.cleaned_data['jawaban']
            is_benar = (jawaban == soal.jawaban_benar)
            
            JawabanKuis.objects.create(
                sesi=sesi,
                soal=soal,
                jawaban_user=jawaban,
                is_benar=is_benar
            )
            
            request.session['soal_saat_ini'] = soal_saat_ini + 1
            return redirect('kerjakan_kuis', sesi_id=sesi.id)
    
    context = {
        'sesi': sesi,
        'soal': soal,
        'form': form,
        'nomor': nomor,
        'total': len(soal_ids),
        'progress': progress,
        'sisa_waktu': sesi.sisa_waktu(),
        'batas_waktu': sesi.batas_waktu,
    }
    
    return render(request, 'kuis/kerjakan_per_soal.html', context)



# =========================
# SELESAI KUIS - DENGAN COOLDOWN
# =========================

@login_required
def selesai_kuis(request, sesi_id):
    """
    Menghitung hasil kuis setelah semua soal dijawab dan set cooldown jika gagal
    """
    from django.utils import timezone
    import datetime
    
    sesi = get_object_or_404(SesiKuis, id=sesi_id, user=request.user)
    
    # Jika sudah selesai sebelumnya, langsung redirect
    if sesi.status in ['lulus', 'gagal', 'waktu_habis']:
        return redirect('hasil_kuis', sesi_id=sesi.id)
    
    # Hitung jawaban benar
    jawaban_benar = JawabanKuis.objects.filter(sesi=sesi, is_benar=True).count()
    total_soal = sesi.total_soal
    
    # Pastikan total soal sesuai dengan jumlah jawaban
    if total_soal == 0:
        total_soal = JawabanKuis.objects.filter(sesi=sesi).count()
        sesi.total_soal = total_soal
    
    sesi.jawaban_benar = jawaban_benar
    sesi.waktu_selesai = timezone.now()
    sesi.save()
    
    # Hitung nilai
    sesi.hitung_nilai()
    
    # Cek kelulusan
    lulus = sesi.cek_kelulusan()
    
    # JIKA GAGAL, SET COOLDOWN 1 MENIT
    if not lulus:
        sesi.cooldown_until = timezone.now() + datetime.timedelta(minutes=1)
        sesi.save()
        messages.warning(request, f"Anda belum lulus (Nilai: {sesi.nilai}). Tunggu 1 menit untuk mencoba lagi.")
    else:
        messages.success(request, f"Selamat! Anda lulus dengan nilai {sesi.nilai}!")
    
    # Update progress kuis
    progress, created = ProgressKuis.objects.get_or_create(
        user=request.user,
        kursus=sesi.kursus,
        materi=sesi.materi
    )
    
    progress.total_percobaan += 1
    if sesi.nilai > progress.nilai_tertinggi:
        progress.nilai_tertinggi = sesi.nilai
    
    if lulus:
        progress.sudah_lulus = True
    
    progress.save()
    
    # Hitung statistik untuk ditampilkan di hasil
    jawaban_list = JawabanKuis.objects.filter(sesi=sesi).select_related('soal')
    total_benar = jawaban_list.filter(is_benar=True).count()
    total_salah = jawaban_list.filter(is_benar=False).count()
    
    # Simpan statistik di session untuk hasil
    request.session['hasil_kuis'] = {
        'total_benar': total_benar,
        'total_salah': total_salah,
        'nilai': sesi.nilai,
        'lulus': lulus,
        'percobaan_ke': sesi.percobaan_ke,
    }
    
    # Bersihkan session kuis
    if 'sesi_kuis_id' in request.session:
        del request.session['sesi_kuis_id']
    if 'soal_terpilih' in request.session:
        del request.session['soal_terpilih']
    if 'soal_saat_ini' in request.session:
        del request.session['soal_saat_ini']
    
    return redirect('hasil_kuis', sesi_id=sesi.id)


# =========================
# HASIL KUIS - DENGAN INFORMASI COOLDOWN
# =========================

@login_required
def hasil_kuis(request, sesi_id):
    """
    Menampilkan hasil kuis dengan informasi cooldown jika gagal
    """
    sesi = get_object_or_404(SesiKuis, id=sesi_id, user=request.user)
    
    # Ambil semua jawaban
    jawaban_list = JawabanKuis.objects.filter(sesi=sesi).select_related('soal')
    
    # Hitung statistik
    total_benar = jawaban_list.filter(is_benar=True).count()
    total_salah = jawaban_list.filter(is_benar=False).count()
    
    # Cek cooldown
    dalam_cooldown = sesi.dalam_cooldown()
    sisa_cooldown = sesi.sisa_cooldown()
    
    # Tentukan pesan berdasarkan hasil
    if sesi.status == 'lulus':
        pesan = "Selamat! Anda lulus kuis ini. 🎉"
        if sesi.tipe == 'final':
            pesan += " Anda telah menyelesaikan seluruh kursus!"
    elif sesi.status == 'waktu_habis':
        pesan = f"Waktu habis! Nilai Anda: {sesi.nilai}."
        if sesi.percobaan_ke < 3:
            pesan += f" Silakan coba lagi dalam {sisa_cooldown} detik."
    else:
        if sesi.percobaan_ke < 3:
            pesan = f"Anda belum lulus. Nilai: {sesi.nilai}. Silakan coba lagi!"
            if dalam_cooldown:
                pesan = f"Anda belum lulus. Nilai: {sesi.nilai}. Tunggu {sisa_cooldown} detik untuk mencoba lagi."
        else:
            pesan = f"Anda belum lulus setelah {sesi.percobaan_ke} percobaan. Silakan pelajari kembali materinya."
    
    context = {
        'sesi': sesi,
        'jawaban_list': jawaban_list,
        'total_benar': total_benar,
        'total_salah': total_salah,
        'pesan': pesan,
        'bisa_ulang': sesi.status in ['gagal', 'waktu_habis'] and sesi.percobaan_ke < 3 and not dalam_cooldown,
        'dalam_cooldown': dalam_cooldown,
        'sisa_cooldown': sisa_cooldown,
        'sisa_cooldown_format': sesi.format_waktu(sisa_cooldown) if hasattr(sesi, 'format_waktu') else str(sisa_cooldown),
        'percobaan_ke': sesi.percobaan_ke,
        'max_percobaan': 3,
    }
    
    return render(request, 'kuis/hasil.html', context)


# =========================
# CHATBOT faq
# =========================

from .models import FAQChatbot


def chatbot(request):

    message = request.GET.get("message", "").lower()

    if not message:
        return JsonResponse({
            "reply": "Silakan tuliskan pertanyaan Anda."
        })

    faqs = FAQChatbot.objects.filter(aktif=True)

    for faq in faqs:

        keywords = [k.strip() for k in faq.kata_kunci.lower().split(",")]

        for keyword in keywords:

            if keyword in message:

                return JsonResponse({
                    "reply": faq.jawaban
                })

    return JsonResponse({
        "reply": "Maaf saya belum menemukan jawaban yang sesuai. Silakan hubungi admin."
    })

# =========================
# REGISTER USER ======
# =========================

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False  # akun belum aktif
        )

        messages.success(request, "Akun berhasil dibuat. Tunggu admin mengaktifkan akun Anda.")
        return redirect('login')

    return render(request, 'registration/register.html')