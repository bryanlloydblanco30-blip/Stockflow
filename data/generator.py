"""
data/generator.py
Sample data generator with a fixed seed (Doc 8.3 / Task 6.1).
Generates:
- 6 to 8 categories (20% to 30% no-expiry)
- 30 to 100 products (labelled as '[SAMPLE]')
- Multiple batches per product with realistic perishable and non-perishable dates
- 30 to 90 days of simulated sales and transactions
"""

import random
from datetime import date, timedelta
from typing import List, Dict, Any
import sqlite3

from backend.db.schema import init_schema
from backend.models.category import Category
from backend.models.product import Product
from backend.models.batch import Batch
from backend.models.transaction import Transaction
from backend.models.transaction_line import TransactionLine
from backend.db.storage import save_category, save_product, save_batch, save_transaction_atomic


SAMPLE_CATEGORIES = [
    # (name, tracks_expiry, warn_days)
    ("Bakery", True, 7),
    ("Dairy & Chilled", True, 10),
    ("Canned Goods", True, 30),
    ("Beverages", True, 14),
    ("Snacks & Biscuits", True, 21),
    ("Household & Cleaning", False, 0),  # 1/7 = ~14.3%
    ("School & Office Supplies", False, 0),  # 2/7 = ~28.6% (meets 20-30% no-expiry requirement)
]

PRODUCT_TEMPLATES = [
    ("Pandesal 10s", 0, 20.0, 30.0, 10),
    ("Sliced Bread", 0, 35.0, 50.0, 8),
    ("Ensaymada", 0, 15.0, 25.0, 12),
    ("Monay Bread", 0, 18.0, 28.0, 10),
    ("Fresh Milk 1L", 1, 65.0, 90.0, 6),
    ("Yogurt Drink", 1, 22.0, 35.0, 10),
    ("Cheddar Cheese 200g", 1, 45.0, 65.0, 8),
    ("Butter Salted 225g", 1, 80.0, 110.0, 5),
    ("Corned Beef 150g", 2, 38.0, 52.0, 15),
    ("Sardines in Tomato 155g", 2, 18.0, 26.0, 20),
    ("Tuna Flakes in Oil", 2, 32.0, 44.0, 15),
    ("Evaporated Milk 370ml", 2, 28.0, 38.0, 12),
    ("Mineral Water 500ml", 3, 10.0, 15.0, 24),
    ("Instant Coffee 3-in-1", 3, 7.0, 12.0, 50),
    ("Orange Juice 1L", 3, 55.0, 75.0, 8),
    ("Softdrink Can 330ml", 3, 25.0, 35.0, 20),
    ("Potato Chips 110g", 4, 30.0, 45.0, 12),
    ("Chocolate Bar 50g", 4, 25.0, 38.0, 15),
    ("Cream Crackers 250g", 4, 35.0, 48.0, 10),
    ("Peanut Butter 340g", 4, 60.0, 85.0, 6),
    ("Dishwashing Liquid 500ml", 5, 40.0, 58.0, 10),
    ("Laundry Detergent 1kg", 5, 75.0, 105.0, 8),
    ("Fabric Conditioner 800ml", 5, 65.0, 92.0, 8),
    ("Bleach 500ml", 5, 25.0, 38.0, 10),
    ("Ballpen Black 0.5mm", 6, 8.0, 12.0, 30),
    ("Notebook 80 Leaves", 6, 20.0, 30.0, 20),
    ("Yellow Pad Paper", 6, 35.0, 50.0, 15),
    ("Correction Tape", 6, 18.0, 28.0, 10),
]


