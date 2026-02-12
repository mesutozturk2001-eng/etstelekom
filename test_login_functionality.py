import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IK_Takip.settings')
django.setup()

from django.contrib.auth import authenticate
from core.models import Personel, User

# Test admin login
username = '12345678901'
password = 'admin123'

user = authenticate(username=username, password=password)

if user is not None:
    print(f"Login successful: {user.get_full_name()}")
    
    # Get personel information
    try:
        personel = Personel.objects.get(user=user)
        print(f"Profil Tipi: {personel.profil_tipi}")
        print(f"Aktif: {personel.aktif}")
        
        # Check if user can access IK panel
        from core.views import ik_paneli
        from django.http import HttpRequest
        
        # Create a mock request
        request = HttpRequest()
        request.user = user
        
        # Try to access ik_paneli view
        try:
            response = ik_paneli(request)
            print(f"IK Panel access: Success (status code {response.status_code})")
        except Exception as e:
            print(f"IK Panel access: Failed - {e}")
            
    except Personel.DoesNotExist:
        print("User does not have a Personel record")
        
else:
    print("Login failed")
