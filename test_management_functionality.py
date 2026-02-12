import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IK_Takip.settings')
django.setup()

from core.models import Personel, User, AvansTalebi, IzinTalebi
from core.views import avans_islem, izin_islem
from django.test import RequestFactory
from datetime import date

print("=== Yönetici-Personel Yönetim Fonksiyonları Testi ===")

# Test verilerini sorgula
print("\n--- Test Verileri ---")
yonetici = Personel.objects.get(user__username='manager1')
print(f"Yönetici: {yonetici.user.get_full_name()}")

personeller = Personel.objects.filter(yonetici=yonetici)
print(f"Yöneticiye bağlı personel sayısı: {personeller.count()}")

for p in personeller:
    print(f"  - {p.user.get_full_name()}")

# Yönetici kullanıcısını al
yonetici_user = User.objects.get(username='manager1')
factory = RequestFactory()

# Test 1: Avans talebi oluştur ve yönetici onayı ver
print("\n--- Test 1: Yönetici Avans Onayı ---")
try:
    # İlk personel için avans talebi oluştur
    test_personel = personeller.first()
    avans_talebi = AvansTalebi.objects.create(
        personel=test_personel,
        miktar=500,
        tarih=date.today(),
        aciklama="Yol masrafı için avans talebi",
        durum="Bekliyor"
    )
    
    print(f"Oluşturulan avans talebi: {avans_talebi}")
    
    # Yönetici onayı işlemi
    request = factory.get(f'/avans-islem/{avans_talebi.id}/onayla')
    request.user = yonetici_user
    
    response = avans_islem(request, avans_talebi.id, 'onayla')
    print(f"Onay işlem sonucu: {response.status_code}")
    
    avans_talebi.refresh_from_db()
    print(f"Talebin yeni durumu: {avans_talebi.durum}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    print(traceback.format_exc())

# Test 2: İzin talebi oluştur ve yönetici onayı ver
print("\n--- Test 2: Yönetici İzin Onayı ---")
try:
    # İlk personel için izin talebi oluştur
    test_personel = personeller.last()
    izin_talebi = IzinTalebi.objects.create(
        personel=test_personel,
        baslangic_tarihi=date.today(),
        bitis_tarihi=date.today(),
        gun_sayisi=1,
        aciklama="Aile hastalığı için izin talebi",
        durum="Bekliyor"
    )
    
    print(f"Oluşturulan izin talebi: {izin_talebi}")
    
    # Yönetici onayı işlemi
    request = factory.get(f'/izin-islem/{izin_talebi.id}/onayla')
    request.user = yonetici_user
    
    response = izin_islem(request, izin_talebi.id, 'onayla')
    print(f"Onay işlem sonucu: {response.status_code}")
    
    izin_talebi.refresh_from_db()
    print(f"Talebin yeni durumu: {izin_talebi.durum}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    print(traceback.format_exc())

# Test 3: Yetki kontrolü - Yönetici sadece kendi personellerini onaylayabilir
print("\n--- Test 3: Yetki Kontrolü ---")
try:
    # Diğer bir yönetici (varsa) veya farklı bir personel
    if Personel.objects.count() > len(personeller) + 1:
        other_personel = Personel.objects.exclude(yonetici=yonetici).exclude(id=yonetici.id).first()
        if other_personel:
            # Bu personel için avans talebi oluştur
            avans_talebi = AvansTalebi.objects.create(
                personel=other_personel,
                miktar=300,
                tarih=date.today(),
                aciklama="Test için avans talebi",
                durum="Bekliyor"
            )
            
            print(f"Farklı bir personel için oluşturulan avans talebi: {avans_talebi}")
            
            # Yönetici onayı işlemi dene
            request = factory.get(f'/avans-islem/{avans_talebi.id}/onayla')
            request.user = yonetici_user
            
            response = avans_islem(request, avans_talebi.id, 'onayla')
            print(f"Yetkisiz erişim sonucu: {response.status_code}")
            print(f"Yönlendirme: {response.url}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    print(traceback.format_exc())

# Temizlik (opsiyonel)
print("\n--- Temizlik ---")
try:
    for talep in AvansTalebi.objects.all():
        if 'Test' in talep.aciklama or 'test' in talep.aciklama or 'Yol masrafı' in talep.aciklama:
            talep.delete()
    
    for talep in IzinTalebi.objects.all():
        if 'Test' in talep.aciklama or 'test' in talep.aciklama or 'Aile hastalığı' in talep.aciklama:
            talep.delete()
    
    print("Test talepleri silindi")
except Exception as e:
    print(f"Silme hatası: {e}")

print("\n=== Test tamamlandı ===")