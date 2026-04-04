#!/usr/bin/env python3
"""
VCF Health Check GUI — Standalone Tkinter application for running
vcf-health-check.sh with a graphical interface.

Provides environment profile management, live terminal output,
historical report browsing, and a dashboard with grade/score display.

Copyright (c) 2026 Virtual Control LLC. All rights reserved.
"""

import base64
import copy
import glob
import hashlib
import hmac
import json
import logging
import math
import os
import platform
import queue
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("vcf-health-check-gui")
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.FileHandler("vcf-gui.log", encoding="utf-8"),
                              logging.NullHandler()])

# ── Optional partner ecosystem modules ──────────────────────────────────────
try:
    import vcf_license_manager as license_mgr
    _HAS_LICENSE_MGR = True
except ImportError:
    _HAS_LICENSE_MGR = False

try:
    import vcf_client_manager as client_mgr
    _HAS_CLIENT_MGR = True
except ImportError:
    _HAS_CLIENT_MGR = False

try:
    import vcf_usage_tracker as usage_tracker
    _HAS_USAGE_TRACKER = True
except ImportError:
    _HAS_USAGE_TRACKER = False

# ============================================================================
#  CONSTANTS & COLOR SCHEMES
# ============================================================================

APP_TITLE = "VCF Health Check"
APP_VERSION = "8.0"
APP_COPYRIGHT = "Copyright \u00a9 2026 Virtual Control LLC"
INITIAL_SIZE = "1300x800"

# Resolve paths relative to this script / executable
if getattr(sys, "frozen", False):
    # PyInstaller --onefile: sys.executable is the .exe path
    _SCRIPT_DIR = Path(os.path.abspath(os.path.dirname(sys.executable)))
else:
    _SCRIPT_DIR = Path(__file__).parent.resolve()

# Debug log for troubleshooting path issues in frozen builds
_DEBUG_LOG = os.path.join(str(_SCRIPT_DIR), ".vcf-gui-debug.log")
try:
    with open(_DEBUG_LOG, "w", encoding="utf-8") as _f:
        _f.write(f"frozen: {getattr(sys, 'frozen', False)}\n")
        _f.write(f"sys.executable: {sys.executable}\n")
        _f.write(f"_SCRIPT_DIR: {_SCRIPT_DIR}\n")
        _f.write(f"cwd: {os.getcwd()}\n")
        _sh = os.path.join(str(_SCRIPT_DIR), "vcf-health-check.sh")
        _f.write(f"script candidate: {_sh}\n")
        _f.write(f"script exists: {os.path.isfile(_sh)}\n")
        _f.write(f"dir listing: {os.listdir(str(_SCRIPT_DIR))[:20]}\n")
except Exception as e:  # noqa: E722
    logger.debug("Suppressed: %s", e)

PROFILES_FILE = str(_SCRIPT_DIR / "vcf-health-profiles.json")
PROFILES_VERSION = "1.0"
USERS_FILE = str(_SCRIPT_DIR / "vcf-health-users.json")
AUDIT_LOG_FILE = str(_SCRIPT_DIR / "vcf-health-audit.log")

# License key constants — imported from license manager, with fallback
try:
    from vcf_license_manager import _LICENSE_SECRET
except ImportError:
    _LICENSE_SECRET = os.urandom(32)
LICENSE_TRIAL_MAX_PROFILES = 1
LICENSE_GRACE_DAYS = 14

# Light mode colors (defaults)
BRAND_BLUE = "#0077B6"
SIDEBAR_BG = "#0A1F33"
SIDEBAR_TEXT = "#EAF2F8"
CONTENT_BG = "#F4F6F6"
CARD_BG = "#FFFFFF"
HEADER_BG = "#D6EAF8"

LIGHT_COLORS = {
    "BRAND_BLUE": "#0077B6",
    "SIDEBAR_BG": "#0A1F33",
    "SIDEBAR_TEXT": "#EAF2F8",
    "CONTENT_BG": "#F4F6F6",
    "CARD_BG": "#FFFFFF",
    "HEADER_BG": "#D6EAF8",
    "TEXT_PRIMARY": "#1C2833",
    "TEXT_SECONDARY": "#566573",
    "SUCCESS": "#27AE60",
    "ERROR": "#E74C3C",
    "WARNING": "#F39C12",
    "TERMINAL_BG": "#1E1E1E",
    "TERMINAL_FG": "#D4D4D4",
    "BORDER": "#D5D8DC",
}

DARK_COLORS = {
    "BRAND_BLUE": "#0099E6",
    "SIDEBAR_BG": "#1A1A2E",
    "SIDEBAR_TEXT": "#E0E0E0",
    "CONTENT_BG": "#16213E",
    "CARD_BG": "#1F2833",
    "HEADER_BG": "#0F3460",
    "TEXT_PRIMARY": "#E0E0E0",
    "TEXT_SECONDARY": "#A0A0A0",
    "SUCCESS": "#2ECC71",
    "ERROR": "#E74C3C",
    "WARNING": "#F39C12",
    "TERMINAL_BG": "#0D1117",
    "TERMINAL_FG": "#C9D1D9",
    "BORDER": "#30363D",
}

# Grade color mapping
GRADE_COLORS = {
    "A": "#27AE60",
    "B+": "#2ECC71",
    "B": "#F1C40F",
    "C": "#F39C12",
    "D": "#E67E22",
    "F": "#E74C3C",
}

# ============================================================================
#  FIELD DEFINITIONS — drives the Environment form
# ============================================================================

# Each section: (section_key, section_label, expanded_by_default, fields)
# Each field: (env_var_name, label, field_type, default_value)
# field_type: "text", "password", "int", "textarea", "checkbox", "file"

FIELD_SECTIONS = [
    (
        "endpoints",
        "Management Endpoints",
        True,
        [
            ("VCENTER", "vCenter FQDN / IP", "text", ""),
            ("SDDC", "SDDC Manager FQDN / IP", "text", ""),
            ("NSX_VIP", "NSX VIP FQDN / IP", "text", ""),
            ("NSX_NODE", "NSX Node IP", "text", ""),
            ("VCF_OPS", "VCF Operations IP", "text", ""),
            ("FLEET", "Fleet Manager IP", "text", ""),
        ],
    ),
    (
        "credentials",
        "Credentials",
        False,
        [
            ("SSO_USER", "SSO Username", "text", "administrator@vsphere.local"),
            ("SSO_PASS", "SSO Password", "password", ""),
            ("NSX_USER", "NSX Username", "text", "admin"),
            ("NSX_PASS", "NSX Password", "password", ""),
            ("OPS_USER", "Operations Username", "text", "admin"),
            ("OPS_PASS", "Operations Password", "password", ""),
            ("FLEET_USER", "Fleet Username", "text", "admin@local"),
            ("FLEET_PASS", "Fleet Password", "password", ""),
            ("ESXI_USER", "ESXi Username", "text", "root"),
            ("ESXI_PASS", "ESXi Password", "password", ""),
        ],
    ),
    (
        "esxi_hosts",
        "ESXi Hosts",
        False,
        [
            ("ESXI_HOSTS", "Host IPs (space-separated)", "textarea", ""),
        ],
    ),
    (
        "timeouts",
        "Timeouts (seconds)",
        False,
        [
            ("CURL_CONNECT_TIMEOUT", "Connect Timeout", "int", "15"),
            ("CURL_MAX_TIME", "Max Request Time", "int", "30"),
            ("TIMEOUT_INFRA", "Infra Timeout", "int", "30"),
            ("TIMEOUT_VCENTER", "vCenter Timeout", "int", "30"),
            ("TIMEOUT_SDDC", "SDDC Timeout", "int", "45"),
            ("TIMEOUT_NSX", "NSX Timeout", "int", "30"),
            ("TIMEOUT_OPS", "Operations Timeout", "int", "30"),
            ("TIMEOUT_FLEET", "Fleet Timeout", "int", "30"),
        ],
    ),
    (
        "thresholds",
        "Thresholds",
        False,
        [
            ("CERT_WARN_DAYS", "Certificate Warning (days)", "int", "30"),
            ("DATASTORE_WARN_PCT", "Datastore Warning (%)", "int", "80"),
            ("DATASTORE_CRIT_PCT", "Datastore Critical (%)", "int", "90"),
            ("TASK_WARN_THRESHOLD", "Stale Task Threshold", "int", "5"),
            ("SNAPSHOT_WARN_HOURS", "Snapshot Warning (hours)", "int", "72"),
            ("BACKUP_WARN_HOURS", "Backup Warning (hours)", "int", "48"),
            ("DFW_RULE_WARN", "DFW Rule Warning Count", "int", "500"),
            ("CLUSTER_CPU_WARN_PCT", "Cluster CPU Warning (%)", "int", "70"),
            ("CLUSTER_CPU_CRIT_PCT", "Cluster CPU Critical (%)", "int", "85"),
            ("CLUSTER_MEM_WARN_PCT", "Cluster Memory Warning (%)", "int", "70"),
            ("CLUSTER_MEM_CRIT_PCT", "Cluster Memory Critical (%)", "int", "85"),
        ],
    ),
    (
        "notifications",
        "Notifications",
        False,
        [
            ("SMTP_TO", "SMTP To", "text", ""),
            ("SMTP_FROM", "SMTP From", "text", ""),
            ("SMTP_SERVER", "SMTP Server", "text", ""),
            ("SMTP_PORT", "SMTP Port", "int", "25"),
            ("SLACK_WEBHOOK", "Slack Webhook URL", "text", ""),
            ("TEAMS_WEBHOOK", "Teams Webhook URL", "text", ""),
            ("WEBHOOK_URL", "Generic Webhook URL", "text", ""),
            ("NOTIFY_THRESHOLD", "Notify Threshold (A/B/C/D/F)", "text", "C"),
        ],
    ),
    (
        "incident_mgmt",
        "Incident Management",
        False,
        [
            ("PAGERDUTY_KEY", "PagerDuty Routing Key", "password", ""),
            ("OPSGENIE_KEY", "OpsGenie API Key", "password", ""),
        ],
    ),
    (
        "weights",
        "Scoring Weights",
        False,
        [
            ("WEIGHT_INFRA", "Infrastructure", "int", "1"),
            ("WEIGHT_VCENTER", "vCenter", "int", "2"),
            ("WEIGHT_SDDC", "SDDC Manager", "int", "2"),
            ("WEIGHT_NSX", "NSX", "int", "2"),
            ("WEIGHT_OPS", "Operations", "int", "1"),
            ("WEIGHT_FLEET", "Fleet", "int", "1"),
        ],
    ),
    (
        "branding",
        "Customer Branding",
        False,
        [
            ("CUSTOMER_NAME", "Company Name", "text", ""),
            ("CUSTOMER_LOGO", "Company Logo", "file", ""),
            ("CUSTOMER_CONTACT", "Contact Email", "text", ""),
            ("CUSTOMER_ENV_LABEL", "Environment Label", "text", "VCF 9.0 Lab Environment"),
        ],
    ),
    (
        "other",
        "Other Settings",
        False,
        [
            ("PLUGIN_DIR", "Plugin Directory", "text", ""),
            ("EXPECTED_DOWN", "Expected Down (comma-sep)", "text", ""),
            ("REPORT_RETENTION_DAYS", "Report Retention (days)", "int", "30"),
            ("SSL_VERIFY", "Enable SSL Verification", "text", "false"),
            ("CA_BUNDLE", "CA Bundle Path", "text", ""),
        ],
    ),
]

# Run option flags
RUN_OPTIONS = [
    ("fix", "--fix", "Auto-remediate safe issues"),
    ("cleanup_tasks", "--cleanup-tasks", "Auto-cancel stale SDDC tasks"),
    ("diff", "--diff", "Only show changed checks since last run"),
    ("csv", "--csv", "Also generate CSV report"),
    ("markdown", "--markdown", "Also generate Markdown report"),
    ("quiet", "--quiet", "Suppress terminal output"),
    ("json_only", "--json-only", "Output JSON report only"),
]

# ── Field validation rules ────────────────────────────────────────────────
FIELD_VALIDATION = {
    "VCENTER": "ip_or_fqdn", "SDDC": "ip_or_fqdn", "NSX_VIP": "ip_or_fqdn",
    "NSX_NODE": "ip_or_fqdn", "VCF_OPS": "ip_or_fqdn", "FLEET": "ip_or_fqdn",
    "SMTP_TO": "email", "SMTP_FROM": "email", "CUSTOMER_CONTACT": "email",
    "SMTP_PORT": "port",
    "SLACK_WEBHOOK": "url", "TEAMS_WEBHOOK": "url", "WEBHOOK_URL": "url",
}

_IP_RE = re.compile(
    r'^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$'
)
_FQDN_RE = re.compile(
    r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$'
)
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$')
_URL_RE = re.compile(r'^https?://\S+$')


def _validate_ip_or_fqdn(value: str) -> str:
    """Return error message or empty string."""
    if not value:
        return ""
    if _IP_RE.match(value) or _FQDN_RE.match(value):
        return ""
    return f"'{value}' is not a valid IP address or FQDN"


def _validate_email(value: str) -> str:
    if not value:
        return ""
    if _EMAIL_RE.match(value):
        return ""
    return f"'{value}' is not a valid email address"


def _validate_url(value: str) -> str:
    if not value:
        return ""
    if _URL_RE.match(value):
        return ""
    return f"'{value}' is not a valid URL (must start with http:// or https://)"


def _validate_port(value: str) -> str:
    if not value:
        return ""
    try:
        p = int(value)
        if 1 <= p <= 65535:
            return ""
        return f"Port {value} out of range (1-65535)"
    except ValueError:
        return f"'{value}' is not a valid port number"


def validate_field(var_name: str, value: str) -> str:
    """Validate a single field. Returns error message or empty string."""
    vtype = FIELD_VALIDATION.get(var_name)
    if not vtype:
        return ""
    validators = {
        "ip_or_fqdn": _validate_ip_or_fqdn,
        "email": _validate_email,
        "url": _validate_url,
        "port": _validate_port,
    }
    fn = validators.get(vtype)
    return fn(value) if fn else ""


# ── Field tooltips ────────────────────────────────────────────────────────
FIELD_TOOLTIPS = {
    "VCENTER": "FQDN or IP of the vCenter Server (e.g. vcsa.lab.local)",
    "SDDC": "FQDN or IP of the SDDC Manager appliance",
    "NSX_VIP": "NSX Manager VIP (cluster virtual IP)",
    "NSX_NODE": "IP of a specific NSX Manager node for direct API calls",
    "VCF_OPS": "IP of VCF Operations (Aria/vROps) appliance",
    "FLEET": "IP of Fleet Manager appliance",
    "SSO_USER": "vCenter SSO admin user (usually administrator@vsphere.local)",
    "SSO_PASS": "Password for the SSO admin user",
    "NSX_USER": "NSX Manager admin username (usually admin)",
    "NSX_PASS": "Password for NSX Manager admin user",
    "ESXI_HOSTS": "Space-separated list of ESXi host IPs to check",
    "CURL_CONNECT_TIMEOUT": "Seconds to wait for TCP connection to establish",
    "CURL_MAX_TIME": "Maximum seconds for an entire API request",
    "CERT_WARN_DAYS": "Warn when certificates expire within this many days",
    "DATASTORE_WARN_PCT": "Warn when datastore usage exceeds this percentage",
    "DATASTORE_CRIT_PCT": "Critical alert when datastore usage exceeds this %",
    "CLUSTER_CPU_WARN_PCT": "Warn when cluster CPU usage exceeds this percentage",
    "CLUSTER_CPU_CRIT_PCT": "Critical alert when cluster CPU usage exceeds this %",
    "CLUSTER_MEM_WARN_PCT": "Warn when cluster memory usage exceeds this percentage",
    "CLUSTER_MEM_CRIT_PCT": "Critical alert when cluster memory usage exceeds this %",
    "SMTP_TO": "Email address to send health check notifications to",
    "SMTP_FROM": "Sender email address for notification emails",
    "SMTP_SERVER": "SMTP server hostname or IP",
    "SMTP_PORT": "SMTP server port (25, 465, 587)",
    "SLACK_WEBHOOK": "Slack incoming webhook URL for notifications",
    "TEAMS_WEBHOOK": "Microsoft Teams webhook URL for notifications",
    "WEBHOOK_URL": "Generic webhook URL (receives JSON POST)",
    "NOTIFY_THRESHOLD": "Only notify when grade is at or below this (A/B/C/D/F)",
    "REPORT_RETENTION_DAYS": "Auto-delete reports older than this many days (0=keep all)",
    "CUSTOMER_NAME": "Company name shown on reports",
    "CUSTOMER_CONTACT": "Contact email shown on reports",
    "SSL_VERIFY": "Set to 'true' to enforce SSL certificate verification",
}


class _ToolTip:
    """Lightweight tooltip popup for form fields."""

    def __init__(self, widget, text: str):
        self._widget = widget
        self._text = text
        self._tip_window = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, event=None):
        if self._tip_window:
            return
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 2
        tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(tw, text=self._text, justify="left",
                       background="#FFFDE7", foreground="#333",
                       relief="solid", borderwidth=1,
                       font=("Segoe UI", 9), padx=8, pady=4,
                       wraplength=320)
        lbl.pack()
        self._tip_window = tw

    def _hide(self, event=None):
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None


# Component display info for dashboard
COMPONENTS = [
    ("infra", "Infrastructure", "Hosts, network, storage"),
    ("vcenter", "vCenter", "APIs, services, certificates"),
    ("sddc", "SDDC Manager", "Health, tasks, lifecycle"),
    ("nsx", "NSX", "Managers, controllers, transport"),
    ("ops", "Operations", "Management cluster, services"),
    ("fleet", "Fleet", "vSphere automation, plugins"),
]


# ============================================================================
#  PROFILE PERSISTENCE (JSON, encrypted passwords)
# ============================================================================

_KEY_FILE = Path.home() / ".vcf-hc-key"


def _get_or_create_key() -> bytes:
    """Get or create a machine-local encryption key."""
    if _KEY_FILE.exists():
        return _KEY_FILE.read_bytes()
    from cryptography.fernet import Fernet  # required — no insecure fallback
    key = Fernet.generate_key()
    _KEY_FILE.write_bytes(key)
    try:
        os.chmod(str(_KEY_FILE), 0o600)
    except OSError:
        pass  # Windows may not support Unix permissions
    return key


def _b64_encode(plaintext: str) -> str:
    """Encrypt a plaintext string for profile storage.

    Requires the 'cryptography' package. Install with: pip install cryptography
    """
    if not plaintext:
        return ""
    from cryptography.fernet import Fernet  # required — no insecure fallback
    key = _get_or_create_key()
    token = Fernet(key).encrypt(plaintext.encode("utf-8"))
    return "enc:" + token.decode("ascii")


def _b64_decode(stored: str) -> str:
    """Decrypt a stored credential string.

    Raises RuntimeError if an encrypted credential cannot be decrypted
    (e.g. corrupted key file) rather than silently returning ciphertext.
    """
    if not stored:
        return ""
    if stored.startswith("enc:"):
        try:
            from cryptography.fernet import Fernet
            key = _get_or_create_key()
            return Fernet(key).decrypt(stored[4:].encode("ascii")).decode("utf-8")
        except Exception as e:
            logger.error("SECURITY: Decryption failed — possible key corruption: %s", e)
            raise RuntimeError(
                "Cannot decrypt stored credential. The encryption key may be "
                "corrupted or missing. Re-enter credentials in Settings."
            ) from e
    if stored.startswith("b64:"):
        # Legacy base64 read support — decode but warn so it gets re-encrypted on next save
        logger.warning("Reading insecure base64-encoded credential — will re-encrypt on next save")
        try:
            return base64.b64decode(stored[4:]).decode("utf-8")
        except Exception as e:
            logger.error("Legacy base64 decode failed: %s", e)
            raise RuntimeError(
                "Cannot decode legacy credential. Re-enter credentials in Settings."
            ) from e
    return stored


def _password_fields() -> set:
    """Return set of env var names that are password fields."""
    pw = set()
    for _key, _label, _expanded, fields in FIELD_SECTIONS:
        for var, _lbl, ftype, _default in fields:
            if ftype == "password":
                pw.add(var)
    return pw


PASSWORD_FIELDS = _password_fields()


def load_profiles() -> dict:
    """Load profiles from JSON file."""
    if not os.path.exists(PROFILES_FILE):
        return {
            "_version": PROFILES_VERSION,
            "active_profile": "",
            "profiles": {},
        }
    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {"_version": PROFILES_VERSION, "active_profile": "", "profiles": {}}
        data.setdefault("_version", PROFILES_VERSION)
        data.setdefault("active_profile", "")
        data.setdefault("profiles", {})
        return data
    except Exception as e:  # noqa: E722
        return {"_version": PROFILES_VERSION, "active_profile": "", "profiles": {}}


def save_profiles(data: dict):
    """Save profiles to JSON file."""
    data["_version"] = PROFILES_VERSION
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def profile_to_form(profile: dict) -> dict:
    """Convert stored profile dict to flat {env_var: value} with passwords decoded."""
    flat = {}
    for section_key, _label, _expanded, fields in FIELD_SECTIONS:
        section_data = profile.get(section_key, {})
        for var, _lbl, ftype, default in fields:
            raw = section_data.get(var, default)
            if ftype == "password":
                try:
                    raw = _b64_decode(raw)
                except RuntimeError:
                    logger.warning("Could not decrypt %s — clearing value", var)
                    raw = ""
            flat[var] = raw
    flat["run_options"] = profile.get("run_options", {})
    return flat


def form_to_profile(name: str, flat: dict, run_options: dict) -> dict:
    """Convert flat form values to profile storage dict with passwords encoded."""
    profile = {"name": name}
    for section_key, _label, _expanded, fields in FIELD_SECTIONS:
        section = {}
        for var, _lbl, ftype, _default in fields:
            val = flat.get(var, "")
            if ftype == "password":
                val = _b64_encode(val)
            section[var] = val
        profile[section_key] = section
    profile["run_options"] = dict(run_options)
    return profile


