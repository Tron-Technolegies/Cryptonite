# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from AdminApp.models import Product
from .serializers import ProductSerializer

# ---------- CREATE PRODUCT ----------
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def create_product(request):
    serializer = ProductSerializer(data=request.data)
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


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import BundleOffer
from .serializers import BundleOfferSerializer


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
