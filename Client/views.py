from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum, Case, When, DecimalField, F
from datetime import timedelta
from django.utils import timezone
from Admin.forms import ClientSignupForm
from Client.forms import ClientFeedbackForm
from Admin.models import Transaction, Dealer, Product
from .models import Client, Basket, BasketItem
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from Project1.email_utils import (
    send_purchase_confirmation_email,
    send_deposit_confirmation_email,
    send_share_coupon_email,
    send_account_creation_email
)
from .ai_services.ai_services import get_ai_recommendation, get_chat_response
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
import json
from decimal import Decimal

# Create your views here.
def client_login(request):
    if request.method == 'POST':
        account_name = request.POST.get('username')
        password = request.POST.get('password')
        try:
            client_user = Client.objects.get(username=account_name)
            if check_password(password, client_user.password):
                request.session['client_logged_in'] = True
                request.session['client_username'] = client_user.username
                return redirect('client_dashboard')  # Assuming you have a client dashboard
            else:
                messages.error(request, 'Invalid credentials')
        except Client.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    return render(request, 'Client/client_login.html')

def client_signup(request):
    if request.method == 'POST':
        form = ClientSignupForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.password = make_password(form.cleaned_data['password'])
            client.save()
            send_account_creation_email(client)
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('client_login')
    else:
        form = ClientSignupForm()
    return render(request, 'Client/client_signup.html', {'form': form})

def client_dashboard(request):
    if not request.session.get('client_logged_in'):
        return redirect('client_login')
    username = request.session.get('client_username')
    try:
        client = Client.objects.get(username=username)
        # Calculate account balance
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
        # Fetch recent transactions (last 10)
        recent_transactions = Transaction.objects.filter(client=client).order_by('-timestamp')[:10]
        # Fetch all products and organize by category

        from collections import defaultdict
        
        # Only fetch products that have dealers
        all_products = Product.objects.filter(dealer__isnull=False).select_related('dealer').order_by('category', 'name')
        products_by_category = defaultdict(list)
        categories = ['Building Materials', 'Electronics', 'Furniture', 'Groceries', 'Clothing', 'Automotive', 'Sports', 'Services', 'Health & Beauty', 'Books','Oil & Gas', 'Jewelry', 'Agriculture Supplies', 'Office Supplies', 'Residential Stands','Kitchen Appliances']
        
        for product in all_products:
            if product.category not in categories:
                categories.append(product.category)
            products_by_category[product.category].append(product)

        # Determine top product per category (by highest price)
        top_products_by_category = {}
        for cat in categories:
            prods = products_by_category.get(cat, [])
            if prods:
                try:
                    top = max(prods, key=lambda p: p.price if p.price is not None else 0)
                except Exception:
                    top = prods[0]
                top_products_by_category[cat] = top
            else:
                top_products_by_category[cat] = None

        context = {
            'username': username,
            'balance': balance,
            'recent_transactions': recent_transactions,
            'categories': categories,
            'products_by_category': dict(products_by_category),
            'top_products_by_category': top_products_by_category,
        }


        # Basket Context
        basket, created = Basket.objects.get_or_create(client=client)
        basket_items = basket.items.select_related('product').all()
        basket_total = basket.get_total()
        
        context['basket_items'] = basket_items
        context['basket_total'] = basket_total
        context['basket_count'] = basket_items.count()

        # AI Recommendation
        try:
            last_purchase_obj = Transaction.objects.filter(client=client, transaction_type='purchase').order_by('-timestamp').first()
            last_purchase_desc = last_purchase_obj.description if last_purchase_obj else ""
            
            ai_payload = {
                "season": "festive", # Hardcoded for demo
                "is_festive": 1,
                "last_purchase": last_purchase_desc,
                # Add other fields as needed
            }
            recommendation = get_ai_recommendation(ai_payload)
            context['recommendation'] = recommendation
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            context['recommendation'] = None

        return render(request, 'Client/client_dashboard.html',context)
    except Client.DoesNotExist:
        return redirect('client_login')

