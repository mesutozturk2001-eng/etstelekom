import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IK_Takip.settings')
django.setup()

from core.models import Personel, User
from datetime import date

# Create manager user
if not User.objects.filter(username='manager1').exists():
    manager_user = User.objects.create_user(
        username='manager1',
        password='manager123',
        first_name='Ahmet',
        last_name='Yönetici',
        email='ahmet.yonetici@ets-telekom.com.tr'
    )
    
    manager_personel = Personel.objects.create(
        user=manager_user,
        tc_no='12345678900',
        telefon='5551234560',
        ise_giris_tarihi=date(2020, 1, 1),
        profil_tipi='Muhasebe',
        pozisyon='Yönetici'
    )
    
    print('Yönetici oluşturuldu:', manager_personel.user.get_full_name())

# Create 5 employees
for i in range(1, 6):
    emp_username = f'employee{i}'
    if not User.objects.filter(username=emp_username).exists():
        user = User.objects.create_user(
            username=emp_username,
            password=f'employee{i}123',
            first_name=f'Çalışan{i}',
            last_name=f'Soyisim{i}',
            email=f'calisan{i}@ets-telekom.com.tr'
        )
        
        personel = Personel.objects.create(
            user=user,
            tc_no=f'987654321{i:02}',
            telefon=f'555{i}123456',
            ise_giris_tarihi=date(2021, 1, 1),
            profil_tipi='Personel',
            pozisyon='Çalışan',
            yonetici=Personel.objects.get(user__username='manager1')
        )
        
        print(f'Çalışan{i} oluşturuldu: {personel.user.get_full_name()}')

print('\nTest verileri başarıyla oluşturuldu!')