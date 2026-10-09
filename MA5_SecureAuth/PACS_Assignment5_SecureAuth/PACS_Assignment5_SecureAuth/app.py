import os, sqlite3, time, secrets, hashlib, hmac
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, request, redirect, url_for, session, render_template, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from authlib.integrations.flask_client import OAuth
import pyotp

APP_SECRET = os.environ.get("FLASK_SECRET_KEY")
if not APP_SECRET:
    # Development-only fallback. Set FLASK_SECRET_KEY before any real deployment.
    APP_SECRET = "dev-only-change-this-secret-before-deployment"

DB_PATH = os.environ.get("PACS_DB_PATH", "pacs.db")
app = Flask(__name__)
app.secret_key = APP_SECRET
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=1800,
)
oauth = OAuth(app)
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

# In-memory throttling is suitable only for a single-process classroom demo.
# Production deployments must use a shared store (e.g., Redis/API gateway).
FAILURES = {}
WINDOW_SECONDS = 300
MAX_FAILURES = 5
LOCK_SECONDS = 300
BIOMETRIC_DEMO_CODE = os.environ.get("BIOMETRIC_DEMO_CODE", "BIO-DEMO-4821")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT,
            role TEXT NOT NULL DEFAULT 'USER',
            totp_secret TEXT,
            biometric_hash TEXT,
            auth_provider TEXT NOT NULL DEFAULT 'local',
            created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS audit(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            at TEXT NOT NULL, username TEXT, event TEXT NOT NULL,
            ip TEXT, detail TEXT
        )""")
        count = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]
        if count == 0:
            conn.execute("INSERT INTO users(username,email,password_hash,role,totp_secret,biometric_hash,auth_provider,created_at) VALUES(?,?,?,?,?,?,?,?)",
                ("admin", "admin@example.test", generate_password_hash("ChangeMe-Admin-2026!"), "ADMIN",
                 pyotp.random_base32(), hashlib.sha256(BIOMETRIC_DEMO_CODE.encode()).hexdigest(), "local", now()))
            conn.execute("INSERT INTO users(username,email,password_hash,role,totp_secret,biometric_hash,auth_provider,created_at) VALUES(?,?,?,?,?,?,?,?)",
                ("alice", "alice@example.test", generate_password_hash("ChangeMe-User-2026!"), "USER",
                 pyotp.random_base32(), hashlib.sha256(BIOMETRIC_DEMO_CODE.encode()).hexdigest(), "local", now()))


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def audit(username, event, detail=""):
    with db() as conn:
        conn.execute("INSERT INTO audit(at,username,event,ip,detail) VALUES(?,?,?,?,?)",
                     (now(), username, event, request.remote_addr or "unknown", detail[:250]))


def strong_password(p):
    return (len(p) >= 12 and any(c.islower() for c in p) and any(c.isupper() for c in p)
            and any(c.isdigit() for c in p) and any(not c.isalnum() for c in p))


def password_is_known_demo_weak(p):
    # A small local demonstration denylist; not a replacement for a breached-password service.
    return p.lower() in {"password", "password123", "qwerty123", "admin123", "letmein123"}


def failure_state(key):
    current = time.time()
    state = FAILURES.get(key, {"count": 0, "start": current, "locked_until": 0})
    if current - state["start"] > WINDOW_SECONDS:
        state = {"count": 0, "start": current, "locked_until": 0}
    FAILURES[key] = state
    return state


def record_failure(key):
    state = failure_state(key)
    state["count"] += 1
    if state["count"] >= MAX_FAILURES:
        state["locked_until"] = time.time() + LOCK_SECONDS


def clear_failures(key):
    FAILURES.pop(key, None)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in first.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            if session.get("role") not in roles:
                audit(session.get("username"), "AUTHZ_DENIED", request.path)
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def current_user():
    if not session.get("user_id"):
        return None
    with db() as conn:
        return conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'; base-uri 'self'; frame-ancestors 'none'"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/")
def index():
    return render_template("index.html", user=current_user(), oauth_enabled=bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not username or len(username) < 3 or len(username) > 40:
            flash("Username must contain 3–40 characters.", "danger")
        elif not email or len(email) > 254 or "@" not in email:
            flash("Enter a valid email address.", "danger")
        elif not strong_password(password):
            flash("Use at least 12 characters with upper/lowercase, a number, and a symbol.", "danger")
        elif password_is_known_demo_weak(password):
            flash("This password appears on the demo weak-password denylist.", "danger")
        else:
            try:
                with db() as conn:
                    conn.execute("INSERT INTO users(username,email,password_hash,role,totp_secret,biometric_hash,auth_provider,created_at) VALUES(?,?,?,?,?,?,?,?)",
                        (username, email, generate_password_hash(password), "USER", pyotp.random_base32(),
                         hashlib.sha256(BIOMETRIC_DEMO_CODE.encode()).hexdigest(), "local", now()))
                audit(username, "REGISTER_SUCCESS")
                flash("Account created. Sign in and complete MFA setup.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Username or email already exists.", "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        key = f"{request.remote_addr}:{username.lower()}"
        state = failure_state(key)
        if state["locked_until"] > time.time():
            audit(username, "LOGIN_THROTTLED")
            flash("Too many failed attempts. Try again after the temporary lockout.", "danger")
            return render_template("login.html"), 429
        with db() as conn:
            user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user or not user["password_hash"] or not check_password_hash(user["password_hash"], password):
            record_failure(key)
            audit(username, "LOGIN_FAILED")
            flash("Invalid username or password.", "danger")
            return render_template("login.html"), 401
        clear_failures(key)
        session.clear()
        session["pending_user_id"] = user["id"]
        session["pending_username"] = user["username"]
        session["pending_auth_provider"] = "local"
        audit(username, "PASSWORD_VERIFIED")
        return redirect(url_for("mfa"))
    return render_template("login.html")


@app.route("/mfa", methods=["GET", "POST"])
def mfa():
    if not session.get("pending_user_id"):
        return redirect(url_for("login"))
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (session["pending_user_id"],)).fetchone()
    if not user:
        session.clear()
        return redirect(url_for("login"))
    if request.method == "POST":
        otp = request.form.get("otp", "").strip()
        biometric = request.form.get("biometric", "").strip()
        totp_ok = bool(user["totp_secret"] and pyotp.TOTP(user["totp_secret"]).verify(otp, valid_window=1))
        expected_hash = user["biometric_hash"] or ""
        submitted_hash = hashlib.sha256(biometric.encode()).hexdigest()
        biometric_ok = bool(biometric) and hmac.compare_digest(expected_hash, submitted_hash)
        if totp_ok and biometric_ok:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["auth_provider"] = user["auth_provider"]
            session.permanent = True
            audit(user["username"], "MFA_SUCCESS")
            return redirect(url_for("dashboard"))
        audit(user["username"], "MFA_FAILED", f"totp={totp_ok}, biometric={biometric_ok}")
        flash("MFA failed. Both the time-based OTP and simulated biometric demo code must match.", "danger")
        return render_template("mfa.html", user=user), 401
    return render_template("mfa.html", user=user)


@app.route("/logout")
def logout():
    username = session.get("username") or session.get("pending_username")
    if username:
        audit(username, "LOGOUT")
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user())


@app.route("/user-area")
@roles_required("USER", "ADMIN")
def user_area():
    return render_template("protected.html", heading="User Area", message="Authenticated users can access this resource.", user=current_user())


@app.route("/admin")
@roles_required("ADMIN")
def admin():
    with db() as conn:
        users = conn.execute("SELECT id,username,email,role,auth_provider,created_at FROM users ORDER BY id").fetchall()
        logs = conn.execute("SELECT at,username,event,ip,detail FROM audit ORDER BY id DESC LIMIT 30").fetchall()
    return render_template("admin.html", users=users, logs=logs, user=current_user())


@app.route("/admin/role/<int:user_id>", methods=["POST"])
@roles_required("ADMIN")
def change_role(user_id):
    role = request.form.get("role")
    if role not in {"USER", "ADMIN"}:
        abort(400)
    if user_id == session["user_id"] and role != "ADMIN":
        flash("You cannot remove your own administrator role in this demo.", "danger")
        return redirect(url_for("admin"))
    with db() as conn:
        target = conn.execute("SELECT username FROM users WHERE id=?", (user_id,)).fetchone()
        if not target:
            abort(404)
        conn.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    audit(session.get("username"), "ROLE_CHANGED", f"user={target['username']}; role={role}")
    flash("Role updated.", "success")
    return redirect(url_for("admin"))


@app.route("/oauth/google")
def google_login():
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        flash("Google OAuth is not configured. Follow README setup instructions.", "warning")
        return redirect(url_for("index"))
    redirect_uri = url_for("google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route("/oauth/google/callback")
def google_callback():
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        abort(503)
    token = oauth.google.authorize_access_token()
    info = token.get("userinfo")
    if not info:
        info = oauth.google.userinfo()
    email = (info.get("email") or "").lower()
    if not email or not info.get("email_verified", False):
        flash("Google did not provide a verified email.", "danger")
        return redirect(url_for("login"))
    username = "google_" + hashlib.sha256(email.encode()).hexdigest()[:12]
    with db() as conn:
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if not user:
            conn.execute("INSERT INTO users(username,email,password_hash,role,totp_secret,biometric_hash,auth_provider,created_at) VALUES(?,?,?,?,?,?,?,?)",
                (username, email, None, "USER", pyotp.random_base32(),
                 hashlib.sha256(BIOMETRIC_DEMO_CODE.encode()).hexdigest(), "google", now()))
            user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    session.clear()
    session["pending_user_id"] = user["id"]
    session["pending_username"] = user["username"]
    session["pending_auth_provider"] = "google"
    audit(user["username"], "OAUTH_SUCCESS", "Google OIDC; MFA still required")
    flash("Google identity verified. Complete the second-factor checks.", "success")
    return redirect(url_for("mfa"))


@app.route("/security")
def security():
    return render_template("security.html", user=current_user())


@app.errorhandler(403)
def forbidden(_):
    return render_template("error.html", code=403, message="Forbidden: your current role is not authorized for this resource."), 403


@app.errorhandler(404)
def not_found(_):
    return render_template("error.html", code=404, message="The requested resource was not found."), 404


init_db()

if __name__ == "__main__":
    # Local demo only. Do not expose Flask's development server to the public internet.
    app.run(host="127.0.0.1", port=5000, debug=False)
