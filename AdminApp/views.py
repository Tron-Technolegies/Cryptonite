
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from AdminApp.models import BundleOffer, Product
from .serializers import BlogSerializer, BundleOfferSerializer, BundleOfferCreateSerializer, ProductUpdateSerializer 
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProductCreateSerializer
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProductCreateSerializer
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    BundleOfferCreateSerializer,
    AdminOrderSerializer,
   
)


# ----------CREATE PRODUCTS ----------
@api_view(["POST"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def create_product(request):
    serializer = ProductCreateSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------- GET ALL PRODUCTS ----------
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_products(request):
    products = Product.objects.all().order_by('-created_at')
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# ---------- GET SINGLE PRODUCT ----------
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_product(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


# ---------- UPDATE PRODUCT ----------

@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAdminUser])
def update_product(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductUpdateSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- DELETE PRODUCT ----------
@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_product(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    product.delete()
    return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# ---------- GET ALL RENTAL ORDERS ----------
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from UserApp.models import ProductReview, Rental
from UserApp.serializers import ProductReviewSerializer, RentalSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_all_rent_orders(request):
    rentals = Rental.objects.all().order_by('-start_date')
    serializer = RentalSerializer(rentals, many=True)
    return Response(serializer.data)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from django.contrib.auth import get_user_model
from UserApp.serializers import AdminUserListSerializer

User = get_user_model()

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_all_users(request):
    users = User.objects.all().order_by("-date_joined")
    serializer = AdminUserListSerializer(users, many=True)
    return Response(serializer.data)


#10/12/2025
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from UserApp.models import HostingRequest  # HostingRequest lives in UserApp
from UserApp.serializers import HostingRequestSerializer  # Serializer also in UserApp

# ---------- List All Hosting Requests ----------

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_get_all_hosting_requests(request):
    hosting_requests = HostingRequest.objects.all().order_by('-created_at')
    serializer = HostingRequestSerializer(hosting_requests, many=True)
    return Response(serializer.data)


# ---------- Get Single Hosting Request ----------

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_get_hosting_request(request, id):
    hosting = get_object_or_404(HostingRequest, id=id)
    serializer = HostingRequestSerializer(hosting)
    return Response(serializer.data)



# ---------- Update Hosting Request ----------

@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def admin_update_hosting_request(request, id):
    hosting = get_object_or_404(HostingRequest, id=id)

    status_value = request.data.get("status")
    admin_notes = request.data.get("admin_notes")
    monthly_fee = request.data.get("monthly_fee")
    contacted_at = request.data.get("contacted_at")
    activated_at = request.data.get("activated_at")

    if status_value:
        hosting.status = status_value

    if admin_notes is not None:
        hosting.admin_notes = admin_notes

    if monthly_fee is not None:
        hosting.monthly_fee = monthly_fee

    if contacted_at:
        hosting.contacted_at = contacted_at

    if activated_at:
        hosting.activated_at = activated_at

    hosting.save()

    return Response({
        "message": "Hosting request updated successfully",
        "data": HostingRequestSerializer(hosting).data
    })


# ---------- Delete Hosting Request ----------

@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def admin_delete_hosting_request(request, id):
    hosting = get_object_or_404(HostingRequest, id=id)
    hosting.delete()

    return Response({"message": "Hosting request deleted successfully"})


from UserApp.models import Order
from .serializers import AdminOrderSerializer

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_list_orders(request):
    orders = Order.objects.all().order_by("-created_at")
    serializer = AdminOrderSerializer(orders, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    serializer = AdminOrderSerializer(order)
    return Response(serializer.data, status=200)


@api_view(['PATCH'])
@permission_classes([permissions.IsAdminUser])
def admin_update_order_status(request, id):
    order = get_object_or_404(Order, id=id)

    new_status = request.data.get("status")

    # ✅ Best practice: read from model choices
    allowed_statuses = [choice[0] for choice in Order.STATUS_CHOICES]

    if new_status not in allowed_statuses:
        return Response(
            {"error": "Invalid status"},
            status=400
        )

    order.status = new_status
    order.save()

    return Response(
        {"message": "Order status updated successfully"},
        status=200
    )




import pandas as pd
import requests
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.db import transaction
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProductCreateSerializer


# ---------- HELPERS ----------
def clean_value(value):
    """
    Converts Excel NaN / empty cells into None
    """
    if pd.isna(value):
        return None
    value = str(value).strip()
    return None if value.lower() in ["nan", "null", ""] else value


# ---------- BULK UPLOAD ----------
@api_view(["POST"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def bulk_upload_products(request):
    if "file" not in request.FILES:
        return Response(
            {"error": "No file provided"},
            status=status.HTTP_400_BAD_REQUEST
        )

    file = request.FILES["file"]

    if not file.name.endswith((".xlsx", ".xls")):
        return Response(
            {"error": "Invalid file format. Upload .xlsx or .xls"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        df = pd.read_excel(file)

        # ---------- COLUMN MAPPING ----------
        column_mapping = {
            "Model Name": "model_name",
            "Description": "description",
            "Minable Coins": "minable_coins",
            "Hashrate": "hashrate",
            "Power": "power",
            "Algorithm": "algorithm",
            "Category": "category",
            "Price": "price",
            "Hosting Fee Per KW": "hosting_fee_per_kw",
            "Brand": "brand",
            "Efficiency": "efficiency",
            "Noise Level": "noise",
            "Delivery Type": "delivery_type",
            "Delivery Date": "delivery_date",
            "Is Available": "is_available",
            "Image URL": "image_url",
        }

        df = df.rename(columns=column_mapping)
        df.columns = df.columns.str.strip()

        # ---------- REQUIRED FIELDS ----------
        required_fields = [
            "model_name",
            "description",
            "minable_coins",
            "hashrate",
            "power",
            "algorithm",
            "category",
        ]

        success_count = 0
        error_count = 0
        errors = []

        # ---------- PROCESS ROWS ----------
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    product_data = {
                        "model_name": clean_value(row.get("model_name")),
                        "description": clean_value(row.get("description")),
                        "minable_coins": clean_value(row.get("minable_coins")),
                        "hashrate": clean_value(row.get("hashrate")),
                        "power": clean_value(row.get("power")),
                        "algorithm": clean_value(row.get("algorithm")),
                        "category": clean_value(row.get("category")),
                    }

                    # ---------- REQUIRED VALIDATION ----------
                    missing = [f for f in required_fields if not product_data.get(f)]
                    if missing:
                        error_count += 1
                        errors.append({
                            "row": index + 2,
                            "errors": f"Missing required fields: {missing}"
                        })
                        continue

                    # ---------- OPTIONAL FIELDS ----------
                    try:
                        if clean_value(row.get("price")):
                            product_data["price"] = Decimal(str(row["price"]))
                    except InvalidOperation:
                        pass

                    try:
                        if clean_value(row.get("hosting_fee_per_kw")):
                            product_data["hosting_fee_per_kw"] = Decimal(
                                str(row["hosting_fee_per_kw"])
                            )
                    except InvalidOperation:
                        pass

                    for field in ["brand", "efficiency", "noise", "delivery_type"]:
                        value = clean_value(row.get(field))
                        if value:
                            product_data[field] = value.lower() if field == "delivery_type" else value

                    if clean_value(row.get("delivery_date")):
                        try:
                            product_data["delivery_date"] = pd.to_datetime(
                                row["delivery_date"]
                            ).date()
                        except Exception:
                            pass

                    if "is_available" in row and not pd.isna(row["is_available"]):
                        product_data["is_available"] = bool(row["is_available"])

                    # ---------- IMAGE ----------
                    image_file = None
                    image_url = clean_value(row.get("image_url"))
                    if image_url:
                        try:
                            res = requests.get(image_url, timeout=10)
                            res.raise_for_status()
                            image_file = ContentFile(
                                res.content,
                                name=f"{product_data['model_name'].replace(' ', '_')}.jpg"
                            )
                        except Exception:
                            pass

                    # ---------- SAVE ----------
                    serializer = ProductCreateSerializer(data=product_data)
                    if serializer.is_valid():
                        product = serializer.save()
                        if image_file:
                            product.image = image_file
                            product.save()
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append({
                            "row": index + 2,
                            "errors": serializer.errors
                        })

            except Exception as e:
                error_count += 1
                errors.append({
                    "row": index + 2,
                    "errors": str(e)
                })

        return Response({
            "message": "Bulk upload completed",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"error": f"Failed to process file: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    

# ---------- CREATE BUNDLE ----------

import json
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import BundleOfferCreateSerializer, BundleOfferSerializer
from .models import Blog, BundleOffer
from .serializers import BundleOfferCreateSerializer



@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def create_bundle_offer(request):
    """
    Create a new bundle offer with items.
    Accepts form-data with JSON string for items field.
    """
    
    # Convert QueryDict to regular dict
    data = {}
    for key, value in request.data.items():
        if key != 'items':
            data[key] = value
    
    # Parse items JSON string
    raw_items = request.data.get("items")
    
    if not raw_items:
        return Response(
            {"items": ["This field is required."]},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Parse JSON string
        if isinstance(raw_items, str):
            data["items"] = json.loads(raw_items)
        elif isinstance(raw_items, list):
            data["items"] = raw_items
        else:
            data["items"] = raw_items
    except json.JSONDecodeError as e:
        return Response(
            {"items": [f"Invalid JSON format: {str(e)}"]},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate and create
    serializer = BundleOfferCreateSerializer(data=data)
    
    if serializer.is_valid():
        bundle = serializer.save()
        return Response(
            BundleOfferSerializer(bundle).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- GET ALL BUNDLES ----------

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def list_bundle_offers(request):
    """List all bundle offers"""
    bundles = BundleOffer.objects.all()
    serializer = BundleOfferSerializer(bundles, many=True)
    return Response(serializer.data)

# ---------- GET SINGLE BUNDLE ----------
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_bundle_offer(request, id):
    """Get a single bundle offer"""
    try:
        bundle = BundleOffer.objects.get(id=id)
    except BundleOffer.DoesNotExist:
        return Response(
            {"error": "Bundle not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = BundleOfferSerializer(bundle)
    return Response(serializer.data)


# ---------- UPDATE BUNDLE ----------

@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def update_bundle_offer(request, id):
    """Update a bundle offer"""
    try:
        bundle = BundleOffer.objects.get(id=id)
    except BundleOffer.DoesNotExist:
        return Response(
            {"error": "Bundle not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Convert QueryDict to regular dict
    data = {}
    for key, value in request.data.items():
        if key != 'items':
            data[key] = value
    
    # Parse items if provided
    raw_items = request.data.get("items")
    if raw_items:
        try:
            if isinstance(raw_items, str):
                data["items"] = json.loads(raw_items)
            else:
                data["items"] = raw_items
        except json.JSONDecodeError as e:
            return Response(
                {"items": [f"Invalid JSON format: {str(e)}"]},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Validate and update
    serializer = BundleOfferCreateSerializer(bundle, data=data, partial=(request.method == 'PATCH'))
    
    if serializer.is_valid():
        bundle = serializer.save()
        return Response(BundleOfferSerializer(bundle).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ---------- DELETE BUNDLE ----------

@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_bundle_offer(request, id):
    """Delete a bundle offer"""
    try:
        bundle = BundleOffer.objects.get(id=id)
    except BundleOffer.DoesNotExist:
        return Response(
            {"error": "Bundle not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    bundle.delete()
    return Response(
        {"message": "Bundle deleted successfully"},
        status=status.HTTP_204_NO_CONTENT
    )



from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from UserApp.models import HostingRequest


@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_activate_monitoring(request, id):
    hosting = get_object_or_404(HostingRequest, id=id)
    
    monitoring_type = request.data.get("monitoring_type")
    resend_email = request.data.get("resend_email", False)

    if monitoring_type not in ["internal", "external"]:
        return Response(
            {"monitoring_type": "Invalid monitoring type"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = hosting.user

    # Activate monitoring if not already activated
    activated_now = False
    if not hosting.monitoring_activated:
        hosting.monitoring_activated = True
        hosting.monitoring_type = monitoring_type
        hosting.save()
        activated_now = True

    # Block if already activated and not requesting resend
    if hosting.monitoring_activated and not activated_now and not resend_email:
        return Response(
            {"detail": "Already activated, resend_email=false"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Prepare email content based on monitoring type
    if hosting.monitoring_type == "internal":
        subject = "Your Cryptonite Mining Dashboard is Now Active"
        message = (
            f"Hi {user.username},\n\n"
            "Thank you for your purchase!\n\n"
            "Your mining dashboard is now active. You can now log in with the same "
            "user ID and password you used to purchase the miners.\n\n"
            f"Login here: {settings.FRONTEND_URL}/login\n\n"
            "Start monitoring your mining operations right away!\n\n"
            "Best regards,\n"
            "Team Cryptonite"
        )
    else:  # external
        subject = "Your Cryptonite Mining Monitoring Access Details"
        message = (
            f"Hi {user.username},\n\n"
            "Thank you for your purchase!\n\n"
            "You can now monitor your mining operations at the link below:\n\n"
            "Website: https://external-monitoring-placeholder.com\n"
            f"User ID: {user.username}\n"
            "Password: [To be provided separately]\n\n"
            "IMPORTANT: Please reset your password as soon as you log in for the first time.\n\n"
            "Best regards,\n"
            "Team Cryptonite"
        )

    # Send email
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return Response(
        {
            "monitoring_activated": hosting.monitoring_activated,
            "email_sent": True,
            "activated_now": activated_now,
            "resend_email": resend_email
        },
        status=status.HTTP_200_OK
    )



@api_view(["POST"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def create_blog(request):
    serializer = BlogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def update_blog(request, id):
    blog = get_object_or_404(Blog, id=id)
    serializer = BlogSerializer(blog, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

 
@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_blog(request, id):
    blog = get_object_or_404(Blog, id=id)
    blog.delete()
    return Response({"message": "Blog deleted"})
 

@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_list_blogs(request):
    blogs = Blog.objects.all().order_by("-created_at")
    serializer = BlogSerializer(blogs, many=True)
    return Response(serializer.data)


from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Events
from .serializers import EventsSerializer

@api_view(["POST"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def create_event(request):
    serializer = EventsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(["PUT", "PATCH"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def update_event(request, id):
    event = get_object_or_404(Events, id=id)
    serializer = EventsSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_event(request, id):
    event = get_object_or_404(Events, id=id)
    event.delete()
    return Response({"message": "Event deleted successfully"})

@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_list_events(request):
    events = Events.objects.all().order_by("-created_at")
    serializer = EventsSerializer(events, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_list_reviews(request):
    reviews = ProductReview.objects.all().order_by("-created_at")
    serializer = ProductReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_delete_review(request, id):
    review = get_object_or_404(ProductReview, id=id)
    product = review.product
    review.delete()
    reviews = ProductReview.objects.filter(product=product)

    if reviews.exists():
        product.review_count = reviews.count()
        product.average_rating = round(
            sum(r.rating for r in reviews) / product.review_count, 1
        )
    else:
        product.review_count = 0
        product.average_rating = 0

    product.save()

    return Response({"message": "Review deleted"})
