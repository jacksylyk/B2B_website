from django.contrib import admin
from .models import Category, Product, Characteristic, Cart, Brand, CharacteristicValue


class CharacteristicValueInline(admin.TabularInline):
    model = CharacteristicValue
    extra = 1
    fields = ('characteristic', 'value')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'slug', 'price', 'in_stock', 'created', 'updated']
    list_filter = ['in_stock', 'is_active']
    list_editable = ['price', 'in_stock']
    prepopulated_fields = {'slug': ('name',)}
    inlines = (CharacteristicValueInline,)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_filter')
    list_filter = ('name', 'is_filter')
    search_fields = ('name',)
    ordering = ('name',)
