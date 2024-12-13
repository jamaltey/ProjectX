from django import forms
from accounts.models import User
from core.models import Address
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class SignUpForm(UserCreationForm):
    password1 = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
                'placeholder' : 'Password*',
                'class' : 'form-control',
            }))

    password2 = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
                'placeholder' : 'Confirm password*',
                'class' : 'form-control',
            }))
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone', 'password1', 'password2']

        widgets = {
            'full_name': forms.TextInput(attrs={'id': 'full_name', 'placeholder': 'Your full name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'id': 'email', 'placeholder': 'Your email adress', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'id': 'phone', 'placeholder': 'Your phone number', 'class': 'form-control'}),
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget = forms.TextInput(
            attrs={
                'id': 'email',
                'placeholder' : 'Your email adress',
                'class' : 'form-control',
            }))

    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs={
                'id': 'password',
                'placeholder' : 'Your password',
                'class' : 'form-control',
            }))

    class Meta:
        model = User
        fields = ['username', 'password']

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone']

        widgets = {
            'full_name': forms.TextInput(attrs={'id': 'full_name', 'placeholder': 'Your full name', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'id': 'email', 'placeholder': 'Your email adress', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'id': 'phone', 'placeholder': 'Your phone number', 'class': 'form-control'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address', 'house', 'instructions']

        widgets = {
            'address': forms.TextInput(attrs={'id': 'address', 'placeholder': 'Your address', 'class': 'form-control'}),
            'house': forms.TextInput(attrs={'id': 'house', 'placeholder': 'Your house/apartment number', 'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'id': 'instructions', 'placeholder': 'Additional instructions for delivery', 'class': 'form-control'}),
        }
