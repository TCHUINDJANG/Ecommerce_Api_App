from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from .views import ProfileDetailView, ProfileUpdateView
from .views import ChangePasswordView
from .views import  PaymentMethodViewSet 
from .views import (
    CustomTokenObtainPairView,
    UserRegisterView,
    LogoutView,
    
    
)
from .views import (
    CartDetailView, AddToCardView, UpdateCartItemView,
    CheckoutView, OrderListView
)

from rest_framework_simplejwt.views import(
    TokenRefreshView,
    TokenObtainPairView,
    TokenVerifyView
)




router = DefaultRouter()


# router.register(r'addresses', AddresViewSet, basename='address')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')


urlpatterns = [

    # 1 Authentification et gestion des utilisateurs

    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', UserRegisterView.as_view(), name='user_register'),
    # path('auth/me/', UserProfileView.as_view(), name='user_profile'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('users/' , views.UserList.as_view() , name='user-list'),
    path('users/<int:pk>/' , views.UserDetail.as_view() , name='user-detail'),
    path("profile/", ProfileDetailView.as_view(), name="profile-detail"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile-update"),
    path('auth/password/change/', ChangePasswordView.as_view(), name='change-password'),




        # 2 Gestion des produits (Catalogue) avis et notation

    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetail.as_view(), name='category-detail'),
    path('products/', views.ProductList.as_view(), name='products-list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('reviews/', views.ReviewList.as_view(), name='reviews-list'),
    path('reviews/<int:pk>/', views.ReviewDetail.as_view(), name='reviews-detail'), 
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', AddToCardView.as_view(), name='add-to-cart'),
    path('cart/items/<int:id>/', UpdateCartItemView.as_view(), name='update-cart-item'),
            # 3 Panier d'achat 


    path('checkout/', CheckoutView.as_view(), name='checkout'),

    path('coupons/', views.CouponList.as_view(), name='coupon-list'),
    path('coupons/<int:pk>/', views.CouponDetail.as_view(), name='coupon-detail'),
    path('apply-coupon/', views.ApplyCouponView.as_view(), name='apply-coupon'),
        
]
            # 8 Commandes et paiement
urlpatterns += [
    path('orders/', views.OrderListCreate.as_view(), name='orders-list'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
    path('orders/<int:order_id>/items/', views.OrderItemList.as_view(), name='orders-item-list'),
    path('orders/<int:order_id>/items/<int:pk>/', views.OrderItemDetail.as_view(), name='order-item-detail'),
    path('promotions/', views.PromotionList.as_view(), name='promotion-list'),
    path('promotions/<int:pk>/', views.PromotionDetail.as_view(), name='promotion-detail'),


    #Paiment avec stripe
    path("process/", views.PaymentProcessView.as_view()),
    path("status/<str:payment_id>/", views.PaymentStatusView.as_view()),
    path("webhook/", views.StripeWebhookView.as_view()),  # Nouveau
    
 
]

urlpatterns = format_suffix_patterns(urlpatterns)





# {
#     "shipping_address": {
#         "street": "123 Main St",
#         "city": "Paris",
#         "state": "Ile-de-France",
#         "zip_code": "75001",
#         "country": "France",
#         "is_default": true
#     },
#     "billing_address_same_as_shipping": false,
#     "billing_address": {
#         "street": "456 Billing St",
#         "city": "Paris",
#         "state": "Ile-de-France",
#         "zip_code": "75002",
#         "country": "France",
#         "is_default": false
#     },
#     "payment_method": {
#         "method_type": "credit_card",
#         "details": {
#             "card_number": "4242424242424242",
#             "exp_date": "12/25",
#             "cvc": "123"
#         }
#     },
#     "items": [
#         {"product_id": 1, "quantity": 2},
#         {"product_id": 3, "quantity": 1}
#     ]
# }



# api ajouter une promotion
# {
#   "name":"Fete de paques",
#   "description":"Siant Valentin",
#   "discount_value":1200,
#   "start_date":"2014-10-21",
#   "end_date":"2019-11-10",
#   "code":"Special Promo V1",
#    "product_ids": [1, 2, 3],
#    "category_ids": [4, 5]
# }


# profil utilisateur
# {
  
#   "user": {
#     "email":"paulnicolas519@gmail.com",
#     "first_name":"David",
#     "last_name":"Tankeu"
#   },
  
#   "phone": "6574860000",
#   "address": "Paris",
#   "city": "Soudan",
#   "country": "Asie",
#   "postal_code": "BP 34567",
#   "birth_date": "2014-06-12"
  
# }



