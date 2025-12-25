
from django.urls import path

from AdminApp import views

urlpatterns = [
    path('products/', views.get_products, name='get-products'),
    path('products/<int:id>/', views.get_product, name='get-product'),
    path("products/add/", views.create_product, name="create-product"),

    path('products/bulk-upload/', views.bulk_upload_products, name='bulk-upload-products'),

    path('products/<int:id>/update/', views.update_product, name='update-product'),
    path('products/<int:id>/delete/', views.delete_product, name='delete-product'),


    path("bundles/", views.list_bundle_offers, name="bundle-list"),
    path("bundles/<int:id>/", views.get_bundle_offer, name="bundle-detail"),
    path("bundles/add/", views.create_bundle_offer, name="bundle-create"),
    path("bundles/<int:id>/update/", views.update_bundle_offer, name="bundle-update"),
    path("bundles/<int:id>/delete/", views.delete_bundle_offer, name="bundle-delete"),


    path("rentals/", views.get_all_rent_orders, name="admin-rentals"),

    path("users/", views.get_all_users, name="admin-users"),



    path('hosting/requests/', views.admin_get_all_hosting_requests, name='admin_get_all_hosting_requests'),
    path('hosting/requests/<int:id>/', views.admin_get_hosting_request, name='admin_get_hosting_request'),
    path('hosting/requests/<int:id>/update/', views.admin_update_hosting_request, name='admin_update_hosting_request'),
    path('hosting/requests/<int:id>/delete/', views.admin_delete_hosting_request, name='admin_delete_hosting_request'),
    
    
    path("orders/", views.admin_list_orders, name="admin-list-orders"),
    path("orders/<int:id>/", views.admin_order_detail, name="admin-order-detail"),
    path("orders/<int:id>/status/", views.admin_update_order_status, name="admin-order-status"),
]
