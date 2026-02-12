import requests

# Django login endpoint
url = 'http://localhost:8000/login/'

# Login credentials
credentials = {
    'username': '12345678901',
    'password': 'admin123'
}

# Session to persist cookies
session = requests.Session()

try:
    # Get the login page first to retrieve CSRF token
    response = session.get(url)
    print(f"Login page status code: {response.status_code}")
    
    # Check if we need to extract CSRF token from cookies
    if 'csrftoken' in session.cookies:
        csrf_token = session.cookies['csrftoken']
        print(f"CSRF Token: {csrf_token}")
    else:
        print("No CSRF token found in cookies")
    
    # Try to login with credentials and CSRF token
    headers = {'Referer': url, 'X-CSRFToken': csrf_token}
    login_response = session.post(url, data=credentials, headers=headers)
    
    print(f"Login attempt status code: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("Login failed")
        print(f"Response: {login_response.text[:200]}")
    elif login_response.status_code == 302:
        print("Login successful, redirected to: " + login_response.headers.get('Location'))
    else:
        print("Unexpected response status: " + str(login_response.status_code))
        
    # Try to access IK panel
    ik_response = session.get('http://localhost:8000/ik-paneli/')
    print(f"\nIK Panel status code: {ik_response.status_code}")
    print(ik_response.text[:300])
        
except Exception as e:
    print(f"Error: {e}")
