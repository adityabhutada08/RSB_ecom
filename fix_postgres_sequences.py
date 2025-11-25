#!/usr/bin/env python
"""
Fix PostgreSQL sequences after data migration from SQLite
This ensures that auto-increment IDs work correctly
"""
import os
import sys
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
if os.path.exists('/app'):
    BASE_DIR = Path('/app')
    sys.path.insert(0, str(BASE_DIR))
else:
    sys.path.insert(0, str(BASE_DIR / 'RSB'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RSB.settings')

import django
django.setup()

from django.db import connection

print("=" * 60)
print("Fixing PostgreSQL Sequences")
print("=" * 60)

# Tables that need sequence fixes
tables_to_fix = [
    ('accounts_account', 'id'),
    ('accounts_userprofile', 'id'),
    ('category_category', 'id'),
    ('store_product', 'id'),
    ('store_variation', 'id'),
    ('store_productgallery', 'id'),
    ('store_reviewrating', 'id'),
    ('carts_cart', 'id'),
    ('carts_cartitem', 'id'),
    ('orders_order', 'id'),
    ('orders_payment', 'id'),
    ('orders_orderproduct', 'id'),
]

with connection.cursor() as cursor:
    for table_name, id_column in tables_to_fix:
        try:
            # Get the sequence name
            cursor.execute(f"""
                SELECT pg_get_serial_sequence('{table_name}', '{id_column}');
            """)
            sequence_result = cursor.fetchone()
            
            if sequence_result and sequence_result[0]:
                sequence_name = sequence_result[0]
                
                # Get max ID from table
                cursor.execute(f"SELECT COALESCE(MAX({id_column}), 0) FROM {table_name};")
                max_id = cursor.fetchone()[0]
                
                # Reset sequence to max_id (with true means "this value was used", so next will be max_id + 1)
                if max_id > 0:
                    cursor.execute(f"SELECT setval('{sequence_name}', {max_id}, true);")
                    # Verify next value
                    cursor.execute(f"SELECT nextval('{sequence_name}');")
                    next_val = cursor.fetchone()[0]
                    # Reset it back (since we just consumed it)
                    cursor.execute(f"SELECT setval('{sequence_name}', {max_id}, true);")
                    print(f"✓ {table_name}: Set sequence to {max_id} (next ID will be {next_val})")
                else:
                    # Table is empty, set to 1
                    cursor.execute(f"SELECT setval('{sequence_name}', 1, false);")
                    print(f"○ {table_name}: Table empty, set sequence to 1")
            else:
                print(f"⚠ {table_name}: No sequence found (might not be auto-increment)")
                
        except Exception as e:
            print(f"✗ {table_name}: Error - {e}")

print("\n" + "=" * 60)
print("Sequence fix completed!")
print("=" * 60)
print("\nYou can now add new categories, products, orders, etc. without ID conflicts.")

