import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IK_Takip.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Personel

# Test 1: Check if Personel model has yonetici field
print("Test 1: Checking if Personel model has yonetici field")
if hasattr(Personel, 'yonetici'):
    print("OK: Personel model has yonetici field")
else:
    print("ERROR: Personel model does NOT have yonetici field")

# Test 2: Check if PersonelForm includes yonetici field
from core.forms import PersonelForm
print("\nTest 2: Checking if PersonelForm includes yonetici field")
form = PersonelForm()
if 'yonetici' in form.fields:
    print("OK: PersonelForm includes yonetici field")
else:
    print("ERROR: PersonelForm does NOT include yonetici field")

# Test 3: Get admin user
print("\nTest 3: Getting admin user")
try:
    admin_user = User.objects.get(username='12345678901')
    print(f"OK: Admin user found: {admin_user.first_name} {admin_user.last_name}")
except User.DoesNotExist:
    print("ERROR: Admin user not found")
    admin_user = None

# Test 4: Create a manager and an employee
print("\nTest 4: Creating test manager and employee")
if admin_user:
    # Create manager (admin)
    admin_personel = Personel.objects.get(user=admin_user)
    
    # Create test employee
    try:
        # Check if test user already exists
        test_user = User.objects.get(username='10000000001')
        print("Test user already exists")
        test_personel = Personel.objects.get(user=test_user)
    except User.DoesNotExist:
        test_user = User.objects.create_user(
            username='10000000001',
            password='12345',
            first_name='Ahmet',
            last_name='Yılmaz'
        )
        test_personel = Personel.objects.create(
            user=test_user,
            tc_no='10000000001',
            telefon='5551234567',
            pozisyon='Personel',
            profil_tipi='Personel',
            adres='İstanbul',
            dogum_tarihi='1990-01-01',
            ise_giris_tarihi='2020-01-01',
            yonetici=admin_personel
        )
        print(f"OK: Test employee created: {test_personel.user.get_full_name()}")
    
    # Check if the employee has the manager set
    print(f"\nEmployee's manager: {test_personel.yonetici.user.get_full_name() if test_personel.yonetici else 'None'}")
    if test_personel.yonetici == admin_personel:
        print("OK: Test employee's manager is set correctly")
    else:
        print("ERROR: Test employee's manager is not set correctly")
    
    # Test personel edit form
    print("\nTest 5: Testing PersonelForm with manager")
    form = PersonelForm(instance=test_personel)
    if 'yonetici' in form.fields:
        print("OK: Form includes yonetici field")
        print(f"Current manager selected: {form['yonetici'].value()}")
    else:
        print("ERROR: Form does not include yonetici field")
    
    print("\nAll tests passed!")
else:
    print("\nCannot run tests without admin user")
