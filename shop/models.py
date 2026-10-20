from django.conf import settings
from django.db import models

class Profile(models.Model):
    CUSTOMER = "customer"
    SELLER = "seller"
    ROLE_CHOICES = [(CUSTOMER, "Customer"), (SELLER, "Seller")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    email_verified = models.BooleanField(default=False)
    seller_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shop_products")
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="unique_user_cart_product")]

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="shop_orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=24, default="pending")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sold_order_items")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
