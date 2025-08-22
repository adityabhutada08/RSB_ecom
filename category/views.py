from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .forms import CategoryForm
from django.contrib import messages
from .models import category
from django import forms

# Reuse your staff check
def _is_staff_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(_is_staff_user)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully ✅")
            return redirect("store")  # redirect to store after success
    else:
        form = CategoryForm()

    return render(request, "category/add_category.html", {"form": form})
