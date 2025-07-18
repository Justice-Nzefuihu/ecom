from django.contrib import admin
from .models import (
    Estore, Subscriber, SocialHandle,
    Contact, Review, Category, Product, ProductImage
)
# Register your models here.

admin.site.register(Subscriber)
admin.site.register(Category)
admin.site.register(Review)

class SocialHandleInline(admin.TabularInline):
    model = SocialHandle
    
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

@admin.register(Estore)
class EstoreAdmin(admin.ModelAdmin):
    list_display = ['address', 'current',]
    list_filter =  ['current']
    inlines = [SocialHandleInline]

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject','is_subscribed',]
    list_filter = ['created_at', 'is_subscribed',]
    readonly_fields = ['is_subscribed', ]