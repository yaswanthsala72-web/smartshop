🛒 SmartShop — Premium Django E-Commerce Platform
SmartShop is a modern, feature-rich, and premium e-commerce web application built on Django. It is designed with visual excellence and user engagement in mind, offering intelligent product recommendations, side-by-side product comparisons, real-time analytics/security metrics, and a seamless shopping checkout flow.

✨ Features
🛍️ Comprehensive Product Catalog: Dynamic category filtering, search suggestions, and rich detail pages.
🧠 AI-Powered Product Recommendations:
Trending Products: Hot items popular across the platform.
Recommended For You: User-specific personalized product suggestions.
Similar Products & Customers Also Viewed: Intelligent related item matching on detail pages.
⚖️ Product Comparison Tool: Compare up to 4 products side-by-side with automatic badges highlighting the Lowest Price, Highest Rating, and a custom Best Overall value index.
🛒 Shopping Cart & Checkout: Quick add-to-cart, real-time item quantity adjustment, and step-by-step secure checkout.
📦 Order Tracking System: Interactive multi-stage tracking visualizer (Pending → Confirmed → Packed → Shipped → Out for Delivery → Delivered).
📊 Security & Analytics Dashboard: Built-in endpoints simulating live traffic metrics, SQL/XSS threat blocks, bot activity, and e-commerce conversion stats.
🛡️ Robust Authentication: Fully secure registration, login, and access-control middleware.
🛠️ Technology Stack
Backend: Django 4.2.30
Frontend: Responsive HTML5, Vanilla CSS3 (curated elegant color palettes, custom grid layouts), JavaScript
Database: SQLite (Development) / PostgreSQL (Production-ready via dj-database-url)
Static Assets: WhiteNoise (Compressed & cached asset delivery)
Icons: FontAwesome Icons & Outfit/Inter Google Fonts
🚀 Getting Started
📋 Prerequisites
Ensure you have Python 3.10+ installed on your system.

⚙️ Installation
Clone & Navigate into the Project:

bash

cd C:\E-commerece-code-alpha
Create and Activate a Virtual Environment (Optional but Recommended):

bash

# On Windows
python -m venv venv
.\venv\Scripts\activate
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
Install Dependencies:

bash

pip install -r requirements.txt
Run Database Migrations:

bash

python manage.py migrate
Load Sample Products (Optional): To quickly populate the storefront with beautiful mock products:

bash

python manage.py load_sample_data
Start the Development Server:

bash

python manage.py runserver
The application will be available at http://127.0.0.1:8000/.

🔑 Default Credentials
To explore the application fully, you can use the default administrator account:

Django Admin URL: http://127.0.0.1:8000/admin/
Username: admin
Password: admin123
📂 Project Directory Structure
text

E-commerece-code-alpha/
│
├── smartshop/               # Main project configuration
│   ├── settings.py          # Database, security middleware & app settings
│   ├── urls.py              # Root URL routing configurations
│   └── wsgi.py / asgi.py    # Production web server gateways
│
├── store/                   # Main application app
│   ├── management/          # Custom Django commands (e.g. seeding products)
│   ├── models.py            # Database tables (Product, Cart, Order, Review)
│   ├── views.py             # Business logic & recommendation algorithms
│   ├── forms.py             # Checkout & registration forms validation
│   └── urls.py              # Store-specific URL endpoints
│
├── templates/               # Elegant UI HTML templates
├── static/                  # Shared styling, scripts, and asset folders
├── media/                   # Uploaded product & user images
├── db.sqlite3               # SQLite development database
├── requirements.txt         # Project package dependencies
└── build.sh                 # Cloud deployment automation script
📝 Commands Cheat Sheet
Command	Action
python manage.py runserver	Starts the local web server
python manage.py makemigrations	Prepares database schema updates
python manage.py migrate	Applies prepared schema updates to the DB
python manage.py createsuperuser	Creates a new admin account
python manage.py shell	Opens an interactive Django python shell
python manage.py load_sample_data	Loads pre-configured sample products into DB
