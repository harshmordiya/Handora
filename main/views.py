from pathlib import Path
from io import BytesIO
import os
import secrets
import datetime
import razorpay

from .email_utils import send_order_confirmation_email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import Category, Product, Profile, Wishlist, Order, OrderItem, ContactMessage
from django.db.models import Exists, OuterRef, Q
from .forms import RegisterForm
from .cart import Cart
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.core import signing
import logging
import secrets
import time
import hmac


logger = logging.getLogger(__name__)


def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)[:8]
    bestsellers = Product.objects.filter(is_bestseller=True)[:8]
    latest_products = Product.objects.all()[:8]
    return render(request, 'home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'bestsellers': bestsellers,
        'latest_products': latest_products,
    })


def category(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=cat)

    if request.user.is_authenticated:
        wishlist_subquery = Wishlist.objects.filter(
            user=request.user, product=OuterRef('pk'))
        products = products.annotate(
            in_wishlist=Exists(wishlist_subquery))
    else:
        products = products.annotate(in_wishlist=Exists(Wishlist.objects.none()))

    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'Discount':
        products = products.order_by('-discount_percent')

    paginator = Paginator(products, 24)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    return render(request, 'category.html', {
        'category': cat,
        'products': products_page,
        'sort_by': sort_by,
    })


def search(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return redirect('home')

    # Parse Boolean filter keywords: "featured" and "bestseller"
    words = query.split()
    filter_q = Q()
    keyword_words = []

    for word in words:
        lower_word = word.lower()
        if lower_word == 'featured':
            filter_q &= Q(is_featured=True)
        elif lower_word == 'bestseller':
            filter_q &= Q(is_bestseller=True)
        else:
            keyword_words.append(word)

    # Standard keyword search on remaining words
    q_objects = Q()
    for word in keyword_words:
        word_q = (
            Q(name__icontains=word) |
            Q(description__icontains=word) |
            Q(category__name__icontains=word)
        )
        if q_objects:
            q_objects |= word_q
        else:
            q_objects = word_q

    # Combine Boolean filters with keyword search
    combined_q = filter_q & q_objects

    products = Product.objects.filter(combined_q).select_related('category').distinct()

    if request.user.is_authenticated:
        wishlist_subquery = Wishlist.objects.filter(
            user=request.user, product=OuterRef('pk'))
        products = products.annotate(
            in_wishlist=Exists(wishlist_subquery))
    else:
        products = products.annotate(in_wishlist=Exists(Wishlist.objects.none()))

    paginator = Paginator(products, 24)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    return render(request, 'search_results.html', {
        'query': query,
        'products': products_page,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related,
        'in_wishlist': in_wishlist,
    })


def about(request):
    return render(request, 'about.html')


def our_story(request):
    return render(request, 'our_story.html')


def our_commitment(request):
    return render(request, 'our_commitment.html')


def artisan_partners(request):
    return render(request, 'artisan_partners.html')


def faq(request):
    return render(request, 'faq.html')


def shipping(request):
    return render(request, 'shipping.html')


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def terms(request):
    return render(request, 'terms.html')


def commitment(request):
    return render(request, 'commitment.html')


def artisan_partners(request):
    return render(request, 'artisan_partners.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not (name and email and message):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('contact')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return redirect('contact')

        ContactMessage.objects.create(
            name=name, email=email, subject=subject, message=message)
        messages.success(request, 'Your message has been sent successfully. We will get back to you soon.')
        return redirect('contact')

    return render(request, 'contact.html')


def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Account not found. Please create an account first.')
            return redirect('register')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('home')
        messages.error(request, 'Incorrect password. Please try again.')
    return render(request, 'login.html')


def password_reset(request):

    if request.method == 'POST':

        email = request.POST.get('email', '').strip()

        if email:

            user = User.objects.filter(
                email__iexact=email
            ).first()

            if user:

                # Generate a secure 6-digit OTP
                otp = f"{secrets.randbelow(1000000):06d}"

                # Store reset information in session
                request.session['reset_user_id'] = user.id
                request.session['reset_otp'] = otp
                request.session['reset_otp_expires'] = (
                    time.time() + 300
                )  # 5 minutes

                # OTP verification is not completed yet
                request.session['reset_otp_verified'] = False

                request.session.modified = True

                # Send OTP to registered email
                send_mail(
                    subject='Handora - Password Reset OTP',
                    message=(
                        f'Hello {user.get_full_name() or user.username},\n\n'
                        f'Your Handora password reset OTP is: {otp}\n\n'
                        f'This OTP is valid for 5 minutes.\n\n'
                        f'If you did not request a password reset, '
                        f'you can safely ignore this email.\n\n'
                        f'Thank you,\n'
                        f'Handora Team'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                messages.success(
                    request,
                    'A verification OTP has been sent to your registered email address.'
                )

                return redirect('verify_reset_otp')

            else:

                messages.error(
                    request,
                    'No account was found with this email address.'
                )

        else:

            messages.error(
                request,
                'Please enter your email address.'
            )

    return render(
        request,
        'password_reset.html'
    )

def verify_reset_otp(request):

    if 'reset_user_id' not in request.session:
        messages.error(
            request,
            'Please enter your email address first.'
        )
        return redirect('password_reset')

    if 'reset_otp' not in request.session:
        messages.error(
            request,
            'OTP session expired. Please request a new OTP.'
        )
        return redirect('password_reset')

    if request.method == 'POST':

        otp_entered = request.POST.get(
            'otp',
            ''
        ).strip()

        if not otp_entered:

            messages.error(
                request,
                'Please enter the OTP.'
            )

            return render(
                request,
                'verify_reset_otp.html'
            )

        expiry = request.session.get(
            'reset_otp_expires'
        )

        if not expiry or time.time() > float(expiry):

            request.session.pop(
                'reset_otp',
                None
            )

            request.session.pop(
                'reset_otp_expires',
                None
            )

            request.session.pop(
                'reset_otp_verified',
                None
            )

            request.session.modified = True

            messages.error(
                request,
                'OTP has expired. Please request a new OTP.'
            )

            return redirect('password_reset')

        stored_otp = str(
            request.session.get(
                'reset_otp',
                ''
            )
        )

        if not hmac.compare_digest(
            otp_entered,
            stored_otp
        ):

            messages.error(
                request,
                'Invalid OTP. Please try again.'
            )

            return render(
                request,
                'verify_reset_otp.html'
            )

        # OTP verified successfully
        request.session['reset_otp_verified'] = True

        # OTP should not be reusable
        request.session.pop(
            'reset_otp',
            None
        )

        request.session.pop(
            'reset_otp_expires',
            None
        )

        request.session.modified = True

        messages.success(
            request,
            'OTP verified successfully. You can now reset your password.'
        )

        return redirect('reset_password')

    return render(
        request,
        'verify_reset_otp.html'
    )

def resend_reset_otp(request):

    if 'reset_user_id' not in request.session:
        messages.error(
            request,
            'Please enter your email address first.'
        )
        return redirect('password_reset')

    user = get_object_or_404(
        User,
        id=request.session['reset_user_id']
    )

    # Generate a new 6-digit OTP
    otp = f"{secrets.randbelow(1000000):06d}"

    # Store new OTP and expiry time
    request.session['reset_otp'] = otp
    request.session['reset_otp_expires'] = time.time() + 300
    request.session['reset_otp_verified'] = False

    request.session.modified = True

    # Send new OTP to registered email
    send_mail(
        subject='Handora - Password Reset OTP',
        message=(
            f'Hello {user.get_full_name() or user.username},\n\n'
            f'Your new Handora password reset OTP is: {otp}\n\n'
            f'This OTP is valid for 5 minutes.\n\n'
            f'If you did not request a password reset, '
            f'you can safely ignore this email.\n\n'
            f'Thank you,\n'
            f'Handora Team'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    messages.success(
        request,
        'A new OTP has been sent to your registered email.'
    )

    return redirect('verify_reset_otp')

def reset_password(request):

    if 'reset_user_id' not in request.session:

        messages.error(
            request,
            'Please enter your email address first.'
        )

        return redirect('password_reset')

    # OTP verification is mandatory
    if not request.session.get(
        'reset_otp_verified',
        False
    ):

        messages.error(
            request,
            'Please verify the OTP before resetting your password.'
        )

        return redirect('verify_reset_otp')

    user = get_object_or_404(
        User,
        id=request.session['reset_user_id']
    )

    if request.method == 'POST':

        new_password = request.POST.get(
            'new_password1',
            ''
        )

        confirm_password = request.POST.get(
            'new_password2',
            ''
        )

        if new_password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

        else:

            try:

                validate_password(
                    new_password,
                    user=user
                )

                user.set_password(
                    new_password
                )

                user.save()

                # Clear password reset session data
                request.session.pop(
                    'reset_user_id',
                    None
                )

                request.session.pop(
                    'reset_otp_verified',
                    None
                )

                request.session.pop(
                    'reset_otp',
                    None
                )

                request.session.pop(
                    'reset_otp_expires',
                    None
                )

                request.session.modified = True

                messages.success(
                    request,
                    'Your password has been changed successfully.'
                )

                return redirect(
                    'password_reset_done'
                )

            except ValidationError as e:

                for error in e.messages:

                    messages.error(
                        request,
                        error
                    )

    return render(
        request,
        'password_reset_confirm.html'
    )

def password_reset_done(request):
    return render(request, 'password_reset_done.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user,
                phone=form.cleaned_data['phone']
            )
            messages.success(
                request,
                'Registration successful! Please log in.'
            )
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, f'{product.name} added to your wishlist.')
    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f'{product.name} removed from your wishlist.')
    return redirect('wishlist')


def cart_view(request):
    cart = Cart(request)
    return render(request, 'cart.html', {
        'cart_items': cart.get_items(),
        'total': cart.get_total(),
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if not product.is_available:
        messages.error(request, 'This product is currently unavailable.')
        return redirect('cart_view')
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 15:
        messages.error(request, 'Maximum quantity allowed is 15.')
        return redirect('cart_view')
    if quantity < 1:
        quantity = 1
    cart.add(product, quantity)
    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart_view')


def update_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 15:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': True,
                'message': 'Maximum quantity allowed is 15.',
            })
        messages.error(request, 'Maximum quantity allowed is 15.')
        return redirect('cart_view')
    if quantity < 1:
        quantity = 1
    cart.update(product, quantity)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'product_id': product_id,
            'subtotal': float(product.price) * quantity,
            'total': cart.get_total(),
        })
    return redirect('cart_view')


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from cart.')
    return redirect('cart_view')


@login_required
def checkout(request):
    cart = Cart(request)
    items = cart.get_items()
    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_view')
    total = cart.get_total()

    checkout_data = request.session.get('checkout_data', {})

    if not checkout_data:
        checkout_data = {}
        if request.user.is_authenticated:
            checkout_data['email'] = request.user.email or ''
            checkout_data['first_name'] = request.user.first_name or ''
            checkout_data['last_name'] = request.user.last_name or ''
            try:
                checkout_data['phone'] = request.user.profile.phone or ''
            except Profile.DoesNotExist:
                checkout_data['phone'] = ''

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        apartment = request.POST.get('apartment', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        country = request.POST.get('country', 'India').strip()

        if not all([first_name, last_name, email, phone, address, city, state, pincode, country]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'checkout.html', {
                'cart_items': items,
                'total': total,
                'checkout_data': checkout_data,
            })

        request.session['checkout_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'address': address,
            'apartment': apartment,
            'city': city,
            'state': state,
            'pincode': pincode,
            'country': country,
        }

        return redirect('payment_method')

    return render(request, 'checkout.html', {
        'cart_items': items,
        'total': total,
        'checkout_data': checkout_data,
    })


@login_required
def payment_method(request):
    cart = Cart(request)
    items = cart.get_items()
    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_view')
    total = cart.get_total()

    checkout_data = request.session.get('checkout_data', {})
    if not checkout_data:
        messages.info(request, 'Please fill in your details first.')
        return redirect('checkout')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        first_name = checkout_data.get('first_name', '')
        last_name = checkout_data.get('last_name', '')
        full_name = f"{first_name} {last_name}".strip()
        email = checkout_data.get('email', '')
        phone = checkout_data.get('phone', '')
        address = checkout_data.get('address', '')
        apartment = checkout_data.get('apartment', '')
        city = checkout_data.get('city', '')
        state = checkout_data.get('state', '')
        pincode = checkout_data.get('pincode', '')
        country = checkout_data.get('country', 'India')

        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            apartment=apartment,
            city=city,
            state=state,
            pincode=pincode,
            country=country,
            total_amount=total,
            status='Pending',
            payment_status='Pending',
            payment_method=payment_method,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].final_price,
            )

        if payment_method == 'COD':
            order.status = 'Pending'
            order.payment_status = 'Pending'
            order.save()
            request.session['cod_order_id'] = order.id
            request.session['cod_email'] = checkout_data.get('email', '')
            return redirect('cod_email')

        elif payment_method == 'RAZORPAY':
            razorpay_key = settings.RAZORPAY_KEY_ID
            razorpay_order = None
            test_mode = False

            if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
                try:
                    client = razorpay.Client(
                        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                    )
                    razorpay_order = client.order.create({
                        'amount': int(total * 100),
                        'currency': 'INR',
                        'receipt': f'order_{order.id}',
                        'notes': {
                            'order_id': str(order.id),
                        },
                    })
                    order.razorpay_order_id = razorpay_order['id']
                    order.save()
                except Exception as e:
                    logger.exception(f"Razorpay order creation failed: {e}")
                    order.payment_status = 'Failed'
                    order.save()
                    messages.error(
                        request,
                        'Unable to initialize payment. Please try again.'
                    )
                    return redirect('payment_method')
            else:
                test_mode = True
                order.razorpay_order_id = f'test_order_{order.id}'
                order.save()

            return render(request, 'payment_method.html', {
                'cart_items': items,
                'total': total,
                'order': order,
                'checkout_data': checkout_data,
                'razorpay_order_id': razorpay_order['id'] if razorpay_order else order.razorpay_order_id,
                'razorpay_key': razorpay_key,
                'razorpay_amount': int(total * 100),
                'razorpay_name': 'Handora',
                'razorpay_description': f'Order #{order.id}',
                'test_mode': test_mode,
            })

    return render(request, 'payment_method.html', {
        'cart_items': items,
        'total': total,
        'checkout_data': checkout_data,
    })


OTP_TTL_MINUTES = 5


@login_required
def cod_email(request):
    order_id = request.session.get('cod_order_id')
    if not order_id:
        messages.info(request, 'Please select a payment method first.')
        return redirect('payment_method')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Email is required.')
            return render(request, 'cod_email.html', {
                'order': order,
                'email': email,
            })

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'cod_email.html', {
                'order': order,
                'email': email,
            })

        otp = str(secrets.randbelow(900000) + 100000)
        expiry = datetime.datetime.now() + datetime.timedelta(minutes=OTP_TTL_MINUTES)

        request.session['cod_email'] = email
        request.session['cod_otp'] = otp
        request.session['cod_otp_expires'] = expiry.timestamp()

        try:
            send_mail(
                'Handora - Your COD Verification OTP',
                f'Your OTP for Cash on Delivery order #{order.id} is: {otp}\n\nThis OTP will expire in {OTP_TTL_MINUTES} minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return redirect('cod_otp')
        except Exception:
            logger.exception("Failed to send COD OTP email")
            del request.session['cod_otp']
            del request.session['cod_otp_expires']
            messages.error(request, 'Failed to send OTP. Please try again.')
            return render(request, 'cod_email.html', {
                'order': order,
                'email': email,
            })

    return render(request, 'cod_email.html', {
        'order': order,
        'email': request.session.get('cod_email', ''),
    })


@login_required
def cod_otp(request):
    order_id = request.session.get('cod_order_id')
    if not order_id:
        messages.info(request, 'Please select a payment method first.')
        return redirect('payment_method')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        otp_entered = request.POST.get('otp', '').strip()

        if not otp_entered:
            messages.error(request, 'Please enter the OTP.')
            return render(request, 'cod_otp.html', {
                'order': order,
            })

        stored_otp = request.session.get('cod_otp')
        expiry_timestamp = request.session.get('cod_otp_expires')

        if not stored_otp or not expiry_timestamp:
            messages.error(request, 'OTP session expired. Please request a new one.')
            return redirect('cod_email')

        expiry_time = datetime.datetime.fromtimestamp(float(expiry_timestamp))
        if datetime.datetime.now() > expiry_time:
            del request.session['cod_otp']
            del request.session['cod_otp_expires']
            messages.error(request, 'OTP has expired. Please request a new one.')
            return redirect('cod_email')

        if otp_entered != stored_otp:
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'cod_otp.html', {
                'order': order,
            })

        order.status = 'Confirmed'
        order.payment_status = 'Paid'
        order.email = request.session.get('cod_email', order.email)
        order.save()

        send_order_confirmation_email(request, order)

        cart = Cart(request)
        cart.clear()

        del request.session['cod_order_id']
        del request.session['cod_otp']
        del request.session['cod_otp_expires']
        del request.session['cod_email']

        messages.success(request, 'Order confirmed! Cash on Delivery.')
        return redirect('order_success', order_id=order.id)

    return render(request, 'cod_otp.html', {
        'order': order,
    })


