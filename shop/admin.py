from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
    Category,
    Product,
    Cart,
    CartItem,
    Review,
    Adress,  # Correction orthographique
    Order,
    OrderItem,
    Wishlist,
    Coupon,
    Promotion,
    Payment,
    Profile,
)

# Configuration des modèles avec personnalisations

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'birth_date')  # Adaptez avec vos champs réels
    search_fields = ('user__username', 'country')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'available', 'category')
    list_filter = ('available', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'transaction_id')
    inlines = [OrderItemInline]

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    # Ajoutez d'autres personnalisations si nécessaire

# Enregistrement des modèles

# 1. D'abord désenregistrer les modèles par défaut
admin.site.unregister(User)

# 2. Enregistrer les modèles avec leurs configurations personnalisées
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)

# 3. Enregistrer les autres modèles sans personnalisation
models_to_register = [
    Category,
    Cart,
    CartItem,
    Review,
    Adress,
    Wishlist,
    Coupon,
    Promotion,
    Payment,
]

for model in models_to_register:
    admin.site.register(model)