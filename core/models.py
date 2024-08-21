from django.db import models
from colorfield.fields import ColorField
from accounts.models import User
import re, math

class Rating(models.Model):
    rating = models.PositiveIntegerField()

    @classmethod
    def get_default_pk(cls):
        return cls.objects.get_or_create(rating=0)[0].pk

    def render_stars_html(self):
        result = ''
        for i in range(self.rating):
            result += '<img src="/static/img/star.svg" alt="">\n'
        for i in range(5 - self.rating):
            result += '<img src="/static/img/star-empty.svg" alt="">\n'
        return result

    def __str__(self):
        return str(self.rating) if self.rating > 0 else 'No rating'

class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="images/")
    brand = models.ForeignKey("Brand", on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    specifications = models.ForeignKey("Specifications", on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    storages = models.ManyToManyField("Storage", related_name="products", blank=True)
    type = models.ForeignKey("ProductType", on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    rating = models.ForeignKey("Rating", on_delete=models.CASCADE, related_name="products", default=Rating.get_default_pk, null=True, blank=True)
    price = models.PositiveIntegerField() # TODO: different configurations have different prices
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
    def reviews(self) -> models.QuerySet:
        return self.comments.filter(rating__rating__gt=0)

    def calculate_rating(self):
        reviews = self.reviews
        if reviews.count() > 0:
            summ = sum(i.rating.rating for i in reviews.all())
            count = reviews.count()
            avg = math.ceil(summ / count)
            return avg
        else:
            return 0

    def __str__(self):
        return f"{self.brand} {self.title}"

class Specifications(models.Model):
    FIELDS = {'operating_system':'Operating system'
              ,'cellular_technology':'Cellular technology'
              ,'display_type':'Display type'
              ,'camera':'Camera'
              ,'cpu':'CPU'
              ,'ram':'RAM'
              ,'battery':'Battery'
              ,'water_and_dust_rating':'Water and dust rating'}
    
    name = models.CharField(max_length=100, null=True, blank=True)
    operating_system = models.CharField(max_length=100, null=True, blank=True)
    cellular_technology = models.CharField(max_length=100, null=True, blank=True)
    display_type = models.CharField(max_length=100, null=True, blank=True)
    camera = models.CharField(max_length=100, null=True, blank=True)
    cpu = models.CharField(max_length=100, null=True, blank=True)
    ram = models.CharField(max_length=100, null=True, blank=True)
    battery = models.CharField(max_length=100, null=True, blank=True)
    water_and_dust_rating = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Specifications"
        verbose_name_plural = "Specifications"

    @property
    def dict(self):
        result = {}; FIELDS = self.FIELDS
        for i in FIELDS:
            value = eval(f'self.{i}')
            if value:
                result[FIELDS[i]] = value
        return result
    
    def __iter__(self):
        return iter(self.dict.items())

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

class Color(models.Model):
    color_name = models.CharField(max_length=100)
    color = ColorField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="colors")

    def __str__(self):
        return f"{self.color_name} ({self.color}) —— {self.product}"

class Storage(models.Model):
    storage = models.PositiveIntegerField() # in GB
    price = models.PositiveIntegerField(default=0)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="storages", null=True, blank=True, db_constraint=False)

    @property
    def size_format(self):
        return f"{self.storage} GB" if self.storage < 1024 else f"{self.storage//1024} TB"

    def __str__(self):
        return f"{self.size_format}, +{self.price}$"

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
    text = models.TextField()
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name="comments", default=Rating.get_default_pk)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.full_name}: {self.text}'

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorites")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.full_name}: {self.product}'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    products = models.ManyToManyField("ProductVersion", related_name="carts", blank=True)
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
        if self.products.first():
            return self.products.first().image

    def clear_cart(self):
        for product in self.products.all():
            self.products.remove(product)

    def __str__(self):
        return f"{self.user.full_name}'s cart"

class ProductVersion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="versions")
    quantity = models.PositiveIntegerField(default=1)
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
            old_price =  old_price + self.storage.price
        if self.quantity > 1:
            old_price = old_price * self.quantity
        return old_price

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
        # if self.quantity > 1:
        #     result += f" x{self.quantity}"
        return result

class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="address", null=True, blank=True)
    address = models.CharField(max_length=100)
    house = models.CharField(max_length=100, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.address}"
    
    def __iter__(self):
        yield f'Address: {self.address}'
        if self.house:
            yield f'House: {self.house}'
        if self.instructions:
            yield f'Additional Instructions: {self.instructions}'

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    products = models.ManyToManyField(ProductVersion, related_name="orders")
    address = models.ForeignKey("Address", on_delete=models.CASCADE, related_name="order")
    payment_method = models.CharField(max_length=100, choices=PAYMENT_CHOICES, default="Cash")
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def shipping_price(self):
        SHIPPING_PRICE = 9.99
        return SHIPPING_PRICE
    
    @property
    def price(self):
        return sum(i.final_price for i in self.products.all())

    @property
    def total_price(self):
        return self.price + self.shipping_price

    def __str__(self):
        return f"{self.user.full_name}'s order {self.id} ({self.status}) ${self.total_price}"
