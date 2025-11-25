#!/usr/bin/env python
"""
Direct SQLite to PostgreSQL migration script
Reads directly from SQLite and inserts into PostgreSQL via Django ORM
"""
import sqlite3
import os
import sys
from pathlib import Path

# Setup Django for PostgreSQL connection
# Handle both local and Docker environments
if os.path.exists('/app'):
    # Docker environment
    BASE_DIR = Path('/app')
    sqlite_path = Path('/app/db.sqlite3')
    sys.path.insert(0, str(BASE_DIR))
else:
    # Local environment
    BASE_DIR = Path(__file__).resolve().parent
    sqlite_path = BASE_DIR / 'RSB' / 'db.sqlite3'
    sys.path.insert(0, str(BASE_DIR / 'RSB'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RSB.settings')

import django
django.setup()

from accounts.models import Account, UserProfile
from category.models import category
from store.models import Product, Variation, ProductGallery, ReviewRating
from carts.models import Cart, CartItem
from orders.models import Order, Payment, OrderProduct
sqlite_conn = sqlite3.connect(str(sqlite_path))
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# Helper function to safely get values from sqlite3.Row
def get_row_value(row, key, default=None):
    try:
        return row[key] if row[key] is not None else default
    except (KeyError, IndexError):
        return default

print("=" * 60)
print("Direct SQLite to PostgreSQL Migration")
print("=" * 60)
print(f"SQLite: {sqlite_path}")
print()

# Track what we migrate
migrated = {}

try:
    # 1. Migrate Accounts
    print("[1/6] Migrating Accounts...")
    sqlite_cursor.execute("SELECT * FROM accounts_account")
    accounts = sqlite_cursor.fetchall()
    for row in accounts:
        account, created = Account.objects.get_or_create(
            id=row['id'],
            defaults={
                'password': row['password'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'username': row['username'],
                'email': row['email'],
                'phone': row['phone'],
                'date_joined': row['date_joined'],
                'last_login': row['last_login'],
                'is_admin': bool(row['is_admin']),
                'is_staff': bool(row['is_staff']),
                'is_active': bool(row['is_active']),
                'is_superadmin': bool(row['is_superadmin']),
            }
        )
        if created:
            migrated.setdefault('accounts', 0)
            migrated['accounts'] += 1
    print(f"  ✓ Migrated {migrated.get('accounts', 0)} accounts")
    
    # 2. Migrate User Profiles
    print("[2/6] Migrating User Profiles...")
    sqlite_cursor.execute("SELECT * FROM accounts_userprofile")
    profiles = sqlite_cursor.fetchall()
    for row in profiles:
        try:
            user = Account.objects.get(id=row['user_id'])
            profile, created = UserProfile.objects.get_or_create(
                id=row['id'],
                defaults={
                    'user': user,
                    'address_line_1': get_row_value(row, 'address_line_1', ''),
                    'address_line_2': get_row_value(row, 'address_line_2', ''),
                    'profile_picture': get_row_value(row, 'profile_picture', 'default/default-user.png'),
                    'city': get_row_value(row, 'city', ''),
                    'state': get_row_value(row, 'state', ''),
                    'country': get_row_value(row, 'country', ''),
                }
            )
            if created:
                migrated.setdefault('profiles', 0)
                migrated['profiles'] += 1
        except Account.DoesNotExist:
            print(f"  ⚠ Skipping profile {row['id']} - user {row['user_id']} not found")
    print(f"  ✓ Migrated {migrated.get('profiles', 0)} profiles")
    
    # 3. Migrate Categories
    print("[3/6] Migrating Categories...")
    sqlite_cursor.execute("SELECT * FROM category_category")
    categories = sqlite_cursor.fetchall()
    for row in categories:
        cat, created = category.objects.get_or_create(
            id=row['id'],
            defaults={
                'category_name': row['category_name'],
                'category_description': get_row_value(row, 'category_description', ''),
                'category_img': get_row_value(row, 'category_img', ''),
                'slug': get_row_value(row, 'slug', ''),
            }
        )
        if created:
            migrated.setdefault('categories', 0)
            migrated['categories'] += 1
    print(f"  ✓ Migrated {migrated.get('categories', 0)} categories")
    
    # 4. Migrate Products
    print("[4/6] Migrating Products...")
    sqlite_cursor.execute("SELECT * FROM store_product")
    products = sqlite_cursor.fetchall()
    for row in products:
        try:
            cat = category.objects.get(id=row['category_id']) if row['category_id'] else None
            product, created = Product.objects.get_or_create(
                id=row['id'],
                defaults={
                    'product_name': row['product_name'],
                    'slug': get_row_value(row, 'slug', ''),
                    'description': get_row_value(row, 'description', ''),
                    'price': row['price'],
                    'images': get_row_value(row, 'images', ''),
                    'stock': get_row_value(row, 'stock', 0),
                    'is_available': bool(get_row_value(row, 'is_available', True)),
                    'created_date': get_row_value(row, 'created_date'),
                    'modified_date': get_row_value(row, 'modified_date'),
                    'category': cat,
                    'weight': get_row_value(row, 'weight', ''),
                }
            )
            if created:
                migrated.setdefault('products', 0)
                migrated['products'] += 1
        except category.DoesNotExist:
            print(f"  ⚠ Skipping product {row['id']} - category {row['category_id']} not found")
    print(f"  ✓ Migrated {migrated.get('products', 0)} products")
    
    # 5. Migrate Orders
    print("[5/6] Migrating Orders...")
    sqlite_cursor.execute("SELECT * FROM orders_order")
    orders = sqlite_cursor.fetchall()
    for row in orders:
        try:
            user = Account.objects.get(id=row['user_id'])
            order, created = Order.objects.get_or_create(
                id=row['id'],
                defaults={
                    'user': user,
                    'order_number': get_row_value(row, 'order_number', ''),
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone': row['phone'],
                    'email': row['email'],
                    'address_line_1': row['address_line_1'],
                    'address_line_2': get_row_value(row, 'address_line_2', ''),
                    'country': row['country'],
                    'state': row['state'],
                    'city': row['city'],
                    'order_note': get_row_value(row, 'order_note', ''),
                    'order_total': row['order_total'],
                    'tax': get_row_value(row, 'tax', 0),
                    'status': get_row_value(row, 'status', 'New'),
                    'ip': get_row_value(row, 'ip', ''),
                    'is_ordered': bool(get_row_value(row, 'is_ordered', False)),
                    'created_at': get_row_value(row, 'created_at'),
                    'updated_at': get_row_value(row, 'updated_at'),
                }
            )
            if created:
                migrated.setdefault('orders', 0)
                migrated['orders'] += 1
        except Account.DoesNotExist:
            print(f"  ⚠ Skipping order {row['id']} - user {row['user_id']} not found")
    print(f"  ✓ Migrated {migrated.get('orders', 0)} orders")
    
    # 6. Migrate Payments and Order Products
    print("[6/6] Migrating Payments and Order Products...")
    
    # Payments
    sqlite_cursor.execute("SELECT * FROM orders_payment")
    payments = sqlite_cursor.fetchall()
    for row in payments:
        try:
            user = Account.objects.get(id=row['user_id'])
            payment, created = Payment.objects.get_or_create(
                id=row['id'],
                defaults={
                    'user': user,
                    'payment_id': get_row_value(row, 'payment_id', ''),
                    'payment_method': get_row_value(row, 'payment_method', ''),
                    'amount_paid': row['amount_paid'],
                    'status': get_row_value(row, 'status', ''),
                    'created_at': get_row_value(row, 'created_at'),
                }
            )
            if created:
                migrated.setdefault('payments', 0)
                migrated['payments'] += 1
        except Account.DoesNotExist:
            print(f"  ⚠ Skipping payment {row['id']} - user {row['user_id']} not found")
    
    # Order Products
    sqlite_cursor.execute("SELECT * FROM orders_orderproduct")
    order_products = sqlite_cursor.fetchall()
    for row in order_products:
        try:
            order = Order.objects.get(id=row['order_id'])
            payment = Payment.objects.get(id=row['payment_id']) if row['payment_id'] else None
            user = Account.objects.get(id=row['user_id'])
            product = Product.objects.get(id=row['product_id'])
            
            order_product, created = OrderProduct.objects.get_or_create(
                id=row['id'],
                defaults={
                    'order': order,
                    'payment': payment,
                    'user': user,
                    'product': product,
                    'quantity': row['quantity'],
                    'product_price': row['product_price'],
                    'ordered': bool(get_row_value(row, 'ordered', True)),
                    'created_at': get_row_value(row, 'created_at'),
                    'updated_at': get_row_value(row, 'updated_at'),
                }
            )
            if created:
                migrated.setdefault('order_products', 0)
                migrated['order_products'] += 1
        except (Order.DoesNotExist, Account.DoesNotExist, Product.DoesNotExist, Payment.DoesNotExist) as e:
            print(f"  ⚠ Skipping order product {row['id']} - {type(e).__name__}")
    
    print(f"  ✓ Migrated {migrated.get('payments', 0)} payments")
    print(f"  ✓ Migrated {migrated.get('order_products', 0)} order products")
    
    sqlite_conn.close()
    
    print("\n" + "=" * 60)
    print("Migration Summary")
    print("=" * 60)
    total = sum(migrated.values())
    for key, value in sorted(migrated.items()):
        print(f"  {key.capitalize()}: {value}")
    print(f"\n✓ Total records migrated: {total}")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Migration failed: {e}")
    import traceback
    traceback.print_exc()
    sqlite_conn.close()
    sys.exit(1)

