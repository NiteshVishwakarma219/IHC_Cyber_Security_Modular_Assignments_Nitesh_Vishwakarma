# Assignment 6 evidence checklist
Capture genuine screenshots; never show keys, passwords, or real card data.
- [ ] Dependencies installed.
- [ ] `python app.py init` succeeds.
- [ ] `python app.py seed` inserts synthetic records.
- [ ] `python app.py encrypted-view` shows ciphertext.
- [ ] `python app.py authorized-view` shows masked card numbers.
- [ ] `python app.py verify` succeeds.
- [ ] `python -m unittest discover -s tests -v` passes.
- [ ] VeraCrypt container created/mounted (or supported BitLocker data volume used).
- [ ] Database file shown inside the mounted volume.
- [ ] Volume safely dismounted/locked; evidence does not expose secrets.
- [ ] Report and references reviewed; portal answer copied from `PORTAL_ANSWER.txt`.
