from django.db import models
from Dealer.models import Dealer
from django.contrib.auth.hashers import make_password

class Location(models.Model):
    location_name = models.CharField(max_length=200)
    email_address = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    user = models.ForeignKey(Dealer, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_locations')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.location_name

    class Meta:
        ordering = ['-created_at']

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email_address = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50, default='user')
    category = models.CharField(max_length=100, blank=True, null=True)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.username})"

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        # Hash password if it's not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('inquiry', 'Inquiry'),
        ('other', 'Other'),
    ]

    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.subject}"

    class Meta:
        ordering = ['-submitted_at']