import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, CartItem, Order, OrderItem, Review
from .forms import RegisterForm, CheckoutForm, ReviewForm
from .recommendations import (
    get_similar_products, get_trending_products,
    get_recommended_for_user, get_customers_also_viewed, get_top_rated_products
)


def home(request):
    """Home page with product listing, search, category filter, and recommendations."""
    products = Product.objects.all()
    categories = Product.CATEGORY_CHOICES
    query = request.GET.get('q', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    category = request.GET.get('category', '')
    if category:
        products = products.filter(category=category)

    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()

    # Recommendations
    trending = get_trending_products(8)
    recommended = get_recommended_for_user(request.user, 8)

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category,
        'cart_count': cart_count,
        'trending': trending,
        'recommended': recommended,
    }
    return render(request, 'home.html', context)


def product_detail(request, pk):
    """Display product details with reviews and recommendations."""
    product = get_object_or_404(Product, pk=pk)
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()

    reviews = product.reviews.select_related('user').all()
    user_review = None
    review_form = ReviewForm()

    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, product=product).first()

    similar = get_similar_products(product, 4)
    also_viewed = get_customers_also_viewed(product, 4)

    context = {
        'product': product,
        'cart_count': cart_count,
        'reviews': reviews,
        'user_review': user_review,
        'review_form': review_form,
        'similar_products': similar,
        'also_viewed': also_viewed,
    }
    return render(request, 'product_detail.html', context)


@login_required
def submit_review(request, pk):
    """Submit or update a product review."""
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        existing = Review.objects.filter(user=request.user, product=product).first()
        if existing:
            form = ReviewForm(request.POST, instance=existing)
        else:
            form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Your review has been submitted! ⭐')
        else:
            messages.error(request, 'Please fix the errors in your review.')

    return redirect('product_detail', pk=pk)


@login_required
def add_to_cart(request, pk):
    """Add a product to the user's cart."""
    product = get_object_or_404(Product, pk=pk)
    if product.stock <= 0:
        messages.error(request, f'"{product.name}" is out of stock.')
        return redirect('home')

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, product=product, defaults={'quantity': 1}
    )
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Updated "{product.name}" quantity in your cart.')
        else:
            messages.warning(request, f'Cannot add more. Only {product.stock} available.')
    else:
        messages.success(request, f'"{product.name}" has been added to your cart!')

    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


@login_required
def cart(request):
    """Display the user's shopping cart."""
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    total = sum(item.subtotal for item in cart_items)
    cart_count = cart_items.count()
    context = {'cart_items': cart_items, 'total': total, 'cart_count': cart_count}
    return render(request, 'cart.html', context)


@login_required
def update_cart(request, pk, action):
    """Update cart item quantity."""
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, f'Only {cart_item.product.stock} available.')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, f'"{cart_item.product.name}" removed from cart.')
    return redirect('cart')


@login_required
def remove_from_cart(request, pk):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'"{name}" has been removed from your cart.')
    return redirect('cart')


@login_required
def checkout(request):
    """Display checkout form."""
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('home')

    total = sum(item.subtotal for item in cart_items)
    initial = {'full_name': request.user.get_full_name() or request.user.username, 'email': request.user.email}
    form = CheckoutForm(initial=initial)
    context = {'form': form, 'cart_items': cart_items, 'total': total, 'cart_count': cart_items.count()}
    return render(request, 'checkout.html', context)


@login_required
def place_order(request):
    """Process the order with payment handling."""
    if request.method != 'POST':
        return redirect('checkout')

    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('home')

    form = CheckoutForm(request.POST)
    if form.is_valid():
        total = sum(item.subtotal for item in cart_items)
        order = form.save(commit=False)
        order.user = request.user
        order.total_amount = total

        # Read payment method from custom radio buttons
        order.payment_method = request.POST.get('payment_method', 'COD')

        # Generate transaction ID
        order.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"

        # Set payment status based on method
        if order.payment_method == 'COD':
            order.payment_status = 'Pending'
        else:
            order.payment_status = 'Paid'

        order.save()

        for item in cart_items:
            OrderItem.objects.create(
                order=order, product=item.product,
                quantity=item.quantity, price=item.product.price,
            )
            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()
        messages.success(request, 'Your order has been placed successfully!')
        return redirect('order_success', order_id=order.id)
    else:
        total = sum(item.subtotal for item in cart_items)
        context = {'form': form, 'cart_items': cart_items, 'total': total, 'cart_count': cart_items.count()}
        messages.error(request, 'Please correct the errors below.')
        return render(request, 'checkout.html', context)


