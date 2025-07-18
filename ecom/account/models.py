from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from core.models import Subscriber
from django_countries.fields import CountryField

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    order_update = models.BooleanField(default=True)
    promotion = models.BooleanField(default=False)
    subscribe = models.BooleanField(default=True)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.user.email


@receiver(post_save, sender=Account)
def create_or_update_subscription(sender, instance, created, **kwargs):
    email = instance.user.email
    if instance.subscribe:
        Subscriber.objects.get_or_create(email=email)
    else:
        Subscriber.objects.filter(email=email).delete()

@receiver(post_delete, sender=Account)
def delete_subscription(sender, instance, **kwargs):
    email = instance.user.email
    Subscriber.objects.filter(email=email).delete()


class Address(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, related_name='addresses')
    default = models.BooleanField(default=True)
    billing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.user.email}" if self.user else f"{self.street}, {self.city}" 
    
    class Meta:
        verbose_name_plural = "Addresses"
    
    def save(self, *args, **kwargs):
        if self.default:
            Address.objects.filter(user=self.user, default=True).exclude(pk=self.pk).update(default=False)
        if self.billing:
            Address.objects.filter(user=self.user, billing=True).exclude(pk=self.pk).update(billing=False)
        return super().save(*args, **kwargs)


class Country(models.Model):
    country = CountryField(blank_label='Select Country')

    def __str__(self):
        return self.country.name

    class Meta:
        verbose_name_plural = "Countries"

        ordering = ['country',]
        indexes = [
            models.Index(fields=['country',]),
        ]
