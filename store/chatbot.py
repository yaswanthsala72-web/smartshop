import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from store.models import Product, Order, CartItem


# FAQ knowledge base
FAQS = {
    'shipping': 'We offer FREE shipping on all orders. Delivery typically takes 5-7 business days.',
    'delivery': 'Estimated delivery time is 5-7 business days after order placement.',
    'return': 'We have a 7-day easy return policy. Contact support@smartshop.com to initiate a return.',
    'refund': 'Refunds are processed within 5-7 business days after we receive the returned item.',
    'payment': 'We accept Cash on Delivery (COD), UPI, and Debit/Credit Card payments.',
    'contact': 'You can reach us at support@smartshop.com or call +91 98765 43210. Hours: Mon-Sat, 9AM-9PM.',
    'account': 'You can create an account by clicking "Register" in the navbar. It\'s quick and free!',
    'cancel': 'To cancel an order, please contact us at support@smartshop.com with your Order ID.',
    'track': 'You can track your orders by visiting the "My Orders" page after logging in.',
    'discount': 'Check our homepage regularly for seasonal offers and discounts!',
    'warranty': 'Electronics products come with a 1-year manufacturer warranty.',
    'cod': 'Yes, we offer Cash on Delivery (COD) on all orders across India.',
}

GREETINGS = ['hi', 'hello', 'hey', 'hola', 'good morning', 'good evening', 'good afternoon', 'howdy', 'sup']
THANKS = ['thank', 'thanks', 'thx', 'appreciate']
BYES = ['bye', 'goodbye', 'see you', 'cya', 'later']


def get_greeting(username=None):
    name = username if username else 'there'
    return f"Hello {name}! 👋 Welcome to SmartShop. I'm your shopping assistant. I can help you with:\n\n🔍 **Product search** — _\"Show me headphones\"_\n💰 **Budget finds** — _\"Products under ₹1000\"_\n📦 **Order tracking** — _\"Track my order\"_\n❓ **FAQs** — _\"Shipping info\"_\n🏷️ **Categories** — _\"Show electronics\"_\n\nHow can I help you today?"


def search_products(query, limit=5):
    """Search products by name, description, or category."""
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query)
    ).order_by('-stock')[:limit]
    return products


def format_product_list(products, intro="Here's what I found:"):
    """Format products into a chat-friendly response."""
    if not products:
        return "😕 Sorry, I couldn't find any matching products. Try a different search term!"

    lines = [f"{intro}\n"]
    for p in products:
        stock_status = "✅ In Stock" if p.stock > 0 else "❌ Out of Stock"
        lines.append(f"🛍️ **{p.name}** — ₹{p.price}\n   {stock_status} | [View Details](/product/{p.id}/)")
    lines.append(f"\n_Found {len(products)} product(s). Click a link to view details!_")
    return '\n'.join(lines)


