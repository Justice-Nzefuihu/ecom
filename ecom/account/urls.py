from  django.urls import path
from .views import (
    login_register, logout_user, index, 
    settings, addresses, reviews
    )

app_name = 'account'

urlpatterns = [
    path('', index, name='index'),
    path('login_register', login_register, name='login_register'),
    path('logout', logout_user, name='logout'),
    path('settings', settings, name='settings'),
    path('addresses', addresses, name='addresses'),
    path('reviews', reviews, name='reviews'),
] 