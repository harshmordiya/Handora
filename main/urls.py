from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Categories & Products
    path('category/<slug:slug>/', views.category, name='category'),
    path('search/', views.search, name='search'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # About / Information Pages
    path('about/', views.about, name='about'),
    path('our-story/', views.our_story, name='our_story'),
    path('our-commitment/', views.our_commitment, name='our_commitment'),
    path('artisan-partners/', views.artisan_partners, name='artisan_partners'),
    path('contact/', views.contact, name='contact'),

    # Other Information
    path('faq/', views.faq, name='faq'),
    path('shipping/', views.shipping, name='shipping'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),

    # Existing Commitment Route
    path('commitment/', views.commitment, name='commitment'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'),name='logout'),

    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/',views.remove_from_wishlist,name='remove_from_wishlist' ),

    # Cart
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/',views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/',views.remove_from_cart,name='remove_from_cart'),

    # Checkout & Payment
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment_method, name='payment_method'),
    path( 'payment/verify/', views.payment_callback, name='payment_callback'),

    # COD
    path('cod_email/', views.cod_email, name='cod_email'),
    path('cod_otp/', views.cod_otp, name='cod_otp'),
    path('cod_resend/', views.cod_resend, name='cod_resend'),

    # Orders
    path('order_success/<int:order_id>/',views.order_success, name='order_success'),
    path('bill/<int:order_id>/', views.generate_bill,name='generate_bill'),


    # Password Reset
    path('password-reset/',views.password_reset, name='password_reset'),
    path('verify-reset-otp/',views.verify_reset_otp,name='verify_reset_otp'),
    path('resend-reset-otp/',views.resend_reset_otp,name='resend_reset_otp'),
    path('reset-password/', views.reset_password,name='reset_password' ),
    path('password-reset/done/',views.password_reset_done,name='password_reset_done'),

    path('receipt/<str:token>/',views.secure_receipt,name='secure_receipt'),

]