def client_account(request):
    if not request.session.get('client_logged_in'):
        return redirect('client_login')
    username = request.session.get('client_username')
    try:
        client = Client.objects.get(username=username)
        # Calculate account balance
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
        # Fetch recent transactions (last 10)
        recent_transactions = Transaction.objects.filter(client=client).order_by('-timestamp')[:10]
        context = {
            'username': username,
            'balance': balance,
            'recent_transactions': recent_transactions
        }
        return render(request, 'Client/client_account.html', context)
    except Client.DoesNotExist:
        return redirect('client_login')
def client_accounts(request):
    if not request.session.get('client_logged_in'):
        return redirect('client_login')
    username = request.session.get('client_username')
    try:
        client = Client.objects.get(username=username)
        transactions = Transaction.objects.filter(client=client).order_by('-timestamp')
        context = {
            'transactions': transactions
        }
        return render(request, 'Client/client_accounts.html', context)
    except Client.DoesNotExist:
        return redirect('client_login')

def client_purchases(request):
    if not request.session.get('client_logged_in'):
        return redirect('client_login')
    username = request.session.get('client_username')
    try:
        client = Client.objects.get(username=username)
        # Fetch all purchase transactions
        purchases = Transaction.objects.filter(client=client, transaction_type='purchase').order_by('-timestamp')
        # Define current purchases as last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        current_purchases = purchases.filter(timestamp__gte=thirty_days_ago)
        previous_purchases = purchases.filter(timestamp__lt=thirty_days_ago)
        context = {
            'username': username,
            'current_purchases': current_purchases,
            'previous_purchases': previous_purchases
        }
        return render(request, 'Client/client_purchases.html', context)
    except Client.DoesNotExist:
        return redirect('client_login')

def client_topup(request):
    if not request.session.get('client_logged_in'):
        return redirect('client_login')
    username = request.session.get('client_username')
    try:
        client = Client.objects.get(username=username)
        if request.method == 'POST':
            amount = request.POST.get('amount')
            payment_method = request.POST.get('payment_method')
            if amount and payment_method:
                # Create deposit transaction
                Transaction.objects.create(
                    transaction_type='deposit',
                    amount=amount,
                    client=client,
                    category='Topup',
                    description=f'Topup via {payment_method}'
                )
                send_deposit_confirmation_email(client, amount, payment_method)
                messages.success(request, f'Account topped up with ${amount} via {payment_method}.')
                return redirect('client_dashboard')
            else:
                messages.error(request, 'Please provide amount and select payment method.')
        context = {
            'username': username
        }
        return render(request, 'Client/client_topup.html', context)
    except Client.DoesNotExist:
        return redirect('client_login')

def client_history(request):
    if not request.session.get('client_logged_in'):
        return redirect('client_login')
    username = request.session.get('client_username')
    try:
        client = Client.objects.get(username=username)
        # Fetch all transactions
        transactions = Transaction.objects.filter(client=client).order_by('-timestamp')
        # Separate into credits (deposits) and debits (purchases/redemptions)
        credits = transactions.filter(transaction_type='deposit')
        debits = transactions.filter(transaction_type__in=['purchase', 'redemption'])
        context = {
            'username': username,
            'credits': credits,
            'debits': debits
        }
        return render(request, 'Client/client_history.html', context)
    except Client.DoesNotExist:
        return redirect('client_login')

def client_settings(request):
    if not request.session.get('client_logged_in'):
        return redirect('client_login')
    username = request.session.get('client_username')
    try:
        client = Client.objects.get(username=username)
        if request.method == 'POST':
            # Handle profile update
            client.firstname = request.POST.get('firstname', client.firstname)
            client.lastname = request.POST.get('lastname', client.lastname)
            client.phone_number = request.POST.get('phone_number', client.phone_number)
            client.email_address = request.POST.get('email_address', client.email_address)
            client.save()
            messages.success(request, 'Profile updated successfully.')
        context = {
            'username': username,
            'client': client
        }
        return render(request, 'Client/client_settings.html', context)
    except Client.DoesNotExist:
        return redirect('client_login')

