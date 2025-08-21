from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name="store"),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
    path('admin/price-manager/', views.price_manager, name='price_manager'),
    path('admin/update-price/', views.update_product_price, name='update_product_price'),

    path("stock-manager/", views.stock_manager, name="stock_manager"),
    path("update-stock/", views.update_product_stock, name="update_product_stock"),
]