"""PACS Assignment 6: AES-256-GCM application-level encryption demo."""
import argparse, base64, os, sqlite3, sys
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

DB_DEFAULT = Path(os.environ.get('PACS_DB_PATH', 'data/secure_cards.db'))
KEY_ENV = 'APP_ENCRYPTION_KEY'
SAMPLES = [
    ('TXN-1001', 'Alex Example', '4111111111111111', '12/29'),
    ('TXN-1002', 'Jordan Sample', '5555555555554444', '09/28'),
    ('TXN-1003', 'Taylor Demo', '4000000000000002', '03/30'),
]

def get_key():
    value = os.environ.get(KEY_ENV, '').strip()
    if not value:
        raise RuntimeError(f'{KEY_ENV} is not set. Follow README.md to generate a key.')
    try: key = base64.b64decode(value, validate=True)
    except Exception as e: raise RuntimeError(f'{KEY_ENV} must be Base64.') from e
    if len(key) != 32: raise RuntimeError(f'{KEY_ENV} must decode to exactly 32 bytes.')
    return key

def encrypt(key, text, aad):
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=16)
    cipher.update(aad)
    ciphertext, tag = cipher.encrypt_and_digest(text.encode('utf-8'))
    return nonce, ciphertext, tag

def decrypt(key, nonce, ciphertext, tag, aad):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=16)
    cipher.update(aad)
    return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

def connect(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path); conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn

def init(path):
    with connect(path) as c:
        c.execute('''CREATE TABLE IF NOT EXISTS encrypted_transactions (
          transaction_id TEXT PRIMARY KEY, cardholder_name TEXT NOT NULL,
          card_nonce BLOB NOT NULL, card_ciphertext BLOB NOT NULL, card_tag BLOB NOT NULL,
          expiry_nonce BLOB NOT NULL, expiry_ciphertext BLOB NOT NULL, expiry_tag BLOB NOT NULL,
          algorithm TEXT NOT NULL DEFAULT 'AES-256-GCM', key_version INTEGER NOT NULL DEFAULT 1,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')

def seed(path):
    key = get_key(); init(path); added = 0
    with connect(path) as c:
        for tx, name, card, expiry in SAMPLES:
            n1, ct1, t1 = encrypt(key, card, f'{tx}:card_number:v1'.encode())
            n2, ct2, t2 = encrypt(key, expiry, f'{tx}:expiry:v1'.encode())
            cur = c.execute('''INSERT OR IGNORE INTO encrypted_transactions
             (transaction_id,cardholder_name,card_nonce,card_ciphertext,card_tag,
              expiry_nonce,expiry_ciphertext,expiry_tag) VALUES (?,?,?,?,?,?,?,?)''',
              (tx,name,n1,ct1,t1,n2,ct2,t2))
            added += cur.rowcount
    print(f'Inserted {added} synthetic record(s). Database: {path}')

def encrypted_view(path):
    init(path)
    with connect(path) as c: rows = c.execute('SELECT * FROM encrypted_transactions ORDER BY transaction_id').fetchall()
    if not rows: print('No records. Run: python app.py seed'); return
    print('DATABASE VIEW — ciphertext only (no decryption key used):')
    for r in rows:
        print(f"\n{r['transaction_id']} | {r['cardholder_name']}")
        print('  Card ciphertext (hex):', bytes(r['card_ciphertext']).hex())
        print('  Expiry ciphertext (hex):', bytes(r['expiry_ciphertext']).hex())
        print('  Algorithm:', r['algorithm'], '| Key version:', r['key_version'])

def authorized_view(path):
    key = get_key(); init(path)
    with connect(path) as c: rows = c.execute('SELECT * FROM encrypted_transactions ORDER BY transaction_id').fetchall()
    if not rows: print('No records. Run: python app.py seed'); return
    print('AUTHORIZED APPLICATION VIEW — synthetic data; card numbers masked:')
    for r in rows:
        tx = r['transaction_id']
        card = decrypt(key,bytes(r['card_nonce']),bytes(r['card_ciphertext']),bytes(r['card_tag']),f'{tx}:card_number:v1'.encode())
        expiry = decrypt(key,bytes(r['expiry_nonce']),bytes(r['expiry_ciphertext']),bytes(r['expiry_tag']),f'{tx}:expiry:v1'.encode())
        print(f"{tx} | {r['cardholder_name']} | Card: {'*' * (len(card)-4)}{card[-4:]} | Expiry: {expiry}")

def verify(path):
    key = get_key()
    with connect(path) as c: rows = c.execute('SELECT * FROM encrypted_transactions').fetchall()
    for r in rows:
        tx = r['transaction_id']
        decrypt(key,bytes(r['card_nonce']),bytes(r['card_ciphertext']),bytes(r['card_tag']),f'{tx}:card_number:v1'.encode())
        decrypt(key,bytes(r['expiry_nonce']),bytes(r['expiry_ciphertext']),bytes(r['expiry_tag']),f'{tx}:expiry:v1'.encode())
    print(f'Integrity verification passed for {len(rows)} record(s).')

def main():
    p = argparse.ArgumentParser(description='PACS Assignment 6 database encryption demo')
    p.add_argument('command', choices=['init','seed','encrypted-view','authorized-view','verify'])
    p.add_argument('--db', default=str(DB_DEFAULT)); a = p.parse_args(); path = Path(a.db)
    try:
        if a.command == 'init': init(path); print(f'Database initialized: {path}')
        elif a.command == 'seed': seed(path)
        elif a.command == 'encrypted-view': encrypted_view(path)
        elif a.command == 'authorized-view': authorized_view(path)
        elif a.command == 'verify': verify(path)
    except (RuntimeError, ValueError, sqlite3.Error) as e:
        print(f'ERROR: {e}', file=sys.stderr); return 1
    return 0
if __name__ == '__main__': raise SystemExit(main())
