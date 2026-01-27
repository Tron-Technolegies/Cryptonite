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



from .models import CartItem, Invoice, Order, OrderItem
from AdminApp.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'



from .models import CartItem

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
    calculated_fee = serializers.SerializerMethodField()
    invoice_id = serializers.SerializerMethodField()

    class Meta:
        model = Rental
        fields = "__all__"
        read_only_fields = ["start_date", "end_date", "is_active"]
    
    def get_calculated_fee(self, obj):
        try:
            return obj.calculate_rental_fee()
        except Exception:
            return None
    def get_invoice_id(self, obj):
        invoice = Invoice.objects.filter(
            user=obj.user,              # 🔐 IMPORTANT
            purchase_type="rent",
            related_id=obj.id
        ).first()
        return invoice.id if invoice else None

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




from rest_framework import serializers
from .models import HostingRequest

class HostingRequestSerializer(serializers.ModelSerializer):
    hosting_location_display = serializers.CharField(source="get_hosting_location_display",read_only=True)
    invoice_id = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)
    
    class Meta:
        model = HostingRequest
        fields = "__all__"
   
    def get_invoice_id(self, obj):
        invoice = Invoice.objects.filter(
            user=obj.user,
            purchase_type="hosting",
            related_id=obj.id
        ).first()
        return invoice.id if invoice else None

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
    invoice_id = serializers.SerializerMethodField()

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
            "invoice_id"
        ]
    def get_invoice_id(self, obj):
        invoice = Invoice.objects.filter(
            user=obj.user,              # 🔐 IMPORTANT
            purchase_type="buy",
            related_id=obj.id
        ).first()
        return invoice.id if invoice else None



class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "purchase_type",
            "amount",
            "currency",
            "created_at",
        ]


from rest_framework import serializers
from .models import ProductReview


class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = "__all__"
        read_only_fields = ("user", "product")

    def get_user_name(self, obj):
        return obj.user.username if obj.user else None


from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            # Do NOT reveal user existence
            raise serializers.ValidationError(
                "If this email exists, a verification link will be sent."
            )

        if user.is_active:
            raise serializers.ValidationError("User is already verified.")

        self.context["user"] = user
        return value
