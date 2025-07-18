from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth import logout
from django.contrib import messages
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from .utils import submit_form
from .models import Address
from core.models import Review
from .forms import (
    UserLogInForm, UserRegisterForm, 
    AccountForm, UserEditForm, ChangePasswordForm,
    AddressForm, ReviewForm
)

# Create your views here.
def login_register(request):
    if request.method == "POST":
        form_type = request.POST.get('form_type')
        if form_type == "login":
            login_form = UserLogInForm(data=request.POST)
            return submit_form(request, login_form, form_type)
        elif form_type == "register":
            register_form = UserRegisterForm(data=request.POST)
            return submit_form(request, register_form, form_type)
                
    login_form = UserLogInForm()
    register_form = UserRegisterForm()

    context = {
        'login_form': login_form,
        "register_form": register_form
    }
    return render(request, 'login-register.html', context)

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "You have be successfully logged out")
    return redirect("store:index")

@login_required
def index(request):
    current_user = request.user
    edit_form = UserEditForm(instance=current_user)
    account_form = AccountForm(instance=current_user.account)
    change_pwd_form = ChangePasswordForm()
    address_form = AddressForm()

    addresses = Address.objects.filter(user__user = current_user).select_related('user', 'user__user', 'country')
    reviews = Review.objects.filter(user=current_user).select_related('product', 'user')
    reviews_pag  = Paginator(reviews, 1)
    page_num = request.GET.get('page', 1)
    try:
        reviews = reviews_pag.page(page_num)
    except EmptyPage:
        reviews = reviews_pag.page(1)
    except PageNotAnInteger:
        reviews = reviews_pag.page(reviews_pag.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.GET.get("pagination"):
        print('iheroinreoireoi')
        html = render_to_string("partials/review_cards.html", {"reviews": reviews},request=request)
        return JsonResponse({"grid":'reviews', "html":html})

    context = {
         "edit_form": edit_form,
         'account_form': account_form,
         'change_pwd_form': change_pwd_form,
         'address_form': address_form,
         'addresses': addresses,
         "reviews": reviews
    }
    return render(request, 'account_base.html', context)

@require_POST
@login_required
def settings(request):
    current_user = request.user
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form_type = request.POST.get('form_type')
        if form_type == 'edit_user':
            edit_form = UserEditForm(data=request.POST, instance=current_user)
            account_form = AccountForm(data=request.POST, instance=current_user.account)
            if edit_form.is_valid() and account_form.is_valid():
                edit_form.save()
                account_form.save()
                return HttpResponse('OK')
            errors1 = ". ".join([', '.join(mssgs) for mssgs in account_form.errors.values()])
            errors2 = ". ".join([', '.join(mssgs) for mssgs in edit_form.errors.values()])
            errors = '. '.join([errors1, errors2])
            return HttpResponseBadRequest(errors)
        elif form_type == 'change_pwd':
            change_pwd_form = ChangePasswordForm(data=request.POST, user=current_user)
            if change_pwd_form.is_valid():
                current_user.set_password(
                    change_pwd_form.cleaned_data['new_password']
                    )
                current_user.save()
                update_session_auth_hash(request, request.user)
                return HttpResponse('OK')
            errors = ". ".join([', '.join(mssgs) for mssgs in change_pwd_form.errors.values()])
            return HttpResponseBadRequest(errors)
        elif form_type == 'delete_account':
            current_user.is_active = False
            current_user.save()
            logout(request)
            messages.success(request, "Your account ha been deleted successfully..")
            return JsonResponse({'url': reverse("store:index")})
        elif form_type == 'email_preference':
            account = current_user.account
            account.order_update = 'order_update' in request.POST
            account.promotion = 'promotion' in request.POST
            account.subscribe = 'subscribe' in request.POST
            account.save()
            return HttpResponse("OK")


@require_POST
@login_required
def addresses(request):
    current_user = request.user
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form_type = request.POST.get('form_type')
        if form_type == 'add_address':
            index = request.POST.get('index')
            address = None
            if index:
                address = get_object_or_404(Address, pk=index, user__user=current_user)

            address_form = AddressForm(request.POST, instance=address)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                if not address:
                    address.user = current_user.account
                address.save()
                return HttpResponse("OK")
            errors = ". ".join([', '.join(mssgs) for mssgs in address_form.errors.values()])
            return HttpResponseBadRequest(errors)
        elif form_type == 'delete_address':
            index = request.POST.get('index')
            address = get_object_or_404(Address, pk=index, user__user=current_user)
            address.delete()
            messages.success(request, "You have deleted an address successfully..")
            return JsonResponse()
        elif form_type == 'make_billing':
            index = request.POST.get('index')
            address = get_object_or_404(Address, pk=index, user__user=current_user)
            address.billing = True
            address.save()
            messages.success(request, "You have updated your addresses successfully..")
            return JsonResponse({'status': 'success'})
        elif form_type == 'make_default':
            index = request.POST.get('index')
            address = get_object_or_404(Address, pk=index, user__user=current_user)
            address.default = True
            address.save()
            messages.success(request, "You have updated your addresses successfully..")
            return JsonResponse({'status': 'success'})
        elif form_type == 'edit_address':
            index = request.POST.get('index')
            address = get_object_or_404(Address, pk=index, user__user=current_user) 
            address_form = AddressForm(instance=address)
            html = render_to_string("partials/address_form.html", {"address_form": address_form, "index": index}, request=request)
            return JsonResponse({"html": html})

@login_required
@require_POST
def reviews(request):
    current_user = request.user
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        form_type = request.POST.get('form_type')
        if form_type == "delete_review":
            index = request.POST.get('index')
            review = get_object_or_404(Review, pk=index, user=current_user)
            review.delete()
            messages.success(request, "You have deleted a review successfully..")
            return JsonResponse()
        elif form_type == "edit_review":
            index = request.POST.get('index')
            review = get_object_or_404(Review, pk=index, user=current_user)
            review_form = ReviewForm(instance=review)
            html = render_to_string("partials/review_form.html", {"review_form": review_form, "index": index}, request=request)
            return JsonResponse({"html": html})
        elif form_type == "add_reviews":
            index = request.POST.get('index')
            review = None
            if index:
                review = get_object_or_404(Review, pk=index, user__user=current_user)

            review_form = ReviewForm(request.POST, instance=review)
            if review_form.is_valid():
                review = review_form.save()
                messages.success(request, "You have Update a review successfully..")
                return redirect("account:index")
            errors = ". ".join([', '.join(mssgs) for mssgs in review_form.errors.values()])
            messages.error(request, errors)
            return redirect("account:index")
            




