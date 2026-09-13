# Coding defaults

- Prefer the standard library and small auditable components.
- Target Python 3.11+ for the prototype host and conservative C/C++ for Tablet OS.
- Keep authored source files under 400 lines where practical.
- Reject unknown protocol versions and malformed boundary input explicitly.
- Use argument arrays with `shell=False`; remote clients invoke action IDs only.
- Bind durable formats to a schema/version field.
- Store secrets and machine-specific configuration beneath ignored `local/`.
- Keep third-party notices and exact dependency versions when dependencies arrive.
- Do not silently broaden listening interfaces or weaken authentication.

