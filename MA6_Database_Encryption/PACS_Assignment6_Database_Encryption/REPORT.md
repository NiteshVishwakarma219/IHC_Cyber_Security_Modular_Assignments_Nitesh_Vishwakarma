# Database Encryption — Assignment 6

**Course:** IHC — Practical Approach to Cyber Security (PACS)  
**Topic:** Database Encryption  
**Implementation:** Python, SQLite, PyCryptodome, AES-256-GCM  
**Data:** Synthetic demonstration records only

## 1. Objective
The assignment asks for a solution demonstrating encrypted file systems and application-level encryption to secure database data, along with research, comparison, implementation steps, security rationale, strengths, limitations, source code, and documentation.

## 2. Architecture
The CLI reads a 32-byte AES key from the `APP_ENCRYPTION_KEY` environment variable. It inserts synthetic transaction rows into SQLite and encrypts the card-number and expiry fields before storage. Each field uses AES-256-GCM with a fresh random 12-byte nonce and a 16-byte authentication tag. Associated data binds each ciphertext to its transaction ID, column name, and version. `encrypted-view` displays stored ciphertext, `authorized-view` decrypts the fields in application memory and masks the card number, and `verify` checks authentication tags.

## 3. Application-level encryption
AES-GCM provides confidentiality and integrity/authenticity for selected fields. The key is not stored in the SQLite database or hard-coded in the source. The demo uses an environment variable; a production implementation should use a managed key-management service or HSM, with strict access control, rotation, audit trails, and recovery procedures. Associated data is authenticated but not encrypted. The transaction ID, name, timestamps, row count, schema, and other unencrypted metadata remain visible.

## 4. Encrypted file-system implementation
The database file can be stored inside a mounted VeraCrypt encrypted container or on a supported BitLocker-protected data drive. The user must create and mount the encrypted volume separately, place the database inside it, and safely dismount/lock it. The Python code does not create or verify the volume itself. Screenshots should show the mounted volume containing the database and the volume after dismounting; do not expose passwords or keys.

Volume encryption protects files at rest when the volume is locked. Once unlocked, authorized processes can read files. Therefore, volume encryption helps protect storage media and offline theft scenarios but does not by itself hide database columns from a user/process that can access the unlocked system.

## 5. Comparison

| Criterion | Encrypted file system / volume | Application-level field encryption |
|---|---|---|
| Protection layer | Storage / operating system | Application / selected columns |
| Coverage | Files placed on protected volume | Only explicitly encrypted fields |
| While in use | Transparent while volume is unlocked | Decryption occurs when application uses key |
| Direct database-file exposure | Protected at rest while volume is locked | Encrypted fields remain ciphertext without key |
| Metadata | Depends on volume state and setup | Unencrypted columns/schema remain visible |
| Key management | Volume password/key and recovery process | Separate application encryption key |
| Limitation | Unlocked system access can expose files | Key or application compromise can expose plaintext |
| Best use | Storage media, files, backups at rest | Sensitive fields requiring additional protection |

These approaches are complementary, not interchangeable.

## 6. Strengths
- Sensitive fields are not stored as plaintext in SQLite.
- AES-GCM authentication detects ciphertext or associated-data tampering.
- Key material is supplied separately from the database.
- Fresh random nonces are generated per field encryption.
- The authorized output masks the card number.
- A real encrypted-volume procedure provides a separate storage-at-rest layer.

## 7. Limitations and risks
- The whole SQLite file is not encrypted by the application; metadata and names remain readable.
- A compromised application process with access to the key may decrypt fields.
- Environment variables are not a complete production key-management solution.
- The volume encryption procedure is manual and must be performed and evidenced on the actual computer.
- This is not a production payment application and is not a PCI DSS compliance claim.
- Nonce reuse with AES-GCM under the same key can undermine security; the demo generates fresh random nonces.

## 8. Test plan

| Test | Command/action | Expected observation |
|---|---|---|
| Initialize | `python app.py init` | Database and table created |
| Seed | `python app.py seed` | Synthetic rows inserted once |
| Ciphertext view | `python app.py encrypted-view` | Ciphertext shown; no plaintext card number |
| Authorized view | `python app.py authorized-view` | Decryption succeeds; card number masked |
| Integrity | `python app.py verify` | Authentication tags validate |
| Unit tests | `python -m unittest discover -s tests -v` | Tests pass |
| File-system test | Place database on mounted encrypted volume, then dismount | Protected at rest while locked |

Report a test as passed only after you have run it. Capture actual screenshots for evidence.

## 9. Conclusion
Encrypted file systems protect stored files at rest while locked; application-level AES-GCM encryption protects explicitly selected fields and authenticates them when decrypted. Using both layers can reduce exposure of sensitive database information, but secure key management, access controls, auditing, backup practices, and operational discipline remain necessary.

## 10. References
1. VeraCrypt official website: https://www.veracrypt.fr/
2. Microsoft Learn, BitLocker overview: https://learn.microsoft.com/windows/security/operating-system-security/data-protection/bitlocker/
3. PyCryptodome AES documentation: https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html
4. OWASP Cryptographic Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
5. OWASP Application Security Verification Standard: https://owasp.org/www-project-application-security-verification-standard/
6. SQLite documentation: https://www.sqlite.org/docs.html
