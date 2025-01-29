import random
import string

from django.contrib.auth.hashers import make_password

from ..models import User, UserRole

PASSWORD = "password"

def create_test_user():
    return User.objects.create_user(
        name="test_user",
        email=generate_random_email(),
        password=PASSWORD,
    )

def create_test_subject():
    return User.objects.create_user(
        name="test_subject",
        email=generate_random_email(),
        password=PASSWORD,
        user_role=UserRole.SUBJECT
    )

def create_test_user_or_subject_details():
    return {
        "name": "test_user",
        "email": generate_random_email(),
        "password": PASSWORD
    }


def generate_random_email():
    domain = 'bodastage.com'   
    username_length = random.randint(6, 12)
    
    # Create username using letters, numbers, and some special characters
    chars = string.ascii_lowercase + string.digits + '._-'
    username = ''.join(random.choice(chars) for _ in range(username_length))
    
    # Make sure username doesn't start or end with a special character
    while username[0] in '._-' or username[-1] in '._-':
        username = ''.join(random.choice(chars) for _ in range(username_length))
    
    return f"{username}@{domain}"
