import json
from rest_framework import serializers
from AdminApp.models import BundleItem, Product, BundleOffer


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

    class Meta:
        model = Product
        fields = ["id", "model_name", "price", "image"]



class ProductMiniSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "model_name", "price", "image"]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


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





# serializers.py

from rest_framework import serializers
from .models import BundleOffer, BundleItem, Product
# serializers.py

from rest_framework import serializers
from .models import BundleOffer, BundleItem, Product


class BundleItemSerializer(serializers.Serializer):
    """Serializer for bundle items input"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Product with id {value} does not exist.")
        return value


class BundleOfferCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating bundle offers"""
    items = BundleItemSerializer(many=True)

    class Meta:
        model = BundleOffer
        fields = [
            "name",
            "description",
            "price",
            "hosting_fee_per_kw",
            "total_hashrate",
            "total_power",
            "image",
            "items",
        ]

    def validate_items(self, value):
        """Ensure items list is not empty"""
        if not value:
            raise serializers.ValidationError("Items list cannot be empty.")
        return value

    def create(self, validated_data):
        """Create bundle with items"""
        items_data = validated_data.pop("items")
        
        # Create the bundle (CloudinaryField handles image upload automatically)
        bundle = BundleOffer.objects.create(**validated_data)
        
        # Create bundle items
        for item_data in items_data:
            BundleItem.objects.create(
                bundle=bundle,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"]
            )
        
        return bundle

    def update(self, instance, validated_data):
        """Update bundle and items"""
        items_data = validated_data.pop("items", None)
        
        # Update bundle fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update items if provided
        if items_data is not None:
            # Delete existing items
            instance.bundle_items.all().delete()
            
            # Create new items
            for item_data in items_data:
                BundleItem.objects.create(
                    bundle=instance,
                    product_id=item_data["product_id"],
                    quantity=item_data["quantity"]
                )
        
        return instance


class BundleItemDetailSerializer(serializers.ModelSerializer):
    """Serializer for bundle item details in response"""
    product_id = serializers.IntegerField(source='product.id')
    product_name = serializers.CharField(source='product.model_name')  # Changed to model_name
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=12,
        decimal_places=2
    )
    
    class Meta:
        model = BundleItem
        fields = ['product_id', 'product_name', 'product_price', 'quantity']


class BundleOfferSerializer(serializers.ModelSerializer):
    """Serializer for reading bundle offers"""
    image = serializers.SerializerMethodField()
    items = BundleItemDetailSerializer(source='bundle_items', many=True, read_only=True)
    
    class Meta:
        model = BundleOffer
        fields = [
            'id',
            'name',
            'description',
            'price',
            'hosting_fee_per_kw',
            'total_hashrate',
            'total_power',
            'image',
            'items',
            'created_at',
        ]
    
    def get_image(self, obj):
        """Return Cloudinary URL"""
        if obj.image:
            return obj.image.url
        return None