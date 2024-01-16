from django.shortcuts import render, redirect, get_object_or_404

from .forms import CartItemForm
from .models import Category, Product, Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def category_detail(request, category_id=None):
    default_category_id = 1
    if category_id is None:
        category_id = default_category_id

    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()

    return render(request, 'store/home.html', {'category': category, 'products': products, 'categories': categories})


@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(product=product, cart=user_cart)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('store:index')


@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if cart_item.cart.user == request.user:
        cart_item.delete()
        messages.success(request, "Item removed from your cart.")

    return redirect('store:cart_detail', cart_id=cart_item.cart.id)


@login_required
def cart_detail(request, cart_id):
    cart = get_object_or_404(Cart, pk=cart_id)
    cart_items = cart.items.all()
    return render(request, 'store/cart_detail.html', {'cart_items': cart_items})


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


def get_user_cart(user):
    if user.is_authenticated:
        return Cart.objects.get_or_create(user=user)[0]
    return None
