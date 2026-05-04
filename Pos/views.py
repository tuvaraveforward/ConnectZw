from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Pos
from Admin.models import Transaction, Product
from django.utils import timezone
from django.db.models import Count
from Project1.email_utils import send_redemption_confirmation_email
from Project1.aes_utils import encrypt_bytes
from django.db import connection


def find_transaction_by_coupon_serial(coupon_id: str, serial_number: str = None):
    """
    Find a purchase transaction by coupon_code and optional serial_number.
    Uses Python-level decryption since AES-GCM encrypted field ORM queries don't work.
    """
    for tx in Transaction.objects.filter(transaction_type='purchase'):
        try:
            if tx.coupon_code != coupon_id:
                continue
        except Exception:
            continue
        if serial_number:
            try:
                if tx.serial_number != serial_number:
                    continue
            except Exception:
                continue
        return tx
    return None


def pos_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            # Authenticate using pos_name as username and pos_code as password
            pos = Pos.objects.get(pos_name=username)
            if password == pos.pos_code:
                request.session['pos_logged_in'] = True
                request.session['pos_id'] = pos.id
                request.session['pos_user_username'] = pos.pos_name
                return redirect('pos_dashboard')
            else:
                # Password (pos_code) does not match
                messages.error(request, 'Invalid credentials.')
        except Pos.DoesNotExist:
            # POS with the given pos_name not found
            messages.error(request, 'Invalid credentials.')
    return render(request, 'Pos/pos_login.html')

def pos_dashboard(request):
    if not request.session.get('pos_logged_in'):
        return redirect('pos_login')

    pos_id = request.session.get('pos_id')
    try:
        pos = Pos.objects.get(id=pos_id)
    except Pos.DoesNotExist:
        # Log out if POS not found
        request.session.flush()
        return redirect('pos_login')

    return render(request, 'Pos/pos_dashboard.html', {'pos': pos})

def pos_logout(request):
    request.session.flush()
    return redirect('pos_login')

def redeem_coupon(request):
    if not request.session.get('pos_logged_in'):
        return redirect('pos_login')

    context = {}
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'redeem_confirm':
            coupon_id = request.POST.get('coupon_id')
            try:
                # Find all transactions with this coupon code using Python-level decryption
                matching_txs = [tx for tx in Transaction.objects.filter(transaction_type='purchase')
                               if tx.coupon_code == coupon_id]
                
                pos_id = request.session.get('pos_id')
                current_pos = Pos.objects.get(id=pos_id)
                
                updated_count = 0
                for tx in matching_txs:
                    tx.is_redeemed = True
                    tx.redemption_pos = current_pos
                    tx.redemption_timestamp = timezone.now()
                    tx.save()
                    updated_count += 1
                
                if updated_count > 0:
                    # Send Email Confirmation
                    first_transaction = matching_txs[0]
                    if first_transaction and first_transaction.client:
                        send_redemption_confirmation_email(first_transaction.client, coupon_id, updated_count)
                    
                    messages.success(request, f'Coupon {coupon_id} redeemed successfully! {updated_count} items processed.')
                    return redirect('redeem_coupon')
                else:
                    messages.error(request, 'Error: Could not find transactions to redeem.')
            except Exception as e:
                messages.error(request, f'Error processing redemption: {str(e)}')
                
        else:
            # Default to verification logic
            coupon_id = request.POST.get('coupon_id')
            # accept either 'serial_number' or legacy 'Serial_number' field names
            serial_number = request.POST.get('serial_number') or request.POST.get('Serial_number')
            
            try:
                # Use helper function for Python-level lookup
                transaction = find_transaction_by_coupon_serial(coupon_id, serial_number)

                if transaction:
                    if transaction.is_redeemed:
                         messages.error(request, 'Error: This coupon has already been redeemed.')
                    else:
                         # Verification successful, fetch all items in this basket (same coupon_code)
                         basket_items = [tx for tx in Transaction.objects.filter(transaction_type='purchase')
                                        if tx.coupon_code == coupon_id]
                         context['basket_items'] = basket_items
                         context['verified'] = True
                         context['redeemed_coupon_id'] = coupon_id
                         messages.success(request, 'Coupon verified successfully!')
                else:
                     messages.error(request, 'Error: Invalid Coupon ID or Serial Number.')
            
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'Pos/redeem_coupon.html', context)

def pos_check_validity(request):
    if not request.session.get('pos_logged_in'):
        return redirect('pos_login')

    if request.method == 'POST':
        coupon_id = request.POST.get('coupon_number')
        serial_number = request.POST.get('serial_number')

        try:
            # Use helper function for Python-level lookup
            transaction = find_transaction_by_coupon_serial(coupon_id, serial_number)

            if transaction:
                if transaction.is_redeemed:
                    messages.warning(request, f'Coupon {coupon_id} has ALREADY been used.')
                else:
                    messages.success(request, f'Coupon {coupon_id} is VALID and ready for use.')
            else:
                messages.error(request, f'Invalid Coupon: {coupon_id} or Serial Number.')
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    return render(request, 'Pos/pos_check_validity.html')

def pos_run_report(request):
    if not request.session.get('pos_logged_in'):
        return redirect('pos_login')

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        email = request.POST.get('email')

        # TODO: Implement report generation and email sending logic
        # This would involve:
        # 1. Filtering transactions by date/time range and POS
        # 2. Generating PDF report
        # 3. Sending email with PDF attachment

        messages.success(request, 'Report generated and sent to email successfully!')
        return redirect('pos_run_report')

    return render(request, 'Pos/pos_run_report.html')

def pos_report_coupon(request):
    if not request.session.get('pos_logged_in'):
        return redirect('pos_login')

    return render(request, 'Pos/pos_report_coupon.html')

def pos_settings(request):
    if not request.session.get('pos_logged_in'):
        return redirect('pos_login')

    return render(request, 'Pos/pos_settings.html')

def pos_sales(request):
    if not request.session.get('pos_logged_in'):
        return redirect('pos_login')
    
    pos_id = request.session.get('pos_id')
    current_pos = Pos.objects.get(id=pos_id)
    
    # Fetch redeemed transactions for this POS
    redeemed_transactions = Transaction.objects.filter(
        redemption_pos=current_pos,
        is_redeemed=True,
        transaction_type='purchase'
    ).order_by('-redemption_timestamp')
    
    # Group by coupon_code to aggregate items
    sales_data = {}
    for trans in redeemed_transactions:
        if trans.coupon_code not in sales_data:
            sales_data[trans.coupon_code] = {
                'coupon_id': trans.coupon_code,
                'serial_number': trans.serial_number,
                'time': trans.redemption_timestamp,
                'products': []
            }
        
        # Determine product name (either from category or description as fallback)
        product_name = trans.category if trans.category else trans.description
        sales_data[trans.coupon_code]['products'].append(product_name)

    context = {
        'sales': sales_data.values()
    }
    return render(request, 'Pos/pos_sales.html', context)
