from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken


from .serializers import RegisterSerializer
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


# ---------- Register ----------

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=False)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"http://localhost:5175/verify-email/{uid}/{token}"

        send_mail(
            subject="Verify your Cryptonite account",
            message=f"Hi {user.username}, please verify your email by clicking here: {verification_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

# ---------- verification endpoint  ----------

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid verification link"}, status=400)

        if user.is_active:
            return Response({"detail": "User already verified."}, status=200)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            # automatically issue tokens (auto login)
            refresh = RefreshToken.for_user(user)
            return Response({
                "detail": "Email verified successfully.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {"id": user.id, "email": user.email, "username": user.username}
            })
        else:
            return Response({"detail": "Invalid or expired token."}, status=400)

# ---------- Login by email ----------
class EmailTokenObtainView(APIView):
    """
    POST: { "email": "user@example.com", "password": "secret" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response(
                {"detail": "Email and password required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid credentials."}, status=401)

        user = authenticate(request, username=user_obj.username, password=password)
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {"id": user.id, "username": user.username, "email": user.email},
            }
        )


from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.conf import settings

# ---------------- FORGOT PASSWORD -----------------
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email is required."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=404)

        token_generator = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        # Example reset URL — your frontend will handle this page
        reset_link = f"http://localhost:3000/reset-password/{uid}/{token}"

        # Send email (for now, console output)
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"detail": "Password reset link sent to email."})
    

# ---------------- RESET PASSWORD -----------------
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        password = request.data.get("password")
        password2 = request.data.get("password2")

        if not password or not password2:
            return Response({"detail": "Both password fields are required."}, status=400)
        if password != password2:
            return Response({"detail": "Passwords do not match."}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid link."}, status=400)

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=400)

        user.set_password(password)
        user.save()

        return Response({"detail": "Password reset successful."})
    


# ---------------- LOGOUT -----------------
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.permissions import IsAuthenticated

class LogoutView(APIView):
    """
    Logout by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]   #allowAny if you want to logout even if access token is expired

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=205)
        except KeyError:
            return Response({"detail": "Refresh token required."}, status=400)
        except TokenError:
            return Response({"detail": "Invalid or expired token."}, status=400)


# ---------------- VIEW PPRODUCTS -----------------

from rest_framework import generics
from .serializers import ProductSerializer, CartItemSerializer
from AdminApp.models import Product

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    permission_classes = []


# ---------------- VIEW SINGLE PRODUCT -----------------
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
    permission_classes = []



# ----------------ADD TO CART (PRODUCT & BUNDLE) -----------------
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import CartItem
from AdminApp.models import BundleOffer

class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        bundle_id = request.data.get("bundle_id")   #new
        quantity = int(request.data.get("quantity", 1))

        if not product_id and not bundle_id: #new
            return Response({"error": "Provide either product_id or bundle_id"}, status=400)

        if product_id: 
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product
            )
        elif bundle_id:
            try:
                bundle = BundleOffer.objects.get(id=bundle_id)
            except BundleOffer.DoesNotExist:
                return Response({"error": "Bundle not found"}, status=404)

            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                bundle=bundle,
                product=None  # ensures it's bundle cart
            )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()
        return Response({"message": "Added to cart"}, status=status.HTTP_200_OK)



# ---------------- VIEW CART -----------------
class CartListView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


# ---------------- UPDATE CART -----------------

