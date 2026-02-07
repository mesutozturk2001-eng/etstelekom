import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IK_Takip.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Personel

def create_data():
    # Admin
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Admin kullanıcısı oluşturuldu: admin / admin123")
    else:
        print("Admin kullanıcısı zaten var.")

    # Personel
    if not User.objects.filter(username='ali').exists():
        u = User.objects.create_user('ali', 'ali@example.com', 'ali123')
        u.first_name = "Ali"
        u.last_name = "Yılmaz"
        u.save()
        
        Personel.objects.create(
            user=u,
            tc_no="11111111111",
            telefon="05551234567",
            ise_giris_tarihi=date(2023, 1, 1),
            kalan_izin=14,
            guncel_avans_borcu=0
        )
        print("Test personeli oluşturuldu: ali / ali123")
    else:
        print("Personel kullanıcısı zaten var.")

if __name__ == '__main__':
    create_data()
