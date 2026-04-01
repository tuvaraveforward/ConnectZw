from django import forms
from Admin.models import Feedback
from Client.models import Client
from .models import ServiceRequest


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['service_provider', 'amount', 'beneficiaries', 'provider_contact']
        widgets = {
            'service_provider': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service provider name'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'beneficiaries': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated beneficiary names'}),
            'provider_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone or email'}),
        }

class ClientFeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['location', 'feedback_type', 'subject', 'message']
        widgets = {
            'location': forms.Select(attrs={'class': 'form-control'}),
            'feedback_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your complaint or feedback', 'rows': 5}),
        }