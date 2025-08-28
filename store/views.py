from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import category
from carts.models import CartItem
from django.db.models import Q

from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_POST

# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(category , slug = category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()


    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


# Admin-only price manager
def _is_staff_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superadmin or user.is_admin)


@user_passes_test(_is_staff_user)
def price_manager(request):
    query = request.GET.get('q', '')  # Get search query
    products = Product.objects.all().order_by('id')

    if query:
        products = products.filter(product_name__icontains=query)  # Case-insensitive search

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'store/price_manager.html', context)


@login_required
@require_POST
def update_product_price(request):
    if not _is_staff_user(request.user):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    try:
        product_id = int(request.POST.get('product_id'))
        new_price = request.POST.get('price')
        if new_price is None:
            return JsonResponse({'success': False, 'message': 'Price is required'}, status=400)
        try:
            new_price_int = int(new_price)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid price'}, status=400)
        if new_price_int < 0:
            return JsonResponse({'success': False, 'message': 'Price must be positive'}, status=400)

        product = Product.objects.get(id=product_id)
        product.price = new_price_int
        product.save(update_fields=['price', 'modified_date'])
        return JsonResponse({'success': True, 'product_id': product.id, 'price': product.price})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Server error'}, status=500)



# ------------------------
# Admin-only Stock Manager
# ------------------------

@user_passes_test(_is_staff_user)
def stock_manager(request):
    query = request.GET.get('q', '')  # Get search query
    products = Product.objects.all().order_by('id')

    if query:
        products = products.filter(product_name__icontains=query)  # Case-insensitive search

    context = {
        'products': products,
        'query': query,
    }
    return render(request, 'store/stock_manager.html', context)


@login_required
@require_POST
def update_product_stock(request):
    if not _is_staff_user(request.user):
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    try:
        product_id = int(request.POST.get('product_id'))
        new_stock = request.POST.get('stock')

        if new_stock is None:
            return JsonResponse({'success': False, 'message': 'Stock is required'}, status=400)

        try:
            new_stock_int = int(new_stock)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid stock value'}, status=400)

        if new_stock_int < 0:
            return JsonResponse({'success': False, 'message': 'Stock must be non-negative'}, status=400)

        product = Product.objects.get(id=product_id)
        product.stock = new_stock_int
        product.save(update_fields=['stock', 'modified_date'])

        return JsonResponse({'success': True, 'product_id': product.id, 'stock': product.stock})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Server error'}, status=500)





def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request), product = single_product).exists()

    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    # products = Product.objects.none()  # Initialize an empty queryset
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']  # Get and clean up the keyword
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)

                
# store/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.template.loader import render_to_string
from .models import Product
from .forms import ProductForm


@user_passes_test(_is_staff_user)
def manage_products(request):
    """
    Admin page: add a product (AJAX), live-search, and sort products (AJAX).
    """
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    query = request.GET.get("q", "")
    sort_by = request.GET.get("sort", "")

    # Base queryset
    products = Product.objects.all()

    # --- Filtering by search ---
    if query:
        products = products.filter(product_name__icontains=query)

    # --- Sorting logic ---
    if sort_by == "name_asc":
        products = products.order_by("product_name")
    elif sort_by == "name_desc":
        products = products.order_by("-product_name")
    elif sort_by == "price_low":
        products = products.order_by("price")
    elif sort_by == "price_high":
        products = products.order_by("-price")
    else:
        products = products.order_by("-id")  # default: latest first

    form = ProductForm(request.POST or None, request.FILES or None)

    # --- Add Product (AJAX) ---
    if request.method == "POST":
        if form.is_valid():
            product = form.save()
            if is_ajax:
                row_html = render_to_string(
                    "store/partials/product_row.html",
                    {"product": product},
                    request=request,
                )
                return JsonResponse(
                    {"success": True, "row_html": row_html, "message": "Product added successfully"}
                )
            return redirect("manage_products")
        else:
            if is_ajax:
                return JsonResponse({"success": False, "errors": form.errors})

    # --- Return products table for AJAX (search/sort) ---
    if is_ajax and request.method == "GET":
        table_html = render_to_string(
            "store/partials/product_table_body.html",
            {"products": products},
            request=request,
        )
        return JsonResponse({"success": True, "table_html": table_html})

    # Normal page load
    context = {
        "form": form,
        "products": products,
        "query": query,
    }
    return render(request, "store/manage_products.html", context)



@user_passes_test(_is_staff_user)
@require_POST
def delete_product(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Product

@require_GET
def sort_products(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and 'sort' in request.GET:
        sort_by = request.GET.get('sort')
        products_qs = Product.objects.all()

        if sort_by == 'name_asc':
            products_qs = products_qs.order_by('product_name')
        elif sort_by == 'name_desc':
            products_qs = products_qs.order_by('-product_name')

        # serialize queryset into JSON
        data = [{
            'id': prod.id,
            'product_name': prod.product_name,
            'slug': prod.slug,
            'description': prod.description,
            'price': float(prod.price),
            'stock': prod.stock,
            'image': prod.images.url if prod.images else ''
        } for prod in products_qs]

        return JsonResponse({'products': data})
