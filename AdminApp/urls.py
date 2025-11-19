
from django.urls import path

from AdminApp import views

urlpatterns = [
    path('products/', views.get_products, name='get-products'),
    path('products/<int:id>/', views.get_product, name='get-product'),
    path('products/add/', views.create_product, name='create-product'),
    path('products/<int:id>/update/', views.update_product, name='update-product'),
    path('products/<int:id>/delete/', views.delete_product, name='delete-product'),
   

    path("bundles/", views.get_bundle_offers, name="bundle-list"),
    path("bundles/<int:id>/", views.get_bundle_offer, name="bundle-detail"),
    path("bundles/add/", views.create_bundle_offer, name="bundle-create"),
    path("bundles/<int:id>/update/", views.update_bundle_offer, name="bundle-update"),
    path("bundles/<int:id>/delete/", views.delete_bundle_offer, name="bundle-delete"),


    path("rentals/", views.get_all_rent_orders, name="admin-rentals"),

    path("users/", views.get_all_users, name="admin-users")
    

]
