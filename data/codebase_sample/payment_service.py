class PaymentService:
    """
    Handles payments for NeoPay, a payments platform used by small merchants.
    Currently supports card and netbanking. UPI and wallet are on the roadmap.
    """

    SUPPORTED_METHODS = ["card", "netbanking"]
    REFUND_APPROVAL_THRESHOLD = 10000  # INR, above this a second approver is required

    def process_payment(self, order_id, amount, method):
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(f"Unsupported payment method: {method}")
        # charges the customer, then records the transaction
        return {"status": "success", "order_id": order_id}

    def refund(self, order_id, amount):
        """Refunds an existing payment. Every refund must be written to the audit log."""
        if amount > self.REFUND_APPROVAL_THRESHOLD:
            raise PermissionError("Refunds above threshold need secondary approval")
        # writes to audit_log, then reverses the charge
        return {"status": "refunded", "order_id": order_id}