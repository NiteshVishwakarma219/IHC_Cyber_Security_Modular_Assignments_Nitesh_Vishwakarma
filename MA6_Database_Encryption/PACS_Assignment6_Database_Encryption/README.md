# PACS Assignment 6 — Database Encryption

## Objective
This project demonstrates two complementary controls requested in the assignment: (1) encrypted file-system/volume storage using a real VeraCrypt container or supported BitLocker data volume, and (2) application-level encryption of sensitive SQLite columns using AES-256-GCM.

## Scope and safety
- Synthetic demonstration records only. Do not enter real payment-card data.
- This is a classroom CLI prototype, not a production payment-card system.
- The Python program encrypts the card-number and expiry fields before storing them. It does **not** create or automatically verify an encrypted file-system volume; that part must be performed separately and evidenced.
- The SQLite schema, transaction IDs, cardholder names, row count, and timestamps remain visible.

## Setup (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$keyBytes = New-Object byte[] 32
[System.Security.Cryptography.RandomNumberGenerator]::Fill($keyBytes)
$env:APP_ENCRYPTION_KEY = [Convert]::ToBase64String($keyBytes)
python app.py init
python app.py seed
python app.py encrypted-view
python app.py authorized-view
python app.py verify
python -m unittest discover -s tests -v
```
Keep this terminal open while running commands. The key exists only in the current session. Keep it separate from the database and do not include it in screenshots, source control, report, or portal. If you close the terminal or generate another key, old encrypted values cannot be decrypted without the original key.

Default database: `data/secure_cards.db`. Choose a custom path with `--db`. For a mounted VeraCrypt drive, for example: `python app.py seed --db "V:\PACS\secure_cards.db"`.

## Encrypted file-system demonstration (VeraCrypt)
1. Download VeraCrypt only from its official site: https://www.veracrypt.fr/ .
2. In VeraCrypt choose **Create Volume** → **Create an encrypted file container**. Use a new container file and a strong volume password. Do not reformat or encrypt your Windows system drive for this assignment.
3. Finish the wizard, mount the container to an unused drive letter such as `V:`, then create `V:\PACS`.
4. With the current key still set in PowerShell, run `python app.py seed --db "V:\PACS\secure_cards.db"` and capture a screenshot showing the mounted volume and database file.
5. Dismount the volume from VeraCrypt. Capture the dismounted state, without exposing your password or keys.

When the volume is locked/dismounted, its contents are protected at rest. While mounted/unlocked, the OS and authorized processes can read files. Do not claim this step is complete unless you actually perform it.

## BitLocker alternative
If supported by your Windows edition and device, a separate BitLocker-protected data drive can be used instead. Understand recovery-key backup before enabling it. Official guide: https://learn.microsoft.com/windows/security/operating-system-security/data-protection/bitlocker/ . If neither is available, document the limitation and do not claim an encrypted-volume implementation.

## Commands
- `init`: create table.
- `seed`: insert three synthetic examples (duplicate IDs are ignored).
- `encrypted-view`: display ciphertext without using the key to decrypt.
- `authorized-view`: decrypt in application memory and mask all but the final four digits.
- `verify`: validate AES-GCM authentication tags.

## Limitations and production guidance
The environment variable is a demo key-delivery mechanism, not full key management. Production systems should use a managed KMS/HSM, strict access control, rotation, audit logging, backups, and separation of duties. AES-GCM requires a unique nonce for each encryption under a given key; this program generates a fresh random 12-byte nonce for every field. Real payment-card processing can trigger PCI DSS obligations; this project uses only synthetic data.
