from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('user','cart_id', 'date_added')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user','product', 'cart', 'quantity', 'is_active', 'date_added')

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)