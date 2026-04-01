from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings

def send_account_notification(user, password, account_type, request):
    """
    Sends an email notification to the newly created account.
    
    Args:
        user: The created user object (Location or Dealer).
        password: The raw password for the account.
        account_type: 'location' or 'dealer'.
        request: The current request object (used to build absolute URI).
    """
    if account_type == 'location':
        login_url = request.build_absolute_uri(reverse('location_login'))
        account_name = user.location_name
        email_to = user.email_address
    elif account_type == 'dealer':
        login_url = request.build_absolute_uri(reverse('dealer_login'))
        account_name = f"{user.firstname} {user.lastname}"
        email_to = user.email_address
    elif account_type == 'pos':
        login_url = request.build_absolute_uri(reverse('pos_login'))
        account_name = user.pos_name
        # POS might be assigned to a user or a location directly
        if user.user and user.user.email_address:
             email_to = user.user.email_address
        else:
             email_to = user.location.email_address
    elif account_type == 'user':
        # Assuming users login via the location portal or simply use their credentials for POS context
        try:
            login_url = request.build_absolute_uri(reverse('location_login'))
        except:
             login_url = request.build_absolute_uri('/') # Fallback
        account_name = f"{user.firstname} {user.lastname}"
        email_to = user.email_address
    else:
        return

    subject = 'Welcome to CONNECTZW - Account Created'
    message = f"Dear {account_name} your account was successfully created and your password is {password}, To login click the link. Welcome to CONNECTZW\n\nLink: {login_url}"
    
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email_to],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email to {email_to}: {e}")
