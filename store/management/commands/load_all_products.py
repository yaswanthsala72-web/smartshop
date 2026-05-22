import os
import random
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.conf import settings
from store.models import Product


# Product data: 10 products per category
PRODUCTS = {
    'electronics': [
        ('Wireless Bluetooth Headphones', 'Premium wireless headphones with active noise cancellation, 30-hour battery life, and crystal-clear sound quality.', 2499),
        ('Smart Fitness Watch', 'Track your health with heart rate monitoring, step counter, sleep tracking, and 7-day battery life. Water resistant.', 3999),
        ('Portable Bluetooth Speaker', 'Compact waterproof speaker with 360-degree sound, 12-hour playtime, and built-in microphone for calls.', 1799),
        ('USB-C Fast Charger', 'Ultra-fast 65W GaN charger with dual ports. Compatible with laptops, tablets, and smartphones.', 1299),
        ('Wireless Earbuds Pro', 'True wireless earbuds with ANC, transparency mode, and premium sound. IPX5 water resistant.', 4499),
        ('Mechanical Gaming Keyboard', 'RGB backlit mechanical keyboard with blue switches, anti-ghosting, and programmable macro keys.', 3499),
        ('4K Webcam HD', 'Ultra HD 4K webcam with auto-focus, built-in ring light, and noise-canceling microphone for streaming.', 2999),
        ('Power Bank 20000mAh', 'High-capacity portable charger with fast charging, LED display, and triple USB output ports.', 1499),
        ('Smart LED Desk Lamp', 'Touch-control LED desk lamp with 5 brightness levels, color temperature adjustment, and USB charging port.', 1899),
        ('Noise Cancelling Earphones', 'In-ear noise cancelling earphones with Hi-Res audio, tangle-free cable, and comfortable fit.', 999),
    ],
    'clothing': [
        ('Premium Cotton T-Shirt', 'Ultra-soft 100% organic cotton t-shirt with modern fit. Machine washable and wrinkle-resistant.', 799),
        ('Slim Fit Denim Jeans', 'Classic slim fit jeans made from premium stretch denim. Comfortable all-day wear with modern styling.', 1999),
        ('Casual Hoodie Jacket', 'Warm fleece-lined hoodie with front zipper, kangaroo pocket, and adjustable drawstring hood.', 1499),
        ('Formal Cotton Shirt', 'Crisp formal shirt in premium cotton with button-down collar. Perfect for office and events.', 1299),
        ('Sports Track Pants', 'Lightweight breathable track pants with elastic waist, zipper pockets, and tapered fit.', 899),
        ('Winter Wool Sweater', 'Cozy merino wool sweater with ribbed cuffs and hem. Warm, stylish, and perfect for cold weather.', 2499),
        ('Cotton Polo T-Shirt', 'Classic polo t-shirt in pique cotton with embroidered logo. Smart casual essential.', 699),
        ('Cargo Shorts', 'Durable cotton cargo shorts with multiple pockets. Perfect for outdoor adventures and casual wear.', 999),
        ('Linen Summer Shirt', 'Breathable pure linen shirt for hot weather. Relaxed fit with rolled-up sleeve tabs.', 1599),
        ('Athletic Compression Tee', 'Moisture-wicking compression t-shirt for workouts. Four-way stretch and anti-odor technology.', 599),
    ],
    'books': [
        ('Python Programming Book', 'Comprehensive guide covering basics to advanced Python including Django, Flask, and data science.', 599),
        ('JavaScript Mastery', 'Complete JavaScript handbook from ES6+ to React, Node.js, and modern web development patterns.', 699),
        ('Data Science Handbook', 'Learn data science with Python, pandas, NumPy, and machine learning. Includes real-world projects.', 849),
        ('Clean Code Principles', 'Master the art of writing clean, maintainable code. Best practices from industry experts.', 549),
        ('System Design Interview', 'Prepare for system design interviews with scalable architecture patterns and real examples.', 799),
        ('Machine Learning Basics', 'Introduction to ML algorithms, neural networks, and deep learning with practical examples.', 999),
        ('Web Development Guide', 'Full-stack web development with HTML, CSS, JavaScript, React, and Node.js. Beginner friendly.', 649),
        ('Django for Beginners', 'Step-by-step guide to building web applications with Django. Includes 5 complete projects.', 499),
        ('Database Design Patterns', 'Learn SQL, NoSQL, database optimization, indexing, and scalable data architecture patterns.', 749),
        ('Cloud Computing Essentials', 'Master AWS, Azure, and GCP. Deploy, scale, and manage cloud infrastructure effectively.', 899),
    ],
    'home': [
        ('Stainless Steel Water Bottle', 'Double-wall vacuum insulated bottle. Keeps drinks cold 24hrs or hot 12hrs. BPA-free.', 499),
        ('Non-Stick Cookware Set', 'Premium 5-piece non-stick cookware set with heat-resistant handles and tempered glass lids.', 3499),
        ('Bamboo Cutting Board', 'Eco-friendly bamboo cutting board with juice groove and anti-slip edges. Knife-friendly surface.', 699),
        ('Automatic Soap Dispenser', 'Touchless infrared sensor soap dispenser with adjustable volume. Hygienic and battery operated.', 899),
        ('LED String Lights', 'Warm white fairy lights with 100 LEDs, 10 meters. Waterproof with 8 lighting modes for decoration.', 399),
        ('Ceramic Coffee Mug Set', 'Set of 4 premium ceramic mugs with modern design. Microwave and dishwasher safe. 350ml capacity.', 799),
        ('Air Purifier Compact', 'HEPA filter air purifier for rooms up to 300 sq ft. Removes 99.97% of allergens and dust.', 4999),
        ('Stainless Steel Thermos', 'Vacuum insulated thermos flask with pour-through stopper. Keeps beverages hot for 18 hours.', 1299),
        ('Scented Candle Set', 'Set of 3 natural soy wax candles with essential oils. Lavender, vanilla, and jasmine scents.', 599),
        ('Kitchen Organizer Rack', 'Multi-tier stainless steel organizer for spices, utensils, and condiments. Space-saving design.', 1199),
    ],
    'sports': [
        ('Yoga Mat Premium', 'Extra thick 6mm yoga mat with non-slip surface. Lightweight and portable with carrying strap.', 1299),
        ('Adjustable Dumbbells Set', 'Space-saving adjustable dumbbells from 2.5kg to 15kg. Quick-change weight system.', 5999),
        ('Resistance Bands Pack', 'Set of 5 resistance bands with different strengths. Perfect for home workouts and rehabilitation.', 499),
        ('Jump Rope Speed', 'Professional speed jump rope with ball bearings, adjustable length, and comfortable foam handles.', 349),
        ('Foam Roller Muscle', 'High-density foam roller for deep tissue massage, muscle recovery, and flexibility improvement.', 799),
        ('Sports Gym Bag', 'Spacious gym bag with shoe compartment, wet pocket, and adjustable shoulder strap. Water-resistant.', 1499),
        ('Fitness Gloves Pair', 'Breathable workout gloves with wrist support and padded palms. Anti-slip grip for weightlifting.', 599),
        ('Ab Roller Wheel', 'Double-wheel ab roller with knee pad for core strengthening. Ergonomic handles with foam grip.', 449),
        ('Sports Water Bottle 1L', 'BPA-free sports bottle with time marker, motivational quotes, and leak-proof flip-top lid.', 299),
        ('Skipping Rope Digital', 'Digital counting jump rope with LCD display showing jumps, calories, and time. Cordless option.', 699),
    ],
    'beauty': [
        ('Organic Face Cream', 'Natural moisturizer with vitamin E, aloe vera, and hyaluronic acid. For all skin types. Paraben-free.', 649),
        ('Vitamin C Serum', 'Brightening serum with 20% Vitamin C, hyaluronic acid, and niacinamide. Reduces dark spots.', 899),
        ('Hair Growth Oil', 'Ayurvedic hair oil with bhringraj, amla, and coconut oil. Strengthens hair and reduces hair fall.', 449),
        ('Sunscreen SPF 50', 'Broad spectrum sunscreen with SPF 50 PA+++. Lightweight, non-greasy, and water-resistant formula.', 599),
        ('Charcoal Face Wash', 'Deep cleansing face wash with activated charcoal. Removes impurities and excess oil effectively.', 349),
        ('Lip Balm Set Natural', 'Set of 4 organic lip balms with shea butter. Flavors: strawberry, vanilla, mint, and honey.', 299),
        ('Anti-Aging Night Cream', 'Retinol-enriched night cream that reduces fine lines and wrinkles. Wake up with youthful skin.', 1299),
        ('Aloe Vera Gel Pure', '99% pure aloe vera gel for face, body, and hair. Soothes sunburn and moisturizes dry skin.', 249),
        ('Hair Straightener Pro', 'Ceramic plate hair straightener with adjustable temperature. Fast heat-up and auto shut-off.', 1999),
        ('Perfume Gift Set', 'Luxury perfume set with 3 fragrances: floral, woody, and citrus. Long-lasting 8-hour scent.', 2499),
    ],
    'toys': [
        ('Building Blocks 500pc', '500-piece colorful building blocks set compatible with major brands. Stimulates creativity.', 1499),
        ('Remote Control Car', 'High-speed RC car with 2.4GHz remote, rechargeable battery, and all-terrain wheels.', 1999),
        ('Board Game Collection', 'Family board game set with 10 classic games including chess, ludo, snakes & ladders, and more.', 899),
        ('Puzzle 1000 Pieces', 'Premium quality 1000-piece jigsaw puzzle with beautiful landscape artwork. Great for adults.', 599),
        ('Rubiks Cube Speed', 'Professional speed cube with smooth rotation and corner cutting. Competition grade quality.', 349),
        ('Science Experiment Kit', 'Educational science kit with 50+ experiments in chemistry, physics, and biology. Ages 8+.', 1299),
        ('Drone Mini Camera', 'Foldable mini drone with 720p camera, altitude hold, and one-key takeoff. Great for beginners.', 3499),
        ('Art Supply Kit', 'Complete art set with 120 pieces including colored pencils, markers, crayons, and sketch pad.', 799),
        ('Plush Teddy Bear', 'Soft and cuddly 18-inch teddy bear made with premium plush fabric. Perfect gift for kids.', 699),
        ('Magnetic Drawing Board', 'Colorful magnetic drawing board with stamps and stylus. Erase and redraw endlessly. Non-toxic.', 449),
    ],
    'accessories': [
        ('Leather Wallet', 'Genuine leather bi-fold wallet with RFID protection. Multiple card slots and coin pocket.', 899),
        ('Aviator Sunglasses', 'Classic aviator sunglasses with UV400 protection, polarized lenses, and metal frame.', 1299),
        ('Analog Wrist Watch', 'Elegant analog watch with leather strap, Japanese quartz movement, and water resistance.', 2499),
        ('Laptop Backpack', 'Anti-theft laptop backpack with USB charging port, padded compartment, and water-resistant fabric.', 1799),
        ('Leather Belt Premium', 'Genuine leather belt with brushed metal buckle. Reversible black/brown design. Adjustable size.', 699),
        ('Wireless Mouse Ergonomic', 'Ergonomic wireless mouse with silent clicks, adjustable DPI, and USB-C rechargeable battery.', 899),
        ('Phone Case Premium', 'Shock-absorbing phone case with military-grade drop protection. Slim design with raised bezels.', 499),
        ('Travel Neck Pillow', 'Memory foam travel pillow with adjustable clasp. Soft velour cover and compact carrying bag.', 599),
        ('Cotton Socks Pack', 'Pack of 6 premium cotton socks with cushioned sole. Breathable and moisture-wicking material.', 399),
        ('Crossbody Sling Bag', 'Compact crossbody sling bag with multiple compartments. Water-resistant nylon with adjustable strap.', 999),
    ],
}

