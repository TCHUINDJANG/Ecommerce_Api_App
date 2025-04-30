from django.contrib import admin
from .models import (
    User,
    Category,
    Product,
    Cart,
    CartItem,
    Review,
    Adress,  # Note: L'orthographe correcte serait "Address"
    Order,
    OrderItem,
    Wishlist,
    Coupon,
    Promotion,
    Payment, 
    
)

# Enregistrement des modèles de base
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Review)
admin.site.register(Adress)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wishlist)
admin.site.register(Coupon)
admin.site.register(Promotion)
admin.site.register(Payment)


# Si vous voulez des personnalisations pour certains modèles :
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available', 'category')
    list_filter = ('available', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'transaction_id')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

# Désenregistrer puis réenregistrer avec la personnalisation
admin.site.unregister(Product)
admin.site.unregister(Order)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)

# Pour le modèle User personnalisé (si vous avez des champs supplémentaires)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_custommer', 'is_seller')
    list_filter = ('is_custommer', 'is_seller')

admin.site.unregister(User)  # Important si User