def test_card_payment_succeeds():
    service = PaymentService()
    result = service.process_payment(order_id=1, amount=500, method="card")
    assert result["status"] == "success"

def test_unsupported_method_rejected():
    service = PaymentService()
    try:
        service.process_payment(order_id=2, amount=500, method="upi")
        assert False, "should have raised"
    except ValueError:
        pass

def test_small_refund_succeeds():
    service = PaymentService()
    result = service.refund(order_id=1, amount=500)
    assert result["status"] == "refunded"