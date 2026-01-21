from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken


from .serializers import HostingRequestSerializer, InvoiceSerializer, RegisterSerializer, UserOrderSerializer
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
        verification_link = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"

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

        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"

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
from AdminApp.models import Blog, Product

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
from .models import CartItem, HostingRequest
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


from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from AdminApp.models import Product
from .models import Rental
from .serializers import RentalSerializer
from decimal import Decimal

class RentMinerView(generics.CreateAPIView):
    serializer_class = RentalSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        duration_days = request.data.get("duration_days", 30)
        amount_paid = request.data.get("amount_paid")  # Now optional

        # 1. Get product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        # 2. Validate duration
        try:
            duration_days = int(duration_days)
            if duration_days not in [30, 60, 90, 180, 365]:  # Optional: restrict allowed durations
                return Response({"error": "Allowed durations: 30, 60, 90, 180, or 365 days"}, status=400)
        except ValueError:
            return Response({"error": "Invalid duration_days"}, status=400)

        # 3. Calculate end date
        end_date = timezone.now() + timedelta(days=duration_days)

        # 4. Calculate correct rental fee
        temp_rental = Rental(product=product, duration_days=duration_days)
        try:
            required_amount = temp_rental.calculate_rental_fee()
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        # 5. Validate payment (if user sent amount_paid)
        if amount_paid is not None:
            try:
                amount_paid = Decimal(str(amount_paid))  # str() fixes float issues
                if amount_paid < required_amount:
                    return Response({
                        "error": "Insufficient payment",
                        "required": float(required_amount),
                        "received": float(amount_paid)
                    }, status=400)
            except:
                return Response({"error": "Invalid amount_paid format"}, status=400)
        else:
            amount_paid = required_amount  # Auto-fill correct amount

        # 6. Create rental
        rental = Rental.objects.create(
            user=request.user,
            product=product,
            duration_days=duration_days,
            amount_paid=amount_paid,
            end_date=end_date,
            is_active=True
        )

        return Response({
            "message": "Miner rented successfully!",
            "rental_id": rental.id,
            "required_amount": float(required_amount),
            "amount_paid": float(amount_paid),
            "duration_days": duration_days,
            "end_date": end_date.isoformat(),
            "daily_cost": float(required_amount / duration_days)
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
from AdminApp.serializers import BlogSerializer, BundleOfferSerializer


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
from .utils import calculate_cart_total, calculate_rent_total
from decimal import Decimal
from .utils import calculate_cart_total
from .models import HostingRequest

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        purchase_type = request.data.get("purchase_type")  # buy / rent / hosting

        if purchase_type not in ["buy", "rent", "hosting"]:
            return Response(
                {"error": "purchase_type must be 'buy', 'rent', or 'hosting'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------
        # BUY 
        # -------------------------------
        if purchase_type == "buy":
            total_price, cart_items = calculate_cart_total(user)

            if not cart_items.exists():
                return Response({"error": "Cart is empty"}, status=400)
        # -------------------------------
        # RENT 
        # -------------------------------
        if purchase_type == "rent":
            duration_days = int(request.data.get("duration_days", 30))

            # UPDATED: unpack total + snapshot correctly
            total_price, rent_snapshot = calculate_rent_total(
                user=user,
                duration_days=duration_days
            )

            if total_price <= 0:
                return Response({"error": "Cart is empty"}, status=400)

        # -------------------------------
        # HOSTING
        # -------------------------------
        if purchase_type == "hosting":
            hosting_request_id = request.data.get("hosting_request_id")

            if not hosting_request_id:
                return Response(
                    {"error": "hosting_request_id is required for hosting"},
                    status=400
                )

            hosting_request = HostingRequest.objects.get(
                id=hosting_request_id,
                user=user,
                is_paid=False
            )

            total_price = hosting_request.total_amount

        # -------------------------------
        # BUY → address required
        # -------------------------------
        metadata = {
            "user_id": str(user.id),
            "purchase_type": purchase_type,
        }

        if purchase_type == "buy":
            address = request.data.get("address")
            save_address = request.data.get("save_address", False)

            if not address:
                return Response(
                    {"error": "Address is required for purchase_type='buy'"},
                    status=400
                )

            if save_address:
                user.shipping_address = address
                user.save()

            metadata.update({
                "name": address.get("name", ""),
                "line1": address.get("line1", ""),
                "city": address.get("city", ""),
                "state": address.get("state", ""),
                "postal_code": address.get("postal_code", ""),
                "country": address.get("country", ""),
            })

        # -------------------------------
        # RENT → duration required
        # -------------------------------
        if purchase_type == "rent":
            metadata["duration_days"] = str(duration_days)
        # -------------------------------
        # HOSTING metadata
        # -------------------------------
        if purchase_type == "hosting":
            metadata.update({
                "hosting_request_id": str(hosting_request.id),
                "hosting_location": hosting_request.hosting_location,
                "setup_fee": str(hosting_request.setup_fee),
            })

        # -------------------------------
        # Stripe PaymentIntent
        # -------------------------------
        amount_in_cents = int(Decimal(total_price) * 100)

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



import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import (
    CartItem,
    Order,
    OrderItem,
    Rental,
    HostingRequest,
    Invoice,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        # We only care about successful payments
        if event["type"] != "payment_intent.succeeded":
            return Response(status=200)

        intent = event["data"]["object"]
        metadata = intent.get("metadata", {})

        # 🔐 DUPLICATE PROTECTION (VERY IMPORTANT)
        if Invoice.objects.filter(stripe_payment_intent=intent["id"]).exists():
            return Response(status=200)

        user_id = metadata.get("user_id")
        purchase_type = metadata.get("purchase_type")

        if not user_id or not purchase_type:
            return Response(status=200)

        User = get_user_model()
        user = User.objects.get(id=user_id)

        # =====================================================
        # BUY
        # =====================================================
        if purchase_type == "buy":
            cart_items = CartItem.objects.filter(user=user)
            if not cart_items.exists():
                return Response(status=200)

            total_price = sum(
                (ci.product.price if ci.product else ci.bundle.price) * ci.quantity
                for ci in cart_items
            )

            order = Order.objects.create(
                user=user,
                total_amount=total_price,
                stripe_payment_intent=intent["id"],
                status="completed",
                delivery_address={
                    "name": metadata.get("name"),
                    "line1": metadata.get("line1"),
                    "city": metadata.get("city"),
                    "state": metadata.get("state"),
                    "postal_code": metadata.get("postal_code"),
                    "country": metadata.get("country"),
                },
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    bundle=item.bundle,
                    quantity=item.quantity,
                )

            # 🧾 INVOICE (BUY)
            Invoice.objects.create(
                user=user,
                invoice_number=f"INV-BUY-{order.id}",
                purchase_type="buy",
                related_id=order.id,
                amount=order.total_amount,
                currency="USD",
                stripe_payment_intent=intent["id"],
                invoice_data={
                    "items": [
                        {
                            "title": (
                                item.product.model_name
                                if item.product else item.bundle.name
                            ),
                            "quantity": item.quantity,
                            "unit_price": str(
                                item.product.price if item.product else item.bundle.price
                            ),
                            "total_price": str(
                                (item.product.price if item.product else item.bundle.price)
                                * item.quantity
                            ),
                        }
                        for item in cart_items
                    ],
                    "delivery_address": order.delivery_address,
                },
            )

            cart_items.delete()

        # =====================================================
        # RENT
        # =====================================================

        elif purchase_type == "rent":
            duration_days = int(metadata.get("duration_days", 30))
            cart_items = CartItem.objects.filter(user=user)

            rentals = []

            for item in cart_items:

                # PRODUCT RENT
                if item.product:
                    temp_rental = Rental(
                        user=user,
                        product=item.product,
                        duration_days=duration_days,
                        end_date=timezone.now()
                    )
                    amount = temp_rental.calculate_rental_fee()

                    rental = Rental.objects.create(
                        user=user,
                        product=item.product,
                        duration_days=duration_days,
                        amount_paid=amount,
                        end_date=timezone.now() + timezone.timedelta(days=duration_days),
                    )
                    rentals.append(rental)

                # BUNDLE RENT
                elif item.bundle:
                    amount = item.bundle.price * item.quantity

                    rental = Rental.objects.create(
                        user=user,
                        bundle=item.bundle,
                        duration_days=duration_days,
                        amount_paid=amount,
                        end_date=timezone.now() + timezone.timedelta(days=duration_days),
                    )
                    rentals.append(rental)


            # 🧾 INVOICE (RENT)
            if rentals:
                Invoice.objects.create(
                    user=user,
                    invoice_number=f"INV-RENT-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    purchase_type="rent",
                    # related_id=rentals[0].id,  # ✅ SAFE
                    related_id=None,
                    amount=sum(r.amount_paid for r in rentals),
                    currency="USD",
                    stripe_payment_intent=intent["id"],
                    invoice_data={
                        "rentals": [
                            {
                                "item": (
                                    r.product.model_name
                                    if r.product
                                    else r.bundle.name
                                ),
                                "duration_days": r.duration_days,
                                "amount": str(r.amount_paid),
                                "end_date": str(r.end_date),
                            }
                            for r in rentals
                        ]
                    },
                )

            cart_items.delete()

        # =====================================================
        # HOSTING
        # =====================================================
        elif purchase_type == "hosting":
            hosting_request_id = metadata.get("hosting_request_id")

            hosting_request = HostingRequest.objects.get(
                id=hosting_request_id,
                user=user
            )

            if hosting_request.is_paid:
                return Response(status=200)

            hosting_request.is_paid = True
            hosting_request.payment_reference = intent["id"]
            hosting_request.status = "paid"
            hosting_request.save()

            # 🧾 INVOICE (HOSTING)
            Invoice.objects.create(
                user=user,
                invoice_number=f"INV-HOST-{hosting_request.id}",
                purchase_type="hosting",
                related_id=hosting_request.id,
                amount=hosting_request.total_amount,
                currency="USD",
                stripe_payment_intent=intent["id"],
                invoice_data={
                    "items": hosting_request.items,
                    "setup_fee": str(hosting_request.setup_fee),
                    "hosting_location": hosting_request.hosting_location,
                },
            )

            CartItem.objects.filter(user=user).delete()

        return Response(status=200)


# ---------------- CHECKOUT -----------------
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


# ---------------- HOSTING REQUEST -----------------
SETUP_FEE_PER_DEVICE = 1150

class CreateHostingRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        phone = request.data.get("phone")
        message = request.data.get("message", "")
        hosting_location = request.data.get("hosting_location")

        if not phone:
            return Response({"error": "phone is required"}, status=400)

        if hosting_location not in ["US", "ET", "UAE"]:
            return Response({"error": "Invalid hosting location"}, status=400)

        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        snapshot = []
        items_total = 0
        total_devices = 0 

        for cart_item in cart_items:
            if cart_item.product:
                price = cart_item.product.price * cart_item.quantity
                items_total += price
                total_devices += cart_item.quantity

                snapshot.append({
                    "type": "product",
                    "id": cart_item.product.id,
                    "title": cart_item.product.model_name,
                    "quantity": cart_item.quantity,
                    "unit_price": str(cart_item.product.price),
                    "total_price": str(price)
                })

            elif cart_item.bundle:
                price = cart_item.bundle.price * cart_item.quantity
                items_total += price
                total_devices += cart_item.quantity

                snapshot.append({
                    "type": "bundle",
                    "id": cart_item.bundle.id,
                    "title": cart_item.bundle.name,
                    "quantity": cart_item.quantity,
                    "unit_price": str(cart_item.bundle.price),
                    "total_price": str(price)
                })
        setup_fee = SETUP_FEE_PER_DEVICE * total_devices
        total_amount = items_total + setup_fee

        hosting_request = HostingRequest.objects.create(
            user=user,
            phone=phone,
            message=message,
            hosting_location=hosting_location,
            items=snapshot,
            setup_fee=setup_fee,
            total_amount=total_amount,
            is_paid=False
        )

        # ⚠️ DO NOT clear cart yet
        # Clear only after payment success

        return Response({
            "message": "Hosting request created. Proceed to payment.",
            "hosting_request_id": hosting_request.id,
            "items_total": items_total,
            "setup_fee": setup_fee,       
            "total_devices": total_devices,
            "total_amount": total_amount
        }, status=201)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
import requests
import traceback
import requests
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

WHAT_TO_MINE_URL = "https://whattomine.com/asic.json"
CACHE_KEY = "asic_profitability_raw"
CACHE_TTL = 900  # 15 minutes

@api_view(["GET"])
def asic_profitability(request):
    try:
        # Check cache
        cached_data = cache.get(CACHE_KEY)
        if cached_data:
            return Response({
                "live": False,
                "cached": True,
                "source": "whattomine.com",
                "data": cached_data
            })

        # Fetch external API
        r = requests.get(
            WHAT_TO_MINE_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
        r.raise_for_status()

        data = r.json()  # FULL response

        # Cache full response
        cache.set(CACHE_KEY, data, CACHE_TTL)

        return Response({
            "live": True,
            "cached": False,
            "source": "whattomine.com",
            "data": data
        })

    except requests.exceptions.RequestException as e:
        return Response(
            {
                "status": "error",
                "message": "Failed to fetch data from WhatToMine",
                "details": str(e)
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")
        .prefetch_related("items", "items__product", "items__bundle")
    )

    serializer = UserOrderSerializer(orders, many=True)
    return Response(serializer.data, status=200)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_rentals(request):
    print("Logged in user:", request.user.id, request.user.email)

    rentals = (
        Rental.objects
        .filter(user=request.user)
        .select_related("product")
        .order_by("-start_date")
    )

    serializer = RentalSerializer(rentals, many=True)
    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_hosting_requests(request):
    requests = (
        HostingRequest.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    serializer = HostingRequestSerializer(requests, many=True)
    return Response(serializer.data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_invoices(request):
    invoices = (
        Invoice.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )
    serializer = InvoiceSerializer(invoices, many=True)
    return Response(serializer.data)

from reportlab.pdfgen import canvas


from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from .models import Invoice

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_invoice(request, id):
    invoice = get_object_or_404(
        Invoice,
        id=id,
        user=request.user
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{invoice.invoice_number}.pdf"'
    )

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    BRAND = colors.HexColor("#00c336")

    # ================= HEADER =================
    p.setFillColor(BRAND)
    p.setFont("Helvetica-Bold", 22)
    p.drawString(40, height - 50, "CRYPTONITE")

    p.setFont("Helvetica", 11)
    p.setFillColor(colors.black)
    p.drawRightString(
        width - 40,
        height - 50,
        "INVOICE"
    )

    p.setStrokeColor(BRAND)
    p.setLineWidth(3)
    p.line(40, height - 65, width - 40, height - 65)

    # ================= META =================
    y = height - 110
    p.setFont("Helvetica", 10)

    meta = [
        ("Invoice No", invoice.invoice_number),
        ("Date", invoice.created_at.strftime("%d %b %Y")),
        ("Customer", invoice.user.username),
        ("Type", invoice.purchase_type.upper()),
    ]

    for label, value in meta:
        p.drawString(40, y, f"{label}:")
        p.setFont("Helvetica-Bold", 10)
        p.drawString(120, y, str(value))
        p.setFont("Helvetica", 10)
        y -= 18

    # ================= TABLE HEADER =================
    y -= 10
    p.setFillColor(BRAND)
    p.rect(40, y, width - 80, 22, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 10)

    headers = ["ITEM", "QTY", "UNIT PRICE", "TOTAL"]
    x_positions = [45, 300, 360, 460]

    for header, x in zip(headers, x_positions):
        p.drawString(x, y + 6, header)

    # ================= TABLE ROWS =================
    p.setFillColor(colors.black)
    p.setFont("Helvetica", 10)

    y -= 22

    for item in invoice.invoice_data.get("items", []):
        p.drawString(45, y, item["title"][:40])
        p.drawRightString(320, y, str(item["quantity"]))
        p.drawRightString(420, y, item["unit_price"])
        p.drawRightString(540, y, item["total_price"])
        y -= 18

    # ================= TOTAL =================
    y -= 10
    p.setStrokeColor(BRAND)
    p.line(360, y, width - 40, y)

    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(
        width - 40,
        y - 20,
        f"TOTAL: {invoice.amount} {invoice.currency}"
    )

    # ================= FOOTER =================
    p.setFont("Helvetica", 9)
    p.setFillColor(colors.grey)
    p.drawCentredString(
        width / 2,
        40,
        "This is a system-generated invoice. Payment confirmed."
    )

    p.showPage()
    p.save()

    return response





@api_view(["GET"])
def list_blogs(request):
    blogs = Blog.objects.filter(is_published=True).order_by("-created_at")
    serializer = BlogSerializer(blogs, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, is_published=True)
    serializer = BlogSerializer(blog)
    return Response(serializer.data)


from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from AdminApp.models import Events
from AdminApp.serializers import EventsSerializer

@api_view(["GET"])
def list_events(request):
    events = Events.objects.filter(is_published=True).order_by("-created_at")
    serializer = EventsSerializer(events, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def event_detail(request, slug):
    event = get_object_or_404(Events, slug=slug, is_published=True)
    serializer = EventsSerializer(event)
    return Response(serializer.data)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import ProductReview
from AdminApp.models import Product
from .serializers import ProductReviewSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # prevent duplicate review
    if ProductReview.objects.filter(product=product, user=request.user).exists():
        return Response(
            {"error": "You have already reviewed this product"},
            status=400
        )

    serializer = ProductReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, product=product)
        reviews = ProductReview.objects.filter(product=product)
        product.review_count = reviews.count()
        product.average_rating = round(
            sum(r.rating for r in reviews) / product.review_count, 1
        )
        product.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(["GET"])
def list_product_reviews(request, product_id):
    reviews = ProductReview.objects.filter(product_id=product_id).order_by("-created_at")
    serializer = ProductReviewSerializer(reviews, many=True)
    return Response(serializer.data)