# Color palettes for each category
COLORS = {
    'electronics': [(41, 128, 185), (44, 62, 80), (52, 152, 219)],
    'clothing': [(155, 89, 182), (142, 68, 173), (108, 52, 131)],
    'books': [(39, 174, 96), (46, 204, 113), (22, 160, 133)],
    'home': [(230, 126, 34), (243, 156, 18), (211, 84, 0)],
    'sports': [(231, 76, 60), (192, 57, 43), (203, 67, 53)],
    'beauty': [(241, 196, 15), (247, 220, 111), (248, 194, 145)],
    'toys': [(26, 188, 156), (22, 160, 133), (72, 201, 176)],
    'accessories': [(149, 165, 166), (127, 140, 141), (108, 122, 137)],
}

ICONS = {
    'electronics': ['🎧', '⌚', '🔊', '🔌', '🎵', '⌨️', '📷', '🔋', '💡', '🎶'],
    'clothing': ['👕', '👖', '🧥', '👔', '🩳', '🧶', '👕', '🩳', '👔', '🏃'],
    'books': ['📘', '📗', '📊', '📖', '🏗️', '🤖', '🌐', '🐍', '💾', '☁️'],
    'home': ['🥤', '🍳', '🔪', '🧴', '💡', '☕', '🌬️', '🥤', '🕯️', '🗄️'],
    'sports': ['🧘', '🏋️', '💪', '🤸', '🏃', '🎒', '🧤', '💪', '🥤', '🤸'],
    'beauty': ['🧴', '✨', '💇', '☀️', '🧼', '💋', '🌙', '🌿', '💇', '🌸'],
    'toys': ['🧱', '🏎️', '🎲', '🧩', '🎯', '🔬', '🚁', '🎨', '🧸', '✏️'],
    'accessories': ['👛', '🕶️', '⌚', '🎒', '👔', '🖱️', '📱', '😴', '🧦', '👜'],
}


