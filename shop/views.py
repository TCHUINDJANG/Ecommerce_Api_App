from rest_framework import generics, permissions, status , filters
from rest_framework.response import Response
from rest_framework.views import APIView
import stripe.error
from .models import Category, Product, Order, OrderItem, Review , Adress , Cart , CartItem , ContactMessage
from .serializers import (CategorySerializer, ProductSerializer, CartSerializer,
                         OrderSerializer,AdressSerializer,  ReviewSerializer, OrderItemSerializer ,UserSerializer)
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsOwnerOrReadOnly   , IsProductOwner
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from .models import Promotion,  Coupon , Profile ,PaymentMethod
from rest_framework import viewsets
from rest_framework.decorators import action
# import stripe
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from django.conf import settings
from .filters import ProductFilter
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet , GenericViewSet
from rest_framework.mixins import CreateModelMixin , RetrieveModelMixin
from django.views.decorators.csrf import csrf_exempt
from .serializers import PromotionSerializer,CheckoutSerializer , ContactMessageSerializer,CartItemSerializer ,  PaymentMethodSerializer,ProfileSerializer, CouponSerializer, ApplyCouponSerializer , AdressSerializer
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import NotAuthenticated
from django.contrib.auth import get_user_model
from django.http import Http404
from .permissions import IsCartOwner
from rest_framework.permissions import IsAuthenticated
from .serializers import ChangePasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import MultipleObjectsReturned
from rest_framework.permissions import AllowAny
from rest_framework import generics, pagination
from rest_framework import status
import stripe


User = get_user_model()

stripe.api_key = settings.STRIPE_SECRET_KEY







class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]



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
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializers = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializers.is_valid():
            user = request.user
            new_password = serializers.validated_data['new_password']
            user.set_password(new_password)
            user.save()

        # Invalider tous les tokens JWT existants
            RefreshToken.for_user(user)


            return Response({
            "status":"success",
            "message": "Mot de passe changé avec succès. Tous vos tokens ont été invalidés." },status=status.HTTP_200_OK)
    

        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    
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
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend , filters.SearchFilter , filters.OrderingFilter]
    filterset_fields = ['category' , 'available']
    filterset_class = ProductFilter
    search_fields = ['name' , 'description']
    ordering_fields = ['price' , 'created_at']
    pagination_class = PageNumberPagination
    # permission_classes = [permissions.IsAuthenticated , IsProductOwner]



    def get(self, request, *args, **kwargs):
    # Laissez la parent class gérer la pagination et les filtres
         return super().get(request, *args, **kwargs)


    # def get(self ,request):
    #     products = Product.objects.all()
    #     serializer = ProductSerializer(products , many=True)
    #     return Response(serializer.data)

   

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


class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]



    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).prefetch_related(
            'items__product'
        )

    def get_object(self):
        try:
            # Essayez de récupérer le panier existant
            return Cart.objects.get(user=self.request.user)
        except Cart.DoesNotExist:
            return Cart.objects.create(user=self.request.user)
        except MultipleObjectsReturned:
            # Gestion des doublons : récupère le plus récent
            carts = Cart.objects.filter(user=self.request.user).order_by('-created')
            # Garde le plus récent et supprime les doublons
            main_cart = carts.first()
            carts.exclude(id=main_cart.id).delete()
            return main_cart



