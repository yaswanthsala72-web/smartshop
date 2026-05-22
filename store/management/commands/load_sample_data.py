from django.core.management.base import BaseCommand
from store.models import Product


class Command(BaseCommand):
    help = 'Load sample products into the database'

    def handle(self, *args, **kwargs):
        products = [
            {
                'name': 'Wireless Bluetooth Headphones',
                'description': 'Premium wireless headphones with active noise cancellation, 30-hour battery life, and crystal-clear audio. Perfect for music lovers and professionals.',
                'price': 2499.00,
                'category': 'electronics',
                'stock': 25,
            },
            {
                'name': 'Smart Fitness Watch',
                'description': 'Track your health and fitness with heart rate monitoring, step counter, sleep tracking, and 7-day battery life. Water resistant up to 50 meters.',
                'price': 3999.00,
                'category': 'electronics',
                'stock': 15,
            },
            {
                'name': 'Premium Cotton T-Shirt',
                'description': 'Ultra-soft 100% organic cotton t-shirt with a modern fit. Available in multiple colors. Machine washable and wrinkle-resistant.',
                'price': 799.00,
                'category': 'clothing',
                'stock': 50,
            },
            {
                'name': 'Python Programming Book',
                'description': 'Comprehensive guide to Python programming covering basics to advanced topics including Django, Flask, and data science applications.',
                'price': 599.00,
                'category': 'books',
                'stock': 30,
            },
            {
                'name': 'Stainless Steel Water Bottle',
                'description': 'Double-wall vacuum insulated water bottle. Keeps drinks cold for 24 hours or hot for 12 hours. BPA-free and eco-friendly.',
                'price': 499.00,
                'category': 'home',
                'stock': 40,
            },
            {
                'name': 'Yoga Mat Premium',
                'description': 'Extra thick 6mm yoga mat with non-slip surface. Lightweight and portable with carrying strap. Perfect for yoga, pilates, and stretching.',
                'price': 1299.00,
                'category': 'sports',
                'stock': 20,
            },
            {
                'name': 'Leather Wallet',
                'description': 'Genuine leather bi-fold wallet with RFID protection. Multiple card slots, ID window, and coin pocket. Slim and elegant design.',
                'price': 899.00,
                'category': 'accessories',
                'stock': 35,
            },
            {
                'name': 'Organic Face Cream',
                'description': 'Natural and organic face moisturizer with vitamin E, aloe vera, and hyaluronic acid. Suitable for all skin types. Paraben-free.',
                'price': 649.00,
                'category': 'beauty',
                'stock': 45,
            },
        ]

        count = 0
        for p in products:
            obj, created = Product.objects.get_or_create(
                name=p['name'],
                defaults=p
            )
            if created:
                count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {p["name"]}'))
            else:
                self.stdout.write(f'  Exists: {p["name"]}')

        self.stdout.write(self.style.SUCCESS(f'\nDone! {count} new products added.'))
