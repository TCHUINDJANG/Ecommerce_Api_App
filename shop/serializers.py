from rest_framework import serializers
from .models import (
    Category , Product ,Cart ,ContactMessage, Profile , CartItem,  PaymentMethod ,Review ,Adress, Order , OrderItem , Wishlist , Coupon , Promotion 
)

from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import PaymentMethod
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from decimal import Decimal



User = get_user_model()



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls , user):
        token = super().get_token(user)
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        return token

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name' , 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}  # non requis en update
        }


    def validate_username(self , value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est deja pris")
        return value
    
    
    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value


    def create(self , validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name']
        )

        return user
    


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self , data):
        user = self.context['request'].user

        if not user.check_password(data.get('old_password')):
            raise serializers.ValidationError({"old_password": "Ancien mot de passe incorrect"})
        
        try:
            validate_password(data.get('new_password') , user)
        except exceptions.ValidationError as e:
            raise  serializers.ValidationError({"new_password": list(e.messages)})
        
        return data
    




class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = "__all__"
        
    
    def update(self , instance , validated_data):
        user_data = validated_data.pop('user' , {})

        # Mise à jour User (sans toucher au username/password)
        user = instance.user
        for attr , value in user_data.items():


            setattr(user , attr , value)
        user.save()


        # Mise à jour Profile
        for attr , value in validated_data.items():
            setattr(instance , attr , value)
        instance.save()

        return instance


# class ProfileUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields = ["phone", "address", "city"  , "country", "postal_code", "birth_date", "profile_picture"]
#         read_only_fields = [ "created_at", "updated_at"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id' , 'slug']

        extra_kwargs = {
            'name': {
                'validators' : [
                    UniqueValidator(
                        queryset=Category.objects.all(),
                        message = 'Cette categorie existe deja'
                    )
                ]
            }
        }


class ProductSerializer(serializers.ModelSerializer):
    available = serializers.SerializerMethodField()
    seller = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset = Category.objects.filter(is_active=True),
        source='category',
        write_only=True
    )

    current_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)


    class Meta:
        model = Product
        fields = [
            'id','category', 'category_id', 'name', 'slug',
            'description' , 'price' , 'discount_price' , 'current_price',
            'stock' , 'available' , 'created_at' , 'updated_at',
            'sale_count' , 'average_rating' , 'review_count' , 'seller', 'image'
        ]

        read_only_fields = [
            'id' , 'slug' , 'created_at' , 'updated_at',
            'sale_count' , 'current_price' ,'average_rating', 'review_count'
        ]

        extra_kwargs = {
            'name' : {
                'validators' : [
                    UniqueValidator(
                        queryset=Product.objects.all(),
                        message = "Ce produit existe deja"
                    )
                ]
            }
        }
    def validate(self , data):
        if 'discount_price' in data and data['discount_price']:
            if data['discount_price'] >=data['price']:
                raise serializers.ValidationError(
                    "Le prix reduit doit etre inferieur au prix normal"
                )
            return data
    
    def get_available(self , obj):
        return obj.stock > 0
            
        
    

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = serializers.PrimaryKeyRelatedField(
        queryset = Product.objects.all(),
        write_only = True
    )

    class Meta:
        model = Review
        fields = [
            'id', 'product' , 'user' , 'rating' , 'comment',
            'is_approved' , 'created_at' , 'updated_at'
        ]

        read_only_fields = [
            'id' , 'user' , 'created_at' , 'updated_at'
        ]

        def validate_rating(self , value):
            if value < 1 or value > 5:
                raise serializers.ValidationError(
                    "La note doit etre comprise entre 1 et 5"
                )
            return value
        

        def validate(self, data):
             if not data.get('comment') and data.get('rating') < 3:
                raise serializers.ValidationError("Un commentaire est obligatoire pour les notes inférieures à 3.")
             return data
        
        def validate(self , data):
            user = self.context['request'].user
            product = data['product']

            if Review.objects.filter(user=user , product=product).exists():
                raise serializers.ValidationError(
                    "Vous avez deja poste un avis pour ce produits"
                )
            
        def validate_product_id(self , value):
            if not Product.objects.filter(id=value).exists():
                raise serializers.ValidationError("Products does not exits")
            return value
            


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)


    class Meta:
        model = OrderItem
        fields = [
            'id' , 'product' , 'product_id' , 'price',
            'quantity' , 'total' 

        ]

        read_only_fields = ['price' , 'total']


    def validate_items(self , value):
            if not value:
                raise serializers.ValidationError(
                    "Une commande doit contenir au moins un article"
                )
            return value
