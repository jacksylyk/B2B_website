import json
import operator
from collections import defaultdict
from datetime import datetime
from functools import reduce
from django.db import transaction
from django.db.models import Case, Value, When, IntegerField
from django.db.models import F
from django.db.models import Min, Max
from django.http.response import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView

from .forms import CartItemForm, ProductFilterForm
from .models import Category, Product, Cart, CartItem, Brand, Characteristic, CharacteristicValue, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Case, Value, When, IntegerField


class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'


def category_detail(request, category_id=None):
    default_category_id = 1
    if category_id is None:
        category_id = default_category_id

    category = get_object_or_404(Category, id=category_id)
    categories = Category.objects.all()
    brands = Brand.objects.filter(brand_product__category=category).distinct()

    characteristics = CharacteristicValue.objects.filter(product__category=category,
                                                         characteristic__is_filter=True).distinct()
    characteristics_filter = defaultdict(list)

    for characteristic in characteristics:
        characteristics_filter[characteristic.characteristic.name].append(characteristic.value)

    brand_filter = request.GET.getlist('brand')
    brand_ids = Brand.objects.filter(name__in=brand_filter).values_list('id', flat=True)
    characteristic_filter = request.GET.getlist('characteristic')

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    quantity_filter = request.GET.get('quantity')  # Get quantity filter value

    # Annotate the queryset with the quantity annotation
    products = Product.objects.annotate(annotated_quantity=Case(
        When(quantity__gt=0, then=Value(1)),
        default=Value(0),
        output_field=IntegerField(),
    ))

    # Filter products based on other criteria
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if characteristic_filter:
        char_names = [char.split('|')[0] for char in characteristic_filter]
        char_values = [char.split('|')[1] for char in characteristic_filter]
        chars_by_name = {}

        for name, value in zip(char_names, char_values):
            if name not in chars_by_name:
                chars_by_name[name] = []
            chars_by_name[name].append(value)

        for name, values in chars_by_name.items():
            filter_char = Characteristic.objects.get(name=name)
            products = products.filter(characteristicvalue__characteristic=filter_char,
                                       characteristicvalue__value__in=values)

    if brand_ids:
        products = products.filter(category=category, brand__in=brand_ids)
    else:
        products = products.filter(category=category)

    # Apply quantity filter
    if quantity_filter == 'in_stock':
        products = products.filter(annotated_quantity__gt=0)
    elif quantity_filter == 'out_of_stock':
        products = products.filter(annotated_quantity=0)

    context = {
        'category_active': category,
        'products': products,
        'categories': categories,
        'filter': {
            'brands': brands,
            'characteristics': dict(characteristics_filter),
            'min_price': min_price if min_price is not None else Product.objects.aggregate(Min('price'))['price__min'],
            'max_price': max_price if max_price is not None else Product.objects.aggregate(Max('price'))['price__max'],
        }
    }

    return render(request, 'store/home.html', context)


@login_required
def add_to_cart(request, product_id):
    current_url = request.build_absolute_uri()
    if request.method == 'POST':
        product = Product.objects.get(pk=product_id)
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(product=product, cart=user_cart)
        cart_item.quantity += 1
        cart_item.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Product added to cart'})

    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if cart_item.cart.user == request.user:
        cart_item.delete()

    return redirect('store:cart_detail', cart_id=cart_item.cart.id)


@login_required
def cart_detail(request, cart_id):
    cart = get_object_or_404(Cart, pk=cart_id)
    cart_items = cart.items.all().order_by('product__name')
    error_messages = messages.get_messages(request)
    return render(request, 'store/cart_detail.html', {'cart_items': cart_items, 'errors': error_messages, 'cart_id': cart_id, 'delivery_price': 5000})


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if 'action' in request.POST:
                if request.POST['action'] == 'increment':
                    quantity += 1
                elif request.POST['action'] == 'decrement':
                    quantity -= 1 if quantity > 1 else 0

            cart_item.quantity = quantity
            cart_item.save()

    return redirect('store:cart_detail', cart_id=cart_item.cart.id)


@login_required
def clear_cart(request, cart_id):
    cart = get_object_or_404(Cart, pk=cart_id)
    cart.products.clear()
    return redirect('store:cart_detail', cart_id=cart_id)


def get_user_cart(user):
    if user.is_authenticated:
        return Cart.objects.get_or_create(user=user)[0]
    return None


@login_required
def create_order(request):
    user_cart = get_user_cart(request.user)
    if request.method == 'POST':
        delivery_type = request.POST.get('delivery')
        city = request.POST.get('city')
        street = request.POST.get('street')
        house_number = request.POST.get('house_number')
        phone_number = request.POST.get('phone_number')
        if delivery_type == "1":
            fields = {'Город': city, 'Улица': street, 'Дом/Офис': house_number}
            for field_name, field_value in fields.items():
                if not field_value:
                    messages.error(request, f"Строка \"{field_name}\" не заполнена")
            if any(not value for value in fields.values()):
                return redirect('store:cart_detail', cart_id=user_cart.id)

        if user_cart:
            with transaction.atomic():
                order = Order.objects.create(user=request.user, delivery=delivery_type, city=city, street=street,
                                             house_number=house_number, phone_number=phone_number)
                for cart_item in user_cart.items.all():
                    # Reduce the quantity of ordered items from the stock
                    if cart_item.product.quantity > 0:  # Check if there is enough stock
                        cart_item.product.quantity = F('quantity') - cart_item.quantity  # Update the stock quantity
                        cart_item.product.save()  # Save the changes to the product
                    else:
                        # Handle the case where there is not enough stock
                        error_message = f'"{cart_item.product}" нет в наличии'
                        messages.error(request, error_message)
                        return redirect('store:cart_detail', cart_id=user_cart.id)
                    OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity,
                                             price=cart_item.product.price)
                user_cart.products.clear()
            return redirect('store:cart_detail', cart_id=user_cart.id)
        else:
            return redirect('store:index')


@login_required
def filter_orders(request):
    if request.method == 'POST':
        # Extracting dates from the form
        date_range = request.POST.get('range_date').split(', ')
        start_date_str = date_range[0]
        end_date_str = date_range[1]

        start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
        end_date = datetime.strptime(end_date_str, '%d.%m.%Y')

        # Filtering orders by date range
        orders = Order.objects.filter(user=request.user, created__range=[start_date, end_date]).order_by('-created')

        # Redirecting with filtered orders as URL parameters
        return redirect('store:my_orders', filtered_orders=orders)


@login_required
def my_orders(request):
    # Retrieve orders associated with the current user
    orders = Order.objects.filter(user=request.user).order_by('-created')
    range_date = request.GET.get('range_date')  # Use request.GET instead of request.POST
    if range_date:
        # Split the date range and parse the start and end dates
        start_date_str, end_date_str = range_date.split(', ')
        start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
        end_date = datetime.strptime(end_date_str, '%d.%m.%Y')

        # Filter orders within the date range
        orders = orders.filter(created__date__gte=start_date, created__date__lte=end_date)

    return render(request, 'store/orders.html', {'orders': orders})