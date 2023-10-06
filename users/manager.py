from django.contrib.auth.models import BaseUserManager
from django.db.models import Q  

class CustomManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Can not go further without set email")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be  True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must  is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, username):
        return self.get(Q(email__iexact=username) | Q(phone_number__iexact=username))

    def get_user_by_email_or_phone(self, identifier):
        return self.get(Q(email__iexact=identifier) | Q(phone_number__iexact=identifier))
