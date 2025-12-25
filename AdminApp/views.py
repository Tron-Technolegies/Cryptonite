# Create your views here.
# from turtle import pd
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from AdminApp.models import BundleOffer, Product
from .serializers import BundleOfferReadSerializer, BundleOfferCreateSerializer
# import pandas as pd
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

    serializer = ProductSerializer(product, data=request.data, partial=True)
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


from .serializers import BundleOfferCreateSerializer


# ---------- CREATE BUNDLE ----------
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def create_bundle_offer(request):
    serializer = BundleOfferCreateSerializer(data=request.data)

    if serializer.is_valid():
        bundle = serializer.save()
        return Response(
            BundleOfferReadSerializer(bundle).data,
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------- GET ALL BUNDLES ----------
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_bundle_offers(request):
    bundles = BundleOffer.objects.prefetch_related("items__product").order_by("-created_at")

    serializer = BundleOfferReadSerializer(bundles, many=True)
    return Response(serializer.data)


# ---------- GET SINGLE BUNDLE ----------
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_bundle_offer(request, id):
    try:
        # bundle = BundleOffer.objects.get(id=id)
        bundle = BundleOffer.objects.prefetch_related("items__product").get(id=id)

    except BundleOffer.DoesNotExist:
        return Response({"error": "Bundle not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = BundleOfferReadSerializer(bundle)
    return Response(serializer.data)


# ---------- UPDATE BUNDLE ----------
@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAdminUser])
def update_bundle_offer(request, id):
    try:
        bundle = BundleOffer.objects.get(id=id)
    except BundleOffer.DoesNotExist:
        return Response({"error": "Bundle not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = BundleOfferCreateSerializer(bundle, data=request.data, partial=True)
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






import pandas as pd
import requests
from io import BytesIO
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.core.files.base import ContentFile
from datetime import datetime
from decimal import Decimal, InvalidOperation
import cloudinary.uploader


@api_view(["POST"])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def bulk_upload_products(request):
    """
    Bulk upload products from an Excel file.
    Expected file format: .xlsx or .xls
    """
    
    if 'file' not in request.FILES:
        return Response(
            {"error": "No file provided. Please upload an Excel file."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    # Validate file extension
    if not file.name.endswith(('.xlsx', '.xls')):
        return Response(
            {"error": "Invalid file format. Please upload an Excel file (.xlsx or .xls)"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        # Optional: Rename columns to match expected format
        # This maps your Excel column names to the model field names
        column_mapping = {
            'Model Name': 'model_name',
            'model_name': 'model_name',
            'Description': 'description',
            'description': 'description',
            'Minable Coins': 'minable_coins',
            'minable_coins': 'minable_coins',
            'Hashrate': 'hashrate',
            'hashrate': 'hashrate',
            'Power': 'power',
            'power': 'power',
            'Algorithm': 'algorithm',
            'algorithm': 'algorithm',
            'Category': 'category',
            'category': 'category',
            'Price': 'price',
            'price': 'price',
            'Hosting Fee Per KW': 'hosting_fee_per_kw',
            'hosting_fee_$per_kwH': 'hosting_fee_per_kw',  # Your Excel header
            'hosting_fee_per_kw': 'hosting_fee_per_kw',
            'Brand': 'brand',
            'brand': 'brand',
            'Efficiency': 'efficiency',
            'efficiency': 'efficiency',
            'Noise': 'noise',
            'noise': 'noise',
            'noise_level': 'noise',  # Your Excel header
            'Noise Level': 'noise',
            'Delivery Type': 'delivery_type',
            'delivery_type': 'delivery_type',
            'Delivery Date': 'delivery_date',
            'delivery_date': 'delivery_date',
            'Is Available': 'is_available',
            'is_available': 'is_available',
            'Image URL': 'image_url',
            'image_url': 'image_url'
        }
        df = df.rename(columns=column_mapping)
        
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        # Debug: Print columns (remove after testing)
        print("Columns found in Excel:", df.columns.tolist())
        
        # Validate required columns
        required_columns = [
            'model_name', 'description', 'minable_coins', 
            'hashrate', 'power', 'algorithm', 'category'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return Response(
                {"error": f"Missing required columns: {', '.join(missing_columns)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process products
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            # Use transaction per product instead of for all products
            try:
                with transaction.atomic():
                    try:
                        # Prepare product data
                        product_data = {
                            'model_name': str(row['model_name']),
                            'description': str(row['description']),
                            'minable_coins': str(row['minable_coins']),
                            'hashrate': str(row['hashrate']),
                            'power': str(row['power']),
                            'algorithm': str(row['algorithm']),
                            'category': str(row['category']).lower(),
                        }
                        
                        # Optional fields with default handling
                        if 'price' in df.columns and pd.notna(row['price']):
                            try:
                                product_data['price'] = Decimal(str(row['price']))
                            except (InvalidOperation, ValueError):
                                pass
                        
                        if 'hosting_fee_per_kw' in df.columns and pd.notna(row['hosting_fee_per_kw']):
                            try:
                                product_data['hosting_fee_per_kw'] = Decimal(str(row['hosting_fee_per_kw']))
                            except (InvalidOperation, ValueError):
                                pass
                        
                        if 'brand' in df.columns and pd.notna(row['brand']):
                            product_data['brand'] = str(row['brand'])
                        
                        if 'efficiency' in df.columns and pd.notna(row['efficiency']):
                            product_data['efficiency'] = str(row['efficiency'])
                        
                        if 'noise' in df.columns and pd.notna(row['noise']):
                            product_data['noise'] = str(row['noise'])
                        
                        if 'delivery_type' in df.columns and pd.notna(row['delivery_type']):
                            product_data['delivery_type'] = str(row['delivery_type']).lower()
                        
                        if 'delivery_date' in df.columns and pd.notna(row['delivery_date']):
                            try:
                                if isinstance(row['delivery_date'], str):
                                    product_data['delivery_date'] = datetime.strptime(
                                        row['delivery_date'], '%Y-%m-%d'
                                    ).date()
                                else:
                                    # Handle datetime objects from Excel (convert to date only)
                                    product_data['delivery_date'] = pd.to_datetime(row['delivery_date']).date()
                            except (ValueError, TypeError):
                                pass
                        
                        if 'is_available' in df.columns and pd.notna(row['is_available']):
                            product_data['is_available'] = bool(row['is_available'])
                        
                        # Handle image URL if provided
                        image_file = None
                        if 'image_url' in df.columns and pd.notna(row['image_url']):
                            try:
                                image_url = str(row['image_url']).strip()
                                if image_url:
                                    # Download image from URL
                                    response = requests.get(image_url, timeout=10)
                                    response.raise_for_status()
                                    
                                    # Get file extension from URL or content-type
                                    content_type = response.headers.get('content-type', '')
                                    if 'image' in content_type:
                                        ext = content_type.split('/')[-1]
                                        if ext == 'jpeg':
                                            ext = 'jpg'
                                    else:
                                        ext = image_url.split('.')[-1].lower()
                                        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                                            ext = 'jpg'
                                    
                                    # Create file object
                                    image_file = ContentFile(
                                        response.content,
                                        name=f"{product_data['model_name'].replace(' ', '_')}.{ext}"
                                    )
                            except Exception as img_error:
                                # Log error but continue - image is optional
                                pass
                        
                        # Create product using serializer
                        serializer = ProductCreateSerializer(data=product_data)
                        
                        if serializer.is_valid():
                            product = serializer.save()
                            
                            # Upload image to Cloudinary if available
                            if image_file:
                                try:
                                    # Reset file pointer to beginning
                                    image_file.seek(0)
                                    # Assign file directly - Cloudinary handles the upload
                                    product.image = image_file
                                    product.save()
                                except Exception as upload_error:
                                    # Image upload failed but product was created - silently continue
                                    pass
                            
                            success_count += 1
                        else:
                            error_count += 1
                            errors.append({
                                'row': index + 2,  # +2 because Excel rows start at 1 and header is row 1
                                'model_name': product_data.get('model_name', 'Unknown'),
                                'errors': serializer.errors
                            })
                    
                    except Exception as e:
                        error_count += 1
                        errors.append({
                            'row': index + 2,
                            'model_name': row.get('model_name', 'Unknown'),
                            'errors': str(e)
                        })
                
            except Exception as e:
                error_count += 1
                errors.append({
                    'row': index + 2,
                    'model_name': row.get('model_name', 'Unknown'),
                    'errors': str(e)
                })
        
        # Prepare response
        response_data = {
            'message': 'Bulk upload completed',
            'success_count': success_count,
            'error_count': error_count,
        }
        
        if errors:
            response_data['errors'] = errors
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response(
            {"error": f"Failed to process file: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )