
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)  # 👈 important for email verification

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
    


class Rental(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField()  # ex: 30, 60, 90

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} rented {self.product.model_name}"
