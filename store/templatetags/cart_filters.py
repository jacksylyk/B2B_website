from django import template

register = template.Library()


@register.filter(name='total_price')
def total_price(cart_items):
    return sum(item.product.price * item.quantity for item in cart_items)

@register.filter(name='multiply')
def multiply(value, arg):
    return value * arg