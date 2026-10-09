# PACS Assignment 5 — Secure Authentication and Access Control

**Module:** IHC — Practical Approach to Cyber Security  
**Assignment:** 5 — Authentication and Access Control  
**Implementation:** Python 3, Flask, SQLite, Authlib, PyOTP  
**Status:** Runnable classroom prototype; not production-ready.

## 1. Requirement mapping

| Assignment requirement | Implementation / evidence |
|---|---|
| Compare access-control models (DAC, MAC, RBAC) | `REPORT.md`, Section 3; RBAC is implemented in `app.py` |
| Demonstrate password attacks and at least two defenses | `REPORT.md`, Section 4; local weak-password attempts, repeated failed login attempts, adaptive password hashing, strength checks, denylist, throttling |
| Integrate OAuth 2.0 into a sample application | Optional Google Authorization Code + OpenID Connect integration in `/oauth/google` and callback; credentials configured locally |
| Implement MFA including biometric factor (can be simulated) | TOTP plus explicitly simulated biometric demo code in `/mfa` |
| Document design, implementation and security considerations | `REPORT.md`, `SECURITY_NOTES.md`, this README |
| Source code, screenshots/video, brief model report, dataset/library references | Application source and templates included; screenshot checklist in `EVIDENCE_CHECKLIST.md`; references in report |

## 2. Quick start (Windows PowerShell)

Use Python 3.10 or newer.

```powershell
cd PACS_Assignment5_SecureAuth
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:FLASK_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(48))")
python app.py
```

Open `http://127.0.0.1:5000`. This binds to loopback only.

If PowerShell blocks activation, run the commands using `.\.venv\Scripts\python.exe` directly, or use Command Prompt activation `.\.venv\Scripts\activate.bat`.

## 3. Seeded demo accounts

The SQLite database is created automatically on first launch.

- **Administrator:** username `admin`, password `ChangeMe-Admin-2026!`
- **Standard user:** username `alice`, password `ChangeMe-User-2026!`
- **Simulated biometric input:** `BIO-DEMO-4821`

These are demonstration credentials only. Do not deploy them or reuse them. For an authenticator code, get the seeded user's TOTP secret from the local database and generate the current code:

```powershell
python -c "import sqlite3,pyotp; c=sqlite3.connect('pacs.db'); print([(u,s,pyotp.TOTP(s).now()) for u,s in c.execute('select username,totp_secret from users where username in (?,?)',('admin','alice'))])"
```

Use the current six-digit code and the simulated biometric input on the MFA page. The OTP changes every 30 seconds. If the app is run with a different `PACS_DB_PATH`, adjust the database path in the command.

## 4. Optional Google OAuth 2.0 / OIDC configuration

OAuth is deliberately optional so the local application works without external credentials. To demonstrate the real federated flow:

1. Create a Google OAuth client in Google Cloud Console.
2. Configure the local development redirect URI exactly as `http://127.0.0.1:5000/oauth/google/callback`.
3. Set the environment variables in the same PowerShell session before starting the app:

```powershell
$env:GOOGLE_CLIENT_ID = "your-client-id"
$env:GOOGLE_CLIENT_SECRET = "your-client-secret"
$env:FLASK_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(48))")
python app.py
```

4. Click **Continue with Google OAuth 2.0**. Sign in using a test account with verified email, then complete the second-factor page.
5. Never commit credentials. For a production app, use HTTPS, exact redirect URIs, secret management, CSRF/state protections supplied by the OAuth library, account linking rules, and a reviewed recovery process.

The OAuth login uses OpenID Connect (OIDC) scopes `openid email profile`. OAuth 2.0 is an authorization framework; OIDC adds the identity layer.

## 5. Demonstration plan

1. **Normal login:** sign in as `alice`, generate current TOTP, enter `BIO-DEMO-4821`, verify the dashboard loads.
2. **RBAC denial:** while signed in as `alice`, navigate to `/admin`. Expected: HTTP 403.
3. **Admin access:** sign in as `admin`, complete both factors, open Admin. Users and recent audit events appear.
4. **Password strength defense:** try registering a new account with `password123`. Expected: rejected.
5. **Password-guessing defense:** on the local login form, submit an incorrect password five times for the same username/IP pair. Expected: temporary throttling/HTTP 429 after the threshold.
6. **MFA defense:** enter a wrong TOTP or biometric code. Expected: access denied and an audit event.
7. **OAuth flow:** only after credentials are configured, complete Google sign-in; the account must still pass MFA.
8. Capture screenshots according to `EVIDENCE_CHECKLIST.md`. Use your own actual run results; do not present mock screenshots or unexecuted tests as evidence.

## 6. Run tests

```powershell
pip install pytest
pytest -q
```

Tests cover homepage availability, weak-password rejection, RBAC denial, and password-hash storage. These are baseline functional tests, not a full penetration test.

## 7. Important limitations

- The biometric factor is simulated with a demo string and a stored digest. It is **not** real biometric authentication.
- The rate limiter is in-memory and intended for a single-process local demonstration. It is not reliable across multiple workers or restarts.
- OAuth requires your own client credentials and an interactive browser sign-in; this package does not include or invent credentials.
- No claim of HIPAA compliance or production security is made.
- Do not expose the Flask development server to the public internet.
