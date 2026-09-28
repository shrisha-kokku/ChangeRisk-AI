def test_card_payment():
    """Existing test: verifies card payments process successfully."""
    service = PaymentService()
    result = service.process_payment(order_id=1, amount=500, method="card")
    assert result["status"] == "success"

def test_netbanking_payment():
    """Existing test: verifies netbanking payments process successfully."""
    service = PaymentService()
    result = service.process_payment(order_id=2, amount=1000, method="netbanking")
    assert result["status"] == "success"