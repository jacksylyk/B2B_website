from django.urls import path

from store import views

app_name = 'store'
urlpatterns = [
    path('', views.category_detail, name='index', kwargs={'category_id': 1}),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path("remove/<int:cart_item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/<int:cart_id>/", views.cart_detail, name="cart_detail"),
    path('update_cart/<int:item_id>/', views.update_cart, name='update_cart'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('clear_cart/<int:cart_id>/', views.clear_cart, name='clear_cart'),
    path('orders', views.my_orders, name='orders'),
    path('create_order', views.create_order, name='create_order'),
    path('filter-orders/', views.filter_orders, name='filter_orders'),
]
