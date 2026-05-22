"""AI Recommendation Engine for SmartShop."""
from django.db.models import Avg, Count, Q
from .models import Product, Order, OrderItem, CartItem, Review


def get_similar_products(product, limit=8):
    """Get products in the same category, excluding the current one."""
    return Product.objects.filter(
        category=product.category, stock__gt=0
    ).exclude(pk=product.pk).order_by('?')[:limit]


def get_trending_products(limit=8):
    """Get most ordered products."""
    trending_ids = (
        OrderItem.objects.values('product')
        .annotate(order_count=Count('id'))
        .order_by('-order_count')[:limit]
    )
    ids = [item['product'] for item in trending_ids]
    products = Product.objects.filter(id__in=ids, stock__gt=0)
    if products.count() < limit:
        extra = Product.objects.filter(stock__gt=0).exclude(id__in=ids).order_by('?')[:limit - products.count()]
        return list(products) + list(extra)
    return products


def get_top_rated_products(limit=8):
    """Get highest rated products."""
    return Product.objects.filter(
        stock__gt=0, reviews__isnull=False
    ).annotate(
        avg_rat=Avg('reviews__rating')
    ).order_by('-avg_rat')[:limit]


def get_recommended_for_user(user, limit=8):
    """Get personalized recommendations based on user's cart and order history."""
    if not user.is_authenticated:
        return Product.objects.filter(stock__gt=0).order_by('?')[:limit]

    # Get categories from user's cart and orders
    cart_categories = CartItem.objects.filter(user=user).values_list('product__category', flat=True)
    order_categories = OrderItem.objects.filter(order__user=user).values_list('product__category', flat=True)
    
    user_categories = set(list(cart_categories) + list(order_categories))

    # Get products user already has
    cart_product_ids = CartItem.objects.filter(user=user).values_list('product_id', flat=True)
    order_product_ids = OrderItem.objects.filter(order__user=user).values_list('product_id', flat=True)
    exclude_ids = set(list(cart_product_ids) + list(order_product_ids))

    if user_categories:
        products = Product.objects.filter(
            category__in=user_categories, stock__gt=0
        ).exclude(id__in=exclude_ids).order_by('?')[:limit]

        if products.count() < limit:
            extra = Product.objects.filter(stock__gt=0).exclude(
                id__in=exclude_ids
            ).exclude(id__in=[p.id for p in products]).order_by('?')[:limit - products.count()]
            return list(products) + list(extra)
        return products

    return Product.objects.filter(stock__gt=0).order_by('?')[:limit]


def get_customers_also_viewed(product, limit=6):
    """Get products that other customers also bought when they bought this product."""
    # Find orders containing this product
    order_ids = OrderItem.objects.filter(product=product).values_list('order_id', flat=True)
    
    # Find other products in those orders
    also_bought_ids = (
        OrderItem.objects.filter(order_id__in=order_ids)
        .exclude(product=product)
        .values('product')
        .annotate(count=Count('id'))
        .order_by('-count')[:limit]
    )
    ids = [item['product'] for item in also_bought_ids]
    products = Product.objects.filter(id__in=ids, stock__gt=0)
    
    if products.count() < limit:
        extra = get_similar_products(product, limit - products.count())
        return list(products) + list(extra)
    return products
