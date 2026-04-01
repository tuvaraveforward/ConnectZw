from django import forms
from Admin.models import Transaction, Product
from Client.models import Client
from Location.models import Location

class DealerReportForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False, empty_label="All Clients")
    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=False, empty_label="All Locations")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    email = forms.EmailField(required=True, help_text="Email address to send the report to")

    def __init__(self, *args, category=None, **kwargs):
        super().__init__(*args, **kwargs)
        # If a category is provided, limit locations to that category and active ones
        if category:
            self.fields['location'].queryset = Location.objects.filter(category=category, is_active=True)
        else:
            # Default to active locations only
            self.fields['location'].queryset = Location.objects.filter(is_active=True)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
