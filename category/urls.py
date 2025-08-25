# category/urls.py
from django.urls import path
from . import views

app_name = "category"

urlpatterns = [
    path("add-category/", views.manage_categories, name="manage_categories"),
    path("delete-category/<int:pk>/", views.delete_category, name="delete_category"),
    # path('delete/<int:category_id>/', views.delete_category, name='delete_category'),
]
