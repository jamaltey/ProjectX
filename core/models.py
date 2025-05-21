import math
import os

from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify

from accounts.models import User

from .utils import Rating


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/')
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    specifications = models.ForeignKey('Specifications', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    colors = models.ManyToManyField('Color', related_name='products', blank=True)
    storages = models.ManyToManyField('Storage', related_name='products', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(0)])
    old_price = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(0)], null=True, blank=True)
    sold_units = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def discount(self):
        return int((self.old_price - self.price) / self.old_price * 100) if self.old_price else 0

    @property
    def reviews(self):
        self.comments: models.QuerySet[Comment]
        return self.comments.filter(rating_value__gt=0)

    @cached_property
    def rating(self):
        return Rating(self.calculate_rating())

    def calculate_rating(self):
        avg_rating = self.reviews.aggregate(models.Avg('rating_value'))['rating_value__avg']
        return math.ceil(avg_rating) if avg_rating else 0

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ['-created_at']

class Specifications(models.Model):
    FIELDS = {
        'operating_system':'Operating system',
        'cellular_technology':'Cellular technology',
        'display':'Display',
        'camera':'Camera',
        'chip': 'Chip',
        'cpu':'CPU',
        'ram':'RAM',
        'battery':'Battery',
        'water_and_dust_rating':'Water and dust rating'
    }

    name = models.CharField(max_length=100, null=True, blank=True)
    operating_system = models.CharField(max_length=100, null=True, blank=True)
    cellular_technology = models.CharField(max_length=100, null=True, blank=True)
    display = models.CharField(max_length=100, null=True, blank=True)
    camera = models.CharField(max_length=100, null=True, blank=True)
    chip = models.CharField(max_length=100, null=True, blank=True)
    cpu = models.CharField(max_length=100, null=True, blank=True)
    ram = models.CharField(max_length=100, null=True, blank=True)
    battery = models.CharField(max_length=100, null=True, blank=True)
    water_and_dust_rating = models.CharField(max_length=100, null=True, blank=True)
    additional_specifications = models.JSONField(null=True, blank=True, default=dict)

    def to_dict(self):
        return {
            self.FIELDS[key]: getattr(self, key)
            for key in self.FIELDS
            if getattr(self, key)
        } | (self.additional_specifications or {})

    def __iter__(self):
        return iter(self.to_dict().items())

    class Meta:
        verbose_name_plural = verbose_name = 'Specifications'

    def __str__(self):
        return self.name if self.name else str(self.to_dict())

class ProductImage(models.Model):
    image = models.ImageField(upload_to='images/')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    color = models.ForeignKey('Color', on_delete=models.CASCADE, related_name='images', null=True, blank=True)

    def clean(self):
        max_images_count = self.product.colors.count() + 1 if self.product.colors.exists() else 5
        if not self.pk and self.product.images.count() >= max_images_count:
            raise ValidationError(f"This product can't have more than {max_images_count} images")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def url(self):
        return self.image.url

    def __str__(self):
        filename = os.path.basename(self.image.name)
        if self.color:
            return f'{self.product} ({self.color.name}) —— {filename}'
        return f'{self.product} —— {filename}'

    class Meta:
        ordering = ['product']

class Color(models.Model):
    name = models.CharField(max_length=100)
    color = ColorField()

    def __str__(self):
        return f'{self.name} ({self.color})'

    class Meta:
        ordering = ['name']

class Storage(models.Model):
    storage = models.PositiveSmallIntegerField(help_text='In GB')
    add_price = models.PositiveSmallIntegerField(
        blank=True, default=0, help_text='The price that will be added to the price of the product'
    )

    @property
    def size_format(self):
        return f'{self.storage} GB' if self.storage < 1024 else f'{self.storage // 1024} TB'

    def __str__(self):
        return f'{self.size_format}, +{self.add_price}$'

    class Meta:
        ordering = ['storage']

class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'

class Comment(models.Model):
    RATING_CHOICES =(
        (0, 'No rating'),
        (1, '1 star'),
        (2, '2 stars'),
        (3, '3 stars'),
        (4, '4 stars'),
        (5, '5 stars')
    )

    text = models.TextField()
    rating_value = models.PositiveSmallIntegerField(default=0, choices=RATING_CHOICES)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def rating(self):
        return Rating(self.rating_value)

    def __str__(self):
        truncated = self.text[:50] + ('...' if len(self.text) > 50 else '')
        return f'{self.author.full_name}: {truncated}'

    class Meta:
        ordering = ['-rating_value']

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    quantity = models.PositiveSmallIntegerField(default=1)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @cached_property
    def image(self):
        if self.color:
            product_image = next(
                (img for img in self.product.images.all() if img.color_id == self.color_id),
                None
            )
            if product_image:
                return product_image.image
        return self.product.image

    @cached_property
    def old_price(self):
        old_price = self.product.old_price or 0
        if self.storage:
            old_price += self.storage.add_price
        return old_price * self.quantity

    @cached_property
    def final_price(self):
        final_price = self.product.price
        if self.storage:
            final_price += self.storage.add_price
        return final_price * self.quantity

    def __str__(self):
        result = str(self.product)
        if self.color:
            result += f' {self.color.name}'
        if self.storage:
            result += f' {self.storage.size_format}'
        return result + f' x{self.quantity}'
