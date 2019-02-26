from django.contrib.auth.models import User

def generate_password():
    random_password = User.objects.make_random_password(allowed_chars='abcdefghjkmnpqrstuvwxyz'
        'ABCDEFGHJKLMNPQRSTUVWXYZ'
        '23456789!@#$%&')
    
    return random_password