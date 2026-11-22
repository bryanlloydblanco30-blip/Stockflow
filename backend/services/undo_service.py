"""
backend/services/undo_service.py
Single-level transaction undo using Stack (Task 4.7 / Doc 6.7).
Restores stock to exact supplying batches and creates a void record.
"""


class UndoService:
    def __init__(self, undo_stack, db_conn):
        self.stack = undo_stack
        self.conn = db_conn

    def void_last_transaction(self):
        """Reverses most recent transaction only. Blocked if newer transactions exist."""
        pass

