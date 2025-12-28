
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
    
# Import Decimal for accurate financial calculations
from decimal import Decimal

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
        # Read machine power from product.
        # ASSUMPTION: power is stored in WATTS (no unit in DB)
        power_watts = Decimal(self.product.power)

        # Convert power from watts to kilowatts (1 kW = 1000 W)
        power_kw = power_watts / Decimal("1000")

        # Ensure hosting fee per kW is set for this product
        # This is required to calculate the hosting cost
        if self.product.hosting_fee_per_kw is None:
            raise ValueError("hosting_fee_per_kw is not set for this product")

        # Calculate monthly hosting cost for this machine
        # Formula: power (kW) × hosting fee per kW
        monthly_cost = power_kw * self.product.hosting_fee_per_kw

        # Convert monthly cost to daily cost
        # Assumption: 30.5 days = 1 month (standard hosting calculation)
        daily_cost = monthly_cost / Decimal("30.5")

        # STEP 6:
        # Calculate total rental cost for the given rental duration
        # Formula: daily cost × number of rental days
        total = daily_cost * Decimal(self.duration_days)

        # STEP 7:
        # Round the final amount to 2 decimal places (currency format)
        return total.quantize(Decimal("0.01"))



from django.db import models
from django.conf import settings
from AdminApp.models import Product, BundleOffer


class Order(models.Model):
    STATUS_CHOICES = (
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("shipped", "Shipped"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    stripe_payment_intent = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="processing"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    delivery_address = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

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
    MONITORING_CHOICES = (
        ("internal", "Cryptonite Platform"),
        ("external", "Third Party Platform"),
    )

    monitoring_type = models.CharField(
        max_length=20,
        choices=MONITORING_CHOICES,
        null=True,
        blank=True
    )

    monitoring_activated = models.BooleanField(default=False)
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



class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    purchase_type = models.CharField(max_length=20)
    related_id = models.PositiveIntegerField()  # order_id / rental_id / hosting_id
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    stripe_payment_intent = models.CharField(max_length=255)
    invoice_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

