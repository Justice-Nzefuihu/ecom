from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.db.models import Prefetch, Avg, Count, Sum, Q
from django.urls import reverse, NoReverseMatch
from account.models import Account
from .models import (
    Product, Category, ProductImage,
)
from .forms import (
    SubscribingForm, ContactForm
)

# Create your views here.
def index(request):
    products_qs = Product.objects.prefetch_related(
        Prefetch(
            'images',
            queryset=ProductImage.objects.order_by('id'),
            to_attr='prefetched_images'
        )
    )

    floating_products = products_qs.filter(is_sale=True).annotate(
        avg_rating=Avg('reviews__rating'),
        num_ratings=Count('reviews')
    ).order_by('-discount', '-avg_rating', '-num_ratings')[:2]

    total_categories = Category.objects.filter(Q(subcategories__isnull=True) | Q(products__isnull=False)).prefetch_related(
        Prefetch(
            'products',
            queryset=products_qs.all(),
            to_attr='prefetched_products'
        )
    ).distinct()

    best_sellers = products_qs.annotate(
        total_sold = Sum('order_items__quantity')
    ).order_by('-total_sold')[:4]
    
    categories = Category.objects.filter(parent__isnull=True)
    
    products = products_qs.select_related('category')[:8]

    context = {
        'floating_products': floating_products,
        'total_categories': total_categories,
        'categories': categories,
        'best_sellers': best_sellers,
        'products': products
    }

    return render(request, 'index.html', context)

def contact(request):
    contact_form = ContactForm()
    context = {
        "contact_form": contact_form
    }
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        contact_form = ContactForm(data=request.POST)
        if contact_form.is_valid():
            # data = contact_form.cleaned_data
            # code for sending email
            contact_form.save()
            return HttpResponse('OK')
        errors = '<br>'.join([f"{field}: {', '.join(mssg)}"for field, mssg in contact_form.errors.items()])
        return HttpResponseBadRequest(errors)

    return render(request, 'contact.html', context)

@require_POST
def subscribe(request):
    form = SubscribingForm(data=request.POST)
    if form.is_valid():
        data = form.cleaned_data
        # code for sending email
        form.save()
        account = Account.objects.filter(user__email=data['email']).select_related('user').first()
        if account and not account.subscribe:
            account.subscribe = True
            account.save()
        return HttpResponse('OK')
    errors = '<br>'.join([f"{field}: {', '.join(mssg)}"for field, mssg in form.errors.items()])
    return HttpResponseBadRequest(errors)

PAGES = {
    "categories": "store:category_list",
    "index": "store:index",
    "home": "store:index",
    "contact": "store:contact",
}

def search(request):
    page = request.GET.get('page').strip().lower()
    if page:
        if page in PAGES:
            try:
                url = reverse(PAGES[page])
                return redirect(url)
            except NoReverseMatch:
                raise Http404()
    raise Http404()

    
def custom_404(request, exception):
    return render(request, '404.html', status=404)