def client_reset_password(request):
    if not request.session.get('client_logged_in'):
        return redirect('client_login')
    
    username = request.session.get('client_username')
    try:
        client = Client.objects.get(username=username)
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not check_password(old_password, client.password):
                messages.error(request, 'Incorrect old password')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
            else:
                client.password = make_password(new_password)
                client.save()
                messages.success(request, 'Password changed successfully')
                return redirect('client_settings')
        
        context = {
            'username': username,
            'client': client
        }
        return render(request, 'Client/reset_password.html', context)
    except Client.DoesNotExist:
        return redirect('client_login')

def add_to_basket(request, product_id):
    if not request.session.get('client_logged_in'):
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            
            client = Client.objects.get(username=request.session.get('client_username'))
            product = get_object_or_404(Product, id=product_id) # Product is imported from Admin.models
            basket, created = Basket.objects.get_or_create(client=client)
            
            item, created = BasketItem.objects.get_or_create(basket=basket, product=product)
            if not created:
                item.quantity += quantity
            else:
                item.quantity = quantity
            item.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Added to basket',
                'cart_count': basket.items.count(),
                'cart_total': basket.get_total()
            })
        except Exception as e:
            print(f"Error adding to basket: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)

def update_basket_item(request, item_id):
    if not request.session.get('client_logged_in'):
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=403)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            
            item = get_object_or_404(BasketItem, id=item_id, basket__client__username=request.session.get('client_username'))
            basket = item.basket
            if quantity > 0:
                item.quantity = quantity
                item.save()
            else:
                item.delete()
                
            return JsonResponse({
                'status': 'success', 
                'message': 'Updated',
                'item_total': item.get_cost() if quantity > 0 else 0,
                'cart_total': basket.get_total()
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
def remove_basket_item(request, item_id):
    if not request.session.get('client_logged_in'):
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=403)
    
    if request.method == 'POST':
        try:
            item = get_object_or_404(BasketItem, id=item_id, basket__client__username=request.session.get('client_username'))
            basket = item.basket
            item.delete()
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Removed',
                'cart_total': basket.get_total(),
                'cart_count': basket.items.count()
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def checkout(request):
    if not request.session.get('client_logged_in'):
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=403)
        
    if request.method == 'POST':
        client = Client.objects.get(username=request.session.get('client_username'))
        basket, created = Basket.objects.get_or_create(client=client)
        items = basket.items.select_related('product').all()
        
        if not items:
             return JsonResponse({'status': 'error', 'message': 'Basket is empty'})

        total_cost = basket.get_total()
        
        # Check Balance
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
        
        if balance < total_cost:
            return JsonResponse({'status': 'error', 'message': 'Insufficient funds'})
            
        try:
            import random
            import string
            
            # Generate common components (timezone-aware)
            now = timezone.now()
            time_str = now.strftime("%H%M%S")
            date_str = now.strftime("%Y%m%d")
            client_id = str(client.id)
            
            # Categories list for index mapping (must match the one in client_dashboard)
            categories_list = ['Building Materials', 'Electronics', 'Furniture', 'Groceries', 'Clothing', 'Automotive', 'Sports', 'Services', 'Health & Beauty', 'Books','Oil & Gas', 'Jewelry', 'Agriculture Supplies', 'Office Supplies', 'Residential Stands','Kitchen Appliances']
            
            # "id for all categories in the basket"
            # We will concatenate the indices of categories present in the basket
            basket_category_indices = ""
            for item in items:
                try:
                    # simplistic mapping: find index in list + 1
                    idx = categories_list.index(item.product.category) + 1
                    basket_category_indices += str(idx)
                except ValueError:
                    basket_category_indices += "0" # 0 if not found
            
            # Order number component (using timestamp microseconds for uniqueness in lieu of real order ID)
            order_num = now.strftime("%f")[:4] 
            
            # Coupon ID: client_id + time + date
            coupon_code = f"{client_id}{time_str}{date_str}"

            for item in items:
                # Serial number: client_id + id for all categories + time + order number + random letter
                random_letter = random.choice(string.ascii_uppercase)
                serial_number = f"{client_id}{basket_category_indices}{time_str}{order_num}{random_letter}"
                
                Transaction.objects.create(
                    transaction_type='purchase',
                    amount=item.get_cost(),
                    client=client,
                    dealer=item.product.dealer,
                    category=item.product.category,
                    description=f"Purchase: {item.quantity} x {item.product.name}",
                    coupon_code=coupon_code,
                    serial_number=serial_number
                )
            
            # Clear basket
            basket.items.all().delete()
            
            # Send Email Confirmation
            # Fetch the created transactions to include in the email
            recent_transactions = Transaction.objects.filter(client=client, coupon_code=coupon_code)
            send_purchase_confirmation_email(client, recent_transactions, total_cost, coupon_code)
            
            return JsonResponse({'status': 'success', 'message': 'Purchase successful'})
        except Exception as e:
             return JsonResponse({'status': 'error', 'message': str(e)})


