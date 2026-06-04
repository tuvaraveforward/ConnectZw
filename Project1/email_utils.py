import logging
import os
import threading
from email.mime.image import MIMEImage

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _send_in_thread(fn, *args, **kwargs):
    """Run fn(*args, **kwargs) in a daemon thread so it never blocks a request."""
    t = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
    t.start()


def _do_send(subject, template_name, context, recipient_list):
    """Render template and send via SMTP — called only from a background thread."""
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as exc:
        logger.error("Email send failed (%s → %s): %s", template_name, recipient_list, exc)


def send_client_email(subject, template_name, context, recipient_list):
    """Non-blocking: schedules the email in a background thread and returns True."""
    _send_in_thread(_do_send, subject, template_name, context, recipient_list)
    return True


# ── Public send functions ─────────────────────────────────────────────────────

def send_account_creation_email(client):
    return send_client_email(
        'Welcome to ConnectZw — Account Created',
        'emails/account_creation.html',
        {'client': client},
        [client.email_address],
    )


def send_purchase_confirmation_email(client, transactions, total_amount, coupon_code):
    return send_client_email(
        'Purchase Confirmation',
        'emails/purchase_confirmation.html',
        {'client': client, 'transactions': transactions,
         'total_amount': total_amount, 'coupon_code': coupon_code},
        [client.email_address],
    )


def send_deposit_confirmation_email(client, amount, payment_method):
    return send_client_email(
        'Deposit Successful',
        'emails/deposit_confirmation.html',
        {'client': client, 'amount': amount, 'payment_method': payment_method},
        [client.email_address],
    )


def send_service_confirmation_email(service_request, confirm_url, decline_url):
    return send_client_email(
        'Confirm your service request',
        'emails/service_confirmation.html',
        {'client': service_request.client, 'service_request': service_request,
         'confirm_url': confirm_url, 'decline_url': decline_url},
        [service_request.client.email_address],
    )


def send_service_completed_email(client, transaction, service_request):
    return send_client_email(
        'Service payment successful',
        'emails/service_completed.html',
        {'client': client, 'transaction': transaction, 'service_request': service_request},
        [client.email_address],
    )


def send_dealer_alert_email(dealer, transaction, service_request):
    return send_client_email(
        'New Service Request Confirmed',
        'emails/dealer_alert.html',
        {'dealer': dealer, 'transaction': transaction, 'service_request': service_request},
        [dealer.email_address],
    )


def send_redemption_confirmation_email(client, coupon_id, items_count):
    return send_client_email(
        'Coupon Redeemed Successfully',
        'emails/redemption_confirmation.html',
        {'client': client, 'coupon_id': coupon_id, 'items_count': items_count},
        [client.email_address],
    )


def send_share_coupon_email(sender_name, recipient_email, coupon_id,
                            serial_number, amount=None, category=None):
    """Non-blocking coupon share email with embedded logo."""
    context = {
        'sender_name': sender_name,
        'coupon_id': coupon_id,
        'serial_number': serial_number,
        'amount': amount,
        'category': category,
    }
    _send_in_thread(_do_send_share_coupon, recipient_email, context, sender_name)
    return True


def _do_send_share_coupon(recipient_email, context, sender_name):
    """Background worker for the coupon share email."""
    try:
        html_message = render_to_string('emails/share_coupon.html', context)
        plain_message = strip_tags(html_message)

        email = EmailMultiAlternatives(
            subject=f'{sender_name} shared a coupon with you!',
            body=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[recipient_email],
        )
        email.attach_alternative(html_message, 'text/html')

        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'icon.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<logo>')
                img.add_header('Content-Disposition', 'inline', filename='logo.png')
                email.attach(img)

        email.send(fail_silently=False)
        logger.info("Coupon share email sent to %s", recipient_email)
    except Exception as exc:
        logger.error("Coupon share email failed to %s: %s", recipient_email, exc)