class AddToCardView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]


    def create(self , request , *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response (
                {
                    'error':'Product not found'
                },
                status= status.HTTP_404_NOT_FOUND
            )
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item , created = CartItem.objects.get_or_create(
            cart = cart , 
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity+= int(quantity)
            cart_item.save()

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data , status=status.HTTP_201_CREATED)
    

class UpdateCartItemView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

   
        

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
    

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        return Order.objects.filter(user= self.request.user)
    

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
            customer = self.request.user,
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
    serializer_class = PaymentMethodSerializer
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
    serializer_class = PaymentMethodSerializer
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

class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        payment_method = self.get_object()
        PaymentMethod.objects.filter(user=request.user).update(is_default=False)
        payment_method.is_default = True
        payment_method.save()
        return Response({'status': 'default payment method set'})
    


class CheckoutView(generics.CreateAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]


    @transaction.atomic
    def create(self , request , *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

            # verifier que le panier n'est pas vide

        cart = Cart.objects.get(user=request.user)
        if not cart.items.exits():
            return Response(
                {'error':'Your Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Vérifier le stock avant de créer la commande
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                return Response(
                    {'error': f'Not enough stock for {item.product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        # Créer la commande
        order = Order.objects.create(
            user = request.user,
            shipping_address=serializer.validated_data['shipping_address'],
            billing_address=serializer.validated_data.get('billing_address'),
            total_price=cart.total_price
        )

        # Créer les OrderItems et mettre à jour le stock
        for cart_item in cart_item.all():
            OrderItem.objects.create(
                order = order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        # Mettre à jour le stock
        cart_item.product.stock -= cart_item.quantity
        cart_item.product.save()

        # Vider le panier
        cart.items.all().delete()

        # Retourner la commande créée
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data , status=status.HTTP_201_CREATED)
    


# accepter le paiment avec stripe

class PaymentProcessView(APIView):
    def post(self, request):
        order_id = request.data.get('order_id')
        token = request.data.get('token')   #token stripe pour le frontend
        try:
            order = Order.objects.get(id=order_id , user=request.user)


            # Créer un paiement Stripe
            charge = stripe.Charge.create(
                amount = int(order.total * 100),  # stripe utilise les centemes
                currency="usd",
                source=token,
                description=f"Paiment pour la commande {order.transaction_id}",
            )

            # Sauvegarder le paiement en base
            payment = PaymentMethod.objects.create(
                order=order,
                transaction_id = charge.id,
                amount = order.total,
                currency="usd",
                status="succeeded" if charge.paid else "failed",
                payment_method = "stripe"
            )

            return Response(
                {"status":"success" , "transaction_id":payment.transaction_id},
                status=status.HTTP_201_CREATED,
            )
        except Order.DoesNotExist:
            return Response(
                {"error":"Commande introuvable"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except stripe.error.StripeError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        



# Endpoint de Confirmation de paiement (GET
class PaymentStatusView(APIView):
    def get(self , request, payment_id):
        try:
            payment = PaymentMethod.objects.get(payment_id=payment_id)
            return Response(
                {
                    "payment_id":payment.transaction_id,
                    "status":payment.status,
                    "amount":payment.amount,
                    "order_id":payment.order
                },
                status = status.HTTP_200_OK
            )
        except PaymentMethod.DoesNotExist:
            return Response(
                {"error": "Paiement introuvable"}, 
                status=status.HTTP_404_NOT_FOUND,
            )
        


# pour confirmer les paiements de manière asynchrone.
class StripeWebhookView(APIView):
    @csrf_exempt
    def post(self, request):
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return HttpResponse(status=400)  # Requête invalide
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)  # Signature invalide

        # Gérer les événements Stripe
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            self.handle_payment_succeeded(payment_intent)
        
        return HttpResponse(status=200)
    

    def handle_payment_succeeded(self , payment_intent):
        payment_id = payment_intent['id']
        try:
            payment = PaymentMethod.objects.get(payment_id=payment_id)
            payment.status = "succeeded",
            payment.save()

            #mettre a jour la commande comme paye
            payment.order.status = "paid"
            payment.order.save()
        except PaymentMethod.DoesNotExist:
            pass



class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer



    def create(self , request , *args, **kwargs):
        serializers = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        self.perform_create(serializers)

        return Response(
            {"message": "Votre message a bien été envoyé. Nous vous répondrons dès que possible."},
            status=status.HTTP_201_CREATED
        )



    


class ReviewContactMessageView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly , IsOwnerOrReadOnly]
    

    

   












