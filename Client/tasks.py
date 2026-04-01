import threading
from django.utils import timezone
from django.db.models import Sum, Case, When, DecimalField, F
from Admin.models import Transaction
from .models import ServiceRequest, Client
from Project1.email_utils import send_service_confirmation_email, send_service_completed_email, send_dealer_alert_email
import json
import random
import string


def send_service_confirmation_email_task(service_request_id, confirm_url, decline_url):
    """Send service confirmation email in a background thread."""
    def _run():
        try:
            sr = ServiceRequest.objects.get(id=service_request_id)
            send_service_confirmation_email(sr, confirm_url, decline_url)
        except Exception as e:
            print(f"[ERROR] send_service_confirmation_email_task: {e}")

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def process_service_request_task(service_request_id):
    """Process a service request (deduct balance, create transaction) in a background thread."""
    def _run():
        try:
            sr = ServiceRequest.objects.get(id=service_request_id)
            if sr.status != 'pending':
                print(f"[INFO] process_service_request_task: ServiceRequest {sr.id} not pending (status={sr.status})")
                return

            client = sr.client
            # compute balance
            balance = Transaction.objects.filter(client=client).aggregate(
                total=Sum(
                    Case(
                        When(transaction_type='deposit', then='amount'),
                        When(transaction_type__in=['purchase', 'redemption'], then=F('amount') * -1),
                        default=0,
                        output_field=DecimalField()
                    )
                )
            )['total'] or 0

            if balance < sr.amount:
                sr.status = 'cancelled'
                sr.save()
                print(f"[INFO] process_service_request_task: insufficient funds for ServiceRequest {sr.id}")
                return

            # generate coupon and serial
            now = timezone.now()
            time_str = now.strftime('%H%M%S')
            date_str = now.strftime('%Y%m%d')
            client_id = str(client.id)
            order_num = now.strftime('%f')[:4]
            random_letter = random.choice(string.ascii_uppercase)
            
            product_category = sr.product.category if sr.product else 'Services'
            categories_list = ['Building Materials', 'Electronics', 'Furniture', 'Groceries', 'Clothing', 'Automotive', 'Sports', 'Services', 'Health & Beauty', 'Books','Oil & Gas', 'Jewelry', 'Agriculture Supplies', 'Office Supplies', 'Residential Stands','Kitchen Appliances']
            
            try:
                idx = categories_list.index(product_category) + 1
                basket_category_indices = str(idx)
            except ValueError:
                basket_category_indices = "0"
            
            serial_number = f"{client_id}{basket_category_indices}{time_str}{order_num}{random_letter}"
            coupon_code = f"{client_id}{time_str}{date_str}"
            
            dealer = sr.product.dealer if sr.product else None

            transaction = Transaction.objects.create(
                transaction_type='purchase',
                amount=sr.amount,
                client=client,
                dealer=dealer,
                category=product_category,
                description=json.dumps({
                    'service_provider': sr.service_provider,
                    'beneficiaries': sr.beneficiaries,
                    'provider_contact': sr.provider_contact,
                    'service_request_id': sr.id
                }),
                coupon_code=coupon_code,
                serial_number=serial_number
            )

            sr.mark_confirmed()

            # send completion email
            send_service_completed_email(client, transaction, sr)

            # send alert to dealer
            if dealer and dealer.email_address:
                send_dealer_alert_email(dealer, transaction, sr)

        except Exception as e:
            print(f"[ERROR] process_service_request_task: {e}")

    t = threading.Thread(target=_run, daemon=True)
    t.start()