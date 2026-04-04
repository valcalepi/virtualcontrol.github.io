"""
VCF Health Check — Partner License Manager
============================================
Manages partner license tiers, enhanced key generation/validation,
and tier-based enforcement for the partner ecosystem.

Business model: Virtual Control → VMware Partners → Enterprise Clients
No trial mode — a valid license is required to use the app.
Admin users with correct credentials serve as a backdoor.

Copyright (c) 2026 Virtual Control LLC. All rights reserved.
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import tkinter as tk
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

# ============================================================================
#  CONSTANTS
# ============================================================================

_SECRETS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".vcf-hc-secrets.json")


def _load_secret(key_name: str, env_var: str) -> bytes:
    """Load a secret from env var or persistent local secrets file.

    Priority: env var > .vcf-hc-secrets.json > auto-generated random secret.
    """
    val = os.environ.get(env_var)
    if val:
        return val.encode()
    secrets: dict = {}
    if os.path.isfile(_SECRETS_FILE):
        try:
            with open(_SECRETS_FILE) as f:
                secrets = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    if key_name in secrets:
        return secrets[key_name].encode()
    new_val = os.urandom(32).hex()
    secrets[key_name] = new_val
    try:
        with open(_SECRETS_FILE, "w") as f:
            json.dump(secrets, f, indent=2)
    except OSError:
        pass
    return new_val.encode()


_LICENSE_SECRET = _load_secret("license_secret", "VCF_LICENSE_SECRET")
_PARTNER_SECRET = _load_secret("partner_secret", "VCF_PARTNER_SECRET")
LICENSE_GRACE_DAYS = 14
LICENSES_FILE = "vcf-health-licenses.json"

# Admin backdoor password hash (SHA-256 of the admin password)
# Set VCF_ADMIN_PASSWORD_HASH env var or add to vcf-health-check.env
_ADMIN_BACKDOOR_HASH = os.environ.get("VCF_ADMIN_PASSWORD_HASH")
if not _ADMIN_BACKDOOR_HASH:
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "vcf-health-check.env")
    if os.path.isfile(_env_path):
        try:
            with open(_env_path) as _ef:
                for _line in _ef:
                    _line = _line.strip()
                    if _line.startswith("VCF_ADMIN_PASSWORD_HASH="):
                        _ADMIN_BACKDOOR_HASH = _line.split("=", 1)[1].strip().strip("'\"")
                        break
        except OSError:
            pass

# ── Tier Definitions ────────────────────────────────────────────────────────

TIER_DEFINITIONS = {
    "standard": {
        "label": "Standard",
        "max_environments": 5,
        "max_clients": 3,
        "features": [],
    },
    "starter": {  # backward-compat alias → same limits as standard
        "label": "Standard",
        "max_environments": 5,
        "max_clients": 3,
        "features": [],
    },
    "professional": {
        "label": "Professional",
        "max_environments": 25,
        "max_clients": 15,
        "features": ["branding", "scheduling"],
    },
    "enterprise": {
        "label": "Enterprise",
        "max_environments": 100,
        "max_clients": 0,  # 0 = unlimited
        "features": ["branding", "scheduling", "api_export", "white_label"],
    },
    "custom": {
        "label": "Custom",
        "max_environments": 0,
        "max_clients": 0,
        "features": [],
    },
}

TIER_COLORS = {
    "standard": "#3498DB",
    "starter": "#3498DB",  # backward-compat alias
    "professional": "#9B59B6",
    "enterprise": "#E67E22",
    "custom": "#1ABC9C",
}


# ============================================================================
#  DATA PERSISTENCE
# ============================================================================

def _licenses_path(script_dir: str) -> str:
    return os.path.join(script_dir, LICENSES_FILE)


def _load_licenses(script_dir: str) -> dict:
    path = _licenses_path(script_dir)
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"_version": "1.0", "partner_license": None, "activation_date": None, "last_validated": None}


def _save_licenses(script_dir: str, data: dict):
    path = _licenses_path(script_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


# ============================================================================
#  ENHANCED PARTNER LICENSE KEY SYSTEM
# ============================================================================

def generate_partner_license_key(
    partner_name: str,
    partner_id: str,
    tier: str,
    expiry_date: str,
    max_environments: int = 0,
    max_clients: int = 0,
    features: Optional[List[str]] = None,
) -> str:
    """Generate an enhanced partner license key (admin tool).

    Format: VCF-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (8 groups)
    """
    tier_def = TIER_DEFINITIONS.get(tier, TIER_DEFINITIONS["standard"])
    if max_environments == 0:
        max_environments = tier_def["max_environments"]
    if max_clients == 0:
        max_clients = tier_def["max_clients"]
    if features is None:
        features = tier_def["features"]

    payload = json.dumps({
        "pn": partner_name,
        "pi": partner_id,
        "t": tier,
        "me": max_environments,
        "mc": max_clients,
        "f": features,
        "e": expiry_date,
        "i": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }, separators=(",", ":"))

    sig = hmac.new(_PARTNER_SECRET, payload.encode(), hashlib.sha256).hexdigest()
    raw = payload.encode().hex() + "." + sig

    # Hex encoding is case-insensitive, safe for key formatting
    clean = raw.replace(".", "X").upper()
    # Split into 5-char groups (variable length based on payload)
    if len(clean) % 5:
        clean += "0" * (5 - len(clean) % 5)
    groups = [clean[i:i+5] for i in range(0, len(clean), 5)]
    return "VCF-" + "-".join(groups)


def validate_partner_license(key: str) -> dict:
    """Validate a partner license key.

    Returns dict with: valid, partner_name, partner_id, tier, max_environments,
    max_clients, features, expires, issued, expired, grace.
    """
    try:
        # Strip VCF- prefix and dashes
        raw = key.replace("VCF-", "").replace("-", "").lower()
        if len(raw) < 20:
            return {"valid": False}

        # Strip padding zeros, then restore 'x' → '.' separator
        raw = raw.rstrip("0") or raw
        raw = raw.replace("x", ".")

        if "." not in raw:
            return {"valid": False}

        parts = raw.split(".", 1)
        payload_hex = parts[0]
        sig_received = parts[1].lower() if len(parts) > 1 else ""

        # Decode hex payload
        payload_bytes = bytes.fromhex(payload_hex)
        payload = json.loads(payload_bytes.decode())

        # Verify HMAC — full-length constant-time comparison
        # Accept both full 64-char (new) and legacy 28-char signatures
        full_sig = hmac.new(_PARTNER_SECRET, payload_bytes, hashlib.sha256).hexdigest()
        if len(sig_received) == 28:
            expected_sig = full_sig[:28]
        else:
            expected_sig = full_sig
        if not hmac.compare_digest(sig_received, expected_sig.lower()):
            return {"valid": False}

        # Parse payload
        partner_name = payload.get("pn", "")
        partner_id = payload.get("pi", "")
        tier = payload.get("t", "starter")
        max_environments = payload.get("me", 5)
        max_clients = payload.get("mc", 3)
        features = payload.get("f", [])
        expiry = payload.get("e", "")
        issued = payload.get("i", "")

        expired = False
        grace = False
        days_remaining = 0
        if expiry:
            try:
                exp_dt = datetime.fromisoformat(expiry)
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                days_past = (datetime.now(timezone.utc) - exp_dt).days
                days_remaining = -days_past  # positive = days left
                if days_past > 0:
                    expired = True
                    grace = days_past <= LICENSE_GRACE_DAYS
            except Exception as e:
                logging.debug("Suppressed: %s", e)

        return {
            "valid": True,
            "partner_name": partner_name,
            "partner_id": partner_id,
            "tier": tier,
            "max_environments": max_environments,
            "max_clients": max_clients,
            "features": features,
            "expires": expiry,
            "issued": issued,
            "expired": expired,
            "grace": grace,
            "days_remaining": days_remaining,
        }
    except Exception as e:
        return {"valid": False}


# ============================================================================
#  LEGACY LICENSE COMPATIBILITY
# ============================================================================

def is_legacy_license(key: str) -> bool:
    """Check if a key is the old 4-group format (VCF-XXXXX-XXXXX-XXXXX-XXXXX)."""
    parts = key.replace("VCF-", "").split("-")
    return len(parts) == 4 and all(len(p) == 5 for p in parts)


def validate_legacy_license(key: str) -> dict:
    """Validate an old-format license key. Returns legacy-compatible dict."""
    try:
        raw = key.replace("VCF-", "").replace("-", "")
        if len(raw) < 10:
            return {"valid": False}
        raw = raw.replace("X", ".").replace("Y", "/").replace("Z", "+")
        if "." not in raw:
            return {"valid": False}
        parts = raw.split(".", 1)
        payload_b64 = parts[0]
        sig_received = parts[1].lower() if len(parts) > 1 else ""
        if len(payload_b64) % 4:
            payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload_bytes = base64.b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode())
        expected_sig = hmac.new(_LICENSE_SECRET, payload_bytes, hashlib.sha256).hexdigest()[:20]
        if not hmac.compare_digest(sig_received, expected_sig.lower()):
            return {"valid": False}
        customer = payload.get("c", "")
        expiry = payload.get("e", "")
        max_profiles = payload.get("m", 0)
        expired = False
        grace = False
        if expiry:
            try:
                exp_dt = datetime.fromisoformat(expiry)
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                days_past = (datetime.now(timezone.utc) - exp_dt).days
                if days_past > 0:
                    expired = True
                    grace = days_past <= LICENSE_GRACE_DAYS
            except Exception as e:
                logging.debug("Suppressed: %s", e)
        return {
            "valid": True,
            "customer": customer,
            "expires": expiry,
            "max_profiles": max_profiles,
            "expired": expired,
            "grace": grace,
        }
    except Exception as e:
        return {"valid": False}


def migrate_legacy_license(key: str) -> dict:
    """Migrate a legacy key into partner license format info (without re-keying).

    Returns partner-compatible info dict with tier=starter.
    """
    info = validate_legacy_license(key)
    if not info.get("valid"):
        return info
    return {
        "valid": True,
        "partner_name": info.get("customer", ""),
        "partner_id": "",
        "tier": "standard",
        "max_environments": info.get("max_profiles", 5) or 5,
        "max_clients": 3,
        "features": [],
        "expires": info.get("expires", ""),
        "issued": "",
        "expired": info.get("expired", False),
        "grace": info.get("grace", False),
        "days_remaining": 0,
        "legacy": True,
    }


# ============================================================================
#  ADMIN BACKDOOR AUTHENTICATION
# ============================================================================

def verify_admin_backdoor(password: str) -> bool:
    """Verify admin backdoor password for unlicensed access."""
    if not _ADMIN_BACKDOOR_HASH:
        return False
    return hmac.compare_digest(
        hashlib.sha256(password.encode()).hexdigest(),
        _ADMIN_BACKDOOR_HASH
    )


# ============================================================================
#  MAIN LICENSE CHECK (replaces _check_license in main app)
# ============================================================================

def check_partner_license(script_dir: str, settings: dict) -> dict:
    """Check partner license status. Returns comprehensive license info.

    Modes:
      - "licensed"   : Valid partner license active
      - "grace"      : License expired but within grace period
      - "legacy"     : Old-format key detected, treated as starter
      - "admin_bypass": Admin user authenticated via backdoor
      - "unlicensed" : No valid license — app should block usage
    """
    # Check for admin bypass flag in settings
    if settings.get("_admin_bypass"):
        return {
            "valid": True,
            "mode": "admin_bypass",
            "partner_name": "Admin Bypass",
            "partner_id": "admin",
            "tier": "enterprise",
            "max_environments": 999,
            "max_clients": 0,
            "features": ["branding", "scheduling", "api_export", "white_label"],
        }

    # Check for stored partner license
    licenses_data = _load_licenses(script_dir)
    partner_lic = licenses_data.get("partner_license")
    if partner_lic and partner_lic.get("license_key"):
        key = partner_lic["license_key"]
        # Try partner format first
        info = validate_partner_license(key)
        if info.get("valid"):
            # Update last_validated
            licenses_data["last_validated"] = datetime.now(timezone.utc).isoformat()
            _save_licenses(script_dir, licenses_data)

            if info.get("expired"):
                if info.get("grace"):
                    return {**info, "mode": "grace"}
                return {"valid": False, "mode": "unlicensed", "reason": "expired"}
            return {**info, "mode": "licensed"}

    # Check legacy key in settings
    key = settings.get("license_key", "")
    if key:
        if is_legacy_license(key):
            info = migrate_legacy_license(key)
            if info.get("valid"):
                if info.get("expired"):
                    if info.get("grace"):
                        return {**info, "mode": "grace"}
                    return {"valid": False, "mode": "unlicensed", "reason": "expired"}
                return {**info, "mode": "legacy"}
        else:
            # Try as partner key from settings
            info = validate_partner_license(key)
            if info.get("valid"):
                if info.get("expired"):
                    if info.get("grace"):
                        return {**info, "mode": "grace"}
                    return {"valid": False, "mode": "unlicensed", "reason": "expired"}
                return {**info, "mode": "licensed"}

    return {"valid": False, "mode": "unlicensed", "reason": "no_license"}


def activate_partner_license(script_dir: str, key: str) -> dict:
    """Activate a partner license key. Saves to licenses file.

    Returns: {success, info_or_error}
    """
    # Try partner format
    info = validate_partner_license(key)
    if not info.get("valid"):
        # Try legacy
        if is_legacy_license(key):
            info = migrate_legacy_license(key)

    if not info.get("valid"):
        return {"success": False, "error": "Invalid license key."}

    if info.get("expired") and not info.get("grace"):
        return {"success": False, "error": f"License has expired ({info.get('expires', 'N/A')})."}

    # Save to licenses file
    licenses_data = _load_licenses(script_dir)
    licenses_data["partner_license"] = {
        "license_key": key,
        "partner_name": info.get("partner_name", ""),
        "partner_id": info.get("partner_id", ""),
        "tier": info.get("tier", "standard"),
        "max_environments": info.get("max_environments", 5),
        "max_clients": info.get("max_clients", 3),
        "features": info.get("features", []),
        "issued_date": info.get("issued", ""),
        "expiry_date": info.get("expires", ""),
    }
    licenses_data["activation_date"] = datetime.now(timezone.utc).isoformat()
    licenses_data["last_validated"] = datetime.now(timezone.utc).isoformat()
    _save_licenses(script_dir, licenses_data)

    return {"success": True, "info": info}


# ============================================================================
#  TIER ENFORCEMENT
# ============================================================================

def can_add_environment(script_dir: str, settings: dict, current_count: int) -> Tuple[bool, str]:
    """Check if adding a new environment/profile is allowed by the license tier."""
    lic = check_partner_license(script_dir, settings)
    mode = lic.get("mode", "unlicensed")

    if mode == "unlicensed":
        return False, "A valid license is required. Activate a license key in Settings."

    max_env = lic.get("max_environments", 0)
    if max_env == 0:  # unlimited
        return True, ""

    if current_count >= max_env:
        tier = lic.get("tier", "standard")
        return False, (
            f"Your {TIER_DEFINITIONS.get(tier, {}).get('label', tier)} license allows "
            f"{max_env} environment(s). Upgrade your tier for more."
        )

    return True, ""


def can_add_client(script_dir: str, settings: dict, current_count: int) -> Tuple[bool, str]:
    """Check if adding a new client is allowed by the license tier."""
    lic = check_partner_license(script_dir, settings)
    mode = lic.get("mode", "unlicensed")

    if mode == "unlicensed":
        return False, "A valid license is required."

    max_cl = lic.get("max_clients", 0)
    if max_cl == 0:  # unlimited
        return True, ""

    if current_count >= max_cl:
        tier = lic.get("tier", "standard")
        return False, (
            f"Your {TIER_DEFINITIONS.get(tier, {}).get('label', tier)} license allows "
            f"{max_cl} client(s). Upgrade your tier for more."
        )

    return True, ""


def has_feature(script_dir: str, settings: dict, feature: str) -> bool:
    """Check if a feature is available in the current license tier."""
    lic = check_partner_license(script_dir, settings)
    return feature in lic.get("features", [])


# ============================================================================
#  TKINTER UI BUILDERS
# ============================================================================

def build_license_settings_card(parent: tk.Frame, settings: dict, script_dir: str,
                                colors: dict, activate_callback, admin_bypass_callback) -> tk.Frame:
    """Build the license settings card for the Settings view.

    Returns the card frame so the caller can manage layout.
    """
    card_bg = colors.get("CARD_BG", "#FFFFFF")
    text_p = colors.get("TEXT_PRIMARY", "#1C2833")
    text_s = colors.get("TEXT_SECONDARY", "#566573")
    brand = colors.get("BRAND_BLUE", "#0077B6")
    success = colors.get("SUCCESS", "#27AE60")
    warning = colors.get("WARNING", "#F39C12")
    error = colors.get("ERROR", "#E74C3C")

    card = tk.Frame(parent, bg=card_bg, bd=1, relief="solid")
    card.pack(fill="x", padx=20, pady=8)

    tk.Label(card, text="Partner License", bg=card_bg, fg=text_p,
             font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 5))

    # Current status
    lic = check_partner_license(script_dir, settings)
    mode = lic.get("mode", "unlicensed")

    if mode == "licensed":
        tier_label = TIER_DEFINITIONS.get(lic.get("tier", ""), {}).get("label", lic.get("tier", ""))
        status_text = (f"Licensed to: {lic.get('partner_name', 'N/A')} — "
                       f"{tier_label} tier — expires {lic.get('expires', 'N/A')}")
        status_color = success
    elif mode == "legacy":
        status_text = f"Legacy license: {lic.get('partner_name', 'N/A')} (Standard tier)"
        status_color = warning
    elif mode == "grace":
        status_text = f"License expired (grace period) — {lic.get('partner_name', 'N/A')}"
        status_color = warning
    elif mode == "admin_bypass":
        status_text = "Admin Bypass — Full access granted"
        status_color = success
    else:
        status_text = "No License — A valid license is required to use this application"
        status_color = error

    tk.Label(card, text=f"Status: {status_text}", bg=card_bg, fg=status_color,
             font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=15, pady=(0, 5))

    # Tier badge and details (if licensed)
    if mode in ("licensed", "legacy", "grace"):
        detail_frame = tk.Frame(card, bg=card_bg)
        detail_frame.pack(fill="x", padx=15, pady=(0, 5))

        tier = lic.get("tier", "standard")
        tier_color = TIER_COLORS.get(tier, "#3498DB")
        tk.Label(detail_frame, text=f" {TIER_DEFINITIONS.get(tier, {}).get('label', tier).upper()} ",
                 bg=tier_color, fg="white", font=("Segoe UI", 9, "bold"),
                 padx=6, pady=1).pack(side="left")

        max_env = lic.get("max_environments", 0)
        max_cl = lic.get("max_clients", 0)
        env_txt = str(max_env) if max_env > 0 else "Unlimited"
        cl_txt = str(max_cl) if max_cl > 0 else "Unlimited"
        tk.Label(detail_frame, text=f"  Environments: {env_txt}  |  Clients: {cl_txt}",
                 bg=card_bg, fg=text_s, font=("Segoe UI", 9)).pack(side="left", padx=5)

        features = lic.get("features", [])
        if features:
            tk.Label(card, text=f"Features: {', '.join(features)}",
                     bg=card_bg, fg=text_s, font=("Segoe UI", 9)).pack(anchor="w", padx=15, pady=(0, 5))

    # License key entry
    lk_row = tk.Frame(card, bg=card_bg)
    lk_row.pack(fill="x", padx=15, pady=(3, 5))
    tk.Label(lk_row, text="License Key:", bg=card_bg, fg=text_p,
             font=("Segoe UI", 10), anchor="w").pack(side="left")
    key_var = tk.StringVar(value="")
    tk.Entry(lk_row, textvariable=key_var, font=("Consolas", 10),
             bd=1, relief="solid", width=45).pack(side="left", padx=(5, 0))
    tk.Button(lk_row, text="Activate", command=lambda: activate_callback(key_var.get().strip()),
              bg=brand, fg="white", font=("Segoe UI", 9, "bold"),
              relief="flat", padx=10, cursor="hand2").pack(side="left", padx=(5, 0))

    tk.Label(card, text="Format: VCF-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX (or legacy 4-group)",
             bg=card_bg, fg=text_s, font=("Segoe UI", 8)).pack(anchor="w", padx=15, pady=(0, 5))

    # Admin bypass button (only show if unlicensed)
    if mode == "unlicensed":
        sep = tk.Frame(card, bg=colors.get("BORDER", "#D5D8DC"), height=1)
        sep.pack(fill="x", padx=15, pady=5)
        bypass_row = tk.Frame(card, bg=card_bg)
        bypass_row.pack(fill="x", padx=15, pady=(0, 10))
        tk.Label(bypass_row, text="Admin Bypass:", bg=card_bg, fg=text_s,
                 font=("Segoe UI", 9)).pack(side="left")
        pw_var = tk.StringVar()
        tk.Entry(bypass_row, textvariable=pw_var, font=("Consolas", 10),
                 bd=1, relief="solid", width=20, show="*").pack(side="left", padx=(5, 0))
        tk.Button(bypass_row, text="Unlock", command=lambda: admin_bypass_callback(pw_var.get()),
                  bg="#566573", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, cursor="hand2").pack(side="left", padx=(5, 0))

    return card


def build_license_dashboard(parent: tk.Frame, script_dir: str, settings: dict,
                            colors: dict) -> tk.Frame:
    """Build a license dashboard widget with tier badge, usage bars, expiry countdown."""
    card_bg = colors.get("CARD_BG", "#FFFFFF")
    text_p = colors.get("TEXT_PRIMARY", "#1C2833")
    text_s = colors.get("TEXT_SECONDARY", "#566573")
    success = colors.get("SUCCESS", "#27AE60")
    warning = colors.get("WARNING", "#F39C12")
    error = colors.get("ERROR", "#E74C3C")

    frame = tk.Frame(parent, bg=card_bg, bd=1, relief="solid")

    lic = check_partner_license(script_dir, settings)
    mode = lic.get("mode", "unlicensed")

    # Header with tier badge
    header = tk.Frame(frame, bg=card_bg)
    header.pack(fill="x", padx=15, pady=(10, 5))

    tier = lic.get("tier", "starter")
    tier_color = TIER_COLORS.get(tier, "#3498DB")
    tier_label = TIER_DEFINITIONS.get(tier, {}).get("label", tier)

    if mode in ("licensed", "legacy", "grace", "admin_bypass"):
        tk.Label(header, text=f" {tier_label.upper()} ",
                 bg=tier_color, fg="white", font=("Segoe UI", 10, "bold"),
                 padx=8, pady=2).pack(side="left")
        tk.Label(header, text=f"  {lic.get('partner_name', '')}",
                 bg=card_bg, fg=text_p, font=("Segoe UI", 11, "bold")).pack(side="left")

        # Expiry countdown
        days = lic.get("days_remaining", 0)
        if mode == "grace":
            exp_text = "EXPIRED — Grace period active"
            exp_color = warning
        elif days > 0 and days <= 30:
            exp_text = f"{days} days remaining"
            exp_color = warning
        elif days > 30:
            exp_text = f"Expires {lic.get('expires', 'N/A')}"
            exp_color = success
        else:
            exp_text = f"Expires {lic.get('expires', 'N/A')}"
            exp_color = text_s

        tk.Label(frame, text=exp_text, bg=card_bg, fg=exp_color,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=15, pady=(0, 5))
    else:
        tk.Label(header, text="NO LICENSE", bg=error, fg="white",
                 font=("Segoe UI", 10, "bold"), padx=8, pady=2).pack(side="left")

    return frame
