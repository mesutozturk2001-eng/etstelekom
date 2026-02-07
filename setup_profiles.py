import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IK_Takip.settings')

import django
django.setup()

from django.contrib.auth.models import User
from core.models import Personel, get_profil_tipi
from datetime import date

print("="*50)
print("Proje Profil Sistemi Kurulumu")
print("="*50)

# Patron kullanicisi olustur
try:
    user = User.objects.get(username='patron')
    print(f"[OK] Patron kullanicisi zaten mevcut (ID: {user.id})")
except User.DoesNotExist:
    user = User.objects.create_user(
        username='patron',
        password='patron',
        first_name='Patron',
        last_name='Kullanici',
        email='patron@ets.com',
        is_staff=True,
        is_superuser=True
    )
    print(f"[OK] Patron kullanicisi olusturuldu: patron/patron")

# Personel profili olustur
try:
    personel = Personel.objects.get(user=user)
    print(f"[OK] Patron personeli zaten mevcut (Profil: {personel.profil_tipi})")
except Personel.DoesNotExist:
    personel = Personel.objects.create(
        user=user,
        tc_no='99999999999',
        pozisyon='Patron',
        ise_giris_tarihi=date.today(),
        profil_tipi='Patron'
    )
    print(f"[OK] Patron personeli olusturuldu")

print("\n" + "="*50)
print("Mevcut Personeller:")
print("="*50)

# Mevcut personellerin profil tiplerini guncelle
muhasebe_count = 0
for personel in Personel.objects.all():
    if personel.pozisyon and personel.pozisyon.lower() == 'muhasebe':
        personel.profil_tipi = 'Muhasebe'
        personel.save()
        muhasebe_count = muhasebe_count + 1
        print(f"  * {personel.user.username} ({personel.pozisyon}) -> Muhasebe")
    else:
        # Profil tipini pozisyona gore guncelle
        yeni_profil = get_profil_tipi(personel.pozisyon)
        if personel.profil_tipi != yeni_profil:
            personel.profil_tipi = yeni_profil
            personel.save()
        print(f"  * {personel.user.username} ({personel.pozisyon or 'Belirtilmemis'}) -> {yeni_profil}")

print("\n" + "="*50)
print(f"Toplam {muhasebe_count} personele Muhasebe profili atandi")
print("="*50)

# List all users and their profile types
print("\nKullanici Ozeti:")
print("-"*50)
for user in User.objects.all().select_related('personel'):
    if hasattr(user, 'personel'):
        print(f"  {user.username}: {user.personel.profil_tipi}")
    else:
        print(f"  {user.username}: Personel profili yok")
