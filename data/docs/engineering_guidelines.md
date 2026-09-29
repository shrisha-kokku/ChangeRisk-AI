
# NeoPay Engineering Guidelines

- Documentation-only changes do not require a security review or new tests.
- Any change to a public API endpoint must update the API docs and bump the version number.
- Changes to security configuration (timeouts, thresholds, retry limits) always require review,
  even if the change looks small.
