def user_profile(request):
    """
    Context processor to add user profile information to all templates.
    Priority:
    1. Staff users (admin) -> 'Patron'
    2. Users with personel profile -> use their profil_tipi
    """
    profile_tipi = None
    if request.user.is_authenticated:
        # Staff users (admin) get Patron profile for full access
        if request.user.is_staff:
            profile_tipi = 'Patron'
        # Check if user has personel profile
        elif hasattr(request.user, 'personel'):
            profile_tipi = request.user.personel.profil_tipi
    
    return {
        'profil_tipi': profile_tipi,
    }
