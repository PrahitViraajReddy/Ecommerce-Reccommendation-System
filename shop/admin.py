from django.contrib import admin
from .models import Profile, Product, CartItem, Order, OrderItem

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "email_verified", "seller_approved")
    list_filter = ("role", "email_verified", "seller_approved")
    search_fields = ("user__username", "user__email")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "seller", "category", "price", "stock", "active")
    list_filter = ("active", "category")
    search_fields = ("name", "seller__username")

admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
