from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter(name='total_price')
def total_price(cart_items):
    return sum(item.product.price * item.quantity for item in cart_items)

@register.filter(name='multiply')
def multiply(value, arg):
    return value * arg

@register.filter(name='price_filter')
def price_filter(price):
    return intcomma(price).replace(',', ' ')