# transction garanti que toutes les operation de la BD s'execute dans une transaction unique
       
    def create(self , validated_data):
            item_data = validated_data.pop('items')
            request = self.context.get('request') 
            order = Order.objects.create(user = request.user ,**validated_data )

            for item_data in item_data:
                product = item_data['product']
                OrderItem.objects.create(
                    order = order,
                    product=product,
                    price=product.current_price,
                    quantity = item_data['quantity']
                )

                order.update_total()
                return order
            

class PromotionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all(),
        source='products',
        write_only=True,
        required=False
    )
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        source='categories',
        write_only=True,
        required=False
    )

    class Meta:
        model = Promotion
        fields = '__all__'


    def create(self , validated_data):
        # extraire les donnes des categories et des produits
        products = validated_data.pop('products',[])
        categories = validated_data.pop('categories' , [])

        promotion = Promotion.objects.create(**validated_data)

        promotion.products.set(products)
        promotion.categories.set(categories)

        return promotion


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)
    order_id = serializers.IntegerField()

    def validate(self, data):
        try:
            order = Order.objects.get(pk=data['order_id'])
            if order.user != self.context['request'].user:
                raise serializers.ValidationError("This order doesn't belong to you.")
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order does not exist.")
       
        try:
            coupon = Coupon.objects.get(code=data['code'], active=True)
            if not (coupon.valid_from <= timezone.now() <= coupon.valid_to):
                raise serializers.ValidationError("Coupon is expired.")
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")
       
        data['coupon'] = coupon
        return data
    

class AdressSerializer(serializers.ModelSerializer):
    class Meta:
        model=Adress
        fields = ['id', 'street', 'city',  
            'zip_code', 'country', 'is_default']

        extra_kwargs = {
            'user': {'read_only': True},
            'is_default': {'required': False}
        }

    def validate_is_default(self , value):
        if value and self.instance:
            Adress.objects.filter(user=self.instance.user , is_default=True).update(is_default=False)

        return value
    

class PaymentMethodSerializer(serializers.ModelSerializer):
    card_number = serializers.CharField(write_only=True)
    masked_card_number = serializers.SerializerMethodField(read_only=True)
    details = serializers.JSONField()

    class Meta:
        model = PaymentMethod
        fields = ['PAYMENT_METHOD', 'details' , 'masked_card_number' , 'card_number']
        

    def get_masked_card_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}"

    def validate_card_number(self, value):
        # Remove all non-digit characters
        cleaned_value = ''.join(c for c in value if c.isdigit())
        if len(cleaned_value) not in (15, 16):
            raise serializers.ValidationError("Card number must be 15 or 16 digits")
        return cleaned_value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True , required=True)   
    user = UserSerializer(read_only=True)
    transaction_id = serializers.CharField(required=False)


    shipping_address = AdressSerializer(required=True)
    billing_address = AdressSerializer(required=True)
    payment_method = PaymentMethodSerializer(required=True)
    status = serializers.CharField(read_only=True)
    promotion = PromotionSerializer(read_only=True)
    promotion_id = serializers.PrimaryKeyRelatedField(
        queryset = Promotion.objects.filter(
            activate=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ),
        source='promotion',
        write_only=True,
        required=False
    )


    coupon = CouponSerializer(read_only=True)
    coupon_code = serializers.CharField(
        source='promotion',
        write_only=True,
        required=False
    )


    class Meta:
        model = Order
        fields = '__all__' 


    
    def create(self , validated_data):
        items_data = validated_data.pop('items')
        shipping_data = validated_data.pop('shipping_address')
        billing_data = validated_data.pop('billing_address')
        payment_data = validated_data.pop('payment_method')



        # creation des adresses

        shipping_address = Adress.objects.create(**shipping_data)
        billing_address = Adress.objects.aaggregate(**billing_data)

        order = Order.objects.create(
            shipping_address = shipping_address,
            billing_data = billing_address,
            payment_method = payment_data,
            **validated_data

        )

        # ajout des items


        for items_data in items_data:
            OrderItem.objects.create(order=order , **items_data)

        return order





