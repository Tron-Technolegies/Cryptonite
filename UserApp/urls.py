from django.urls import path

from UserApp import views
from .views import AddToCartView, BundleOfferDetailView, BundleOfferListView, CartListView, CartTotalView, CheckoutView, CreateHostingRequestView, CreatePaymentIntentView, ForgotPasswordView, GetUserInfoView, LogoutView, ProductDetailView, ProductListView, RegisterView, EmailTokenObtainView, RemoveFromCartView, RentMinerView, ResetPasswordView, StripeWebhookView, UpdateCartView, UserActiveRentalsView, UserPastRentalsView, VerifyEmailView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path('auth/verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path("auth/login/", EmailTokenObtainView.as_view(), name="auth-login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="reset-password"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),

    # Product endpoints
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:id>/", ProductDetailView.as_view(), name="product-detail"),

    # Cart endpoints
    path("cart/", CartListView.as_view(), name="cart-view"),
    path("cart/add/", AddToCartView.as_view(), name="cart-add"),
    path("cart/<int:id>/update/", UpdateCartView.as_view(), name="cart-update"),
    path("cart/<int:id>/delete/", RemoveFromCartView.as_view(), name="cart-delete"),
    path("cart/total/", CartTotalView.as_view(), name="cart-total"),


    #Miner rentals
    path("rent/", RentMinerView.as_view(), name="rent-miner"),
    path("rent/active/", UserActiveRentalsView.as_view(), name="active-rentals"),
    path("rent/history/", UserPastRentalsView.as_view(), name="past-rentals"),


    #Get user info
    path("auth/me/", GetUserInfoView.as_view(), name="user-info"),

    #Bundle offers
    path("bundles/", BundleOfferListView.as_view(), name="bundle-list"),
    path("bundles/<int:id>/", BundleOfferDetailView.as_view(), name="bundle-detail"),

    #Payment
    path("payments/create-intent/", CreatePaymentIntentView.as_view(), name="create-payment-intent"),
    path("payments/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),

    path("checkout/", CheckoutView.as_view(), name="checkout"),

    #hosting
    path("hosting/create/", CreateHostingRequestView.as_view(), name="create-hosting"),

    path("asic-profitability/", views.asic_profitability, name='asic_profitability'),

    path("orders/my-orders/", views.my_orders, name="my-orders"),
    path("my-rentals/", views.my_rentals, name='my_rentals'),
    path('my-hosting-requests/', views.my_hosting_requests, name='my_hosting_requests'),

    path("invoices/",views.my_invoices, name='my_invoices'),
    path("invoices/<int:id>/download/", views.download_invoice, name='download_invoice'),

    # PUBLIC BLOG APIs
    path("blogs/", views.list_blogs, name="blog-list"),
    path("blogs/<slug:slug>/", views.blog_detail, name="blog-detail"),

    path("events/", views.list_events, name='list_events'),
    path("events/<slug:slug>/", views.event_detail, name='event_detail'),

    path('products/<int:product_id>/reviews/', views.list_product_reviews, name='product-reviews'),
    path('products/<int:product_id>/reviews/create/', views.create_review, name='review-create'),
    # path('products/<int:product_id>/reviews/',views.list_product_reviews,name='product-review-list'),
]