@login_required
def cod_resend(request):
    order_id = request.session.get('cod_order_id')
    if not order_id:
        messages.info(request, 'Please select a payment method first.')
        return redirect('payment_method')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    email = request.session.get('cod_email', '')
    if not email:
        return redirect('cod_email')

    otp = str(secrets.randbelow(900000) + 100000)
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=OTP_TTL_MINUTES)

    request.session['cod_otp'] = otp
    request.session['cod_otp_expires'] = expiry.timestamp()

    try:
        send_mail(
            'Handora - Your COD Verification OTP',
            f'Your OTP for Cash on Delivery order #{order.id} is: {otp}\n\nThis OTP will expire in {OTP_TTL_MINUTES} minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        messages.success(request, 'OTP sent successfully. Please check your email.')
    except Exception:
        logger.exception("Failed to resend COD OTP email")
        messages.error(request, 'Failed to send OTP. Please try again.')

    return redirect('cod_otp')

@login_required
def payment_callback(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        payment_id = request.POST.get('razorpay_payment_id')
        signature = request.POST.get('razorpay_signature')

        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user
        )

        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:

            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET
                )
            )

            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': order.razorpay_order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature,
                })

                payment = client.payment.fetch(payment_id)
                payment_method_type = payment.get('method', '')

                method_map = {
                    'upi': 'razorpay_upi',
                    'card': 'razorpay_card',
                    'netbanking': 'razorpay_netbanking',
                    'wallet': 'razorpay_wallet',
                    'emi': 'razorpay_emi',
                }

                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.payment_status = 'Paid'
                order.status = 'Confirmed'
                order.payment_method = method_map.get(
                    payment_method_type,
                    'pending'
                )

                order.save()

                # Email failure should NOT make payment fail
                try:
                    send_order_confirmation_email(
                        request,
                        order
                    )
                except Exception as e:
                    logger.exception(
                        f"Order confirmation email failed: {e}"
                    )

                cart = Cart(request)
                cart.clear()

                messages.success(
                    request,
                    'Payment successful! Your order has been confirmed.'
                )

                return redirect(
                    'order_success',
                    order_id=order.id
                )

            except Exception as e:
                logger.exception(
                    f"Payment verification failed: {e}"
                )

                order.payment_status = 'Failed'
                order.save()

                messages.error(
                    request,
                    'Payment verification failed. Please try again.'
                )

                return redirect('payment_method')

        else:
            # Test mode fallback

            order.razorpay_payment_id = payment_id
            order.razorpay_signature = signature
            order.payment_status = 'Paid'
            order.status = 'Confirmed'
            order.payment_method = 'razorpay_upi'

            order.save()

            # Email failure should NOT affect order status
            try:
                send_order_confirmation_email(
                    request,
                    order
                )
            except Exception as e:
                logger.exception(
                    f"Order confirmation email failed: {e}"
                )

            cart = Cart(request)
            cart.clear()

            messages.success(
                request,
                'Order confirmed!'
            )

            return redirect(
                'order_success',
                order_id=order.id
            )

    return redirect('payment_method')


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})


