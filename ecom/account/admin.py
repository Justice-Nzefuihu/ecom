from django.contrib import admin
from .models import Account, Address, Country
from django.contrib.auth.models import User

# Register your models here.
admin.site.unregister(User)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    search_fields = ('country',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'country', 'default', 'billing')
    list_filter = ('country', 'default', 'billing')
    search_fields = ('user__user__email', 'street', 'city')


class AccountInline(admin.TabularInline):
    model = Account

class AddressInline(admin.StackedInline):
    model = Address
    extra = 1

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    inlines = [AddressInline]


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = [
        "username", "first_name", "last_name", 
        'password', "email", 'is_active', "is_staff", "is_superuser",
        "last_login", "date_joined",
       ]
    list_display = [
            "email", "first_name", "last_name", 
            'is_active', "is_staff", "is_superuser"
            ]
    readonly_fields = ['password', "last_login", "date_joined"]
    inlines = [AccountInline]