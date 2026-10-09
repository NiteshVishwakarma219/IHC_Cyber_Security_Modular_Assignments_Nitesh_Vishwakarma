# Security notes
- Use synthetic demo records only; never use real payment-card data.
- Do not share `APP_ENCRYPTION_KEY` in the portal, screenshots, source control, or report.
- The key must remain separate from the SQLite database. If lost, the data cannot be decrypted; if compromised, an attacker may decrypt it.
- AES-GCM requires unique nonces per key; this program generates a fresh random 12-byte nonce per field encryption.
- The app encrypts selected fields, not the entire SQLite database.
- The VeraCrypt/BitLocker step must be performed and verified separately.
- This is an educational prototype, not a production payment-card system or PCI DSS compliance implementation.
