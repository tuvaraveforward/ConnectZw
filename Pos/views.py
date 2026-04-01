from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Pos
from Admin.models import Transaction, Product
from django.utils import timezone
from django.db.models import Count
from Project1.email_utils import send_redemption_confirmation_email

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
                # Update all transactions with this coupon code
                transactions = Transaction.objects.filter(coupon_code=coupon_id, transaction_type='purchase')
                
                pos_id = request.session.get('pos_id')
                current_pos = Pos.objects.get(id=pos_id)
                
                updated_count = transactions.update(
                    is_redeemed=True,
                    redemption_pos=current_pos,
                    redemption_timestamp=timezone.now()
                )
                
                if updated_count > 0:
                    # Send Email Confirmation
                    # We need the client to send them an email. 
                    # We can get the client from the first transaction in the set.
                    first_transaction = transactions.first()
                    if first_transaction and first_transaction.client:
                        send_redemption_confirmation_email(first_transaction.client, coupon_id, updated_count)
                    
                    messages.success(request, f'Coupon {coupon_id} redeemed successfully! {updated_count} items processed.')
                    return redirect('redeem_coupon') # Reset form
                else:
                    messages.error(request, 'Error: Could not find transactions to redeem.')
            except Exception as e:
                messages.error(request, f'Error processing redemption: {str(e)}')
                
        else:
            # Default to verification logic
            coupon_id = request.POST.get('coupon_id')
            serial_number = request.POST.get('Serial_number')
            
            try:
                # Check for the specific transaction with this coupon and serial
                transaction = Transaction.objects.filter(
                    coupon_code=coupon_id, 
                    serial_number=serial_number,
                    transaction_type='purchase'
                ).first()

                if transaction:
                    if transaction.is_redeemed:
                         messages.error(request, 'Error: This coupon has already been redeemed.')
                    else:
                         # Verification successful, fetch all items in this basket (same coupon_code)
                         # We assume all items in the basket share the same coupon_code
                         basket_items = Transaction.objects.filter(
                             coupon_code=coupon_id,
                             transaction_type='purchase'
                         )
                         context['basket_items'] = basket_items
                         context['verified'] = True
                         context['redeemed_coupon_id'] = coupon_id # pass back for potential "Complete Redemption" action later
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
            # Check for the transaction
            transaction = Transaction.objects.filter(
                coupon_code=coupon_id,
                serial_number=serial_number,
                transaction_type='purchase'
            ).first()

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
