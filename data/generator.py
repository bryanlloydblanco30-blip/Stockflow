"""
data/generator.py
Sample data generator with fixed seed (Doc 8.3 / Task 6.1).
Generates 30 to 100 products, 6 to 8 categories (20-30% no-expiry), 30 to 90 days of sales.
"""

import random


def generate_sample_data(seed: int = 42, product_count: int = 50, days_of_sales: int = 60):
    """Generates reproducible dataset for development and benchmarking."""
    random.seed(seed)
    pass

