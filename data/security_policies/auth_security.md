
# NeoPay Authentication Policy

- Session timeout is 30 minutes for any account with payment access. This is not
  configurable per user.
- Password reset links expire in 15 minutes and can be used once.
- 5 failed login attempts locks the account for 15 minutes.
- All login attempts, successful or not, are written to the audit log.
