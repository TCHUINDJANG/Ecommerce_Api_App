from rest_framework import serializers
from .models import (
    Category , Product ,Cart , Profile , CartItem,  Review ,Adress, Order , OrderItem , Wishlist , Coupon , Promotion , Payment
)

from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import Payment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



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
        read_only_fields = ['id']


    def create(self , validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data['email'],
            password = validated_data['password'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name']
        )

        return user
    

# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=User
#         fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
#         read_only_fields = ('id', 'date_joined')




class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["user", "created_at", "updated_at"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["phone", "address", "city"  , "country", "postal_code", "birth_date", "profile_picture"]
        read_only_fields = [ "created_at", "updated_at"]


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
    product_id = serializers.PrimaryKeyRelatedField(
        queryset = Product.objects.filter(available=True),
        source='product',
        write_only=True
    )


    class Meta:
        model = OrderItem
        fields = [
            'id' , 'product' , 'product_id' , 'price',
            'quantity' , 'total' 

        ]

        read_only_fields = ['id' , 'price' , 'total' , 'product', 'quantity']



    # class Meta:
    #     model = Order
    #     fields = [
    #         'id' , 'user' , 'transaction_id' ,'status' , 'shipping_adress',
    #         'billing_adress' , 'tax' , 'total' ,'payment_method' , 'payment_status',
    #         'notes' , 'transaction_id'
    #     ]

    #     read_only_fields = [
    #         'id' , 'user' , 'transaction_id', 'status' , 
    #         'total' , 'created_at' , 'updated_at'
    #     ]


        def validate_items(self , value):
            if not value:
                raise serializers.ValidationError(
                    "Une commande doit contenir au moins un article"
                )
            return value
# transction garanti que toutes les operation de la BD s'execute dans une transaction unique
        @transaction.atomic
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
    





class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = UserSerializer(read_only=True)
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





class AdressSerializer(serializers.ModelSerializer):
    class Meta:
        model=Adress
        fields = ['id' , 'user' , 'city' , 'postal_code' , 'country' , 'is_default']

        read_only_fields = ['id', 'user']

    def validate_is_default(self , value):
        if value and self.instance:
            Adress.objects.filter(user=self.instance.user , is_default=True).update(is_default=False)

        return value
    

class PaymentSerializer(serializers.ModelSerializer):
    billing_address = AdressSerializer(read_only=True)
    shipping_address = AdressSerializer(read_only=True)
    billing_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Adress.objects.all(),
        source='billing_address',
        write_only=True
    )
    shipping_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Adress.objects.all(),
        source='shipping_address',
        write_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'stripe_charge_id', 'amount', 'currency', 'status',
            'created_at', 'billing_address', 'shipping_address',
            'billing_address_id', 'shipping_address_id'
        ]
        read_only_fields = ['id', 'user', 'stripe_charge_id', 'status', 'created_at']



class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.IntegerField()
    sub_total = serializers.SerializerMethodField(method_name="total")
   
    class Meta:
        model = CartItem
        fields = [ 'product' , 'quantity' , 'sub_total']


    def total(self, cartItems: CartItem):
        return cartItems.quantity * cartItems.product.price




class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True , write_only=True)
    class Meta:
        model = Cart
        fields = ['id' , 'created' , 'items']


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










        