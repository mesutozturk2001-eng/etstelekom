import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IK_Takip.settings')
django.setup()

from django.contrib.auth import authenticate
from core.models import Personel

username = '12345678901'
password = 'admin123'

user = authenticate(username=username, password=password)

if user:
    print('User authenticated successfully')
    try:
        personel = Personel.objects.get(user=user)
        print(f'Profil Tipi: {personel.profil_tipi}')
        print(f'Aktif: {personel.aktif}')
    except Personel.DoesNotExist:
        print('User does not have a Personel record')
else:
    print('Authentication failed')
