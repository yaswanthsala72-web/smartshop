"""Download real product images from the web for all products."""
import os
import urllib.request
import ssl

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartshop.settings')
import django
django.setup()
from store.models import Product

# Disable SSL verification for downloading
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

MEDIA_DIR = os.path.join('media', 'product_images')
os.makedirs(MEDIA_DIR, exist_ok=True)

# Map each product to a relevant Unsplash image search keyword + unique seed
IMAGE_URLS = {
    # ELECTRONICS
    'Wireless Bluetooth Headphones': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&h=600&fit=crop',
    'Smart Fitness Watch': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&h=600&fit=crop',
    'Portable Bluetooth Speaker': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&h=600&fit=crop',
    'USB-C Fast Charger': 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&h=600&fit=crop',
    'Wireless Earbuds Pro': 'https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=600&h=600&fit=crop',
    'Mechanical Gaming Keyboard': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&h=600&fit=crop',
    '4K Webcam HD': 'https://images.unsplash.com/photo-1596742578443-7682ef5251cd?w=600&h=600&fit=crop',
    'Power Bank 20000mAh': 'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=600&h=600&fit=crop',
    'Smart LED Desk Lamp': 'https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?w=600&h=600&fit=crop',
    'Noise Cancelling Earphones': 'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=600&h=600&fit=crop',

    # CLOTHING
    'Premium Cotton T-Shirt': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&h=600&fit=crop',
    'Slim Fit Denim Jeans': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&h=600&fit=crop',
    'Casual Hoodie Jacket': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=600&h=600&fit=crop',
    'Formal Cotton Shirt': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&h=600&fit=crop',
    'Sports Track Pants': 'https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600&h=600&fit=crop',
    'Winter Wool Sweater': 'https://images.unsplash.com/photo-1434389677669-e08b4cda3a20?w=600&h=600&fit=crop',
    'Cotton Polo T-Shirt': 'https://images.unsplash.com/photo-1625910513413-5fc421e0fd4f?w=600&h=600&fit=crop',
    'Cargo Shorts': 'https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=600&h=600&fit=crop',
    'Linen Summer Shirt': 'https://images.unsplash.com/photo-1607345366928-199ea26cfe3e?w=600&h=600&fit=crop',
    'Athletic Compression Tee': 'https://images.unsplash.com/photo-1571945153237-4929e783af4a?w=600&h=600&fit=crop',

    # BOOKS
    'Python Programming Book': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&h=600&fit=crop',
    'JavaScript Mastery': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=600&h=600&fit=crop',
    'Data Science Handbook': 'https://images.unsplash.com/photo-1553729459-afe8f2e2ed65?w=600&h=600&fit=crop',
    'Clean Code Principles': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600&h=600&fit=crop',
    'System Design Interview': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600&h=600&fit=crop',
    'Machine Learning Basics': 'https://images.unsplash.com/photo-1550399105-c4db5fb85c18?w=600&h=600&fit=crop',
    'Web Development Guide': 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=600&h=600&fit=crop',
    'Django for Beginners': 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=600&h=600&fit=crop',
    'Database Design Patterns': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=600&h=600&fit=crop',
    'Cloud Computing Essentials': 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=600&h=600&fit=crop',

    # HOME & KITCHEN
    'Stainless Steel Water Bottle': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=600&h=600&fit=crop',
    'Non-Stick Cookware Set': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&h=600&fit=crop',
    'Bamboo Cutting Board': 'https://images.unsplash.com/photo-1594226801341-41427b4e5c22?w=600&h=600&fit=crop',
    'Automatic Soap Dispenser': 'https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?w=600&h=600&fit=crop',
    'LED String Lights': 'https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=600&h=600&fit=crop',
    'Ceramic Coffee Mug Set': 'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=600&h=600&fit=crop',
    'Air Purifier Compact': 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&h=600&fit=crop',
    'Stainless Steel Thermos': 'https://images.unsplash.com/photo-1570554886111-e80fcca6a029?w=600&h=600&fit=crop',
    'Scented Candle Set': 'https://images.unsplash.com/photo-1602607700009-f865ec438314?w=600&h=600&fit=crop',
    'Kitchen Organizer Rack': 'https://images.unsplash.com/photo-1556909172-54557c7e4fb7?w=600&h=600&fit=crop',

    # SPORTS & FITNESS
    'Yoga Mat Premium': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600&h=600&fit=crop',
    'Adjustable Dumbbells Set': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600&h=600&fit=crop',
    'Resistance Bands Pack': 'https://images.unsplash.com/photo-1598289431512-b97b0917affc?w=600&h=600&fit=crop',
    'Jump Rope Speed': 'https://images.unsplash.com/photo-1517963879433-6ad2b056d712?w=600&h=600&fit=crop',
    'Foam Roller Muscle': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=600&fit=crop',
    'Sports Gym Bag': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&h=600&fit=crop',
    'Fitness Gloves Pair': 'https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=600&h=600&fit=crop',
    'Ab Roller Wheel': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600&h=600&fit=crop',
    'Sports Water Bottle 1L': 'https://images.unsplash.com/photo-1523362628745-0c100150b504?w=600&h=600&fit=crop',
    'Skipping Rope Digital': 'https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=600&h=600&fit=crop',

    # BEAUTY & HEALTH
    'Organic Face Cream': 'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=600&h=600&fit=crop',
    'Vitamin C Serum': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&h=600&fit=crop',
    'Hair Growth Oil': 'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=600&h=600&fit=crop',
    'Sunscreen SPF 50': 'https://images.unsplash.com/photo-1556227702-d1e4e7b5c232?w=600&h=600&fit=crop',
    'Charcoal Face Wash': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&h=600&fit=crop',
    'Lip Balm Set Natural': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=600&h=600&fit=crop',
    'Anti-Aging Night Cream': 'https://images.unsplash.com/photo-1570194065650-d99fb4b38b17?w=600&h=600&fit=crop',
    'Aloe Vera Gel Pure': 'https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=600&h=600&fit=crop',
    'Hair Straightener Pro': 'https://images.unsplash.com/photo-1522338140262-f46f5913618a?w=600&h=600&fit=crop',
    'Perfume Gift Set': 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=600&h=600&fit=crop',

    # TOYS & GAMES
    'Building Blocks 500pc': 'https://images.unsplash.com/photo-1587654780291-39c9404d7dd0?w=600&h=600&fit=crop',
    'Remote Control Car': 'https://images.unsplash.com/photo-1581235707960-15e9b977ad38?w=600&h=600&fit=crop',
    'Board Game Collection': 'https://images.unsplash.com/photo-1611891487122-207579fd17d4?w=600&h=600&fit=crop',
    'Puzzle 1000 Pieces': 'https://images.unsplash.com/photo-1606503153255-59d8b8b82176?w=600&h=600&fit=crop',
    'Rubiks Cube Speed': 'https://images.unsplash.com/photo-1577401239170-897c1893f12b?w=600&h=600&fit=crop',
    'Science Experiment Kit': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=600&h=600&fit=crop',
    'Drone Mini Camera': 'https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=600&h=600&fit=crop',
    'Art Supply Kit': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&h=600&fit=crop',
    'Plush Teddy Bear': 'https://images.unsplash.com/photo-1559715541-5daf8a0296d0?w=600&h=600&fit=crop',
    'Magnetic Drawing Board': 'https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=600&h=600&fit=crop',

    # ACCESSORIES
    'Leather Wallet': 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=600&h=600&fit=crop',
    'Aviator Sunglasses': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&h=600&fit=crop',
    'Analog Wrist Watch': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=600&h=600&fit=crop',
    'Laptop Backpack': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&h=600&fit=crop',
    'Leather Belt Premium': 'https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=600&h=600&fit=crop',
    'Wireless Mouse Ergonomic': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&h=600&fit=crop',
    'Phone Case Premium': 'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=600&h=600&fit=crop',
    'Travel Neck Pillow': 'https://images.unsplash.com/photo-1520006403893-b1e7e70fa20b?w=600&h=600&fit=crop',
    'Cotton Socks Pack': 'https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=600&h=600&fit=crop',
    'Crossbody Sling Bag': 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&h=600&fit=crop',
}

downloaded = 0
failed = 0

for name, url in IMAGE_URLS.items():
    try:
        product = Product.objects.get(name=name)
        filename = name.lower().replace(' ', '_').replace('/', '_') + '.jpg'
        filepath = os.path.join(MEDIA_DIR, filename)

        # Download image
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, context=ctx, timeout=15)
        with open(filepath, 'wb') as f:
            f.write(response.read())

        # Update product
        product.image = f'product_images/{filename}'
        product.save()
        downloaded += 1
        print(f'  OK: {name}')
    except Exception as e:
        failed += 1
        print(f'  FAIL: {name} - {e}')

print(f'\nDone! Downloaded: {downloaded}, Failed: {failed}')
