from django.db import models

class Product(models.Model):
    model_name = models.CharField(max_length=255)
    description = models.TextField()
    product_details = models.TextField(blank=True, null=True)
    minable_coins = models.CharField(max_length=255, help_text="Comma-separated list, e.g. BTC, BCH, BSV")
    hashrate = models.CharField(max_length=100)
    power = models.CharField(max_length=100)
    algorithm = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    hosting_fee_per_kw = models.DecimalField(
        max_digits=10,
        decimal_places=2,   #It stores currency accurately,It doesn’t create floating point errors,It's used for money everywhere in Django
        blank=True,
        null=True,
        help_text="Fee per kilowatt for hosting"
    )

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

    image = models.ImageField(upload_to='bundle_offers/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



