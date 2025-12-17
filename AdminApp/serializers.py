from rest_framework import serializers
from AdminApp.models import Product,BundleOffer


class ProductBulkUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    
class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = "__all__"

    def validate(self, attrs):
        """
        Business validation:
        - If delivery_type is 'future', delivery_date must be provided
        """
        delivery_type = attrs.get("delivery_type")
        delivery_date = attrs.get("delivery_date")

        if delivery_type == "future" and not delivery_date:
            raise serializers.ValidationError({
                "delivery_date": "Delivery date is required when delivery type is 'Future'."
            })

        return attrs



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


from rest_framework import serializers
from UserApp.models import Order, OrderItem


class AdminOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.model_name",
        read_only=True
    )
    bundle_title = serializers.CharField(
        source="bundle.title",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_name",
            "bundle_title",
            "quantity",
        ]


class AdminOrderSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    items = AdminOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user_email",
            "total_amount",
            "status",
            "stripe_payment_intent",
            "delivery_address",
            "created_at",
            "items",
        ]
