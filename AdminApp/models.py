from django.db import models
from cloudinary.models import CloudinaryField

from django.db import models
from cloudinary.models import CloudinaryField


class Product(models.Model):

    # ---------------- BASIC DETAILS ----------------
    model_name = models.CharField(max_length=255)
    description = models.TextField()
    

    # ---------------- MINING DETAILS ----------------
    minable_coins = models.CharField(
        max_length=255,
        help_text="Comma-separated list, e.g. BTC, BCH, BSV"
    )
    hashrate = models.CharField(max_length=100)
    power = models.CharField(max_length=100)
    algorithm = models.CharField(max_length=100)

    # ---------------- PRICING ----------------
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )

    hosting_fee_per_kw = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Fee per kilowatt for hosting"
    )

    # ---------------- CATEGORY ----------------
    CATEGORY_CHOICES = [
        ("air", "Air Cooled"),
        ("immersion", "Immersion"),
        ("hydro", "Hydro"),
        ("home", "Home Miner"),
    ]

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='null'
    )

    # ---------------- BRAND & TECH ----------------
    brand = models.CharField(max_length=100, default='null')
    efficiency = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Example: 29.5 J/TH"

    )
    noise = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Example: 75 dB"
    )

    # ---------------- DELIVERY ----------------
    DELIVERY_TYPE_CHOICES = [
        ("spot", "Spot"),
        ("future", "Future"),
    ]

    delivery_type = models.CharField(
        max_length=10,
        choices=DELIVERY_TYPE_CHOICES,
        default="spot"
    )

    delivery_date = models.DateField(
        blank=True,
        null=True,
        help_text="Required only if delivery type is Future"
    )

    # ---------------- AVAILABILITY ----------------
    is_available = models.BooleanField(
        default=True,
        help_text="Is the product currently available?"
    )

    # ---------------- MEDIA ----------------
    image = CloudinaryField("image", blank=True, null=True)

    # ---------------- META ----------------
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.model_name


class BundleOffer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    products = models.ManyToManyField(Product)  # multiple machines

    price = models.DecimalField(max_digits=12, decimal_places=2)
    hosting_fee_per_kw = models.DecimalField(max_digits=10, decimal_places=2)

    total_hashrate = models.CharField(max_length=100, blank=True, null=True)  
    total_power = models.CharField(max_length=100, blank=True, null=True)

    # image = CloudinaryField("image", blank=True, null=True)
    image = models.ImageField(upload_to="bundle_offers/", blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



