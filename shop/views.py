from rest_framework import generics, permissions, status , filters
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, Product, Order, OrderItem, Review , Adress , Cart , CartItem
from .serializers import (CategorySerializer, ProductSerializer, CartSerializer,
                         OrderSerializer,AdressSerializer, ProfileUpdateSerializer , ReviewSerializer, OrderItemSerializer ,UserSerializer)
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsOwnerOrReadOnly   , IsProductOwner
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from .models import Promotion, Payment, Coupon , Profile
from rest_framework import viewsets
from rest_framework.decorators import action
# import stripe
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from django.conf import settings
from .filters import ProductFilter
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet , GenericViewSet
from rest_framework.mixins import CreateModelMixin , RetrieveModelMixin
from .serializers import PromotionSerializer, PaymentSerializer,ProfileSerializer, CouponSerializer, ApplyCouponSerializer , AdressSerializer
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth import get_user_model
from django.http import Http404
from .permissions import IsCartOwner


User = get_user_model()



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


# class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = UserProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]
    


class ProfileDetailView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.profile
        except Profile.DoesNotExist:
            return Profile.objects.create(user=self.request.user)
        except AttributeError:
            raise Http404("Profil non trouvé")

class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    
class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self , request):
        response = Response({"detail": "Successfully logged out."})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    # permission_classes = [permissions.IsAuthenticated]





class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [permissions.IsAdminUser]

class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_fields = ['category' , 'available']
    filterset_class = ProductFilter
    search_fields = ['name' , 'description']
    ordering_fields = ['price' , 'created_at']
    pagination_class = PageNumberPagination
    # permission_classes = [permissions.IsAuthenticated]

   

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [permissions.IsAuthenticated  , IsProductOwner]

class ReviewCreate(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product_slug = self.kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)
        serializer.save(user=self.request.user, product=product)

class OrderListCreate(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated , IsCartOwner]



class CartCreateView(APIView):
    def post(self, request):
        if 'items' not in request.data:
            return Response(
                {"error": "La clé 'items' est requise"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            cart = serializer.save()
            return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


   
        

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated , IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
    

class OrderItemList(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        order_id = self.kwargs['order_id']
        if self.request.user.is_staff:
            return OrderItem.objects.filter(order_id=order_id)
        return OrderItem.objects.filter(order_id=order_id , order__user=self.request.user)
    
    
    def perform_create(self , serializer):
        order_id = self.kwargs['order_id']
        order = generics.get_object_or_404(Order , pk=order_id)
        serializer.save(order=order)


class OrderItemDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated , IsOwnerOrReadOnly]


    def get_queryset(self):
        if self.request.user.is_staff:
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order__user=self.request.user)
    

class ReviewList(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        product = self.request.query_params.get('product')

        if product:
            queryset = queryset.filter(product=product)

        return queryset
    

    def perform_create(self, serializer):
        product_id = self.request.data.get('product')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({"product": "Produit introuvable"})
        
        serializer.save(
            user = self.request.user,
            product=product
        )
        
        


class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly , IsOwnerOrReadOnly]
    



class PromotionList(generics.ListCreateAPIView):
    queryset = Promotion.objects.filter(
        active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
    )

    # queryset = Promotion.objects.filter(end_date__gte=timezone.now())
    serializer_class = PromotionSerializer
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['discount_type']
    search_fields = ['name', 'code']

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product_id')
        category_id = self.request.query_params.get('category_id')
       
        if product_id:
            queryset = queryset.filter(products__id=product_id)
        if category_id:
            queryset = queryset.filter(categories__id=category_id)
       
        return queryset.distinct()

class PromotionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    # permission_classes = [permissions.IsAdminUser]

class PaymentList(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        if order.user != self.request.user:
            raise PermissionDenied("You can't create payment for this order.")
       
        # Simuler un processus de paiement
        payment = serializer.save()
        payment.status = 'completed'
        payment.transaction_id = f"TXN-{timezone.now().timestamp()}"
        payment.save()
       
        # Mettre à jour le statut de la commande
        order.status = 'completed'
        order.save()

class PaymentDetail(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=self.request.user)

class CouponList(generics.ListCreateAPIView):
    queryset = Coupon.objects.filter(
        active=True,
        valid_from__lte=timezone.now(),
        valid_to__gte=timezone.now()
    )
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]

class CouponDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]

class ApplyCouponView(generics.CreateAPIView):
    serializer_class = ApplyCouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
       
        coupon = serializer.validated_data['coupon']
        order = Order.objects.get(pk=serializer.validated_data['order_id'])
       
        # Appliquer la réduction
        discount = coupon.discount
        order.total = order.total * (100 - discount) / 100
        order.save()
       
        return Response({
            'success': True,
            'message': f'Coupon applied successfully. {discount}% discount applied.',
            'new_total': order.total
        }, status=status.HTTP_200_OK)
    



class AdressViewSet(viewsets.ModelViewSet):
    serializer_class = AdressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Adress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        if serializer.validated_data.get('is_default' , False):
            Adress.objects.filter(user=self.request.user ,is_default=True).update(is_default=False)
        serializer.save(user=self.request.user)

    def perform_update(self ,serializer):
        if serializer.validated_data.get('is_default' , False):
            Adress.objects.filter(user=self.request.user ,is_default=True).update(is_default=False)
        serializer.save(user=self.request.user)


class PayementViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_query(self):
        return Payment.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_payement_intent(self, request):
        try:
            amount = int(float(request.data.get('amount'))  * 100)  # Convertir en cents
            currency = request.data.get('currency' , 'usd')


        #verifier les adress
            billing_address_id = request.data.get('billing_address_id')
            shipping_address_id = request.data.get('shipping_address_id')


            if not shipping_address_id or not shipping_address_id:
                return Response (
                    {'errotr': 'Billing and shipping addresses are required'},
                    status = status.HTTP_400_BAD_REQUEST
                )
            
            try:
                billing_address = Adress.objects.get(id=billing_address_id , user=request.user)
                shipping_address = Adress.objects.get(id=shipping_address_id , user=request.user)

            except Adress.DoesNotExist:
                return Response(
                    {'error':'Invalid adress ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            

                #creer un payement avec stripe
            # intent = stripe.PaymentItent.create(
            #         amount = amount,
            #         currency = currency,
            #         metadata = {
            #             'user_id': request.user.id,
            #             'billing_address_id': billing_address_id,
            #             'shipping_address_id': shipping_address_id
            #         }
            #     )
            return Response({
                # 'clientSecret': intent.client_secret,
                'publishableKey': settings.STRIPE_PUBLISHABLE_KEY
            })
        except Exception as e:
            return Response (
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
            )
        








