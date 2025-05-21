from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.utils.functional import cached_property
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    username = None
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    email = models.EmailField(('Email Address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']

    favorites = models.ManyToManyField('core.Product', blank=True)

    def __str__(self):
        return f'{self.full_name} ({self.email})'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    products = models.ManyToManyField('core.ProductVariant', related_name='carts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def count(self):
        return self.products.count()

    @property
    def discount(self):
        return sum(i.old_price-i.final_price for i in self.products.all() if i.old_price)

    @property
    def total_price(self):
        return sum(i.final_price for i in self.products.all())

    @property
    def image(self):
        if self.products.exists():
            return self.products.first().image

    def __str__(self):
        return f"{self.user.full_name}'s cart"

class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='address', null=True, blank=True)
    address = models.CharField(max_length=100)
    house = models.CharField(max_length=100, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.address}'
    
    def __iter__(self):
        yield f'Address: {self.address}'
        if self.house:
            yield f'House: {self.house}'
        if self.instructions:
            yield f'Additional Instructions: {self.instructions}'

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    PAYMENT_CHOICES = (
        ('Cash', 'Cash'),
        ('Card', 'Card'),
    )
    SHIPPING_PRICE = Decimal('9.99')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField('core.ProductVariant', related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='order')
    payment_method = models.CharField(max_length=100, choices=PAYMENT_CHOICES, default='Cash')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def shipping_price(self):
        return self.SHIPPING_PRICE

    @cached_property
    def price(self):
        return sum(i.final_price for i in self.products.all())

    @property
    def total_price(self):
        return self.price + self.shipping_price

    def get_absolute_url(self):
        return reverse('accounts:order-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.user.full_name}'s order {self.id} ({self.status}) ${self.total_price}"

    class Meta:
        ordering = ['-created_at']
