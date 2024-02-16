from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter(name='total_price')
def total_price(cart_items):
    return sum(item.product.price * item.quantity for item in cart_items)


@register.filter(name='total_quantity')
def total_quantity(cart_items):
    return sum(item.quantity for item in cart_items)


@register.filter(name='multiply')
def multiply(value, arg):
    return value * arg


@register.filter(name='price_filter')
def price_filter(price):
    return intcomma(price).replace(',', ' ')


@register.filter(name='get_list')
def get_list(dictionary, key):
    return dictionary.getlist(key)


@register.filter(name='combine')
def combine(title, value):
    return f"{title}|{value}"


@register.filter(name='string')
def string(brand):
    return f"{brand}"


@register.filter(name='result_price')
def result_price(total_price, delivery_price):
    total_price = int(total_price)
    delivery_price = int(delivery_price)
    result = (total_price + delivery_price) * 1.12
    return round(result, 2)


@register.filter(name='is_completed')
def is_completed(orders, status):
    return orders.filter(completed=status)


@register.filter(name='get_price')
def get_price(order):
    return int(order.get_total_amount())

