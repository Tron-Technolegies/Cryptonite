from rest_framework import serializers
from AdminApp.models import Product,BundleOffer


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

    def validate(self, data):
        delivery_type = data.get("delivery_type")
        delivery_date = data.get("delivery_date")

        if delivery_type == "future" and not delivery_date:
            raise serializers.ValidationError({
                "delivery_date": "Delivery date is required for future delivery type."
            })

        if delivery_type == "spot" and delivery_date:
            raise serializers.ValidationError({
                "delivery_date": "Delivery date should be empty for spot delivery type."
            })

        return data

class ProductMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "model_name", "price", "image"]


      
class BundleOfferSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    products = ProductMiniSerializer(many=True, read_only=True)

    class Meta:
        model = BundleOffer
        fields = "__all__"


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
