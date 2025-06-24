from django.shortcuts import render, redirect
from django.http import JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import razorpay
import json
import logging

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

# Configure logging
logger = logging.getLogger(__name__)

def place_order(request, total=0, quantity=0):
    current_user = request.user

    # Check if cart is empty
    cart_items = CartItem.objects.filter(user=current_user)
    if not cart_items.exists():
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    tax = (3.5 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Save order details
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            current_date = datetime.date.today().strftime("%Y%m%d")
            order_number = f"{current_date}{data.id}"
            data.order_number = order_number
            data.save()

            # Create Razorpay Order
            print(f"DEBUG: Using Razorpay Key ID: {settings.RAZORPAY_KEY_ID}")
            print(f"DEBUG: Using Razorpay Secret Key: {settings.RAZORPAY_SECRET_KEY}")
        
            razorpay_order = client.order.create({
                "amount": int(grand_total * 100),
                "currency": "INR",
                "receipt": order_number,
                "payment_capture": 1,
            })

            context = {
                'order': data,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
            }
            print("Order created with order_number:", data.order_number)

            return render(request, 'orders/payments.html', context)
    return redirect('checkout')

from django.db import transaction

def payments(request):
    body = json.loads(request.body)
    try:
        with transaction.atomic():
            # Fetch the order
            order = Order.objects.get(
                user=request.user, is_ordered=False, order_number=body['orderID']
            )

            # Save payment details
            payment = Payment.objects.create(
                user=request.user,
                payment_id=body['transID'],
                payment_method=body['payment_method'],
                amount_paid=order.order_total,
                status=body['status'],
            )

            # Update order status
            if body['status'] == 'captured':
                order.payment = payment
                order.is_ordered = True
                order.save()

                print(f"Order updated successfully: {order.order_number}, is_ordered={order.is_ordered}")

                # Move cart items to order products
                cart_items = CartItem.objects.filter(user=request.user)
                for item in cart_items:
                    orderproduct = OrderProduct.objects.create(
                        order=order,
                        payment=payment,
                        user=request.user,
                        product=item.product,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        ordered=True,
                    )

                    # Reduce stock
                    item.product.stock -= item.quantity
                    item.product.save()

                # Clear the cart
                cart_items.delete()

                # Send confirmation email
                mail_subject = "Thank you for your order!"
                try:
                    message = render_to_string('orders/order_received_email.html', {
                        'user': request.user,
                        'order': order,
                    })
                    to_email = request.user.email
                    send_email = EmailMessage(mail_subject, message, to=[to_email])
                    send_email.send()
                    print("Order confirmation email sent successfully.")
                except Exception as e:
                    logger.error(f"Error sending confirmation email: {e}")
                    print(f"Error sending confirmation email: {e}")

                print("Payment and order processing completed successfully.")

                # Return success response
                return JsonResponse({
                    'success': True,
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                })
            else:
                print("Payment not captured.")
                return JsonResponse({'success': False, 'message': 'Payment not captured!'}, status=400)
    except Order.DoesNotExist:
        print("Order does not exist.")
        return JsonResponse({'success': False, 'message': 'Order not found!'}, status=404)
    except Exception as e:
        logger.error(f"Payment error: {e}")
        print(f"Payment error: {e}")
        return JsonResponse({'success': False, 'message': 'Payment processing failed!'}, status=500)

def order_complete(request):
    order_number = request.GET.get('order_number', '').strip()
    transID = request.GET.get('payment_id', '').strip()

    print("Received order_number:", order_number)
    print("Received transID:", transID)

    if not order_number or not transID:
        print("Missing parameters.")
        return redirect('home')

    try:
        # Fetch the order and payment
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        payment = Payment.objects.get(payment_id=transID)
        ordered_products = OrderProduct.objects.filter(order=order)

        # Calculate subtotal
        subtotal = sum([item.quantity * item.product_price for item in ordered_products])

        context = {
            'order': order,
            'payment': payment,
            'ordered_products': ordered_products,
            'order_number': order_number,
            'transID': transID,
            'subtotal': subtotal,
        }
        print("Order and payment found. Rendering order_complete.")
        return render(request, 'orders/order_complete.html', context)
    except Order.DoesNotExist:
        print(f"Order with number {order_number} does not exist or is not marked as ordered.")
        return redirect('home')
    except Payment.DoesNotExist:
        print(f"Payment with ID {transID} does not exist.")
        return redirect('home')
