from django.urls import path
from .views import (
    index, contact, search, subscribe
)

app_name = "store"

urlpatterns = [
    path('', index, name='index'),
    path('contact', contact, name='contact'),
    path('search', search, name='search'),
    path('subscribe', subscribe, name='subscribe'),
]