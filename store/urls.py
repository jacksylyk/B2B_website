from django.contrib import admin
from django.urls import path

from store import views

app_name = 'store'
urlpatterns = [

    path('', views.index, name='index'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path("remove/<int:cart_item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/<int:cart_id>/", views.cart_detail, name="cart_detail"),
    path('update_cart/<int:item_id>/', views.update_cart, name='update_cart'),
]
