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


# 10/12/25
from rest_framework import serializers
from UserApp.models import HostingRequest

class AdminHostingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostingRequest
        # allow admin to edit certain fields
        fields = [
            "id", "request_id", "user", "whatsapp_number", "message", "items",
            "status", "admin_notes", "monthly_fee", "contacted_at", "activated_at", "created_at"
        ]
        read_only_fields = ["id", "request_id", "user", "items", "created_at"]
