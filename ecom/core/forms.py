from django import forms

from .models import (
    Subscriber, Contact
)


class SubscribingForm(forms.ModelForm):
    email = forms.EmailField(
        label='',
        widget= forms.EmailInput(attrs={
            "placeholder": "Your email address"
        }), required=True
    )

    class Meta:
        model = Subscriber
        fields = ['email']

class ContactForm(forms.ModelForm):
    name = forms.CharField(
        label='',
        widget= forms.TextInput(attrs={
            'class': 'form-control',
            "placeholder": "Your name"
        }), required=True
    )
    email = forms.EmailField(
        label='',
        widget= forms.EmailInput(attrs={
            'class': 'form-control',
            "placeholder": "Your Email"
        }), required=True
    )
    subject = forms.CharField(
        label='',
        widget= forms.TextInput(attrs={
            'class': 'form-control',
            "placeholder": "Subject"
        }), required=True
    )
    message = forms.CharField(
        label='',
        widget= forms.Textarea(attrs={
            'class': 'form-control',
            "placeholder": "Message",
            'rows': "6"
        }), required=True
    )

    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']