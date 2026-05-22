from django.urls import path
from . import views
from .chatbot import chatbot_api

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/review/', views.submit_review, name='submit_review'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('update-cart/<int:pk>/<str:action>/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('order-tracking/<int:order_id>/', views.order_tracking, name='order_tracking'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('api/chatbot/', chatbot_api, name='chatbot_api'),
    path('api/dashboard-stats/', views.api_dashboard_stats, name='api_dashboard_stats'),
    path('api/visual-search/', views.api_visual_search, name='api_visual_search'),
    path('compare/', views.compare_products, name='compare'),
    path('api/compare-summary/', views.api_compare_summary, name='api_compare_summary'),
]
