from django.urls import path
from . import admin_views

urlpatterns = [
    path('', admin_views.admin_root, name='admin_root'),
    path('login/', admin_views.admin_login, name='admin_login'),
    path('logout/', admin_views.admin_logout, name='admin_logout'),
    path('dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),

    path('categories/', admin_views.admin_categories, name='admin_categories'),
    path('categories/add/', admin_views.admin_category_add, name='admin_category_add'),
    path('categories/<int:id>/edit/', admin_views.admin_category_edit, name='admin_category_edit'),
    path('categories/<int:id>/delete/', admin_views.admin_category_delete, name='admin_category_delete'),

    path('products/', admin_views.admin_products, name='admin_products'),
    path('products/add/', admin_views.admin_product_add, name='admin_product_add'),
    path('products/<int:id>/edit/', admin_views.admin_product_edit, name='admin_product_edit'),
    path('products/<int:id>/delete/', admin_views.admin_product_delete, name='admin_product_delete'),
    path('products/<int:id>/update-availability/', admin_views.admin_product_update_availability, name='admin_product_update_availability'),
    path('products/<int:id>/update-discount/', admin_views.admin_product_update_discount, name='admin_product_update_discount'),

    path('users/', admin_views.admin_users, name='admin_users'),
    path('users/add/', admin_views.admin_user_add, name='admin_user_add'),
    path('users/<int:id>/edit/', admin_views.admin_user_edit, name='admin_user_edit'),
    path('users/<int:id>/delete/', admin_views.admin_user_delete, name='admin_user_delete'),

    path('orders/', admin_views.admin_orders, name='admin_orders'),
    path('orders/<int:id>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('orders/<int:id>/update-status/', admin_views.admin_order_update_status, name='admin_order_update_status'),
    path('orders/<int:id>/delete/', admin_views.admin_order_delete, name='admin_order_delete'),

    path('feedback/', admin_views.admin_feedback, name='admin_feedback'),
    path('feedback/<int:id>/mark-read/', admin_views.admin_feedback_mark_read, name='admin_feedback_mark_read'),
    path('feedback/<int:id>/delete/', admin_views.admin_feedback_delete, name='admin_feedback_delete'),
    path('feedback/<int:feedback_id>/reply/', admin_views.reply_feedback, name='admin_feedback_reply'),
]