def process_message(message, user=None):
    """Process user message and generate a smart response."""
    msg = message.lower().strip()

    # Greetings
    if any(g in msg for g in GREETINGS):
        username = user.username if user and user.is_authenticated else None
        return get_greeting(username)

    # Thanks
    if any(t in msg for t in THANKS):
        return "You're welcome! 😊 Happy to help. Let me know if you need anything else!"

    # Goodbye
    if any(b in msg for b in BYES):
        return "Goodbye! 👋 Thanks for visiting SmartShop. Have a great day! 🌟"

    # Order tracking
    if any(w in msg for w in ['track', 'order status', 'my order', 'where is my order']):
        if user and user.is_authenticated:
            orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
            if orders:
                lines = ["📦 Here are your recent orders:\n"]
                for o in orders:
                    status_emoji = {'Pending': '🕐', 'Processing': '⚙️', 'Shipped': '🚚', 'Delivered': '✅'}.get(o.status, '📦')
                    lines.append(f"{status_emoji} **Order #{o.id}** — ₹{o.total_amount} — **{o.status}**\n   Placed on {o.created_at.strftime('%d %b %Y')}")
                lines.append("\n[View all orders →](/my-orders/)")
                return '\n'.join(lines)
            else:
                return "📦 You don't have any orders yet. Start shopping and place your first order! 🛒\n\n[Browse Products →](/#products)"
        else:
            return "🔒 Please [log in](/login/) first to track your orders."

    # Cart info
    if any(w in msg for w in ['cart', 'my cart', 'what\'s in my cart', 'view cart']):
        if user and user.is_authenticated:
            items = CartItem.objects.filter(user=user).select_related('product')
            if items:
                total = sum(i.subtotal for i in items)
                lines = [f"🛒 Your cart has **{items.count()} item(s)**:\n"]
                for i in items:
                    lines.append(f"  • {i.product.name} × {i.quantity} = ₹{i.subtotal}")
                lines.append(f"\n💰 **Total: ₹{total}**\n\n[Go to Cart →](/cart/) | [Checkout →](/checkout/)")
                return '\n'.join(lines)
            else:
                return "🛒 Your cart is empty! Browse our products and add something you love.\n\n[Shop Now →](/#products)"
        else:
            return "🔒 Please [log in](/login/) to view your cart."

    # Budget/price filter: "under ₹X" or "below X" or "less than X"
    price_match = re.search(r'(?:under|below|less than|within|budget)\s*₹?\s*(\d+)', msg)
    if price_match:
        max_price = int(price_match.group(1))
        products = Product.objects.filter(price__lte=max_price, stock__gt=0).order_by('-price')[:6]
        return format_product_list(products, f"💰 Products under ₹{max_price}:")

    # Category browsing
    categories = {
        'electronics': ['electronic', 'gadget', 'tech', 'device'],
        'clothing': ['cloth', 'wear', 'fashion', 'dress', 'shirt', 'jeans', 'hoodie'],
        'books': ['book', 'read', 'novel', 'programming book'],
        'home': ['home', 'kitchen', 'house', 'cook'],
        'sports': ['sport', 'fitness', 'gym', 'exercise', 'yoga', 'workout'],
        'beauty': ['beauty', 'skin', 'hair', 'cream', 'makeup', 'cosmetic'],
        'toys': ['toy', 'game', 'play', 'puzzle', 'kids'],
        'accessories': ['accessor', 'wallet', 'bag', 'watch', 'sunglasses'],
    }
    for cat, keywords in categories.items():
        if any(k in msg for k in keywords):
            products = Product.objects.filter(category=cat, stock__gt=0).order_by('?')[:6]
            cat_display = dict(Product.CATEGORY_CHOICES).get(cat, cat)
            return format_product_list(products, f"🏷️ **{cat_display}** products:")

    # Best/popular/recommend products
    if any(w in msg for w in ['best', 'popular', 'recommend', 'top', 'trending', 'suggestion']):
        products = Product.objects.filter(stock__gt=0).order_by('?')[:5]
        return format_product_list(products, "⭐ Here are some recommended products for you:")

    # New/latest products
    if any(w in msg for w in ['new', 'latest', 'recent', 'arrival']):
        products = Product.objects.filter(stock__gt=0).order_by('-created_at')[:5]
        return format_product_list(products, "🆕 Latest arrivals:")

    # Cheapest/affordable
    if any(w in msg for w in ['cheap', 'affordable', 'lowest', 'budget']):
        products = Product.objects.filter(stock__gt=0).order_by('price')[:5]
        return format_product_list(products, "💰 Most affordable products:")

    # Expensive/premium
    if any(w in msg for w in ['expensive', 'premium', 'luxury', 'high end', 'costly']):
        products = Product.objects.filter(stock__gt=0).order_by('-price')[:5]
        return format_product_list(products, "💎 Premium products:")

    # FAQ matching
    for key, answer in FAQS.items():
        if key in msg:
            return f"ℹ️ {answer}"

    # Help
    if any(w in msg for w in ['help', 'what can you do', 'menu', 'options']):
        return get_greeting(user.username if user and user.is_authenticated else None)

    # General product search (fallback)
    words = [w for w in msg.split() if len(w) > 2 and w not in ['show', 'find', 'search', 'get', 'want', 'need', 'looking', 'for', 'the', 'any', 'some', 'please']]
    if words:
        query = ' '.join(words)
        products = search_products(query, limit=5)
        if products:
            return format_product_list(products, f"🔍 Search results for \"{query}\":")

    # Default fallback
    return "🤔 I'm not sure I understand. Here's what I can help with:\n\n🔍 **Search products** — _\"Show me headphones\"_\n💰 **Budget finds** — _\"Products under ₹1000\"_\n📦 **Order tracking** — _\"Track my order\"_\n🛒 **Cart info** — _\"What's in my cart\"_\n❓ **FAQs** — _\"Shipping info\"_ or _\"Return policy\"_\n\nTry asking me something!"


@csrf_exempt
@require_POST
def chatbot_api(request):
    """API endpoint for chatbot messages."""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()

        if not message:
            return JsonResponse({'response': 'Please type a message!'})

        response = process_message(message, request.user)
        return JsonResponse({'response': response})

    except Exception as e:
        return JsonResponse({'response': f'Sorry, something went wrong. Please try again! 😅'}, status=500)
