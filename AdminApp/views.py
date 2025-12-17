# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from AdminApp.models import Product
from .serializers import ProductSerializer

# ---------- CREATE PRODUCT ----------

# @api_view(['POST'])
# @permission_classes([permissions.IsAdminUser])
# def create_product(request):
#     serializer = ProductSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .serializers import ProductSerializer


@api_view(["POST"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def add_product(request):
    """
    Admin: Add a new product with image upload (Cloudinary)
    """
    serializer = ProductSerializer(data=request.data)

    if serializer.is_valid():
        product = serializer.save()   # Cloudinary upload happens here
        return Response(
            {
                "message": "Product added successfully",
                "product": ProductSerializer(product).data
            },
            status=status.HTTP_201_CREATED
        )

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
# @api_view(['PUT', 'PATCH'])
# @permission_classes([permissions.IsAdminUser])
# def update_product(request, id):
#     try:
#         product = Product.objects.get(id=id)
#     except Product.DoesNotExist:
#         return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

#     serializer = ProductSerializer(product, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import get_object_or_404


@api_view(["PUT", "PATCH"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def update_product(request, id):
    """
    Admin: Update product details (image optional)
    """
    product = get_object_or_404(Product, id=id)

    serializer = ProductSerializer(
        product,
        data=request.data,
        partial=True   # Allows updating only required fields
    )

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Product updated successfully",
                "product": serializer.data
            },
            status=status.HTTP_200_OK
        )

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


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import BundleOffer
from .serializers import BundleOfferSerializer



import pandas as pd
import requests

from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import Product
from .serializers import ProductBulkUploadSerializer, ProductSerializer
@api_view(["POST"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def bulk_upload_products(request):
    """
    Admin bulk upload products using Excel
    """
    serializer = ProductBulkUploadSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    excel_file = serializer.validated_data["file"]

    try:
        df = pd.read_excel(excel_file)
    except Exception:
        return Response(
            {"error": "Invalid Excel file"},
            status=status.HTTP_400_BAD_REQUEST
        )

    created_count = 0
    updated_count = 0
    failed_rows = []

    for index, row in df.iterrows():
        try:
            model_name = str(row["model_name"]).strip()

            product, created = Product.objects.get_or_create(
                model_name=model_name
            )

            data = {
                "model_name": model_name, 
                "description": row.get("description"),
                # "product_details": row.get("product_details"),
                "minable_coins": row.get("minable_coins"),
                "hashrate": row.get("hashrate"),
                "power": row.get("power"),
                "algorithm": row.get("algorithm"),
                "price": row.get("price"),
                "category": row.get("category"),
                "brand": row.get("brand"),
                "efficiency": row.get("efficiency"),
                "noise": row.get("noise"),
                "delivery_type": row.get("delivery_type", "spot"),
                "delivery_date": row.get("delivery_date"),
                "is_available": str(row.get("is_available", "yes")).lower() == "yes",
            }

            product_serializer = ProductSerializer(
                product,
                data=data,
                partial=True
            )

            if product_serializer.is_valid():
                product_serializer.save()

                # ---- IMAGE (optional via URL) ----
                image_url = row.get("image_url")
                if image_url and isinstance(image_url, str):
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        product.image.save(
                            f"{model_name}.jpg",
                            ContentFile(response.content),
                            save=True
                        )

                if created:
                    created_count += 1
                else:
                    updated_count += 1
            else:
                failed_rows.append({
                    "row": index + 2,
                    "errors": product_serializer.errors
                })

        except Exception as e:
            failed_rows.append({
                "row": index + 2,
                "error": str(e)
            })

    return Response({
        "message": "Bulk upload finished",
        "created": created_count,
        "updated": updated_count,
        "failed_rows": failed_rows
    }, status=status.HTTP_200_OK)













# ---------- CREATE BUNDLE ----------
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_bundle_offer(request):
    serializer = BundleOfferSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- GET ALL BUNDLES ----------
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_bundle_offers(request):
    bundles = BundleOffer.objects.all().order_by('-created_at')
    serializer = BundleOfferSerializer(bundles, many=True)
    return Response(serializer.data)


# ---------- GET SINGLE BUNDLE ----------
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_bundle_offer(request, id):
    try:
        bundle = BundleOffer.objects.get(id=id)
    except BundleOffer.DoesNotExist:
        return Response({"error": "Bundle not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = BundleOfferSerializer(bundle)
    return Response(serializer.data)


# ---------- UPDATE BUNDLE ----------
@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAdminUser])
def update_bundle_offer(request, id):
    try:
        bundle = BundleOffer.objects.get(id=id)
    except BundleOffer.DoesNotExist:
        return Response({"error": "Bundle not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = BundleOfferSerializer(bundle, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------- DELETE BUNDLE ----------
@api_view(['DELETE'])
@permission_classes([permissions.IsAdminUser])
def delete_bundle_offer(request, id):
    try:
        bundle = BundleOffer.objects.get(id=id)
    except BundleOffer.DoesNotExist:
        return Response({"error": "Bundle not found"}, status=status.HTTP_404_NOT_FOUND)

    bundle.delete()
    return Response({"message": "Bundle deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# ---------- GET ALL RENTAL ORDERS ----------
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from UserApp.models import Rental
from UserApp.serializers import RentalSerializer

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


# ---------- Update Hosting Request ----------

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