def generate_sample_data(
    conn: sqlite3.Connection,
    seed: int = 42,
    num_products: int = 35,
    days_of_sales: int = 60,
    base_date: date = date(2026, 11, 23),
) -> Dict[str, Any]:
    """
    Populates SQLite database with deterministic, reproducible sample data.
    Ensures all sample products carry the '[SAMPLE]' label.
    """
    rng = random.Random(seed)
    start_date = base_date - timedelta(days=days_of_sales)

    # 1. Insert Categories
    categories: List[Category] = []
    for name, tracks_exp, warn_d in SAMPLE_CATEGORIES:
        cat = Category(id=0, name=f"[SAMPLE] {name}", tracks_expiry=tracks_exp, warn_days=warn_d)
        cat = save_category(conn, cat)
        categories.append(cat)

    # 2. Insert Products (30 to 100 products)
    products: List[Product] = []
    prod_id_counter = 1
    for i in range(num_products):
        template = PRODUCT_TEMPLATES[i % len(PRODUCT_TEMPLATES)]
        name_base, cat_idx, cost, price, reorder = template
        suffix = f" {i // len(PRODUCT_TEMPLATES) + 1}" if i >= len(PRODUCT_TEMPLATES) else ""
        prod_name = f"[SAMPLE] {name_base}{suffix}"
        barcode = f"480{rng.randint(1000000, 9999999)}"

        prod = Product(
            id=0,
            barcode=barcode,
            name=prod_name,
            category_id=categories[cat_idx].id,
            cost_price=cost,
            selling_price=price,
            reorder_level=reorder,
            location_id=1,
            active=True,
        )
        prod = save_product(conn, prod)
        products.append(prod)

    # 3. Insert Initial Batches for each product
    batches: List[Batch] = []
    for prod in products:
        cat = next(c for c in categories if c.id == prod.category_id)
        # Create 2 to 4 batches per product
        batch_count = rng.randint(2, 4)
        for b_idx in range(batch_count):
            recv_offset = rng.randint(5, days_of_sales)
            recv_date = (start_date + timedelta(days=recv_offset)).isoformat()
            qty = rng.randint(15, 50)

            exp_date_str = None
            if cat.tracks_expiry:
                # Some batches expired, some near-expiry, some safe
                exp_offset = rng.randint(-5, 45)
                exp_date_str = (base_date + timedelta(days=exp_offset)).isoformat()

            b = Batch(
                id=0,
                product_id=prod.id,
                quantity=qty,
                cost_price=prod.cost_price,
                received_date=recv_date,
                expiry_date=exp_date_str,
                moved_to_front=False,
            )
            b = save_batch(conn, b)
            batches.append(b)

    # 4. Generate Historical Sales across days_of_sales
    total_sales_count = 0
    for day_idx in range(days_of_sales):
        current_day = start_date + timedelta(days=day_idx)
        # 2 to 6 sales transactions per day
        daily_tx_count = rng.randint(2, 6)
        for _ in range(daily_tx_count):
            # Select 1 to 3 items per transaction
            items_count = rng.randint(1, 3)
            cart_products = rng.sample(products, items_count)
            tx_total = 0.0
            tx_lines: List[TransactionLine] = []

            for cp in cart_products:
                qty_bought = rng.randint(1, 3)
                # Find available batch for this product
                cur = conn.cursor()
                cur.execute("SELECT id, quantity, cost_price FROM batches WHERE product_id = ? AND quantity >= ? LIMIT 1;", (cp.id, qty_bought))
                brow = cur.fetchone()
                if brow:
                    batch_id, available_qty, batch_cost = brow[0], brow[1], brow[2]
                    subtotal = qty_bought * cp.selling_price
                    tx_total += subtotal
                    tx_lines.append(TransactionLine(
                        id=0,
                        transaction_id=0,
                        product_id=cp.id,
                        batch_id=batch_id,
                        quantity=qty_bought,
                        price_at_time=cp.selling_price,
                        cost_at_time=batch_cost,
                    ))

            if tx_lines:
                cash = tx_total + rng.choice([0.0, 10.0, 50.0, 100.0])
                change = cash - tx_total
                tx = Transaction(
                    id=0,
                    type="sale",
                    date_time=f"{current_day.isoformat()} {rng.randint(8, 20):02d}:{rng.randint(0, 59):02d}:00",
                    total=tx_total,
                    cash_given=cash,
                    change=change,
                    location_id=1,
                )
                save_transaction_atomic(conn, tx, tx_lines)
                total_sales_count += 1

    return {
        "categories_count": len(categories),
        "products_count": len(products),
        "batches_count": len(batches),
        "sales_count": total_sales_count,
        "days_of_sales": days_of_sales,
    }
