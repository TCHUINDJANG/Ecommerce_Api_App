from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, PayementViewSet
from .views import (
    CustomTokenObtainPairView,
    UserRegisterView,
    UserProfileView,
    LogoutView,
    
    
)

from rest_framework_simplejwt.views import(
    TokenRefreshView,
    TokenObtainPairView,
    TokenVerifyView
)




router = DefaultRouter()


router.register(r'carts', CartViewSet, basename='cart')
router.register(r'payments', PayementViewSet, basename='payment')


urlpatterns = [

    # 1 Authentification et gestion des utilisateurs

    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserRegisterView.as_view(), name='user_register'),
    path('auth/me/', UserProfileView.as_view(), name='user_profile'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('users/' , views.UserList.as_view() , name='user-list'),
    path('users/<int:pk>/' , views.UserDetail.as_view() , name='user-detail'),




        # 2 Gestion des produits (Catalogue) avis et notation

    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetail.as_view(), name='category-detail'),
    path('products/', views.ProductList.as_view(), name='products-list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('reviews/', views.ReviewList.as_view(), name='reviews-list'),
    path('reviews/<int:pk>/', views.ReviewDetail.as_view(), name='reviews-detail'), 

            # 3 Panier d'achat 

    path('coupons/', views.CouponList.as_view(), name='coupon-list'),
    path('coupons/<int:pk>/', views.CouponDetail.as_view(), name='coupon-detail'),
    path('apply-coupon/', views.ApplyCouponView.as_view(), name='apply-coupon'),



            # 4 Livraison

    # path('shipping-methods/', ShippingMethodListAPIView.as_view(), name='shipping-method-list'),
    # path('shipping-cost/', ShippingCostCalculatorAPIView.as_view(), name='shipping-cost'),
    # path('addresses/', UserAddressListCreateAPIView.as_view(), name='address-list'),
    # path('addresses/<int:pk>/', UserAddressRetrieveUpdateDestroyAPIView.as_view(), name='address-detail'),



            # 5 Promotions et réductions


    # path('coupons/validate/', CouponValidateAPIView.as_view(), name='coupon-validate'),
    # path('deals/', DealListAPIView.as_view(), name='deal-list'),
    # path('flash-sales/', FlashSaleListAPIView.as_view(), name='flash-sale-list'),



            #  6 Statistiques et rapports (Admin)


    # path('dashboard/', AdminDashboardAPIView.as_view(), name='admin-dashboard'),
    # path('sales-report/', SalesReportAPIView.as_view(), name='sales-report'),
    # path('product-performance/', ProductPerformanceAPIView.as_view(), name='product-performance'),
    # path('customer-insights/', CustomerInsightsAPIView.as_view(), name='customer-insights'),



            #  7 Notifications

    # path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    # path('notifications/<int:pk>/read/', NotificationReadAPIView.as_view(), name='notification-read'),
    # path('notifications/preferences/', NotificationPreferenceAPIView.as_view(), name='notification-preference'),
         
]
            # 8 Commandes et paiement
urlpatterns += [
    path('orders/', views.OrderListCreate.as_view(), name='orders-list'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
    path('orders/<int:order_id>/items/', views.OrderItemList.as_view(), name='orders-item-list'),
    path('orders/<int:order_id>/items/<int:pk>/', views.OrderItemDetail.as_view(), name='order-item-detail'),
    path('promotions/', views.PromotionList.as_view(), name='promotion-list'),
    path('promotions/<int:pk>/', views.PromotionDetail.as_view(), name='promotion-detail'),
    
]

urlpatterns = format_suffix_patterns(urlpatterns)


