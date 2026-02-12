from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('ik-paneli/', views.ik_paneli, name='ik_paneli'),
    path('muhasebe-paneli/', views.muhasebe_paneli, name='muhasebe_paneli'),
    path('personel-detay/<int:personel_id>/', views.personel_detay, name='personel_detay'),
    path('personel/', views.personel_panel, name='personel_panel'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('borc-guncelle/<int:personel_id>/', views.borc_guncelle, name='borc_guncelle'),
    path('avans-islem/<int:talep_id>/<str:islem>/', views.avans_islem, name='avans_islem'),
    path('personel-ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel-duzenle/<int:personel_id>/', views.personel_duzenle, name='personel_duzenle'),
    path('personel-arsivle/<int:personel_id>/', views.personel_arsivle, name='personel_arsivle'),
    path('personel-aktiflestir/<int:personel_id>/', views.personel_aktiflestir, name='personel_aktiflestir'),
    path('arsivli-personeller/', views.arsivli_personeller, name='arsivli_personeller'),
    path('personel-yukle/', views.personel_yukle, name='personel_yukle'),
    path('sablon-indir/', views.download_excel_template, name='download_excel_template'),
    path('toplu-excel-indir/', views.toplu_excel_indir, name='toplu_excel_indir'),
    path('sifre-degistir/', views.sifre_degistir, name='sifre_degistir'),
    path('sifre-resetle/<int:personel_id>/', views.sifre_resetle, name='sifre_resetle'),
    # Izin Talepleri
    path('izin-talep/', views.izin_talep_et, name='izin_talep_et'),
    path('izin-listesi/', views.izin_listesi, name='izin_listesi'),
    path('izin-detay/<int:talep_id>/', views.izin_detay, name='izin_detay'),
    path('izin-islem/<int:talep_id>/<str:islem>/', views.izin_islem, name='izin_islem'),
    path('hesapla-gun/', views.hesapla_gun, name='hesapla_gun'),
    path('zimmetlerim/', views.zimmetlerim, name='zimmetlerim'),
    path('egitimlerim/', views.egitimlerim, name='egitimlerim'),
    # Masraf Talepleri
    path('masraf-talep/', views.masraf_talep_et, name='masraf_talep_et'),
    path('masraf-listem/', views.masraf_listem, name='masraf_listem'),
    path('masraf-listesi/', views.masraf_listesi, name='masraf_yonetim'),
    path('masraf-detay/<int:talep_id>/', views.masraf_detay, name='masraf_detay'),
    path('masraf-islem/<int:talep_id>/<str:islem>/', views.masraf_islem, name='masraf_islem'),
    # Taleplerim (Personel)
    path('taleplerim/', views.taleplerim, name='taleplerim'),
    path('taleplerim/avans/', views.avans_taleplerim, name='avans_taleplerim'),
    path('taleplerim/izin/', views.izin_taleplerim, name='izin_taleplerim'),
    path('taleplerim/masraf/', views.masraf_taleplerim, name='masraf_taleplerim'),
    # Talep Yönetim (Admin/Muhasebe/Patron)
    path('talep-yonetim/', views.talep_yonetim, name='talep_yonetim'),
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Zimmet ve Egitim Yönetimi
    path('zimmet-yonetim/', views.zimmet_yonetim_home, name='zimmet_yonetim_home'),
    path('zimmet-yonetimi/<int:personel_id>/', views.zimmet_yonetimi, name='zimmet_yonetimi'),
    path('zimmet-sil/<int:zimmet_id>/', views.zimmet_sil, name='zimmet_sil'),
    path('egitim-yonetim/', views.egitim_yonetim_home, name='egitim_yonetim_home'),
    path('egitim-yonetimi/<int:personel_id>/', views.egitim_yonetimi, name='egitim_yonetimi'),
    path('egitim-sil/<int:egitim_id>/', views.egitim_sil, name='egitim_sil'),
]
