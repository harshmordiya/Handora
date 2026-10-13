from functools import wraps
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Category, Product, Order, OrderItem, Profile, ContactMessage
from .admin_forms import CategoryForm, ProductForm, OrderStatusForm, UserCreateForm, UserEditForm
import calendar
from datetime import date


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not request.user.is_staff:
            messages.error(request, 'Access denied. Staff only.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_root(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('admin_login')


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or access denied.')
    return render(request, 'admin_panel/login.html')


def admin_logout(request):
    logout(request)
    return redirect('home')


@admin_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_categories = Category.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0

    status_counts = Order.objects.values('status').annotate(count=Count('status')).order_by('status')
    status_map = {s[0]: 0 for s in Order.STATUS_CHOICES}
    for item in status_counts:
        status_map[item['status']] = item['count']

    payment_counts = Order.objects.values('payment_status').annotate(count=Count('payment_status')).order_by('payment_status')
    payment_map = {s[0]: 0 for s in Order.PAYMENT_STATUS_CHOICES}
    for item in payment_counts:
        payment_map[item['payment_status']] = item['count']

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    for order in recent_orders:
        order.display_amount = str(order.total_amount)

    status_data = []
    for value, label in Order.STATUS_CHOICES:
        count = status_map.get(value, 0)
        percentage = round((count / total_orders * 100)) if total_orders > 0 else 0
        status_data.append({
            'value': value,
            'label': label,
            'count': count,
            'percentage': percentage,
        })

    current_year = date.today().year
    monthly_revenue = []
    monthly_orders = []
    monthly_labels = []
    for month in range(1, 13):
        monthly_labels.append(calendar.month_abbr[month])
        month_orders = Order.objects.filter(created_at__year=current_year, created_at__month=month)
        month_revenue = month_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        monthly_revenue.append(float(month_revenue))
        monthly_orders.append(month_orders.count())

    status_labels = [label for value, label in Order.STATUS_CHOICES]
    status_counts_list = [status_map.get(value, 0) for value, label in Order.STATUS_CHOICES]

    categories_with_counts = Category.objects.annotate(product_count=Count('products')).order_by('-product_count')[:8]
    category_names = [cat.name for cat in categories_with_counts]
    category_product_counts = [cat.product_count for cat in categories_with_counts]

    avg_order_value = round(float(total_revenue) / total_orders, 2) if total_orders > 0 else 0

    return render(request, 'admin_panel/dashboard.html', {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_categories': total_categories,
        'total_revenue': total_revenue,
        'status_map': status_map,
        'payment_map': payment_map,
        'status_data': status_data,
        'status_total': total_orders,
        'recent_orders': recent_orders,
        'monthly_labels': monthly_labels,
        'monthly_revenue': monthly_revenue,
        'monthly_orders': monthly_orders,
        'status_labels': status_labels,
        'status_counts': status_counts_list,
        'category_names': category_names,
        'category_product_counts': category_product_counts,
        'avg_order_value': avg_order_value,
    })


@admin_required
def admin_categories(request):
    categories = Category.objects.all()
    paginator = Paginator(categories, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/categories.html', {'categories': page_obj})


@admin_required
def admin_category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    return render(request, 'admin_panel/category_form.html', {'form': form, 'action': 'Add'})


@admin_required
def admin_category_edit(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_panel/category_form.html', {'form': form, 'action': 'Edit', 'category': category})


@admin_required
def admin_category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('admin_categories')
    return render(request, 'admin_panel/category_confirm_delete.html', {'category': category})


@admin_required
def admin_products(request):
    products = Product.objects.select_related('category').all()
    search = request.GET.get('search', '')
    if search:
        # Parse Boolean filter keywords: "featured" and "bestseller"
        filter_q = Q()
        remaining_words = []

        for word in search.split():
            lower_word = word.lower()
            if lower_word == 'featured':
                filter_q &= Q(is_featured=True)
            elif lower_word == 'bestseller':
                filter_q &= Q(is_bestseller=True)
            else:
                remaining_words.append(word)

        search_text = ' '.join(remaining_words).strip()

        # Apply Boolean filters
        if filter_q.children:
            products = products.filter(filter_q)

        # Apply keyword search on remaining words
        if search_text:
            products = products.filter(
                Q(name__icontains=search_text) | Q(category__name__icontains=search_text)
            )

    paginator = Paginator(products, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/products.html', {
        'products': page_obj,
        'search_query': search,
    })


@admin_required
def admin_product_add(request):
    if request.method == 'POST':

        post_data = request.POST.copy()

        # Discount is optional.
        # If user leaves it blank, save it as 0.
        if not post_data.get('discount_percent'):
            post_data['discount_percent'] = '0'

        form = ProductForm(
            post_data,
            request.FILES
        )

        if form.is_valid():

            product = form.save()

            messages.success(
                request,
                'Product added successfully.'
            )

            return redirect('admin_products')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request,
                        f'{field}: {error}'
                    )

    else:
        form = ProductForm()

    return render(
        request,
        'admin_panel/product_form.html',
        {
            'form': form,
            'action': 'Add'
        }
    )

@admin_required
def admin_product_edit(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        return_page = request.POST.get('return_page', '1')
        return_search = request.POST.get('return_search', '')

        # Existing discount ko preserve karo
        post_data = request.POST.copy()

        if not post_data.get('discount_percent'):
            post_data['discount_percent'] = str(
                product.discount_percent or 0
            )

        # Existing availability ko preserve karo
        if 'is_available' not in post_data:
            post_data['is_available'] = (
                '1' if product.is_available else '0'
            )

        form = ProductForm(
            post_data,
            request.FILES,
            instance=product
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Product updated successfully.'
            )

            url = reverse('admin_products')

            params = []

            if return_page:
                params.append(f'page={return_page}')

            if return_search:
                params.append(f'search={return_search}')

            if params:
                url += '?' + '&'.join(params)

            return redirect(url)

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request,
                        f'{field}: {error}'
                    )

    else:
        form = ProductForm(instance=product)
        return_page = request.GET.get('page', '1')
        return_search = request.GET.get('search', '')

    return render(
        request,
        'admin_panel/product_form.html',
        {
            'form': form,
            'action': 'Edit',
            'product': product,
            'return_page': return_page,
            'return_search': return_search,
        }
    )

@admin_required
def admin_product_delete(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('admin_products')
    return render(request, 'admin_panel/product_confirm_delete.html', {'product': product})


@admin_required
def admin_product_update_discount(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        discount = request.POST.get('discount_percent', '0')
        try:
            discount = float(discount)
            if discount < 0:
                discount = 0
            elif discount > 100:
                discount = 100
        except (ValueError, TypeError):
            discount = 0
        product.discount_percent = discount
        product.save()
        messages.success(request, f'Discount updated successfully.')
    # Preserve pagination and search params
    params = []
    page = request.POST.get('page') or request.GET.get('page')
    search = request.POST.get('search') or request.GET.get('search')
    if page:
        params.append(f'page={page}')
    if search:
        params.append(f'search={search}')
    url = reverse('admin_products')
    if params:
        url += '?' + '&'.join(params)
    return redirect(url)


@admin_required
def admin_product_update_availability(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        is_available = request.POST.get('is_available') == '1'
        product.is_available = is_available
        product.save()
        messages.success(request, f'Product availability updated successfully.')
    # Preserve pagination and search params
    params = []
    page = request.POST.get('page') or request.GET.get('page')
    search = request.POST.get('search') or request.GET.get('search')
    if page:
        params.append(f'page={page}')
    if search:
        params.append(f'search={search}')
    url = reverse('admin_products')
    if params:
        url += '?' + '&'.join(params)
    return redirect(url)


@admin_required
def admin_users(request):
    users = User.objects.select_related('profile').all()
    search = request.GET.get('search', '')
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search))
    paginator = Paginator(users, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/users.html', {
        'users': page_obj,
        'search_query': search,
    })


@admin_required
def admin_user_add(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)

        if form.is_valid():
            user = form.save()

            phone = form.cleaned_data.get('phone', '').strip()

            profile, created = Profile.objects.get_or_create(
                user=user
            )

            profile.phone = phone
            profile.save()

            messages.success(
                request,
                'User created successfully.'
            )

            return redirect('admin_users')

    else:
        form = UserCreateForm()

    return render(
        request,
        'admin_panel/user_form.html',
        {
            'form': form,
            'action': 'Add'
        }
    )

@admin_required
def admin_user_edit(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        form = UserEditForm(
            request.POST,
            instance=user
        )

        if form.is_valid():
            user = form.save()

            phone = form.cleaned_data.get(
                'phone',
                ''
            ).strip()

            profile, created = Profile.objects.get_or_create(
                user=user
            )

            profile.phone = phone
            profile.save()

            messages.success(
                request,
                'User updated successfully.'
            )

            return redirect('admin_users')

    else:
        form = UserEditForm(
            instance=user
        )

    return render(
        request,
        'admin_panel/user_form.html',
        {
            'form': form,
            'action': 'Edit',
            'user_obj': user
        }
    )
@admin_required
def admin_user_delete(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('admin_users')
    return render(request, 'admin_panel/user_confirm_delete.html', {'user_obj': user})


@admin_required
def admin_orders(request):
    orders = Order.objects.select_related('user').all()
    search = request.GET.get('search', '')
    if search:
        orders = orders.filter(Q(user__username__icontains=search) | Q(full_name__icontains=search) | Q(id__icontains=search))
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    paginator = Paginator(orders, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/orders.html', {
        'orders': page_obj,
        'search_query': search,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    })


@admin_required
def admin_order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    items = order.items.select_related('product').all()
    status_form = OrderStatusForm()
    return render(request, 'admin_panel/order_detail.html', {
        'order': order,
        'items': items,
        'status_form': status_form,
    })


@admin_required
def admin_order_update_status(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            order.status = form.cleaned_data['status']
            order.save()
            messages.success(request, 'Order status updated successfully.')
            return redirect('admin_order_detail', id=order.id)
        else:
            messages.error(request, 'Invalid status value.')
    return redirect('admin_order_detail', id=order.id)


@admin_required
def admin_order_delete(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        order_id = order.id
        order.delete()
        messages.success(request, f'Order #{order_id} deleted successfully.')
        # Preserve current pagination/search/filter state in redirect
        params = []
        page = request.GET.get('page')
        search = request.GET.get('search')
        status = request.GET.get('status')
        if page:
            params.append(f'page={page}')
        if search:
            params.append(f'search={search}')
        if status:
            params.append(f'status={status}')
        url = reverse('admin_orders')
        if params:
            url += '?' + '&'.join(params)
        return redirect(url)
    return redirect('admin_orders')


@admin_required
def admin_feedback(request):
    messages_list = ContactMessage.objects.all()
    search = request.GET.get('search', '')
    if search:
        messages_list = messages_list.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        )
    paginator = Paginator(messages_list, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/feedback.html', {
        'feedback_messages': page_obj,
        'search_query': search,
        'unread_count': ContactMessage.objects.filter(is_read=False).count(),
    })


@admin_required
def admin_feedback_mark_read(request, id):

    msg = get_object_or_404(ContactMessage, id=id)

    if request.method == 'POST':
        msg.is_read = True
        msg.save()
        messages.success(request, 'Message marked as read.')

    return redirect('admin_feedback')


@admin_required
def admin_feedback_delete(request, id):
    msg = get_object_or_404(ContactMessage, id=id)
    if request.method == 'POST':
        msg.delete()
        messages.success(request, 'Feedback deleted successfully.')
    return redirect('admin_feedback')


@admin_required
def reply_feedback(request, feedback_id):
    msg = get_object_or_404(ContactMessage, id=feedback_id)
    if request.method == 'POST':
        response_text = request.POST.get('response', '').strip()
        if not response_text:
            messages.error(request, 'Please enter a response message.')
            return render(request, 'admin_panel/feedback_reply.html', {
                'msg': msg,
                'response_text': response_text,
            })
        try:
            subject = f"Re: {msg.subject}" if msg.subject else "Reply from Handora"
            email_body = f"""Dear {msg.name},

Thank you for reaching out to Handora. We have received your message and would like to respond:

Your Original Message:
Subject: {msg.subject or 'N/A'}
Message: {msg.message}

Our Response:
{response_text}

If you have any further questions, please don't hesitate to contact us.

Best regards,
Handora Customer Support
"""
            email = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[msg.email],
            )
            email.send(fail_silently=False)
            messages.success(request, f'Reply sent successfully to {msg.email}.')
            return redirect('admin_feedback')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')
            return render(request, 'admin_panel/feedback_reply.html', {
                'msg': msg,
                'response_text': response_text,
            })
    return render(request, 'admin_panel/feedback_reply.html', {'msg': msg})