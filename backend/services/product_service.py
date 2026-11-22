"""
backend/services/product_service.py
Product management, BST barcode search, and Trie name search (Task 3.2 / Doc 6.1).
"""


class ProductService:
    def __init__(self, bst_index, trie_index, db_conn):
        self.bst = bst_index
        self.trie = trie_index
        self.conn = db_conn

    def register_product(self, barcode: str, name: str, cost: float, price: float, category_id=None, reorder_level=0):
        pass

    def edit_product(self, product_id: int, **fields):
        pass

    def delete_product(self, product_id: int):
        """Soft deletes product if transaction history exists."""
        pass

    def find_by_barcode(self, barcode: str):
        return self.bst.find(barcode)

    def search_by_name_prefix(self, prefix: str):
        return self.trie.list_under_prefix(prefix.lower(), limit=8)

