# Security Notes

## Safe classroom demonstration scope
Run only on `127.0.0.1`. The login guessing demonstration is deliberately limited to the app's own seeded demo accounts. Do not test credentials against any external system.

## Controls currently present
- Password hashing via Werkzeug.
- Password strength validation and small local denylist.
- Temporary per-IP/username throttling.
- TOTP plus simulated biometric-code verification.
- Role checks at protected routes.
- Audit logging and baseline browser security headers.
- OAuth library integration using provider discovery when configured.

## Known gaps / non-production controls
- No CSRF token implementation.
- In-memory rate limiting is single-process only.
- No formal MFA enrollment or recovery workflow.
- Simulated biometric code is not real biometric authentication.
- No security review, penetration test, compliance audit, or production deployment validation has been performed.
- Local SQLite and demo seed credentials are for a disposable learning environment.

## Before any real deployment
Use HTTPS, secure secret storage, production WSGI server, managed database, CSRF protection, distributed throttling, strong account recovery, email verification, session revocation, monitoring, dependency scanning, data minimization, backups, and a formal security/privacy review.
