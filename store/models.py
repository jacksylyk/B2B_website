from django.conf import settings
from django.db import models
from django.utils import timezone


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
    articul = models.CharField(max_length=16, blank=True, verbose_name="Артикул")

    class Meta:
        verbose_name_plural = "Продукты"
        ordering = ('-created',)

    def __str__(self):
        return self.name


class Characteristic(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название характеристики")
    is_filter = models.BooleanField(default=False, verbose_name="Статус для фильтрации")

    def __str__(self):
        return f"{self.name}"


class CharacteristicValue(models.Model):
    value = models.CharField(max_length=100, verbose_name="Значение")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.characteristic.name}: {self.value}"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='cart', on_delete=models.CASCADE, unique=False,
                                primary_key=False)
    products = models.ManyToManyField(max_length=255, related_name='all_products', blank=True, to='Product',
                                      through='CartItem')

    def __str__(self):
        return f"{self.user}'s cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.quantity} x {self.product}'


# ORDER
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField('Product', through='OrderItem')
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    delivery = models.BooleanField(default=False)
    city = models.CharField(max_length=255, blank=True, default="Астана")
    street = models.CharField(max_length=255, blank=True, default="Акжол")
    house_number = models.CharField(max_length=255, blank=True, default="97/1")
    phone_number = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'Order {self.id}'

    # TODO Указать сумму доставки
    def get_price_delivery(self):
        if self.delivery:
            return 5000
        return 2000

    #TODO Добавить цену с учетом НДС
    def get_total_amount(self):
        if self.delivery:
            price = sum(item.get_item_total() for item in self.order_items.all()) + self.get_price_delivery()
        else:
            price = sum(item.get_item_total() for item in self.order_items.all())
        return price


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def get_item_total(self):
        return self.quantity * self.price