def share_coupon_via_email(request):
    """
    Handle sharing coupon via email (JSON-based submission).
    This is called from the modal form with JSON data.
    """
    if not request.session.get('client_logged_in'):
        print(f"[ERROR] share_coupon_via_email: User not logged in")
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recipient_email = data.get('recipient_email', '').strip()
            coupon_id = data.get('coupon_id', '').strip()
            serial_number = data.get('serial_number', '').strip()
            amount = data.get('amount')
            category = data.get('category')
            
            # Validate email and coupon data
            if not recipient_email:
                print(f"[ERROR] share_coupon_via_email: No recipient email provided")
                return JsonResponse({'status': 'error', 'message': 'Recipient email is required'})
            
            if not coupon_id or not serial_number:
                print(f"[ERROR] share_coupon_via_email: Incomplete coupon data - coupon_id={coupon_id}, serial={serial_number}")
                return JsonResponse({'status': 'error', 'message': 'Coupon information is incomplete'})
            
            # Get sender name
            username = request.session.get('client_username')
            if not username:
                print(f"[ERROR] share_coupon_via_email: No username in session")
                return JsonResponse({'status': 'error', 'message': 'Session expired. Please log in again.'})
            
            client = Client.objects.get(username=username)
            sender_name = f"{client.firstname} {client.lastname}" if client.firstname and client.lastname else client.username
            
            print(f"[INFO] share_coupon_via_email: Sending coupon {coupon_id} to {recipient_email} from {sender_name}")
            
            # Send email
            success = send_share_coupon_email(
                sender_name=sender_name,
                recipient_email=recipient_email,
                coupon_id=coupon_id,
                serial_number=serial_number,
                amount=amount,
                category=category
            )
            
            if success:
                print(f"[INFO] share_coupon_via_email: Email successfully sent to {recipient_email}")
                return JsonResponse({'status': 'success', 'message': f'Coupon shared successfully to {recipient_email}'})
            else:
                print(f"[ERROR] share_coupon_via_email: Failed to send email")
                return JsonResponse({'status': 'error', 'message': 'Failed to send email. Please check email configuration.'})
                
        except json.JSONDecodeError as e:
            print(f"[ERROR] share_coupon_via_email: Invalid JSON - {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Invalid request data'}, status=400)
        except Client.DoesNotExist:
            print(f"[ERROR] share_coupon_via_email: Client not found")
            return JsonResponse({'status': 'error', 'message': 'Client not found'}, status=404)
        except Exception as e:
            print(f"[ERROR] share_coupon_via_email: Unexpected error - {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def share_coupon(request):
    """
    Handle sharing coupon via email (form-based submission).
    This endpoint expects POST data with coupon_code and recipient_email.
    """
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()
        recipient_email = request.POST.get('recipient_email', '').strip()
        username = request.session.get('client_username')
        
        # Validation
        if not username:
            print(f"[ERROR] share_coupon: No username in session")
            return JsonResponse({'success': False, 'message': 'Not logged in. Please log in first.'})
        
        if not coupon_code:
            print(f"[ERROR] share_coupon: No coupon code provided")
            return JsonResponse({'success': False, 'message': 'Coupon code is required.'})
        
        if not recipient_email:
            print(f"[ERROR] share_coupon: No recipient email provided")
            return JsonResponse({'success': False, 'message': 'Recipient email is required.'})
        
        try:
            # Get client from username
            client = Client.objects.get(username=username)
            print(f"[INFO] share_coupon: Client '{username}' found")
            
            # Find the transaction with this coupon_code
            transaction = Transaction.objects.filter(client=client, coupon_code=coupon_code).first()
            
            if not transaction:
                print(f"[ERROR] share_coupon: No transaction found for client '{username}' with coupon code '{coupon_code}'")
                # Debug info: show what coupons this client has
                client_coupons = Transaction.objects.filter(client=client, coupon_code__isnull=False).exclude(coupon_code='').values_list('coupon_code', flat=True)
                print(f"[DEBUG] Client's available coupons: {list(client_coupons)}")
                return JsonResponse({'success': False, 'message': 'Coupon not found. Please make sure the coupon belongs to your account.'})
            
            print(f"[INFO] share_coupon: Transaction {transaction.id} found, sending to {recipient_email}")
            
            coupon_id = transaction.id
            serial_number = transaction.serial_number
            
            # Send email with logo, coupon id, and serial number
            success = send_share_coupon_email(
                sender_name=client.username,
                recipient_email=recipient_email,
                coupon_id=coupon_id,
                serial_number=serial_number,
                amount=transaction.amount,
                category=transaction.category
            )
            
            if success:
                print(f"[INFO] share_coupon: Email successfully sent to {recipient_email}")
                return JsonResponse({'success': True, 'message': f'Coupon shared successfully to {recipient_email}'})
            else:
                print(f"[ERROR] share_coupon: Failed to send email to {recipient_email}")
                return JsonResponse({'success': False, 'message': 'Failed to send email. Please check your email configuration.'})
                
        except Client.DoesNotExist:
            print(f"[ERROR] share_coupon: Client '{username}' not found in database")
            return JsonResponse({'success': False, 'message': 'Client account not found.'})
        except Exception as e:
            print(f"[ERROR] share_coupon: Unexpected error - {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method. Please use POST.'})

def client_feedback(request):
    if not request.session.get('client_logged_in'):
        return redirect('client_login')

    # Use the username stored in session (set at login) to fetch client
    username = request.session.get('client_username')
    if not username:
        return redirect('client_login')

    try:
        client = Client.objects.get(username=username)
    except Client.DoesNotExist:
        request.session.flush()
        return redirect('client_login')

    if request.method == 'POST':
        form = ClientFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.client = client
            feedback.save()
            messages.success(request, 'Your feedback has been submitted successfully!')
            return redirect('client_feedback')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ClientFeedbackForm()
    context = {
        'client': client,
        'form': form,
    }
    return render(request, 'Client/client_feedback.html', context)


def client_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            response_text = get_chat_response(message)
            return JsonResponse({'status': 'success', 'reply': response_text})
        except Exception as e:
             return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def client_products(request, category):
    """Display all products for a given category."""
    # Ensure logged in
    if not request.session.get('client_logged_in'):
        return redirect('client_login')

    username = request.session.get('client_username')
    try:
        client = Client.objects.get(username=username)
    except Client.DoesNotExist:
        return redirect('client_login')

    # Fetch products in this category
    products = Product.objects.filter(category=category, dealer__isnull=False).select_related('dealer')

    # Basket context
    basket, created = Basket.objects.get_or_create(client=client)
    basket_items = basket.items.select_related('product').all()

    context = {
        'username': username,
        'category': category,
        'products': products,
        'basket_items': basket_items,
        'basket_total': basket.get_total(),
        'basket_count': basket_items.count(),
    }
    return render(request, 'Client/client-products.html', context)


def service_request(request, product_id):
    """Handle service-specific submissions (e.g., school fees) via JSON POST."""
    if not request.session.get('client_logged_in'):
        return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    # Required fields for generic service flow
    service_provider = data.get('service_provider', '').strip()
    amount = data.get('amount')
    beneficiaries = data.get('beneficiaries', '').strip()
    provider_contact = data.get('provider_contact', '').strip()

    if not service_provider or not amount or not beneficiaries:
        return JsonResponse({'status': 'error', 'message': 'Please provide service provider, amount and beneficiary name(s).'}, status=400)

    try:
        amount_val = Decimal(str(amount))
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid amount'}, status=400)

    try:
        # Server-side validation using form
        from Client.forms import ServiceRequestForm
        form = ServiceRequestForm({
            'service_provider': service_provider,
            'amount': amount_val,
            'beneficiaries': beneficiaries,
            'provider_contact': provider_contact,
        })
        if not form.is_valid():
            return JsonResponse({'status': 'error', 'message': 'Validation failed', 'errors': form.errors}, status=400)

        username = request.session.get('client_username')
        client = Client.objects.get(username=username)
        product = get_object_or_404(Product, id=product_id)

        # Create a pending ServiceRequest and enqueue confirmation email
        from Client.models import ServiceRequest
        sr = ServiceRequest.objects.create(
            client=client,
            product=product,
            service_provider=service_provider,
            amount=amount_val,
            beneficiaries=beneficiaries,
            provider_contact=provider_contact,
        )

        # Build confirmation and decline URLs
        from django.urls import reverse
        confirm_path = reverse('service_confirm', args=[str(sr.token)])
        confirm_url = request.build_absolute_uri(confirm_path)
        decline_path = reverse('service_decline', args=[str(sr.token)])
        decline_url = request.build_absolute_uri(decline_path)

        # Schedule background task to send confirmation email
        try:
            from Client.tasks import send_service_confirmation_email_task
            send_service_confirmation_email_task(sr.id, confirm_url, decline_url)
        except Exception as e:
            print(f"[ERROR] service_request: failed to schedule confirmation email task: {e}")
            return JsonResponse({'status': 'success', 'message': 'Service request received but failed to schedule confirmation email. Please contact support.'})

        return JsonResponse({'status': 'success', 'message': 'Service request submitted. Please check your email to confirm or decline.'})
    except Client.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Client not found'}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def service_confirm(request, token):
    """Endpoint hit from confirmation email to process payment, deduct balance and create coupon."""
    try:
        from Client.models import ServiceRequest
        sr = ServiceRequest.objects.get(token=token)
    except ServiceRequest.DoesNotExist:
        return HttpResponse('Invalid or expired confirmation link', status=404)

    if sr.status != 'pending':
        return HttpResponse('This request has already been processed.', status=400)

    # Schedule background processing and return immediate acknowledgement
    try:
        from Client.tasks import process_service_request_task
        process_service_request_task(sr.id)
    except Exception as e:
        print(f"[ERROR] service_confirm: failed to schedule processing task for ServiceRequest {sr.id}: {e}")
        return HttpResponse('Failed to schedule processing. Please contact support.', status=500)

    return render(request, 'Client/service_confirmed.html', {'service_request': sr, 'transaction': None})


def service_decline(request, token):
    """Endpoint hit from decline link in email — cancels the service request."""
    try:
        from Client.models import ServiceRequest
        sr = ServiceRequest.objects.get(token=token)
    except ServiceRequest.DoesNotExist:
        return HttpResponse('Invalid or expired link.', status=404)

    if sr.status != 'pending':
        return HttpResponse('This request has already been processed.', status=400)

    sr.status = 'cancelled'
    sr.save()
    return render(request, 'Client/service_declined.html', {'service_request': sr})
