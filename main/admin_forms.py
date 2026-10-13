from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.text import slugify
from .models import Category, Product, Order, ContactMessage


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['slug'].widget = forms.HiddenInput(
            attrs={'class': 'form-control'}
        )
        self.fields['slug'].required = False

        self.fields['name'].widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Category name'
            }
        )

        self.fields['description'].widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description (optional)'
            }
        )

        self.fields['image'].widget = forms.ClearableFileInput(
            attrs={'class': 'form-control'}
        )

    def save(self, commit=True):
        instance = super().save(commit=False)

        base_slug = slugify(instance.name)
        instance.slug = base_slug

        counter = 1
        while Category.objects.filter(
            slug=instance.slug
        ).exclude(pk=instance.pk).exists():
            instance.slug = f"{base_slug}-{counter}"
            counter += 1

        if commit:
            instance.save()

        return instance


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'slug',
            'description',
            'price',
            'image',
            'is_available',
            'discount_percent',
            'is_featured',
            'is_bestseller',
            'rating'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].widget.attrs.update({
            'class': 'form-control'
        })
        self.fields['category'].empty_label = 'Select a category'

        self.fields['name'].widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Product name'
            }
        )

        self.fields['slug'].widget = forms.HiddenInput(
            attrs={'class': 'form-control'}
        )
        self.fields['slug'].required = False

        self.fields['description'].widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Product description'
            }
        )

        self.fields['price'].widget = forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }
        )

        self.fields['discount_percent'].widget = forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': '0-100',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }
        )

        self.fields['rating'].widget = forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': '0.0',
                'step': '0.1',
                'min': '0',
                'max': '5'
            }
        )

        self.fields['is_available'].widget = forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )

        self.fields['is_featured'].widget = forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )

        self.fields['is_bestseller'].widget = forms.CheckboxInput(
            attrs={'class': 'form-check-input'}
        )

    def clean_discount_percent(self):
        discount = self.cleaned_data.get('discount_percent')

        if discount is not None and (discount < 0 or discount > 100):
            raise forms.ValidationError(
                'Discount must be between 0 and 100.'
            )

        return discount

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')

        if rating is not None and (rating < 0 or rating > 5):
            raise forms.ValidationError(
                'Rating must be between 0 and 5.'
            )

        return rating

    def save(self, commit=True):
        instance = super().save(commit=False)

        base_slug = slugify(instance.name)
        instance.slug = base_slug

        counter = 1
        while Product.objects.filter(
            slug=instance.slug
        ).exclude(pk=instance.pk).exists():
            instance.slug = f"{base_slug}-{counter}"
            counter += 1

        if commit:
            instance.save()

        return instance


class OrderStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=Order.STATUS_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'max-width: 200px;'
            }
        )
    )


class UserCreateForm(UserCreationForm):

    # NEW: Phone number for the user's Profile
    phone = forms.CharField(
        required=True,
        max_length=15,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Phone number',
                'maxlength': '15'
            }
        )
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser',
            'password1',
            'password2'
        ]

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Username'
                }
            ),

            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'First name'
                }
            ),

            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Last name'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Email address'
                }
            ),

            'is_staff': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),

            'is_superuser': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }


class UserEditForm(UserChangeForm):

    password = None

    # NEW: Phone number
    phone = forms.CharField(
        required=True,
        max_length=15,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Phone number',
                'maxlength': '15'
            }
        )
    )

    class Meta:
        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser',
            'is_active'
        ]

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Username'
                }
            ),

            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'First name'
                }
            ),

            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Last name'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Email address'
                }
            ),

            'is_staff': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),

            'is_superuser': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),

            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            try:
                self.fields['phone'].initial = self.instance.profile.phone
            except Profile.DoesNotExist:
                self.fields['phone'].initial = ''