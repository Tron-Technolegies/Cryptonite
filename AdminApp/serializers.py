from rest_framework import serializers
from AdminApp.models import Product,BundleOffer

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'




class BundleOfferSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all()
    )

    class Meta:
        model = BundleOffer
        fields = "__all__"


