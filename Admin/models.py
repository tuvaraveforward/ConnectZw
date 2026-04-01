from django.db import models
from Client.models import Client
from Dealer.models import Dealer
from Location.models import Location
from Pos.models import Pos
from django.utils import timezone

class Admin(models.Model):
    username = models.CharField(max_length=150, unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15)
    email_address = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=100)
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.price} - {self.category}"

    class Meta:
        ordering = ['-created_at']

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('purchase', 'Purchase'),
        ('redemption', 'Redemption'),
    ]

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='transactions')
    dealer = models.ForeignKey(Dealer, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    pos = models.ForeignKey(Pos, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    category = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    coupon_code = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    is_redeemed = models.BooleanField(default=False)
    redemption_pos = models.ForeignKey(Pos, on_delete=models.SET_NULL, null=True, blank=True, related_name='redeemed_transactions')
    redemption_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.client.username} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('complaint', 'Complaint'),
        ('feedback', 'Feedback'),
    ]

    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='feedbacks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.feedback_type} - {self.subject} - {self.location.location_name}"

    class Meta:
        ordering = ['-created_at']

class LoginAttempt(models.Model):
    username = models.CharField(max_length=150, unique=True)
    failed_attempts = models.IntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    last_attempt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.failed_attempts} attempts"

