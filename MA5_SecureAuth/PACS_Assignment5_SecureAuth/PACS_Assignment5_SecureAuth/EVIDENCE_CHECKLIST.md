# Demonstration Evidence Checklist

Capture screenshots from your own local run and paste them into the final submission document or keep them in an `evidence/` folder. Include short captions with the action and observed result.

1. **Home page** — shows project title and the four security capabilities.
2. **Registration defense** — weak password `password123` rejected.
3. **Successful local login + MFA** — dashboard after valid TOTP and demo biometric input. Do not include the actual TOTP secret in the screenshot.
4. **MFA rejection** — wrong TOTP or biometric input rejected.
5. **Rate limiting** — five incorrect local login attempts and the temporary lockout message/HTTP 429.
6. **RBAC denial** — signed in as `alice`, `/admin` returns 403.
7. **Admin console** — signed in as `admin`, user list and recent audit events visible.
8. **OAuth 2.0/OIDC flow** — if Google credentials are configured, show provider redirect and successful callback before MFA. Do not show client secrets or tokens.
9. **Automated tests** — terminal showing `pytest -q` and actual result.
10. **Source layout** — show `app.py`, `REPORT.md`, templates and tests.

Use accurate captions. If OAuth was not configured, state that the route is implemented but live provider sign-in was not demonstrated. Do not fabricate screenshots or results.
