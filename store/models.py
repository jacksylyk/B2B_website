from django.conf import settings
from django.db import models
from django.urls import reverse


class Brand(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='brand_product', on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="product_creator")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/')
    slug = models.SlugField(max_length=255)
    price = models.IntegerField(default=0, blank=True)
    quantity = models.PositiveIntegerField()
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Продукты"
        ordering = ('-created',)

    def __str__(self):
        return self.name


class Characteristic(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name="Название характеристики")
    value = models.CharField(max_length=255, verbose_name="Значение характеристики")
    is_filter = models.BooleanField(default=False, verbose_name="Статус для фильтрации")


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='cart', on_delete=models.CASCADE, unique=False,
                                primary_key=False)
    products = models.ManyToManyField(max_length=255, related_name='all_products', blank=True, to='Product',
                                      through='CartItem')

    def __str__(self):
        return f"{self.user}'s cart"

    def get_absolute_url(self):
        return reverse("store:cart_detail")


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.quantity} x {self.product}'
