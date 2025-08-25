# category/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
import json # You need this for the form errors

from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required




from .models import category
from .forms import CategoryForm

def _is_staff_user(user):
    return user.is_authenticated and (user.is_staff or getattr(user, "is_superadmin", False) or getattr(user, "is_admin", False))

@login_required
@user_passes_test(_is_staff_user)
def manage_categories(request):
    """Add, list, and sort categories on one page."""
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            new_category = form.save()
            
            if is_ajax:
                # Prepare a JSON response for the AJAX request
                # We need the full URL for the image
                img_url = new_category.category_img.url if new_category.category_img else ''
                return JsonResponse({
                    "success": True,
                    "category": {
                        "id": new_category.id,
                        "category_name": new_category.category_name,
                        "slug": new_category.slug,
                        "category_description": new_category.category_description,
                        "category_img": img_url,
                    }
                })
            else:
                # Redirect for a standard form submission
                return redirect('category:manage_categories')
        else:
            if is_ajax:
                # Return form errors as JSON
                errors = dict(form.errors)
                return JsonResponse({"success": False, "errors": errors}, status=400)
            else:
                # Re-render the page with form errors
                context = {
                    "form": form,
                    "categories": category.objects.all(),
                }
                return render(request, "category/manage_categories.html", context)
    
    # Handle GET requests (initial page load and AJAX sorting)
    if is_ajax and 'sort' in request.GET:
        sort_by = request.GET.get('sort')
        categories_qs = category.objects.all()
        if sort_by == 'name_asc':
            categories_qs = categories_qs.order_by('category_name')
        elif sort_by == 'name_desc':
            categories_qs = categories_qs.order_by('-category_name')
        
        data = [{'id': cat.id, 'category_name': cat.category_name, 'slug': cat.slug, 'category_description': cat.category_description, 'category_img': cat.category_img.url if cat.category_img else ''} for cat in categories_qs]
        return JsonResponse({'categories': data})

    form = CategoryForm()
    categories = category.objects.all()
    context = {
        "form": form,
        "categories": categories,
    }
    return render(request, "category/manage_categories.html", context)


@login_required
@user_passes_test(_is_staff_user)
@require_POST
def delete_category(request, pk):
    try:
        cat = get_object_or_404(category, pk=pk)
        
        if cat.category_img:
            cat.category_img.delete(save=False)
        
        cat.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)