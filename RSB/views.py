from django.shortcuts import render, redirect
from store.models import Product, ReviewRating
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')

    # Get the reviews
    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)


def about_us(request):
    return render(request, 'about_us.html')

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        query = request.POST.get('query')
        if name and email and subject and query:
            full_message = f"From: {name} <{email}>\n\n{query}"
            send_mail(
                subject,
                full_message,
                settings.EMAIL_HOST_USER,
                ['rsb.grocery@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, 'Your query is submitted. We will reach out to you soon!')
            return redirect('contact_us')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'contact_us.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_conditions(request):
    return render(request, 'terms_conditions.html')

def cancellation_policy(request):
    return render(request, 'cancellation_policy.html')


def refund_policy(request):
    return render(request, 'refund_policy.html')

