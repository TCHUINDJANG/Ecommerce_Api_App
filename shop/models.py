from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator , MaxValueValidator
from django.contrib.auth.models import AbstractBaseUser
from uuid import UUID
from django.contrib.auth.models import User



User = get_user_model()


# class User (AbstractBaseUser):
#     is_custommer = models.BooleanField(default=False)
#     is_seller = models.BooleanField(default=False)


class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# permet de classer les produits par categorie
class Category(TimestampModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/' , blank=True)
    is_active = models.BooleanField(default=True)



    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


    def __str__(self):
        return self.name
    

class Product(TimestampModel):
    seller = models.ForeignKey(User , on_delete=models.CASCADE , related_name='products' , null=True , blank=True)
    category = models.ForeignKey(Category , related_name='products' , on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200 ,unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10 , decimal_places=2 , validators=[MinValueValidator(0)])
    available = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    created_at= models.DateTimeField(auto_now_add=True)
    update_at= models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='products/' , blank=True , null=True)
    discount_price = models.DecimalField(max_digits=10 , decimal_places=2 , validators=[MinValueValidator(0)])
    sale_count = models.PositiveIntegerField(default=0 , editable=False)


    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return self.name
    
    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price
    
    # @property
    # def review_count(self):
    #     return self.review_count()
    



class Promotion(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    discount_type = models.CharField(
        max_length=10,
        choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')],
        default='percentage'
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)
    products = models.ManyToManyField(Product, related_name='products', blank=True)
    categories = models.ManyToManyField(Category, related_name='category', blank=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    code = models.CharField(max_length=20, unique=True)
    activate = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
    


class Order(TimestampModel):

    STATUS_CHOICES = [
        ('pending' , 'Pending'),
        ('processing', 'Processing'),
        ('shipped' , 'Shipped'),
        ('delivered' , 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    user = models.ForeignKey(User , related_name='oders' , on_delete=models.SET_NULL , null=True)
    status = models.CharField(max_length=20 , choices=STATUS_CHOICES , default='pending')
    shipping_adress = models.CharField(max_length=20 , null=True , blank=True)
    billing_adress = models.CharField(blank=True , null=True)
    tax = models.DecimalField(max_digits=10 , decimal_places=2 , default=0)
    total = models.DecimalField(max_digits=10 , decimal_places=2 , default=0)
    payment_method = models.CharField(max_length=50)
    payment_status = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    transaction_id = models.CharField(max_length=100 , unique=True)
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def apply_promotion(self , promotion):
        if promotion.min_order_amount and self.total <promotion.min_order_amount:
            return False
        
        if promotion.discount_type == 'percentage':
            self.discount_amount = self.total * promotion.discount_value /100

        else:
            self.discount_amount = min(promotion.discount_value , self.total)

        self.total -= self.discount_amount
        self.promotion = promotion
        self.save()
        return True


    def apply_coupon(self , coupon):
        self.total = self.total * (100 - coupon.discount) /100
        self.discount_amount = self.total * coupon.discount / 100
        self.coupon = coupon
        self.save()
        return True


    @property
    def update_total(self):
        return sum(item.price for item in self.item.all())

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


    
# Suivre les commande des clients

# cette table donne les information sur les produit comandes tel que la quantite le pric
# detaille des articles dans une commande
class OrderItem(models.Model):
    order = models.ForeignKey(Order , related_name='items' , on_delete=models.CASCADE)
    product = models.ForeignKey(Product , related_name='order_items' , on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10 , decimal_places = 2)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10 , decimal_places=2)


    def save (self , *args , **kwargs):
        self.total = self.price *self.quantity
        super().save(*args , **kwargs)
        self.order.update_total()

    def __str__(self):
        return f"{self.quantity} * {self.product.name}"
    
# liste les souhaits pour un utilisateus
class Wishlist(models.Model):
     user = models.ForeignKey(User , related_name='wishlist' , on_delete=models.SET_NULL , null=True)
     products = models.ManyToManyField(Product , related_name='wishlisted_by')

     def __str__(self):
         return f"Wishlist of {self.user.usernames}"



class Review(TimestampModel):
    product = models.ForeignKey(Product , related_name='reviews' , on_delete=models.CASCADE)
    customer = models.ForeignKey(User , related_name='reviews' , on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1) , MaxValueValidator(5)]) 
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)


    class Meta:
        unique_together = ['product']
        ordering = ['-created_at']


        def __str__(self):
            return f"{self.user.username} - {self.product.name} - {self.rating}"
        




class Adress (models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name='adress')
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.city} , {self.country}"
    
    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-created_at']


        
    

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
   
    PAYMENT_METHOD = (
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    )
   
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    currency = models.CharField(max_length=3, default='usd')
    billing_address = models.ForeignKey(Adress, on_delete=models.SET_NULL, null=True, related_name='billing_payments')
    shipping_address = models.ForeignKey(Adress, on_delete=models.SET_NULL, null=True, related_name='shipping_payments')

    def __str__(self):
        return f"Payment {self.stripe_charge_id} - {self.amount} {self.currency}"
    

    class Meta:
        ordering = ['-created_at']






class Cart(models.Model):
    id = models.UUIDField(default=UUID , editable=False , primary_key=True)
    created =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.card_id)
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart , on_delete=models.CASCADE , blank=True , null=True)
    product = models.ForeignKey(Product , on_delete=models.CASCADE , blank=True , null=True, related_name='cartitems')
    quantity = models.IntegerField(default=0)




class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile de {self.user.username}"
    


 
