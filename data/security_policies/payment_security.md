
# Payment Security Policy

- All refund operations must be logged with user ID and timestamp.
- Refunds above ₹10,000 require secondary approval.
- No refund logic may bypass the audit log table.
- UPI transactions must be verified against the NPCI transaction ID before refund.
