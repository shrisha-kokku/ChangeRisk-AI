class PaymentService:
    def process_payment(self, order_id, amount, method):
        """Handles card and netbanking payments only."""
        if method not in ["card", "netbanking"]:
            raise ValueError("Unsupported payment method")
        return {"status": "success", "order_id": order_id}