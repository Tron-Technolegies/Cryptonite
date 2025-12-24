from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
import AdminApp

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {'username': {'required': True}, 'email': {'required': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)   # remove confirm password
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)             # hashes password
        user.save()
        return user



from .models import CartItem, Order, OrderItem
from AdminApp.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



from .models import CartItem

# class CartItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.CharField(source='product.model_name', read_only=True)
#     product_price = serializers.DecimalField(source='product.price', max_digits=12, decimal_places=2, read_only=True)

#     bundle_name = serializers.CharField(source='bundle.name', read_only=True)
#     bundle_price = serializers.DecimalField(source='bundle.price', max_digits=12, decimal_places=2, read_only=True)

#     class Meta:
#         model = CartItem
#         fields = [
#             "id",
#             "product",
#             "product_name",
#             "product_price",
#             "bundle",
#             "bundle_name",
#             "bundle_price",
#             "quantity"
#         ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # FULL PRODUCT DETAILS

    bundle = serializers.SerializerMethodField()  # FULL BUNDLE DETAILS

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "bundle",
            "quantity",
        ]

    def get_bundle(self, obj):
        if obj.bundle:
            return {
                "id": obj.bundle.id,
                "name": obj.bundle.name,
                "price": obj.bundle.price,
                "image": obj.bundle.image.url if obj.bundle.image else None
            }
        return None


from .models import Rental

class RentalSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.model_name", read_only=True)

    class Meta:
        model = Rental
        fields = "__all__"
        read_only_fields = ["start_date", "end_date", "is_active"]



from django.contrib.auth import get_user_model

User = get_user_model()

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


from django.contrib.auth import get_user_model

User = get_user_model()

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "date_joined"]




# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ["id", "product", "bundle", "quantity"]


# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True, read_only=True)

#     class Meta:
#         model = Order
#         fields = [
#             "id",
#             "user",
#             "total_amount",
#             "stripe_payment_intent",
#             "status",
#             "created_at",
#             "items"
#         ]



#10/12/2025

from rest_framework import serializers
from .models import HostingRequest

class HostingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostingRequest
        fields = "__all__"


class UserOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.model_name", read_only=True)
    bundle_name = serializers.CharField(source="bundle.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "bundle",
            "bundle_name",
            "quantity",
        ]


class UserOrderSerializer(serializers.ModelSerializer):
    items = UserOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_amount",
            "delivery_address",
            "stripe_payment_intent",
            "created_at",
            "items",
        ]



