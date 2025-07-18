from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Create your models here.
class Estore(models.Model):
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=250)
    opening_hour = models.TextField()
    map_embed_url = models.URLField(blank=True, null=True)
    current = models.BooleanField()

    def __str__(self):
        return self.address

    class Meta:
        verbose_name_plural = 'Estore'

    def save(self, *args, **kwargs):
        if self.current:
            prev_current = Estore.objects.filter(current = True)
            prev_current.update(current = False)
        return super().save(*args, **kwargs)
    

class SocialMedia(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.SlugField(unique=True, editable=False)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.icon:
            icon_slug = f"bi-{self.name.lower()}"
            self.icon = slugify(icon_slug)
        return super().save(*args, **kwargs)

class SocialHandle(models.Model):
    estore = models.ForeignKey(
        Estore, on_delete=models.CASCADE, related_name='Social_handle'
        )
    url = models.URLField()
    platform = models.ForeignKey(SocialMedia, on_delete=models.CASCADE)


class Subscriber(models.Model):
    email = models.EmailField(unique=True, max_length=250)

    def __str__(self):
        return self.email
    
    class Meta:
        ordering = ['email',]
        indexes = [
            models.Index(fields=['email',]),
        ]


class Contact(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=250)
    subject = models.CharField(max_length=250)
    message = models.TextField()
    is_subscribed = models.BooleanField(default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
         if not self.is_subscribed:
            subcriber = Subscriber.objects.filter(email = self.email).first()
            if subcriber:
                self.is_subscribed = True
         return super().save(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="subcategories" , null=True, blank=True
    )
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_root(self):
        category = self
        while category.parent:
            category = category.parent
        return category

    @property
    def root_slug(self):
        return self.get_root().slug

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name',]
        indexes = [
            models.Index(fields=['name',]),
        ]

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1, related_name='products')
    description = models.TextField(default='', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    is_sale = models.BooleanField(default=False, editable=False)
    discount = models.DecimalField(
        default=0, decimal_places=2, max_digits=4, help_text="Discount as a percentage (e.g. 10 for 10%)"
        )
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-discount',]
        indexes = [
            models.Index(fields=['-discount',]),
        ]
    
    def save(self, *args, **kwargs):
        if  self.discount != 0:
            discount_amount = self.price * (self.discount / 100)
            self.sale_price = self.price - discount_amount
            self.is_sale = True
        else:
            self.is_sale = False
        return super().save(*args, **kwargs)
    
    @property
    def in_stock(self):
        return self.quantity > 0

    def is_new(self):
        return self.created_at >= now() - timedelta(days=30) and self.in_stock
    
    def average_rating(self):
        avg = self.reviews.aggregate(avg=models.Avg('rating'))['avg']
        if avg is None:
            return 0
        return round(avg * 2) / 2
    
    def rating_count(self):
        return self.reviews.count()
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=225, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    title = models.CharField(null=True, blank=True)
    rating = models.DecimalField(
        default=0, decimal_places=1, max_digits=3,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-rating',]
        indexes = [
            models.Index(fields=['-rating',]),
        ]
    
    def __str__(self):
        return f"{self.title}" if self.title else f"{self.pk}"

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)