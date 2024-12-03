from django.db import models
from colorfield.fields import ColorField
from accounts.models import *
from .utils import Rating
import re, math

class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="images/")
    brand = models.ForeignKey("Brand", on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    specifications = models.ForeignKey("Specifications", on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    storages = models.ManyToManyField("Storage", related_name="products", blank=True)
    type = models.ForeignKey("ProductType", on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    price = models.PositiveSmallIntegerField()
    old_price = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def discount(self):
        if self.old_price:
            return int((self.old_price - self.price) / self.old_price * 100)
        else:
            return 0

    @property
    def category(self):
        if self.type:
            return self.type.category
        else:
            return None

    @property
    def reviews(self):
        reviews: models.QuerySet[Comment] = self.comments.filter(rating_value__gt=0)
        return reviews

    @property
    def rating(self):
        return Rating(self.calculate_rating())

    def calculate_rating(self):
        reviews = self.reviews
        count = reviews.count()
        if count > 0:
            summ = sum(i.rating_value for i in reviews)
            avg = math.ceil(summ / count)
            return avg
        else:
            return 0

    def __str__(self):
        return f"{self.brand} {self.title}"

class Specifications(models.Model):
    FIELDS = {'operating_system':'Operating system',
            'cellular_technology':'Cellular technology',
            'display_type':'Display type',
            'camera':'Camera',
            'cpu':'CPU',
            'ram':'RAM',
            'battery':'Battery',
            'water_and_dust_rating':'Water and dust rating'}

    name = models.CharField(max_length=100, null=True, blank=True)
    operating_system = models.CharField(max_length=100, null=True, blank=True)
    cellular_technology = models.CharField(max_length=100, null=True, blank=True)
    display_type = models.CharField(max_length=100, null=True, blank=True)
    camera = models.CharField(max_length=100, null=True, blank=True)
    cpu = models.CharField(max_length=100, null=True, blank=True)
    ram = models.CharField(max_length=100, null=True, blank=True)
    battery = models.CharField(max_length=100, null=True, blank=True)
    water_and_dust_rating = models.CharField(max_length=100, null=True, blank=True)
    additional_specifications = models.JSONField(null=True, blank=True)

    @property
    def dict(self):
        FIELDS = self.FIELDS
        result = self.additional_specifications or {}
        for i in FIELDS:
            value = getattr(self, i)
            if value:
                result[FIELDS[i]] = value
        return result
    
    def __iter__(self):
        return iter(self.dict.items())

    class Meta:
        verbose_name_plural = verbose_name = "Specifications"

    def __str__(self):
        if self.name:
            return self.name
        return str(self.dict)

class ProductImage(models.Model):
    image = models.ImageField(upload_to="images/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    color = models.ForeignKey("Color", on_delete=models.CASCADE, related_name="images", null=True, blank=True)

    @property
    def url(self):
        return self.image.url

    def __str__(self):
        filename = re.search(r'images/(.*)', self.image.url).group(1)
        if self.color:
            return f"{self.product} ({self.color.color_name}) —— {filename}"
        return f"{self.product} —— {filename}"
    
    class Meta:
        ordering = ['color__color_name']

class Color(models.Model):
    color_name = models.CharField(max_length=100)
    color = ColorField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="colors")

    def __str__(self):
        return f"{self.color_name} ({self.color}) —— {self.product}"
    
    class Meta:
        ordering = ['color_name']

class Storage(models.Model):
    storage = models.PositiveSmallIntegerField() # in GB
    price = models.PositiveSmallIntegerField(default=0)

    @property
    def size_format(self):
        return f"{self.storage} GB" if self.storage < 1024 else f"{self.storage//1024} TB"

    def __str__(self):
        return f"{self.size_format}, +{self.price}$"
    
    class Meta:
        ordering = ['storage']

class Brand(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class ProductType(models.Model):
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.title

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
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def rating(self):
        return Rating(self.rating_value)

    def __str__(self):
        return f'{self.author.full_name}: {self.text}'
    
    class Meta:
        ordering = ['-rating_value']

class ProductVersion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="versions")
    quantity = models.PositiveSmallIntegerField(default=1)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def image(self):
        try:
            return self.product.images.get(color__color_name=self.color.color_name).image
        except:
            return self.product.image

    @property
    def old_price(self):
        old_price = self.product.old_price
        if not old_price:
            return 0
        if self.storage:
            old_price = old_price + self.storage.price
        return old_price * self.quantity

    @property
    def final_price(self):
        final_price = self.product.price
        if self.storage:
            final_price += self.storage.price
        return final_price * self.quantity

    @classmethod
    def delete_empty(cls):
        n = 0
        for i in cls.objects.all():
            if not i.carts.count() and not i.orders.count():
                i.delete()
                n += 1
        return n

    def __str__(self):
        result = str(self.product)
        if self.color:
            result += f" {self.color.color_name}"
        if self.storage:
            result += f" {self.storage.size_format}"
        return result + f" x{self.quantity}"
