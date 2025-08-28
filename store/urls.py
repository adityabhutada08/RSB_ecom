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



    # path('products/', views.product_list, name='product_list'),
    # path('products/add/', views.add_product, name='add_product'),
    # path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('admin/products/', views.manage_products, name='manage_products'),
    path('admin/products/<int:pk>/delete/', views.delete_product, name='delete_product'),

]
