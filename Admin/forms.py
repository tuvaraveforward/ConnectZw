from django import forms
from .models import Admin, Transaction
from Location.models import Location, User
from Dealer.models import Dealer
from Pos.models import Pos
from Client.models import Client
from django.contrib.auth.hashers import make_password

class AdminSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Admin
        fields = ['username', 'firstname', 'lastname', 'email_address', 'phone_number']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class LocationRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        initial='Zimconnect',
        help_text='Default password is set to Zimconnect'
    )
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Location
        fields = ['location_name', 'email_address', 'username', 'city', 'province', 'category', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        # Check if username already exists
        username = cleaned_data.get('username')
        if Location.objects.filter(username=username).exists():
            raise forms.ValidationError("A location with this username already exists")

        # Check if email already exists
        email = cleaned_data.get('email_address')
        if Location.objects.filter(email_address=email).exists():
            raise forms.ValidationError("A location with this email already exists")

        return cleaned_data

    def save(self, commit=True):
        location = super().save(commit=False)
        location.password = make_password(self.cleaned_data['password'])
        if commit:
            location.save()
        return location

class UserRegistrationForm(forms.Form):
    # User fields
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}))
    firstname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}))
    lastname = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}))
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}))
    email_address = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}))

    # Hidden fields for defaults
    role = forms.CharField(widget=forms.HiddenInput(), initial='user', required=False)
    password = forms.CharField(widget=forms.HiddenInput(), initial='Zimconnect', required=False)

    class Meta:
        fields = ['username', 'firstname', 'lastname', 'phone_number', 'email_address']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists")
        return username

    def clean_email_address(self):
        email = self.cleaned_data['email_address']
        if User.objects.filter(email_address=email).exists():
            raise forms.ValidationError("A dealer with this email already exists")
        return email

    def save(self):
        # Create dealer
        user = User.objects.create(
            username=self.cleaned_data['username'],
            firstname=self.cleaned_data['firstname'],
            lastname=self.cleaned_data['lastname'],
            phone_number=self.cleaned_data['phone_number'],
            email_address=self.cleaned_data['email_address'],
            password=self.cleaned_data['password'],  # Will be hashed by the model's save method
            role=self.cleaned_data['role']
        )

        return user

class PosRegistrationForm(forms.ModelForm):
    class Meta:
        model = Pos
        fields = ['pos_name', 'location', 'user', 'is_active']
        widgets = {
            'pos_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter POS name'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ClientEditForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['username', 'firstname', 'lastname', 'phone_number', 'email_address', 'is_active']

class DealerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, initial='Zimconnect', help_text='Default password is set to Zimconnect')

    class Meta:
        model = Dealer
        fields = ['username', 'firstname', 'lastname', 'phone_number', 'email_address', 'category']

    def clean_username(self):
        username = self.cleaned_data['username']
        if Dealer.objects.filter(username=username).exists():
            raise forms.ValidationError("A dealer with this username already exists")
        return username

    def clean_email_address(self):
        email = self.cleaned_data['email_address']
        if Dealer.objects.filter(email_address=email).exists():
            raise forms.ValidationError("A dealer with this email already exists")
        return email

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'client', 'dealer', 'location', 'pos', 'category', 'description']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'dealer': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'pos': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ClientSignupForm(forms.ModelForm):
    username = forms.CharField(
        label='Account Name',
        widget=forms.TextInput(attrs={'placeholder': 'Enter Account Name'})
    )
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = Client
        fields = ['username', 'firstname', 'lastname', 'email_address', 'phone_number']
        labels = {
            'firstname': 'First Name',
            'lastname': 'Last Name',
            'email_address': 'Email Address',
            'phone_number': 'Phone Number',
        }
        widgets = {
            'firstname': forms.TextInput(attrs={'placeholder': 'Enter First Name'}),
            'lastname': forms.TextInput(attrs={'placeholder': 'Enter Last Name'}),
            'email_address': forms.EmailInput(attrs={'placeholder': 'Enter Email Address'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter Phone Number'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class ReportForm(forms.Form):
    dealer = forms.ModelChoiceField(queryset=Dealer.objects.all(), required=False, empty_label="All Dealers")
    client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False, empty_label="All Clients")
    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=False, empty_label="All Locations")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    email = forms.EmailField(required=True, help_text="Email address to send the report to")
