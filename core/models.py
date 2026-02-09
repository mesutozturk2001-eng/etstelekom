from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date, timedelta
import math


PROFIL_CHOICES = [
    ('Personel', 'Personel'),
    ('Muhasebe', 'Muhasebe'),
    ('Patron', 'Patron'),
]


def get_profil_tipi(pozisyon):
    """Pozisyona göre profil tipini belirler"""
    if not pozisyon:
        return 'Personel'
    pozisyon_lower = pozisyon.lower().strip()
    if pozisyon_lower == 'muhasebe':
        return 'Muhasebe'
    elif pozisyon_lower == 'patron':
        return 'Patron'
    return 'Personel'


def yas_hesapla(dogum_tarihi):
    """Personelin yaşını hesaplar"""
    if not dogum_tarihi:
        return 0
    bugun = date.today()
    yas = bugun.year - dogum_tarihi.year
    # Doğum günü henüz geçmemişse yaşı bir azalt
    if (bugun.month, bugun.day) < (dogum_tarihi.month, dogum_tarihi.day):
        yas -= 1
    return yas


def yillik_izin_hakki_hesapla(ise_giris_tarihi, dogum_tarihi=None):
    """
    Yıllık izin hakkını hesaplar.
    Kurallar:
    - İşe girişten itibaren 1 yıl: 0 gün
    - 1-6 yıl arası: 14 gün
    - 6-15 yıl arası: 20 gün
    - 16+ yıl: 26 gün
    
    50 yaş üstü için:
    - İlk yıl: 0 gün
    - Sonraki yıllar (16 yıla kadar): 20 gün
    - 16+ yıl: 26 gün
    """
    if not ise_giris_tarihi:
        return 14  # Varsayılan
    
    bugun = date.today()
    yillar = (bugun - ise_giris_tarihi).days // 365
    
    yas = yas_hesapla(dogum_tarihi) if dogum_tarihi else 0
    
    # 50 yaş üstü kontrolü
    if yas >= 50:
        if yillar < 1:
            return 0
        elif yillar < 16:
            return 20
        else:
            return 26
    else:
        if yillar < 1:
            return 0
        elif yillar < 6:
            return 14
        elif yillar < 16:
            return 20
        else:
            return 26


def calisma_gunleri_hesapla(baslangic, bitis):
    """
    İki tarih arasındaki çalışma günlerini hesaplar.
    Pazar günleri hariç tutulur.
    """
    if not baslangic or not bitis:
        return 0
    
    baslangic = date(baslangic.year, baslangic.month, baslangic.day)
    bitis = date(bitis.year, bitis.month, bitis.day)
    
    gun_sayisi = 0
    current = baslangic
    while current <= bitis:
        # Pazar günü (weekday 6) değilse say
        if current.weekday() != 6:
            gun_sayisi += 1
        current += timedelta(days=1)
    
    return gun_sayisi


class Personel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tc_no = models.CharField(max_length=11, unique=True, verbose_name="TC Kimlik No")
    telefon = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon Numarası")
    pozisyon = models.CharField(max_length=100, blank=True, default='', verbose_name="Pozisyon")
    profil_tipi = models.CharField(max_length=20, choices=PROFIL_CHOICES, default='Personel', verbose_name="Profil Tipi")
    adres = models.TextField(blank=True, default='', verbose_name="Adres")
    dogum_tarihi = models.DateField(verbose_name="Doğum Tarihi", null=True, blank=True)
    ise_giris_tarihi = models.DateField(verbose_name="İşe Giriş Tarihi")
    izin_hakki = models.IntegerField(default=14, verbose_name="Yıllık İzin Hakkı")
    kalan_izin = models.IntegerField(default=0, verbose_name="Kalan İzin Günü")
    guncel_avans_borcu = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Güncel Avans Borcu")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.tc_no})"

    def save(self, *args, **kwargs):
        # Pozisyona göre profil tipini otomatik belirle
        if not self.profil_tipi or self.profil_tipi == 'Personel':
            self.profil_tipi = get_profil_tipi(self.pozisyon)
        super().save(*args, **kwargs)

class AvansTalebi(models.Model):
    DURUM_CHOICES = [
        ('Bekliyor', 'Bekliyor'),
        ('Onaylandı', 'Onaylandı'),
        ('Reddedildi', 'Reddedildi'),
    ]
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    miktar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar")
    tarih = models.DateField(verbose_name="Talep Tarihi")
    aciklama = models.TextField(verbose_name="Açıklama")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='Bekliyor', verbose_name="Durum")

    def save(self, *args, **kwargs):
        # Borç güncelleme mantığı
        if self.pk:
            # Güncelleme işlemi
            old_inst = AvansTalebi.objects.get(pk=self.pk)
            if old_inst.durum != 'Onaylandı' and self.durum == 'Onaylandı':
                self.personel.guncel_avans_borcu += self.miktar
                self.personel.save()
            elif old_inst.durum == 'Onaylandı' and self.durum != 'Onaylandı':
                pass
        else:
            # Yeni kayıt
            if self.durum == 'Onaylandı':
                self.personel.guncel_avans_borcu += self.miktar
                self.personel.save()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.personel.user.get_full_name()} - {self.miktar} TL"