def create_product_image(name, category, index, save_path):
    """Generate a visually appealing product image."""
    width, height = 600, 600
    colors = COLORS.get(category, [(100, 100, 100)])
    base_color = colors[index % len(colors)]

    # Create gradient background
    img = Image.new('RGB', (width, height), base_color)
    draw = ImageDraw.Draw(img)

    # Add decorative elements
    r, g, b = base_color
    lighter = (min(r+40, 255), min(g+40, 255), min(b+40, 255))
    darker = (max(r-40, 0), max(g-40, 0), max(b-40, 0))

    # Draw circles for decoration
    draw.ellipse([350, -50, 650, 250], fill=lighter)
    draw.ellipse([-100, 400, 200, 700], fill=darker)
    draw.ellipse([400, 400, 550, 550], fill=lighter, outline=None)

    # Draw a white card area
    draw.rounded_rectangle([60, 80, 540, 520], radius=20, fill=(255, 255, 255, 200), outline=None)
    # Since PIL doesn't support alpha on RGB, use a light shade
    card_color = (min(r+120, 250), min(g+120, 250), min(b+120, 250))
    draw.rounded_rectangle([60, 80, 540, 520], radius=20, fill=card_color)

    # Add icon/emoji text
    icons = ICONS.get(category, ['📦'])
    icon = icons[index % len(icons)]

    try:
        # Try to use a larger font
        title_font = ImageFont.truetype('arial.ttf', 28)
        small_font = ImageFont.truetype('arial.ttf', 16)
    except:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Draw product name (wrapped)
    words = name.split()
    lines = []
    current = ''
    for w in words:
        test = current + ' ' + w if current else w
        if len(test) > 18:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)

    y_start = 200
    for i, line in enumerate(lines):
        draw.text((100, y_start + i * 40), line, fill=darker, font=title_font)

    # Draw category label
    draw.rounded_rectangle([100, 140, 100 + len(category) * 14 + 30, 175], radius=12, fill=base_color)
    draw.text((115, 145), category.upper(), fill=(255, 255, 255), font=small_font)

    # Draw decorative line
    draw.rectangle([100, y_start + len(lines) * 40 + 10, 300, y_start + len(lines) * 40 + 13], fill=base_color)

    # Bottom bar
    draw.rounded_rectangle([60, 530, 540, 580], radius=15, fill=base_color)
    draw.text((80, 540), 'SmartShop', fill=(255, 255, 255), font=small_font)

    img.save(save_path)


class Command(BaseCommand):
    help = 'Load 80 products (10 per category) with generated images'

    def handle(self, *args, **kwargs):
        media_dir = os.path.join(settings.MEDIA_ROOT, 'product_images')
        os.makedirs(media_dir, exist_ok=True)

        total = 0
        for category, items in PRODUCTS.items():
            self.stdout.write(f'\n--- {category.upper()} ---')
            for i, (name, desc, price) in enumerate(items):
                # Generate image
                filename = f"{category}_{i+1}.png"
                filepath = os.path.join(media_dir, filename)
                create_product_image(name, category, i, filepath)

                # Create product
                stock = random.randint(10, 50)
                obj, created = Product.objects.update_or_create(
                    name=name,
                    defaults={
                        'description': desc,
                        'price': price,
                        'category': category,
                        'stock': stock,
                        'image': f'product_images/{filename}',
                    }
                )
                status = 'Created' if created else 'Updated'
                total += 1
                self.stdout.write(f'  {status}: {name}')

        self.stdout.write(self.style.SUCCESS(f'\nDone! {total} products loaded with images.'))