class UpdateCartView(generics.UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


# ---------------- REMOVE FROM CART -----------------
class RemoveFromCartView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    

# ---------------- CART TOTAL -----------------

class CartTotalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cart_items = CartItem.objects.filter(user=request.user)

        total_price = 0

        for item in cart_items:
            if item.product:
                total_price += float(item.product.price) * item.quantity
            elif item.bundle:
                total_price += float(item.bundle.price) * item.quantity

        return Response({"total_price": total_price})



# ---------------- RENT MINER -----------------

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, timedelta, timezone
from AdminApp.models import Product
from .models import Rental
from .serializers import RentalSerializer

class RentMinerView(generics.CreateAPIView):
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        duration = int(request.data.get("duration_days", 30))
        amount = request.data.get("amount_paid")

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        end_date = datetime.now() + timedelta(days=duration)

        rental = Rental.objects.create(
            user=request.user,
            product=product,
            duration_days=duration,
            amount_paid=amount,
            end_date=end_date
        )

        return Response({
            "message": "Miner rented successfully",
            "rental_id": rental.id,
            "end_date": rental.end_date
        }, status=201)


# ---------------- LIST OF ACTIVE RENTALS -----------------

class UserActiveRentalsView(generics.ListAPIView):
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rental.objects.filter(user=self.request.user, is_active=True)



# ---------------- LIST OF PAST RENTALS -----------------


class UserPastRentalsView(generics.ListAPIView):
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rental.objects.filter(user=self.request.user, is_active=False)


def mark_expired_rentals():
    now = datetime.now()
    rentals = Rental.objects.filter(end_date__lt=now, is_active=True)
    for rental in rentals:
        rental.is_active = False
        rental.save()


# ---------------- GET USER INFO -----------------

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import UserInfoSerializer

class GetUserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserInfoSerializer(user)
        return Response(serializer.data)


# ---------------- VIEW ALL BUNDLE OFFERS -----------------

from AdminApp.models import BundleOffer
from AdminApp.serializers import BundleOfferSerializer


class BundleOfferListView(generics.ListAPIView):
    queryset = BundleOffer.objects.all().order_by('-created_at')
    serializer_class = BundleOfferSerializer
    permission_classes = [AllowAny]


# ---------------- VIEW SINGLE BUNDLE OFFER -----------------

class BundleOfferDetailView(generics.RetrieveAPIView):
    queryset = BundleOffer.objects.all()
    serializer_class = BundleOfferSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'



# ---------------- PAYMENT INTENT CREATION -----------------

import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .utils import calculate_cart_total

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        purchase_type = request.data.get("purchase_type")  # "buy" or "rent"

        if purchase_type not in ["buy", "rent"]:
            return Response({"error": "purchase_type must be 'buy' or 'rent'"},
                            status=status.HTTP_400_BAD_REQUEST)

        # 1) Calculate total
        total_price, cart_items = calculate_cart_total(user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        # 2) BUY → address required
        address = None
        save_address = False

        if purchase_type == "buy":
            address = request.data.get("address")
            save_address = request.data.get("save_address", False)

            if not address:
                return Response({"error": "Address is required for purchase_type='buy'"},
                                status=status.HTTP_400_BAD_REQUEST)

            if save_address:
                user.shipping_address = address
                user.save()

        # 3) RENT → duration required
        duration_days = None
        if purchase_type == "rent":
            duration_days = request.data.get("duration_days", 30)
            try:
                duration_days = int(duration_days)
            except ValueError:
                return Response({"error": "duration_days must be an integer"},
                                status=status.HTTP_400_BAD_REQUEST)

        # 4) Stripe needs amount in cents
        amount_in_cents = int(total_price * 100)

        # 5) Build metadata for webhook
        metadata = {
            "user_id": str(user.id),
            "purchase_type": purchase_type,
        }

        if purchase_type == "rent":
            metadata["duration_days"] = str(duration_days)

        if purchase_type == "buy":
            metadata.update({
                "name": address.get("name", ""),
                "line1": address.get("line1", ""),
                "city": address.get("city", ""),
                "state": address.get("state", ""),
                "postal_code": address.get("postal_code", ""),
                "country": address.get("country", ""),
            })

        # 6) Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="usd",
            metadata=metadata,
        )

        return Response({
            "client_secret": intent.client_secret,
            "amount": total_price,
            "currency": "usd"
        })



# ---------------- STRIPE WEBHOOK -----------------
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
import stripe

from django.contrib.auth import get_user_model
from .models import CartItem, Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY

@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = []

    def post(self, request):
        print("\n🔔 Webhook received")

        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=webhook_secret,
            )
            event_type = event["type"]
            print(f"✅ Event verified: {event_type}")
        except Exception as e:
            print("❌ Verification failed:", e)
            return Response({"error": str(e)}, status=400)

        if event_type == "payment_intent.succeeded":
            print("🎉 payment_intent.succeeded received")

            intent = event["data"]["object"]
            metadata = intent.get("metadata", {}) or {}

            user_id = metadata.get("user_id")
            purchase_type = metadata.get("purchase_type")

            if not user_id or not purchase_type:
                print("⚠ Missing metadata")
                return Response(status=200)

            User = get_user_model()
            user = User.objects.get(id=user_id)

            cart_items = CartItem.objects.filter(user=user)
            if not cart_items.exists():
                print("⚠ Cart empty")
                return Response(status=200)

            total_price = sum(
                (float(ci.product.price) if ci.product else float(ci.bundle.combo_price)) * ci.quantity
                for ci in cart_items
            )

            if purchase_type == "buy":
                delivery_address = {
                    "name": metadata.get("name"),
                    "line1": metadata.get("line1"),
                    "city": metadata.get("city"),
                    "state": metadata.get("state"),
                    "postal_code": metadata.get("postal_code"),
                    "country": metadata.get("country"),
                }

                order = Order.objects.create(
                    user=user,
                    total_amount=total_price,
                    stripe_payment_intent=intent["id"],
                    status="completed",
                    delivery_address=delivery_address,
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        bundle=item.bundle,
                        quantity=item.quantity,
                    )

                print("🧾 Order created:", order.id)

            elif purchase_type == "rent":
                duration_days = int(metadata.get("duration_days", 30))

                for item in cart_items:
                    if item.product:  
                        amount = float(item.product.price) * item.quantity
                        end_date = timezone.now() + timezone.timedelta(days=duration_days)

                        rental = Rental.objects.create(
                            user=user,
                            product=item.product,
                            duration_days=duration_days,
                            amount_paid=amount,
                            end_date=end_date,
                        )

                        print("🛠 Rental created:", rental.id)

            cart_items.delete()
            print("🗑 Cart cleared")

        return Response(status=200)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CartItem
from .serializers import CartItemSerializer
from .utils import calculate_cart_total

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns checkout summary for frontend
        """
        total_price, cart_items = calculate_cart_total(request.user)
        serialized_items = CartItemSerializer(cart_items, many=True).data

        response = {
            "cart_items": serialized_items,
            "total_price": total_price,
            "price_breakup": {
                "subtotal": total_price,
                "tax": round(total_price * 0.05, 2),      # example 5%
                "final_total": round(total_price * 1.05, 2)
            },
            "can_buy": True,
            "can_rent": True,
            "user_default_address": None,  # add later when you store addresses
        }

        return Response(response)
