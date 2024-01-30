from django.contrib import admin
from .models import Category, Product, Characteristic, Cart


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class CharacteristicInline(admin.TabularInline):
    model = Characteristic
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'slug', 'price', 'in_stock', 'created', 'updated']
    list_filter = ['in_stock', 'is_active']
    list_editable = ['price', 'in_stock']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CharacteristicInline]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user']
