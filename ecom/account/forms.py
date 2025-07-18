from django import forms
from django.contrib.auth.models import User
from .models import Account, Address, Country
from core.models import Review

class UserLogInForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={
            "class":"form-control",
            "id":"login-register-login-email"
        }), required=True

    )
    password = forms.CharField(
        label='Password',
        required=True,
        widget=forms.PasswordInput(attrs={
            "class":"form-control",
            "id":"login-register-login-password"
        })
    )
    remember_me = forms.BooleanField(
        label='Password',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "class":"form-check-input",
            "id":"login-register-remember-me"
        })
    )


class BaseUserForm(forms.ModelForm):
    first_name = forms.CharField(label="First name", required=True)
    last_name = forms.CharField(label="Last name", required=True)
    email = forms.EmailField(label="Email address", required=True)
    def __init__(self, prefix_id = '', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].widget.attrs.update({
            "class": "form-control",
            "id": f"{prefix_id}firstname"
        })
        self.fields['last_name'].widget.attrs.update({
            "class": "form-control",
            "id": f"{prefix_id}lastname"
        })
        self.fields['email'].widget.attrs.update({
            "class": "form-control",
            "id": f"{prefix_id}email"
        })

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = User.objects.exclude(id=self.instance.id).filter(email=email)
        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return email



class UserRegisterForm(BaseUserForm):
    password = forms.CharField(
        label='Password',
        required=True,
        widget=forms.PasswordInput(attrs={
            "class":"form-control",
            "id":"login-register-reg-password"
        })
    )
    password2 = forms.CharField(
        label='Confirm password',
        required=True,
        widget=forms.PasswordInput(attrs={
            "class":"form-control",
            "id":"login-register-reg-confirm-password"
        })
    )
    agree_to_policy = forms.BooleanField(
        label="I agree to the privacy policy and terms.",
        required=True,
        error_messages={
            'required': 'You must agree to the policy to continue.'
        },
        widget=forms.CheckboxInput(attrs={
            "class":"form-check-input",
            "id":"login-register-terms"
        })
    )

    class Meta(BaseUserForm.Meta):
        fields = BaseUserForm.Meta.fields + ['password']

    def __init__(self, *args, **kwargs):  
        super().__init__(prefix_id = "login-register-reg-", *args, **kwargs)
    
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password']
    

class UserEditForm(BaseUserForm):
    def __init__(self, *args, **kwargs):
        super().__init__(prefix_id = "", *args, **kwargs)

class AccountForm(forms.ModelForm):
    phone = forms.CharField(
        label='Phone',
        required=False,
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "id":"phone"
        })
    )

    class Meta:
        model = Account
        fields = ['phone']

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='Current password',
        required=True,
        widget=forms.PasswordInput(attrs={
            "class":"form-control",
            "id":"currentPassword"
        })
    )
    new_password = forms.CharField(
        label='New password',
        required=True,
        widget=forms.PasswordInput(attrs={
            "class":"form-control",
            "id":"newPassword"
        })
    )
    new_password2 = forms.CharField(
        label='Confirm password',
        required=True,
        widget=forms.PasswordInput(attrs={
            "class":"form-control",
            "id":"confirmPassword"
        })
    )

    def __init__(self, user : User = None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Invalid current password")
        return old_password

    def clean_new_password2(self):
        cd = self.cleaned_data
        if cd['new_password'] != cd['new_password2']:
            raise forms.ValidationError("New Passwords don't match.")
        return cd['new_password']
    

class AddressForm(forms.ModelForm):
    street = forms.CharField(
        label='Street Address',
        required=True,
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "id": "address",
            "placeholder": "Street Address"
        })
    )
    city = forms.CharField(
        label='City',
        required=True,
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "id": "city",
            "placeholder": "City"
        })
    )
    state = forms.CharField(
        label='State',
        required=True,
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "id": "state",
            "placeholder": "State"
        })
    )
    zipcode = forms.CharField(
        label='Zip Code',
        required=True,
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "id": "zipcode",
            "placeholder": "Zip Code"
        })
    )
    country = forms.ModelChoiceField(
        queryset= Country.objects.all(),
        empty_label='Select Country',
        label='Country',
        required=True,
        widget=forms.Select(attrs={
            "class":"form-select",
            "id": "country",
            "placeholder": "Country"
        })
    )

    default = forms.BooleanField(
        label="Make Default Shipping Address",
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class":"form-check-input",
            "id":"default"
        })
    )
    billing = forms.BooleanField(
        label="Make Billing Address",
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class":"form-check-input",
            "id":"billing"
        })
    )

    class Meta:
        model = Address
        fields = [
            'street', 'city', 'state', 'zipcode', 
            'country', 'default', 'billing'
            ]
        
class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'id': 'star'}),
        label="Your Rating"
    )
    name = forms.CharField(
        label='Your Name',
        required=False,
        widget=forms.widgets.TextInput(attrs={
            "class":"form-control", "id":"review-name"
        })
    )
    email = forms.EmailField(
        label='Your Email',
        required=False,
        widget=forms.widgets.EmailInput(attrs={
            "class":"form-control", "id":"review-email"
        })
    )
    title = forms.CharField(
        label='Review Title',
        required=False,
        widget=forms.widgets.TextInput(attrs={
            "class":"form-control", "id":"review-title"
        })
    )
    review = forms.CharField(
        label='Your Review',
        required=True,
        widget=forms.widgets.TextInput(attrs={
            "class":"form-control", "id":"review-content", "rows":"4"
        })
    )

    class Meta:
        model = Review
        fields = ['name', 'email', 'title', 'rating', "review"]