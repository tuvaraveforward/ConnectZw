from django import forms
from Admin.models import Transaction, Feedback
from Client.models import Client
from .models import User
from Pos.models import Pos

class LocationReportForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False, empty_label="All Clients")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    email = forms.EmailField(required=True, help_text="Email address to send the report to")

class LocationFeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'subject', 'message']
        widgets = {
            'feedback_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your complaint or feedback', 'rows': 5}),
        }

class LocationUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'username', 'password', 'phone_number', 'email_address', 'role']
        widgets = {
            'firstname': forms.TextInput(attrs={'class': 'form-control'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email_address': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(choices=[('cashier', 'Cashier'), ('manager', 'Manager')], attrs={'class': 'form-control'}),
        }

class LocationPosForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.none(), required=True, label="Assign Staff")

    def __init__(self, *args, **kwargs):
        location = kwargs.pop('location', None)
        super(LocationPosForm, self).__init__(*args, **kwargs)
        if location:
            self.fields['user'].queryset = User.objects.filter(location=location)
        self.fields['user'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Pos
        fields = ['pos_name', 'user']
        widgets = {
            'pos_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter POS Name (e.g. Counter 1)'}),
        }
