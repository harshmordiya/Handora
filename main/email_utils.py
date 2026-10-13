from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.core import signing


def send_order_confirmation_email(request, order):

    # Prevent duplicate confirmation emails
    if order.confirmation_email_sent:
        return False

    # Use registered user's email
    customer_email = ''

    if order.user and order.user.email:
        customer_email = order.user.email
    elif order.email:
        customer_email = order.email

    # If no email is available, do not send
    if not customer_email:
        return False

    # Customer name
    customer_name = order.full_name

    if not customer_name:
        customer_name = order.user.get_full_name()

    if not customer_name:
        customer_name = order.user.username

    # Get all purchased items
    items = order.items.select_related('product').all()

    # Generate absolute receipt URL

    receipt_token = signing.dumps(order.id)

    receipt_url = request.build_absolute_uri(
        reverse(
            'email_bill',
            args=[receipt_token]
        )
    )

    # Email template context
    context = {
        'order': order,
        'items': items,
        'customer_name': customer_name,
        'receipt_url': receipt_url,
    }

    # Render HTML email
    html_content = render_to_string(
        'email/order_confirmation.html',
        context
    )

    subject = f'Order Confirmation - Handora #{order.id}'

    from_email = getattr(
        settings,
        'DEFAULT_FROM_EMAIL',
        settings.EMAIL_HOST_USER
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=(
            f'Hello {customer_name},\n\n'
            f'Your Handora order #{order.id} has been confirmed.\n\n'
            f'Total Amount: ₹{order.total_amount}\n\n'
            f'View your receipt here:\n'
            f'{receipt_url}'
        ),
        from_email=from_email,
        to=[customer_email],
    )

    email.attach_alternative(
        html_content,
        'text/html'
    )

    try:
        # Send email
        email.send()

        # Mark as sent only after successful email sending
        order.confirmation_email_sent = True
        order.save(
            update_fields=['confirmation_email_sent']
        )

        return True

    except Exception:
        # Do not mark email as sent if sending fails
        return False