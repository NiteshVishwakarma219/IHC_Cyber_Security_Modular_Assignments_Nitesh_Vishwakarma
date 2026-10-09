"""
PACS Assignment 7 — Usable Security Nudge Prototype
A local educational demo that nudges users to make safer link-opening decisions.
Do not use this prototype as a production phishing detector.
"""
from __future__ import annotations

from flask import Flask, render_template, request, session, redirect, url_for
from urllib.parse import urlparse
import ipaddress
import re

app = Flask(__name__)
app.secret_key = "local-classroom-demo-change-before-deployment"


def inspect_url(value: str) -> dict:
    """Heuristic URL check for demonstration; not a reputation service."""
    raw = (value or "").strip()
    reasons = []
    if not raw:
        return {"level": "unknown", "label": "No URL entered", "reasons": ["Enter a URL to review it."]}

    candidate = raw if "://" in raw else "https://" + raw
    try:
        parsed = urlparse(candidate)
        host = (parsed.hostname or "").lower().rstrip(".")
    except ValueError:
        host = ""

    if not host:
        return {"level": "danger", "label": "Invalid or incomplete URL", "reasons": ["The address could not be parsed. Do not open it until you verify the source."]}

    if parsed.scheme.lower() not in {"http", "https"}:
        reasons.append("The link uses an unexpected protocol.")
    if parsed.username or parsed.password:
        reasons.append("The address contains user-information before the host, which can disguise the real destination.")
    if "xn--" in host:
        reasons.append("The hostname contains an internationalized/punycode label; check for look-alike characters.")
    try:
        ipaddress.ip_address(host)
        reasons.append("The destination is a raw IP address rather than a recognizable domain.")
    except ValueError:
        pass
    if host.count(".") >= 4:
        reasons.append("The hostname has many subdomain levels; confirm the registered domain.")
    if len(host) > 50:
        reasons.append("The hostname is unusually long.")
    suspicious_words = ("login", "verify", "secure", "account", "update", "password", "wallet", "urgent")
    if any(word in host for word in suspicious_words):
        reasons.append("The hostname uses words often seen in account-alert lures; this alone does not prove fraud.")
    if parsed.scheme.lower() == "http":
        reasons.append("The connection scheme is HTTP, not HTTPS; HTTPS alone would not prove the site is trustworthy.")

    if reasons:
        return {
            "level": "caution",
            "label": "Pause and verify before opening",
            "reasons": reasons,
            "host": host,
            "scheme": parsed.scheme.lower(),
        }
    return {
        "level": "clear",
        "label": "No basic warning signs detected",
        "reasons": ["This simple check found no configured warning signs. It cannot confirm that the link is safe."],
        "host": host,
        "scheme": parsed.scheme.lower(),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    url = ""
    action = None
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        action = request.form.get("action", "check")
        if action == "check":
            result = inspect_url(url)
            session["last_result"] = result
            session["last_url"] = url
        elif action == "continue":
            # This demo intentionally does not navigate to the entered URL.
            session["last_action"] = "continue_selected"
            result = session.get("last_result") or inspect_url(url)
            result = dict(result)
            result["user_choice"] = "You selected continue. In a real product, make sure the destination is expected and independently verified."
        elif action == "cancel":
            session["last_action"] = "cancel_selected"
            result = session.get("last_result") or inspect_url(url)
            result = dict(result)
            result["user_choice"] = "You chose not to continue. That is a safe choice when you cannot verify the destination."
    return render_template("index.html", result=result, url=url)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
