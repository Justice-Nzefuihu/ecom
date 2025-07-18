from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.db import transaction
from .models import Account, Address

def submit_form(request, form, form_type):
    if form.is_valid():
        cd = form.cleaned_data
        if form_type == 'register':
           password = form.cleaned_data['password']
           register_user(form, password)
        user = authenticate(
            request, email=cd['email'], password=cd['password']
            )
        if user:
            if user.is_active:
                login(request, user)
                if form_type == 'login':
                    remember_me = cd.get('remember_me')
                    if remember_me:
                        request.session.set_expiry(60 * 60 * 24 * 30)
                messages.success(request, f"You have be successfully {form_type}ed")
                return redirect("store:index")
            messages.error(request, "Invalid Credentials")
            return redirect("account:login_register")
        else:
            messages.error(request, "Invalid Credentials")
            return redirect("account:login_register")
    else:
        # errors = form.errors.as_ul()
        errors = ". ".join([', '.join(mssgs) for mssgs in form.errors.values()])
        messages.error(request, errors)
        if form_type == 'register':
            return redirect(reverse("account:login_register") + "#login-register-registration-form")
        return redirect("account:login_register")
    
def register_user(form, password):
    with transaction.atomic():
        user = form.save(commit=False)
        user.username = user.email
        user.set_password(password)
        user.save()
        Account.objects.create(user=user)
    return user