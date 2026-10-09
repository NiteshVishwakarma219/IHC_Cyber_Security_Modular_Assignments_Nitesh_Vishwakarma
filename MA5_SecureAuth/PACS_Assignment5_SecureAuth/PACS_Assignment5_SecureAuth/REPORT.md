# Assignment 5 Report: Authentication and Access Control

## 1. Introduction and objectives

This project implements a small web application that demonstrates password-based sign-in, optional federated sign-in using Google OAuth 2.0 with OpenID Connect, multi-factor verification, and role-based authorization. The design follows the assignment's four assessment areas: access-control model analysis and implementation, password-attack demonstration and defense, OAuth 2.0 and MFA integration, and clear documentation/security discussion.

The application uses seeded demo identities and a local SQLite database so that the main flows can be demonstrated without paid cloud services. It is an educational prototype, not a production identity platform.

## 2. Architecture and authentication flow

**Components**
- Browser: registration, login, MFA and protected pages.
- Flask application: authentication routes, OAuth callback, MFA verification, role guards and security headers.
- SQLite: account records and audit events.
- Google identity provider (optional): OAuth 2.0 Authorization Code flow with OIDC identity information.
- PyOTP: TOTP generation/verification.
- Simulated biometric module: compares a demo sample's SHA-256 digest with the enrolled demo digest.

**Local-password flow**
1. The user submits username and password over the local demo.
2. The application retrieves the account and verifies the stored adaptive password hash.
3. On success, a pending authentication session is created; the user is not yet fully authenticated.
4. The user must provide a current TOTP and the simulated biometric sample.
5. Only after both checks succeed is the authenticated session established.
6. Each protected route checks authentication and, where required, the user's role.

**Federated flow**
1. The browser is redirected to Google's authorization endpoint.
2. Google authenticates the user and returns the browser to the registered callback.
3. Authlib processes the response using provider metadata and obtains OIDC user information.
4. The application requires a verified email and creates or locates a standard-user record.
5. The application still requires its second-factor page before granting an application session.

OAuth 2.0 is an authorization framework; OpenID Connect provides the standardized identity layer used here. OAuth client credentials are not bundled and must be supplied by the demonstrator.

## 3. Access-control model comparison

| Model | Decision basis | Strengths | Limitations | Suitable examples |
|---|---|---|---|---|
| DAC — Discretionary Access Control | A resource owner decides who may access that resource | Flexible collaboration and delegated sharing | Owners can accidentally expose resources; policy can become inconsistent | Shared files, collaborative workspaces |
| MAC — Mandatory Access Control | Central policy and labels/classifications determine access; users cannot freely override policy | Strong centralized enforcement and consistent classifications | Rigid; administration and classification can be complex | Classified government or military environments |
| RBAC — Role-Based Access Control | Permissions are assigned to roles; users receive roles | Simple administration, scalable for job functions, easy to audit | Role explosion or coarse permissions when roles are poorly designed | Enterprise applications with user/admin separation |
| ABAC — Attribute-Based Access Control | Policies evaluate subject, resource, action and environmental attributes | Fine-grained and context-aware decisions | More complex to design, test and explain | Contextual access by department, sensitivity, device or location |

**Selected model:** RBAC. The sample defines `USER` and `ADMIN` roles. `/dashboard` requires an authenticated session; `/user-area` accepts `USER` or `ADMIN`; `/admin` and role-management actions require `ADMIN`. The role is checked on the server for every protected request, rather than trusting a role value supplied by the browser. Unauthorized access generates an audit event and a 403 response.

RBAC is appropriate for this compact demonstration because its permission structure is easy to inspect and test. A real healthcare or enterprise application could combine RBAC with ABAC policies, resource ownership checks, and tenant boundaries.

## 4. Password attacks and defenses

### 4.1 Threats demonstrated

- **Password guessing / brute-force attempts:** repeated guesses may eventually discover a weak or reused password.
- **Credential stuffing:** attackers try username/password pairs leaked from unrelated services.
- **Weak-password selection:** common passwords can be guessed quickly.
- **Password database exposure:** plaintext password storage would disclose every password immediately if the database were stolen.

Only the local demonstration application should be tested. Do not run guessing attempts against external accounts or services.

### 4.2 Implemented defenses

1. **Adaptive password hashing:** password values are stored using Werkzeug's password-hashing function (scrypt in supported Werkzeug versions), not as plaintext. Hash verification uses the library API.
2. **Strength validation:** registration requires at least 12 characters, lowercase and uppercase letters, a digit and a symbol.
3. **Local weak-password denylist:** a small list rejects common examples such as `password123`. This illustrates the control; a real service should use a maintained blocklist and breached-password screening.
4. **Login throttling / temporary lockout:** five failures for the same IP/username key within the configured window trigger a five-minute temporary lockout. The login response is generic to reduce account enumeration.
5. **MFA:** a guessed password alone is not enough to establish an authenticated session.
6. **Audit trail:** failed login, successful password verification, MFA outcomes, role denials and administrative role changes are logged.

### 4.3 Controlled test and expected observations

