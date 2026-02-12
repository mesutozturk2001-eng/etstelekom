import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IK_Takip.settings')
django.setup()

from core.models import Personel

print("Manager-employee relationships:")
print("-" * 80)
for p in Personel.objects.all():
    manager = p.yonetici.user.get_full_name() if p.yonetici else "None"
    print(f"{p.user.get_full_name()} ({p.profil_tipi}) -> {manager}")
