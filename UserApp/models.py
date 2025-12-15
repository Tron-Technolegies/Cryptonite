
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)  # 👈 important for email 

    # NEW → Save default shipping address if user chooses
    shipping_address = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.email or self.username



from django.conf import settings
from AdminApp.models import BundleOffer, Product   

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    bundle = models.ForeignKey(BundleOffer, on_delete=models.CASCADE, null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            ('user', 'product'),
            ('user', 'bundle'),
        )

    def __str__(self):
        if self.product:
            return f"{self.user.email} - Product: {self.product.model_name}"
        return f"{self.user.email} - Bundle: {self.bundle.name}"
    


# class Rental(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)

#     start_date = models.DateTimeField(auto_now_add=True)
#     end_date = models.DateTimeField()
    
#     amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
#     duration_days = models.PositiveIntegerField()  # ex: 30, 60, 90

#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.user.email} rented {self.product.model_name}"


class Rental(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} rented {self.product.model_name}"

   
    def calculate_rental_fee(self):
        """
        Calculates total rental fee based on:
        - Machine power consumption (e.g., "3250W" → 3.25 kW)
        - hosting_fee_per_kw (monthly rate per kW)
        - duration_days
        """
        import re
        from decimal import Decimal

        power_str = self.product.power.strip()
        match = re.search(r'(\d+(?:\.\d+)?)\s*(kw|w)', power_str, re.IGNORECASE)
        if not match:
            raise ValueError(f"Cannot parse power value: '{power_str}'. Use format like '3250W' or '3.25 kW'")

        value = Decimal(match.group(1))
        unit = match.group(2).upper()

        # Convert to kW
        power_kw = value if unit == 'KW' else value / Decimal('1000')

        if not self.product.hosting_fee_per_kw:
            raise ValueError("hosting_fee_per_kw is not set for this product")

        # Monthly hosting cost for this machine
        monthly_cost = power_kw * self.product.hosting_fee_per_kw

        # Convert to daily (30-day month is standard in mining hosting)
        daily_cost = monthly_cost / Decimal('30')

        # Total for the rental period
        total = daily_cost * Decimal(self.duration_days)

        return total.quantize(Decimal('0.01'))  # Round to 2 decimal places

from django.db import models
from django.conf import settings
from AdminApp.models import Product, BundleOffer

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    stripe_payment_intent = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default="completed")
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_address = models.JSONField(null=True, blank=True)   #new line


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    bundle = models.ForeignKey(BundleOffer, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)


class HostingRequest(models.Model):
    HOSTING_LOCATIONS = (
        ("US", "United States"),
        ("ET", "Ethiopia"),
        ("UAE", "UAE"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    hosting_location = models.CharField(max_length=10, choices=HOSTING_LOCATIONS)

    items = models.JSONField()

    # ⬇️ allow NULL, but NO default
    setup_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    is_paid = models.BooleanField(default=False)

    stripe_payment_intent = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