class CheckoutSerializer(serializers.Serializer):
    shipping_address = AdressSerializer()
    billing_address_same_as_shipping = serializers.BooleanField()
    billing_address = AdressSerializer(required=False)
    payment_method = PaymentMethodSerializer()
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    def validate(self, data):
        if not data.get('billing_address_same_as_shipping') and not data.get('billing_address'):
            raise serializers.ValidationError({
                'billing_address': 'Billing address is required when not same as shipping'
            })
        return data


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer
    unit_price = serializers.DecimalField(
        source='price',
        max_digits=10, 
        decimal_places=2,
        read_only=True
    )
    total_price = serializers.SerializerMethodField()
   
    class Meta:
        model = CartItem
        fields = [ 'id' , 'product' , 'unit_price', 'quantity' , 'total_price']


    def get_total_price(self, obj):
        return obj.total_price
    


class CartSummarySerializer(serializers.Serializer):
    items_count = serializers.IntegerField()
    products_count = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    shipping_cost = serializers.DecimalField(max_digits=6, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    discounts = serializers.DictField()
    eligible_for_free_shipping = serializers.BooleanField()

    

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    _links = serializers.SerializerMethodField

    items_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CartItem.objects.all(),
        source='cartItems',
        write_only=True,
        required=False
    )

    products_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all(),
        source='products',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Cart
        fields = ['id' , 'user', 'created'  ,'summary', 'total_price'  , 'items' , 'products_ids' , 'items_ids']

        extra_kwargs = {
            '_links': {'read_only': True},
            'summary': {'read_only': True},
            'items': {'read_only': True}
        }


    def get_total_price(self , obj):
        return obj.total_price
    

    def get_links(self, obj):
        request = self.context.get('request')
        return {
            'self': request.build_absolute_uri(),
            'checkout': request.build_absolute_uri('/api/checkout/'),
            'continue_shopping': request.build_absolute_uri('/api/products/')
        }


    def create(self , validated_data):
        items_data = validated_data.pop("items" , [])
        cart = Cart.objects.create()
        for item_data in items_data:
            try:
                CartItem.objects.create(
                    cart=cart,
                    product_id=item_data.get('product_id'),  # Utilisez .get() avec valeur par défaut
                    quantity=int(item_data.get('quantity', 1))  # Valeur par défaut 1
                )
            except (TypeError, ValueError) as e:
                raise serializers.ValidationError({
                    'error': f"Données d'item invalides: {str(e)}"
                })
        
        return cart
    

    def get_summary(self, obj):
        items = obj.items.all()
        subtotal = sum(item.quantity * item.product.price for item in items)
        
        return {
            'items_count': sum(item.quantity for item in items),
            'products_count': items.count(),
            'subtotal': subtotal,
            'eligible_for_free_shipping': subtotal > 100  # Exemple: gratuit à partir de 100€
        }
    

    # def _calculate_shipping(self, panier):
    #     """Méthode protégée pour calculer les frais de livraison"""
    #     # Exemple de logique - à remplacer par votre calcul réel
    #     if panier.poids_total > 10:
    #         return Decimal('15.00')
    #     return Decimal('5.00')
    
    
    def update(self , validated_data):
        return None
    
    def delete (self):
        return None



class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']









        