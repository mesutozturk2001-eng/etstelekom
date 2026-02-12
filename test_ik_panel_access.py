import requests
from bs4 import BeautifulSoup

# URL for login and IK Panel
login_url = 'http://localhost:8000/login/'
ik_panel_url = 'http://localhost:8000/ik-paneli/'

# Login credentials
payload = {
    'username': '12345678901',
    'password': 'admin123'
}

# Start a session to persist cookies
with requests.Session() as session:
    # Get login page first to obtain CSRF token
    login_page = session.get(login_url)
    print(f"Login page status: {login_page.status_code}")
    
    # Extract CSRF token from response cookies
    csrf_token = session.cookies.get('csrftoken')
    print(f"CSRF Token: {csrf_token}")
    
    # Login with credentials and CSRF token
    headers = {
        'Referer': login_url,
        'X-CSRFToken': csrf_token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    login_response = session.post(login_url, data=payload, headers=headers, allow_redirects=True)
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response URL: {login_response.url}")
    
    # Check if login was successful (redirect to index or IK panel)
    if login_response.url == ik_panel_url or login_response.url == 'http://localhost:8000/':
        print("Login successful")
        
        # Access IK Panel
        ik_response = session.get(ik_panel_url)
        print(f"IK Panel status: {ik_response.status_code}")
        
        # Parse IK Panel content
        soup = BeautifulSoup(ik_response.content, 'html.parser')
        
        # Check if Yönetici column exists
        manager_column = soup.find('th', string='Yönetici')
        if manager_column:
            print("OK: Yönetici column found in IK Panel")
            
            # Check if any employee has a manager
            manager_cells = soup.find_all('td')
            manager_found = False
            for cell in manager_cells:
                if cell.text.strip() and cell.text.strip() != '-' and cell.text.strip() != 'Yönetici':
                    manager_found = True
                    break
            
            if manager_found:
                print("OK: Manager information found for some employees")
            else:
                print("WARNING: No manager information found for employees")
                
            # Print a portion of the IK Panel content
            print("\nIK Panel content preview:")
            print(soup.find('table', class_='table').prettify()[:500])
            
        else:
            print("ERROR: Yönetici column not found in IK Panel")
            
    else:
        print("Login failed")
        print(f"Response: {login_response.text[:300]}")