| Test | Procedure | Expected result |
|---|---|---|
| Weak password | Register with `password123` | Registration rejected |
| Hash storage | Inspect `password_hash` in SQLite | Hash differs from submitted password |
| Guessing throttling | Submit five incorrect passwords for the same username from the same local IP | Further attempt is temporarily throttled |
| MFA failure | Submit wrong TOTP or simulated biometric input | MFA rejected; no authenticated session |
| Privilege escalation attempt | Sign in as `alice` and request `/admin` | HTTP 403; authorization denial logged |

The in-memory limiter is intentionally simple for a classroom lab. It resets on restart and does not coordinate across multiple worker processes. A production implementation should use a shared rate-limit store, progressive delays or risk-based controls, alerting and recovery protections.

## 5. OAuth 2.0 and multi-factor authentication

### 5.1 OAuth/OIDC

The sample uses Authlib to register Google's OpenID Connect discovery endpoint and request `openid`, `email` and `profile`. When valid client credentials are configured, the application redirects to Google and handles the callback. It requires a verified email before creating/locating a local account. Credentials and callback configuration are supplied by the student during setup.

OAuth 2.0 is not itself a password replacement or an identity protocol. OpenID Connect adds authentication and identity claims. The implementation uses the provider's maintained metadata and library flow rather than manually parsing OAuth responses. Production deployments must use HTTPS and exact redirect URIs, protect secrets, review account linking, validate identity claims and implement secure session/recovery controls.

### 5.2 TOTP factor

TOTP produces short-lived numeric codes based on a shared secret and time. PyOTP verifies the submitted code with a small time window to account for clock drift. In a production system, enrollment would present a QR code, require proof of possession before enabling MFA, encrypt or tightly protect the secret, and provide controlled recovery/revocation.

### 5.3 Simulated biometric factor

The second factor is a fixed demo string (`BIO-DEMO-4821`) whose SHA-256 digest is compared with the stored digest. This is only a **simulation** to satisfy the assignment's allowance for simulated biometrics. It does not measure a fingerprint, face or other human trait, and the string can be copied. A hash does not turn a low-entropy demo string into a real biometric. For production use, prefer platform-backed WebAuthn/passkeys or a vetted biometric system with consent, liveness/anti-replay measures, privacy controls, template protection and a recovery path.

### 5.4 Factor independence

The two demo checks illustrate two factors in the application workflow, but the simulated code is not a genuine inherence factor. Therefore, the report does not claim that the demo has production-grade biometric MFA. A stronger practical implementation would pair a password or federated identity with a TOTP/security key and use WebAuthn for phishing-resistant possession/user-verification.

## 6. Security considerations

- **Transport security:** local HTTP is restricted to loopback for demonstration. Production requires HTTPS/TLS.
- **Session security:** HTTP-only and SameSite cookies are set; Secure is configurable for HTTPS. The secret key must be a random environment secret.
- **Authorization:** server-side route decorators enforce roles. UI visibility alone is not an authorization control.
- **Input handling:** basic validation and parameterized SQL operations are used.
- **Security headers:** CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy and no-store are added.
- **Auditability:** security events include timestamps, usernames, source IP and short details.
- **Privacy:** use synthetic accounts only; avoid real biometric samples and real personal information.
- **CSRF:** the classroom prototype does not include a complete CSRF token system; this must be added before deployment, especially for role-changing POST routes.
- **Rate limiting:** in-memory state is not distributed or persistent; use a shared store/API gateway in production.
- **Account lifecycle:** recovery, MFA reset, session revocation, email verification, credential rotation and alerting are not fully implemented.
- **Compliance:** this project is not certified or assessed for HIPAA or any other regulatory compliance.

## 7. Test plan and evidence

Functional tests are supplied in `tests/test_security.py`. Run them using `pytest -q`. Capture real screenshots of the running application for the evidence checklist. Record the actual test output and environment used. Do not claim a test passed until it has been run.

## 8. Conclusion

The prototype demonstrates layered authentication and server-side authorization in a runnable application. It compares DAC, MAC, RBAC and ABAC; implements RBAC; demonstrates weak-password rejection and login throttling; supports optional Google OAuth/OIDC; and requires TOTP plus a simulated biometric input before granting access. The implementation also documents important boundaries, especially that the biometric and local rate limiter are classroom simulations and that production deployment requires further security engineering.

## 9. References

1. TCS IHC, *Practical Approach to Cyber Security — Assignment 5: Authentication and Access Control* (assignment brief supplied for this task).
2. Flask documentation: https://flask.palletsprojects.com/
3. Authlib Flask client documentation: https://docs.authlib.org/en/latest/client/flask.html
4. Google OpenID Connect documentation: https://developers.google.com/identity/openid-connect/openid-connect
5. PyOTP documentation: https://pyauth.github.io/pyotp/
6. Werkzeug security utilities: https://werkzeug.palletsprojects.com/en/stable/utils/#module-werkzeug.security
7. OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
8. OWASP Password Storage Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
9. OWASP Authorization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
10. Have I Been Pwned Pwned Passwords: https://haveibeenpwned.com/Passwords (referenced by the assignment as a breached-password analysis resource; this prototype uses a local demonstration denylist and does not call the service).
11. Spring Security reference (alternative implementation/library suggested by assignment): https://docs.spring.io/spring-security/reference/
12. OAuth 2.0 RFC 6749: https://www.rfc-editor.org/rfc/rfc6749
13. OpenID Connect Core: https://openid.net/specs/openid-connect-core-1_0.html