def parse_env_file(filepath: str) -> dict:
    """Parse a .env (bash) file into {VAR: value} dict."""
    result = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                m = re.match(r'^([A-Z_][A-Z0-9_]*)=(.*)$', line)
                if m:
                    key = m.group(1)
                    val = m.group(2).strip()
                    # Remove surrounding quotes
                    if (val.startswith('"') and val.endswith('"')) or \
                       (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    result[key] = val
    except Exception as e:  # noqa: E722
        logger.debug("Suppressed: %s", e)
    return result


def export_env_file(filepath: str, flat: dict):
    """Write form values to a .env file."""
    lines = [
        "# ============================================================================",
        "#  VCF Health Check — Environment Configuration",
        "#  Generated by VCF Health Check GUI — Virtual Control LLC",
        "# ============================================================================",
        "",
    ]
    for section_key, section_label, _expanded, fields in FIELD_SECTIONS:
        lines.append(f"# --- {section_label} ---")
        for var, _lbl, ftype, _default in fields:
            val = flat.get(var, "")
            if ftype == "textarea":
                lines.append(f'{var}="{val}"')
            elif ftype == "int":
                lines.append(f'{var}={val}')
            else:
                lines.append(f'{var}="{val}"')
        lines.append("")
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    try:
        os.chmod(filepath, 0o600)  # Owner read/write only
    except OSError:
        pass  # Windows may not support Unix permissions


# ============================================================================
#  BASH / SCRIPT DETECTION
# ============================================================================


def find_bash() -> Optional[str]:
    """Find a usable bash binary (Git Bash, WSL, PATH)."""
    candidates = [
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Git\bin\bash.exe"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    # WSL
    wsl = shutil.which("wsl")
    if wsl:
        return wsl
    # Generic PATH
    bash = shutil.which("bash")
    if bash:
        return bash
    return None


def find_script() -> Optional[str]:
    """Find vcf-health-check.sh in the app directory, parent, or CWD."""
    search_dirs = [
        _SCRIPT_DIR,
        _SCRIPT_DIR.parent,
        Path.cwd(),
    ]
    # Also try the directory of sys.executable directly (belt + suspenders)
    if getattr(sys, "frozen", False):
        search_dirs.insert(0, Path(os.path.dirname(sys.executable)))
    for d in search_dirs:
        candidate = os.path.join(str(d), "vcf-health-check.sh")
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)
    return None


# ============================================================================
#  JSON REPORT PARSING
# ============================================================================


def _normalize_components(raw_components) -> dict:
    """Normalize components from array or dict format into a consistent dict.

    The script outputs components as an array of objects:
      [{"name": "Infrastructure", "pass": 12, "warn": 1, "fail": 0, "status": "PASS"}, ...]

    We normalize to:
      {"infra": {"passed": 12, "warnings": 1, "failed": 0, "status": "PASS"}, ...}
    """
    # Name-to-key mapping
    name_map = {
        "infrastructure": "infra",
        "vcenter server": "vcenter",
        "vcenter": "vcenter",
        "sddc manager": "sddc",
        "nsx manager": "nsx",
        "nsx": "nsx",
        "vcf operations": "ops",
        "operations": "ops",
        "fleet (vrslcm)": "fleet",
        "fleet": "fleet",
    }

    if isinstance(raw_components, dict):
        # Already a dict — normalize field names
        result = {}
        for key, val in raw_components.items():
            if isinstance(val, dict):
                result[key] = {
                    "passed": val.get("passed", val.get("pass", 0)),
                    "warnings": val.get("warnings", val.get("warn", 0)),
                    "failed": val.get("failed", val.get("fail", 0)),
                    "status": val.get("status", "N/A"),
                }
            else:
                result[key] = val
        return result

    if isinstance(raw_components, list):
        result = {}
        for item in raw_components:
            if not isinstance(item, dict):
                continue
            name = item.get("name", "").lower().strip()
            comp_key = name_map.get(name, name.replace(" ", "_"))
            result[comp_key] = {
                "passed": item.get("passed", item.get("pass", 0)),
                "warnings": item.get("warnings", item.get("warn", 0)),
                "failed": item.get("failed", item.get("fail", 0)),
                "status": item.get("status", "N/A"),
            }
        return result

    return {}


def _normalize_trend(data: dict) -> list:
    """Extract trend data from report JSON.

    The script stores trend as an array:
      [{"date": "2026-03-16 18:02", "grade": "D", "score": "46%"}, ...]

    We normalize to: [{"date": datetime, "score": int, "grade": str}, ...]
    """
    raw = data.get("trend", [])
    if not isinstance(raw, list):
        return []
    result = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        score_raw = item.get("score", "0")
        if isinstance(score_raw, str):
            score_raw = score_raw.replace("%", "").strip()
        try:
            score_val = int(float(score_raw))
        except (ValueError, TypeError):
            score_val = 0
        try:
            dt = datetime.strptime(item.get("date", ""), "%Y-%m-%d %H:%M")
        except Exception as e:  # noqa: E722
            dt = None
        result.append({
            "date": dt,
            "score": score_val,
            "grade": item.get("grade", "?"),
        })
    return result


def discover_reports(script_dir: str) -> List[dict]:
    """Find VCF-Health-Report_*.json files and parse metadata."""
    pattern = os.path.join(script_dir, "VCF-Health-Report_*.json")
    files = glob.glob(pattern)
    reports = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            basename = os.path.basename(f)
            # Extract timestamp from filename: VCF-Health-Report_YYYYMMDD_HHMMSS.json
            m = re.search(r'(\d{8}_\d{6})', basename)
            ts_str = m.group(1) if m else ""
            try:
                ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
            except Exception as e:  # noqa: E722
                ts = datetime.fromtimestamp(os.path.getmtime(f))

            stem = os.path.splitext(f)[0]

            # Normalize components (array or dict)
            components = _normalize_components(data.get("components", []))

            # Executive summary — top-level or under metadata
            exec_summary = data.get("executive_summary", "")
            if not exec_summary:
                meta = data.get("metadata", {})
                if isinstance(meta, dict):
                    exec_summary = meta.get("exec_summary", "")

            # Delta / previous grade
            delta = data.get("delta", {})
            if not isinstance(delta, dict):
                delta = {}
            prev_grade = delta.get("prev_grade", "")

            # Trend data
            trend = _normalize_trend(data)

            reports.append({
                "path_json": f,
                "path_txt": stem + ".txt" if os.path.isfile(stem + ".txt") else None,
                "path_html": stem + ".html" if os.path.isfile(stem + ".html") else None,
                "path_csv": stem + ".csv" if os.path.isfile(stem + ".csv") else None,
                "path_md": stem + ".md" if os.path.isfile(stem + ".md") else None,
                "grade": data.get("grade", "?"),
                "score": data.get("score", 0),
                "date": ts,
                "date_str": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "summary": data.get("summary", {}),
                "components": components,
                "exec_summary": exec_summary,
                "prev_grade": prev_grade,
                "trend": trend,
                "data": data,
            })
        except Exception as e:  # noqa: E722
            continue
    reports.sort(key=lambda r: r["date"], reverse=True)
    return reports


# ── Notifications (email / webhook) ──────────────────────────────────────

_GRADE_ORDER = {"A": 0, "B+": 1, "B": 2, "C": 3, "D": 4, "F": 5}


def _should_notify(grade: str, threshold: str) -> bool:
    """Return True if grade is at or below threshold."""
    if not threshold:
        return True
    return _GRADE_ORDER.get(grade, 5) >= _GRADE_ORDER.get(threshold, 5)


def _send_email_notification(flat: dict, grade: str, score, profile_name: str):
    """Send email notification via SMTP (stdlib only)."""
    import smtplib
    from email.mime.text import MIMEText
    to_addr = flat.get("SMTP_TO", "")
    from_addr = flat.get("SMTP_FROM", "") or "vcf-health-check@localhost"
    server = flat.get("SMTP_SERVER", "")
    port = int(flat.get("SMTP_PORT", 25) or 25)
    if not to_addr or not server:
        return
    body = (f"VCF Health Check completed for profile '{profile_name}'.\n\n"
            f"Grade: {grade}\nScore: {score}%\n\nThis is an automated notification.")
    msg = MIMEText(body)
    msg["Subject"] = f"VCF Health Check — {profile_name} — Grade {grade} ({score}%)"
    msg["From"] = from_addr
    msg["To"] = to_addr
    try:
        with smtplib.SMTP(server, port, timeout=30) as srv:
            srv.sendmail(from_addr, [to_addr], msg.as_string())
        _audit_log("system", "NOTIFICATION_EMAIL_SENT", f"to={to_addr}")
    except Exception as e:
        _audit_log("system", "NOTIFICATION_EMAIL_FAILED", str(e))


def _send_webhook_notification(url: str, grade: str, score, profile_name: str, channel: str = "generic"):
    """Send JSON POST to a webhook URL."""
    import urllib.request
    if not url:
        return
    payload = json.dumps({
        "text": f"VCF Health Check — {profile_name} — Grade {grade} ({score}%)",
        "grade": grade, "score": score, "profile": profile_name,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
        _audit_log("system", f"NOTIFICATION_{channel.upper()}_SENT", url)
    except Exception as e:
        _audit_log("system", f"NOTIFICATION_{channel.upper()}_FAILED", str(e))


def send_run_notifications(flat: dict, grade: str, score, profile_name: str):
    """Orchestrator: send all configured notifications if threshold met."""
    threshold = flat.get("NOTIFY_THRESHOLD", "C")
    if not _should_notify(grade, threshold):
        return
    # Email
    if flat.get("SMTP_TO") and flat.get("SMTP_SERVER"):
        try:
            _send_email_notification(flat, grade, score, profile_name)
        except Exception as e:  # noqa: E722
            logger.debug("Suppressed: %s", e)
    # Slack
    slack_url = flat.get("SLACK_WEBHOOK", "")
    if slack_url:
        try:
            _send_webhook_notification(slack_url, grade, score, profile_name, "slack")
        except Exception as e:  # noqa: E722
            logger.debug("Suppressed: %s", e)
    # Teams
    teams_url = flat.get("TEAMS_WEBHOOK", "")
    if teams_url:
        try:
            _send_webhook_notification(teams_url, grade, score, profile_name, "teams")
        except Exception as e:  # noqa: E722
            logger.debug("Suppressed: %s", e)
    # Generic webhook
    generic_url = flat.get("WEBHOOK_URL", "")
    if generic_url:
        try:
            _send_webhook_notification(generic_url, grade, score, profile_name, "webhook")
        except Exception as e:  # noqa: E722
            logger.debug("Suppressed: %s", e)


def cleanup_old_reports(script_dir: str, retention_days: int) -> int:
    """Delete report files older than retention_days. Returns count of deleted sets."""
    if retention_days <= 0:
        return 0
    cutoff = datetime.now(timezone.utc) - __import__("datetime").timedelta(days=retention_days)
    pattern = os.path.join(script_dir, "VCF-Health-Report_*.json")
    files = glob.glob(pattern)
    deleted = 0
    for f in files:
        try:
            basename = os.path.basename(f)
            m = re.search(r'(\d{8}_\d{6})', basename)
            if not m:
                continue
            ts = datetime.strptime(m.group(1), "%Y%m%d_%H%M%S")
            if ts < cutoff:
                stem = os.path.splitext(f)[0]
                for ext in (".json", ".txt", ".html", ".csv", ".md"):
                    p = stem + ext
                    if os.path.isfile(p):
                        os.remove(p)
                deleted += 1
        except Exception as e:  # noqa: E722
            continue
    return deleted


# ============================================================================
#  SPLASH SCREEN
# ============================================================================


class SplashScreen:
    """Branded splash screen shown during startup.

    Uses a Toplevel window over the hidden main root to avoid
    multiple Tk() instances (which freeze on Windows).
    """

    def __init__(self, master: tk.Tk):
        self.master = master
        self.win = tk.Toplevel(master)
        self.win.title("")
        self.win.overrideredirect(True)

        self.width = 700
        self.height = 400
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = (sw - self.width) // 2
        y = (sh - self.height) // 2
        self.win.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.win.attributes("-topmost", True)

        self.canvas = tk.Canvas(
            self.win, width=self.width, height=self.height, highlightthickness=0
        )
        self.canvas.pack()

        self.progress = 0.0
        self.status_text = "Initializing..."

        # Draw static particles once
        self.particles = []
        for _ in range(30):
            self.particles.append({
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "size": random.randint(1, 3),
            })

        self._draw()
        self.master.update_idletasks()

    def _interpolate_color(self, c1: str, c2: str, t: float) -> str:
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw(self):
        """Draw the splash frame (called on each progress update)."""
        self.canvas.delete("all")

        # Gradient background
        colors = ["#0A1628", "#0D2137", "#0F2D4A", "#0A1628"]
        bands = 40
        for i in range(bands):
            y1 = i * (self.height / bands)
            y2 = (i + 1) * (self.height / bands)
            pos = (i / bands) % 1.0
            seg = pos * (len(colors) - 1)
            idx = min(int(seg), len(colors) - 2)
            blend = seg - idx
            color = self._interpolate_color(colors[idx], colors[idx + 1], blend)
            self.canvas.create_rectangle(0, y1, self.width, y2, fill=color, outline=color)

        # Particles
        for p in self.particles:
            self.canvas.create_oval(
                p["x"] - p["size"], p["y"] - p["size"],
                p["x"] + p["size"], p["y"] + p["size"],
                fill="#1E90FF", outline="",
            )

        # Title
        self.canvas.create_text(
            self.width // 2, 120,
            text="VCF HEALTH CHECK",
            font=("Segoe UI", 40, "bold"),
            fill="#FFFFFF",
        )
        self.canvas.create_text(
            self.width // 2, 170,
            text="VMware Cloud Foundation Environment Monitor",
            font=("Segoe UI", 14),
            fill="#7FB3D5",
        )

        # Progress bar
        bar_w = 400
        bar_h = 8
        bx = (self.width - bar_w) // 2
        by = 260
        self.canvas.create_rectangle(bx, by, bx + bar_w, by + bar_h, fill="#1A2A3A", outline="")
        fill_w = int(bar_w * self.progress)
        if fill_w > 0:
            self.canvas.create_rectangle(bx, by, bx + fill_w, by + bar_h, fill="#0077B6", outline="")

        # Status
        self.canvas.create_text(
            self.width // 2, 290,
            text=self.status_text,
            font=("Segoe UI", 11),
            fill="#A0B4C8",
        )

        # Copyright + Version
        self.canvas.create_text(
            self.width // 2, self.height - 40,
            text=APP_COPYRIGHT,
            font=("Segoe UI", 9),
            fill="#5A7A9A",
        )
        self.canvas.create_text(
            self.width // 2, self.height - 20,
            text=f"v{APP_VERSION}",
            font=("Segoe UI", 9),
            fill="#4A6A8A",
        )

    def set_progress(self, progress: float, status: str = None):
        self.progress = min(max(progress, 0.0), 1.0)
        if status:
            self.status_text = status
        self._draw()
        self.master.update_idletasks()

    def close(self):
        self.win.destroy()


# ============================================================================
#  MAIN APPLICATION
# ============================================================================


class VCFHealthCheckApp:
    """Main application class."""

    def __init__(self, root: tk.Tk, user_info: Optional[dict] = None):
        self.root = root
        self.current_user = user_info or {"username": "admin", "role": "admin"}

        # State
        self.profiles_data = load_profiles()
        self.current_view = "dashboard"
        self.form_vars: Dict[str, Any] = {}  # env_var -> StringVar or BooleanVar
        self.section_frames: Dict[str, Tuple[tk.Frame, tk.Frame, tk.Label]] = {}
        self.section_states: Dict[str, bool] = {}  # expanded state

        # Script execution state
        self.process: Optional[subprocess.Popen] = None
        self.output_queue: queue.Queue = queue.Queue()
        self.run_thread: Optional[threading.Thread] = None
        self.run_start_time: Optional[float] = None
        self.run_elapsed_after_id = None
        self.is_running = False

        # Settings — validate saved paths; fall back to auto-detect if stale
        self.settings = self.profiles_data.get("_settings", {})
        saved_script = self.settings.get("script_path", "")
        if saved_script and os.path.isfile(saved_script):
            self.script_path = saved_script
        else:
            self.script_path = find_script() or ""
        saved_bash = self.settings.get("bash_path", "")
        if saved_bash and os.path.isfile(saved_bash):
            self.bash_path = saved_bash
        else:
            self.bash_path = find_bash() or ""

        # License check — partner module preferred, fallback to legacy
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        if _HAS_LICENSE_MGR:
            self._license_info = license_mgr.check_partner_license(script_dir, self.settings)
        else:
            self._license_info = _check_license(self.settings)
        lic_mode = self._license_info.get("mode", "unlicensed")
        unlicensed_tag = " [UNLICENSED]" if lic_mode == "unlicensed" else ""
        grace_tag = " [LICENSE EXPIRING]" if lic_mode == "grace" else ""
        bypass_tag = " [ADMIN]" if lic_mode == "admin_bypass" else ""
        self.root.title(f"{APP_TITLE} — Virtual Control LLC — "
                        f"{self.current_user['username']} ({self.current_user['role']})"
                        f"{unlicensed_tag}{grace_tag}{bypass_tag}")
        # Geometry is set by _finish() after splash — do not set here to avoid double-expand

        # Dark mode
        self.is_dark_mode: bool = False
        self.current_colors: Dict[str, str] = LIGHT_COLORS.copy()
        self._init_dark_mode()

        # After-id tracking for cleanup
        self._after_ids: list = []
        self._timeout_after_id = None

        # Session timeout / activity tracking
        self._last_activity = time.time()

        # Unsaved changes tracking
        self._form_snapshot: Dict[str, str] = {}

        # Scheduled runs
        self._schedule_after_id = None
        self._schedule_interval_minutes = 0

        # Client detail view state (partner ecosystem)
        self._selected_client_id = None

        # Build UI
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_layout()

        # Post-build initialization
        self._setup_activity_tracking()
        self._start_timeout_checker()
        self.root.bind("<F1>", lambda e: self._show_about())

        self._show_dashboard()

    # ── Feature / tier helpers ────────────────────────────────────────────

    def _has_feature(self, feature: str) -> bool:
        """Check if current license includes a feature."""
        if _HAS_LICENSE_MGR:
            return feature in self._license_info.get("features", [])
        return True  # no license module → no restrictions

    # ── Color helpers ────────────────────────────────────────────────────

    def _get_color(self, key: str) -> str:
        return self.current_colors.get(key, "#000000")

    def _init_dark_mode(self):
        setting = self.settings.get("dark_mode", "system")
        if setting == "system":
            self.is_dark_mode = self._detect_system_dark_mode()
        elif setting == "dark":
            self.is_dark_mode = True
        else:
            self.is_dark_mode = False
        self.current_colors = DARK_COLORS.copy() if self.is_dark_mode else LIGHT_COLORS.copy()

    def _detect_system_dark_mode(self) -> bool:
        try:
            import winreg
            reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(
                reg, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception as e:  # noqa: E722
            return False

    def _toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        self.current_colors = DARK_COLORS.copy() if self.is_dark_mode else LIGHT_COLORS.copy()
        self.settings["dark_mode"] = "dark" if self.is_dark_mode else "light"
        self._save_settings()
        self._cancel_all_after()
        self.sidebar_container.destroy()
        self.content.destroy()
        self._build_layout()
        # Re-show current view
        show_fn = {
            "dashboard": self._show_dashboard,
            "environment": self._show_environment,
            "run": self._show_run,
            "reports": self._show_reports,
            "run_history": self._show_run_history,
            "suppressions": self._show_suppressions,
            "users": self._show_users,
            "audit": self._show_audit_log,
            "settings": self._show_settings,
        }
        show_fn.get(self.current_view, self._show_dashboard)()

    def _save_settings(self):
        self.settings["script_path"] = self.script_path
        self.settings["bash_path"] = self.bash_path
        self.profiles_data["_settings"] = self.settings
        save_profiles(self.profiles_data)

    def _cancel_all_after(self):
        for aid in self._after_ids:
            try:
                self.root.after_cancel(aid)
            except Exception as e:  # noqa: E722
                logger.debug("Suppressed: %s", e)
        self._after_ids.clear()
        if self.run_elapsed_after_id:
            try:
                self.root.after_cancel(self.run_elapsed_after_id)
            except Exception as e:  # noqa: E722
                logger.debug("Suppressed: %s", e)
            self.run_elapsed_after_id = None
        if hasattr(self, "_timeout_after_id") and self._timeout_after_id:
            try:
                self.root.after_cancel(self._timeout_after_id)
            except Exception as e:  # noqa: E722
                logger.debug("Suppressed: %s", e)
            self._timeout_after_id = None
        if hasattr(self, "_schedule_after_id") and self._schedule_after_id:
            try:
                self.root.after_cancel(self._schedule_after_id)
            except Exception as e:  # noqa: E722
                logger.debug("Suppressed: %s", e)
            self._schedule_after_id = None

    def _after(self, ms, func, *args):
        aid = self.root.after(ms, func, *args)
        self._after_ids.append(aid)
        return aid

    # ── Layout ───────────────────────────────────────────────────────────

    def _build_layout(self):
        sb_bg = self._get_color("SIDEBAR_BG")
        sb_text = self._get_color("SIDEBAR_TEXT")
        ct_bg = self._get_color("CONTENT_BG")
        brand = self._get_color("BRAND_BLUE")

        self.root.configure(bg=ct_bg)

        # Sidebar
        self.sidebar_container = tk.Frame(self.root, bg=sb_bg, width=260)
        self.sidebar_container.pack(side="left", fill="y")
        self.sidebar_container.pack_propagate(False)

        sidebar_canvas = tk.Canvas(self.sidebar_container, bg=sb_bg, highlightthickness=0, width=260)
        sidebar_scroll = ttk.Scrollbar(self.sidebar_container, orient="vertical", command=sidebar_canvas.yview)
        self.sidebar = tk.Frame(sidebar_canvas, bg=sb_bg)

        sidebar_canvas.create_window((0, 0), window=self.sidebar, anchor="nw", width=260)
        sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)

        def _update_sidebar_scroll(event=None):
            sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all"))
            if self.sidebar.winfo_reqheight() > sidebar_canvas.winfo_height():
                sidebar_scroll.pack(side="right", fill="y")
            else:
                sidebar_scroll.pack_forget()

        self.sidebar.bind("<Configure>", _update_sidebar_scroll)
        sidebar_canvas.bind("<Configure>", _update_sidebar_scroll)

        sidebar_canvas.pack(side="left", fill="both", expand=True)

        def _on_sb_wheel(event):
            sidebar_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        sidebar_canvas.bind("<Enter>", lambda e: sidebar_canvas.bind_all("<MouseWheel>", _on_sb_wheel))
        sidebar_canvas.bind("<Leave>", lambda e: sidebar_canvas.unbind_all("<MouseWheel>"))

        # App title (single line to save space)
        title_frame = tk.Frame(self.sidebar, bg=sb_bg)
        title_frame.pack(pady=(12, 3))
        tk.Label(
            title_frame, text="VCF Health ", fg=sb_text, bg=sb_bg,
            font=("Segoe UI", 17, "bold"),
        ).pack(side="left")
        tk.Label(
            title_frame, text="Check", fg=brand, bg=sb_bg,
            font=("Segoe UI", 17, "bold"),
        ).pack(side="left")
        tk.Frame(self.sidebar, bg="#1A3A5C", height=1).pack(fill="x", padx=15, pady=3)

        # Nav buttons
        btn_kw = dict(
            bg=sb_bg, fg=sb_text, font=("Segoe UI", 12), relief="flat",
            activebackground="#123254", activeforeground="#FFFFFF",
            cursor="hand2", anchor="w", padx=20,
        )
        is_admin = self.current_user.get("role") == "admin"
        nav_items = [
            ("Dashboard", self._show_dashboard, True),
            ("Environment", self._show_environment, True),
            ("Run Check", self._show_run, True),
            ("Reports", self._show_reports, True),
            ("Run History", self._show_run_history, True),
            ("Clients", self._show_clients, is_admin and _HAS_CLIENT_MGR),
            ("Usage & Billing", self._show_usage, is_admin and _HAS_USAGE_TRACKER and self._has_feature("api_export")),
            ("Suppressions", self._show_suppressions, is_admin),
            ("Users", self._show_users, is_admin),
            ("Audit Log", self._show_audit_log, is_admin),
            ("Settings", self._show_settings, is_admin),
            ("Help", self._show_help, True),
            ("About", self._show_about_page, True),
        ]
        for label, cmd, enabled in nav_items:
            if enabled:
                guarded = (lambda c=cmd: self._nav_guard(c))
                tk.Button(self.sidebar, text=label, command=guarded, **btn_kw).pack(fill="x", pady=1)

        # Logged-in user indicator
        tk.Frame(self.sidebar, bg="#1A3A5C", height=1).pack(fill="x", padx=15, pady=3)
        role_color = "#27AE60" if is_admin else "#F39C12"
        tk.Label(
            self.sidebar, text=f"{self.current_user['username']}",
            fg=sb_text, bg=sb_bg, font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=20)
        tk.Label(
            self.sidebar, text=self.current_user["role"].upper(),
            fg=role_color, bg=sb_bg, font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=20)
        tk.Button(
            self.sidebar, text="Change Password", command=self._change_own_password,
            bg="#1A3A5C", fg=sb_text, font=("Segoe UI", 9), relief="flat",
            activebackground="#2A5A8C", cursor="hand2",
        ).pack(fill="x", padx=20, pady=(4, 0))

        tk.Frame(self.sidebar, bg="#1A3A5C", height=1).pack(fill="x", padx=15, pady=5)

        # Profile section
        tk.Label(
            self.sidebar, text="PROFILE", fg="#5A8AB5", bg=sb_bg,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=20)

        self.profile_var = tk.StringVar()
        profile_names = list(self.profiles_data.get("profiles", {}).keys())
        active = self.profiles_data.get("active_profile", "")
        if active and active in profile_names:
            self.profile_var.set(active)
        elif profile_names:
            self.profile_var.set(profile_names[0])

        self.profile_dropdown = ttk.Combobox(
            self.sidebar, textvariable=self.profile_var, values=profile_names,
            state="readonly", width=22,
        )
        self.profile_dropdown.pack(padx=20, pady=3, fill="x")
        self.profile_dropdown.bind("<<ComboboxSelected>>", lambda e: self._load_profile())

        # Profile buttons
        sm_btn = dict(
            bg="#1A3A5C", fg=sb_text, font=("Segoe UI", 9), relief="flat",
            activebackground="#2A5A8C", cursor="hand2",
        )

        if is_admin:
            # Admin: full profile management
            pf1 = tk.Frame(self.sidebar, bg=sb_bg)
            pf1.pack(fill="x", padx=20, pady=2)
            tk.Button(pf1, text="Save", command=self._save_profile, **sm_btn).pack(side="left", expand=True, fill="x", padx=(0, 2))
            tk.Button(pf1, text="Delete", command=self._delete_profile, **sm_btn).pack(side="left", expand=True, fill="x", padx=(2, 0))

            pf2 = tk.Frame(self.sidebar, bg=sb_bg)
            pf2.pack(fill="x", padx=20, pady=2)
            tk.Button(pf2, text="New", command=self._new_profile, **sm_btn).pack(side="left", expand=True, fill="x", padx=(0, 2))
            tk.Button(pf2, text="Import .env", command=self._import_env, **sm_btn).pack(side="left", expand=True, fill="x", padx=(2, 0))

            pf3 = tk.Frame(self.sidebar, bg=sb_bg)
            pf3.pack(fill="x", padx=20, pady=2)
            tk.Button(pf3, text="Clone", command=self._clone_profile, **sm_btn).pack(side="left", expand=True, fill="x", padx=(0, 2))
            tk.Button(pf3, text="Reset", command=self._reset_profile, **sm_btn).pack(side="left", expand=True, fill="x", padx=(2, 0))

            pf4 = tk.Frame(self.sidebar, bg=sb_bg)
            pf4.pack(fill="x", padx=20, pady=2)
            tk.Button(pf4, text="Export .env", command=self._export_env, **sm_btn).pack(side="left", expand=True, fill="x", padx=(0, 2))
            tk.Button(pf4, text="Export JSON", command=self._export_json_profile, **sm_btn).pack(side="left", expand=True, fill="x", padx=(2, 0))

            pf5 = tk.Frame(self.sidebar, bg=sb_bg)
            pf5.pack(fill="x", padx=20, pady=2)
            tk.Button(pf5, text="Import JSON", command=self._import_json_profile, **sm_btn).pack(side="left", expand=True, fill="x")
        else:
            # Operator: read-only — only export buttons
            pf1 = tk.Frame(self.sidebar, bg=sb_bg)
            pf1.pack(fill="x", padx=20, pady=2)
            tk.Button(pf1, text="Export .env", command=self._export_env, **sm_btn).pack(side="left", expand=True, fill="x", padx=(0, 2))
            tk.Button(pf1, text="Export JSON", command=self._export_json_profile, **sm_btn).pack(side="left", expand=True, fill="x", padx=(2, 0))

        tk.Frame(self.sidebar, bg="#1A3A5C", height=1).pack(fill="x", padx=15, pady=5)

        # Dark mode toggle
        dm_frame = tk.Frame(self.sidebar, bg=sb_bg)
        dm_frame.pack(fill="x", padx=20, pady=3)
        dm_text = "Light Mode" if self.is_dark_mode else "Dark Mode"
        tk.Button(
            dm_frame, text=dm_text, command=self._toggle_dark_mode,
            bg="#1A3A5C", fg=sb_text, font=("Segoe UI", 10), relief="flat",
            activebackground="#2A5A8C", cursor="hand2",
        ).pack(fill="x")

        # Last run status
        tk.Frame(self.sidebar, bg="#1A3A5C", height=1).pack(fill="x", padx=15, pady=5)
        self.last_run_label = tk.Label(
            self.sidebar, text="No runs yet", fg="#5A8AB5", bg=sb_bg,
            font=("Segoe UI", 9), wraplength=220, justify="left",
        )
        self.last_run_label.pack(anchor="w", padx=20, pady=3)
        self._update_last_run_label()

        # Copyright (clickable — opens About dialog)
        copyright_label = tk.Label(
            self.sidebar, text=APP_COPYRIGHT,
            fg="#3A5A7A", bg=sb_bg, font=("Segoe UI", 8),
            wraplength=220, cursor="hand2",
        )
        copyright_label.pack(anchor="w", padx=20, pady=(10, 15))
        copyright_label.bind("<Button-1>", lambda e: self._show_about())

        # Content area
        self.content = tk.Frame(self.root, bg=ct_bg)
        self.content.pack(side="right", fill="both", expand=True)

    def _update_last_run_label(self):
        """Show latest report grade/date in sidebar."""
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        reports = discover_reports(script_dir)
        if reports:
            r = reports[0]
            grade = r.get("grade", "?")
            date_str = r.get("date_str", "")
            color = GRADE_COLORS.get(grade, "#FFFFFF")
            self.last_run_label.configure(
                text=f"Last: Grade {grade}  ({date_str})", fg=color
            )
        else:
            self.last_run_label.configure(
                text="No runs yet", fg="#5A8AB5"
            )

    # ── View switching ───────────────────────────────────────────────────

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()
        # Clear form widget references so stale destroyed widgets are never accessed
        self.form_vars.clear()

    def _make_header(self, title: str):
        ct_bg = self._get_color("CONTENT_BG")
        text_primary = self._get_color("TEXT_PRIMARY")
        header = tk.Frame(self.content, bg=ct_bg)
        header.pack(fill="x", padx=30, pady=(20, 10))
        tk.Label(
            header, text=title, bg=ct_bg, fg=text_primary,
            font=("Segoe UI", 22, "bold"),
        ).pack(side="left")
        return header

    def _make_card(self, parent, **pack_kw) -> tk.Frame:
        card_bg = self._get_color("CARD_BG")
        border = self._get_color("BORDER")
        card = tk.Frame(parent, bg=card_bg, bd=1, relief="solid", highlightbackground=border, highlightthickness=1)
        card.pack(fill="x", padx=30, pady=5, **pack_kw)
        return card

    # ── DASHBOARD VIEW ───────────────────────────────────────────────────

    def _show_dashboard(self):
        self.current_view = "dashboard"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")
        success = self._get_color("SUCCESS")
        error = self._get_color("ERROR")
        warning = self._get_color("WARNING")

        self._make_header("Dashboard")

        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        reports = discover_reports(script_dir)

        if not reports:
            # Empty state
            empty = tk.Frame(self.content, bg=ct_bg)
            empty.pack(fill="both", expand=True)
            tk.Label(
                empty, text="No Health Check Reports Found",
                bg=ct_bg, fg=text_s, font=("Segoe UI", 16),
            ).pack(pady=(80, 10))
            tk.Label(
                empty, text="Run a health check to see results here.\nGo to the Environment tab to configure, then Run Check.",
                bg=ct_bg, fg=text_s, font=("Segoe UI", 11), justify="center",
            ).pack(pady=10)
            tk.Button(
                empty, text="Run Check", command=self._show_run,
                bg=brand, fg="white", font=("Segoe UI", 12, "bold"),
                relief="flat", padx=20, pady=8, cursor="hand2",
            ).pack(pady=20)
            return

        latest = reports[0]
        grade = latest.get("grade", "?")
        score = latest.get("score", 0)
        summary = latest.get("summary", {})
        components = latest.get("components", {})

        # Scrollable frame
        canvas = tk.Canvas(self.content, bg=ct_bg, highlightthickness=0)
        vscroll = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=ct_bg)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw",
                             tags="scroll_win")

        def _resize_scroll(event):
            canvas.itemconfig("scroll_win", width=event.width)
        canvas.bind("<Configure>", _resize_scroll)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        def _on_dash_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_dash_wheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # --- Multi-Environment Overview ---
        profiles = self.profiles_data.get("profiles", {})
        if len(profiles) > 1:
            overview_card = tk.Frame(scroll_frame, bg=card_bg, bd=1, relief="solid")
            overview_card.pack(fill="x", padx=30, pady=(5, 10))
            tk.Label(overview_card, text="Environment Overview",
                     font=("Segoe UI", 13, "bold"), bg=card_bg, fg=text_p).pack(
                anchor="w", padx=15, pady=(10, 5))

            grid = tk.Frame(overview_card, bg=card_bg)
            grid.pack(fill="x", padx=10, pady=(0, 10))
            for i in range(3):
                grid.columnconfigure(i, weight=1)

            col = 0
            for pname, pdata in profiles.items():
                last_run = pdata.get("_last_run", {})
                row_idx = col // 3
                col_idx = col % 3

                # Colored left-border based on grade
                lr_grade = last_run.get("grade", "?") if last_run else "?"
                _border_color = GRADE_COLORS.get(lr_grade, "#CCCCCC")

                env_card = tk.Frame(grid, bg=ct_bg, bd=0,
                                    cursor="hand2", padx=8, pady=6)
                env_card.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="nsew")
                # Colored left border accent
                accent = tk.Frame(env_card, bg=_border_color, width=4)
                accent.pack(side="left", fill="y", padx=(0, 8))

                inner = tk.Frame(env_card, bg=ct_bg)
                inner.pack(side="left", fill="both", expand=True)

                # Profile name
                tk.Label(inner, text=pname, bg=ct_bg, fg=text_p,
                         font=("Segoe UI", 10, "bold")).pack(anchor="w")

                # Environment label (if set)
                _env_lbl = last_run.get("env_label", "") if last_run else ""
                if _env_lbl:
                    tk.Label(inner, text=_env_lbl, bg=ct_bg, fg=text_s,
                             font=("Segoe UI", 8)).pack(anchor="w")

                if last_run:
                    lr_score = last_run.get("score", 0)
                    lr_date = last_run.get("date", "")
                    gc = GRADE_COLORS.get(lr_grade, "#888888")

                    info_row = tk.Frame(inner, bg=ct_bg)
                    info_row.pack(anchor="w")

                    # Mini grade badge
                    mini_badge = tk.Canvas(info_row, width=28, height=28,
                                          bg=ct_bg, highlightthickness=0)
                    mini_badge.pack(side="left", padx=(0, 5))
                    mini_badge.create_oval(2, 2, 26, 26, fill=gc, outline="")
                    mini_badge.create_text(14, 14, text=lr_grade, fill="white",
                                           font=("Segoe UI", 9, "bold"))

                    tk.Label(info_row, text=f"{lr_score}%  |  {lr_date}",
                             bg=ct_bg, fg=text_s, font=("Segoe UI", 8)).pack(side="left")

                    # Pass / Warn / Fail counts
                    _p = last_run.get("pass", 0)
                    _w = last_run.get("warn", 0)
                    _f = last_run.get("fail", 0)
                    if _p or _w or _f:
                        counts_row = tk.Frame(inner, bg=ct_bg)
                        counts_row.pack(anchor="w", pady=(2, 0))
                        tk.Label(counts_row, text=f"\u2713 {_p}", bg=ct_bg, fg="#27AE60",
                                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 6))
                        tk.Label(counts_row, text=f"\u26A0 {_w}", bg=ct_bg, fg="#F39C12",
                                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 6))
                        tk.Label(counts_row, text=f"\u2717 {_f}", bg=ct_bg, fg="#E74C3C",
                                 font=("Segoe UI", 8, "bold")).pack(side="left")
                else:
                    tk.Label(inner, text="No runs yet", bg=ct_bg, fg=text_s,
                             font=("Segoe UI", 8, "italic")).pack(anchor="w")

                # Click handler — bind to all descendants
                _all_widgets = [env_card, accent, inner]
                for w in (inner.winfo_children() if inner.winfo_children else []):
                    _all_widgets.append(w)
                    if hasattr(w, "winfo_children"):
                        _all_widgets.extend(w.winfo_children())
                for widget in _all_widgets:
                    widget.bind("<Button-1>",
                                lambda e, n=pname: self._switch_to_profile(n))

                col += 1

        # Top row: grade badge + score + summary
        top = tk.Frame(scroll_frame, bg=ct_bg)
        top.pack(fill="x", padx=30, pady=10)

        # Grade badge (large circle)
        grade_color = GRADE_COLORS.get(grade, "#888888")
        badge_canvas = tk.Canvas(top, width=120, height=120, bg=ct_bg, highlightthickness=0)
        badge_canvas.pack(side="left", padx=(0, 20))
        badge_canvas.create_oval(10, 10, 110, 110, fill=grade_color, outline="")
        badge_canvas.create_text(60, 55, text=grade, fill="white", font=("Segoe UI", 36, "bold"))

        # Score + date
        info_frame = tk.Frame(top, bg=ct_bg)
        info_frame.pack(side="left", fill="x", expand=True)
        tk.Label(
            info_frame, text=f"Score: {score}%", bg=ct_bg, fg=text_p,
            font=("Segoe UI", 28, "bold"),
        ).pack(anchor="w")
        tk.Label(
            info_frame, text=f"Date: {latest.get('date_str', '')}",
            bg=ct_bg, fg=text_s, font=("Segoe UI", 12),
        ).pack(anchor="w")
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        warnings = summary.get("warnings", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)
        tk.Label(
            info_frame,
            text=f"Passed: {passed}  |  Warnings: {warnings}  |  Failed: {failed}  |  Skipped: {skipped}  |  Total: {total}",
            bg=ct_bg, fg=text_s, font=("Segoe UI", 11),
        ).pack(anchor="w", pady=(5, 0))

        # Executive summary
        exec_summary = latest.get("exec_summary", "")
        if exec_summary:
            card = tk.Frame(scroll_frame, bg=card_bg, bd=1, relief="solid")
            card.pack(fill="x", padx=30, pady=10)
            tk.Label(
                card, text="Executive Summary", bg=card_bg, fg=text_p,
                font=("Segoe UI", 13, "bold"),
            ).pack(anchor="w", padx=15, pady=(10, 5))
            tk.Label(
                card, text=exec_summary, bg=card_bg, fg=text_s,
                font=("Segoe UI", 10), wraplength=800, justify="left",
            ).pack(anchor="w", padx=15, pady=(0, 10))

        # Previous grade info
        prev_grade = latest.get("prev_grade", "")
        if prev_grade:
            card = tk.Frame(scroll_frame, bg=card_bg, bd=1, relief="solid")
            card.pack(fill="x", padx=30, pady=5)
            tk.Label(
                card, text=f"Previous Grade: {prev_grade}", bg=card_bg, fg=text_s,
                font=("Segoe UI", 10),
            ).pack(padx=15, pady=8)

        # Component cards grid (3 columns)
        tk.Label(
            scroll_frame, text="Component Status", bg=ct_bg, fg=text_p,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", padx=30, pady=(15, 5))

        grid_frame = tk.Frame(scroll_frame, bg=ct_bg)
        grid_frame.pack(fill="x", padx=30, pady=5)
        for i in range(3):
            grid_frame.columnconfigure(i, weight=1)

        for idx, (comp_key, comp_label, comp_desc) in enumerate(COMPONENTS):
            row = idx // 3
            col = idx % 3
            comp_data = components.get(comp_key, {})
            c_passed = comp_data.get("passed", 0)
            c_warn = comp_data.get("warnings", 0)
            c_fail = comp_data.get("failed", 0)
            c_status = comp_data.get("status", "N/A")

            status_color = success if c_status == "PASS" else (warning if c_status == "WARN" else error)

            card = tk.Frame(grid_frame, bg=card_bg, bd=1, relief="solid")
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            # Status indicator
            hdr = tk.Frame(card, bg=card_bg)
            hdr.pack(fill="x", padx=10, pady=(10, 5))
            tk.Label(
                hdr, text=comp_label, bg=card_bg, fg=text_p,
                font=("Segoe UI", 12, "bold"),
            ).pack(side="left")
            tk.Label(
                hdr, text=c_status, bg=status_color, fg="white",
                font=("Segoe UI", 9, "bold"), padx=6, pady=2,
            ).pack(side="right")

            tk.Label(
                card, text=comp_desc, bg=card_bg, fg=text_s,
                font=("Segoe UI", 9),
            ).pack(anchor="w", padx=10)

            detail = f"Pass: {c_passed}  Warn: {c_warn}  Fail: {c_fail}"
            tk.Label(
                card, text=detail, bg=card_bg, fg=text_s,
                font=("Segoe UI", 9),
            ).pack(anchor="w", padx=10, pady=(2, 10))

        # Score trend chart
        # Use embedded trend data from the latest report, plus the current score
        trend_entries = list(latest.get("trend", []))
        # Add current report as the latest data point
        trend_entries.insert(0, {
            "date": latest.get("date"),
            "score": score,
            "grade": grade,
        })
        # Filter entries that have valid dates and reverse to chronological order
        trend_entries = [t for t in trend_entries if t.get("date") is not None]
        trend_entries.reverse()

        if len(trend_entries) >= 2:
            tk.Label(
                scroll_frame, text="Score Trend", bg=ct_bg, fg=text_p,
                font=("Segoe UI", 14, "bold"),
            ).pack(anchor="w", padx=30, pady=(20, 5))

            chart_card = tk.Frame(scroll_frame, bg=card_bg, bd=1, relief="solid")
            chart_card.pack(fill="x", padx=30, pady=5)

            chart_w = 700
            chart_h = 180
            chart = tk.Canvas(chart_card, width=chart_w, height=chart_h, bg=card_bg, highlightthickness=0)
            chart.pack(padx=20, pady=15)

            n = len(trend_entries)
            margin_l, margin_r, margin_t, margin_b = 50, 30, 20, 30
            plot_w = chart_w - margin_l - margin_r
            plot_h = chart_h - margin_t - margin_b

            # Y axis (0-100)
            for yv in [0, 25, 50, 75, 100]:
                yy = margin_t + plot_h - (yv / 100 * plot_h)
                chart.create_line(margin_l, yy, chart_w - margin_r, yy, fill="#E0E0E0", dash=(2, 2))
                chart.create_text(margin_l - 5, yy, text=str(yv), anchor="e",
                                  fill=text_s, font=("Segoe UI", 8))

            # Plot points
            points = []
            for i, t in enumerate(trend_entries):
                x = margin_l + (i / max(n - 1, 1)) * plot_w
                s = t.get("score", 0)
                y = margin_t + plot_h - (s / 100 * plot_h)
                points.append((x, y))

            for i in range(len(points) - 1):
                chart.create_line(
                    points[i][0], points[i][1], points[i + 1][0], points[i + 1][1],
                    fill=brand, width=2,
                )
            for i, (px, py) in enumerate(points):
                chart.create_oval(px - 4, py - 4, px + 4, py + 4, fill=brand, outline="white")
                dt = trend_entries[i].get("date")
                date_label = dt.strftime("%m/%d") if isinstance(dt, datetime) else "?"
                chart.create_text(
                    px, margin_t + plot_h + 15,
                    text=date_label,
                    fill=text_s, font=("Segoe UI", 7),
                )

        # Quick actions
        actions = tk.Frame(scroll_frame, bg=ct_bg)
        actions.pack(fill="x", padx=30, pady=20)
        tk.Button(
            actions, text="Run New Check", command=self._show_run,
            bg=brand, fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", padx=15, pady=6, cursor="hand2",
        ).pack(side="left", padx=(0, 10))
        tk.Button(
            actions, text="View Reports", command=self._show_reports,
            bg="#1A3A5C", fg="white", font=("Segoe UI", 11),
            relief="flat", padx=15, pady=6, cursor="hand2",
        ).pack(side="left")

    # ── ENVIRONMENT VIEW ─────────────────────────────────────────────────

    def _show_environment(self):
        self.current_view = "environment"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")
        border = self._get_color("BORDER")
        is_readonly = self.current_user.get("role") != "admin"

        header = self._make_header("Environment Configuration")
        if is_readonly:
            tk.Label(header, text="  READ-ONLY", bg=ct_bg, fg="#E74C3C",
                     font=("Segoe UI", 11, "bold")).pack(side="left", padx=10)

        # Scrollable area
        canvas = tk.Canvas(self.content, bg=ct_bg, highlightthickness=0)
        vscroll = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=ct_bg)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="scroll_win")

        def _resize(event):
            canvas.itemconfig("scroll_win", width=event.width)
        canvas.bind("<Configure>", _resize)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        def _on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_wheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        self.form_vars.clear()
        self.section_frames.clear()
        self.section_states.clear()

        # Load active profile data
        active = self.profile_var.get()
        profile_data = {}
        if active and active in self.profiles_data.get("profiles", {}):
            profile_data = profile_to_form(self.profiles_data["profiles"][active])

        # Integer validation
        vcmd = (self.root.register(self._validate_int), "%P")

        # Build collapsible sections
        for section_key, section_label, expanded_default, fields in FIELD_SECTIONS:
            # Gate branding section behind Professional+ tier
            if section_key == "branding" and not self._has_feature("branding"):
                self._build_locked_section(
                    scroll_frame, section_label, "Professional",
                    card_bg, text_p, text_s, border, ct_bg,
                )
                continue
            self._build_collapsible_section(
                scroll_frame, section_key, section_label, expanded_default,
                fields, profile_data, card_bg, text_p, text_s, brand, border, ct_bg, vcmd,
            )

        # Run Options section
        self._build_run_options_section(scroll_frame, profile_data, card_bg, text_p, text_s, brand, border, ct_bg)

        # Read-only mode for operators: disable all form widgets
        if is_readonly:
            for var_name, widget in self.form_vars.items():
                if isinstance(widget, tk.Text):
                    widget.configure(state="disabled")
                elif isinstance(widget, tk.BooleanVar):
                    # Find checkbutton and disable
                    pass  # Handled by _build_run_options_section
            # Also disable all Entry widgets in the form
            self._set_form_readonly(scroll_frame)

        # Bottom padding
        tk.Frame(scroll_frame, bg=ct_bg, height=40).pack()

        # Snapshot form for unsaved-changes detection
        self.root.after(100, self._snapshot_form)

    def _set_form_readonly(self, parent):
        """Recursively disable all Entry, Text, and Checkbutton widgets."""
        for child in parent.winfo_children():
            try:
                if isinstance(child, tk.Entry):
                    child.configure(state="readonly")
                elif isinstance(child, tk.Text):
                    child.configure(state="disabled")
                elif isinstance(child, tk.Checkbutton):
                    child.configure(state="disabled")
            except tk.TclError:
                pass
            self._set_form_readonly(child)

    def _validate_int(self, value: str) -> bool:
        if value == "":
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False

    def _build_locked_section(
        self, parent, section_label, required_tier,
        card_bg, text_p, text_s, border, ct_bg,
    ):
        """Render a locked/disabled section with upgrade prompt."""
        container = tk.Frame(parent, bg=ct_bg)
        container.pack(fill="x", padx=30, pady=5)
        header = tk.Frame(container, bg=card_bg)
        header.pack(fill="x")
        header.configure(highlightbackground=border, highlightthickness=1)
        tk.Label(
            header, text="\U0001F512", bg=card_bg, fg=text_s,
            font=("Segoe UI", 12),
        ).pack(side="left", padx=(15, 5), pady=10)
        tk.Label(
            header, text=section_label, bg=card_bg, fg=text_s,
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left", pady=10)
        tk.Label(
            header, text=f"{required_tier} edition required",
            bg=card_bg, fg="#E67E22", font=("Segoe UI", 9, "italic"),
        ).pack(side="right", padx=15)

    def _build_collapsible_section(
        self, parent, section_key, section_label, expanded_default,
        fields, profile_data, card_bg, text_p, text_s, brand, border, ct_bg, vcmd,
    ):
        """Build one collapsible form section."""
        container = tk.Frame(parent, bg=ct_bg)
        container.pack(fill="x", padx=30, pady=5)

        is_expanded = expanded_default
        self.section_states[section_key] = is_expanded

        # Header (clickable)
        header = tk.Frame(container, bg=card_bg, cursor="hand2")
        header.pack(fill="x")
        header.configure(highlightbackground=border, highlightthickness=1)

        arrow_text = "\u25BC" if is_expanded else "\u25B6"
        arrow_label = tk.Label(
            header, text=arrow_text, bg=card_bg, fg=brand,
            font=("Segoe UI", 12),
        )
        arrow_label.pack(side="left", padx=(15, 5), pady=10)

        tk.Label(
            header, text=section_label, bg=card_bg, fg=text_p,
            font=("Segoe UI", 12, "bold"),
        ).pack(side="left", pady=10)

        field_count = len(fields)
        tk.Label(
            header, text=f"{field_count} fields", bg=card_bg, fg=text_s,
            font=("Segoe UI", 9),
        ).pack(side="right", padx=15)

        # Content
        content_frame = tk.Frame(container, bg=card_bg)
        content_frame.configure(highlightbackground=border, highlightthickness=1)

        # Build fields inside content_frame
        for var_name, label, ftype, default in fields:
            row = tk.Frame(content_frame, bg=card_bg)
            row.pack(fill="x", padx=15, pady=4)

            tk.Label(
                row, text=label, bg=card_bg, fg=text_p,
                font=("Segoe UI", 10), width=25, anchor="w",
            ).pack(side="left")

            val = profile_data.get(var_name, default)

            if ftype == "textarea":
                var = tk.StringVar(value=val)
                self.form_vars[var_name] = var
                txt = tk.Text(row, height=3, font=("Segoe UI", 10), wrap="word", bd=1, relief="solid")
                txt.insert("1.0", val)
                txt.pack(side="left", fill="x", expand=True, padx=(5, 0))
                # Store text widget ref for extraction
                self.form_vars[var_name] = txt
            elif ftype == "password":
                var = tk.StringVar(value=val)
                self.form_vars[var_name] = var
                entry = tk.Entry(row, textvariable=var, show="*", font=("Segoe UI", 10), bd=1, relief="solid")
                entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
                # Toggle button
                def make_toggle(e=entry):
                    def toggle():
                        if e.cget("show") == "*":
                            e.configure(show="")
                        else:
                            e.configure(show="*")
                    return toggle
                tk.Button(
                    row, text="\U0001F441", command=make_toggle(entry),
                    bg=card_bg, fg=text_s, font=("Segoe UI", 10),
                    relief="flat", cursor="hand2", width=3,
                ).pack(side="left")
            elif ftype == "int":
                var = tk.StringVar(value=val)
                self.form_vars[var_name] = var
                entry = tk.Entry(
                    row, textvariable=var, font=("Segoe UI", 10), bd=1, relief="solid",
                    validate="key", validatecommand=vcmd, width=10,
                )
                entry.pack(side="left", padx=(5, 0))
            elif ftype == "file":
                var = tk.StringVar(value=val)
                self.form_vars[var_name] = var
                entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10), bd=1, relief="solid")
                entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
                def make_browse(v=var):
                    def browse():
                        path = filedialog.askopenfilename(
                            title="Select Logo Image",
                            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.svg"), ("All files", "*.*")],
                        )
                        if path:
                            v.set(path)
                    return browse
                tk.Button(
                    row, text="Browse...", command=make_browse(var),
                    bg=brand, fg="white", font=("Segoe UI", 9),
                    relief="flat", cursor="hand2", padx=8,
                ).pack(side="left", padx=(5, 0))
            else:
                var = tk.StringVar(value=val)
                self.form_vars[var_name] = var
                entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 10), bd=1, relief="solid")
                entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

            # Attach tooltip if defined
            tip_text = FIELD_TOOLTIPS.get(var_name)
            if tip_text:
                _ToolTip(row, tip_text)

        if is_expanded:
            content_frame.pack(fill="x")

        # Store references
        self.section_frames[section_key] = (container, content_frame, arrow_label)

        # Toggle handler
        def make_toggle_section(sk=section_key):
            def toggle(event=None):
                expanded = self.section_states[sk]
                _, cf, al = self.section_frames[sk]
                if expanded:
                    cf.pack_forget()
                    al.configure(text="\u25B6")
                else:
                    cf.pack(fill="x")
                    al.configure(text="\u25BC")
                self.section_states[sk] = not expanded
            return toggle

        toggle_fn = make_toggle_section(section_key)
        header.bind("<Button-1>", toggle_fn)
        for child in header.winfo_children():
            child.bind("<Button-1>", toggle_fn)

    def _build_run_options_section(self, parent, profile_data, card_bg, text_p, text_s, brand, border, ct_bg):
        """Build the run options (checkboxes) section."""
        container = tk.Frame(parent, bg=ct_bg)
        container.pack(fill="x", padx=30, pady=5)

        section_key = "run_options"
        self.section_states[section_key] = False

        header = tk.Frame(container, bg=card_bg, cursor="hand2")
        header.pack(fill="x")
        header.configure(highlightbackground=border, highlightthickness=1)

        arrow_label = tk.Label(header, text="\u25B6", bg=card_bg, fg=brand, font=("Segoe UI", 12))
        arrow_label.pack(side="left", padx=(15, 5), pady=10)
        tk.Label(header, text="Run Options", bg=card_bg, fg=text_p, font=("Segoe UI", 12, "bold")).pack(side="left", pady=10)
        tk.Label(header, text=f"{len(RUN_OPTIONS)} flags", bg=card_bg, fg=text_s, font=("Segoe UI", 9)).pack(side="right", padx=15)

        content_frame = tk.Frame(container, bg=card_bg)
        content_frame.configure(highlightbackground=border, highlightthickness=1)

        run_opts_data = profile_data.get("run_options", {})
        for opt_key, flag, desc in RUN_OPTIONS:
            row = tk.Frame(content_frame, bg=card_bg)
            row.pack(fill="x", padx=15, pady=3)
            var = tk.BooleanVar(value=run_opts_data.get(opt_key, False))
            self.form_vars[f"opt_{opt_key}"] = var
            tk.Checkbutton(
                row, text=f"{flag}  —  {desc}", variable=var,
                bg=card_bg, fg=text_p, font=("Segoe UI", 10),
                activebackground=card_bg, selectcolor=card_bg,
                anchor="w",
            ).pack(anchor="w")

        self.section_frames[section_key] = (container, content_frame, arrow_label)

        def toggle(event=None):
            expanded = self.section_states[section_key]
            _, cf, al = self.section_frames[section_key]
            if expanded:
                cf.pack_forget()
                al.configure(text="\u25B6")
            else:
                cf.pack(fill="x")
                al.configure(text="\u25BC")
            self.section_states[section_key] = not expanded

        header.bind("<Button-1>", toggle)
        for child in header.winfo_children():
            child.bind("<Button-1>", toggle)

    def _get_form_values(self) -> Tuple[dict, dict]:
        """Extract current form values. Returns (flat_dict, run_options_dict)."""
        flat = {}
        for section_key, _label, _expanded, fields in FIELD_SECTIONS:
            for var_name, _lbl, ftype, default in fields:
                widget = self.form_vars.get(var_name)
                if widget is None:
                    flat[var_name] = default
                elif isinstance(widget, tk.Text):
                    flat[var_name] = widget.get("1.0", "end-1c").strip()
                elif isinstance(widget, (tk.StringVar,)):
                    flat[var_name] = widget.get()
                else:
                    flat[var_name] = str(widget.get()) if hasattr(widget, "get") else default

        run_options = {}
        for opt_key, _flag, _desc in RUN_OPTIONS:
            var = self.form_vars.get(f"opt_{opt_key}")
            run_options[opt_key] = var.get() if var else False

        return flat, run_options

    # ── RUN CHECK VIEW ───────────────────────────────────────────────────

    def _show_run(self):
        self.current_view = "run"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")
        success = self._get_color("SUCCESS")
        error = self._get_color("ERROR")
        term_bg = self._get_color("TERMINAL_BG")
        term_fg = self._get_color("TERMINAL_FG")

        self._make_header("Run Health Check")

        # Check prerequisites
        bash_ok = self.bash_path and os.path.isfile(self.bash_path)
        script_ok = self.script_path and os.path.isfile(self.script_path)

        if not bash_ok or not script_ok:
            warn_card = self._make_card(self.content)
            tk.Label(warn_card, text="Prerequisites Not Met",
                     font=("Segoe UI", 12, "bold"), fg="#D32F2F",
                     bg=self._get_color("CARD_BG")).pack(anchor="w", padx=15, pady=(10, 5))
            if not bash_ok:
                tk.Label(warn_card, text="Bash shell not found or not configured.",
                         font=("Segoe UI", 10), fg=text_s,
                         bg=self._get_color("CARD_BG")).pack(anchor="w", padx=15, pady=2)
            if not script_ok:
                tk.Label(warn_card, text="Health check script not found or not configured.",
                         font=("Segoe UI", 10), fg=text_s,
                         bg=self._get_color("CARD_BG")).pack(anchor="w", padx=15, pady=2)
            tk.Label(warn_card, text="Go to Settings to configure paths.",
                     font=("Segoe UI", 10, "italic"), fg=text_s,
                     bg=self._get_color("CARD_BG")).pack(anchor="w", padx=15, pady=(4, 2))
            is_admin = self.current_user.get("role") == "admin"
            if is_admin:
                tk.Button(warn_card, text="Open Settings", command=self._show_settings,
                          bg="#0077B6", fg="white", font=("Segoe UI", 10, "bold"),
                          relief="flat", padx=12, pady=4, cursor="hand2",
                          ).pack(anchor="w", padx=15, pady=(4, 10))
            else:
                tk.Label(warn_card, text="Contact an administrator to configure paths.",
                         font=("Segoe UI", 9), fg="#888",
                         bg=self._get_color("CARD_BG")).pack(anchor="w", padx=15, pady=(0, 10))

        # Controls row
        ctrl = tk.Frame(self.content, bg=ct_bg)
        ctrl.pack(fill="x", padx=30, pady=(0, 10))

        # Profile display
        active = self.profile_var.get()
        if active:
            tk.Label(
                ctrl, text=f"Profile: {active}", bg=ct_bg, fg=text_p,
                font=("Segoe UI", 11),
            ).pack(side="left", padx=(0, 15))

        # Buttons — disabled if prerequisites not met
        btn_state = "normal" if (bash_ok and script_ok) else "disabled"

        self.btn_validate = tk.Button(
            ctrl, text="Validate Only", command=self._run_validate,
            bg="#1A3A5C", fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=12, pady=5, cursor="hand2", state=btn_state,
        )
        self.btn_validate.pack(side="left", padx=5)

        self.btn_run = tk.Button(
            ctrl, text="Run Full Check", command=self._run_full,
            bg=brand, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=12, pady=5, cursor="hand2", state=btn_state,
        )
        self.btn_run.pack(side="left", padx=5)

        self.btn_stop = tk.Button(
            ctrl, text="Stop", command=self._stop_run, state="disabled",
            bg=error, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=12, pady=5, cursor="hand2",
        )
        self.btn_stop.pack(side="left", padx=5)

        # Elapsed timer
        self.elapsed_label = tk.Label(
            ctrl, text="", bg=ct_bg, fg=text_s,
            font=("Segoe UI", 10),
        )
        self.elapsed_label.pack(side="right")

        # Schedule row
        sched_row = tk.Frame(self.content, bg=ct_bg)
        sched_row.pack(fill="x", padx=30, pady=(0, 5))
        tk.Label(sched_row, text="Schedule:", bg=ct_bg, fg=text_p,
                 font=("Segoe UI", 10)).pack(side="left")
        if self._has_feature("scheduling"):
            self._schedule_var = tk.StringVar(value="Off")
            sched_options = ["Off", "30 min", "60 min", "2 hr", "4 hr", "8 hr", "12 hr", "24 hr"]
            sched_menu = ttk.Combobox(sched_row, textvariable=self._schedule_var,
                                      values=sched_options, state="readonly", width=10)
            sched_menu.pack(side="left", padx=(5, 10))
            sched_menu.bind("<<ComboboxSelected>>", lambda e: self._on_schedule_changed())
            self._schedule_status_label = tk.Label(sched_row, text="", bg=ct_bg, fg=text_s,
                                                   font=("Segoe UI", 9, "italic"))
            self._schedule_status_label.pack(side="left")
            # Reflect current state
            if self._schedule_interval_minutes > 0:
                mins = self._schedule_interval_minutes
                labels = {30: "30 min", 60: "60 min", 120: "2 hr", 240: "4 hr",
                          480: "8 hr", 720: "12 hr", 1440: "24 hr"}
                self._schedule_var.set(labels.get(mins, f"{mins} min"))
                self._schedule_status_label.config(text=f"Active — every {mins} min", fg=self._get_color("SUCCESS"))
        else:
            tk.Label(sched_row, text="Professional edition required",
                     bg=ct_bg, fg="#E67E22", font=("Segoe UI", 9, "italic")).pack(side="left", padx=(5, 0))
            self._schedule_var = tk.StringVar(value="Off")
            self._schedule_status_label = tk.Label(sched_row, text="", bg=ct_bg, fg=text_s,
                                                   font=("Segoe UI", 9, "italic"))

        # Terminal
        term_frame = tk.Frame(self.content, bg=term_bg, bd=1, relief="solid",
                              highlightbackground=self._get_color("BORDER"), highlightthickness=1)
        term_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        self.terminal = tk.Text(
            term_frame, bg=term_bg, fg=term_fg,
            font=("Consolas", 10), wrap="word",
            insertbackground=term_fg, relief="flat",
            padx=10, pady=10, state="disabled",
        )
        term_scroll = ttk.Scrollbar(term_frame, orient="vertical", command=self.terminal.yview)
        self.terminal.configure(yscrollcommand=term_scroll.set)
        term_scroll.pack(side="right", fill="y")
        self.terminal.pack(fill="both", expand=True)

        # Configure text tags for coloring
        self.terminal.tag_configure("pass", foreground="#27AE60")
        self.terminal.tag_configure("warn", foreground="#F39C12")
        self.terminal.tag_configure("fail", foreground="#E74C3C")
        self.terminal.tag_configure("info", foreground="#3498DB")
        self.terminal.tag_configure("header", foreground="#FFFFFF", font=("Consolas", 10, "bold"))

        # Show prompt in terminal
        self._write_terminal("Ready. Click 'Validate Only' or 'Run Full Check' to begin.\n\n", "info")
        if active:
            self._write_terminal(f"Active profile: {active}\n", "info")
            self._write_terminal(f"Script: {self.script_path or 'Not configured'}\n", "info")
            self._write_terminal(f"Bash: {self.bash_path or 'Not configured'}\n", "info")

        # Report buttons frame (hidden until run completes)
        self.report_buttons_frame = tk.Frame(self.content, bg=ct_bg)
        self.report_buttons_frame.pack(fill="x", padx=30, pady=(0, 15))

        # If currently running, resume polling
        if self.is_running:
            self._set_running_state(True)
            self._poll_output()

    def _write_terminal(self, text: str, tag: str = None):
        """Append text to terminal widget."""
        self.terminal.configure(state="normal")
        if tag:
            self.terminal.insert("end", text, tag)
        else:
            self.terminal.insert("end", text)
        self.terminal.see("end")
        self.terminal.configure(state="disabled")

    def _set_running_state(self, running: bool):
        """Enable/disable buttons based on run state."""
        if hasattr(self, "btn_validate"):
            self.btn_validate.configure(state="disabled" if running else "normal")
        if hasattr(self, "btn_run"):
            self.btn_run.configure(state="disabled" if running else "normal")
        if hasattr(self, "btn_stop"):
            self.btn_stop.configure(state="normal" if running else "disabled")

    def _snapshot_form(self):
        """Capture current form values as clean baseline for dirty checking."""
        snap = {}
        for var_name, widget in self.form_vars.items():
            if isinstance(widget, tk.Text):
                snap[var_name] = widget.get("1.0", "end").strip()
            elif isinstance(widget, tk.BooleanVar):
                snap[var_name] = str(widget.get())
            elif isinstance(widget, tk.StringVar):
                snap[var_name] = widget.get()
        self._form_snapshot = snap

    def _is_form_dirty(self) -> bool:
        """Check if any form field has changed since last snapshot."""
        if not self._form_snapshot or not self.form_vars:
            return False
        for var_name, widget in self.form_vars.items():
            if isinstance(widget, tk.Text):
                current = widget.get("1.0", "end").strip()
            elif isinstance(widget, tk.BooleanVar):
                current = str(widget.get())
            elif isinstance(widget, tk.StringVar):
                current = widget.get()
            else:
                continue
            if current != self._form_snapshot.get(var_name, ""):
                return True
        return False

    def _check_unsaved_changes(self) -> bool:
        """If form is dirty, ask user. Returns True if OK to proceed (discard/clean)."""
        if not self._is_form_dirty():
            return True
        return messagebox.askyesno(
            "Unsaved Changes",
            "You have unsaved changes in the Environment form.\n\nDiscard changes and continue?",
        )

    def _validate_all_fields(self) -> list:
        """Validate all form fields. Returns list of error strings."""
        errors = []
        if not self.form_vars:
            return errors
        if self.current_view != "environment":
            # Widgets may be destroyed; validate from saved profile instead
            active = self.profile_var.get()
            if active and active in self.profiles_data.get("profiles", {}):
                flat = profile_to_form(self.profiles_data["profiles"][active])
                for var_name, val in flat.items():
                    err = validate_field(var_name, str(val).strip())
                    if err:
                        errors.append(err)
            return errors
        for var_name, widget in self.form_vars.items():
            try:
                if isinstance(widget, tk.Text):
                    val = widget.get("1.0", "end").strip()
                elif isinstance(widget, (tk.StringVar, tk.BooleanVar)):
                    val = str(widget.get()).strip()
                else:
                    continue
            except tk.TclError:
                continue
            err = validate_field(var_name, val)
            if err:
                errors.append(err)
        return errors

    def _on_schedule_changed(self):
        """Handle schedule dropdown change."""
        val = self._schedule_var.get()
        mapping = {"Off": 0, "30 min": 30, "60 min": 60, "2 hr": 120, "4 hr": 240,
                   "8 hr": 480, "12 hr": 720, "24 hr": 1440}
        minutes = mapping.get(val, 0)
        if minutes == 0:
            self._stop_schedule()
            if hasattr(self, "_schedule_status_label"):
                self._schedule_status_label.config(text="", fg=self._get_color("TEXT_SECONDARY"))
        else:
            self._start_schedule(minutes)
            if hasattr(self, "_schedule_status_label"):
                self._schedule_status_label.config(
                    text=f"Active — every {minutes} min", fg=self._get_color("SUCCESS"))

    def _start_schedule(self, interval_minutes: int):
        """Start a recurring health check schedule."""
        self._stop_schedule()
        if interval_minutes <= 0:
            return
        self._schedule_interval_minutes = interval_minutes
        ms = interval_minutes * 60 * 1000
        self._schedule_after_id = self._after(ms, self._scheduled_run)
        _audit_log(self.current_user["username"], "SCHEDULE_STARTED", f"every {interval_minutes} min")

    def _stop_schedule(self):
        """Stop the recurring schedule."""
        if self._schedule_after_id:
            try:
                self.root.after_cancel(self._schedule_after_id)
            except Exception as e:  # noqa: E722
                logger.debug("Suppressed: %s", e)
            self._schedule_after_id = None
            if self._schedule_interval_minutes > 0:
                _audit_log(self.current_user["username"], "SCHEDULE_STOPPED")
            self._schedule_interval_minutes = 0

    def _scheduled_run(self):
        """Execute a scheduled health check run, then re-schedule."""
        self._schedule_after_id = None
        if self.is_running:
            # Already running — skip this cycle, reschedule
            ms = self._schedule_interval_minutes * 60 * 1000
            self._schedule_after_id = self._after(ms, self._scheduled_run)
            return
        _audit_log(self.current_user["username"], "SCHEDULED_RUN_TRIGGERED")
        self._execute_script(validate_only=False)
        # Reschedule
        if self._schedule_interval_minutes > 0:
            ms = self._schedule_interval_minutes * 60 * 1000
            self._schedule_after_id = self._after(ms, self._scheduled_run)

    def _run_validate(self):
        self._execute_script(validate_only=True)

    def _run_full(self):
        self._execute_script(validate_only=False)

    def _execute_script(self, validate_only: bool = False):
        """Start script execution in a background thread."""
        # Check prerequisites
        if not self.bash_path or not os.path.isfile(self.bash_path):
            messagebox.showerror("Error", f"Bash not found: {self.bash_path}\nConfigure in Settings.")
            return
        if not self.script_path or not os.path.isfile(self.script_path):
            messagebox.showerror("Error", f"Script not found: {self.script_path}\nConfigure in Settings.")
            return

        # Input validation — block run if errors
        validation_errors = self._validate_all_fields()
        if validation_errors:
            msg = "Fix the following before running:\n\n" + "\n".join(f"  • {e}" for e in validation_errors)
            messagebox.showerror("Validation Errors", msg)
            return

        # Reload profiles from disk to pick up any external edits
        self.profiles_data = load_profiles()
        active = self.profile_var.get()

        # Sync form widgets with on-disk profile data (if form is open)
        if self.form_vars and active and active in self.profiles_data.get("profiles", {}):
            disk_flat = profile_to_form(self.profiles_data["profiles"][active])
            disk_flat.pop("run_options", None)
            for var_name, widget in self.form_vars.items():
                if var_name in disk_flat:
                    if isinstance(widget, tk.Text):
                        widget.delete("1.0", "end")
                        widget.insert("1.0", disk_flat[var_name])
                    elif isinstance(widget, (tk.StringVar, tk.BooleanVar)):
                        widget.set(disk_flat[var_name])

        # Collect form values if environment view was shown
        if self.form_vars:
            flat, run_options = self._get_form_values()
        else:
            # Load from active profile
            if active and active in self.profiles_data.get("profiles", {}):
                flat = profile_to_form(self.profiles_data["profiles"][active])
                run_options = flat.pop("run_options", {})
            else:
                flat, run_options = {}, {}

        # Generate temp .env file
        script_dir = os.path.dirname(self.script_path)
        temp_env = os.path.join(script_dir, ".vcf-hc-gui-temp.env")
        export_env_file(temp_env, flat)

        # Build command — convert Windows paths for the target shell
        cmd = [self.bash_path]
        if "wsl" in self.bash_path.lower():
            # WSL: /mnt/e/...
            bash_script = self._win_to_wsl_path(self.script_path)
            bash_env = self._win_to_wsl_path(temp_env)
        elif "git" in self.bash_path.lower() or "msys" in self.bash_path.lower():
            # Git Bash / MSYS2: /e/...
            bash_script = self._win_to_git_bash_path(self.script_path)
            bash_env = self._win_to_git_bash_path(temp_env)
        else:
            # Unknown bash — try Git Bash style conversion as best-effort
            bash_script = self._win_to_git_bash_path(self.script_path)
            bash_env = self._win_to_git_bash_path(temp_env)
        cmd.extend([bash_script, "--env", bash_env])

        if validate_only:
            cmd.append("--validate")
        else:
            for opt_key, flag, _desc in RUN_OPTIONS:
                if run_options.get(opt_key, False):
                    cmd.append(flag)

        # Clear terminal
        if hasattr(self, "terminal"):
            self.terminal.configure(state="normal")
            self.terminal.delete("1.0", "end")
            self.terminal.configure(state="disabled")

        # Clear report buttons
        if hasattr(self, "report_buttons_frame"):
            for w in self.report_buttons_frame.winfo_children():
                w.destroy()

        mode = "Validate" if validate_only else "Full Check"
        _audit_log(self.current_user["username"], "HEALTHCHECK_STARTED", f"{active} ({mode})")
        self._write_terminal(f"[GUI] Starting {mode}...\n", "info")
        self._write_terminal(f"[GUI] User: {self.current_user['username']} ({self.current_user['role']})\n", "info")
        self._write_terminal(f"[GUI] Script: {self.script_path}\n", "info")
        self._write_terminal(f"[GUI] Env: {temp_env}\n\n", "info")

        # Start execution
        self.is_running = True
        self.run_start_time = time.time()
        self._set_running_state(True)

        # Empty queue
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break

        # Start thread
        self.run_thread = threading.Thread(
            target=self._run_worker, args=(cmd, script_dir, temp_env),
            daemon=True,
        )
        self.run_thread.start()

        # Start polling
        self._poll_output()
        self._update_elapsed()

    @staticmethod
    def _win_to_git_bash_path(path: str) -> str:
        """Convert Windows path to Git Bash (MSYS2) path.  E:\\Foo\\Bar -> /e/Foo/Bar"""
        path = path.replace("\\", "/")
        m = re.match(r"^([A-Za-z]):/(.*)$", path)
        if m:
            return f"/{m.group(1).lower()}/{m.group(2)}"
        return path

    def _win_to_wsl_path(self, path: str) -> str:
        """Convert Windows path to WSL path.  E:\\Foo\\Bar -> /mnt/e/Foo/Bar"""
        path = path.replace("\\", "/")
        m = re.match(r"^([A-Za-z]):/(.*)$", path)
        if m:
            return f"/mnt/{m.group(1).lower()}/{m.group(2)}"
        return path

    def _run_worker(self, cmd: list, cwd: str, temp_env: str):
        """Worker thread: run subprocess and push output to queue."""
        try:
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                creationflags=creation_flags,
            )

            for line in iter(self.process.stdout.readline, ""):
                self.output_queue.put(("line", line))
            self.process.stdout.close()
            rc = self.process.wait()
            self.output_queue.put(("done", rc))
        except Exception as e:
            self.output_queue.put(("error", str(e)))
        finally:
            # Clean up temp env
            try:
                if os.path.exists(temp_env):
                    os.remove(temp_env)
            except Exception as e:  # noqa: E722
                logger.debug("Suppressed: %s", e)

    def _poll_output(self):
        """Poll output queue and update terminal. Runs on main thread."""
        if not self.is_running:
            return

        try:
            while True:
                msg_type, data = self.output_queue.get_nowait()
                if msg_type == "line":
                    self._append_line(data)
                elif msg_type == "done":
                    self._on_run_complete(data)
                    return
                elif msg_type == "error":
                    self._write_terminal(f"\n[GUI] ERROR: {data}\n", "fail")
                    self._on_run_complete(-1)
                    return
        except queue.Empty:
            pass

        self._after(100, self._poll_output)

    def _append_line(self, line: str):
        """Append a line to terminal with ANSI stripping and color tags."""
        # Strip ANSI escape codes
        clean = re.sub(r'\x1b\[[0-9;]*[mGKHJ]', '', line)

        # Determine tag based on content
        tag = None
        if re.search(r'\[PASS\]', clean):
            tag = "pass"
        elif re.search(r'\[WARN\]', clean):
            tag = "warn"
        elif re.search(r'\[FAIL\]', clean):
            tag = "fail"
        elif re.search(r'\[INFO\]', clean):
            tag = "info"
        elif re.search(r'^[=\-]{10,}', clean) or re.search(r'^\s*VCF Health', clean):
            tag = "header"

        self._write_terminal(clean, tag)

    def _update_elapsed(self):
        """Update elapsed time display."""
        if not self.is_running or self.run_start_time is None:
            return
        elapsed = time.time() - self.run_start_time
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        if hasattr(self, "elapsed_label"):
            self.elapsed_label.configure(text=f"Elapsed: {mins:02d}:{secs:02d}")
        self.run_elapsed_after_id = self._after(1000, self._update_elapsed)

    def _on_run_complete(self, return_code: int):
        """Handle script completion."""
        self.is_running = False
        self.process = None
        self._set_running_state(False)

        elapsed = time.time() - self.run_start_time if self.run_start_time else 0
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)

        # Exit codes: 0=all pass, 1=warnings, 2=failures — all are successful runs
        if return_code == 0:
            self._write_terminal(f"\n[GUI] Completed — all checks passed ({mins}m {secs}s)\n", "pass")
        elif return_code == 1:
            self._write_terminal(f"\n[GUI] Completed — warnings detected ({mins}m {secs}s)\n", "warn")
        elif return_code == 2:
            self._write_terminal(f"\n[GUI] Completed — failures detected ({mins}m {secs}s)\n", "warn")
        else:
            self._write_terminal(f"\n[GUI] Exited with code {return_code} after {mins}m {secs}s\n", "fail")

        # Update sidebar last run
        self._update_last_run_label()

        # Store _last_run in active profile for multi-environment dashboard
        active = self.profile_var.get()
        if active and active in self.profiles_data.get("profiles", {}):
            script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
            reports = discover_reports(script_dir)
            if reports:
                latest = reports[0]
                # Extract pass/warn/fail counts from summary
                _summary = latest.get("summary", {})
                _pass_c = _summary.get("pass", 0) if isinstance(_summary, dict) else 0
                _warn_c = _summary.get("warn", 0) if isinstance(_summary, dict) else 0
                _fail_c = _summary.get("fail", 0) if isinstance(_summary, dict) else 0
                # Get env label from profile data
                _prof = self.profiles_data["profiles"].get(active, {})
                _flat = profile_to_form(_prof)
                _env_label = _flat.get("CUSTOMER_ENV_LABEL", "")
                self.profiles_data["profiles"][active]["_last_run"] = {
                    "grade": latest.get("grade", "?"),
                    "score": latest.get("score", 0),
                    "date": latest.get("date_str", ""),
                    "report_path": latest.get("path_json", ""),
                    "pass": _pass_c,
                    "warn": _warn_c,
                    "fail": _fail_c,
                    "env_label": _env_label,
                }
                save_profiles(self.profiles_data)
                grade_str = latest.get("grade", "?")
                score_str = latest.get("score", 0)
                _audit_log(self.current_user["username"], "HEALTHCHECK_COMPLETED",
                           f"{active} grade={grade_str} score={score_str} rc={return_code}")

        # Auto-cleanup old reports
        try:
            script_dir_c = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
            flat_c = profile_to_form(self.profiles_data["profiles"].get(active, {})) if active else {}
            ret_days = int(flat_c.get("REPORT_RETENTION_DAYS", 30) or 30)
            cleaned = cleanup_old_reports(script_dir_c, ret_days)
            if cleaned > 0:
                _audit_log(self.current_user["username"], "REPORTS_CLEANED", f"{cleaned} report(s)")
        except Exception as e:  # noqa: E722
            logger.debug("Suppressed: %s", e)

        # Send notifications
        try:
            if active and active in self.profiles_data.get("profiles", {}):
                flat_n = profile_to_form(self.profiles_data["profiles"][active])
                grade_n = self.profiles_data["profiles"][active].get("_last_run", {}).get("grade", "?")
                score_n = self.profiles_data["profiles"][active].get("_last_run", {}).get("score", 0)
                threading.Thread(
                    target=send_run_notifications,
                    args=(flat_n, grade_n, score_n, active),
                    daemon=True,
                ).start()
        except Exception as e:  # noqa: E722
            logger.debug("Suppressed: %s", e)

        # Record usage event (partner ecosystem tracking)
        if _HAS_USAGE_TRACKER:
            try:
                script_dir_u = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
                partner_id = self._license_info.get("partner_id", "")
                # Resolve client for this profile
                u_client_id = ""
                u_client_name = ""
                if _HAS_CLIENT_MGR and active:
                    cl = client_mgr.get_client_for_profile(script_dir_u, active)
                    if cl:
                        u_client_id = cl.get("id", "")
                        u_client_name = cl.get("name", "")
                lr = self.profiles_data["profiles"].get(active, {}).get("_last_run", {})
                usage_tracker.record_health_check_run(
                    script_dir=script_dir_u,
                    partner_id=partner_id,
                    client_id=u_client_id,
                    client_name=u_client_name,
                    profile_name=active or "",
                    duration_seconds=elapsed,
                    grade=lr.get("grade", ""),
                    score=lr.get("score", 0),
                    run_mode="full",
                    user=self.current_user.get("username", ""),
                    report_path=lr.get("report_path", ""),
                )
            except Exception as e:  # noqa: E722
                logger.debug("Suppressed: %s", e)

        # Show report buttons
        self._show_report_buttons()

    def _show_report_buttons(self):
        """Show buttons to open generated reports."""
        if not hasattr(self, "report_buttons_frame"):
            return
        for w in self.report_buttons_frame.winfo_children():
            w.destroy()

        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        reports = discover_reports(script_dir)
        if not reports:
            return

        latest = reports[0]
        ct_bg = self._get_color("CONTENT_BG")
        brand = self._get_color("BRAND_BLUE")

        tk.Label(
            self.report_buttons_frame, text="Open Report:",
            bg=ct_bg, fg=self._get_color("TEXT_PRIMARY"),
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 10))

        btn_kw = dict(
            bg="#1A3A5C", fg="white", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=8, pady=3, cursor="hand2",
        )

        for label, key in [("TXT", "path_txt"), ("HTML", "path_html"), ("JSON", "path_json"),
                           ("CSV", "path_csv"), ("MD", "path_md")]:
            path = latest.get(key)
            if path and os.path.isfile(path):
                def make_open(p=path):
                    def open_file():
                        try:
                            os.startfile(p)
                        except Exception as e:  # noqa: E722
                            messagebox.showerror("Error", f"Could not open: {p}")
                    return open_file
                tk.Button(
                    self.report_buttons_frame, text=f"[{label}]", command=make_open(path), **btn_kw,
                ).pack(side="left", padx=3)

    def _stop_run(self):
        """Stop the running script."""
        if self.process:
            self._write_terminal("\n[GUI] Stopping...\n", "warn")
            try:
                self.process.terminate()
            except Exception as e:  # noqa: E722
                logger.debug("Suppressed: %s", e)
            # Grace period then kill
            def force_kill():
                if self.process and self.process.poll() is None:
                    try:
                        self.process.kill()
                    except Exception as e:  # noqa: E722
                        logger.debug("Suppressed: %s", e)
                    self._write_terminal("[GUI] Force killed.\n", "fail")
            self._after(2000, force_kill)

    # ── RUN HISTORY DASHBOARD ─────────────────────────────────────────────

    def _show_run_history(self):
        """Show run history with score trend chart and statistics."""
        self.current_view = "run_history"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")

        self._make_header("Run History")

        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        reports = discover_reports(script_dir)

        if not reports:
            tk.Label(self.content, text="No run history available.",
                     bg=ct_bg, fg=text_s, font=("Segoe UI", 14)).pack(pady=50)
            tk.Label(self.content, text="Run a health check to start tracking history.",
                     bg=ct_bg, fg=text_s, font=("Segoe UI", 10)).pack()
            return

        # Scrollable frame
        canvas_outer = tk.Canvas(self.content, bg=ct_bg, highlightthickness=0)
        vscroll = ttk.Scrollbar(self.content, orient="vertical", command=canvas_outer.yview)
        scroll_frame = tk.Frame(canvas_outer, bg=ct_bg)
        scroll_frame.bind("<Configure>", lambda e: canvas_outer.configure(scrollregion=canvas_outer.bbox("all")))
        _win_id = canvas_outer.create_window((0, 0), window=scroll_frame, anchor="nw", tags="scroll_win")

        def _resize(event):
            canvas_outer.itemconfig("scroll_win", width=event.width)
        canvas_outer.bind("<Configure>", _resize)
        canvas_outer.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas_outer.pack(fill="both", expand=True)

        def _on_wheel(event):
            canvas_outer.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas_outer.bind("<Enter>", lambda e: canvas_outer.bind_all("<MouseWheel>", _on_wheel))
        canvas_outer.bind("<Leave>", lambda e: canvas_outer.unbind_all("<MouseWheel>"))

        # ── Statistics card ──
        scores = [r.get("score", 0) for r in reports]
        grades = [r.get("grade", "?") for r in reports]
        latest = reports[0]
        avg_score = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
        worst_score = min(scores) if scores else 0
        trend_str = ""
        if len(scores) >= 2:
            diff = scores[0] - scores[1]
            trend_str = f"+{diff}" if diff >= 0 else str(diff)

        stat_card = tk.Frame(scroll_frame, bg=card_bg, bd=1, relief="solid")
        stat_card.pack(fill="x", padx=30, pady=(10, 5))
        tk.Label(stat_card, text="Statistics", font=("Segoe UI", 12, "bold"),
                 fg=brand, bg=card_bg).pack(anchor="w", padx=15, pady=(10, 5))

        stats_row = tk.Frame(stat_card, bg=card_bg)
        stats_row.pack(fill="x", padx=15, pady=(0, 10))
        stat_items = [
            ("Total Runs", str(len(reports))),
            ("Latest", f"{latest.get('grade', '?')} ({latest.get('score', 0)}%)"),
            ("Trend", trend_str or "N/A"),
            ("Average", f"{avg_score:.1f}%"),
            ("Best", f"{best_score}%"),
            ("Worst", f"{worst_score}%"),
        ]
        for label, val in stat_items:
            sf = tk.Frame(stats_row, bg=card_bg)
            sf.pack(side="left", padx=10, expand=True)
            tk.Label(sf, text=label, font=("Segoe UI", 8), fg=text_s, bg=card_bg).pack()
            tk.Label(sf, text=val, font=("Segoe UI", 14, "bold"), fg=text_p, bg=card_bg).pack()

        # ── Score trend chart ──
        chart_card = tk.Frame(scroll_frame, bg=card_bg, bd=1, relief="solid")
        chart_card.pack(fill="x", padx=30, pady=5)
        tk.Label(chart_card, text="Score Trend", font=("Segoe UI", 12, "bold"),
                 fg=brand, bg=card_bg).pack(anchor="w", padx=15, pady=(10, 5))

        chart_w, chart_h = 800, 300
        pad_l, pad_r, pad_t, pad_b = 50, 20, 20, 40
        chart = tk.Canvas(chart_card, width=chart_w, height=chart_h, bg=card_bg,
                          highlightthickness=0)
        chart.pack(padx=15, pady=(0, 15))

        # Sorted chronologically (oldest first)
        sorted_reports = list(reversed(reports))
        n = len(sorted_reports)
        if n < 1:
            return

        plot_w = chart_w - pad_l - pad_r
        plot_h = chart_h - pad_t - pad_b

        # Grade zone shading
        zones = [(90, 100, "#E8F5E9"), (80, 90, "#F1F8E9"), (70, 80, "#FFFDE7"),
                 (60, 70, "#FFF3E0"), (0, 60, "#FFEBEE")]
        for lo, hi, color in zones:
            y1 = pad_t + plot_h - (hi / 100 * plot_h)
            y2 = pad_t + plot_h - (lo / 100 * plot_h)
            chart.create_rectangle(pad_l, y1, pad_l + plot_w, y2, fill=color, outline="")

        # Grid lines
        for pct in [20, 40, 60, 80, 100]:
            y = pad_t + plot_h - (pct / 100 * plot_h)
            chart.create_line(pad_l, y, pad_l + plot_w, y, fill="#DDD", dash=(2, 2))
            chart.create_text(pad_l - 5, y, text=f"{pct}%", anchor="e",
                              font=("Segoe UI", 8), fill=text_s)

        # Plot points
        points = []
        for i, r in enumerate(sorted_reports):
            x = pad_l + (i / max(n - 1, 1)) * plot_w
            sc = r.get("score", 0)
            y = pad_t + plot_h - (sc / 100 * plot_h)
            points.append((x, y, r))

        # Area fill
        if len(points) >= 2:
            area_pts = [(pad_l, pad_t + plot_h)]
            area_pts += [(px, py) for px, py, _ in points]
            area_pts.append((pad_l + plot_w, pad_t + plot_h))
            flat_pts = [c for p in area_pts for c in p]
            chart.create_polygon(flat_pts, fill="#D6EAF8", outline="")

        # Line
        if len(points) >= 2:
            line_pts = [(px, py) for px, py, _ in points]
            flat_line = [c for p in line_pts for c in p]
            chart.create_line(flat_line, fill=brand, width=2, smooth=True)

        # Dots with grade colors
        for px, py, r in points:
            g = r.get("grade", "?")
            color = GRADE_COLORS.get(g, "#888")
            chart.create_oval(px - 5, py - 5, px + 5, py + 5, fill=color, outline="white", width=2)

        # X-axis labels (show up to 8)
        step = max(1, n // 8)
        for i in range(0, n, step):
            x = pad_l + (i / max(n - 1, 1)) * plot_w
            ds = sorted_reports[i].get("date_str", "")
            short = ds[:10] if len(ds) >= 10 else ds
            chart.create_text(x, chart_h - 5, text=short, anchor="s",
                              font=("Segoe UI", 7), fill=text_s, angle=0)

        # ── Grade distribution ──
        dist_card = tk.Frame(scroll_frame, bg=card_bg, bd=1, relief="solid")
        dist_card.pack(fill="x", padx=30, pady=5)
        tk.Label(dist_card, text="Grade Distribution", font=("Segoe UI", 12, "bold"),
                 fg=brand, bg=card_bg).pack(anchor="w", padx=15, pady=(10, 5))

        dist_row = tk.Frame(dist_card, bg=card_bg)
        dist_row.pack(fill="x", padx=15, pady=(0, 10))
        for g in ["A", "B+", "B", "C", "D", "F"]:
            count = grades.count(g)
            gf = tk.Frame(dist_row, bg=card_bg)
            gf.pack(side="left", padx=8, expand=True)
            color = GRADE_COLORS.get(g, "#888")
            tk.Label(gf, text=g, font=("Segoe UI", 14, "bold"), fg=color, bg=card_bg).pack()
            tk.Label(gf, text=str(count), font=("Segoe UI", 10), fg=text_p, bg=card_bg).pack()

        # Bottom padding
        tk.Frame(scroll_frame, bg=ct_bg, height=30).pack()

    def _cleanup_reports_manual(self):
        """Manual cleanup of old reports with confirmation dialog."""
        active = self.profile_var.get()
        flat = {}
        if active and active in self.profiles_data.get("profiles", {}):
            flat = profile_to_form(self.profiles_data["profiles"][active])
        ret_days = int(flat.get("REPORT_RETENTION_DAYS", 30) or 30)
        if not messagebox.askyesno("Cleanup Reports",
                                   f"Delete reports older than {ret_days} days?\n\nThis cannot be undone."):
            return
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        cleaned = cleanup_old_reports(script_dir, ret_days)
        _audit_log(self.current_user["username"], "REPORTS_CLEANED_MANUAL", f"{cleaned} report(s)")
        messagebox.showinfo("Cleanup", f"Deleted {cleaned} old report set(s).")
        self._show_reports()

    # ── REPORTS VIEW ─────────────────────────────────────────────────────

    def _show_reports(self):
        self.current_view = "reports"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")
        success = self._get_color("SUCCESS")
        error = self._get_color("ERROR")
        warning = self._get_color("WARNING")

        header = self._make_header("Reports")
        if self.current_user.get("role") == "admin":
            tk.Button(header, text="Cleanup Old Reports", command=self._cleanup_reports_manual,
                      bg="#1A3A5C", fg="white", font=("Segoe UI", 9, "bold"),
                      relief="flat", padx=10, pady=3, cursor="hand2").pack(side="right")

        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        reports = discover_reports(script_dir)

        if not reports:
            tk.Label(
                self.content, text="No reports found.",
                bg=ct_bg, fg=text_s, font=("Segoe UI", 14),
            ).pack(pady=50)
            tk.Label(
                self.content,
                text=f"Reports are discovered from:\n{script_dir}",
                bg=ct_bg, fg=text_s, font=("Segoe UI", 10), justify="center",
            ).pack()
            return

        # Scrollable list
        canvas = tk.Canvas(self.content, bg=ct_bg, highlightthickness=0)
        vscroll = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=ct_bg)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="scroll_win")

        def _resize(event):
            canvas.itemconfig("scroll_win", width=event.width)
        canvas.bind("<Configure>", _resize)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        def _on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_wheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        for r in reports:
            grade = r.get("grade", "?")
            score = r.get("score", 0)
            date_str = r.get("date_str", "")
            summary = r.get("summary", {})
            grade_color = GRADE_COLORS.get(grade, "#888888")

            card = tk.Frame(scroll_frame, bg=card_bg, bd=1, relief="solid")
            card.pack(fill="x", padx=30, pady=5)

            # Top row: grade badge + info + buttons
            top = tk.Frame(card, bg=card_bg)
            top.pack(fill="x", padx=15, pady=10)

            # Small grade badge
            badge = tk.Canvas(top, width=50, height=50, bg=card_bg, highlightthickness=0)
            badge.pack(side="left", padx=(0, 15))
            badge.create_oval(5, 5, 45, 45, fill=grade_color, outline="")
            badge.create_text(25, 25, text=grade, fill="white", font=("Segoe UI", 16, "bold"))

            # Info
            info = tk.Frame(top, bg=card_bg)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(
                info, text=f"Score: {score}%  |  {date_str}",
                bg=card_bg, fg=text_p, font=("Segoe UI", 11, "bold"),
            ).pack(anchor="w")

            total = summary.get("total", 0)
            passed = summary.get("passed", 0)
            warnings_count = summary.get("warnings", 0)
            failed = summary.get("failed", 0)
            tk.Label(
                info, text=f"P:{passed}  W:{warnings_count}  F:{failed}  T:{total}",
                bg=card_bg, fg=text_s, font=("Segoe UI", 9),
            ).pack(anchor="w")

            # Open buttons
            btns = tk.Frame(top, bg=card_bg)
            btns.pack(side="right")

            btn_kw = dict(
                bg="#1A3A5C", fg="white", font=("Segoe UI", 9, "bold"),
                relief="flat", padx=6, pady=2, cursor="hand2",
            )

            for label, key in [("TXT", "path_txt"), ("HTML", "path_html"),
                               ("JSON", "path_json"), ("CSV", "path_csv"), ("MD", "path_md")]:
                path = r.get(key)
                if path and os.path.isfile(path):
                    def make_open(p=path):
                        def open_file():
                            try:
                                os.startfile(p)
                            except Exception as e:  # noqa: E722
                                messagebox.showerror("Error", f"Could not open: {p}")
                        return open_file
                    tk.Button(btns, text=label, command=make_open(path), **btn_kw).pack(side="left", padx=2)

        # Bottom padding
        tk.Frame(scroll_frame, bg=ct_bg, height=30).pack()

    # ── USER MANAGEMENT VIEW ────────────────────────────────────────────

    def _show_users(self):
        self.current_view = "users"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")
        border = self._get_color("BORDER")
        error_c = self._get_color("ERROR")

        self._make_header("User Management")

        users_data = _load_users()
        users = users_data.get("users", {})

        # Existing users list
        list_card = self._make_card(self.content)
        tk.Label(
            list_card, text=f"User Accounts ({len(users)})", bg=card_bg, fg=text_p,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        for ukey, urec in users.items():
            row = tk.Frame(list_card, bg=card_bg, bd=1, relief="solid",
                           highlightbackground=border, highlightthickness=1)
            row.pack(fill="x", padx=15, pady=2)

            info = tk.Frame(row, bg=card_bg)
            info.pack(side="left", fill="x", expand=True, padx=10, pady=6)

            display = urec.get("display_name", ukey)
            role = urec.get("role", "operator")
            created = urec.get("created", "")[:10]
            role_color = "#27AE60" if role == "admin" else "#F39C12"

            name_frame = tk.Frame(info, bg=card_bg)
            name_frame.pack(anchor="w")
            tk.Label(name_frame, text=display, bg=card_bg, fg=text_p,
                     font=("Segoe UI", 11, "bold")).pack(side="left")
            tk.Label(name_frame, text=f"  {role.upper()}", bg=card_bg, fg=role_color,
                     font=("Segoe UI", 9, "bold")).pack(side="left")

            tk.Label(info, text=f"Created: {created}", bg=card_bg, fg=text_s,
                     font=("Segoe UI", 9)).pack(anchor="w")

            btn_frame = tk.Frame(row, bg=card_bg)
            btn_frame.pack(side="right", padx=10, pady=6)

            # Don't allow deleting yourself
            is_self = ukey == self.current_user["username"].lower()
            if not is_self:
                tk.Button(
                    btn_frame, text="Remove",
                    command=lambda k=ukey, d=display: self._remove_user(k, d),
                    bg=error_c, fg="white", font=("Segoe UI", 9),
                    relief="flat", padx=8, pady=2, cursor="hand2",
                ).pack(side="right", padx=(5, 0))

            # Toggle role button (not for yourself)
            if not is_self:
                new_role = "admin" if role == "operator" else "operator"
                tk.Button(
                    btn_frame, text=f"Make {new_role.title()}",
                    command=lambda k=ukey, r=new_role: self._change_user_role(k, r),
                    bg="#1A3A5C", fg="white", font=("Segoe UI", 9),
                    relief="flat", padx=8, pady=2, cursor="hand2",
                ).pack(side="right")

            # Reset password
            tk.Button(
                btn_frame, text="Reset Password",
                command=lambda k=ukey, d=display: self._reset_user_password(k, d),
                bg="#1A3A5C", fg="white", font=("Segoe UI", 9),
                relief="flat", padx=8, pady=2, cursor="hand2",
            ).pack(side="right", padx=(0, 5))

        # Add new user card
        add_card = self._make_card(self.content)
        tk.Label(
            add_card, text="Add New User", bg=card_bg, fg=text_p,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        row1 = tk.Frame(add_card, bg=card_bg)
        row1.pack(fill="x", padx=15, pady=(2, 2))
        tk.Label(row1, text="Username:", bg=card_bg, fg=text_p,
                 font=("Segoe UI", 10), width=10, anchor="w").pack(side="left")
        self._new_user_var = tk.StringVar()
        tk.Entry(row1, textvariable=self._new_user_var, font=("Segoe UI", 10),
                 bd=1, relief="solid").pack(side="left", fill="x", expand=True)

        row2 = tk.Frame(add_card, bg=card_bg)
        row2.pack(fill="x", padx=15, pady=(2, 2))
        tk.Label(row2, text="Password:", bg=card_bg, fg=text_p,
                 font=("Segoe UI", 10), width=10, anchor="w").pack(side="left")
        self._new_user_pw_var = tk.StringVar()
        tk.Entry(row2, textvariable=self._new_user_pw_var, show="*",
                 font=("Segoe UI", 10), bd=1, relief="solid").pack(side="left", fill="x", expand=True)

        row3 = tk.Frame(add_card, bg=card_bg)
        row3.pack(fill="x", padx=15, pady=(2, 2))
        tk.Label(row3, text="Role:", bg=card_bg, fg=text_p,
                 font=("Segoe UI", 10), width=10, anchor="w").pack(side="left")
        self._new_user_role_var = tk.StringVar(value="operator")
        ttk.Combobox(
            row3, textvariable=self._new_user_role_var,
            values=["operator", "admin"], state="readonly", width=15,
        ).pack(side="left")

        btn_row = tk.Frame(add_card, bg=card_bg)
        btn_row.pack(fill="x", padx=15, pady=(5, 10))
        tk.Button(
            btn_row, text="Add User", command=self._add_user,
            bg=brand, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=15, pady=4, cursor="hand2",
        ).pack(side="left")

    def _add_user(self):
        uname = self._new_user_var.get().strip()
        pw = self._new_user_pw_var.get()
        role = self._new_user_role_var.get()
        if not uname:
            messagebox.showwarning("Missing", "Username is required.")
            return
        if len(pw) < 4:
            messagebox.showwarning("Missing", "Password must be at least 4 characters.")
            return
        users_data = _load_users()
        if uname.lower() in users_data.get("users", {}):
            messagebox.showwarning("Exists", f"User '{uname}' already exists.")
            return
        users_data["users"][uname.lower()] = {
            "display_name": uname,
            "password_hash": _hash_password(pw, uname.lower()),
            "role": role,
            "created": datetime.now(timezone.utc).isoformat(),
        }
        _save_users(users_data)
        _audit_log(self.current_user["username"], "USER_CREATED", f"{uname} as {role}")
        messagebox.showinfo("Created", f"User '{uname}' created as {role}.")
        self._show_users()

    def _remove_user(self, ukey: str, display: str):
        if not messagebox.askyesno("Remove User", f"Remove user '{display}'?\nThis cannot be undone."):
            return
        users_data = _load_users()
        users_data.get("users", {}).pop(ukey, None)
        _save_users(users_data)
        _audit_log(self.current_user["username"], "USER_REMOVED", display)
        self._show_users()

    def _change_user_role(self, ukey: str, new_role: str):
        users_data = _load_users()
        if ukey in users_data.get("users", {}):
            users_data["users"][ukey]["role"] = new_role
            _save_users(users_data)
            _audit_log(self.current_user["username"], "USER_ROLE_CHANGED", f"{ukey} -> {new_role}")
        self._show_users()

    def _reset_user_password(self, ukey: str, display: str):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Reset Password — {display}")
        dialog.geometry("350x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        frame = tk.Frame(dialog, padx=15, pady=10)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text=f"New password for {display}:", font=("Segoe UI", 10)).pack(anchor="w")
        pw_var = tk.StringVar()
        pw_entry = tk.Entry(frame, textvariable=pw_var, show="*", font=("Segoe UI", 11))
        pw_entry.pack(fill="x", pady=(5, 5))
        err_label = tk.Label(frame, text="", fg="red", font=("Segoe UI", 9))
        err_label.pack()

        def _save():
            pw = pw_var.get()
            if len(pw) < 4:
                err_label.config(text="Password must be at least 4 characters")
                return
            users_data = _load_users()
            if ukey in users_data.get("users", {}):
                users_data["users"][ukey]["password_hash"] = _hash_password(pw, ukey)
                users_data["users"][ukey]["password_changed"] = datetime.now(timezone.utc).isoformat()
                _save_users(users_data)
            dialog.destroy()
            _audit_log(self.current_user["username"], "USER_PASSWORD_RESET", display)
            messagebox.showinfo("Done", f"Password reset for '{display}'.")

        tk.Button(frame, text="Reset Password", command=_save,
                  bg="#0077B6", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=10, pady=3).pack()
        pw_entry.focus_set()
        pw_entry.bind("<Return>", lambda e: _save())

    # ── SUPPRESSIONS VIEW ─────────────────────────────────────────────────

    def _get_known_issues_path(self) -> str:
        """Return path to known-issues.json alongside the script."""
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        return os.path.join(script_dir, "known-issues.json")

    def _load_known_issues(self) -> list:
        """Load suppression rules from known-issues.json."""
        path = self._get_known_issues_path()
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("suppress", [])
        except Exception as e:  # noqa: E722
            return []

    def _save_known_issues(self, rules: list):
        """Save suppression rules to known-issues.json."""
        path = self._get_known_issues_path()
        data = {"suppress": rules}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ── CLIENTS VIEW (partner ecosystem) ────────────────────────────────

    def _show_clients(self):
        """Show the client management view."""
        if not _HAS_CLIENT_MGR:
            return
        self.current_view = "clients"
        self._clear_content()
        self._make_header("Clients")
        ct_bg = self._get_color("CONTENT_BG")
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        is_admin = self.current_user.get("role") == "admin"

        # Check if we should show detail view
        if hasattr(self, "_selected_client_id") and self._selected_client_id:
            cid = self._selected_client_id
            self._selected_client_id = None
            view = client_mgr.build_client_detail_view(
                self.content, script_dir, cid, self.profiles_data,
                self.current_colors,
                on_back_callback=self._show_clients,
                on_edit_callback=self._edit_client,
                on_assign_callback=self._assign_profile_dialog,
                on_unassign_callback=self._unassign_profile,
                is_admin=is_admin,
            )
            view.pack(fill="both", expand=True)
            return

        view = client_mgr.build_client_list_view(
            self.content, script_dir, self.profiles_data,
            self.current_colors,
            on_select_callback=self._select_client,
            on_create_callback=self._create_client_dialog,
            is_admin=is_admin,
        )
        view.pack(fill="both", expand=True)

    def _select_client(self, client_id: str):
        self._selected_client_id = client_id
        self._show_clients()

    def _create_client_dialog(self):
        if not _HAS_CLIENT_MGR or not _HAS_LICENSE_MGR:
            return
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        # Check client limit
        current_count = len(client_mgr.list_clients(script_dir, status_filter="active"))
        allowed, msg = license_mgr.can_add_client(script_dir, self.settings, current_count)
        if not allowed:
            messagebox.showwarning("Client Limit", msg)
            return

        def _on_save(form_data):
            client_mgr.create_client(script_dir, **form_data)
            _audit_log(self.current_user["username"], "CLIENT_CREATED", form_data.get("name", ""))

        client_mgr.build_client_form_dialog(
            self.root, script_dir, self.current_colors,
            on_save_callback=_on_save,
        )
        self._show_clients()

    def _edit_client(self, client_id: str):
        if not _HAS_CLIENT_MGR:
            return
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)

        def _on_save(form_data):
            client_mgr.update_client(script_dir, client_id, **form_data)
            _audit_log(self.current_user["username"], "CLIENT_UPDATED", form_data.get("name", ""))

        client_mgr.build_client_form_dialog(
            self.root, script_dir, self.current_colors,
            client_id=client_id, on_save_callback=_on_save,
        )
        self._selected_client_id = client_id
        self._show_clients()

    def _assign_profile_dialog(self, client_id: str):
        if not _HAS_CLIENT_MGR:
            return
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        all_profiles = list(self.profiles_data.get("profiles", {}).keys())
        unassigned = client_mgr.get_unassigned_profiles(script_dir, all_profiles)
        if not unassigned:
            messagebox.showinfo("Assign Profile", "All profiles are already assigned to clients.")
            return
        # Simple selection dialog
        choice = simpledialog.askstring(
            "Assign Profile",
            f"Available profiles:\n{', '.join(unassigned)}\n\nEnter profile name to assign:",
            parent=self.root,
        )
        if choice and choice.strip() in unassigned:
            client_mgr.assign_profile_to_client(script_dir, client_id, choice.strip())
            _audit_log(self.current_user["username"], "PROFILE_ASSIGNED",
                       f"{choice.strip()} -> {client_id}")
            self._selected_client_id = client_id
            self._show_clients()
        elif choice:
            messagebox.showwarning("Assign Profile", f"Profile '{choice}' not found in unassigned list.")

    def _unassign_profile(self, client_id: str, profile_name: str):
        if not _HAS_CLIENT_MGR:
            return
        if not messagebox.askyesno("Unassign Profile",
                                   f"Remove '{profile_name}' from this client?"):
            return
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        client_mgr.unassign_profile_from_client(script_dir, client_id, profile_name)
        _audit_log(self.current_user["username"], "PROFILE_UNASSIGNED",
                   f"{profile_name} from {client_id}")
        self._selected_client_id = client_id
        self._show_clients()

    # ── USAGE & BILLING VIEW (partner ecosystem) ────────────────────────

    def _show_usage(self):
        """Show the usage tracking and billing dashboard."""
        if not _HAS_USAGE_TRACKER:
            return
        self.current_view = "usage"
        self._clear_content()
        self._make_header("Usage & Billing")
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)

        view = usage_tracker.build_usage_dashboard(
            self.content, script_dir, self.current_colors,
            on_export_csv_callback=self._export_usage_csv,
            on_export_json_callback=self._export_usage_json,
            on_export_billing_callback=self._export_billing_summary,
        )
        view.pack(fill="both", expand=True)

    def _export_usage_csv(self):
        if not _HAS_USAGE_TRACKER:
            return
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        path = filedialog.asksaveasfilename(
            title="Export Usage CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"vcf-usage-{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv",
        )
        if path:
            usage_tracker.export_usage_csv(script_dir, output_path=path)
            _audit_log(self.current_user["username"], "USAGE_EXPORTED_CSV", path)
            messagebox.showinfo("Export", f"Usage data exported to:\n{path}")

    def _export_usage_json(self):
        if not _HAS_USAGE_TRACKER:
            return
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        path = filedialog.asksaveasfilename(
            title="Export Usage JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile=f"vcf-usage-{datetime.now(timezone.utc).strftime('%Y%m%d')}.json",
        )
        if path:
            usage_tracker.export_usage_json(script_dir, output_path=path)
            _audit_log(self.current_user["username"], "USAGE_EXPORTED_JSON", path)
            messagebox.showinfo("Export", f"Usage data exported to:\n{path}")

    def _export_billing_summary(self):
        if not _HAS_USAGE_TRACKER:
            return
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        now = datetime.now(timezone.utc)
        # Default to current month
        start = now.strftime("%Y-%m-01")
        end = now.strftime("%Y-%m-%d")
        path = filedialog.asksaveasfilename(
            title="Export Billing Summary",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"vcf-billing-{start}-to-{end}.csv",
        )
        if path:
            usage_tracker.export_billing_summary_csv(script_dir, start, end, output_path=path)
            _audit_log(self.current_user["username"], "BILLING_EXPORTED", path)
            messagebox.showinfo("Export", f"Billing summary exported to:\n{path}")

    # ── SUPPRESSIONS VIEW ───────────────────────────────────────────────

    def _show_suppressions(self):
        self.current_view = "suppressions"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")
        border = self._get_color("BORDER")

        self._make_header("Suppression Rules")

        # Description card
        desc_card = self._make_card(self.content)
        tk.Label(
            desc_card, text="Known Issue Suppressions", bg=card_bg, fg=text_p,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 2))
        tk.Label(
            desc_card, bg=card_bg, fg=text_s, font=("Segoe UI", 9), anchor="w",
            justify="left", wraplength=700,
            text=(
                "Suppression rules let you mute known issues during health checks. "
                "When a check result matches a pattern below, FAIL results are downgraded "
                "to WARN, and WARN results are downgraded to PASS. The pattern is matched "
                "as a case-insensitive substring against the check message.\n\n"
                "Rules are stored in known-issues.json alongside the health check script."
            ),
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Existing rules list
        rules = self._load_known_issues()
        self._suppression_rules = list(rules)  # working copy

        list_card = self._make_card(self.content)
        tk.Label(
            list_card, text=f"Active Rules ({len(rules)})", bg=card_bg, fg=text_p,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Scrollable frame for rules
        list_outer = tk.Frame(list_card, bg=card_bg)
        list_outer.pack(fill="both", padx=15, pady=(0, 10))

        self._rule_widgets_frame = tk.Frame(list_outer, bg=card_bg)
        self._rule_widgets_frame.pack(fill="x")

        self._render_rule_list()

        # Add new rule card
        add_card = self._make_card(self.content)
        tk.Label(
            add_card, text="Add New Rule", bg=card_bg, fg=text_p,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Pattern row
        pat_row = tk.Frame(add_card, bg=card_bg)
        pat_row.pack(fill="x", padx=15, pady=(2, 2))
        tk.Label(pat_row, text="Pattern:", bg=card_bg, fg=text_p,
                 font=("Segoe UI", 10), width=8, anchor="w").pack(side="left")
        self._new_pattern_var = tk.StringVar()
        tk.Entry(
            pat_row, textvariable=self._new_pattern_var, font=("Segoe UI", 10),
            bd=1, relief="solid",
        ).pack(side="left", fill="x", expand=True)

        # Note row
        note_row = tk.Frame(add_card, bg=card_bg)
        note_row.pack(fill="x", padx=15, pady=(2, 5))
        tk.Label(note_row, text="Note:", bg=card_bg, fg=text_p,
                 font=("Segoe UI", 10), width=8, anchor="w").pack(side="left")
        self._new_note_var = tk.StringVar()
        tk.Entry(
            note_row, textvariable=self._new_note_var, font=("Segoe UI", 10),
            bd=1, relief="solid",
        ).pack(side="left", fill="x", expand=True)

        # Add button
        btn_row = tk.Frame(add_card, bg=card_bg)
        btn_row.pack(fill="x", padx=15, pady=(2, 10))
        tk.Button(
            btn_row, text="Add Suppression Rule", command=self._add_suppression_rule,
            bg=brand, fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", padx=15, pady=4, cursor="hand2",
        ).pack(side="left")

        # File info
        path_label = tk.Label(
            self.content, text=f"File: {self._get_known_issues_path()}",
            bg=ct_bg, fg=text_s, font=("Segoe UI", 8),
        )
        path_label.pack(anchor="w", padx=30, pady=(10, 0))

    def _render_rule_list(self):
        """Render the list of suppression rules."""
        for w in self._rule_widgets_frame.winfo_children():
            w.destroy()
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        border = self._get_color("BORDER")
        error_c = self._get_color("ERROR")

        if not self._suppression_rules:
            tk.Label(
                self._rule_widgets_frame,
                text="No suppression rules configured. All checks will report normally.",
                bg=card_bg, fg=text_s, font=("Segoe UI", 10, "italic"),
            ).pack(anchor="w", pady=5)
            return

        for idx, rule in enumerate(self._suppression_rules):
            row = tk.Frame(self._rule_widgets_frame, bg=card_bg, bd=1,
                           relief="solid", highlightbackground=border, highlightthickness=1)
            row.pack(fill="x", pady=2)

            info = tk.Frame(row, bg=card_bg)
            info.pack(side="left", fill="x", expand=True, padx=10, pady=6)

            pattern = rule.get("pattern", "")
            note = rule.get("note", "")
            tk.Label(
                info, text=f"Pattern:  {pattern}", bg=card_bg, fg=text_p,
                font=("Consolas", 10), anchor="w",
            ).pack(anchor="w")
            tk.Label(
                info, text=f"Note:  {note}", bg=card_bg, fg=text_s,
                font=("Segoe UI", 9), anchor="w",
            ).pack(anchor="w")

            tk.Button(
                row, text="Remove",
                command=lambda i=idx: self._remove_suppression_rule(i),
                bg=error_c, fg="white", font=("Segoe UI", 9),
                relief="flat", padx=8, pady=2, cursor="hand2",
            ).pack(side="right", padx=10, pady=6)

    def _add_suppression_rule(self):
        """Add a new suppression rule and save."""
        pattern = self._new_pattern_var.get().strip()
        note = self._new_note_var.get().strip()
        if not pattern:
            messagebox.showwarning("Missing Pattern",
                                   "Enter a pattern to match against check messages.")
            return
        if not note:
            note = "Suppressed via GUI"
        self._suppression_rules.append({"pattern": pattern, "note": note})
        try:
            self._save_known_issues(self._suppression_rules)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save known-issues.json:\n{e}")
            self._suppression_rules.pop()
            return
        _audit_log(self.current_user["username"], "SUPPRESSION_ADDED", pattern)
        self._new_pattern_var.set("")
        self._new_note_var.set("")
        self._show_suppressions()  # Refresh full view to update count

    def _remove_suppression_rule(self, index: int):
        """Remove a suppression rule by index and save."""
        if index < 0 or index >= len(self._suppression_rules):
            return
        rule = self._suppression_rules[index]
        if not messagebox.askyesno(
            "Remove Rule",
            f"Remove this suppression rule?\n\nPattern: {rule.get('pattern', '')}\n"
            f"Note: {rule.get('note', '')}",
        ):
            return
        pattern = rule.get("pattern", "")
        self._suppression_rules.pop(index)
        try:
            self._save_known_issues(self._suppression_rules)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save known-issues.json:\n{e}")
            return
        _audit_log(self.current_user["username"], "SUPPRESSION_REMOVED", pattern)
        self._show_suppressions()  # Refresh full view to update count

    # ── SETTINGS VIEW ────────────────────────────────────────────────────

    def _show_settings(self):
        self.current_view = "settings"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")
        border = self._get_color("BORDER")

        self._make_header("Settings")

        # Scrollable area for all settings
        canvas = tk.Canvas(self.content, bg=ct_bg, highlightthickness=0)
        vscroll = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=ct_bg)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", tags="scroll_win")

        def _resize(event):
            canvas.itemconfig("scroll_win", width=event.width)
        canvas.bind("<Configure>", _resize)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        def _on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_wheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        def _make_settings_card(parent, **pack_kw) -> tk.Frame:
            c = tk.Frame(parent, bg=card_bg, bd=1, relief="solid",
                         highlightbackground=border, highlightthickness=1)
            c.pack(fill="x", padx=30, pady=5, **pack_kw)
            return c

        # Script path
        card = _make_settings_card(scroll_frame)
        tk.Label(card, text="Script Path", bg=card_bg, fg=text_p, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
        tk.Label(card, text="Path to vcf-health-check.sh", bg=card_bg, fg=text_s, font=("Segoe UI", 9)).pack(anchor="w", padx=15)
        sp_row = tk.Frame(card, bg=card_bg)
        sp_row.pack(fill="x", padx=15, pady=(5, 10))
        self.script_path_var = tk.StringVar(value=self.script_path)
        tk.Entry(sp_row, textvariable=self.script_path_var, font=("Segoe UI", 10), bd=1, relief="solid").pack(side="left", fill="x", expand=True)
        tk.Button(sp_row, text="Browse", command=self._browse_script,
                  bg=brand, fg="white", font=("Segoe UI", 9), relief="flat", padx=8, cursor="hand2").pack(side="left", padx=(5, 0))
        tk.Button(sp_row, text="Auto-detect", command=self._autodetect_script,
                  bg="#1A3A5C", fg="white", font=("Segoe UI", 9), relief="flat", padx=8, cursor="hand2").pack(side="left", padx=(5, 0))

        # Bash path
        card2 = _make_settings_card(scroll_frame)
        tk.Label(card2, text="Bash Path", bg=card_bg, fg=text_p, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
        tk.Label(card2, text="Path to bash.exe (Git Bash, WSL, etc.)", bg=card_bg, fg=text_s, font=("Segoe UI", 9)).pack(anchor="w", padx=15)
        bp_row = tk.Frame(card2, bg=card_bg)
        bp_row.pack(fill="x", padx=15, pady=(5, 10))
        self.bash_path_var = tk.StringVar(value=self.bash_path)
        tk.Entry(bp_row, textvariable=self.bash_path_var, font=("Segoe UI", 10), bd=1, relief="solid").pack(side="left", fill="x", expand=True)
        tk.Button(bp_row, text="Browse", command=self._browse_bash,
                  bg=brand, fg="white", font=("Segoe UI", 9), relief="flat", padx=8, cursor="hand2").pack(side="left", padx=(5, 0))
        tk.Button(bp_row, text="Auto-detect", command=self._autodetect_bash,
                  bg="#1A3A5C", fg="white", font=("Segoe UI", 9), relief="flat", padx=8, cursor="hand2").pack(side="left", padx=(5, 0))

        # Dark mode
        card3 = _make_settings_card(scroll_frame)
        tk.Label(card3, text="Appearance", bg=card_bg, fg=text_p, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
        dm_row = tk.Frame(card3, bg=card_bg)
        dm_row.pack(fill="x", padx=15, pady=(5, 10))
        self.dark_mode_var = tk.StringVar(value=self.settings.get("dark_mode", "system"))
        for val, label in [("system", "System"), ("light", "Light"), ("dark", "Dark")]:
            tk.Radiobutton(dm_row, text=label, variable=self.dark_mode_var, value=val,
                           bg=card_bg, fg=text_p, font=("Segoe UI", 10),
                           activebackground=card_bg, selectcolor=card_bg,
                           command=self._on_dark_mode_setting_change).pack(side="left", padx=10)

        # --- Security Settings ---
        sec_card = _make_settings_card(scroll_frame)
        tk.Label(sec_card, text="Security", bg=card_bg, fg=text_p,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 5))

        # Password expiry
        pe_row = tk.Frame(sec_card, bg=card_bg)
        pe_row.pack(fill="x", padx=15, pady=3)
        tk.Label(pe_row, text="Password Expiry (days):", bg=card_bg, fg=text_p,
                 font=("Segoe UI", 10), width=25, anchor="w").pack(side="left")
        self._pw_expiry_var = tk.StringVar(value=str(self.settings.get("password_expiry_days", 90)))
        tk.Entry(pe_row, textvariable=self._pw_expiry_var, font=("Segoe UI", 10),
                 bd=1, relief="solid", width=8).pack(side="left")
        tk.Label(pe_row, text="(0 = disabled)", bg=card_bg, fg=text_s,
                 font=("Segoe UI", 8)).pack(side="left", padx=5)

        # Session timeout
        st_row = tk.Frame(sec_card, bg=card_bg)
        st_row.pack(fill="x", padx=15, pady=(3, 10))
        tk.Label(st_row, text="Session Timeout (minutes):", bg=card_bg, fg=text_p,
                 font=("Segoe UI", 10), width=25, anchor="w").pack(side="left")
        self._timeout_var = tk.StringVar(value=str(self.settings.get("session_timeout_minutes", 30)))
        tk.Entry(st_row, textvariable=self._timeout_var, font=("Segoe UI", 10),
                 bd=1, relief="solid", width=8).pack(side="left")
        tk.Label(st_row, text="(0 = disabled)", bg=card_bg, fg=text_s,
                 font=("Segoe UI", 8)).pack(side="left", padx=5)

        # --- License ---
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        if _HAS_LICENSE_MGR:
            license_mgr.build_license_settings_card(
                scroll_frame, self.settings, script_dir,
                self.current_colors,
                activate_callback=self._activate_partner_license,
                admin_bypass_callback=self._admin_bypass_login,
            )
        else:
            lic_card = _make_settings_card(scroll_frame)
            tk.Label(lic_card, text="License", bg=card_bg, fg=text_p,
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 5))

            license_info = _check_license(self.settings)
            lic_mode = license_info.get("mode", "unlicensed")
            if lic_mode == "licensed":
                status_text = f"Licensed to: {license_info.get('customer', 'N/A')} — expires {license_info.get('expires', 'N/A')}"
                status_color = self._get_color("SUCCESS")
            elif lic_mode == "grace":
                status_text = f"License expired (grace period) — {license_info.get('customer', 'N/A')}"
                status_color = self._get_color("WARNING")
            else:
                status_text = "No License — A valid license is required"
                status_color = self._get_color("ERROR")

            tk.Label(lic_card, text=f"Status: {status_text}", bg=card_bg, fg=status_color,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=15, pady=(0, 5))

            lk_row = tk.Frame(lic_card, bg=card_bg)
            lk_row.pack(fill="x", padx=15, pady=(3, 5))
            tk.Label(lk_row, text="License Key:", bg=card_bg, fg=text_p,
                     font=("Segoe UI", 10), anchor="w").pack(side="left")
            self._license_key_var = tk.StringVar(value=self.settings.get("license_key", ""))
            tk.Entry(lk_row, textvariable=self._license_key_var, font=("Consolas", 10),
                     bd=1, relief="solid", width=35).pack(side="left", padx=(5, 0))
            tk.Button(lk_row, text="Activate", command=self._activate_license,
                      bg=brand, fg="white", font=("Segoe UI", 9, "bold"),
                      relief="flat", padx=10, cursor="hand2").pack(side="left", padx=(5, 0))

            tk.Label(lic_card, text="Format: VCF-XXXXX-XXXXX-XXXXX-XXXXX", bg=card_bg, fg=text_s,
                     font=("Segoe UI", 8)).pack(anchor="w", padx=15, pady=(0, 10))

        # --- LDAP / Active Directory ---
        if _ldap_available():
            ldap_card = _make_settings_card(scroll_frame)
            tk.Label(ldap_card, text="LDAP / Active Directory", bg=card_bg, fg=text_p,
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
            tk.Label(ldap_card, text="Optional AD/LDAP authentication (requires ldap3 package)",
                     bg=card_bg, fg=text_s, font=("Segoe UI", 9)).pack(anchor="w", padx=15)

            self._ldap_enabled_var = tk.BooleanVar(value=self.settings.get("ldap_enabled", False))
            tk.Checkbutton(ldap_card, text="Enable LDAP Authentication",
                           variable=self._ldap_enabled_var,
                           bg=card_bg, fg=text_p, font=("Segoe UI", 10),
                           activebackground=card_bg, selectcolor=card_bg).pack(anchor="w", padx=15, pady=3)

            ldap_fields = [
                ("Server:", "ldap_server", ""),
                ("Port:", "ldap_port", "389"),
                ("Base DN:", "ldap_base_dn", ""),
                ("Bind DN:", "ldap_bind_dn", ""),
                ("Bind Password:", "ldap_bind_password", ""),
                ("User Filter:", "ldap_user_filter", "(sAMAccountName={username})"),
                ("Admin Group DN:", "ldap_admin_group", ""),
                ("Operator Group DN:", "ldap_operator_group", ""),
            ]

            self._ldap_server_var = tk.StringVar(value=self.settings.get("ldap_server", ""))
            self._ldap_port_var = tk.StringVar(value=str(self.settings.get("ldap_port", "389")))
            self._ldap_ssl_var = tk.BooleanVar(value=self.settings.get("ldap_use_ssl", False))
            self._ldap_base_dn_var = tk.StringVar(value=self.settings.get("ldap_base_dn", ""))
            self._ldap_bind_dn_var = tk.StringVar(value=self.settings.get("ldap_bind_dn", ""))
            try:
                _ldap_pw = _b64_decode(self.settings.get("ldap_bind_password", ""))
            except RuntimeError:
                _ldap_pw = ""
            self._ldap_bind_pw_var = tk.StringVar(value=_ldap_pw)
            self._ldap_filter_var = tk.StringVar(value=self.settings.get("ldap_user_filter", "(sAMAccountName={username})"))
            self._ldap_admin_group_var = tk.StringVar(value=self.settings.get("ldap_admin_group", ""))
            self._ldap_operator_group_var = tk.StringVar(value=self.settings.get("ldap_operator_group", ""))

            ldap_vars = [
                ("Server:", self._ldap_server_var, False),
                ("Port:", self._ldap_port_var, False),
                ("Base DN:", self._ldap_base_dn_var, False),
                ("Bind DN:", self._ldap_bind_dn_var, False),
                ("Bind Password:", self._ldap_bind_pw_var, True),
                ("User Filter:", self._ldap_filter_var, False),
                ("Admin Group:", self._ldap_admin_group_var, False),
                ("Operator Group:", self._ldap_operator_group_var, False),
            ]

            for lbl, var, is_pw in ldap_vars:
                lr = tk.Frame(ldap_card, bg=card_bg)
                lr.pack(fill="x", padx=15, pady=2)
                tk.Label(lr, text=lbl, bg=card_bg, fg=text_p,
                         font=("Segoe UI", 10), width=16, anchor="w").pack(side="left")
                kw = dict(textvariable=var, font=("Segoe UI", 10), bd=1, relief="solid")
                if is_pw:
                    kw["show"] = "*"
                tk.Entry(lr, **kw).pack(side="left", fill="x", expand=True)

            ssl_row = tk.Frame(ldap_card, bg=card_bg)
            ssl_row.pack(fill="x", padx=15, pady=2)
            tk.Checkbutton(ssl_row, text="Use SSL (LDAPS)", variable=self._ldap_ssl_var,
                           bg=card_bg, fg=text_p, font=("Segoe UI", 10),
                           activebackground=card_bg, selectcolor=card_bg).pack(side="left")

            test_row = tk.Frame(ldap_card, bg=card_bg)
            test_row.pack(fill="x", padx=15, pady=(5, 10))
            tk.Button(test_row, text="Test Connection", command=self._test_ldap_connection,
                      bg="#1A3A5C", fg="white", font=("Segoe UI", 9, "bold"),
                      relief="flat", padx=10, cursor="hand2").pack(side="left")
            self._ldap_test_label = tk.Label(test_row, text="", bg=card_bg,
                                             font=("Segoe UI", 9))
            self._ldap_test_label.pack(side="left", padx=10)

        # Detection info
        card4 = _make_settings_card(scroll_frame)
        tk.Label(card4, text="Detection Info", bg=card_bg, fg=text_p, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(10, 5))
        detected_bash = find_bash() or "Not found"
        detected_script = find_script() or "Not found"
        tk.Label(card4, text=f"Application directory: {_SCRIPT_DIR}", bg=card_bg, fg=text_s, font=("Segoe UI", 9)).pack(anchor="w", padx=15)
        tk.Label(card4, text=f"Auto-detected bash: {detected_bash}", bg=card_bg, fg=text_s, font=("Segoe UI", 9)).pack(anchor="w", padx=15)
        tk.Label(card4, text=f"Auto-detected script: {detected_script}", bg=card_bg, fg=text_s, font=("Segoe UI", 9)).pack(anchor="w", padx=15)
        tk.Label(card4, text=f"LDAP library (ldap3): {'Available' if _ldap_available() else 'Not installed'}",
                 bg=card_bg, fg=text_s, font=("Segoe UI", 9)).pack(anchor="w", padx=15, pady=(0, 10))

        # --- Billing Rates (if usage tracker available) ---
        if _HAS_USAGE_TRACKER:
            usage_tracker.build_billing_config_card(
                scroll_frame, script_dir, self.current_colors,
                save_callback=self._save_billing_rates,
            )

        # Save button
        save_frame = tk.Frame(scroll_frame, bg=ct_bg)
        save_frame.pack(fill="x", padx=30, pady=20)
        tk.Button(
            save_frame, text="Save Settings", command=self._apply_settings,
            bg=brand, fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", padx=20, pady=8, cursor="hand2",
        ).pack(side="left")

        # Bottom padding
        tk.Frame(scroll_frame, bg=ct_bg, height=30).pack()

    def _activate_license(self):
        """Validate and activate a legacy license key (fallback when partner module absent)."""
        key = self._license_key_var.get().strip()
        if not key:
            messagebox.showwarning("License", "Enter a license key.")
            return
        info = _validate_license_key(key)
        if not info.get("valid"):
            messagebox.showerror("Invalid Key", "The license key is not valid.")
            return
        if info.get("expired") and not info.get("grace"):
            messagebox.showerror("Expired Key",
                f"This license key has expired.\nCustomer: {info.get('customer', 'N/A')}\n"
                f"Expired: {info.get('expires', 'N/A')}")
            return
        self.settings["license_key"] = key
        self._save_settings()
        self._license_info = _check_license(self.settings)
        self._update_title_bar()
        _audit_log(self.current_user["username"], "LICENSE_ACTIVATED", info.get("customer", ""))
        messagebox.showinfo("License Activated",
            f"License activated successfully!\n\n"
            f"Customer: {info.get('customer', 'N/A')}\n"
            f"Expires: {info.get('expires', 'N/A')}\n"
            f"Max Profiles: {info.get('max_profiles', 'Unlimited') or 'Unlimited'}")
        self._show_settings()

    def _activate_partner_license(self, key: str):
        """Activate a partner license key via the license manager module."""
        if not key:
            messagebox.showwarning("License", "Enter a license key.")
            return
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        result = license_mgr.activate_partner_license(script_dir, key)
        if not result.get("success"):
            messagebox.showerror("Invalid Key", result.get("error", "The license key is not valid."))
            return
        # Also store in settings for backward compat
        self.settings["license_key"] = key
        self._save_settings()
        info = result["info"]
        self._license_info = license_mgr.check_partner_license(script_dir, self.settings)
        self._update_title_bar()
        _audit_log(self.current_user["username"], "PARTNER_LICENSE_ACTIVATED",
                   f"{info.get('partner_name', '')} tier={info.get('tier', '')}")
        tier_label = license_mgr.TIER_DEFINITIONS.get(info.get("tier", ""), {}).get("label", "")
        messagebox.showinfo("License Activated",
            f"Partner license activated!\n\n"
            f"Partner: {info.get('partner_name', 'N/A')}\n"
            f"Tier: {tier_label}\n"
            f"Expires: {info.get('expires', 'N/A')}\n"
            f"Environments: {info.get('max_environments', 0) or 'Unlimited'}\n"
            f"Clients: {info.get('max_clients', 0) or 'Unlimited'}")
        self._show_settings()

    def _admin_bypass_login(self, password: str):
        """Authenticate admin bypass for unlicensed access."""
        if not password:
            messagebox.showwarning("Admin Bypass", "Enter the admin password.")
            return
        if not _HAS_LICENSE_MGR:
            return
        if license_mgr.verify_admin_backdoor(password):
            self.settings["_admin_bypass"] = True
            self._save_settings()
            script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
            self._license_info = license_mgr.check_partner_license(script_dir, self.settings)
            self._update_title_bar()
            _audit_log(self.current_user["username"], "ADMIN_BYPASS_ACTIVATED", "")
            messagebox.showinfo("Admin Bypass", "Admin bypass activated. Full access granted.")
            self._show_settings()
        else:
            _audit_log(self.current_user["username"], "ADMIN_BYPASS_FAILED", "")
            messagebox.showerror("Admin Bypass", "Invalid admin password.")

    def _update_title_bar(self):
        """Update the window title bar with current license status."""
        lic_mode = self._license_info.get("mode", "unlicensed")
        unlicensed_tag = " [UNLICENSED]" if lic_mode == "unlicensed" else ""
        grace_tag = " [LICENSE EXPIRING]" if lic_mode == "grace" else ""
        bypass_tag = " [ADMIN]" if lic_mode == "admin_bypass" else ""
        self.root.title(f"{APP_TITLE} — Virtual Control LLC — "
                        f"{self.current_user['username']} ({self.current_user['role']})"
                        f"{unlicensed_tag}{grace_tag}{bypass_tag}")

    def _save_billing_rates(self, rates: dict):
        """Save billing rates via usage tracker module."""
        if not _HAS_USAGE_TRACKER:
            return
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        usage_tracker.set_billing_rates(script_dir, rates)
        _audit_log(self.current_user["username"], "BILLING_RATES_UPDATED", str(rates))
        messagebox.showinfo("Billing Rates", "Billing rates saved successfully.")

    def _test_ldap_connection(self):
        """Test LDAP connection with current settings."""
        settings = {
            "ldap_server": self._ldap_server_var.get(),
            "ldap_port": self._ldap_port_var.get(),
            "ldap_use_ssl": self._ldap_ssl_var.get(),
            "ldap_base_dn": self._ldap_base_dn_var.get(),
            "ldap_bind_dn": self._ldap_bind_dn_var.get(),
            "ldap_bind_password": _b64_encode(self._ldap_bind_pw_var.get()),
        }
        result = _ldap_test_connection(settings)
        if result.startswith("SUCCESS"):
            color = self._get_color("SUCCESS")
        else:
            color = self._get_color("ERROR")
        if hasattr(self, "_ldap_test_label"):
            self._ldap_test_label.configure(text=result, fg=color)

    def _browse_script(self):
        path = filedialog.askopenfilename(
            title="Select vcf-health-check.sh",
            filetypes=[("Shell scripts", "*.sh"), ("All files", "*.*")],
            initialdir=str(_SCRIPT_DIR),
        )
        if path:
            self.script_path_var.set(path)

    def _autodetect_script(self):
        detected = find_script()
        if detected:
            self.script_path_var.set(detected)
            messagebox.showinfo("Detected", f"Found: {detected}")
        else:
            messagebox.showwarning(
                "Not Found",
                f"Could not find vcf-health-check.sh.\n\n"
                f"Searched in:\n"
                f"  {_SCRIPT_DIR}\n"
                f"  {_SCRIPT_DIR.parent}\n"
                f"  {Path.cwd()}\n\n"
                f"Place the .sh file next to the application,\n"
                f"or use Browse to select it manually.",
            )

    def _browse_bash(self):
        path = filedialog.askopenfilename(
            title="Select bash executable",
            filetypes=[("Executables", "*.exe"), ("All files", "*.*")],
        )
        if path:
            self.bash_path_var.set(path)

    def _autodetect_bash(self):
        detected = find_bash()
        if detected:
            self.bash_path_var.set(detected)
            messagebox.showinfo("Detected", f"Found: {detected}")
        else:
            messagebox.showwarning("Not Found", "Could not auto-detect bash.\nInstall Git for Windows or WSL.")

    def _on_dark_mode_setting_change(self):
        new_val = self.dark_mode_var.get()
        self.settings["dark_mode"] = new_val
        if new_val == "system":
            want_dark = self._detect_system_dark_mode()
        elif new_val == "dark":
            want_dark = True
        else:
            want_dark = False
        if want_dark != self.is_dark_mode:
            self._save_settings()
            self._toggle_dark_mode()

    def _apply_settings(self):
        self.script_path = self.script_path_var.get()
        self.bash_path = self.bash_path_var.get()
        # Gather extended settings
        if hasattr(self, "_pw_expiry_var"):
            try:
                self.settings["password_expiry_days"] = int(self._pw_expiry_var.get() or "90")
            except ValueError:
                self.settings["password_expiry_days"] = 90
        if hasattr(self, "_timeout_var"):
            try:
                self.settings["session_timeout_minutes"] = int(self._timeout_var.get() or "30")
            except ValueError:
                self.settings["session_timeout_minutes"] = 30
        # LDAP settings
        if hasattr(self, "_ldap_enabled_var"):
            self.settings["ldap_enabled"] = self._ldap_enabled_var.get()
            self.settings["ldap_server"] = self._ldap_server_var.get()
            self.settings["ldap_port"] = self._ldap_port_var.get()
            self.settings["ldap_use_ssl"] = self._ldap_ssl_var.get()
            self.settings["ldap_base_dn"] = self._ldap_base_dn_var.get()
            self.settings["ldap_bind_dn"] = self._ldap_bind_dn_var.get()
            raw_pw = self._ldap_bind_pw_var.get()
            if raw_pw:
                self.settings["ldap_bind_password"] = _b64_encode(raw_pw)
            self.settings["ldap_user_filter"] = self._ldap_filter_var.get()
            self.settings["ldap_admin_group"] = self._ldap_admin_group_var.get()
            self.settings["ldap_operator_group"] = self._ldap_operator_group_var.get()
        self._save_settings()
        # Restart timeout checker with new settings
        self._start_timeout_checker()
        _audit_log(self.current_user["username"], "SETTINGS_CHANGED")
        messagebox.showinfo("Saved", "Settings saved successfully.")

    # ── PROFILE MANAGEMENT ───────────────────────────────────────────────

    def _load_profile(self):
        """Load selected profile into form (if Environment view is active)."""
        name = self.profile_var.get()
        if not name or name not in self.profiles_data.get("profiles", {}):
            return
        self.profiles_data["active_profile"] = name
        save_profiles(self.profiles_data)
        # Re-populate form if on environment view
        if self.current_view == "environment":
            self._show_environment()

    def _save_profile(self):
        """Save current form values to the active profile."""
        name = self.profile_var.get()
        if not name:
            self._new_profile()
            return

        if self.form_vars:
            flat, run_options = self._get_form_values()
        else:
            messagebox.showinfo("Info", "Go to Environment tab first to edit values.")
            return

        profile = form_to_profile(name, flat, run_options)
        # Preserve _last_run if it exists
        existing = self.profiles_data.get("profiles", {}).get(name, {})
        if "_last_run" in existing:
            profile["_last_run"] = existing["_last_run"]
        self.profiles_data.setdefault("profiles", {})[name] = profile
        self.profiles_data["active_profile"] = name
        save_profiles(self.profiles_data)
        self._refresh_profile_dropdown()
        _audit_log(self.current_user["username"], "PROFILE_SAVED", name)
        messagebox.showinfo("Saved", f"Profile '{name}' saved.")
        self._snapshot_form()

    def _delete_profile(self):
        name = self.profile_var.get()
        if not name:
            return
        if not messagebox.askyesno("Delete Profile", f"Delete profile '{name}'?"):
            return
        self.profiles_data.get("profiles", {}).pop(name, None)
        if self.profiles_data.get("active_profile") == name:
            self.profiles_data["active_profile"] = ""
        save_profiles(self.profiles_data)
        _audit_log(self.current_user["username"], "PROFILE_DELETED", name)
        self._refresh_profile_dropdown()

    def _new_profile(self):
        # Check license limits — partner module or legacy
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        if _HAS_LICENSE_MGR:
            count = len(self.profiles_data.get("profiles", {}))
            allowed, msg = license_mgr.can_add_environment(script_dir, self.settings, count)
            if not allowed:
                messagebox.showwarning("License Required", msg)
                return
        else:
            license_info = _check_license(self.settings)
            if license_info.get("mode") != "licensed" and license_info.get("mode") != "grace":
                messagebox.showwarning("License Required",
                    "A valid license is required to create profiles.\n"
                    "Activate a license key in Settings.")
                return
        name = simpledialog.askstring("New Profile", "Profile name:", parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()
        if name in self.profiles_data.get("profiles", {}):
            messagebox.showwarning("Exists", f"Profile '{name}' already exists.")
            return
        # Create empty profile
        flat = {}
        for _sk, _sl, _exp, fields in FIELD_SECTIONS:
            for var, _lbl, _ft, default in fields:
                flat[var] = default
        run_options = {k: False for k, _f, _d in RUN_OPTIONS}
        profile = form_to_profile(name, flat, run_options)
        self.profiles_data.setdefault("profiles", {})[name] = profile
        self.profiles_data["active_profile"] = name
        save_profiles(self.profiles_data)
        _audit_log(self.current_user["username"], "PROFILE_CREATED", name)
        self._refresh_profile_dropdown()
        self.profile_var.set(name)
        if self.current_view == "environment":
            self._show_environment()

    def _import_env(self):
        """Import a .env file into a new profile."""
        filepath = filedialog.askopenfilename(
            title="Import .env file",
            filetypes=[("Env files", "*.env"), ("All files", "*.*")],
            initialdir=str(_SCRIPT_DIR),
        )
        if not filepath:
            return

        parsed = parse_env_file(filepath)
        if not parsed:
            messagebox.showwarning("Empty", "No variables found in file.")
            return

        # Ask for profile name
        basename = os.path.splitext(os.path.basename(filepath))[0]
        name = simpledialog.askstring(
            "Profile Name", "Name for imported profile:",
            parent=self.root, initialvalue=basename,
        )
        if not name or not name.strip():
            return
        name = name.strip()

        # Build flat dict from parsed env
        flat = {}
        for _sk, _sl, _exp, fields in FIELD_SECTIONS:
            for var, _lbl, _ft, default in fields:
                flat[var] = parsed.get(var, default)

        run_options = {k: False for k, _f, _d in RUN_OPTIONS}
        profile = form_to_profile(name, flat, run_options)
        self.profiles_data.setdefault("profiles", {})[name] = profile
        self.profiles_data["active_profile"] = name
        save_profiles(self.profiles_data)
        self._refresh_profile_dropdown()
        self.profile_var.set(name)
        if self.current_view == "environment":
            self._show_environment()
        _audit_log(self.current_user["username"], "PROFILE_IMPORTED", f"{name} from .env")
        messagebox.showinfo("Imported", f"Profile '{name}' imported from:\n{filepath}")

    def _export_env(self):
        """Export active profile to a .env file."""
        name = self.profile_var.get()
        if not name or name not in self.profiles_data.get("profiles", {}):
            messagebox.showwarning("No Profile", "Select or create a profile first.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export .env file",
            defaultextension=".env",
            filetypes=[("Env files", "*.env"), ("All files", "*.*")],
            initialdir=str(_SCRIPT_DIR),
            initialfile=f"vcf-health-check-{name.lower().replace(' ', '-')}.env",
        )
        if not filepath:
            return

        flat = profile_to_form(self.profiles_data["profiles"][name])
        flat.pop("run_options", None)
        export_env_file(filepath, flat)
        _audit_log(self.current_user["username"], "PROFILE_EXPORTED", f"{name} to .env")
        messagebox.showinfo("Exported", f"Exported to:\n{filepath}")

    def _reset_profile(self):
        """Reset current profile to defaults (clears all fields)."""
        name = self.profile_var.get()
        if not name:
            messagebox.showwarning("No Profile", "Select or create a profile first.")
            return
        if not messagebox.askyesno(
            "Reset Profile",
            f"Reset '{name}' to defaults?\n\n"
            "This will clear all endpoints, credentials, and settings.\n"
            "This cannot be undone.",
        ):
            return
        flat = {}
        for _sk, _sl, _exp, fields in FIELD_SECTIONS:
            for var, _lbl, _ft, default in fields:
                flat[var] = default
        run_options = {k: False for k, _f, _d in RUN_OPTIONS}
        profile = form_to_profile(name, flat, run_options)
        self.profiles_data["profiles"][name] = profile
        save_profiles(self.profiles_data)
        if self.current_view == "environment":
            self._show_environment()
        _audit_log(self.current_user["username"], "PROFILE_RESET", name)
        messagebox.showinfo("Reset", f"Profile '{name}' has been reset to defaults.")

    def _export_json_profile(self):
        """Export active profile as a shareable JSON file."""
        name = self.profile_var.get()
        if not name or name not in self.profiles_data.get("profiles", {}):
            messagebox.showwarning("No Profile", "Select or create a profile first.")
            return
        filepath = filedialog.asksaveasfilename(
            title="Export Profile as JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(_SCRIPT_DIR),
            initialfile=f"vcf-profile-{name.lower().replace(' ', '-')}.json",
        )
        if not filepath:
            return
        profile = self.profiles_data["profiles"][name]
        export_data = {
            "_format": "vcf-health-check-profile",
            "_version": PROFILES_VERSION,
            "_exported": datetime.now(timezone.utc).isoformat(),
            "name": name,
            "profile": profile,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        _audit_log(self.current_user["username"], "PROFILE_EXPORTED", f"{name} to JSON")
        messagebox.showinfo("Exported", f"Profile '{name}' exported to:\n{filepath}")

    def _import_json_profile(self):
        """Import a JSON profile file, optionally overwriting an existing profile."""
        filepath = filedialog.askopenfilename(
            title="Import JSON Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(_SCRIPT_DIR),
        )
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read JSON file:\n{e}")
            return

        # Validate format
        if not isinstance(data, dict) or "profile" not in data:
            messagebox.showerror(
                "Invalid Format",
                "This JSON file is not a valid VCF Health Check profile export.\n\n"
                "Expected a file exported via 'Export JSON' from this application.",
            )
            return

        suggested_name = data.get("name", "Imported")
        name = simpledialog.askstring(
            "Profile Name",
            "Name for imported profile:\n\n"
            "(Use an existing name to overwrite that profile)",
            parent=self.root,
            initialvalue=suggested_name,
        )
        if not name or not name.strip():
            return
        name = name.strip()

        overwriting = name in self.profiles_data.get("profiles", {})
        if overwriting:
            if not messagebox.askyesno(
                "Overwrite Profile",
                f"Profile '{name}' already exists.\n\nOverwrite it with the imported data?",
            ):
                return

        profile = data["profile"]
        profile["name"] = name
        self.profiles_data.setdefault("profiles", {})[name] = profile
        self.profiles_data["active_profile"] = name
        save_profiles(self.profiles_data)
        self._refresh_profile_dropdown()
        self.profile_var.set(name)
        if self.current_view == "environment":
            self._show_environment()
        action = "overwritten" if overwriting else "imported"
        _audit_log(self.current_user["username"], "PROFILE_IMPORTED", f"{name} from JSON ({action})")
        messagebox.showinfo("Imported", f"Profile '{name}' {action} from:\n{filepath}")

    def _refresh_profile_dropdown(self):
        """Refresh the profile dropdown values."""
        names = list(self.profiles_data.get("profiles", {}).keys())
        self.profile_dropdown["values"] = names
        active = self.profiles_data.get("active_profile", "")
        if active and active in names:
            self.profile_var.set(active)
        elif names:
            self.profile_var.set(names[0])
        else:
            self.profile_var.set("")

    # ── AUDIT LOG VIEW ──────────────────────────────────────────────────

    def _show_audit_log(self):
        self.current_view = "audit"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")
        term_bg = self._get_color("TERMINAL_BG")
        term_fg = self._get_color("TERMINAL_FG")

        self._make_header("Audit Log")

        # Controls row
        ctrl = tk.Frame(self.content, bg=ct_bg)
        ctrl.pack(fill="x", padx=30, pady=(0, 10))

        tk.Label(ctrl, text="Filter:", bg=ct_bg, fg=text_p,
                 font=("Segoe UI", 10)).pack(side="left")
        self._audit_filter_var = tk.StringVar()
        filter_entry = tk.Entry(ctrl, textvariable=self._audit_filter_var,
                                font=("Segoe UI", 10), bd=1, relief="solid", width=30)
        filter_entry.pack(side="left", padx=(5, 10))
        filter_entry.bind("<Return>", lambda e: self._refresh_audit_log())

        tk.Button(ctrl, text="Search", command=self._refresh_audit_log,
                  bg=brand, fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, cursor="hand2").pack(side="left", padx=(0, 5))
        tk.Button(ctrl, text="Refresh", command=self._refresh_audit_log,
                  bg="#1A3A5C", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, cursor="hand2").pack(side="left", padx=(0, 5))
        tk.Button(ctrl, text="Clear Log", command=self._clear_audit_log,
                  bg=self._get_color("ERROR"), fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, cursor="hand2").pack(side="left")
        tk.Button(ctrl, text="Export CSV", command=self._export_audit_csv,
                  bg="#1A3A5C", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", padx=10, cursor="hand2").pack(side="left", padx=(5, 0))

        # Terminal-style log display
        log_frame = tk.Frame(self.content, bg=term_bg, bd=1, relief="solid",
                             highlightbackground=self._get_color("BORDER"), highlightthickness=1)
        log_frame.pack(fill="both", expand=True, padx=30, pady=(0, 15))

        self._audit_text = tk.Text(
            log_frame, bg=term_bg, fg=term_fg,
            font=("Consolas", 9), wrap="none",
            insertbackground=term_fg, relief="flat",
            padx=10, pady=10, state="disabled",
        )
        audit_vscroll = ttk.Scrollbar(log_frame, orient="vertical", command=self._audit_text.yview)
        audit_hscroll = ttk.Scrollbar(log_frame, orient="horizontal", command=self._audit_text.xview)
        self._audit_text.configure(yscrollcommand=audit_vscroll.set, xscrollcommand=audit_hscroll.set)
        audit_vscroll.pack(side="right", fill="y")
        audit_hscroll.pack(side="bottom", fill="x")
        self._audit_text.pack(fill="both", expand=True)

        # Info label
        self._audit_info_label = tk.Label(self.content, text="", bg=ct_bg, fg=text_s,
                                          font=("Segoe UI", 8))
        self._audit_info_label.pack(anchor="w", padx=30)

        self._refresh_audit_log()

    def _refresh_audit_log(self):
        """Reload and display audit log entries."""
        filter_text = self._audit_filter_var.get().strip().lower() if hasattr(self, "_audit_filter_var") else ""
        try:
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []
        except OSError:
            lines = []

        # Apply filter
        if filter_text:
            lines = [l for l in lines if filter_text in l.lower()]

        # Show last 500 lines
        display_lines = lines[-500:]

        self._audit_text.configure(state="normal")
        self._audit_text.delete("1.0", "end")
        for line in display_lines:
            self._audit_text.insert("end", line)
        self._audit_text.see("end")
        self._audit_text.configure(state="disabled")

        total = len(lines)
        shown = len(display_lines)
        info = f"File: {AUDIT_LOG_FILE}  |  Total: {total} entries"
        if shown < total:
            info += f"  |  Showing last {shown}"
        if filter_text:
            info += f"  |  Filter: '{filter_text}'"
        if hasattr(self, "_audit_info_label"):
            self._audit_info_label.configure(text=info)

    def _clear_audit_log(self):
        """Clear the audit log file (admin only, with confirmation)."""
        if not messagebox.askyesno("Clear Audit Log",
                                   "Clear all audit log entries?\n\nThis cannot be undone."):
            return
        try:
            with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
                f.write("")
            _audit_log(self.current_user["username"], "AUDIT_LOG_CLEARED")
            self._refresh_audit_log()
        except OSError as e:
            messagebox.showerror("Error", f"Could not clear audit log:\n{e}")

    def _export_audit_csv(self):
        """Export audit log to CSV file."""
        if not os.path.isfile(AUDIT_LOG_FILE):
            messagebox.showinfo("Export CSV", "No audit log entries to export.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Audit Log as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="vcf-health-audit-export.csv",
        )
        if not path:
            return
        try:
            import csv
            with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as fin:
                lines = fin.readlines()
            with open(path, "w", encoding="utf-8", newline="") as fout:
                writer = csv.writer(fout)
                writer.writerow(["Timestamp", "User", "Action", "Details"])
                for line in lines:
                    parts = line.strip().split(" | ")
                    if len(parts) >= 3:
                        row = parts[:4] if len(parts) >= 4 else parts + [""] * (4 - len(parts))
                        writer.writerow(row)
            _audit_log(self.current_user["username"], "AUDIT_CSV_EXPORTED", path)
            messagebox.showinfo("Export CSV", f"Audit log exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export CSV:\n{e}")

    # ── CHANGE OWN PASSWORD ──────────────────────────────────────────────

    def _change_own_password(self):
        """Dialog for the current user to change their own password."""
        dlg = tk.Toplevel(self.root)
        dlg.title("Change Password")
        dlg.geometry("400x280")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        # Center on parent
        dlg.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 140
        dlg.geometry(f"+{x}+{y}")

        frame = tk.Frame(dlg, padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Change Your Password", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(frame, text=f"User: {self.current_user['username']}", font=("Segoe UI", 9),
                 fg="#666").pack(anchor="w", pady=(0, 10))

        tk.Label(frame, text="Current Password:", font=("Segoe UI", 10)).pack(anchor="w")
        cur_pw_var = tk.StringVar()
        cur_pw_entry = tk.Entry(frame, textvariable=cur_pw_var, show="*", font=("Segoe UI", 11))
        cur_pw_entry.pack(fill="x", pady=(2, 5))

        tk.Label(frame, text="New Password:", font=("Segoe UI", 10)).pack(anchor="w")
        new_pw_var = tk.StringVar()
        new_pw_entry = tk.Entry(frame, textvariable=new_pw_var, show="*", font=("Segoe UI", 11))
        new_pw_entry.pack(fill="x", pady=(2, 5))

        tk.Label(frame, text="Confirm New Password:", font=("Segoe UI", 10)).pack(anchor="w")
        confirm_var = tk.StringVar()
        confirm_entry = tk.Entry(frame, textvariable=confirm_var, show="*", font=("Segoe UI", 11))
        confirm_entry.pack(fill="x", pady=(2, 5))

        err_label = tk.Label(frame, text="", fg="red", font=("Segoe UI", 9))
        err_label.pack()

        def _save():
            uname_key = self.current_user["username"].lower()
            users_data = _load_users()
            user_rec = users_data.get("users", {}).get(uname_key)
            if not user_rec:
                err_label.config(text="User record not found")
                return
            # Verify current password (supports legacy + PBKDF2)
            if not _verify_password(cur_pw_var.get(), user_rec["password_hash"], uname_key):
                err_label.config(text="Current password is incorrect")
                return
            p1 = new_pw_var.get()
            p2 = confirm_var.get()
            if len(p1) < 4:
                err_label.config(text="New password must be at least 4 characters")
                return
            if p1 != p2:
                err_label.config(text="Passwords do not match")
                return
            user_rec["password_hash"] = _hash_password(p1, uname_key)
            user_rec["password_changed"] = datetime.now(timezone.utc).isoformat()
            _save_users(users_data)
            _audit_log(self.current_user["username"], "PASSWORD_CHANGED_SELF")
            dlg.destroy()
            messagebox.showinfo("Password Changed", "Your password has been changed successfully.")

        tk.Button(frame, text="Change Password", command=_save,
                  bg="#0077B6", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=15, pady=3).pack(pady=(5, 0))
        cur_pw_entry.focus_set()
        cur_pw_entry.bind("<Return>", lambda e: new_pw_entry.focus_set())
        new_pw_entry.bind("<Return>", lambda e: confirm_entry.focus_set())
        confirm_entry.bind("<Return>", lambda e: _save())

    # ── SESSION TIMEOUT / AUTO-LOCK ──────────────────────────────────────

    def _setup_activity_tracking(self):
        """Bind events on root to track user activity."""
        for event in ("<Motion>", "<Key>", "<Button>", "<MouseWheel>"):
            self.root.bind_all(event, self._on_activity, add="+")

    def _on_activity(self, event=None):
        """Reset inactivity timer on any user interaction."""
        self._last_activity = time.time()

    def _start_timeout_checker(self):
        """Periodically check for session timeout."""
        # Cancel existing checker if any
        if hasattr(self, "_timeout_after_id") and self._timeout_after_id:
            try:
                self.root.after_cancel(self._timeout_after_id)
            except Exception as e:  # noqa: E722
                logger.debug("Suppressed: %s", e)
            self._timeout_after_id = None

        timeout_min = int(self.settings.get("session_timeout_minutes", 30))
        if timeout_min <= 0:
            return  # Disabled

        elapsed = time.time() - self._last_activity
        if elapsed >= timeout_min * 60:
            self._lock_session()
        else:
            self._timeout_after_id = self.root.after(60000, self._start_timeout_checker)

    def _lock_session(self):
        """Lock the app and require re-authentication."""
        _audit_log(self.current_user["username"], "SESSION_TIMEOUT")
        self.root.withdraw()
        self._show_reauth_dialog()

    def _show_reauth_dialog(self):
        """Show re-authentication dialog for session unlock."""
        dlg = tk.Toplevel()
        dlg.title("Session Locked — Re-authenticate")
        dlg.geometry("420x200")
        dlg.resizable(False, False)
        dlg.attributes("-topmost", True)
        dlg.protocol("WM_DELETE_WINDOW", lambda: self._on_close())

        # Center on screen
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() // 2) - 210
        y = (dlg.winfo_screenheight() // 2) - 100
        dlg.geometry(f"+{x}+{y}")

        frame = tk.Frame(dlg, padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Session Locked", font=("Segoe UI", 14, "bold"),
                 fg="#E74C3C").pack(anchor="w")
        tk.Label(frame, text="Your session has timed out due to inactivity.",
                 font=("Segoe UI", 9), fg="#666").pack(anchor="w", pady=(0, 8))

        user_row = tk.Frame(frame)
        user_row.pack(fill="x", pady=(0, 5))
        tk.Label(user_row, text="User:", font=("Segoe UI", 10), width=10, anchor="w").pack(side="left")
        tk.Label(user_row, text=self.current_user["username"],
                 font=("Segoe UI", 10, "bold")).pack(side="left")

        pw_row = tk.Frame(frame)
        pw_row.pack(fill="x", pady=(0, 5))
        tk.Label(pw_row, text="Password:", font=("Segoe UI", 10), width=10, anchor="w").pack(side="left")
        pw_var = tk.StringVar()
        pw_entry = tk.Entry(pw_row, textvariable=pw_var, show="*", font=("Segoe UI", 11))
        pw_entry.pack(side="left", fill="x", expand=True)

        err_label = tk.Label(frame, text="", fg="red", font=("Segoe UI", 9))
        err_label.pack()

        def _unlock():
            uname_key = self.current_user["username"].lower()
            users_data = _load_users()
            user_rec = users_data.get("users", {}).get(uname_key)
            if not user_rec:
                err_label.config(text="User record not found")
                return
            # Brute-force check
            locked_msg = _check_account_locked(user_rec)
            if locked_msg:
                err_label.config(text=locked_msg)
                return
            if not _verify_password(pw_var.get(), user_rec["password_hash"], uname_key):
                _record_failed_attempt(uname_key, users_data)
                err_label.config(text="Incorrect password")
                pw_var.set("")
                return
            _upgrade_hash_if_legacy(pw_var.get(), user_rec["password_hash"], uname_key, user_rec, users_data)
            _reset_failed_attempts(uname_key, users_data)
            _audit_log(self.current_user["username"], "SESSION_UNLOCKED")
            self._last_activity = time.time()
            dlg.destroy()
            self.root.deiconify()
            self._start_timeout_checker()

        def _cancel():
            dlg.destroy()
            self._on_close()

        btn_row = tk.Frame(frame)
        btn_row.pack(fill="x", pady=(5, 0))
        tk.Button(btn_row, text="Unlock", command=_unlock,
                  bg="#0077B6", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=15, pady=3).pack(side="left")
        tk.Button(btn_row, text="Close App", command=_cancel,
                  font=("Segoe UI", 10), relief="flat", padx=10, pady=3).pack(side="left", padx=(10, 0))

        pw_entry.focus_set()
        pw_entry.bind("<Return>", lambda e: _unlock())

    # ── ABOUT DIALOG ─────────────────────────────────────────────────────

    def _show_about(self):
        """Show About dialog with app info and Virtual Control branding."""
        dlg = tk.Toplevel(self.root)
        dlg.title("About VCF Health Check")
        dlg.geometry("520x500")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        # Center on parent
        dlg.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 260
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 250
        dlg.geometry(f"+{x}+{y}")

        # Banner
        banner = tk.Canvas(dlg, width=520, height=100, highlightthickness=0)
        banner.pack()
        # Gradient
        for i in range(100):
            t = i / 100
            r = int(10 + (0 - 10) * t)
            g = int(31 + (119 - 31) * t)
            b = int(51 + (182 - 51) * t)
            color = f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"
            banner.create_rectangle(0, i, 520, i + 1, fill=color, outline=color)
        banner.create_text(260, 40, text="VCF HEALTH CHECK",
                           font=("Segoe UI", 24, "bold"), fill="white")
        banner.create_text(260, 70, text="VMware Cloud Foundation Environment Monitor",
                           font=("Segoe UI", 10), fill="#A0C8E8")

        frame = tk.Frame(dlg, padx=25, pady=10)
        frame.pack(fill="both", expand=True)

        # Version & copyright
        tk.Label(frame, text=f"Version {APP_VERSION}",
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(frame, text=APP_COPYRIGHT,
                 font=("Segoe UI", 10), fg="#666").pack(anchor="w")
        tk.Label(frame, text="Powered by Virtual Control LLC",
                 font=("Segoe UI", 10, "bold"), fg="#0077B6").pack(anchor="w", pady=(2, 8))

        # License info
        license_info = _check_license(self.settings)
        lic_mode = license_info.get("mode", "trial")
        if lic_mode == "licensed":
            lic_text = f"Licensed to: {license_info.get('customer', 'N/A')}"
            lic_color = "#27AE60"
        elif lic_mode == "grace":
            lic_text = f"License expired (grace period) — {license_info.get('customer', 'N/A')}"
            lic_color = "#F39C12"
        else:
            lic_text = "Trial Mode — limited to 1 profile"
            lic_color = "#E74C3C"
        tk.Label(frame, text=lic_text, font=("Segoe UI", 10, "bold"),
                 fg=lic_color).pack(anchor="w", pady=(0, 8))

        # Separator
        tk.Frame(frame, bg="#D5D8DC", height=1).pack(fill="x", pady=5)

        # System info
        tk.Label(frame, text="System Information",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(5, 3))
        info_items = [
            ("Python", sys.version.split()[0]),
            ("Platform", f"{platform.system()} {platform.release()}"),
            ("Tk Version", str(tk.TkVersion)),
            ("Script", self.script_path or "Not configured"),
            ("Bash", self.bash_path or "Not configured"),
            ("Profiles", str(len(self.profiles_data.get("profiles", {})))),
            ("Users", str(len(_load_users().get("users", {})))),
        ]
        for label, value in info_items:
            row = tk.Frame(frame)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{label}:", font=("Segoe UI", 9, "bold"),
                     width=12, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Segoe UI", 9),
                     fg="#666", wraplength=350, justify="left").pack(side="left")

        # Separator
        tk.Frame(frame, bg="#D5D8DC", height=1).pack(fill="x", pady=8)

        # Contact
        tk.Label(frame, text="Virtual Control LLC",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(frame, text="https://virtualcontrolllc.com",
                 font=("Segoe UI", 9), fg="#0077B6").pack(anchor="w")
        tk.Label(frame, text="mhayes@virtualcontrolllc.com",
                 font=("Segoe UI", 9), fg="#0077B6").pack(anchor="w")
        tk.Label(frame, text="https://valcalepi.github.io/virtualcontrol.github.io/",
                 font=("Segoe UI", 9), fg="#0077B6").pack(anchor="w")

        # Close button
        tk.Button(frame, text="Close", command=dlg.destroy,
                  bg="#0077B6", fg="white", font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=20, pady=5, cursor="hand2").pack(pady=(10, 0))

    # ── ABOUT PAGE (content area) ────────────────────────────────────────

    def _show_about_page(self):
        """Show About info in the main content area (not a popup)."""
        self.current_view = "about"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")

        self._make_header("About")

        # Branding card
        card = self._make_card(self.content)
        tk.Label(card, text="VCF Health Check", font=("Segoe UI", 18, "bold"),
                 fg=brand, bg=card_bg).pack(anchor="w", padx=15, pady=(15, 0))
        tk.Label(card, text="VMware Cloud Foundation Environment Monitor",
                 font=("Segoe UI", 10), fg=text_s, bg=card_bg).pack(anchor="w", padx=15, pady=(2, 0))
        tk.Label(card, text=f"Version {APP_VERSION}", font=("Segoe UI", 12, "bold"),
                 fg=text_p, bg=card_bg).pack(anchor="w", padx=15, pady=(8, 0))
        tk.Label(card, text=APP_COPYRIGHT, font=("Segoe UI", 10),
                 fg=text_s, bg=card_bg).pack(anchor="w", padx=15, pady=(2, 0))
        tk.Label(card, text="Powered by Virtual Control LLC",
                 font=("Segoe UI", 10, "bold"), fg=brand, bg=card_bg).pack(anchor="w", padx=15, pady=(2, 10))

        # License card
        card2 = self._make_card(self.content)
        tk.Label(card2, text="License", font=("Segoe UI", 12, "bold"),
                 fg=text_p, bg=card_bg).pack(anchor="w", padx=15, pady=(10, 5))
        license_info = _check_license(self.settings)
        lic_mode = license_info.get("mode", "trial")
        if lic_mode == "licensed":
            lic_text = f"Licensed to: {license_info.get('customer', 'N/A')}"
            lic_color = "#27AE60"
        elif lic_mode == "grace":
            lic_text = f"License expired (grace period) — {license_info.get('customer', 'N/A')}"
            lic_color = "#F39C12"
        else:
            lic_text = "Trial Mode — limited to 1 profile"
            lic_color = "#E74C3C"
        tk.Label(card2, text=lic_text, font=("Segoe UI", 10, "bold"),
                 fg=lic_color, bg=card_bg).pack(anchor="w", padx=15, pady=(0, 10))

        # System info card
        card3 = self._make_card(self.content)
        tk.Label(card3, text="System Information", font=("Segoe UI", 12, "bold"),
                 fg=text_p, bg=card_bg).pack(anchor="w", padx=15, pady=(10, 5))
        info_items = [
            ("Python", sys.version.split()[0]),
            ("Platform", f"{platform.system()} {platform.release()}"),
            ("Tk Version", str(tk.TkVersion)),
            ("Script", self.script_path or "Not configured"),
            ("Bash", self.bash_path or "Not configured"),
            ("Profiles", str(len(self.profiles_data.get("profiles", {})))),
            ("Users", str(len(_load_users().get("users", {})))),
        ]
        for label, value in info_items:
            row = tk.Frame(card3, bg=card_bg)
            row.pack(fill="x", padx=15, pady=1)
            tk.Label(row, text=f"{label}:", font=("Segoe UI", 9, "bold"),
                     width=12, anchor="w", bg=card_bg, fg=text_p).pack(side="left")
            tk.Label(row, text=value, font=("Segoe UI", 9),
                     fg=text_s, bg=card_bg, wraplength=400, justify="left").pack(side="left")
        tk.Label(card3, text="", bg=card_bg).pack(pady=(0, 5))

        # Contact card
        card4 = self._make_card(self.content)
        tk.Label(card4, text="Virtual Control LLC", font=("Segoe UI", 12, "bold"),
                 fg=text_p, bg=card_bg).pack(anchor="w", padx=15, pady=(10, 3))
        tk.Label(card4, text="https://virtualcontrolllc.com",
                 font=("Segoe UI", 10), fg=brand, bg=card_bg).pack(anchor="w", padx=15)
        tk.Label(card4, text="mhayes@virtualcontrolllc.com",
                 font=("Segoe UI", 10), fg=brand, bg=card_bg).pack(anchor="w", padx=15)
        tk.Label(card4, text="https://valcalepi.github.io/virtualcontrol.github.io/",
                 font=("Segoe UI", 10), fg=brand, bg=card_bg).pack(anchor="w", padx=15, pady=(0, 10))

    # ── HELP PAGE ─────────────────────────────────────────────────────────

    def _show_help(self):
        """Show Help documentation in the main content area."""
        import webbrowser as _wb
        self.current_view = "help"
        self._clear_content()
        ct_bg = self._get_color("CONTENT_BG")
        card_bg = self._get_color("CARD_BG")
        text_p = self._get_color("TEXT_PRIMARY")
        text_s = self._get_color("TEXT_SECONDARY")
        brand = self._get_color("BRAND_BLUE")

        header = self._make_header("Help")

        # Open HTML Help button in header
        html_path = os.path.join(str(_SCRIPT_DIR), "vcf-health-check-help.html")
        if os.path.isfile(html_path):
            def _open_html_help():
                try:
                    os.startfile(html_path)
                except Exception as e:  # noqa: E722
                    _wb.open(f"file:///{html_path.replace(os.sep, '/')}")
            tk.Button(header, text="Open HTML Help", command=_open_html_help,
                      bg=brand, fg="white", font=("Segoe UI", 9, "bold"),
                      relief="flat", padx=10, pady=3, cursor="hand2").pack(side="right")

        # Scrollable frame
        outer = tk.Frame(self.content, bg=ct_bg)
        outer.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        canvas = tk.Canvas(outer, bg=ct_bg, highlightthickness=0)
        vscroll = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=ct_bg)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        _canvas_win_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_wheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        def _section(parent, title, body):
            c = tk.Frame(parent, bg=card_bg, bd=1, relief="solid",
                         highlightbackground=self._get_color("BORDER"), highlightthickness=1)
            c.pack(fill="x", pady=5)
            tk.Label(c, text=title, font=("Segoe UI", 12, "bold"),
                     fg=brand, bg=card_bg).pack(anchor="w", padx=15, pady=(10, 3))
            tk.Label(c, text=body, font=("Segoe UI", 10), fg=text_p,
                     bg=card_bg, justify="left", wraplength=700,
                     anchor="w").pack(anchor="w", padx=15, pady=(0, 10))

        # Update canvas width when resized
        def _on_canvas_resize(event):
            canvas.itemconfig(_canvas_win_id, width=event.width)
        canvas.bind("<Configure>", _on_canvas_resize)

        # ── Welcome ──
        welcome_card = tk.Frame(scroll_frame, bg=brand, bd=0)
        welcome_card.pack(fill="x", pady=(0, 10))
        tk.Label(welcome_card, text="Welcome to VCF Health Check!",
                 font=("Segoe UI", 16, "bold"), fg="white", bg=brand).pack(
                     anchor="w", padx=15, pady=(12, 2))
        tk.Label(welcome_card, text=(
            "This app checks if your computer servers are happy and healthy. "
            "Think of it like a doctor visit, but for big computers!\n\n"
            "Just follow the steps below. Each button on the left side takes you to a different page."),
                 font=("Segoe UI", 10), fg="white", bg=brand,
                 justify="left", wraplength=700).pack(anchor="w", padx=15, pady=(0, 12))

        # ── Step-by-step sections ──

        _section(scroll_frame, "Step 1: Log In",
            "When the app opens, it asks for your username and password.\n\n"
            "If this is the very first time, the app will ask you to create a new account. "
            "Pick a username you will remember (like your name) and a password. "
            "Write the password down somewhere safe!\n\n"
            "There are two kinds of users:\n"
            "  - Admin: Can change everything (the boss).\n"
            "  - Operator: Can look around and run checks, but cannot change settings.")

        _section(scroll_frame, "Step 2: Activate Your License",
            "You need a license key to use this app. "
            "Without one, the title bar at the top will say [UNLICENSED] "
            "and you will not be able to create profiles or run checks.\n\n"
            "How to activate:\n"
            "  1. Click 'Settings' on the left side.\n"
            "  2. Scroll down to the 'Partner License' section.\n"
            "  3. Paste your license key into the box.\n"
            "  4. Click the 'Activate' button.\n"
            "  5. A green message means it worked!\n\n"
            "If you do not have a key, ask your manager or the person who bought the app.")

        _section(scroll_frame, "Step 3: Set Up Your Environment (Profile)",
            "A 'profile' is just a saved list of server addresses and passwords "
            "for one environment you want to check.\n\n"
            "To create one:\n"
            "  1. Look at the left sidebar and find 'New' under PROFILE.\n"
            "  2. Give it a name (like 'my-servers' or 'production').\n"
            "  3. Click 'Environment' on the left side.\n"
            "  4. Fill in the boxes:\n"
            "       - SDDC Manager: The address of your main VCF manager.\n"
            "       - vCenter: The address of your vCenter server.\n"
            "       - NSX: The address of your network manager.\n"
            "       - For each one, type the username and password too.\n"
            "  5. Click 'Save' on the left sidebar when you are done.\n\n"
            "Tip: If you are not sure what to type, ask the person who runs the servers. "
            "You can also hover your mouse over any field and a little hint will pop up.")

        _section(scroll_frame, "Step 4: Run a Health Check",
            "Now the fun part!\n\n"
            "  1. Click 'Run Check' on the left side.\n"
            "  2. You will see two buttons:\n"
            "       - 'Validate Only' just tests if the app can talk to your servers.\n"
            "       - 'Run Full Check' does the real health check.\n"
            "  3. Click 'Run Full Check' and wait.\n"
            "  4. A black box will show text scrolling by. That is the app working!\n"
            "  5. When it is done, it will say 'Completed' and show a grade.\n\n"
            "Grades work like school: A is the best, F means something needs fixing.\n\n"
            "If you see a yellow warning that says 'bash not found' or 'script not found', "
            "go to Step 8 (Settings) and set the paths first.")

        _section(scroll_frame, "Step 5: See Your Results (Dashboard)",
            "Click 'Dashboard' on the left side. This is your home page.\n\n"
            "You will see:\n"
            "  - A big letter grade (like A, B+, or C)\n"
            "  - A number score out of 100\n"
            "  - A breakdown showing how each part of your servers scored\n"
            "  - A line chart showing if things are getting better or worse over time\n\n"
            "If you have more than one profile, you will see cards for all of them "
            "so you can compare them side by side.")

        _section(scroll_frame, "Step 6: Look at Reports",
            "Click 'Reports' on the left side.\n\n"
            "Every time you run a health check, a report is saved here. "
            "Each report shows the date, time, grade, and score.\n\n"
            "Click on a report to see all the details, or use the buttons to open "
            "the full file.")

        _section(scroll_frame, "Step 7: Run History (The Score Chart)",
            "Click 'Run History' on the left side.\n\n"
            "This page is like a scoreboard that keeps track of every check you have done:\n"
            "  - How many checks total\n"
            "  - Your latest grade and if it went up or down\n"
            "  - Your best and worst grades ever\n"
            "  - A chart with colored dots showing your score over time")

        _section(scroll_frame, "Step 8: Settings (Admin Only)",
            "Click 'Settings' on the left side. Only admins can see this page.\n\n"
            "Important things here:\n\n"
            "Paths (at the top):\n"
            "  - Script path: Where the health check file lives on your computer.\n"
            "  - Bash path: Where the 'bash' program is.\n"
            "  If these are wrong, the app cannot run checks. "
            "Usually they are found automatically, but if not, "
            "click the box and type the correct path.\n\n"
            "Security:\n"
            "  - Password expiry: How many days before users must change their password.\n"
            "  - Session timeout: How many minutes you can walk away before "
            "the app locks and asks for your password again.\n\n"
            "Partner License:\n"
            "  - This is where you paste your license key (see Step 2).\n"
            "  - It shows your license tier (Standard, Professional, Enterprise).\n"
            "  - It shows how many environments and clients you are allowed.\n\n"
            "Billing Rates (if available):\n"
            "  - Set how much each health check run costs.\n"
            "  - Set a monthly rate per environment or per client.\n"
            "  - Set to 0.00 if you do not use billing.\n\n"
            "When you are done changing things, click the big 'Save Settings' button.")

        _section(scroll_frame, "Step 9: Manage Clients (Admin Only)",
            "If your company runs health checks for other companies, "
            "you can keep track of them here.\n\n"
            "Click 'Clients' on the left side.\n\n"
            "To add a new client:\n"
            "  1. Click the '+ New Client' button at the top right.\n"
            "  2. Fill in the company name (this is required).\n"
            "  3. Fill in a contact name, email, and phone if you have them.\n"
            "  4. Click 'Save'.\n\n"
            "To connect a profile to a client:\n"
            "  1. Click on a client card to open their details.\n"
            "  2. Click '+ Assign Profile'.\n"
            "  3. Type the name of the profile you want to give them.\n\n"
            "Each client card shows:\n"
            "  - Their name and contact person\n"
            "  - How many environments they have\n"
            "  - Their average health score\n"
            "  - When their last check was\n\n"
            "Note: This page only shows up if the Clients module is installed.")

        _section(scroll_frame, "Step 10: Usage & Billing (Admin Only)",
            "This page keeps track of every health check anyone has run.\n\n"
            "Click 'Usage & Billing' on the left side.\n\n"
            "You will see:\n"
            "  - Total runs: How many checks have been done ever\n"
            "  - This month: How many checks this month\n"
            "  - Clients: How many different companies\n"
            "  - Environments: How many different server groups\n"
            "  - A bar chart showing runs each month\n"
            "  - A table of the last 20 runs\n\n"
            "To export data (for example, to send a bill to someone):\n"
            "  - Click 'Export CSV' to save a spreadsheet of all runs.\n"
            "  - Click 'Export JSON' to save a data file.\n"
            "  - Click 'Billing Summary' to save a cost breakdown by client.\n\n"
            "Note: This page only shows up if the Usage Tracker module is installed.")

        _section(scroll_frame, "Step 11: Manage Users (Admin Only)",
            "Click 'Users' on the left side.\n\n"
            "Here you can:\n"
            "  - Add a new user: Give them a name, password, and pick admin or operator.\n"
            "  - Reset a password: If someone forgets, you can set a new one.\n"
            "  - Remove a user: Delete someone who no longer needs access.")

        _section(scroll_frame, "Step 12: Suppressions (Admin Only)",
            "Sometimes a check fails but you already know about it "
            "and do not want it to count against your grade.\n\n"
            "Click 'Suppressions' on the left side.\n\n"
            "  - Add a rule: Type the name of the check you want to hide.\n"
            "  - Remove a rule: When you fix the problem, remove the suppression.\n"
            "  - Hidden checks do not affect your grade.")

        _section(scroll_frame, "Step 13: Audit Log (Admin Only)",
            "Click 'Audit Log' on the left side.\n\n"
            "This is a diary of everything that happened in the app: "
            "who logged in, who ran a check, who changed settings.\n\n"
            "Click 'Export CSV' to save it as a spreadsheet.")

        _section(scroll_frame, "Extra Features",
            "Notifications:\n"
            "  You can set up the app to send you an email or a message on Slack or Teams "
            "every time a health check finishes. Set this up in the Environment page "
            "under the Notifications section.\n\n"
            "Scheduled Runs:\n"
            "  On the Run Check page, you can tell the app to run checks automatically "
            "every 30 minutes, every hour, or even once a day. "
            "Just pick a time from the Schedule dropdown. Pick 'Off' to stop.\n\n"
            "Dark Mode:\n"
            "  Click the dark mode button at the bottom of the left sidebar "
            "to switch between light and dark colors.\n\n"
            "Clone a Profile:\n"
            "  If you want to copy a profile (like making a copy of your homework), "
            "click 'Clone' in the sidebar. It makes an exact copy with a new name.\n\n"
            "Import / Export:\n"
            "  You can save a profile to a file ('Export .env' or 'Export JSON') "
            "and load it on another computer ('Import .env' or 'Import JSON').\n\n"
            "Field Tooltips:\n"
            "  If you are not sure what a box in the Environment page is for, "
            "move your mouse over it and a little yellow hint will appear.\n\n"
            "Keyboard Shortcut:\n"
            "  Press F1 at any time to open the About window.")

        _section(scroll_frame, "What You Need to Run This App",
            "  - Python 3.8 or newer (the programming language the app is built with)\n"
            "  - A bash shell (needed to run the actual health check script; "
            "if you use Windows, install 'Git for Windows' and it comes with bash)\n"
            "  - A valid license key (ask your manager)\n"
            "  - Tkinter (comes with Python already, so you probably have it)")

        _section(scroll_frame, "Something Not Working? (Troubleshooting)",
            "The app says 'bash not found':\n"
            "  Install Git for Windows, then go to Settings and point "
            "the Bash Path to the bash.exe file (usually in C:\\Program Files\\Git\\bin\\bash.exe).\n\n"
            "The app says 'script not found':\n"
            "  Download the vcf-health-check.sh file, then go to Settings "
            "and point the Script Path to where you saved it.\n\n"
            "I forgot my password:\n"
            "  Ask an admin to reset it for you from the Users page. "
            "If you ARE the only admin, delete the file called "
            "'vcf-health-users.json' and the app will let you make a new account.\n\n"
            "My account is locked:\n"
            "  If you typed the wrong password too many times, just wait 15 minutes. "
            "The lock goes away on its own.\n\n"
            "Title bar says [UNLICENSED]:\n"
            "  Go to Settings, scroll to Partner License, paste your key, "
            "and click Activate.\n\n"
            "I cannot create profiles or clients:\n"
            "  Your license tier sets a limit. Check your tier in Settings. "
            "If you need more, ask about upgrading to a higher tier.\n\n"
            "The app looks weird:\n"
            "  Try clicking the dark mode button to switch themes, "
            "or close and reopen the app.\n\n"
            "Nothing works at all:\n"
            "  Close the app, open a command prompt, and type:\n"
            "    python vcf-health-check-gui.py\n"
            "  Read the error message and share it with your admin or support.")

        # Contact card at bottom of help page
        contact_card = self._make_card(scroll_frame)
        tk.Label(contact_card, text="Virtual Control LLC", font=("Segoe UI", 12, "bold"),
                 fg=text_p, bg=card_bg).pack(anchor="w", padx=15, pady=(10, 3))
        tk.Label(contact_card, text="https://virtualcontrolllc.com",
                 font=("Segoe UI", 10), fg=brand, bg=card_bg).pack(anchor="w", padx=15)
        tk.Label(contact_card, text="mhayes@virtualcontrolllc.com",
                 font=("Segoe UI", 10), fg=brand, bg=card_bg).pack(anchor="w", padx=15)
        tk.Label(contact_card, text="https://valcalepi.github.io/virtualcontrol.github.io/",
                 font=("Segoe UI", 10), fg=brand, bg=card_bg).pack(anchor="w", padx=15, pady=(0, 10))

    # ── PROFILE CLONING ──────────────────────────────────────────────────

    def _clone_profile(self):
        """Clone the active profile with a new name."""
        active = self.profile_var.get()
        if not active or active not in self.profiles_data.get("profiles", {}):
            messagebox.showwarning("Clone Profile", "No active profile to clone.")
            return

        # Check license limits — partner module or legacy
        script_dir = os.path.dirname(self.script_path) if self.script_path else str(_SCRIPT_DIR)
        if _HAS_LICENSE_MGR:
            count = len(self.profiles_data.get("profiles", {}))
            allowed, msg = license_mgr.can_add_environment(script_dir, self.settings, count)
            if not allowed:
                messagebox.showwarning("License Required", msg)
                return
        else:
            license_info = _check_license(self.settings)
            if license_info.get("mode") != "licensed" and license_info.get("mode") != "grace":
                messagebox.showwarning("License Required",
                    "A valid license is required to create profiles.\n"
                    "Activate a license key in Settings.")
                return

        new_name = simpledialog.askstring("Clone Profile",
            f"Clone '{active}' as:", parent=self.root)
        if not new_name or not new_name.strip():
            return
        new_name = new_name.strip()

        if new_name in self.profiles_data["profiles"]:
            messagebox.showerror("Clone Profile", f"Profile '{new_name}' already exists.")
            return

        cloned = copy.deepcopy(self.profiles_data["profiles"][active])
        cloned["name"] = new_name
        cloned.pop("_last_run", None)  # Don't copy run history
        self.profiles_data["profiles"][new_name] = cloned
        self.profiles_data["active_profile"] = new_name
        save_profiles(self.profiles_data)
        self._refresh_profile_dropdown()

        _audit_log(self.current_user["username"], "PROFILE_CLONED", f"{active} -> {new_name}")
        messagebox.showinfo("Clone Profile", f"Profile '{new_name}' created from '{active}'.")

        if self.current_view == "environment":
            self._show_environment()

    # ── MULTI-ENVIRONMENT DASHBOARD HELPER ──────────────────────────────

    def _switch_to_profile(self, profile_name):
        """Switch active profile and refresh dashboard."""
        self.profiles_data["active_profile"] = profile_name
        save_profiles(self.profiles_data)
        self.profile_var.set(profile_name)
        self._show_dashboard()

    # ── Window close ─────────────────────────────────────────────────────

    def _nav_guard(self, target_fn):
        """Wrap a navigation function with unsaved-changes check."""
        if not self._check_unsaved_changes():
            return
        target_fn()

    def _on_close(self):
        if not self._check_unsaved_changes():
            return
        if self.is_running:
            if not messagebox.askyesno("Running", "A health check is running. Stop and exit?"):
                return
            self._stop_run()
        if self._schedule_after_id:
            self._stop_schedule()
        _audit_log(self.current_user["username"], "APP_CLOSED")
        self._cancel_all_after()
        self.root.destroy()


# ============================================================================
#  USER ACCOUNTS & AUTHENTICATION
# ============================================================================


def _hash_password_legacy(pw: str, salt: str = "") -> str:
    """Legacy SHA-256 hash (for verifying old hashes before PBKDF2 migration)."""
    return hashlib.sha256((salt + pw).encode("utf-8")).hexdigest()


_PBKDF2_ITERATIONS = 310_000


def _hash_password(pw: str, salt: str = "") -> str:
    """Hash a password with PBKDF2-HMAC-SHA256 (310 000 iterations).

    Uses a random 16-byte salt for new hashes. Format: 'pbkdf2:<hex_salt>:<hex_dk>'
    Falls back to username-based salt for legacy 'pbkdf2:<hex_dk>' format.
    """
    random_salt = os.urandom(16)
    combined_salt = random_salt + salt.encode("utf-8")
    dk = hashlib.pbkdf2_hmac(
        "sha256", pw.encode("utf-8"), combined_salt, _PBKDF2_ITERATIONS,
    )
    return "pbkdf2:" + random_salt.hex() + ":" + dk.hex()


def _verify_password(pw: str, stored_hash: str, salt: str = "") -> bool:
    """Verify a password against a stored hash (PBKDF2 or legacy SHA-256).

    Supports three formats:
      - 'pbkdf2:<random_salt_hex>:<dk_hex>' (new, random salt)
      - 'pbkdf2:<dk_hex>' (old, username-based salt)
      - bare hex (legacy SHA-256)
    """
    if stored_hash.startswith("pbkdf2:"):
        parts = stored_hash.split(":", 2)
        if len(parts) == 3:
            # New format: pbkdf2:<random_salt>:<dk>
            random_salt = bytes.fromhex(parts[1])
            combined_salt = random_salt + salt.encode("utf-8")
            dk = hashlib.pbkdf2_hmac(
                "sha256", pw.encode("utf-8"), combined_salt, _PBKDF2_ITERATIONS,
            )
            return hmac.compare_digest(parts[2], dk.hex())
        else:
            # Legacy PBKDF2 format: pbkdf2:<dk> (username-based salt)
            dk = hashlib.pbkdf2_hmac(
                "sha256", pw.encode("utf-8"), salt.encode("utf-8"), _PBKDF2_ITERATIONS,
            )
            return hmac.compare_digest(parts[1], dk.hex())
    # Legacy SHA-256 path (no prefix)
    return hmac.compare_digest(stored_hash, _hash_password_legacy(pw, salt))


def _upgrade_hash_if_legacy(pw: str, stored_hash: str, salt: str, user_rec: dict, users_data: dict):
    """If the stored hash is legacy format, upgrade it to PBKDF2 with random salt."""
    if not stored_hash.startswith("pbkdf2:") or stored_hash.count(":") < 2:
        user_rec["password_hash"] = _hash_password(pw, salt)
        try:
            _save_users(users_data)
        except Exception as e:  # noqa: E722
            logger.debug("Suppressed: %s", e)


# ── Brute-force / account lockout ────────────────────────────────────────

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


def _check_account_locked(user_rec: dict) -> str:
    """Return lockout message if account is locked, else empty string."""
    locked_until = user_rec.get("locked_until", "")
    if not locked_until:
        return ""
    try:
        lock_dt = datetime.fromisoformat(locked_until)
        if lock_dt.tzinfo is None:
            lock_dt = lock_dt.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) < lock_dt:
            remaining = int((lock_dt - datetime.now(timezone.utc)).total_seconds() / 60) + 1
            return f"Account locked. Try again in {remaining} min."
        # Lockout expired — clear it
        user_rec["locked_until"] = ""
        user_rec["failed_attempts"] = 0
        return ""
    except Exception as e:  # noqa: E722
        return ""


def _record_failed_attempt(uname: str, users_data: dict):
    """Increment failed login attempts; lock account if threshold reached."""
    user_rec = users_data.get("users", {}).get(uname)
    if not user_rec:
        return
    attempts = user_rec.get("failed_attempts", 0) + 1
    user_rec["failed_attempts"] = attempts
    if attempts >= MAX_LOGIN_ATTEMPTS:
        lock_time = datetime.now(timezone.utc) + __import__("datetime").timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        user_rec["locked_until"] = lock_time.isoformat()
        _audit_log(uname, "ACCOUNT_LOCKED", f"after {attempts} failed attempts")
    try:
        _save_users(users_data)
    except Exception as e:  # noqa: E722
        logger.debug("Suppressed: %s", e)


def _reset_failed_attempts(uname: str, users_data: dict):
    """Reset failed attempts on successful login."""
    user_rec = users_data.get("users", {}).get(uname)
    if not user_rec:
        return
    if user_rec.get("failed_attempts", 0) > 0 or user_rec.get("locked_until", ""):
        user_rec["failed_attempts"] = 0
        user_rec["locked_until"] = ""
        try:
            _save_users(users_data)
        except Exception as e:  # noqa: E722
            logger.debug("Suppressed: %s", e)


def _load_users() -> dict:
    """Load user accounts from JSON file."""
    if not os.path.exists(USERS_FILE):
        return {"_version": "1.0", "users": {}}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"_version": "1.0", "users": {}}
        data.setdefault("_version", "1.0")
        data.setdefault("users", {})
        return data
    except Exception as e:  # noqa: E722
        return {"_version": "1.0", "users": {}}


def _save_users(data: dict):
    """Save user accounts to JSON file."""
    data["_version"] = "1.0"
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    try:
        os.chmod(USERS_FILE, 0o600)
    except OSError:
        pass


def _audit_log(username: str, action: str, details: str = ""):
    """Append an entry to the audit log file."""
    try:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        line = f"{ts} | {username or 'system'} | {action} | {details}\n"
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass  # Audit logging should never crash the app


# ============================================================================
#  LICENSE KEY SYSTEM
# ============================================================================


def _generate_license_key(customer: str, expiry_date: str, max_profiles: int = 0) -> str:
    """Generate a license key (for Virtual Control admin use)."""
    payload = json.dumps({"c": customer, "e": expiry_date, "m": max_profiles}, separators=(",", ":"))
    sig = hmac.new(_LICENSE_SECRET, payload.encode(), hashlib.sha256).hexdigest()[:20]
    raw = base64.b64encode(payload.encode()).decode().rstrip("=") + "." + sig
    # Format as VCF-XXXXX-XXXXX-XXXXX-XXXXX
    clean = raw.replace(".", "X").replace("/", "Y").replace("+", "Z")
    # Pad or truncate to 20 chars
    clean = clean[:20].upper().ljust(20, "0")
    return f"VCF-{clean[:5]}-{clean[5:10]}-{clean[10:15]}-{clean[15:20]}"


def _validate_license_key(key: str) -> dict:
    """Validate a license key. Returns dict with valid, customer, expires, max_profiles, expired, grace."""
    try:
        # Strip formatting
        raw = key.replace("VCF-", "").replace("-", "")
        if len(raw) < 10:
            return {"valid": False}
        # Reverse formatting
        raw = raw.replace("X", ".").replace("Y", "/").replace("Z", "+")
        # Try to split into payload.signature
        if "." not in raw:
            return {"valid": False}
        parts = raw.split(".", 1)
        payload_b64 = parts[0]
        sig_received = parts[1].lower() if len(parts) > 1 else ""
        # Restore base64 padding
        payload_b64 += "=" * (4 - len(payload_b64) % 4) if len(payload_b64) % 4 else ""
        payload_bytes = base64.b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode())
        # Verify HMAC — full-length constant-time comparison
        expected_sig = hmac.new(_LICENSE_SECRET, payload_bytes, hashlib.sha256).hexdigest()[:20]
        if not hmac.compare_digest(sig_received, expected_sig.lower()):
            return {"valid": False}
        # Parse payload
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
            except Exception as e:  # noqa: E722
                logger.debug("Suppressed: %s", e)
        return {
            "valid": True,
            "customer": customer,
            "expires": expiry,
            "max_profiles": max_profiles,
            "expired": expired,
            "grace": grace,
        }
    except Exception as e:  # noqa: E722
        return {"valid": False}


def _check_license(settings: dict) -> dict:
    """Check license status from settings. Returns license info dict.
    No trial mode — a valid license is required.
    """
    key = settings.get("license_key", "")
    if not key:
        return {"valid": False, "mode": "unlicensed"}
    info = _validate_license_key(key)
    if not info.get("valid"):
        return {"valid": False, "mode": "unlicensed"}
    if info.get("expired"):
        if info.get("grace"):
            return {**info, "mode": "grace"}
        return {"valid": False, "mode": "unlicensed"}
    return {**info, "mode": "licensed"}


# ============================================================================
#  LDAP / ACTIVE DIRECTORY AUTHENTICATION
# ============================================================================


def _ldap_available() -> bool:
    """Check if ldap3 library is available."""
    try:
        import ldap3  # noqa: F401
        return True
    except ImportError:
        return False


def _ldap_authenticate(username: str, password: str, settings: dict) -> Optional[dict]:
    """Authenticate via LDAP. Returns user info dict or None."""
    try:
        from ldap3 import Server, Connection, ALL, SUBTREE
    except ImportError:
        return None

    try:
        server = Server(
            settings.get("ldap_server", ""),
            port=int(settings.get("ldap_port", 389)),
            use_ssl=settings.get("ldap_use_ssl", False),
            get_info=ALL,
            connect_timeout=10,
        )
        # Bind with service account
        try:
            bind_pw = _b64_decode(settings.get("ldap_bind_password", ""))
        except RuntimeError:
            return None
        conn = Connection(server, settings.get("ldap_bind_dn", ""), bind_pw, auto_bind=True)

        # Search for user
        # Escape LDAP special characters to prevent injection
        safe_username = username.replace("\\", "\\5c").replace("*", "\\2a").replace(
            "(", "\\28").replace(")", "\\29").replace("\0", "\\00")
        search_filter = settings.get("ldap_user_filter", "(sAMAccountName={username})").replace("{username}", safe_username)
        conn.search(
            settings.get("ldap_base_dn", ""),
            search_filter,
            SUBTREE,
            attributes=["displayName", "memberOf"],
        )

        if not conn.entries:
            conn.unbind()
            return None

        user_entry = conn.entries[0]
        user_dn = str(user_entry.entry_dn)
        conn.unbind()

        # Authenticate with user's credentials
        user_conn = Connection(server, user_dn, password, auto_bind=True)
        if not user_conn.bound:
            return None
        user_conn.unbind()

        # Determine role from group membership
        member_of = [str(g) for g in user_entry.memberOf] if hasattr(user_entry, "memberOf") else []
        role = "operator"
        admin_group = settings.get("ldap_admin_group", "")
        if admin_group and any(admin_group.lower() in g.lower() for g in member_of):
            role = "admin"

        display_name = str(user_entry.displayName) if hasattr(user_entry, "displayName") else username

        return {"username": display_name, "role": role, "auth": "ldap"}
    except Exception as e:  # noqa: E722
        return None


def _ldap_test_connection(settings: dict) -> str:
    """Test LDAP connection. Returns status string."""
    try:
        from ldap3 import Server, Connection, ALL
    except ImportError:
        return "FAILED: ldap3 library not installed (pip install ldap3)"
    try:
        server = Server(
            settings.get("ldap_server", ""),
            port=int(settings.get("ldap_port", 389)),
            use_ssl=settings.get("ldap_use_ssl", False),
            get_info=ALL,
            connect_timeout=10,
        )
        try:
            bind_pw = _b64_decode(settings.get("ldap_bind_password", ""))
        except RuntimeError as e:
            return f"FAILED: {e}"
        conn = Connection(server, settings.get("ldap_bind_dn", ""), bind_pw, auto_bind=True)
        info = f"Connected to {server.host}:{server.port}"
        conn.unbind()
        return f"SUCCESS: {info}"
    except Exception as e:
        return f"FAILED: {e}"


def _force_password_change(gate, parent_frame, uname: str, users_data: dict) -> bool:
    """Show forced password change dialog. Returns True if password was changed."""
    result = {"changed": False}

    dlg = tk.Toplevel(gate)
    dlg.title("Password Expired")
    dlg.geometry("400x250")
    dlg.resizable(False, False)
    dlg.transient(gate)
    dlg.grab_set()

    # Center on gate
    dlg.update_idletasks()
    x = gate.winfo_x() + (gate.winfo_width() // 2) - 200
    y = gate.winfo_y() + (gate.winfo_height() // 2) - 125
    dlg.geometry(f"+{x}+{y}")

    frame = tk.Frame(dlg, padx=20, pady=15)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Your password has expired.", font=("Segoe UI", 11, "bold"),
             fg="#E74C3C").pack(anchor="w")
    tk.Label(frame, text="Please set a new password to continue.",
             font=("Segoe UI", 9), fg="#666").pack(anchor="w", pady=(0, 8))

    tk.Label(frame, text="New Password:", font=("Segoe UI", 10)).pack(anchor="w")
    new_pw_var = tk.StringVar()
    new_pw_entry = tk.Entry(frame, textvariable=new_pw_var, show="*", font=("Segoe UI", 11))
    new_pw_entry.pack(fill="x", pady=(2, 5))

    tk.Label(frame, text="Confirm Password:", font=("Segoe UI", 10)).pack(anchor="w")
    confirm_pw_var = tk.StringVar()
    confirm_pw_entry = tk.Entry(frame, textvariable=confirm_pw_var, show="*", font=("Segoe UI", 11))
    confirm_pw_entry.pack(fill="x", pady=(2, 5))

    err_lbl = tk.Label(frame, text="", fg="red", font=("Segoe UI", 9))
    err_lbl.pack()

    def _save():
        p1 = new_pw_var.get()
        p2 = confirm_pw_var.get()
        if len(p1) < 4:
            err_lbl.config(text="Password must be at least 4 characters")
            return
        if p1 != p2:
            err_lbl.config(text="Passwords do not match")
            return
        users_data["users"][uname]["password_hash"] = _hash_password(p1, uname)
        users_data["users"][uname]["password_changed"] = datetime.now(timezone.utc).isoformat()
        _save_users(users_data)
        _audit_log(uname, "PASSWORD_CHANGED_EXPIRED")
        result["changed"] = True
        dlg.destroy()

    def _cancel():
        dlg.destroy()

    btn_row = tk.Frame(frame)
    btn_row.pack(fill="x", pady=(5, 0))
    tk.Button(btn_row, text="Change Password", command=_save,
              bg="#0077B6", fg="white", font=("Segoe UI", 10, "bold"),
              relief="flat", padx=15, pady=3).pack(side="left")
    tk.Button(btn_row, text="Cancel", command=_cancel,
              font=("Segoe UI", 10), relief="flat", padx=10, pady=3).pack(side="left", padx=(10, 0))

    dlg.protocol("WM_DELETE_WINDOW", _cancel)
    new_pw_entry.focus_set()
    new_pw_entry.bind("<Return>", lambda e: confirm_pw_entry.focus_set())
    confirm_pw_entry.bind("<Return>", lambda e: _save())

    dlg.wait_window()
    return result["changed"]


def _login_gate() -> Optional[dict]:
    """Show login dialog. Returns user dict {'username','role'} or None if cancelled."""
    users_data = _load_users()
    first_time = len(users_data.get("users", {})) == 0
    result = {"user": None}

    gate = tk.Tk()
    gate.title("VCF Health Check — Login")
    h = 440 if first_time else 260
    gate.geometry(f"440x{h}")
    gate.resizable(False, False)
    gate.protocol("WM_DELETE_WINDOW", lambda: _cancel())

    # Center and force to front
    gate.update_idletasks()
    x = (gate.winfo_screenwidth() // 2) - 220
    y = (gate.winfo_screenheight() // 2) - (h // 2)
    gate.geometry(f"+{x}+{y}")
    gate.attributes("-topmost", True)
    gate.lift()
    gate.focus_force()
    gate.after(300, lambda: gate.attributes("-topmost", False))

    frame = tk.Frame(gate, padx=25, pady=15)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="VCF Health Check", font=("Segoe UI", 18, "bold")).pack()
    tk.Label(frame, text=APP_COPYRIGHT, font=("Segoe UI", 8), fg="#888").pack(pady=(0, 8))

    err_label = tk.Label(frame, text="", fg="red", font=("Segoe UI", 9))

    if first_time:
        tk.Label(frame, text="Welcome to VCF Health Check",
                 font=("Segoe UI", 14, "bold"), fg="#0077B6").pack(anchor="w")
        tk.Label(frame, text="First-time setup",
                 font=("Segoe UI", 10), fg="#555555").pack(anchor="w", pady=(2, 0))
        tk.Label(frame, text="No user accounts exist yet. Create an administrator\n"
                 "account to get started. This account will have full access\n"
                 "to all features including user management and settings.",
                 font=("Segoe UI", 9), fg="#333333", justify="left",
                 wraplength=340).pack(anchor="w", pady=(8, 0))

        tk.Label(frame, text="Username:", font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))
        user_var = tk.StringVar()
        user_entry = tk.Entry(frame, textvariable=user_var, width=35, font=("Segoe UI", 11))
        user_entry.pack(fill="x", pady=(2, 0))

        tk.Label(frame, text="Password:", font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))
        pw_var = tk.StringVar()
        pw_entry = tk.Entry(frame, textvariable=pw_var, show="*", width=35, font=("Segoe UI", 11))
        pw_entry.pack(fill="x", pady=(2, 0))

        tk.Label(frame, text="Confirm password:", font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))
        pw2_var = tk.StringVar()
        pw2_entry = tk.Entry(frame, textvariable=pw2_var, show="*", width=35, font=("Segoe UI", 11))
        pw2_entry.pack(fill="x", pady=(2, 0))

        err_label.pack(pady=(4, 0))

        def _create_admin():
            uname = user_var.get().strip()
            p1, p2 = pw_var.get(), pw2_var.get()
            if not uname:
                err_label.config(text="Username is required")
                return
            if len(p1) < 4:
                err_label.config(text="Password must be at least 4 characters")
                return
            if p1 != p2:
                err_label.config(text="Passwords do not match")
                return
            users_data["users"][uname.lower()] = {
                "display_name": uname,
                "password_hash": _hash_password(p1, uname.lower()),
                "role": "admin",
                "created": datetime.now(timezone.utc).isoformat(),
            }
            _save_users(users_data)
            _audit_log(uname, "USER_CREATED", "initial admin setup")
            _audit_log(uname, "LOGIN_SUCCESS", "first-time setup")
            result["user"] = {"username": uname, "role": "admin"}
            gate.destroy()

        tk.Button(frame, text="Create Account & Get Started", command=_create_admin,
                  font=("Segoe UI", 10, "bold"), bg="#0077B6", fg="white",
                  relief="flat", padx=15, pady=5, cursor="hand2").pack(pady=(8, 0), fill="x")
        user_entry.focus_set()
        user_entry.bind("<Return>", lambda e: pw_entry.focus_set())
        pw_entry.bind("<Return>", lambda e: pw2_entry.focus_set())
        pw2_entry.bind("<Return>", lambda e: _create_admin())
    else:
        tk.Label(frame, text="Sign in", font=("Segoe UI", 11, "bold"),
                 fg="#0077B6").pack(anchor="w")

        tk.Label(frame, text="Username:", font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))
        user_var = tk.StringVar()
        user_entry = tk.Entry(frame, textvariable=user_var, width=35, font=("Segoe UI", 11))
        user_entry.pack(fill="x", pady=(2, 0))

        tk.Label(frame, text="Password:", font=("Segoe UI", 10)).pack(anchor="w", pady=(6, 0))
        pw_var = tk.StringVar()
        pw_entry = tk.Entry(frame, textvariable=pw_var, show="*", width=35, font=("Segoe UI", 11))
        pw_entry.pack(fill="x", pady=(2, 0))

        err_label.pack(pady=(4, 0))

        def _login():
            uname = user_var.get().strip().lower()
            pw = pw_var.get()

            # Try LDAP first if configured
            profiles_data = load_profiles()
            _settings = profiles_data.get("_settings", {})
            if _settings.get("ldap_enabled") and _settings.get("ldap_server"):
                ldap_result = _ldap_authenticate(uname, pw, _settings)
                if ldap_result:
                    _audit_log(uname, "LOGIN_SUCCESS", "via LDAP")
                    result["user"] = ldap_result
                    gate.destroy()
                    return
                # LDAP failed — fall through to local auth

            user_rec = users_data.get("users", {}).get(uname)
            if not user_rec:
                _audit_log(uname, "LOGIN_FAILED", "unknown user")
                err_label.config(text="Invalid username or password")
                pw_var.set("")
                return
            # Brute-force lockout check
            locked_msg = _check_account_locked(user_rec)
            if locked_msg:
                err_label.config(text=locked_msg)
                return
            if not _verify_password(pw, user_rec["password_hash"], uname):
                _record_failed_attempt(uname, users_data)
                _audit_log(uname, "LOGIN_FAILED", "wrong password")
                err_label.config(text="Invalid username or password")
                pw_var.set("")
                return

            # Upgrade legacy hash to PBKDF2 transparently
            _upgrade_hash_if_legacy(pw, user_rec["password_hash"], uname, user_rec, users_data)
            _reset_failed_attempts(uname, users_data)

            # Check password expiration
            expiry_days = int(_settings.get("password_expiry_days", 90))
            pw_changed = user_rec.get("password_changed", user_rec.get("created", ""))
            if expiry_days > 0 and pw_changed:
                try:
                    changed_dt = datetime.fromisoformat(pw_changed)
                    if changed_dt.tzinfo is None:
                        changed_dt = changed_dt.replace(tzinfo=timezone.utc)
                    age_days = (datetime.now(timezone.utc) - changed_dt).days
                    if age_days >= expiry_days:
                        _audit_log(uname, "PASSWORD_EXPIRED_FORCE_CHANGE")
                        if not _force_password_change(gate, frame, uname, users_data):
                            return  # User cancelled — stay on login
                except Exception as e:  # noqa: E722
                    logger.debug("Suppressed: %s", e)

            _audit_log(uname, "LOGIN_SUCCESS")
            result["user"] = {
                "username": user_rec.get("display_name", uname),
                "role": user_rec.get("role", "operator"),
            }
            gate.destroy()

        tk.Button(frame, text="Sign In", command=_login,
                  font=("Segoe UI", 10, "bold"), bg="#0077B6", fg="white",
                  relief="flat", padx=15, pady=5, cursor="hand2").pack(pady=(8, 0), fill="x")
        user_entry.focus_set()
        user_entry.bind("<Return>", lambda e: pw_entry.focus_set())
        pw_entry.bind("<Return>", lambda e: _login())

    def _cancel():
        result["user"] = None
        gate.destroy()

    gate.mainloop()
    return result["user"]


# ============================================================================
#  FIRST-RUN SETUP WIZARD
# ============================================================================


def _first_run_wizard(root) -> Optional[dict]:
    """Show a 4-step first-run wizard after login, before the main app.

    Returns dict with setup results or None if the user closed the wizard.
    """
    result = {"completed": False}
    step = {"current": 1}

    wiz = tk.Toplevel(root)
    wiz.title("VCF Health Check — Setup")
    wiz.geometry("550x480")
    wiz.resizable(False, False)
    wiz.grab_set()
    wiz.protocol("WM_DELETE_WINDOW", lambda: _close_wizard())

    # Center on screen
    wiz.update_idletasks()
    x = (wiz.winfo_screenwidth() // 2) - 275
    y = (wiz.winfo_screenheight() // 2) - 240
    wiz.geometry(f"+{x}+{y}")
    wiz.attributes("-topmost", True)
    wiz.lift()
    wiz.focus_force()
    wiz.after(300, lambda: wiz.attributes("-topmost", False))

    # -- Shared state --
    license_valid = {"value": False}
    admin_bypassed = {"value": False}
    license_key_val = {"value": ""}
    license_info = {"value": {}}
    detected_script = find_script() or ""
    detected_bash = find_bash() or ""
    script_path_val = {"value": detected_script}
    bash_path_val = {"value": detected_bash}

    # -- Header (persistent) --
    header = tk.Frame(wiz, bg="#0077B6", height=50)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(header, text="VCF Health Check Setup",
             font=("Segoe UI", 14, "bold"), bg="#0077B6", fg="white").pack(
        side="left", padx=15, pady=10)
    step_label = tk.Label(header, text="Step 1 of 4",
                          font=("Segoe UI", 10), bg="#0077B6", fg="#D6EAF8")
    step_label.pack(side="right", padx=15)

    # -- Content area (swapped per step) --
    content = tk.Frame(wiz, padx=30, pady=15)
    content.pack(fill="both", expand=True)

    # -- Footer with nav buttons --
    footer = tk.Frame(wiz, pady=10, padx=30)
    footer.pack(fill="x", side="bottom")
    btn_next = tk.Button(footer, text="Next", font=("Segoe UI", 10, "bold"),
                         bg="#0077B6", fg="white", relief="flat", padx=20, pady=4)
    btn_next.pack(side="right")

    def _close_wizard():
        result["completed"] = False
        wiz.destroy()

    def _clear_content():
        for w in content.winfo_children():
            w.destroy()

    # ── Step 1: Welcome ──────────────────────────────────────────────────

    def _show_step1():
        step["current"] = 1
        step_label.config(text="Step 1 of 4")
        _clear_content()

        tk.Label(content, text="Let's Get You Set Up!",
                 font=("Segoe UI", 18, "bold"), fg="#0077B6").pack(anchor="w", pady=(10, 5))

        msg = (
            "Welcome to VCF Health Check — the comprehensive health\n"
            "monitoring tool for VMware Cloud Foundation environments.\n\n"
            "This quick setup will walk you through:\n\n"
            "  1.  Activating your license key\n"
            "  2.  Confirming the script and bash paths\n\n"
            "It only takes about a minute. Let's go!"
        )
        tk.Label(content, text=msg, font=("Segoe UI", 10), justify="left",
                 wraplength=480).pack(anchor="w", pady=(5, 0))

        btn_next.config(text="Next  \u2192", state="normal", command=_show_step2)

    # ── Step 2: License Activation ────────────────────────────────────────

    def _show_step2():
        step["current"] = 2
        step_label.config(text="Step 2 of 4")
        _clear_content()

        tk.Label(content, text="License Activation",
                 font=("Segoe UI", 14, "bold"), fg="#0077B6").pack(anchor="w", pady=(5, 2))
        tk.Label(content, text="Enter your partner license key to unlock the full app.",
                 font=("Segoe UI", 9), fg="#555").pack(anchor="w", pady=(0, 8))

        # Key entry row
        key_frame = tk.Frame(content)
        key_frame.pack(fill="x", pady=(0, 3))
        key_var = tk.StringVar(value=license_key_val["value"])
        key_entry = tk.Entry(key_frame, textvariable=key_var, font=("Consolas", 11), width=42)
        key_entry.pack(side="left", fill="x", expand=True)

        activate_btn = tk.Button(key_frame, text="Activate", font=("Segoe UI", 9, "bold"),
                                 bg="#27AE60", fg="white", relief="flat", padx=10, pady=2)
        activate_btn.pack(side="left", padx=(8, 0))

        # Result area
        result_frame = tk.Frame(content)
        result_frame.pack(fill="x", pady=(5, 0))
        result_label = tk.Label(result_frame, text="", font=("Segoe UI", 9), wraplength=460,
                                justify="left")
        result_label.pack(anchor="w")

        # Detail area (partner info after success)
        detail_frame = tk.Frame(content)
        detail_frame.pack(fill="x", pady=(3, 0))

        def _do_activate():
            key = key_var.get().strip()
            if not key:
                result_label.config(text="Please enter a license key.", fg="#E74C3C")
                return
            license_key_val["value"] = key
            # Clear previous detail
            for w in detail_frame.winfo_children():
                w.destroy()

            if not _HAS_LICENSE_MGR:
                result_label.config(text="License manager module not available.", fg="#E74C3C")
                return

            script_dir = os.path.dirname(script_path_val["value"]) if script_path_val["value"] else str(_SCRIPT_DIR)
            act_result = license_mgr.activate_partner_license(script_dir, key)
            if not act_result.get("success"):
                result_label.config(
                    text=act_result.get("error", "The license key is not valid."),
                    fg="#E74C3C")
                license_valid["value"] = False
                _update_next_state()
                return

            info = act_result["info"]
            license_info["value"] = info
            license_valid["value"] = True
            result_label.config(text="\u2714  License activated successfully!", fg="#27AE60")

            # Show partner details
            tier = info.get("tier", "standard")
            tier_label_text = "Standard"
            if _HAS_LICENSE_MGR:
                tier_label_text = license_mgr.TIER_DEFINITIONS.get(tier, {}).get("label", tier)
            tk.Label(detail_frame, text=f"Partner: {info.get('partner_name', 'N/A')}",
                     font=("Segoe UI", 10, "bold")).pack(anchor="w")
            badge_row = tk.Frame(detail_frame)
            badge_row.pack(anchor="w", pady=(2, 0))
            tier_colors = {"standard": "#3498DB", "starter": "#3498DB",
                           "professional": "#27AE60",
                           "enterprise": "#8E44AD", "msp": "#E67E22"}
            badge_bg = tier_colors.get(tier, "#3498DB")
            tk.Label(badge_row, text=f" {tier_label_text.upper()} ",
                     bg=badge_bg, fg="white", font=("Segoe UI", 9, "bold"),
                     padx=6, pady=1).pack(side="left")
            tk.Label(badge_row, text=f"  Expires: {info.get('expires', 'N/A')}",
                     font=("Segoe UI", 9), fg="#555").pack(side="left", padx=(8, 0))

            _update_next_state()

        activate_btn.config(command=_do_activate)
        key_entry.bind("<Return>", lambda e: _do_activate())

        # ── Admin Bypass section ──
        sep = tk.Frame(content, height=1, bg="#D5D8DC")
        sep.pack(fill="x", pady=(15, 10))

        tk.Label(content, text="Admin Bypass",
                 font=("Segoe UI", 10, "bold"), fg="#888").pack(anchor="w")
        tk.Label(content, text="If you have the admin password, you can skip license activation.",
                 font=("Segoe UI", 9), fg="#888").pack(anchor="w", pady=(0, 5))

        bypass_frame = tk.Frame(content)
        bypass_frame.pack(fill="x")
        pw_var = tk.StringVar()
        pw_entry = tk.Entry(bypass_frame, textvariable=pw_var, show="\u2022",
                            font=("Segoe UI", 11), width=30)
        pw_entry.pack(side="left")
        unlock_btn = tk.Button(bypass_frame, text="Unlock", font=("Segoe UI", 9, "bold"),
                               bg="#566573", fg="white", relief="flat", padx=10, pady=2)
        unlock_btn.pack(side="left", padx=(8, 0))

        bypass_result = tk.Label(content, text="", font=("Segoe UI", 9))
        bypass_result.pack(anchor="w", pady=(3, 0))

        def _do_bypass():
            password = pw_var.get().strip()
            if not password:
                bypass_result.config(text="Enter the admin password.", fg="#E74C3C")
                return
            if not _HAS_LICENSE_MGR:
                bypass_result.config(text="License manager not available.", fg="#E74C3C")
                return
            if license_mgr.verify_admin_backdoor(password):
                admin_bypassed["value"] = True
                bypass_result.config(text="\u2714  Admin bypass activated. Full access granted.",
                                     fg="#27AE60")
                _update_next_state()
            else:
                admin_bypassed["value"] = False
                bypass_result.config(text="Invalid admin password.", fg="#E74C3C")
                _update_next_state()

        unlock_btn.config(command=_do_bypass)
        pw_entry.bind("<Return>", lambda e: _do_bypass())

        def _update_next_state():
            if license_valid["value"] or admin_bypassed["value"]:
                btn_next.config(state="normal")
            else:
                btn_next.config(state="disabled")

        btn_next.config(text="Next  \u2192", state="disabled", command=_show_step3)
        # Restore state if returning to this step with a valid license
        if license_valid["value"] or admin_bypassed["value"]:
            btn_next.config(state="normal")

        key_entry.focus_set()

    # ── Step 3: Path Setup ────────────────────────────────────────────────

    def _show_step3():
        step["current"] = 3
        step_label.config(text="Step 3 of 4")
        _clear_content()

        tk.Label(content, text="Path Configuration",
                 font=("Segoe UI", 14, "bold"), fg="#0077B6").pack(anchor="w", pady=(5, 2))
        tk.Label(content, text="Confirm the paths to the health check script and bash executable.",
                 font=("Segoe UI", 9), fg="#555").pack(anchor="w", pady=(0, 12))

        def _make_path_row(parent, label_text, path_val_dict, key, filetypes, dialog_title):
            row = tk.Frame(parent)
            row.pack(fill="x", pady=(0, 12))

            tk.Label(row, text=label_text, font=("Segoe UI", 10, "bold")).pack(anchor="w")

            entry_row = tk.Frame(row)
            entry_row.pack(fill="x", pady=(3, 0))

            path = path_val_dict[key]
            found = bool(path and os.path.isfile(path))

            indicator = "\u2714" if found else "\u2718"
            ind_color = "#27AE60" if found else "#E74C3C"
            ind_label = tk.Label(entry_row, text=indicator, font=("Segoe UI", 14),
                                 fg=ind_color)
            ind_label.pack(side="left", padx=(0, 5))

            path_var = tk.StringVar(value=path)
            path_entry = tk.Entry(entry_row, textvariable=path_var, font=("Segoe UI", 9),
                                  width=50, state="readonly")
            path_entry.pack(side="left", fill="x", expand=True)

            def _browse():
                chosen = filedialog.askopenfilename(
                    title=dialog_title, filetypes=filetypes, parent=wiz)
                if chosen:
                    path_val_dict[key] = chosen
                    path_var.set(chosen)
                    is_ok = os.path.isfile(chosen)
                    ind_label.config(text="\u2714" if is_ok else "\u2718",
                                     fg="#27AE60" if is_ok else "#E74C3C")

            browse_btn = tk.Button(entry_row, text="Browse...", font=("Segoe UI", 9),
                                   relief="flat", padx=8, pady=1, command=_browse)
            browse_btn.pack(side="left", padx=(8, 0))

            if not found:
                tk.Label(row, text="Not auto-detected. Use Browse to locate it, or fix later in Settings.",
                         font=("Segoe UI", 8), fg="#888").pack(anchor="w", pady=(2, 0))

        _make_path_row(content, "Health Check Script  (vcf-health-check.sh)",
                       script_path_val, "value",
                       [("Shell scripts", "*.sh"), ("All files", "*.*")],
                       "Locate vcf-health-check.sh")

        _make_path_row(content, "Bash Executable",
                       bash_path_val, "value",
                       [("Executables", "*.exe"), ("All files", "*.*")],
                       "Locate bash executable")

        # Helpful note
        tk.Label(content,
                 text="Tip: Paths can always be changed later in Settings.",
                 font=("Segoe UI", 9), fg="#888").pack(anchor="w", pady=(10, 0))

        btn_next.config(text="Next  \u2192", state="normal", command=_show_step4)

    # ── Step 4: All Done ──────────────────────────────────────────────────

    def _show_step4():
        step["current"] = 4
        step_label.config(text="Step 4 of 4")
        _clear_content()

        tk.Label(content, text="You're All Set!",
                 font=("Segoe UI", 18, "bold"), fg="#27AE60").pack(anchor="w", pady=(10, 8))

        # Summary card
        card = tk.Frame(content, bd=1, relief="solid", padx=15, pady=12)
        card.pack(fill="x", pady=(0, 10))

        # License info
        if admin_bypassed["value"]:
            lic_text = "Admin Bypass  —  Full access granted"
            lic_color = "#8E44AD"
        elif license_valid["value"]:
            info = license_info["value"]
            tier = info.get("tier", "standard")
            tier_label_text = tier
            if _HAS_LICENSE_MGR:
                tier_label_text = license_mgr.TIER_DEFINITIONS.get(tier, {}).get("label", tier)
            lic_text = f"{info.get('partner_name', 'N/A')}  —  {tier_label_text} tier"
            lic_color = "#27AE60"
        else:
            lic_text = "Unlicensed"
            lic_color = "#E74C3C"

        tk.Label(card, text="License:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        tk.Label(card, text=lic_text, font=("Segoe UI", 10), fg=lic_color).pack(
            anchor="w", padx=(15, 0))

        # Paths
        tk.Label(card, text="Paths:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=(8, 0))
        for lbl, val in [("Script", script_path_val["value"]),
                         ("Bash", bash_path_val["value"])]:
            found = bool(val and os.path.isfile(val))
            icon = "\u2714" if found else "\u2718"
            color = "#27AE60" if found else "#E74C3C"
            display = val if val else "Not found"
            row = tk.Frame(card)
            row.pack(anchor="w", padx=(15, 0), pady=(1, 0))
            tk.Label(row, text=f"{icon} {lbl}:", font=("Segoe UI", 9, "bold"),
                     fg=color).pack(side="left")
            tk.Label(row, text=f"  {display}", font=("Segoe UI", 9),
                     fg="#555").pack(side="left")

        tk.Label(content,
                 text="Everything is saved. The app will now open.",
                 font=("Segoe UI", 10), fg="#555").pack(anchor="w", pady=(12, 0))

        btn_next.config(text="Finish  \u2714", state="normal", command=_do_finish)

    def _do_finish():
        # Persist settings
        profiles_data = load_profiles()
        settings = profiles_data.get("_settings", {})

        # License
        if license_valid["value"] and license_key_val["value"]:
            settings["license_key"] = license_key_val["value"]
        if admin_bypassed["value"]:
            settings["_admin_bypass"] = True

        # Paths
        if script_path_val["value"]:
            settings["script_path"] = script_path_val["value"]
        if bash_path_val["value"]:
            settings["bash_path"] = bash_path_val["value"]

        # Mark complete
        settings["setup_complete"] = True
        profiles_data["_settings"] = settings
        save_profiles(profiles_data)

        _audit_log("system", "SETUP_WIZARD_COMPLETED",
                   f"license={'bypass' if admin_bypassed['value'] else 'key' if license_valid['value'] else 'none'}")

        result["completed"] = True
        result["license_key"] = license_key_val["value"]
        result["script_path"] = script_path_val["value"]
        result["bash_path"] = bash_path_val["value"]
        result["admin_bypass"] = admin_bypassed["value"]
        wiz.destroy()

    # Start at step 1
    _show_step1()
    wiz.wait_window()

    return result if result["completed"] else None


# ============================================================================
#  ENTRY POINT
# ============================================================================


def main():
    _audit_log("system", "APP_STARTED")
    # Login gate — runs as its own Tk() instance, destroyed before app starts
    user_info = _login_gate()
    if not user_info:
        return

    root = tk.Tk()
    root.withdraw()

    splash = SplashScreen(root)
    splash.set_progress(0.2, "Loading profiles...")

    def _step2():
        splash.set_progress(0.5, "Detecting environment...")

    def _step3():
        splash.set_progress(0.8, "Building interface...")

    def _step4():
        splash.set_progress(1.0, "Ready!")

    def _finish():
        splash.close()

        # First-run wizard — show once if setup not yet completed
        profiles_data = load_profiles()
        settings = profiles_data.get("_settings", {})
        if not settings.get("setup_complete"):
            wizard_result = _first_run_wizard(root)
            if wizard_result is None:
                root.destroy()
                return

        # Set geometry before building app so window opens at final size
        root.geometry(INITIAL_SIZE)
        try:
            root.state("zoomed")
        except Exception as e:  # noqa: E722
            logger.debug("Suppressed: %s", e)
        app = VCFHealthCheckApp(root, user_info)
        root.deiconify()
        root.attributes("-topmost", True)
        root.lift()
        root.focus_force()
        root.after(500, lambda: root.attributes("-topmost", False))

    root.after(400, _step2)
    root.after(800, _step3)
    root.after(1200, _step4)
    root.after(1500, _finish)
    root.mainloop()


if __name__ == "__main__":
    main()
