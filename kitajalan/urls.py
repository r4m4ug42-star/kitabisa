#from django.urls import path, include
#from . import views
from django.shortcuts import redirect
from django.http import HttpResponse


urlpatterns = [

    # ROOT → redirect ke kursus
    #path('', lambda request: redirect('daftar_kursus')),
    #path('ping/', lambda request: HttpResponse("OK")),

    # =====================
    # HOME
    # =====================
    #path('kursus/', views.daftar_kursus, name='daftar_kursus'),

    #path('', views.daftar_kursus, name='daftar_kursus'),
    #path('kursus/', views.daftar_kursus, name='daftar_kursus_alt'),

    # =====================
    # DEBUG (optional)
    # =====================
    path('debug/<slug:kursus_slug>/', views.daftar_materi, name='debug_daftar_materi'),

    path('debug/<slug:kursus_slug>/<slug:materi_slug>/',
         views.daftar_materi, name='debug_materi_detail'),

    path('debug/<slug:kursus_slug>/<slug:materi_slug>/halaman/<slug:halaman_slug>/',
         views.halaman_detail_slug, name='debug_halaman_detail'),

    # =====================
    # MAIN ROUTES
    # =====================

    path('kursus/<slug:kursus_slug>/<slug:materi_slug>/halaman/<slug:halaman_slug>/',
         views.halaman_detail_slug,
         name='halaman_detail'),

    path('kursus/<slug:kursus_slug>/<slug:materi_slug>/',
         views.daftar_halaman,
         name='materi_detail'),

    path('kursus/<slug:kursus_slug>/enroll/',
         views.enroll_kursus,
         name='enroll_kursus'),

    path('kursus/<slug:kursus_slug>/',
         views.daftar_materi,
         name='daftar_materi'),

    # Progress
    path('halaman/<int:halaman_id>/selesai/',
         views.tandai_halaman_selesai,
         name='tandai_halaman_selesai'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # API
    path('api/chatbot/', views.chatbot, name='chatbot'),

    path('api/konten-halaman/<slug:kursus_slug>/<slug:materi_slug>/<slug:halaman_slug>/',
         views.api_konten_halaman,
         name='api_konten_halaman'),

    # Auth
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),

    # Sertifikat
    path('sertifikat/<slug:slug>/',
         views.download_sertifikat,
         name='download_sertifikat'),

    # =====================
    # KUIS
    # =====================
    path('kuis/<slug:kursus_slug>/<slug:materi_slug>/mulai/', views.mulai_kuis, name='mulai_kuis'),
    path('kuis/<slug:kursus_slug>/mulai/', views.mulai_kuis, name='mulai_kuis_final'),
    path('kuis/kerjakan/<int:sesi_id>/', views.kerjakan_kuis, name='kerjakan_kuis'),
    path('kuis/selesai/<int:sesi_id>/', views.selesai_kuis, name='selesai_kuis'),
    path('kuis/hasil/<int:sesi_id>/', views.hasil_kuis, name='hasil_kuis'),
]