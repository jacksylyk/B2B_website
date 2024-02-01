from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView

from .forms import CartItemForm, ProductFilterForm
from .models import Category, Product, Cart, CartItem, Brand, Characteristic
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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
    characteristics = Characteristic.objects.filter(is_filter=True)

    # Get the brand and characteristic filters from the request
    brand_filter = request.GET.getlist('brand')
    brand_ids = Brand.objects.filter(name__in=brand_filter).values_list('id', flat=True)
    characteristic_filter = request.GET.getlist('characteristic')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    # If a brand filter is applied, filter the products by brand
    if brand_ids:
        products = Product.objects.filter(category=category, brand__in=brand_ids)
    else:
        products = Product.objects.filter(category=category)

    # If a characteristic filter is applied, filter the products by characteristic
    if characteristic_filter:
        products = products.filter(characteristics__in=characteristic_filter)

    if min_price or max_price:
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

    context = {
        'category_active': category,
        'products': products,
        'categories': categories,
        'filter': {
            'brands': brands,
            'characteristics': characteristics,
        }
    }

    return render(request, 'store/home.html', context)


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(pk=product_id)
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(product=product, cart=user_cart)
        cart_item.quantity += 1
        cart_item.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Product added to cart'})

    return redirect('store:index')


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
    return render(request, 'store/cart_detail.html', {'cart_items': cart_items, 'cart_id': cart_id})


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