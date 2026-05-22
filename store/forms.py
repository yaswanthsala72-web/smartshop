from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, Review


class RegisterForm(UserCreationForm):
    """Form for user registration with email field."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input', 'placeholder': 'Enter your email', 'id': 'register-email',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Choose a username', 'id': 'register-username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Create a password', 'id': 'register-password1',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Confirm your password', 'id': 'register-password2',
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class CheckoutForm(forms.ModelForm):
    """Form for checkout with shipping and payment details."""
    class Meta:
        model = Order
        fields = ['full_name', 'mobile', 'email', 'address', 'city', 'state', 'pincode']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name', 'id': 'checkout-fullname'}),
            'mobile': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mobile Number', 'id': 'checkout-mobile'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address', 'id': 'checkout-email'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Full Address', 'rows': 3, 'id': 'checkout-address'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City', 'id': 'checkout-city'}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'State', 'id': 'checkout-state'}),
            'pincode': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Pincode', 'id': 'checkout-pincode'}),
        }


class ReviewForm(forms.ModelForm):
    """Form for submitting product reviews."""
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(attrs={'id': 'review-rating', 'value': '5'}),
            'comment': forms.Textarea(attrs={
                'class': 'form-input', 'placeholder': 'Write your review here...', 'rows': 4, 'id': 'review-comment',
            }),
        }
