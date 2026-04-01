from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_client_email(subject, template_name, context, recipient_list):
    """
    Utility function to send HTML emails to clients.
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER

    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_account_creation_email(client):
    subject = 'Welcome to Our Service - Account Created'
    template_name = 'emails/account_creation.html'
    context = {'client': client}
    return send_client_email(subject, template_name, context, [client.email_address])

def send_purchase_confirmation_email(client, transactions, total_amount, coupon_code):
    subject = 'Purchase Confirmation'
    template_name = 'emails/purchase_confirmation.html'
    context = {
        'client': client,
        'transactions': transactions,
        'total_amount': total_amount,
        'coupon_code': coupon_code
    }
    return send_client_email(subject, template_name, context, [client.email_address])

def send_deposit_confirmation_email(client, amount, payment_method):
    subject = 'Deposit Successful'
    template_name = 'emails/deposit_confirmation.html'
    context = {
        'client': client,
        'amount': amount,
        'payment_method': payment_method
    }
    return send_client_email(subject, template_name, context, [client.email_address])


def send_service_confirmation_email(service_request, confirm_url, decline_url):
    subject = 'Confirm your service request'
    template_name = 'emails/service_confirmation.html'
    context = {
        'client': service_request.client,
        'service_request': service_request,
        'confirm_url': confirm_url,
        'decline_url': decline_url,
    }
    return send_client_email(subject, template_name, context, [service_request.client.email_address])


def send_service_completed_email(client, transaction, service_request):
    subject = 'Service payment successful'
    template_name = 'emails/service_completed.html'
    context = {
        'client': client,
        'transaction': transaction,
        'service_request': service_request,
    }
    return send_client_email(subject, template_name, context, [client.email_address])

def send_dealer_alert_email(dealer, transaction, service_request):
    subject = 'New Service Request Confirmed'
    template_name = 'emails/dealer_alert.html'
    context = {
        'dealer': dealer,
        'transaction': transaction,
        'service_request': service_request,
    }
    return send_client_email(subject, template_name, context, [dealer.email_address])

def send_redemption_confirmation_email(client, coupon_id, items_count):
    subject = 'Coupon Redeemed Successfully'
    template_name = 'emails/redemption_confirmation.html'
    context = {
        'client': client,
        'coupon_id': coupon_id,
        'items_count': items_count
    }
    return send_client_email(subject, template_name, context, [client.email_address])

def send_share_coupon_email(sender_name, recipient_email, coupon_id, serial_number, amount=None, category=None):
    """
    Send a coupon sharing email with embedded logo.
    
    Args:
        sender_name: Name of the person sharing the coupon
        recipient_email: Email address of the recipient
        coupon_id: The coupon ID/transaction ID
        serial_number: The coupon serial number
        amount: (Optional) The coupon amount
        category: (Optional) The coupon category
    
    Returns:
        True if email sent successfully, False otherwise
    """
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from email.mime.image import MIMEImage
    import os
    import logging
    
    logger = logging.getLogger(__name__)
    
    subject = f'{sender_name} shared a coupon with you!'
    
    # Render the HTML template
    context = {
        'sender_name': sender_name,
        'coupon_id': coupon_id,
        'serial_number': serial_number,
        'amount': amount,
        'category': category
    }
    
    try:
        html_message = render_to_string('emails/share_coupon.html', context)
        plain_message = strip_tags(html_message)
        print(f"[DEBUG] Email template rendered successfully")
    except Exception as e:
        print(f"[ERROR] Failed to render email template: {e}")
        logger.error(f"Failed to render share_coupon template: {e}")
        return False
    
    from_email = settings.EMAIL_HOST_USER
    
    try:
        # Create the email message
        email = EmailMultiAlternatives(
            subject,
            plain_message,
            from_email,
            [recipient_email]
        )
        email.attach_alternative(html_message, "text/html")
        
        # Attach the logo as an embedded image
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'icon.png')
        if os.path.exists(logo_path):
            try:
                with open(logo_path, 'rb') as f:
                    logo_data = f.read()
                    logo_image = MIMEImage(logo_data)
                    logo_image.add_header('Content-ID', '<logo>')
                    logo_image.add_header('Content-Disposition', 'inline', filename='logo.png')
                    email.attach(logo_image)
                print(f"[DEBUG] Logo attached to email")
            except Exception as e:
                print(f"[WARNING] Could not attach logo image: {e}")
                logger.warning(f"Could not attach logo to coupon email: {e}")
        else:
            print(f"[WARNING] Logo image not found at: {logo_path}")
            logger.warning(f"Logo image not found at {logo_path}")
        
        print(f"[INFO] Sending coupon email to {recipient_email}")
        email.send(fail_silently=False)
        print(f"[INFO] Coupon email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error sending coupon share email: {e}")
        logger.error(f"Error sending coupon share email to {recipient_email}: {e}", exc_info=True)
        return False
