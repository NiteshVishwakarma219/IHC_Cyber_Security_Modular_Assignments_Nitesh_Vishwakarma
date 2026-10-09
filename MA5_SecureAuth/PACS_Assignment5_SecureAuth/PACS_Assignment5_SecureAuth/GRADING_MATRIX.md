# Grading Traceability Matrix

| Rubric (25 marks each) | Evidence included | How to demonstrate |
|---|---|---|
| Access control model analysis and implementation | `REPORT.md` Sections 3; `app.py` role guards; admin UI | Explain DAC/MAC/RBAC/ABAC; show USER receives 403 for `/admin`, ADMIN succeeds |
| Password attack demonstration and defense | `app.py` registration validation, hash verification, throttling; `REPORT.md` Section 4 | Try weak registration, wrong-password attempts, inspect hash format |
| OAuth 2.0 and MFA integration | Authlib Google OIDC routes; TOTP and simulated biometric routes | Configure your own Google OAuth credentials for live test; otherwise demonstrate MFA and document OAuth setup limitation |
| Documentation, clarity, security discussion | `README.md`, `REPORT.md`, `SECURITY_NOTES.md`, `EVIDENCE_CHECKLIST.md` | Submit report and genuine screenshots/test output |

No score can be guaranteed. Marks depend on actual execution, the evaluator's interpretation, and the evidence submitted.
