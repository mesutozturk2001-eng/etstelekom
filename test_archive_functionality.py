import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IK_Takip.settings')
django.setup()

from core.models import Personel, User
from core.views import personel_arsivle, personel_aktiflestir
from django.test import RequestFactory
from django.contrib.auth.models import Permission
from datetime import datetime

print("=== Archive Functionality Test ===")

# Create a test user and personel
test_user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@ets-telekom.com.tr'
    }
)
if created:
    test_user.set_password('testpass123')
    test_user.save()

test_personel, created = Personel.objects.get_or_create(
    user=test_user,
    defaults={
        'tc_no': '12345678901',
        'telefon': '5551234567',
        'ise_giris_tarihi': datetime.now().date(),
        'aktif': True
    }
)

print(f"Test personel created/retrieved: {test_personel}")
print(f"Current active status: {test_personel.aktif}")

# Test archiving the personel
print("\n--- Testing Archive Functionality ---")
factory = RequestFactory()

# Create a mock request
request = factory.post(f'/personel-arsivle/{test_personel.id}/', {
    'arsivlenme_nedeni': 'Deneme amaçlı arşivleme'
})
request.user = User.objects.get(username='admin')

from core.views import personel_arsivle
try:
    response = personel_arsivle(request, test_personel.id)
    print(f"Archive response status: {response.status_code}")
    
    # Refresh from DB
    test_personel.refresh_from_db()
    print(f"After archive active status: {test_personel.aktif}")
    print(f"Archive reason: {test_personel.arsivlenme_nedeni}")
    print(f"Archive date: {test_personel.arsivlenme_tarihi}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    print(traceback.format_exc())

# Test restoring from archive
print("\n--- Testing Restore Functionality ---")
request = factory.get(f'/personel-aktiflestir/{test_personel.id}/')
request.user = User.objects.get(username='admin')

from core.views import personel_aktiflestir
try:
    response = personel_aktiflestir(request, test_personel.id)
    print(f"Restore response status: {response.status_code}")
    
    # Refresh from DB
    test_personel.refresh_from_db()
    print(f"After restore active status: {test_personel.aktif}")
    print(f"Archive reason after restore: {test_personel.arsivlenme_nedeni}")
    print(f"Archive date after restore: {test_personel.arsivlenme_tarihi}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    print(traceback.format_exc())

# Verify active personel list
print("\n--- Active Personel List ---")
active_personel = Personel.objects.filter(aktif=True)
print(f"Active personel count: {active_personel.count()}")
for p in active_personel:
    print(f"- {p.user.get_full_name()}")

# Verify archived personel list
print("\n--- Archived Personel List ---")
archived_personel = Personel.objects.filter(aktif=False)
print(f"Archived personel count: {archived_personel.count()}")
for p in archived_personel:
    print(f"- {p.user.get_full_name()}")

print("\n=== Test completed successfully ===")