# NeoPay Payment Security Policy

NeoPay processes payments for over 5,000 small merchants. Because real money moves
through this system, every change to payment code is treated as high risk by default.

## Refunds

- Every refund must write an entry to the audit log: user ID, order ID, amount, timestamp.
- Refunds above INR 10,000 require a second approver before they are processed.
- A refund must be traceable back to the original transaction ID. No blind refunds.

## New payment methods

- Any new payment method (UPI, wallets, BNPL) must verify the transaction with the
  provider (for UPI, this means checking the NPCI transaction ID) before marking a
  payment as successful.
- New payment methods must be added to a feature flag before rollout, so they can be
  disabled instantly if fraud is detected.

## General

- No payment data (card numbers, UPI IDs) may appear in application logs.
- All payment endpoints require authentication. None may be called anonymously.
