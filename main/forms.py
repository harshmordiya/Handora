from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.views.decorators.debug import sensitive_variables

from .models import Product


class RegisterForm(UserCreationForm):

    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'First name'
        })
    )

    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Last name'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@example.com'
        })
    )

    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '10-digit mobile number'
        })
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]
        widgets = {
            'username': forms.TextInput(
                attrs={'placeholder': 'Username'}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Email already exists! Please use another email.'
            )

        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone:
            raise forms.ValidationError(
                'Phone number is required.'
            )

        if not phone.isdigit():
            raise forms.ValidationError(
                'Phone number must contain only digits.'
            )

        if len(phone) != 10:
            raise forms.ValidationError(
                'Invalid phone number! It should be 10 digits.'
            )

        return phone

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username and User.objects.filter(
            username=username
        ).exists():
            raise forms.ValidationError(
                'Username already taken! Please choose another one.'
            )

        return username

    @sensitive_variables("password")
    def validate_password_for_user(
        self,
        user,
        password_field_name="password2"
    ):
        password = self.cleaned_data.get(password_field_name)

        if password:
            try:
                validators = [
                    v for v in password_validation.get_default_password_validators()
                    if not isinstance(
                        v,
                        password_validation.UserAttributeSimilarityValidator
                    )
                ]

                password_validation.validate_password(
                    password,
                    user,
                    validators
                )

            except ValidationError as error:
                self.add_error(
                    password_field_name,
                    error
                )


# =========================================================
# PRODUCT FORM
# =========================================================

class ProductForm(forms.ModelForm):

    rating = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=5,
        max_digits=2,
        decimal_places=1,
        widget=forms.NumberInput(attrs={
            'step': '0.1',
            'min': '0',
            'max': '5',
            'placeholder': '0.0'
        })
    )

    discount_percent = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=100,
        max_digits=5,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '100',
            'placeholder': '0'
        })
    )

    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'slug',
            'description',
            'price',
            'image',
            'is_featured',
            'is_bestseller',
            'is_available',
            'discount_percent',
            'rating',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Discount is optional on Add and Edit Product.
        # If no discount is entered, use 0.
        self.fields['discount_percent'].required = False

        if not self.is_bound:
            if not self.instance or not self.instance.pk:
                self.fields['discount_percent'].initial = 0

        # Availability is managed separately.
        self.fields['is_available'].required = False

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')

        if rating is None:
            if self.instance and self.instance.pk:
                return self.instance.rating
            return 0

        if rating < 0 or rating > 5:
            raise forms.ValidationError(
                'Rating must be between 0 and 5.'
            )

        return rating

    def clean_discount_percent(self):
        discount = self.cleaned_data.get('discount_percent')

        if discount is None:
            if self.instance and self.instance.pk:
                return self.instance.discount_percent
            return 0

        if discount < 0 or discount > 100:
            raise forms.ValidationError(
                'Discount percentage must be between 0 and 100.'
            )

        return discount