@login_required
def order_success(request, order_id):
    """Display order confirmation."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart_count = CartItem.objects.filter(user=request.user).count()
    context = {'order': order, 'cart_count': cart_count}
    return render(request, 'order_success.html', context)


@login_required
def my_orders(request):
    """Display order history."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    cart_count = CartItem.objects.filter(user=request.user).count()
    context = {'orders': orders, 'cart_count': cart_count}
    return render(request, 'my_orders.html', context)


@login_required
def order_tracking(request, order_id):
    """Display detailed order tracking page."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart_count = CartItem.objects.filter(user=request.user).count()

    stages = [
        ('Pending', 'fas fa-clock', 'Order placed'),
        ('Confirmed', 'fas fa-check-circle', 'Order confirmed'),
        ('Packed', 'fas fa-box', 'Order packed'),
        ('Shipped', 'fas fa-shipping-fast', 'Shipped out'),
        ('Out for Delivery', 'fas fa-truck', 'Out for delivery'),
        ('Delivered', 'fas fa-home', 'Delivered'),
    ]
    status_list = [s[0] for s in stages]
    current_idx = status_list.index(order.status) if order.status in status_list else 0

    tracking_stages = []
    for i, (status, icon, label) in enumerate(stages):
        tracking_stages.append({
            'status': status, 'icon': icon, 'label': label,
            'completed': i <= current_idx, 'current': i == current_idx,
        })

    context = {
        'order': order, 'cart_count': cart_count,
        'tracking_stages': tracking_stages, 'progress': order.tracking_progress,
    }
    return render(request, 'order_tracking.html', context)


def register_user(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(request.GET.get('next', '/'))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_user(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def api_dashboard_stats(request):
    """API endpoint returning live analytics and security data."""
    from django.db.models import Sum, Count, Avg
    from django.contrib.auth.models import User
    import random

    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_users = User.objects.count()
    avg_order_value = Order.objects.aggregate(avg=Avg('total_amount'))['avg'] or 0

    # Category distribution
    categories = {}
    for cat_val, cat_label in Product.CATEGORY_CHOICES:
        categories[cat_label] = Product.objects.filter(category=cat_val).count()

    # Recent orders
    recent_orders = []
    for o in Order.objects.select_related('user').order_by('-created_at')[:5]:
        recent_orders.append({
            'id': o.id,
            'user': o.user.username,
            'total': float(o.total_amount),
            'status': o.status,
            'payment': o.payment_method,
            'date': o.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    # Simulated security events (real-time feel)
    threat_types = ['SQL Injection', 'XSS Attempt', 'Brute Force', 'DDoS Probe', 'Bot Traffic', 'Port Scan']
    security_events = []
    for i in range(6):
        security_events.append({
            'type': threat_types[i],
            'blocked': random.randint(10, 500),
            'severity': random.choice(['Low', 'Medium', 'High', 'Critical']),
            'status': 'Blocked',
        })

    # Fraud score simulation
    fraud_stats = {
        'transactions_scanned': total_orders,
        'flagged': max(0, int(total_orders * 0.02)),
        'blocked': max(0, int(total_orders * 0.01)),
        'score': round(random.uniform(97.0, 99.9), 1),
    }

    return JsonResponse({
        'products': total_products,
        'orders': total_orders,
        'revenue': float(total_revenue),
        'users': total_users,
        'avg_order': round(float(avg_order_value), 2),
        'categories': categories,
        'recent_orders': recent_orders,
        'security': security_events,
        'fraud': fraud_stats,
    })


def api_visual_search(request):
    """API endpoint for visual/text search with AI-like matching."""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})

    # Search by name, description, and category
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__icontains=query)
    )[:12]

    results = []
    for p in products:
        results.append({
            'id': p.pk,
            'name': p.name,
            'price': float(p.price),
            'image': p.image.url if p.image else '',
            'category': p.get_category_display(),
            'stock': p.stock,
            'rating': p.avg_rating,
        })

    return JsonResponse({'results': results, 'count': len(results)})


def compare_products(request):
    """Compare up to 4 products side-by-side."""
    ids = request.GET.getlist('ids')
    # Also support comma-separated
    if len(ids) == 1 and ',' in ids[0]:
        ids = ids[0].split(',')

    ids = [int(i) for i in ids if i.isdigit()][:4]
    products = list(Product.objects.filter(pk__in=ids))

    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()

    # Find best values for highlighting
    best = {}
    if products:
        prices = [(p.pk, float(p.price)) for p in products]
        ratings = [(p.pk, p.avg_rating) for p in products]
        stocks = [(p.pk, p.stock) for p in products]
        best['lowest_price'] = min(prices, key=lambda x: x[1])[0]
        best['highest_rating'] = max(ratings, key=lambda x: x[1])[0]
        best['best_stock'] = max(stocks, key=lambda x: x[1])[0]

        # Best overall: score = (norm_rating * 0.4) + (norm_inv_price * 0.35) + (norm_stock * 0.25)
        max_price = max(p[1] for p in prices) or 1
        max_rating = max(p[1] for p in ratings) or 1
        max_stock = max(p[1] for p in stocks) or 1
        scores = []
        for p in products:
            r = p.avg_rating / max_rating if max_rating else 0
            pr = 1 - (float(p.price) / max_price) if max_price else 0
            s = p.stock / max_stock if max_stock else 0
            score = r * 0.4 + pr * 0.35 + s * 0.25
            scores.append((p.pk, score))
        best['overall'] = max(scores, key=lambda x: x[1])[0]

    context = {
        'products': products,
        'best': best,
        'cart_count': cart_count,
    }
    return render(request, 'compare.html', context)


def api_compare_summary(request):
    """Generate AI-powered comparison summary."""
    ids = request.GET.getlist('ids')
    if len(ids) == 1 and ',' in ids[0]:
        ids = ids[0].split(',')
    ids = [int(i) for i in ids if i.isdigit()][:4]
    products = list(Product.objects.filter(pk__in=ids))

    if len(products) < 2:
        return JsonResponse({'summary': 'Add at least 2 products to compare.'})

    # Generate smart summary
    sorted_by_price = sorted(products, key=lambda p: p.price)
    sorted_by_rating = sorted(products, key=lambda p: p.avg_rating, reverse=True)

    lines = []
    cheapest = sorted_by_price[0]
    priciest = sorted_by_price[-1]
    top_rated = sorted_by_rating[0]

    lines.append(f"💰 **{cheapest.name}** offers the best value at ₹{cheapest.price}.")
    if priciest.pk != cheapest.pk:
        lines.append(f"💎 **{priciest.name}** is the premium choice at ₹{priciest.price}.")
    if top_rated.avg_rating > 0:
        lines.append(f"⭐ **{top_rated.name}** has the highest rating ({top_rated.avg_rating}/5).")

    # Stock insights
    out_of_stock = [p for p in products if p.stock <= 0]
    if out_of_stock:
        names = ', '.join(p.name for p in out_of_stock)
        lines.append(f"⚠️ **{names}** {'is' if len(out_of_stock)==1 else 'are'} currently out of stock.")

    # Best overall recommendation
    max_price = max(float(p.price) for p in products) or 1
    max_rating = max(p.avg_rating for p in products) or 1
    max_stock = max(p.stock for p in products) or 1
    best_score, best_product = 0, products[0]
    for p in products:
        r = p.avg_rating / max_rating if max_rating else 0
        pr = 1 - (float(p.price) / max_price) if max_price else 0
        s = p.stock / max_stock if max_stock else 0
        score = r * 0.4 + pr * 0.35 + s * 0.25
        if score > best_score:
            best_score, best_product = score, p

    lines.append(f"\n🏆 **Best Overall: {best_product.name}** — Best balance of price, rating, and availability.")

    return JsonResponse({'summary': '\n'.join(lines)})
