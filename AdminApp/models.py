from django.db import models
from cloudinary.models import CloudinaryField

from django.db import models
from cloudinary.models import CloudinaryField
from decimal import Decimal

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
    discount_percentage = models.PositiveIntegerField(
        default=0,
        help_text="Discount percentage (0–100)"
)
    currency = models.CharField(
        max_length=10,
        default="USD",
        help_text="Example: USD, INR, EUR"
    )

    hosting_fee_per_kw = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Fee per kilowatt for hosting"
    )
    # ---------------- ELECTRICAL & HARDWARE SPECS ----------------
    warranty = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Example: 6 Months, 1 Year"
    )

    dimensions = models.CharField(
        max_length=100,
        blank=True,
        null=True,
      
    )

    voltage = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Example: 200-240V"
    )

    release_date = models.DateField(
        blank=True,
        null=True
    )

    vendor = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    operating_temperature = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Example: 0°C ,40°C"
    )

    network_interface = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Example: Ethernet"
    )

    plug_socket_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Example: US / EU / UK"
    )

    power_cord_information = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Example: Included / Not Included"
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
    average_rating = models.FloatField(default=0)
    review_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.model_name
    @property
    def discount_amount(self):
        if self.price and self.discount_percentage > 0:
            return (self.price * Decimal(self.discount_percentage)) / Decimal(100)
        return Decimal("0.00")

    @property
    def final_price(self):
        if self.price:
            return self.price - self.discount_amount
        return Decimal("0.00")
    # def average_rating(self):
    #     reviews = self.reviews.all()
    #     if reviews.exists():
    #         return round(sum(r.rating for r in reviews) / reviews.count(), 1)
    #     return 0


class BundleOffer(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # products = models.ManyToManyField(Product)  # multiple machines
    # products = models.ManyToManyField(Product, through="BundleItem",related_name="bundles")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    hosting_fee_per_kw = models.DecimalField(max_digits=10, decimal_places=2)

    total_hashrate = models.CharField(max_length=100, blank=True, null=True)  
    total_power = models.CharField(max_length=100, blank=True, null=True)

    image = CloudinaryField("image", blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class BundleItem(models.Model):
    bundle = models.ForeignKey(
        BundleOffer,
        on_delete=models.CASCADE,
        related_name="bundle_items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("bundle", "product")


from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    short_description = models.CharField(max_length=500)

    # Main thumbnail
    thumbnail = models.ImageField(upload_to="blog_thumbnails/", blank=True, null=True)

    # Paragraphs
    paragraph_1 = models.TextField()
    paragraph_2 = models.TextField(blank=True, null=True)
    paragraph_3 = models.TextField(blank=True, null=True)
    paragraph_4 = models.TextField(blank=True, null=True)
    paragraph_5 = models.TextField(blank=True, null=True)

    # Sub images (between paragraphs)
    image_1 = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    image_2 = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    image_3 = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    image_4 = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    image_5 = models.ImageField(upload_to="blog_images/", blank=True, null=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title




class Events(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    short_description = models.CharField(max_length=500)

    # Main thumbnail
    thumbnail = models.ImageField(upload_to="blog_thumbnails/", blank=True, null=True)

    # Paragraphs
    paragraph_1 = models.TextField()
    paragraph_2 = models.TextField(blank=True, null=True)
    paragraph_3 = models.TextField(blank=True, null=True)
    paragraph_4 = models.TextField(blank=True, null=True)
    paragraph_5 = models.TextField(blank=True, null=True)

    # Sub images (between paragraphs)
    image_1 = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    image_2 = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    image_3 = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    image_4 = models.ImageField(upload_to="blog_images/", blank=True, null=True)
    image_5 = models.ImageField(upload_to="blog_images/", blank=True, null=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



