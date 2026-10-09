import os, base64, sqlite3, tempfile, unittest
from pathlib import Path
from app import encrypt, decrypt, init, seed, SAMPLES

class EncryptionTests(unittest.TestCase):
    def test_round_trip_and_aad_tampering(self):
        key=os.urandom(32); aad=b'TX-1:card_number:v1'
        nonce, ct, tag=encrypt(key,'4111111111111111',aad)
        self.assertNotEqual(ct,b'4111111111111111')
        self.assertEqual(decrypt(key,nonce,ct,tag,aad),'4111111111111111')
        with self.assertRaises(ValueError): decrypt(key,nonce,ct,tag,b'TX-2:card_number:v1')
    def test_database_stores_ciphertext(self):
        old=os.environ.get('APP_ENCRYPTION_KEY'); os.environ['APP_ENCRYPTION_KEY']=base64.b64encode(os.urandom(32)).decode()
        try:
            with tempfile.TemporaryDirectory() as d:
                db=Path(d)/'test.db'; init(db); seed(db)
                with sqlite3.connect(db) as c: stored=c.execute('SELECT card_ciphertext FROM encrypted_transactions LIMIT 1').fetchone()[0]
                self.assertNotIn(b'4111111111111111',stored)
        finally:
            if old is None: os.environ.pop('APP_ENCRYPTION_KEY',None)
            else: os.environ['APP_ENCRYPTION_KEY']=old
if __name__=='__main__': unittest.main()