class AvansHareketi(models.Model):
    HAREKET_TURU = [
        ('TALEP', 'Avans Talebi'),
        ('ODEME', 'Borç Ödeme'),
        ('GIRIS', 'İşe Giriş Borcu'),
    ]
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    tarih = models.DateTimeField(auto_now_add=True)
    hareket_turu = models.CharField(max_length=20, choices=HAREKET_TURU)
    miktar = models.DecimalField(max_digits=10, decimal_places=2)
    onceki_borc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    yeni_borc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    aciklama = models.TextField(blank=True)

    class Meta:
        ordering = ['-tarih']

    def __str__(self):
        return f"{self.personel.user.get_full_name()} - {self.hareket_turu} - {self.miktar} TL"


class IzinTalebi(models.Model):
    DURUM_CHOICES = [
        ('Bekliyor', 'Bekliyor'),
        ('Onaylandı', 'Onaylandı'),
        ('Reddedildi', 'Reddedildi'),
    ]
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    baslangic_tarihi = models.DateField(verbose_name="Başlangıç Tarihi")
    bitis_tarihi = models.DateField(verbose_name="Bitiş Tarihi")
    gun_sayisi = models.IntegerField(verbose_name="İzin Günü Sayısı")
    aciklama = models.TextField(blank=True, verbose_name="Açıklama")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='Bekliyor', verbose_name="Durum")
    talep_tarihi = models.DateTimeField(auto_now_add=True)
    admin_notu = models.TextField(blank=True, verbose_name="Admin Notu")
    
    def save(self, *args, **kwargs):
        # Otomatik gün sayısı hesapla
        if self.baslangic_tarihi and self.bitis_tarihi and not self.gun_sayisi:
            self.gun_sayisi = calisma_gunleri_hesapla(self.baslangic_tarihi, self.bitis_tarihi)
        
        # İzin onaylandığında kalan izinden düş
        if self.pk:
            old_inst = IzinTalebi.objects.get(pk=self.pk)
            if old_inst.durum != 'Onaylandı' and self.durum == 'Onaylandı':
                self.personel.kalan_izin -= self.gun_sayisi
                self.personel.save()
        else:
            if self.durum == 'Onaylandı':
                self.personel.kalan_izin -= self.gun_sayisi
                self.personel.save()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.personel.user.get_full_name()} - {self.baslangic_tarihi} / {self.bitis_tarihi} ({self.gun_sayisi} gün)"


class MasrafTalebi(models.Model):
    DURUM_CHOICES = [
        ('Bekliyor', 'Bekliyor'),
        ('Onaylandı', 'Onaylandı'),
        ('Reddedildi', 'Reddedildi'),
    ]
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    miktar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Masraf Tutarı (TL)")
    aciklama = models.TextField(verbose_name="Masraf Açıklaması")
    fis_fatura = models.ImageField(upload_to='fis_faturalar/', verbose_name="Fiş/Fatura Resmi", blank=True, null=True)
    tarih = models.DateField(verbose_name="Masraf Tarihi")
    talep_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Talep Tarihi")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='Bekliyor', verbose_name="Durum")
    admin_notu = models.TextField(blank=True, verbose_name="Admin Notu")
    
    def save(self, *args, **kwargs):
        # Masraf onaylandığında avans bakiyesini güncelle
        if self.pk:
            old_inst = MasrafTalebi.objects.get(pk=self.pk)
            if old_inst.durum != 'Onaylandı' and self.durum == 'Onaylandı':
                # Masrafı avans bakiyesinden düş (eksi ise azalt, artı ise artır)
                self.personel.guncel_avans_borcu -= self.miktar
                self.personel.save()
        else:
            if self.durum == 'Onaylandı':
                self.personel.guncel_avans_borcu -= self.miktar
                self.personel.save()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.personel.user.get_full_name()} - {self.miktar} TL ({self.durum})"


class Zimmet(models.Model):
    DURUM_CHOICES = [
        ('Aktif', 'Aktif'),
        ('Iade Edildi', 'Iade Edildi'),
        ('Zarar Gördü', 'Zarar Gördü'),
    ]
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE, related_name='zimmetler')
    malzeme = models.CharField(max_length=200, verbose_name="Malzeme Adı")
    tarih = models.DateField(verbose_name="Zimmet Tarihi")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='Aktif', verbose_name="Durum")
    aciklama = models.TextField(blank=True, verbose_name="Açıklama")

    def __str__(self):
        return f"{self.personel.user.get_full_name()} - {self.malzeme}"


class Egitim(models.Model):
    DURUM_CHOICES = [
        ('Tamamlandı', 'Tamamlandı'),
        ('Devam Ediyor', 'Devam Ediyor'),
        ('Bekliyor', 'Bekliyor'),
    ]
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE, related_name='egitimler')
    egitim_adi = models.CharField(max_length=200, verbose_name="Eğitim Adı")
    tarih = models.DateField(verbose_name="Eğitim Tarihi")
    sure = models.CharField(max_length=50, blank=True, verbose_name="Süre")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='Bekliyor', verbose_name="Durum")
    aciklama = models.TextField(blank=True, verbose_name="Açıklama")

    def __str__(self):
        return f"{self.personel.user.get_full_name()} - {self.egitim_adi}"