def generate_bill_pdf(order):
    items = order.items.all()

    buffer = BytesIO()

    styles = {
        'handora_title': ParagraphStyle(
            'handora_title',
            fontName='Helvetica',
            fontSize=24,
            spaceAfter=6,
            alignment=1,
            textColor=colors.HexColor('#7B2D26'),
        ),
        'handora_subtitle': ParagraphStyle(
            'handora_subtitle',
            fontName='Helvetica',
            fontSize=12,
            spaceAfter=20,
            alignment=1,
            textColor=colors.HexColor('#666666'),
        ),
        'section_title': ParagraphStyle(
            'section_title',
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=10,
            textColor=colors.HexColor('#7B2D26'),
        ),
        'body': ParagraphStyle(
            'body',
            fontName='Helvetica',
            fontSize=10,
            spaceAfter=4,
            textColor=colors.black,
        ),
        'body_bold': ParagraphStyle(
            'body_bold',
            fontName='Helvetica-Bold',
            fontSize=10,
            spaceAfter=4,
            textColor=colors.black,
        ),
        'right': ParagraphStyle(
            'right',
            fontName='Helvetica',
            fontSize=10,
            spaceAfter=4,
            alignment=2,
            textColor=colors.black,
        ),
        'total': ParagraphStyle(
            'total',
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=4,
            textColor=colors.HexColor('#7B2D26'),
        ),
        'thank_you': ParagraphStyle(
            'thank_you',
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=4,
            alignment=1,
            textColor=colors.HexColor('#7B2D26'),
        ),
    }

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    story = []

    story.append(
        Paragraph(
            'HANDORA',
            styles['handora_title']
        )
    )

    story.append(
        Paragraph(
            'Handmade with Love',
            styles['handora_subtitle']
        )
    )

    story.append(
        Paragraph(
            'Invoice / Bill',
            styles['section_title']
        )
    )

    info_data = [
        [
            Paragraph('Order ID', styles['body_bold']),
            Paragraph(f'#{order.id}', styles['body'])
        ],
        [
            Paragraph('Order Date', styles['body_bold']),
            Paragraph(
                order.created_at.strftime(
                    '%d %B %Y at %I:%M %p'
                ),
                styles['body']
            )
        ],
        [
            Paragraph('Customer Name', styles['body_bold']),
            Paragraph(order.full_name, styles['body'])
        ],
        [
            Paragraph('Email', styles['body_bold']),
            Paragraph(order.email, styles['body'])
        ],
        [
            Paragraph('Phone', styles['body_bold']),
            Paragraph(order.phone, styles['body'])
        ],
        [
            Paragraph('Address', styles['body_bold']),
            Paragraph(
                f"{order.address}<br/>"
                f"{order.apartment}<br/>"
                f"{order.city}, {order.state} "
                f"{order.pincode}<br/>"
                f"{order.country}",
                styles['body']
            )
        ],
    ]

    info_table = Table(
        info_data,
        colWidths=[50 * mm, 90 * mm]
    )

    info_table.setStyle(
        TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ])
    )

    story.append(info_table)
    story.append(Spacer(1, 10 * mm))

    story.append(
        Paragraph(
            'Product Details',
            styles['section_title']
        )
    )

    product_data = [[
        Paragraph('Product', styles['body_bold']),
        Paragraph('Qty', styles['body_bold']),
        Paragraph('Unit Price', styles['body_bold']),
        Paragraph('Subtotal', styles['body_bold']),
    ]]

    for item in items:
        product_data.append([
            Paragraph(
                item.product.name,
                styles['body']
            ),
            Paragraph(
                str(item.quantity),
                styles['body']
            ),
            Paragraph(
                f'₹{item.price:.2f}',
                styles['body']
            ),
            Paragraph(
                f'₹{item.subtotal():.2f}',
                styles['body']
            ),
        ])

    product_table = Table(
        product_data,
        colWidths=[
            75 * mm,
            15 * mm,
            30 * mm,
            25 * mm
        ]
    )

    product_table.setStyle(
        TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5,
             colors.HexColor('#e0e0e0')),
            ('BACKGROUND', (0, 0), (-1, 0),
             colors.HexColor('#f8f9fa')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ])
    )

    story.append(product_table)
    story.append(Spacer(1, 10 * mm))

    total_data = [
        [
            Paragraph(
                'Subtotal',
                styles['body_bold']
            ),
            Paragraph(
                f'₹{order.total_amount:.2f}',
                styles['right']
            )
        ],
        [
            Paragraph(
                'Shipping',
                styles['body_bold']
            ),
            Paragraph(
                'Free',
                styles['right']
            )
        ],
        [
            Paragraph(
                'Total Amount',
                styles['total']
            ),
            Paragraph(
                f'₹{order.total_amount:.2f}',
                styles['total']
            )
        ],
    ]

    total_table = Table(
        total_data,
        colWidths=[100 * mm, 45 * mm]
    )

    total_table.setStyle(
        TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5,
             colors.HexColor('#e0e0e0')),
        ])
    )

    story.append(total_table)
    story.append(Spacer(1, 12 * mm))

    story.append(
        Paragraph(
            f"Payment Method: "
            f"{order.get_payment_method_display()}",
            styles['body_bold']
        )
    )

    story.append(
        Paragraph(
            f"Payment Status: "
            f"{order.get_payment_status_display()}",
            styles['body_bold']
        )
    )

    story.append(
        Paragraph(
            f"Order Status: "
            f"{order.get_status_display()}",
            styles['body_bold']
        )
    )

    if order.razorpay_payment_id:
        story.append(
            Paragraph(
                f"Razorpay Payment ID: "
                f"{order.razorpay_payment_id}",
                styles['body']
            )
        )

    story.append(Spacer(1, 10 * mm))

    story.append(
        Paragraph(
            'Thank you for shopping with Handora!',
            styles['thank_you']
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf


@login_required
def generate_bill(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    pdf = generate_bill_pdf(order)

    response = HttpResponse(
        pdf,
        content_type='application/pdf'
    )

    filename = f'Handora_Bill_Order_{order.id}.pdf'

    response['Content-Disposition'] = (
        f'attachment; filename="{filename}"'
    )

    return response

def send_order_confirmation_email(request, order):
    if not order.email:
        print(
            "Order confirmation email skipped: "
            "customer email is empty."
        )
        return False

    signer = signing.TimestampSigner(
        salt='handora-order-receipt'
    )

    receipt_token = signer.sign(
        str(order.id)
    )

    receipt_path = reverse(
        'secure_receipt',
        kwargs={
            'token': receipt_token
        }
    )

    site_base_url = getattr(
        settings,
        'SITE_BASE_URL',
        ''
    ).strip().rstrip('/')

    if site_base_url:
        receipt_url = (
            f'{site_base_url}{receipt_path}'
        )
    else:
        receipt_url = request.build_absolute_uri(
            receipt_path
        )

    customer_name = (
        order.full_name
        or f'{order.first_name} {order.last_name}'.strip()
        or order.user.get_full_name()
        or order.user.username
    )

    html_content = render_to_string(
        'email/order_confirmation.html',
        {
            'order': order,
            'customer_name': customer_name,
            'receipt_url': receipt_url,
            'items': order.items.select_related(
                'product'
            ),
        }
    )

    text_content = strip_tags(
        html_content
    )

    email = EmailMultiAlternatives(
        subject=(
            f'Handora - '
            f'Order Confirmation #{order.id}'
        ),
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )

    email.attach_alternative(
        html_content,
        'text/html'
    )

    email.send(
        fail_silently=False
    )

    return True

def secure_receipt(request, token):
    signer = signing.TimestampSigner(salt='handora-order-receipt')

    try:
        order_id = signer.unsign(token, max_age=60 * 60 * 24 * 30)
    except signing.SignatureExpired:
        return HttpResponse('This receipt link has expired.', status=403)
    except signing.BadSignature:
        return HttpResponse('This receipt link is invalid.', status=403)

    order = get_object_or_404(Order, id=order_id)

    pdf = generate_bill_pdf(order)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'inline; filename="Handora_Bill_Order_{order.id}.pdf"'
    )

    return response

def send_order_confirmation_email(request, order):
    if not order.email:
        print("Order confirmation email skipped: customer email is empty.")
        return False

    customer_name = (
        order.full_name
        or f'{order.first_name} {order.last_name}'.strip()
        or order.user.get_full_name()
        or order.user.username
    )

    # Generate the SAME PDF that is used for the bill
    pdf = generate_bill_pdf(order)

    html_content = render_to_string(
        'email/order_confirmation.html',
        {
            'order': order,
            'customer_name': customer_name,
            'items': order.items.select_related('product'),
        }
    )

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=f'Handora - Order Confirmation #{order.id}',
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )

    # HTML email
    email.attach_alternative(html_content, 'text/html')

    # Attach customer's actual bill PDF
    email.attach(
        f'Handora_Bill_Order_{order.id}.pdf',
        pdf,
        'application/pdf'
    )

    email.send(fail_silently=False)

    return True