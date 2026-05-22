from django.contrib import admin
from .models import Product, CartItem, Order, OrderItem, Review


class OrderItemInline(admin.TabularInline):
    """Inline display for order items within the Order admin view."""
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'subtotal']

    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'avg_rating', 'review_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock']
    list_per_page = 20

    def avg_rating(self, obj):
        return obj.avg_rating
    avg_rating.short_description = 'Rating'

    def review_count(self, obj):
        return obj.review_count
    review_count.short_description = 'Reviews'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'product__name', 'comment']
    list_per_page = 20


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity']
    list_filter = ['user']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'total_amount', 'status', 'payment_method', 'payment_status', 'transaction_id', 'created_at']
    list_filter = ['status', 'payment_method', 'payment_status', 'created_at']
    search_fields = ['full_name', 'email', 'mobile', 'transaction_id']
    list_editable = ['status', 'payment_status']
    inlines = [OrderItemInline]
    list_per_page = 20


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order']
