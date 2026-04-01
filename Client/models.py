from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import make_password
import uuid
from django.utils import timezone

class Client(models.Model):
    username = models.CharField(max_length=150, unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email_address = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50, default='client')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.username})"

    def save(self, *args, **kwargs):
        # Hash password if it's not already hashed
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class Basket(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='basket')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Basket for {self.client.username}"

    def get_total(self):
        return sum(item.get_cost() for item in self.items.all())

class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Admin.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_cost(self):
        return self.product.price * self.quantity
class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
    ]

    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='feedbacks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.feedback_type} - {self.subject} by {self.client.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Feedbacks' 


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='service_requests')
    product = models.ForeignKey('Admin.Product', on_delete=models.SET_NULL, null=True, blank=True)
    service_provider = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    beneficiaries = models.TextField()
    provider_contact = models.CharField(max_length=100, blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def mark_confirmed(self):
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"ServiceRequest {self.id} - {self.service_provider} - {self.client.username} - {self.status}"