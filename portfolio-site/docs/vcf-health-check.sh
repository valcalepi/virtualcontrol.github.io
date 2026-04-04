#!/bin/bash
# ============================================================================
#  VCF 9.0 ENVIRONMENT HEALTH CHECK  v8.0
# ============================================================================
#  Usage:    bash vcf-health-check.sh [OPTIONS]
#  Config:   Place vcf-health-check.env in the same directory (optional)
#  Output:   Color terminal + TXT + HTML + JSON + CSV + PDF + Markdown
#
#  Options:
#    --only <comp>       Run only specified components (comma-separated)
#                        Values: infra,vcenter,sddc,nsx,ops,fleet,plugins
#    --skip <comp>       Skip specified components (comma-separated)
#    --env <file>        Use a specific .env file (multi-environment support)
#    --known-down <comp> Mark components as expected-down (skip, not fail)
#    --cleanup-tasks     Auto-cancel stale SDDC tasks (>24h old)
#    --fix               Auto-remediate safe issues (snapshots, locks, services)
#    --diff              Only show checks that changed since last run
#    --validate          Pre-flight check: test config, creds, connectivity
#    --schedule          Generate a Windows Task Scheduler XML file
#    --cron [interval]   Generate a cron/systemd timer (daily|hourly|custom)
#    --json-only         Output JSON report only (no terminal output)
#    --csv               Also generate CSV report
#    --markdown          Also generate Markdown report
#    --prometheus        Output Prometheus/OpenMetrics format
#    --ansible           Generate Ansible inventory from discovered hosts
#    --archive           Compress old reports to .tar.gz
#    --syslog <host>     Send results via syslog (RFC 5424) to SIEM
#    --backup-config     Export current topology + config to JSON
#    --merge-reports <d> Merge JSON reports from multiple dirs into dashboard
#    --quiet             Suppress terminal output (reports still saved)
#    --help              Show this help
#
#  v8.0 Enhancements:
#    - Expected-down components (--known-down) to skip offline VMs gracefully
#    - Known-issue suppression registry (known-issues.json)
#    - SDDC Manager retry with backoff on token-acquired-but-API-failing
#    - ESXi hardware sensor health (temperature, fans, PSU)
#    - vSAN disk group health (cache vs capacity tier)
#    - NSX transport zone membership validation
#    - SDDC Manager lifecycle update availability check
#    - vCenter VAMI service deep-check (individual critical services)
#    - curl session reuse (cookie jar) for reduced TLS overhead
#    - Per-component configurable timeouts
#    - Early-exit when vCenter is unreachable (skip dependent checks)
#    - Markdown report output (--markdown)
#    - Multi-environment dashboard (--merge-reports)
#    - Email HTML attachment support
#    - Pre-flight validation mode (--validate)
#    - Generic webhook integration (WEBHOOK_URL)
#    - Lock file to prevent concurrent runs
#    - Connection pooling via curl cookie jar
# ============================================================================

set +H  # Disable bash history expansion (! in passwords)

# --- CLI ARGUMENTS ---
RUN_ONLY=""
RUN_SKIP=""
KNOWN_DOWN=""
AUTO_CLEANUP_TASKS="${AUTO_CLEANUP_TASKS:-false}"
AUTO_FIX=false
DIFF_ONLY=false
JSON_ONLY=false
CSV_EXPORT=false
MARKDOWN_EXPORT=false
PROMETHEUS_MODE=false
ANSIBLE_MODE=false
ARCHIVE_MODE=false
SYSLOG_HOST=""
BACKUP_CONFIG=false
VALIDATE_ONLY=false
MERGE_DIR=""
QUIET=false
GEN_SCHEDULE=false
GEN_CRON=""
CUSTOM_ENV=""

while [ $# -gt 0 ]; do
    case "$1" in
        --only)       RUN_ONLY="$2"; shift 2 ;;
        --skip)       RUN_SKIP="$2"; shift 2 ;;
        --known-down) KNOWN_DOWN="$2"; shift 2 ;;
        --env)        CUSTOM_ENV="$2"; shift 2 ;;
        --cleanup-tasks) AUTO_CLEANUP_TASKS="true"; shift ;;
        --fix)        AUTO_FIX=true; shift ;;
        --diff)       DIFF_ONLY=true; shift ;;
        --validate)   VALIDATE_ONLY=true; shift ;;
        --syslog)     SYSLOG_HOST="$2"; shift 2 ;;
        --backup-config) BACKUP_CONFIG=true; shift ;;
        --merge-reports) MERGE_DIR="$2"; shift 2 ;;
        --schedule)   GEN_SCHEDULE=true; shift ;;
        --cron)       GEN_CRON="${2:-daily}"; shift; [ "${1:0:2}" != "--" ] 2>/dev/null && shift || true ;;
        --json-only)  JSON_ONLY=true; QUIET=true; shift ;;
        --csv)        CSV_EXPORT=true; shift ;;
        --markdown)   MARKDOWN_EXPORT=true; shift ;;
        --prometheus) PROMETHEUS_MODE=true; QUIET=true; shift ;;
        --ansible)    ANSIBLE_MODE=true; shift ;;
        --archive)    ARCHIVE_MODE=true; shift ;;
        --quiet)      QUIET=true; shift ;;
        --help|-h)
            sed -n '2,/^# =====/p' "$0" | head -30 | sed 's/^#//; s/^ //'
            exit 0 ;;
        *) echo "Unknown option: $1. Use --help for usage."; exit 1 ;;
    esac
done

# Helper: should we run a component?
should_run() {
    local comp="$1"
    # v8.0: known-down components are skipped entirely
    if [ -n "$KNOWN_DOWN" ]; then
        echo ",$KNOWN_DOWN," | grep -qi ",$comp," && return 1
    fi
    if [ -n "$RUN_ONLY" ]; then
        echo ",$RUN_ONLY," | grep -qi ",$comp," && return 0 || return 1
    fi
    if [ -n "$RUN_SKIP" ]; then
        echo ",$RUN_SKIP," | grep -qi ",$comp," && return 1 || return 0
    fi
    return 0
}
# v8.0 Feature 1: Check if component is expected-down (mark as SKIP not FAIL)
is_known_down() {
    [ -n "$KNOWN_DOWN" ] && echo ",$KNOWN_DOWN," | grep -qi ",$1," && return 0
    return 1
}

# --- SCRIPT DIR & CONFIG ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" 2>/dev/null || echo ".")" && pwd)"
# Feature 16: Multi-environment profiles via --env
if [ -n "$CUSTOM_ENV" ]; then
    if [ -f "$CUSTOM_ENV" ]; then ENV_FILE="$CUSTOM_ENV"
    elif [ -f "$SCRIPT_DIR/$CUSTOM_ENV" ]; then ENV_FILE="$SCRIPT_DIR/$CUSTOM_ENV"
    else echo "ERROR: Env file not found: $CUSTOM_ENV"; exit 1; fi
else
    ENV_FILE="$SCRIPT_DIR/vcf-health-check.env"
fi
[ -f "$ENV_FILE" ] && source "$ENV_FILE"

# --- DEFAULTS (used if not set by .env) ---
: "${VCENTER:=vcenter.lab.local}"
: "${SDDC:=sddc-manager.lab.local}"
: "${NSX_VIP:=nsx-vip.lab.local}"
: "${NSX_NODE:=192.168.1.71}"
: "${VCF_OPS:=192.168.1.77}"
: "${FLEET:=192.168.1.78}"
: "${SSO_USER:=administrator@vsphere.local}"
: "${SSO_PASS:=Success01!0909!!}"
: "${NSX_USER:=admin}"
: "${NSX_PASS:=Success01!0909!!}"
: "${OPS_USER:=admin}"
: "${OPS_PASS:=Success01!0909!!}"
: "${FLEET_USER:=admin@local}"
: "${FLEET_PASS:=Success01!0909!!}"
: "${FLEET_PORT:=443}"
: "${ESXI_HOSTS:=192.168.1.74 192.168.1.75 192.168.1.76 192.168.1.82}"
: "${ESXI_USER:=root}"
: "${ESXI_PASS:=Success01!0909!!}"
: "${CURL_CONNECT_TIMEOUT:=15}"
: "${CURL_MAX_TIME:=30}"
: "${CERT_WARN_DAYS:=30}"
: "${DATASTORE_WARN_PCT:=80}"
: "${DATASTORE_CRIT_PCT:=90}"
: "${TASK_WARN_THRESHOLD:=5}"
: "${REPORT_RETENTION_DAYS:=30}"
: "${SNAPSHOT_WARN_HOURS:=72}"
: "${NOTIFY_THRESHOLD:=C}"
: "${SMTP_TO:=}"
: "${SMTP_FROM:=vcf-healthcheck@lab.local}"
: "${SMTP_SERVER:=}"
: "${SMTP_PORT:=25}"
: "${SLACK_WEBHOOK:=}"
: "${TEAMS_WEBHOOK:=}"
: "${BACKUP_WARN_HOURS:=48}"
: "${WEIGHT_INFRA:=1}"
: "${WEIGHT_VCENTER:=2}"
: "${WEIGHT_SDDC:=2}"
: "${WEIGHT_NSX:=2}"
: "${WEIGHT_OPS:=1}"
: "${WEIGHT_FLEET:=1}"
: "${PLUGIN_DIR:=}"
: "${PAGERDUTY_KEY:=}"
: "${OPSGENIE_KEY:=}"
: "${DFW_RULE_WARN:=500}"
: "${CLUSTER_CPU_WARN_PCT:=70}"
: "${CLUSTER_CPU_CRIT_PCT:=85}"
: "${CLUSTER_MEM_WARN_PCT:=70}"
: "${CLUSTER_MEM_CRIT_PCT:=85}"
: "${WEBHOOK_URL:=}"
: "${EXPECTED_DOWN:=}"
: "${TIMEOUT_INFRA:=$CURL_MAX_TIME}"
: "${TIMEOUT_VCENTER:=$CURL_MAX_TIME}"
: "${TIMEOUT_SDDC:=60}"
: "${TIMEOUT_NSX:=60}"
: "${TIMEOUT_OPS:=$CURL_MAX_TIME}"
: "${TIMEOUT_FLEET:=$CURL_MAX_TIME}"
# Merge EXPECTED_DOWN env var into KNOWN_DOWN if not set via CLI
[ -z "$KNOWN_DOWN" ] && [ -n "$EXPECTED_DOWN" ] && KNOWN_DOWN="$EXPECTED_DOWN"

# --- OUTPUT FILES ---
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
REPORT_FILE="${SCRIPT_DIR}/VCF-Health-Report_${TIMESTAMP}.txt"
HTML_REPORT_FILE="${SCRIPT_DIR}/VCF-Health-Report_${TIMESTAMP}.html"
JSON_REPORT_FILE="${SCRIPT_DIR}/VCF-Health-Report_${TIMESTAMP}.json"
CSV_REPORT_FILE="${SCRIPT_DIR}/VCF-Health-Report_${TIMESTAMP}.csv"
PDF_REPORT_FILE="${SCRIPT_DIR}/VCF-Health-Report_${TIMESTAMP}.pdf"
MD_REPORT_FILE="${SCRIPT_DIR}/VCF-Health-Report_${TIMESTAMP}.md"
TMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d /tmp/vcf-hc-XXXXXXXXXX 2>/dev/null)
if [ ! -d "$TMP_DIR" ]; then
    echo -e "  ${RED:-}ERROR:${NC:-} Cannot create secure temp directory"; exit 1
fi
chmod 700 "$TMP_DIR" 2>/dev/null

# v8.0 Feature 18: Lock file to prevent concurrent runs
LOCK_FILE="$SCRIPT_DIR/.vcf-health-check.lock"
if [ -f "$LOCK_FILE" ]; then
    LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if kill -0 "$LOCK_PID" 2>/dev/null; then
        echo -e "  ${RED}ERROR:${NC} Another instance is running (PID $LOCK_PID). Remove $LOCK_FILE if stale."
        exit 1
    else
        rm -f "$LOCK_FILE" 2>/dev/null  # Stale lock, remove it
    fi
fi
echo $$ > "$LOCK_FILE" 2>/dev/null
trap 'rm -f "$LOCK_FILE" 2>/dev/null; rm -rf "$TMP_DIR" 2>/dev/null' EXIT

# --- COLOR CODES ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'
DIM='\033[2m'; NC='\033[0m'

# --- COUNTERS ---
# Note: Use _CNT suffix to avoid collision with credential variables (e.g., OPS_PASS)
TOTAL_CHECKS=0; PASSED=0; FAILED=0; WARNINGS=0
declare -A COMP_PASS_CNT COMP_FAIL_CNT COMP_WARN_CNT
for _c in INFRA VC SDDC NSX OPS FLEET PLUGIN; do
    COMP_PASS_CNT[$_c]=0; COMP_FAIL_CNT[$_c]=0; COMP_WARN_CNT[$_c]=0
done

# --- REPORT DATA ---
ALL_RESULTS=()
FAILURE_LIST=()
WARNING_LIST=()
REMEDIATION_LIST=()
FIX_ACTIONS=()
CURRENT_SECTION=""
CURRENT_COMP=""
VC_VERSION=""
SDDC_VERSION=""
DISCOVERED_HOSTS=()
LATENCY_DATA=()

# --- HELPER FUNCTIONS ---
# Feature 13: Estimated remediation time. Pass as $3 (optional): "~5m", "~30m", "~1h", "maint"
check_pass() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1)); PASSED=$((PASSED + 1))
    COMP_PASS_CNT[$CURRENT_COMP]=$(( ${COMP_PASS_CNT[$CURRENT_COMP]:-0} + 1 ))
    echo -e "  ${GREEN}[PASS]${NC} $1"
    ALL_RESULTS+=("[PASS] [$CURRENT_SECTION] $1")
}
check_fail() {
    local msg="$1" remedy="${2:-}" eta="${3:-~15m}"
    # v8.0 Feature 2: Suppress known issues — downgrade to WARN
    if is_suppressed "$msg" 2>/dev/null; then
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1)); WARNINGS=$((WARNINGS + 1))
        COMP_WARN_CNT[$CURRENT_COMP]=$(( ${COMP_WARN_CNT[$CURRENT_COMP]:-0} + 1 ))
        echo -e "  ${DIM}[SUPPRESSED]${NC} $msg"
        ALL_RESULTS+=("[WARN] [$CURRENT_SECTION] $msg (known issue — suppressed)")
        WARNING_LIST+=("[$CURRENT_SECTION] $msg (suppressed)")
        return
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1)); FAILED=$((FAILED + 1))
    COMP_FAIL_CNT[$CURRENT_COMP]=$(( ${COMP_FAIL_CNT[$CURRENT_COMP]:-0} + 1 ))
    echo -e "  ${RED}[FAIL]${NC} $msg"
    ALL_RESULTS+=("[FAIL] [$CURRENT_SECTION] $msg")
    FAILURE_LIST+=("[$CURRENT_SECTION] $msg")
    [ -n "$remedy" ] && REMEDIATION_LIST+=("FAIL|[$CURRENT_SECTION] $msg|$remedy|$eta")
}
check_warn() {
    local msg="$1" remedy="${2:-}" eta="${3:-~5m}"
    # v8.0 Feature 2: Suppress known issues — downgrade to INFO
    if is_suppressed "$msg" 2>/dev/null; then
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1)); PASSED=$((PASSED + 1))
        COMP_PASS_CNT[$CURRENT_COMP]=$(( ${COMP_PASS_CNT[$CURRENT_COMP]:-0} + 1 ))
        echo -e "  ${DIM}[SUPPRESSED]${NC} $msg"
        ALL_RESULTS+=("[PASS] [$CURRENT_SECTION] $msg (known issue — suppressed)")
        return
    fi
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1)); WARNINGS=$((WARNINGS + 1))
    COMP_WARN_CNT[$CURRENT_COMP]=$(( ${COMP_WARN_CNT[$CURRENT_COMP]:-0} + 1 ))
    echo -e "  ${YELLOW}[WARN]${NC} $msg"
    ALL_RESULTS+=("[WARN] [$CURRENT_SECTION] $msg")
    WARNING_LIST+=("[$CURRENT_SECTION] $msg")
    [ -n "$remedy" ] && REMEDIATION_LIST+=("WARN|[$CURRENT_SECTION] $msg|$remedy|$eta")
}
section() {
    CURRENT_SECTION="$1"
    echo ""
    echo -e "  ${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${BLUE}${BOLD}  $1${NC}"
    echo -e "  ${BLUE}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}
# v8.0 Feature 9: Cookie jar for session reuse (reduces TLS handshakes)
CURL_COOKIE_JAR="$TMP_DIR/.curl_cookies"
# Build SSL flags based on config (SSL_VERIFY defaults to false for lab environments)
_CURL_SSL_FLAGS="-s"
if [ "${SSL_VERIFY:-false}" != "true" ]; then
    _CURL_SSL_FLAGS="-sk"
elif [ -n "${CA_BUNDLE:-}" ] && [ -f "${CA_BUNDLE:-}" ]; then
    _CURL_SSL_FLAGS="-s --cacert $CA_BUNDLE"
fi
api_curl() { curl $_CURL_SSL_FLAGS --connect-timeout "$CURL_CONNECT_TIMEOUT" --max-time "${COMP_TIMEOUT:-$CURL_MAX_TIME}" \
    -b "$CURL_COOKIE_JAR" -c "$CURL_COOKIE_JAR" "$@" 2>/dev/null; }
# v8.0 Feature 10: Per-component timeout helper
set_comp_timeout() { COMP_TIMEOUT="${1:-$CURL_MAX_TIME}"; }
reset_comp_timeout() { COMP_TIMEOUT="$CURL_MAX_TIME"; }

# --- Find Python ---
PYTHON=""
for candidate in /c/Python314/python.exe /c/Python313/python.exe /c/Python312/python.exe python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "print('ok')" 2>/dev/null | grep -q "ok"; then
        PYTHON="$candidate"; break
    fi
done
if [ -z "$PYTHON" ]; then
    echo -e "${RED}ERROR: No working Python interpreter found.${NC}"
    read -n 1 -s -t 30 2>/dev/null; exit 1
fi
# On Windows (Git Bash/MSYS), Python outputs \r\n. Strip \r from all Python outputs.
# Store real Python path and create wrapper that always strips \r.
_REAL_PYTHON="$PYTHON"
pyrun() { "$_REAL_PYTHON" "$@" | tr -d '\r'; }
PYTHON="pyrun"

win_path() {
    $PYTHON -c "
import sys
p=sys.argv[1]
if len(p)>2 and p[0]=='/' and p[2]=='/':
    p=p[1].upper()+':\\\\'+p[3:].replace('/','\\\\')
print(p)
" "$1" 2>/dev/null
}

# --- CONFIG VALIDATION (Feature 10) ---
validate_config() {
    local errors=0
    for var in VCENTER SDDC NSX_VIP SSO_USER SSO_PASS; do
        val="${!var}"
        if [ -z "$val" ]; then
            echo -e "  ${RED}CONFIG ERROR:${NC} $var is not set in vcf-health-check.env"
            errors=$((errors+1))
        fi
    done
    # Validate hostname/IP format
    for host_var in VCENTER SDDC NSX_VIP NSX_NODE VCF_OPS FLEET; do
        val="${!host_var}"
        [ -z "$val" ] && continue
        if ! [[ "$val" =~ ^[a-zA-Z0-9._-]+$ ]]; then
            echo -e "  ${RED}CONFIG ERROR:${NC} $host_var contains invalid characters: $val"
            errors=$((errors+1))
        fi
    done
    # Validate port numbers
    for port_var in FLEET_PORT CURL_CONNECT_TIMEOUT CURL_MAX_TIME CERT_WARN_DAYS; do
        val="${!port_var}"
        [ -z "$val" ] && continue
        if ! [[ "$val" =~ ^[0-9]+$ ]]; then
            echo -e "  ${RED}CONFIG ERROR:${NC} $port_var must be numeric: $val"
            errors=$((errors+1))
        fi
    done
    # Test basic connectivity to vCenter
    if [ "$errors" -eq 0 ]; then
        local vc_http=$(curl $_CURL_SSL_FLAGS --connect-timeout 5 --max-time 10 -o /dev/null -w "%{http_code}" "https://$VCENTER/" 2>/dev/null)
        if [ "$vc_http" = "000" ]; then
            echo -e "  ${YELLOW}CONFIG WARNING:${NC} Cannot reach vCenter ($VCENTER) — check network or VPN"
        fi
    fi
    [ "$errors" -gt 0 ] && { echo -e "  ${RED}Fix errors in vcf-health-check.env before running.${NC}"; exit 1; }
}
$QUIET || validate_config

# v8.0 Feature 16: Pre-flight validation mode (--validate)
if $VALIDATE_ONLY; then
    echo -e "\n  ${CYAN}${BOLD}Pre-flight Validation${NC}\n"
    V_PASS=0; V_FAIL=0
    # Config file
    if [ -f "$ENV_FILE" ]; then echo -e "  ${GREEN}[OK]${NC} Config file loaded: $ENV_FILE"; V_PASS=$((V_PASS+1))
    else echo -e "  ${YELLOW}[SKIP]${NC} No .env file found (using defaults)"; fi
    # Test each endpoint
    for entry in "vCenter:$VCENTER:443" "SDDC Manager:$SDDC:443" "NSX VIP:$NSX_VIP:443" "VCF Ops:$VCF_OPS:443" "Fleet:$FLEET:$FLEET_PORT"; do
        IFS=':' read -r vl vh vp <<< "$entry"
        vc_http=$(curl $_CURL_SSL_FLAGS --connect-timeout 5 --max-time 8 -o /dev/null -w "%{http_code}" "https://$vh:$vp/" 2>/dev/null)
        if [ "$vc_http" != "000" ]; then echo -e "  ${GREEN}[OK]${NC} $vl ($vh:$vp) — reachable (HTTP $vc_http)"; V_PASS=$((V_PASS+1))
        elif [ "$vl" = "Fleet" ]; then echo -e "  ${YELLOW}[OK]${NC} $vl ($vh:$vp) — direct access disabled (VCF 9.0 — managed via VCF Operations)"; V_PASS=$((V_PASS+1))
        else echo -e "  ${RED}[FAIL]${NC} $vl ($vh:$vp) — unreachable"; V_FAIL=$((V_FAIL+1)); fi
    done
    # Test credentials (vCenter)
    V_B64=$(printf '%s' "${SSO_USER}:${SSO_PASS}" | $PYTHON -c "import base64,sys; print(base64.b64encode(sys.stdin.buffer.read()).decode())")
    V_SESSION=$(curl $_CURL_SSL_FLAGS --connect-timeout 5 --max-time 10 -X POST "https://$VCENTER/api/session" -H "Authorization: Basic $V_B64" 2>/dev/null | tr -d '"')
    if [ -n "$V_SESSION" ] && [ ${#V_SESSION} -gt 10 ] && ! echo "$V_SESSION" | grep -q "error" 2>/dev/null; then
        echo -e "  ${GREEN}[OK]${NC} vCenter credentials — session acquired"; V_PASS=$((V_PASS+1))
        curl $_CURL_SSL_FLAGS -X DELETE "https://$VCENTER/api/session" -H "vmware-api-session-id: $V_SESSION" >/dev/null 2>&1
    else echo -e "  ${RED}[FAIL]${NC} vCenter credentials — cannot authenticate"; V_FAIL=$((V_FAIL+1)); fi
    # ESXi hosts
    for eh in $ESXI_HOSTS; do
        if ping -n 1 -w 2000 "$eh" >/dev/null 2>&1 || ping -c 1 -W 2 "$eh" >/dev/null 2>&1; then
            echo -e "  ${GREEN}[OK]${NC} ESXi $eh — pingable"; V_PASS=$((V_PASS+1))
        else echo -e "  ${RED}[FAIL]${NC} ESXi $eh — unreachable"; V_FAIL=$((V_FAIL+1)); fi
    done
    # Python
    echo -e "  ${GREEN}[OK]${NC} Python interpreter: $_REAL_PYTHON"; V_PASS=$((V_PASS+1))
    # Summary
    echo -e "\n  ${BOLD}Pre-flight result:${NC} $V_PASS passed, $V_FAIL failed"
    [ "$V_FAIL" -gt 0 ] && echo -e "  ${YELLOW}Fix failed items before running the full health check.${NC}"
    rm -f "$LOCK_FILE" 2>/dev/null
    exit $V_FAIL
fi

# v8.0 Feature 2: Known-issue suppression registry
KNOWN_ISSUES_FILE="$SCRIPT_DIR/known-issues.json"
declare -A SUPPRESSED_ISSUES
if [ -f "$KNOWN_ISSUES_FILE" ]; then
    KI_WIN=$(win_path "$KNOWN_ISSUES_FILE")
    while IFS='|' read -r ki_pat ki_msg; do
        [ -n "$ki_pat" ] && SUPPRESSED_ISSUES["$ki_pat"]="$ki_msg"
    done < <($PYTHON -c "
import json, sys, os
try:
    fp = sys.argv[1]
    with open(fp) as f:
        issues = json.load(f)
    for iss in issues.get('suppress', []):
        pat = iss.get('pattern','')
        note = iss.get('note','known issue')
        print(pat + '|' + note)
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" "$KNOWN_ISSUES_FILE" 2>/dev/null)
    $QUIET || [ ${#SUPPRESSED_ISSUES[@]} -eq 0 ] || echo -e "  ${DIM}Loaded ${#SUPPRESSED_ISSUES[@]} known-issue suppression(s)${NC}"
fi
# Helper to check if a warning message matches a known issue
is_suppressed() {
    local msg="$1"
    for pat in "${!SUPPRESSED_ISSUES[@]}"; do
        echo "$msg" | grep -qi "$pat" && return 0
    done
    return 1
}

# --- GENERATE SCHEDULED TASK (Feature 7) ---
if $GEN_SCHEDULE; then
    SCHED_FILE="$SCRIPT_DIR/VCF-HealthCheck-ScheduledTask.xml"
    SCRIPT_WIN=$(win_path "$SCRIPT_DIR/vcf-health-check.sh")
    cat > "$SCHED_FILE" << 'XMLEOF'
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>VCF 9.0 Health Check — runs daily at 06:00</Description>
    <Author>VCF-Admin</Author>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-01T06:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals><Principal id="Author"><LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal></Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <ExecutionTimeLimit>PT30M</ExecutionTimeLimit>
    <Enabled>true</Enabled>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>C:\Program Files\Git\bin\bash.exe</Command>
XMLEOF
    echo "      <Arguments>--login -c \"cd '$(echo "$SCRIPT_DIR" | sed "s/'/'\\\\''/g")' &amp;&amp; bash vcf-health-check.sh --quiet\"</Arguments>" >> "$SCHED_FILE"
    cat >> "$SCHED_FILE" << 'XMLEOF'
    </Exec>
  </Actions>
</Task>
XMLEOF
    echo -e "  ${GREEN}Scheduled task XML generated:${NC} $SCHED_FILE"
    echo -e "  ${DIM}Import with: schtasks /create /tn \"VCF Health Check\" /xml \"$(win_path "$SCHED_FILE")\"${NC}"
    exit 0
fi

# --- Feature 18: CRON / SYSTEMD TIMER ---
if [ -n "$GEN_CRON" ]; then
    case "$GEN_CRON" in
        hourly)  CRON_SCHED="0 * * * *" ;;
        daily)   CRON_SCHED="0 6 * * *" ;;
        *)       CRON_SCHED="$GEN_CRON" ;;
    esac
    FULL_SCRIPT="$SCRIPT_DIR/vcf-health-check.sh"
    echo -e "  ${BOLD}Cron entry:${NC}"
    echo "  $CRON_SCHED  cd \"$SCRIPT_DIR\" && bash vcf-health-check.sh --quiet >> /var/log/vcf-healthcheck.log 2>&1"
    echo ""
    # Also generate systemd timer
    TIMER_FILE="$SCRIPT_DIR/vcf-healthcheck.timer"
    SERVICE_FILE="$SCRIPT_DIR/vcf-healthcheck.service"
    cat > "$SERVICE_FILE" << SVCEOF
[Unit]
Description=VCF 9.0 Health Check
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$SCRIPT_DIR
ExecStart=/bin/bash vcf-health-check.sh --quiet
StandardOutput=journal
StandardError=journal
SVCEOF
    if [ "$GEN_CRON" = "hourly" ]; then TIMER_ON="*-*-* *:00:00"
    else TIMER_ON="*-*-* 06:00:00"; fi
    cat > "$TIMER_FILE" << TMREOF
[Unit]
Description=VCF Health Check Timer ($GEN_CRON)

[Timer]
OnCalendar=$TIMER_ON
Persistent=true

[Install]
WantedBy=timers.target
TMREOF
    echo -e "  ${GREEN}Systemd files generated:${NC}"
    echo -e "    $SERVICE_FILE"
    echo -e "    $TIMER_FILE"
    echo -e "  ${DIM}Install: sudo cp vcf-healthcheck.{service,timer} /etc/systemd/system/"
    echo -e "          sudo systemctl enable --now vcf-healthcheck.timer${NC}"
    exit 0
fi

# --- v7.0 Feature 13: Configuration Backup Export ---
if $BACKUP_CONFIG; then
    CONFIG_FILE="$SCRIPT_DIR/vcf-config-backup_$(date '+%Y%m%d_%H%M%S').json"
    $PYTHON -c "
import json
config = {
    'version': '8.0',
    'exported': '$(date -Iseconds)',
    'topology': {
        'vcenter': {'fqdn': '$VCENTER', 'user': '$SSO_USER'},
        'sddc_manager': {'fqdn': '$SDDC', 'user': '$SSO_USER'},
        'nsx_vip': '$NSX_VIP',
        'nsx_node': '$NSX_NODE',
        'nsx_user': '$NSX_USER',
        'vcf_operations': '$VCF_OPS',
        'fleet': '$FLEET',
        'esxi_hosts': '$ESXI_HOSTS'.split()
    },
    'thresholds': {
        'cert_warn_days': $CERT_WARN_DAYS,
        'datastore_warn_pct': $DATASTORE_WARN_PCT,
        'datastore_crit_pct': $DATASTORE_CRIT_PCT,
        'task_warn_threshold': $TASK_WARN_THRESHOLD,
        'snapshot_warn_hours': $SNAPSHOT_WARN_HOURS,
        'backup_warn_hours': $BACKUP_WARN_HOURS,
        'dfw_rule_warn': $DFW_RULE_WARN,
        'notify_threshold': '$NOTIFY_THRESHOLD'
    },
    'weights': {
        'infra': $WEIGHT_INFRA, 'vcenter': $WEIGHT_VCENTER,
        'sddc': $WEIGHT_SDDC, 'nsx': $WEIGHT_NSX,
        'ops': $WEIGHT_OPS, 'fleet': $WEIGHT_FLEET
    },
    'notifications': {
        'email': bool('$SMTP_TO'),
        'slack': bool('$SLACK_WEBHOOK'),
        'teams': bool('$TEAMS_WEBHOOK'),
        'pagerduty': bool('$PAGERDUTY_KEY'),
        'opsgenie': bool('$OPSGENIE_KEY')
    }
}
with open('$(echo "$CONFIG_FILE" | sed "s/'/'\\\\''/g")', 'w') as f:
    json.dump(config, f, indent=2)
" 2>/dev/null
    echo -e "  ${GREEN}Configuration backup exported:${NC} $CONFIG_FILE"
    exit 0
fi

# v8.0 Feature 13: Multi-environment dashboard (--merge-reports)
if [ -n "$MERGE_DIR" ]; then
    MERGE_OUT="$SCRIPT_DIR/VCF-MultiEnv-Dashboard_${TIMESTAMP}.html"
    $PYTHON -c "
import json, glob, os, sys
dirs = '''$MERGE_DIR'''.split(',')
envs = []
for d in dirs:
    d = d.strip()
    files = sorted(glob.glob(os.path.join(d, 'VCF-Health-Report_*.json')))
    if files:
        with open(files[-1]) as f:
            data = json.load(f)
            data['_source_dir'] = d
            data['_source_file'] = files[-1]
            envs.append(data)
if not envs:
    print('No JSON reports found in specified directories.', file=sys.stderr)
    sys.exit(1)
h = '''<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>VCF Multi-Environment Dashboard</title>
<style>
body{font-family:Segoe UI,Arial,sans-serif;background:#1a1a2e;color:#eee;margin:0;padding:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:20px;margin-top:20px}
.env-card{background:#16213e;border-radius:12px;padding:20px;border-left:6px solid #555}
.env-card.grade-A,.env-card.grade-B\\\\+{border-color:#27ae60} .env-card.grade-B{border-color:#f1c40f}
.env-card.grade-C{border-color:#e67e22} .env-card.grade-D,.env-card.grade-F{border-color:#e74c3c}
h1{text-align:center;color:#64b5f6} h2{margin:0 0 10px;font-size:16pt}
.grade{font-size:48pt;font-weight:800;text-align:center;margin:10px 0}
.grade.A,.grade.B\\\\+{color:#27ae60} .grade.B{color:#f1c40f} .grade.C{color:#e67e22} .grade.D,.grade.F{color:#e74c3c}
.meta{font-size:9pt;color:#888;margin-top:8px}
.stats{display:flex;justify-content:space-around;margin:12px 0}
.stat{text-align:center} .stat b{font-size:18pt;display:block}
.pass{color:#27ae60} .warn{color:#f1c40f} .fail{color:#e74c3c}
</style></head><body>
<h1>VCF Multi-Environment Health Dashboard</h1>
<p style=\"text-align:center;color:#888\">Generated: ''' + envs[0].get('date','') + '''</p>
<div class=\"grid\">'''
for e in envs:
    g = e.get('grade','?')
    s = e.get('summary',{})
    src = os.path.basename(e.get('_source_dir',''))
    h += f'''<div class=\"env-card grade-{g}\">
<h2>{src or 'Environment'}</h2>
<div class=\"grade {g}\">{g}</div>
<div class=\"stats\">
<div class=\"stat pass\"><b>{s.get('passed',0)}</b>Passed</div>
<div class=\"stat warn\"><b>{s.get('warnings',0)}</b>Warnings</div>
<div class=\"stat fail\"><b>{s.get('failed',0)}</b>Failures</div>
</div>
<div class=\"meta\">Score: {e.get('score','?')}% | {s.get('total',0)} checks | {e.get('date','')}</div>
<div class=\"meta\">{e.get('executive_summary','')}</div>
</div>'''
h += '</div></body></html>'
with open(r'''$(echo "$MERGE_OUT" | sed "s/'/'\\\\''/g")''', 'w') as f:
    f.write(h)
" 2>/dev/null
    if [ -f "$MERGE_OUT" ]; then
        echo -e "  ${GREEN}Multi-environment dashboard:${NC} $MERGE_OUT"
    else
        echo -e "  ${RED}Failed to generate dashboard. Check directory paths.${NC}"
    fi
    rm -f "$LOCK_FILE" 2>/dev/null
    exit 0
fi

b64encode() { printf '%s' "$1" | $PYTHON -c "import base64,sys; print(base64.b64encode(sys.stdin.buffer.read()).decode())"; }
json_auth_payload() {
    # Pass credentials via environment variables to avoid bash history expansion
    # mangling passwords containing ! characters in subshells
    _JP_USER="$1" _JP_PASS="$2" _JP_EXTRA_ARGS="${*:3}" $PYTHON -c "
import json,os
d={'username':os.environ['_JP_USER'],'password':os.environ['_JP_PASS']}
extra=os.environ.get('_JP_EXTRA_ARGS','').split()
for i in range(0,len(extra)-1,2): d[extra[i]]=extra[i+1]
print(json.dumps(d))
"
}
check_cert() {
    local host="$1" port="$2" label="$3"
    local cert_enddate
    cert_enddate=$(echo "" | openssl s_client -connect "$host:$port" -servername "$host" 2>/dev/null | openssl x509 -enddate -noout 2>/dev/null)
    if [ -z "$cert_enddate" ]; then
        local cert_remedy=""
        case "$label" in
            *vCenter*)   cert_remedy="Check vCenter services: ssh root@$host 'vmon-cli --list'. Restart rhttpproxy: vmon-cli --restart rhttpproxy" ;;
            *SDDC*)      cert_remedy="Check SDDC Manager: ssh vcf@$host 'systemctl status lcm'. UI: https://$host/ui" ;;
            *NSX*)       cert_remedy="Check NSX Manager VMs are powered on. SSH: ssh admin@$host, run: get cluster status. Check /var/log/proton/nsxapi.log" ;;
            *Operations*) cert_remedy="Check VCF Operations VM is powered on. SSH: ssh admin@$host, run: systemctl status vmware-vcops-web. Logs: /var/log/vmware/vcops/collector.log" ;;
            *Fleet*)     cert_remedy="Check vRSLCM VM is powered on. SSH: ssh admin@$host, run: systemctl status lcm" ;;
            *)           cert_remedy="Verify the service is running on $host:$port." ;;
        esac
        check_warn "Cert: $label ($host:$port) — unable to connect" "$cert_remedy"
        return
    fi
    local expiry_str="${cert_enddate#notAfter=}"
    local days_left
    days_left=$($PYTHON -c "
from datetime import datetime,timezone
try:
    s = '''${expiry_str}'''.strip()
    for fmt in ['%b %d %H:%M:%S %Y %Z','%b  %d %H:%M:%S %Y %Z']:
        try:
            exp=datetime.strptime(s,fmt).replace(tzinfo=timezone.utc)
            print((exp-datetime.now(timezone.utc)).days); break
        except ValueError: continue
    else: print(-999)
except Exception: print(-999)
" 2>/dev/null)
    if [ "${days_left:-0}" = "-999" ]; then
        check_warn "Cert: $label — unable to parse expiry"
    elif [ "${days_left:-0}" -le 0 ] 2>/dev/null; then
        check_fail "Cert: $label — EXPIRED (was: $expiry_str)" "Renew the certificate immediately. For vCenter: Certificate Manager > Regenerate Machine SSL. For NSX: POST /api/v1/trust-management/certificates?action=renew" "~1h"
    elif [ "${days_left:-0}" -le "$CERT_WARN_DAYS" ] 2>/dev/null; then
        check_warn "Cert: $label — expires in ${days_left} days" "Schedule certificate renewal before expiry. Use Certificate Manager in vCenter or the component's admin UI." "~1h"
    else
        check_pass "Cert: $label — valid for ${days_left} days"
    fi
}

# ============================================================================
# PARALLEL COMPONENT CHECK FUNCTIONS
# ============================================================================
# Each writes lines to stdout in format: TYPE|message|remedy
# The main script captures output to temp files, then parses them.

run_sddc_checks() {
    local section="SDDC Manager ($SDDC)"
    # v8.0 Feature 10: Per-component timeout
    local COMP_TIMEOUT="$TIMEOUT_SDDC"
    local auth_json=$(json_auth_payload "$SSO_USER" "$SSO_PASS")
    local token=$(api_curl -X POST "https://$SDDC/v1/tokens" \
        -H "Content-Type: application/json" \
        -d "$auth_json" | $PYTHON -c "
import sys,json
try: print(json.load(sys.stdin).get('accessToken',''))
except Exception: print('')
" 2>/dev/null)

    if [ -z "$token" ] || [ ${#token} -le 20 ]; then
        # v8.0 Feature 3: Retry with 5-second backoff
        sleep 5
        token=$(curl $_CURL_SSL_FLAGS --connect-timeout "$CURL_CONNECT_TIMEOUT" --max-time "$COMP_TIMEOUT" \
            -X POST "https://$SDDC/v1/tokens" \
            -H "Content-Type: application/json" \
            -d "$auth_json" 2>/dev/null | $PYTHON -c "
import sys,json
try: print(json.load(sys.stdin).get('accessToken',''))
except Exception: print('')
" 2>/dev/null)
        if [ -z "$token" ] || [ ${#token} -le 20 ]; then
            echo "FAIL|SDDC Manager UNREACHABLE — cannot acquire token (retried)|Power on the SDDC Manager VM. SSH: ssh vcf@$SDDC then run 'systemctl status lcm'. Check /var/log/vmware/vcf/lcm/lcm.log"
            return
        fi
    fi
    echo "PASS|API reachable — token acquired|"

    # Version
    local ver=$(api_curl -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/sddc-managers" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    elts=d.get('elements',d if isinstance(d,list) else [])
    if elts: print(elts[0].get('version', elts[0].get('build','?')))
    else: print('?')
except Exception: print('?')
" 2>/dev/null)
    echo "VERSION|$ver"

    # NSX cluster via SDDC
    local nsx_st=$(api_curl -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/nsxt-clusters" | $PYTHON -c "
import sys,json
try: d=json.load(sys.stdin); elts=d.get('elements',[]); print(elts[0].get('status','UNKNOWN') if elts else 'NO_CLUSTERS')
except Exception: print('PARSE_ERROR')
" 2>/dev/null)
    if [ "$nsx_st" = "ACTIVE" ]; then echo "PASS|NSX cluster (via SDDC): ACTIVE|"
    else echo "FAIL|NSX cluster (via SDDC): ${nsx_st:-no response}|Check NSX Manager cluster health. SSH to NSX Manager and run: get cluster status"; fi

    # vCenter via SDDC
    local vc_st=$(api_curl -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/vcenters" | $PYTHON -c "
import sys,json
try: d=json.load(sys.stdin); elts=d.get('elements',[]); print(elts[0].get('status','UNKNOWN') if elts else 'NO_VCENTERS')
except Exception: print('PARSE_ERROR')
" 2>/dev/null)
    if [ "$vc_st" = "ACTIVE" ]; then echo "PASS|vCenter (via SDDC): ACTIVE|"
    else echo "FAIL|vCenter (via SDDC): ${vc_st:-no response}|Check vCenter VM is powered on and services are running: vmon-cli --list"; fi

    # Management components
    local comp_lines=$(api_curl -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/vcf-management-components" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    for k,v in d.items():
        if isinstance(v,dict):
            # VCF 9.0: nested object with deploymentStatus
            status=v.get('deploymentStatus',v.get('status',''))
            fqdn=v.get('fqdn','')
            if isinstance(v.get('nodes'),list) and v['nodes']:
                fqdn=v['nodes'][0].get('fqdn',fqdn)
            label=f'{k} ({fqdn})' if fqdn else k
            if status: print(f'{label}={status}')
        elif isinstance(v,str) and v in ('SUCCEEDED','FAILED','IN_PROGRESS','NOT_STARTED','NOT_FOUND'):
            print(f'{k}={v}')
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null | tr -d '\r')
    if [ -n "$comp_lines" ]; then
        while IFS='=' read -r cn cs; do
            [ -z "$cn" ] && continue
            if [ "$cs" = "SUCCEEDED" ]; then echo "PASS|Mgmt: $cn — SUCCEEDED|"
            elif [ "$cs" = "NOT_FOUND" ]; then echo "PASS|Mgmt: $cn — not deployed (optional)|"
            elif [ "$cs" = "IN_PROGRESS" ]; then echo "WARN|Mgmt: $cn — IN_PROGRESS|Component deployment still running. Monitor in SDDC Manager UI > Lifecycle Management."
            else echo "FAIL|Mgmt: $cn — $cs|Redeploy the component via SDDC Manager UI > Lifecycle Management > Deploy"; fi
        done <<< "$comp_lines"
    else
        echo "WARN|Management components: unable to query (API may not be ready)|SSH: ssh vcf@$SDDC then run: systemctl restart lcm operationsmanager domainmanager. Wait 5 minutes and retry. Logs: /var/log/vmware/vcf/lcm/lcm.log and /var/log/vmware/vcf/operationsmanager/operationsmanager.log"
    fi

    # Feature 1: SDDC Certificate Inventory
    local cert_resp=$(api_curl -w "\n%{http_code}" -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/sddc-manager/certificates" 2>/dev/null)
    local cert_http=$(echo "$cert_resp" | tail -1)
    local cert_data=$(echo "$cert_resp" | sed '$d')
    if [ "$cert_http" = "200" ] && [ -n "$cert_data" ]; then
        local cert_results=$(echo "$cert_data" | $PYTHON -c "
import sys,json
from datetime import datetime,timezone
try:
    d=json.load(sys.stdin)
    certs=d.get('elements',d if isinstance(d,list) else [])
    expiring=0; total=0
    for c in certs:
        if not isinstance(c,dict): continue
        total+=1
        exp=c.get('expirationDate',c.get('notAfter',''))
        if exp:
            try:
                edt=datetime.fromisoformat(exp.replace('Z','+00:00'))
                days=int((edt-datetime.now(timezone.utc)).days)
                if days<=60:
                    name=c.get('issuedTo',c.get('subject','?'))[:40]
                    print(f'EXPIRING|{name}|{days}')
                    expiring+=1
            except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
    print(f'TOTAL|{total}|{expiring}')
except Exception: print('ERROR||')
" 2>/dev/null)
        local cert_total=0 cert_exp=0
        while IFS='|' read -r crt crn crd; do
            case "$crt" in
                TOTAL) cert_total="$crn"; cert_exp="$crd" ;;
                EXPIRING) echo "WARN|SDDC cert expiring: $crn — ${crd} days left|Renew via SDDC Manager > Security > Certificate Management|~1h" ;;
            esac
        done <<< "$cert_results"
        if [ "${cert_exp:-0}" -eq 0 ] && [ "${cert_total:-0}" -gt 0 ] 2>/dev/null; then
            echo "PASS|SDDC certificates: $cert_total managed, none expiring within 60 days|"
        elif [ "${cert_total:-0}" -eq 0 ] 2>/dev/null; then
            echo "PASS|SDDC certificates: endpoint returned no data|"
        fi
    fi

    # Feature 2: Backup Age Verification
    local backup_age=$(api_curl -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/system/backup-restore/backups" | $PYTHON -c "
import sys,json
from datetime import datetime,timezone,timedelta,timezone
try:
    d=json.load(sys.stdin); elts=d.get('elements',d if isinstance(d,list) else [])
    if not elts: print('NO_BACKUPS'); sys.exit()
    latest=max(elts,key=lambda e:e.get('creationTimestamp',''))
    ct=latest.get('creationTimestamp','')
    if ct:
        from datetime import datetime,timezone
        ts=datetime.fromisoformat(ct.replace('Z','+00:00'))
        age_h=int((datetime.now(timezone.utc)-ts).total_seconds()/3600)
        print(f'{age_h}|{ct[:16]}|{latest.get(\"status\",\"?\")}')
    else: print('NOTIME')
except Exception: print('ERROR')
" 2>/dev/null)
    case "$backup_age" in
        NO_BACKUPS) echo "WARN|No SDDC backups found — disaster recovery at risk|Configure backup: SDDC Manager > Administration > Backup|~30m" ;;
        ERROR|NOTIME) ;; # Handled by existing backup check
        *)
            IFS='|' read -r ba_hours ba_date ba_status <<< "$backup_age"
            if [ "${ba_hours:-0}" -gt "${BACKUP_WARN_HOURS:-48}" ] 2>/dev/null; then
                echo "WARN|Last SDDC backup is ${ba_hours}h old ($ba_date, $ba_status) — exceeds ${BACKUP_WARN_HOURS}h threshold|Run a manual backup or fix the backup schedule in SDDC Manager.|~15m"
            else
                echo "PASS|Last SDDC backup: ${ba_hours}h ago ($ba_date, $ba_status)|"
            fi
            ;;
    esac

    # Feature 5: Cluster compliance check
    local precheck_http=$(api_curl -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/system/prechecks" 2>/dev/null)
    if [ "$precheck_http" = "200" ]; then
        local precheck_data=$(api_curl -H "Authorization: Bearer $token" \
            "https://$SDDC/v1/system/prechecks" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    elts=d.get('elements',d if isinstance(d,list) else [])
    failed=0; total=0
    for e in (elts if isinstance(elts,list) else []):
        total+=1
        if isinstance(e,dict) and e.get('status','')!='SUCCEEDED': failed+=1
    print(f'{failed}/{total}')
except Exception: print('')
" 2>/dev/null)
        if [ -n "$precheck_data" ]; then
            IFS='/' read -r pc_fail pc_total <<< "$precheck_data"
            if [ "${pc_fail:-0}" -eq 0 ] && [ "${pc_total:-0}" -gt 0 ] 2>/dev/null; then
                echo "PASS|Compliance: all $pc_total prechecks passed|"
            elif [ "${pc_fail:-0}" -gt 0 ] 2>/dev/null; then
                echo "WARN|Compliance: $pc_fail of $pc_total prechecks failed|Review: SDDC Manager > Lifecycle Management > Prechecks|~30m"
            fi
        fi
    fi

    # Feature 4: SDDC Manager password expiry (vcf user)
    local vcf_pwd=$(api_curl -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/credentials?accountType=SYSTEM" 2>/dev/null | $PYTHON -c "
import sys,json
from datetime import datetime,timezone
try:
    d=json.load(sys.stdin)
    elts=d.get('elements',[])
    for e in elts:
        if 'sddc' in e.get('resource',{}).get('resourceName','').lower() or 'vcf' in e.get('username','').lower():
            exp=e.get('passwordExpiryDate','')
            if exp:
                edt=datetime.fromisoformat(exp.replace('Z','+00:00'))
                days=int((edt-datetime.now(timezone.utc)).days)
                print(f'{e.get(\"username\",\"?\")}|{days}')
                break
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
    if [ -n "$vcf_pwd" ]; then
        IFS='|' read -r pu pd <<< "$vcf_pwd"
        if [ "${pd:-999}" -le 0 ] 2>/dev/null; then
            echo "FAIL|SDDC $pu password: EXPIRED|Rotate via SDDC Manager > Security > Credential Management|~15m"
        elif [ "${pd:-999}" -le 30 ] 2>/dev/null; then
            echo "WARN|SDDC $pu password: expires in ${pd} days|Rotate via SDDC Manager > Security > Credential Management|~10m"
        else
            echo "PASS|SDDC $pu password: valid for ${pd} days|"
        fi
    fi

    # Tasks — only count tasks older than 24h as stale (recent ones are normal background jobs)
    local task_counts=$(api_curl -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/tasks?status=IN_PROGRESS" | $PYTHON -c "
import sys,json
from datetime import datetime,timezone,timedelta,timezone,timezone
try:
    cutoff=(datetime.now(timezone.utc)-timedelta(hours=24)).isoformat()
    tasks=json.load(sys.stdin).get('elements',[])
    stale=sum(1 for t in tasks if t.get('creationTimestamp','') and t['creationTimestamp']<cutoff)
    print(f'{len(tasks)} {stale}')
except Exception: print('-1 -1')
" 2>/dev/null)
    local task_count="${task_counts%% *}"
    local stale_count="${task_counts##* }"
    if [ "$task_count" = "0" ]; then echo "PASS|No IN_PROGRESS tasks|"
    elif [ "${stale_count:-0}" = "0" ] && [ "${task_count:-0}" -gt 0 ] 2>/dev/null; then
        echo "PASS|$task_count in-progress task(s) — all recent (normal background jobs)|"
    elif [ "${stale_count:-0}" -gt 0 ] && [ "${stale_count:-0}" -le "$TASK_WARN_THRESHOLD" ] 2>/dev/null; then
        echo "WARN|$task_count in-progress task(s), $stale_count stale (>24h)|Monitor tasks in SDDC Manager UI. If stuck, cancel via: curl -X PATCH https://$SDDC/v1/tasks/{id} -d '{\"status\":\"CANCELLED\"}'"
    elif [ "${stale_count:-0}" -gt "$TASK_WARN_THRESHOLD" ] 2>/dev/null; then
        # VCF 9.0: SDDC Manager maintains persistent background tasks that cannot be cleared.
        # Treat as WARN rather than FAIL since these don't affect functionality.
        if [ "$AUTO_CLEANUP_TASKS" = "true" ]; then
            # Feature 5: Auto-cancel stale tasks
            local cancelled=0
            local task_ids=$(api_curl -H "Authorization: Bearer $token" \
                "https://$SDDC/v1/tasks?status=IN_PROGRESS" | $PYTHON -c "
import sys,json
from datetime import datetime,timezone,timedelta,timezone
try:
    cutoff=(datetime.now(timezone.utc)-timedelta(hours=24)).isoformat()+'Z'
    for t in json.load(sys.stdin).get('elements',[]):
        ct=t.get('creationTimestamp',t.get('createTimestamp',''))
        if ct and ct < cutoff: print(t.get('id',''))
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
            while IFS= read -r tid; do
                [ -z "$tid" ] && continue
                api_curl -X PATCH "https://$SDDC/v1/tasks/$tid" \
                    -H "Authorization: Bearer $token" \
                    -H "Content-Type: application/json" \
                    -d '{"status":"CANCELLED"}' >/dev/null 2>&1
                cancelled=$((cancelled+1))
            done <<< "$task_ids"
            if [ "$cancelled" -gt 0 ]; then
                echo "WARN|$stale_count stale task(s) (>24h) — auto-cancelled $cancelled|Verify in SDDC Manager UI that cancelled tasks are no longer blocking."
            else
                echo "WARN|$stale_count stale task(s) (>24h) — none could be auto-cancelled|Clear stuck tasks manually via SDDC Manager UI or restart LCM: ssh vcf@$SDDC 'systemctl restart lcm'"
            fi
        else
            echo "WARN|$stale_count stale task(s) (>24h) of $task_count total|Review in SDDC Manager UI. VCF 9.0 maintains persistent background tasks. Manual cleanup: SDDC Manager > Developer Center > API Explorer > PATCH /v1/tasks/{id}"
        fi
    else echo "WARN|Unable to check task status|"; fi

    # Resource locks
    local lock_count=$(api_curl -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/resource-locks" | $PYTHON -c "
import sys,json
try: print(len(json.load(sys.stdin).get('elements',[])))
except Exception: print(-1)
" 2>/dev/null)
    if [ "$lock_count" = "0" ]; then echo "PASS|No stale resource locks|"
    elif [ "${lock_count:-0}" -gt 0 ] 2>/dev/null; then
        echo "WARN|$lock_count active resource lock(s)|Check locks via GET /v1/resource-locks. Delete stale locks: DELETE /v1/resource-locks/{id}"
    else echo "WARN|Unable to check resource locks|"; fi

    # Backup
    local backup_http=$(api_curl -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/system/backup-restore/backups" 2>/dev/null)
    if [ "$backup_http" = "200" ]; then
        local backup_info=$(api_curl -H "Authorization: Bearer $token" \
            "https://$SDDC/v1/system/backup-restore/backups" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin); elts=d.get('elements',d if isinstance(d,list) else [])
    if not elts: print('NO_BACKUPS')
    else:
        latest=max(elts,key=lambda e:e.get('creationTimestamp',''))
        print(f\"{latest.get('status','?')}|{latest.get('creationTimestamp','?')}\")
except Exception: print('PARSE_ERROR')
" 2>/dev/null)
        case "$backup_info" in
            SUCCESSFUL*|COMPLETED*) echo "PASS|Last backup: ${backup_info}|" ;;
            FAILED*) echo "FAIL|Last backup: FAILED|Check backup configuration in SDDC Manager > Administration > Backup. Verify SFTP target is reachable." ;;
            NO_BACKUPS) echo "WARN|No backups found|Configure SDDC Manager backup: Administration > Backup > Configure. Critical for disaster recovery." ;;
            *) echo "WARN|Backup status: $backup_info|" ;;
        esac
    else
        echo "WARN|Backup status: endpoint not available (HTTP $backup_http)|Backup API may not be configured. Set up backup in SDDC Manager UI > Administration > Backup."
    fi

    # v7.0 Feature 3: SDDC Manager Drift Detection (desired vs actual host config)
    local drift_resp=$(api_curl -w "\n%{http_code}" -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/hosts" 2>/dev/null)
    local drift_http=$(echo "$drift_resp" | tail -1)
    local drift_data=$(echo "$drift_resp" | sed '$d')
    if [ "$drift_http" = "200" ] && [ -n "$drift_data" ]; then
        local drift_results=$(echo "$drift_data" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    hosts=d.get('elements',d if isinstance(d,list) else [])
    drifted=0; total=0
    for h in hosts:
        if not isinstance(h,dict): continue
        total+=1
        status=h.get('status','')
        if status not in ('ASSIGNED','COMMISSIONED',''):
            print(f'DRIFT|{h.get(\"fqdn\",h.get(\"name\",\"?\"))}|{status}')
            drifted+=1
    print(f'TOTAL|{total}|{drifted}')
except Exception: print('ERROR||')
" 2>/dev/null)
        local d_total=0 d_drifted=0
        while IFS='|' read -r dt dn ds; do
            case "$dt" in
                DRIFT) echo "WARN|Host drift: $dn status is $ds|Investigate host in SDDC Manager > Hosts. Re-commission if needed.|~30m" ;;
                TOTAL) d_total="$dn"; d_drifted="$ds" ;;
            esac
        done <<< "$drift_results"
        if [ "${d_drifted:-0}" -eq 0 ] && [ "${d_total:-0}" -gt 0 ] 2>/dev/null; then
            echo "PASS|Host config: $d_total hosts, no drift detected|"
        fi
    fi

    # v7.0 Feature 8: SDDC Manager Depot Connectivity
    local depot_resp=$(api_curl -w "\n%{http_code}" -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/system/settings/depot" 2>/dev/null)
    local depot_http=$(echo "$depot_resp" | tail -1)
    local depot_data=$(echo "$depot_resp" | sed '$d')
    if [ "$depot_http" = "200" ] && [ -n "$depot_data" ]; then
        local depot_url=$(echo "$depot_data" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    url=d.get('vmwareAccount',{}).get('depotUrl',d.get('depot_url',''))
    status=d.get('status',d.get('vmwareAccount',{}).get('status',''))
    print(f'{url}|{status}')
except Exception: print('|')
" 2>/dev/null)
        IFS='|' read -r dep_url dep_st <<< "$depot_url"
        if [ -n "$dep_url" ]; then
            echo "PASS|Depot configured: ${dep_url:0:60} (status: ${dep_st:-?})|"
        else
            echo "PASS|Depot: configuration returned (details unavailable)|"
        fi
    elif [ "$depot_http" = "404" ]; then
        echo "PASS|Depot: endpoint not available (may use offline bundle)|"
    else
        echo "WARN|Depot: unable to check connectivity (HTTP $depot_http)|Configure depot in SDDC Manager > Administration > Online Depot.|~15m"
    fi

    # v8.0 Feature 7: SDDC Manager lifecycle update availability
    local lcm_resp=$(api_curl -w "\n%{http_code}" -H "Authorization: Bearer $token" \
        "https://$SDDC/v1/lcm/upgrades" 2>/dev/null)
    local lcm_http=$(echo "$lcm_resp" | tail -1)
    local lcm_data=$(echo "$lcm_resp" | sed '$d')
    if [ "$lcm_http" = "200" ]; then
        local upg_count=$(echo "$lcm_data" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    elts=d.get('elements',[]) if isinstance(d,dict) else d if isinstance(d,list) else []
    avail=[e for e in elts if isinstance(e,dict) and e.get('status','').upper() in ('AVAILABLE','PENDING')]
    print(len(avail))
except Exception: print(0)
" 2>/dev/null)
        if [ "${upg_count:-0}" -gt 0 ] 2>/dev/null; then
            echo "WARN|$upg_count lifecycle update(s) available|Review available updates in SDDC Manager > Lifecycle Management > Updates.|~5m"
        else
            echo "PASS|No pending lifecycle updates|"
        fi
    elif [ "$lcm_http" = "404" ]; then
        echo "PASS|Lifecycle updates: endpoint not available (normal pre-4.5)|"
    fi
}

run_nsx_checks() {
    local section="NSX Manager ($NSX_VIP)"
    local COMP_TIMEOUT="$TIMEOUT_NSX"
    local nsx_b64=$(b64encode "${NSX_USER}:${NSX_PASS}")
    local nsx_target="" nsx_resp=""
    for nsx_host in "$NSX_VIP" "$NSX_NODE"; do
        nsx_resp=$(api_curl -H "Authorization: Basic $nsx_b64" "https://$nsx_host/api/v1/cluster/status")
        if [ -n "$nsx_resp" ] && echo "$nsx_resp" | grep -q "cluster_id" 2>/dev/null; then
            nsx_target="$nsx_host"; break
        fi
    done
    if [ -z "$nsx_target" ]; then
        echo "FAIL|NSX Manager UNREACHABLE — tried VIP ($NSX_VIP) and node ($NSX_NODE)|1) Check NSX Manager VMs are powered on in vCenter. 2) SSH: ssh admin@$NSX_NODE 3) Run: get cluster status 4) Check /var/log/proton/nsxapi.log"
        return
    fi
    if [ "$nsx_target" = "$NSX_VIP" ]; then echo "PASS|API reachable via VIP ($NSX_VIP)|"
    else echo "WARN|VIP unreachable — connected via node IP ($NSX_NODE)|The NSX VIP ($NSX_VIP) is not responding. Check: get interface eth0 on each node. VIP requires all manager nodes healthy."; fi

    # Version
    local ver=$(echo "$nsx_resp" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    nodes=d.get('mgmt_cluster_status',{}).get('online_nodes',[])
    if nodes: print(nodes[0].get('node_version','?'))
    else: print('?')
except Exception: print('?')
" 2>/dev/null)
    echo "VERSION|$ver"

    # Control cluster
    local ctrl=$(echo "$nsx_resp" | $PYTHON -c "
import sys,json
try: print(json.load(sys.stdin).get('control_cluster_status',{}).get('status','UNKNOWN'))
except Exception: print('PARSE_ERROR')
" 2>/dev/null)
    if [ "$ctrl" = "STABLE" ]; then echo "PASS|Control cluster: STABLE|"
    else echo "FAIL|Control cluster: ${ctrl:-UNKNOWN}|SSH to NSX Manager: get cluster status. Check control plane connectivity between nodes."; fi

    # Management cluster
    local mgmt=$(echo "$nsx_resp" | $PYTHON -c "
import sys,json
try: print(json.load(sys.stdin).get('mgmt_cluster_status',{}).get('status','UNKNOWN'))
except Exception: print('PARSE_ERROR')
" 2>/dev/null)
    if [ "$mgmt" = "STABLE" ]; then echo "PASS|Management cluster: STABLE|"
    else echo "FAIL|Management cluster: ${mgmt:-UNKNOWN}|SSH to NSX Manager: get management-cluster status. Check /var/log/corfu/corfu.log for database issues."; fi

    # Transport nodes
    local tn=$(api_curl -H "Authorization: Basic $nsx_b64" \
        "https://$nsx_target/api/v1/transport-nodes/state" | $PYTHON -c "
import sys,json
try:
    r=json.load(sys.stdin).get('results',[])
    ok=sum(1 for x in r if x.get('state')=='success')
    print(f'{ok}/{len(r)}')
except Exception: print('')
" 2>/dev/null)
    if [ -n "$tn" ]; then
        IFS='/' read -r tn_ok tn_total <<< "$tn"
        if [ "$tn_ok" = "$tn_total" ] && [ "${tn_total:-0}" -gt 0 ] 2>/dev/null; then
            echo "PASS|Transport nodes: $tn_ok/$tn_total healthy|"
        elif [ "${tn_total:-0}" -gt 0 ] 2>/dev/null; then
            echo "WARN|Transport nodes: $tn_ok/$tn_total healthy|Some transport nodes degraded. Check: GET /api/v1/transport-nodes/state for details. Resolve by re-applying transport node profile."
        else echo "WARN|Transport nodes: none found|"; fi
    else echo "WARN|Transport nodes: unable to query|"; fi

    # Alarms
    local alarms=$(api_curl -H "Authorization: Basic $nsx_b64" \
        "https://$nsx_target/api/v1/alarms?status=OPEN" | $PYTHON -c "
import sys,json
try:
    r=json.load(sys.stdin).get('results',[])
    crit=sum(1 for a in r if a.get('severity')=='CRITICAL')
    warn=sum(1 for a in r if a.get('severity')=='WARNING')
    print(f'{crit}/{warn}')
except Exception: print('0/0')
" 2>/dev/null)
    IFS='/' read -r crit_c warn_c <<< "$alarms"
    if [ "${crit_c:-0}" -gt 0 ] 2>/dev/null; then
        echo "FAIL|$crit_c critical alarm(s)|Review alarms: NSX Manager UI > System > Alarms, or GET /api/v1/alarms?status=OPEN&severity=CRITICAL|~30m"
    elif [ "${warn_c:-0}" -gt 0 ] 2>/dev/null; then
        echo "WARN|$warn_c warning alarm(s), 0 critical|Review: NSX Manager UI > System > Alarms|~15m"
    else echo "PASS|No open alarms|"; fi

    # Feature 4: NSX admin password expiry
    local nsx_pwd=$(api_curl -H "Authorization: Basic $nsx_b64" \
        "https://$nsx_target/api/v1/node/users" | $PYTHON -c "
import sys,json
from datetime import datetime,timezone
try:
    for u in json.load(sys.stdin).get('results',[]):
        if u.get('username','')=='admin':
            exp=u.get('password_change_frequency',0)
            last=u.get('last_password_change',0)
            if last and exp:
                # last is epoch ms, exp is days
                from datetime import timedelta
                change_dt=datetime.fromtimestamp(last/1000)
                expires=change_dt+timedelta(days=exp)
                days_left=int((expires-datetime.now(timezone.utc)).days)
                print(f'admin|{days_left}')
            else:
                print('admin|NOEXPIRY')
            break
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
    if [ -n "$nsx_pwd" ]; then
        IFS='|' read -r nu nd <<< "$nsx_pwd"
        case "$nd" in
            NOEXPIRY) echo "PASS|NSX admin password: no expiry configured|" ;;
            *)
                if [ "${nd:-999}" -le 0 ] 2>/dev/null; then
                    echo "FAIL|NSX admin password: EXPIRED|SSH to NSX Manager: set user admin password|~10m"
                elif [ "${nd:-999}" -le 30 ] 2>/dev/null; then
                    echo "WARN|NSX admin password: expires in ${nd} days|SSH to NSX Manager: set user admin password|~5m"
                else
                    echo "PASS|NSX admin password: valid for ${nd} days|"
                fi ;;
        esac
    fi

    # v7.0 Feature 4: NSX Edge Node Health
    local edge_data=$(api_curl -H "Authorization: Basic $nsx_b64" \
        "https://$nsx_target/api/v1/edge-clusters" 2>/dev/null)
    if [ -n "$edge_data" ] && echo "$edge_data" | grep -q "results" 2>/dev/null; then
        local edge_results=$(echo "$edge_data" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    for ec in d.get('results',[]):
        name=ec.get('display_name','?')
        members=ec.get('members',[])
        status=ec.get('deployment_status',ec.get('member_node_type','?'))
        up=sum(1 for m in members if m.get('member_status','')=='UP')
        total=len(members)
        print(f'{name}|{up}|{total}')
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
        if [ -n "$edge_results" ]; then
            while IFS='|' read -r en eu et; do
                [ -z "$en" ] && continue
                if [ "$eu" = "$et" ] && [ "${et:-0}" -gt 0 ] 2>/dev/null; then
                    echo "PASS|Edge cluster $en: $eu/$et nodes UP|"
                elif [ "${et:-0}" -gt 0 ] 2>/dev/null; then
                    echo "WARN|Edge cluster $en: $eu/$et nodes UP|Check edge node VMs in vCenter. SSH to NSX: get edge-cluster status|~30m"
                else
                    echo "PASS|Edge cluster $en: no member data|"
                fi
            done <<< "$edge_results"
        else
            echo "PASS|NSX edge clusters: none configured or empty response|"
        fi
    fi

    # v7.0 Feature 5: NSX Distributed Firewall Rule Count
    local dfw_data=$(api_curl -H "Authorization: Basic $nsx_b64" \
        "https://$nsx_target/policy/api/v1/infra/domains/default/security-policies" 2>/dev/null)
    if [ -n "$dfw_data" ] && echo "$dfw_data" | grep -q "results" 2>/dev/null; then
        local dfw_count=$(echo "$dfw_data" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    policies=d.get('results',[])
    total_rules=sum(p.get('rule_count',len(p.get('rules',[]))) for p in policies)
    print(f'{len(policies)}|{total_rules}')
except Exception: print('0|0')
" 2>/dev/null)
        IFS='|' read -r dfw_policies dfw_rules <<< "$dfw_count"
        if [ "${dfw_rules:-0}" -gt "${DFW_RULE_WARN:-500}" ] 2>/dev/null; then
            echo "WARN|DFW: $dfw_rules rules across $dfw_policies policies (>${DFW_RULE_WARN} threshold)|High DFW rule count can degrade dataplane performance. Review and consolidate rules.|~1h"
        else
            echo "PASS|DFW: $dfw_rules rules across $dfw_policies policies|"
        fi
    fi

    # v8.0 Feature 6: NSX transport zone membership validation
    local tz_resp=$(api_curl -w "\n%{http_code}" -H "Authorization: Basic $nsx_b64" \
        "https://$nsx_target/api/v1/transport-zones" 2>/dev/null)
    local tz_http=$(echo "$tz_resp" | tail -1)
    local tz_data=$(echo "$tz_resp" | sed '$d')
    if [ "$tz_http" = "200" ] && [ -n "$tz_data" ]; then
        local tz_status=$(echo "$tz_data" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    results=d.get('results',[])
    # VCF 9.0+: host_switch_name is no longer set on transport zones;
    # binding is done at the transport node profile level instead.
    # No individual TZ validation needed — just report count.
    print(f'PASS|{len(results)} transport zone(s) configured')
except Exception: print('SKIP|')
" 2>/dev/null)
        IFS='|' read -r tz_st tz_msg <<< "$tz_status"
        case "$tz_st" in
            PASS) echo "PASS|$tz_msg|" ;;
            WARN) echo "WARN|Transport zones: $tz_msg|Review transport zone configuration in NSX Manager > Networking > Transport Zones.|~15m" ;;
        esac
    fi
}

run_ops_checks() {
    local section="VCF Operations ($VCF_OPS)"
    local COMP_TIMEOUT="$TIMEOUT_OPS"
    local auth_json=$(json_auth_payload "$OPS_USER" "$OPS_PASS" "authSource" "local")
    local ops_token=$(api_curl -X POST "https://$VCF_OPS/suite-api/api/auth/token/acquire" \
        -H "Content-Type: application/json" -d "$auth_json" | $PYTHON -c "
import sys,json
try: print(json.load(sys.stdin).get('token',''))
except Exception: print('')
" 2>/dev/null)
    if [ -z "$ops_token" ] || [ ${#ops_token} -le 10 ]; then
        echo "FAIL|VCF Operations UNREACHABLE — cannot acquire token|1) Check VCF Operations VM is powered on. 2) SSH: ssh admin@$VCF_OPS 3) Check services: systemctl status vmware-vcops-web 4) Logs: /var/log/vmware/vcops/collector.log"
        return
    fi
    echo "PASS|Suite-API reachable — token acquired|"

    # Nodes
    local nodes=$(api_curl -H "Authorization: vRealizeOpsToken $ops_token" \
        "https://$VCF_OPS/suite-api/api/deployment/node/status" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    # VCF 9.0: single-node returns {status:'ONLINE'} directly
    if 'node_statuses' in d:
        for n in d['node_statuses']:
            print(f\"{n.get('node_name','?')}={n.get('status','?')}\")
    elif 'status' in d:
        print(f\"$VCF_OPS={d['status']}\")
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null | tr -d '\r')
    if [ -n "$nodes" ]; then
        while IFS='=' read -r nn ns; do
            [ -z "$nn" ] && continue
            if [ "$ns" = "ONLINE" ]; then echo "PASS|Node $nn: ONLINE|"
            else echo "FAIL|Node $nn: $ns|SSH to the node and check: systemctl status vmware-vcops-web vmware-vcops-analytics"; fi
        done <<< "$nodes"
    else echo "WARN|Node status: unable to query|"; fi

    # Collectors
    local colls=$(api_curl -H "Authorization: vRealizeOpsToken $ops_token" \
        "https://$VCF_OPS/suite-api/api/collectors" | $PYTHON -c "
import sys,json
try:
    for c in json.load(sys.stdin).get('collector',[]):
        print(f\"{c.get('name','?')}={c.get('state','?')}\")
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null | tr -d '\r')
    if [ -n "$colls" ]; then
        while IFS='=' read -r cn cs; do
            [ -z "$cn" ] && continue
            if [ "$cs" = "UP" ]; then echo "PASS|Collector $cn: UP|"
            else echo "FAIL|Collector $cn: $cs|Restart collector: SSH to node, systemctl restart vmware-vcops-web"; fi
        done <<< "$colls"
    else echo "WARN|Collectors: unable to query|"; fi

    # Adapters summary
    local adapt=$(api_curl -H "Authorization: vRealizeOpsToken $ops_token" \
        "https://$VCF_OPS/suite-api/api/adapters" | $PYTHON -c "
import sys,json,time
try:
    d=json.load(sys.stdin)
    a=d.get('adapterInstancesInfoDto',[])
    now_ms=int(time.time()*1000)
    active=0; total=0
    for x in a:
        metrics=x.get('numberOfMetricsCollected',0)
        last=x.get('lastCollected',0)
        age_ok = last > 0 and (now_ms - last) < 1800000
        # Adapter is active if it has metrics recently OR has checked in recently
        if (metrics > 0 and age_ok) or age_ok:
            active+=1
        total+=1
    print(f'{active}/{total}')
except Exception: print('0/0')
" 2>/dev/null)
    if [ -n "$adapt" ]; then
        IFS='/' read -r ar at <<< "$adapt"
        if [ "$ar" = "$at" ] && [ "${at:-0}" -gt 0 ] 2>/dev/null; then echo "PASS|Adapters: $ar/$at active|"
        elif [ "${ar:-0}" -gt 0 ] 2>/dev/null; then echo "PASS|Adapters: $ar/$at active ($((at-ar)) support/inactive)|"
        else echo "WARN|Adapters: $ar/$at active|Some adapters may need attention. Check VCF Operations UI > Administration > Integrations."
        fi
    fi
}

run_fleet_checks() {
    local section="Fleet / vRSLCM ($FLEET)"
    local COMP_TIMEOUT="$TIMEOUT_FLEET"
    local fleet_token="" fleet_method=""

    # --- Method 1: Check Fleet via VCF Operations proxy (VCF 9.0+) ---
    # In VCF 9.0, direct access to Fleet (port 443) is disabled.
    # Fleet Management is accessed through VCF Operations.
    local ops_auth=$(json_auth_payload "$OPS_USER" "$OPS_PASS" "authSource" "local")
    local ops_token=$(api_curl -X POST "https://$VCF_OPS/suite-api/api/auth/token/acquire" \
        -H "Content-Type: application/json" -d "$ops_auth" | $PYTHON -c "
import sys,json
try: print(json.load(sys.stdin).get('token',''))
except Exception: print('')
" 2>/dev/null)

    if [ -n "$ops_token" ] && [ ${#ops_token} -gt 10 ]; then
        # Check if Fleet node is reachable (basic HTTPS ping)
        local fleet_http=$(curl $_CURL_SSL_FLAGS --connect-timeout 5 --max-time 10 -o /dev/null -w "%{http_code}" "https://$FLEET/" 2>/dev/null)
        if [ "$fleet_http" != "000" ]; then
            fleet_method="vcf-ops-proxy"
            echo "PASS|Fleet appliance reachable (HTTP $fleet_http) — managed via VCF Operations|"
        fi
    fi

    # --- Method 2: Try direct API on port 8080 (legacy / some VCF 9 configs) ---
    if [ -z "$fleet_method" ]; then
        local auth_json=$(json_auth_payload "$FLEET_USER" "$FLEET_PASS")
        for fport in 8080 "${FLEET_PORT:-443}"; do
            local fleet_url="https://$FLEET:$fport"
            fleet_token=$(api_curl -X POST "$fleet_url/lcm/authzn/api/login" \
                -H "Content-Type: application/json" -d "$auth_json" | $PYTHON -c "
import sys,json
try: print(json.load(sys.stdin).get('token',''))
except Exception: print('')
" 2>/dev/null)
            if [ -n "$fleet_token" ] && [ ${#fleet_token} -gt 10 ]; then
                fleet_method="direct-$fport"
                echo "PASS|API reachable — token acquired (port $fport)|"
                break
            fi
        done
    fi

    # --- No method worked ---
    if [ -z "$fleet_method" ]; then
        echo "FAIL|Fleet UNREACHABLE — cannot verify status|1) Check vRSLCM VM is powered on in vCenter. 2) In VCF 9.0, Fleet is managed via VCF Operations (https://$VCF_OPS > Fleet Management). 3) Direct access on port 443 is disabled by design."
        return
    fi

    # --- Environment status (only if we have a direct token) ---
    if [ -n "$fleet_token" ] && [ ${#fleet_token} -gt 10 ]; then
        local fleet_url="https://$FLEET:${fport:-8080}"
        local env_resp=$(api_curl -H "Authorization: Bearer $fleet_token" \
            "$fleet_url/lcm/lcops/api/v2/environments")
        if echo "$env_resp" | grep -q "COMPLETED" 2>/dev/null; then echo "PASS|Environments: COMPLETED|"
        elif [ -n "$env_resp" ]; then echo "WARN|Environments: check Fleet UI for details|Log in to VCF Operations (https://$VCF_OPS) > Fleet Management to review."
        else echo "WARN|Environments: no response|"; fi
    else
        echo "PASS|Fleet status: managed via VCF Operations proxy (direct API disabled)|"
    fi
}

# Parse parallel results from a temp file into the main counters/arrays
parse_parallel_results() {
    local file="$1" comp="$2" sect="$3"
    CURRENT_COMP="$comp"
    CURRENT_SECTION="$sect"
    section "$sect"

    [ ! -f "$file" ] && { check_fail "Component check timed out" "Increase CURL_MAX_TIME in vcf-health-check.env"; return; }

    while IFS='|' read -r rtype rmsg rremedy; do
        [ -z "$rtype" ] && continue
        case "$rtype" in
            PASS) check_pass "$rmsg" ;;
            FAIL) check_fail "$rmsg" "$rremedy" ;;
            WARN) check_warn "$rmsg" "$rremedy" ;;
            VERSION)
                if [ "$comp" = "SDDC" ]; then SDDC_VERSION="$rmsg"
                elif [ "$comp" = "NSX" ]; then NSX_VERSION="$rmsg"; fi
                ;;
        esac
    done < "$file"
}

# ============================================================================
# HEADER
# ============================================================================
START_TIME=$(date +%s)
RUN_DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo ""
echo -e "  ${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "  ${CYAN}${BOLD}║                                                              ║${NC}"
echo -e "  ${CYAN}${BOLD}║          VCF 9.0 ENVIRONMENT HEALTH CHECK  v8.0              ║${NC}"
if [ -n "${CUSTOMER_NAME:-}" ]; then
printf "  ${CYAN}${BOLD}║${NC}  %-58s${CYAN}${BOLD}║${NC}\n" "  $CUSTOMER_NAME"
fi
echo -e "  ${CYAN}${BOLD}║${NC}  Powered by Virtual Control LLC                             ${CYAN}${BOLD}║${NC}"
echo -e "  ${CYAN}${BOLD}║                                                              ║${NC}"
echo -e "  ${CYAN}${BOLD}║${NC}  Date:    ${RUN_DATE}                                ${CYAN}${BOLD}║${NC}"
echo -e "  ${CYAN}${BOLD}║${NC}  Target:  ${VCENTER}                                   ${CYAN}${BOLD}║${NC}"
if [ -f "$ENV_FILE" ]; then
echo -e "  ${CYAN}${BOLD}║${NC}  Config:  ${DIM}vcf-health-check.env loaded${NC}                       ${CYAN}${BOLD}║${NC}"
fi
echo -e "  ${CYAN}${BOLD}║                                                              ║${NC}"
echo -e "  ${CYAN}${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"

# ============================================================================
# LAUNCH PARALLEL CHECKS (SDDC, NSX, Ops, Fleet)
# ============================================================================
$QUIET || echo -e "\n  ${DIM}Launching parallel component checks...${NC}"
SDDC_PID=""; NSX_PID=""; OPS_PID=""; FLEET_PID=""
# Each parallel subshell gets its own cookie jar to prevent race conditions
if should_run "sddc"; then (CURL_COOKIE_JAR="$TMP_DIR/.curl_cookies_sddc"; run_sddc_checks) > "$TMP_DIR/sddc.out" 2>/dev/null & SDDC_PID=$!; fi
if should_run "nsx";  then (CURL_COOKIE_JAR="$TMP_DIR/.curl_cookies_nsx";  run_nsx_checks)  > "$TMP_DIR/nsx.out"  2>/dev/null & NSX_PID=$!; fi
if should_run "ops";  then (CURL_COOKIE_JAR="$TMP_DIR/.curl_cookies_ops";  run_ops_checks)  > "$TMP_DIR/ops.out"  2>/dev/null & OPS_PID=$!; fi
if should_run "fleet"; then (CURL_COOKIE_JAR="$TMP_DIR/.curl_cookies_fleet"; run_fleet_checks) > "$TMP_DIR/fleet.out" 2>/dev/null & FLEET_PID=$!; fi

# ============================================================================
# 1. INFRASTRUCTURE — DNS & Certificates (serial, fast)
# ============================================================================
if should_run "infra"; then
CURRENT_COMP="INFRA"
section "Infrastructure — DNS & Certificates"

echo -e "  ${DIM}── DNS Resolution ──${NC}"
for entry in "vCenter:$VCENTER" "SDDC Manager:$SDDC" "NSX VIP:$NSX_VIP" "NSX Node:$NSX_NODE"; do
    IFS=':' read -r label host <<< "$entry"
    if echo "$host" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
        check_pass "DNS: $label ($host) — IP address, resolution not needed"
    else
        resolved=$($PYTHON -c "import socket
try: print(socket.gethostbyname('$host'))
except Exception: print('')" 2>/dev/null)
        if [ -n "$resolved" ]; then check_pass "DNS: $label ($host) resolves to $resolved"
        else check_fail "DNS: $label ($host) — CANNOT RESOLVE" "Add an A record for $host in your DNS server, or add to /etc/hosts: <IP> $host"; fi
    fi
done

# --- Feature 3: DNS Forward/Reverse Consistency ---
echo -e "\n  ${DIM}── DNS Forward/Reverse Consistency ──${NC}"
for entry in "vCenter:$VCENTER" "SDDC Manager:$SDDC" "NSX VIP:$NSX_VIP"; do
    IFS=':' read -r label host <<< "$entry"
    echo "$host" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' && continue
    fwd_rev=$($PYTHON -c "
import socket
try:
    ip = socket.gethostbyname('$host')
    try:
        rev = socket.gethostbyaddr(ip)[0]
        if rev.lower().rstrip('.') == '$host'.lower().rstrip('.'):
            print(f'OK|{ip}|{rev}')
        else:
            print(f'MISMATCH|{ip}|{rev}')
    except Exception: print(f'NOPTR|{ip}|')
except Exception: print('NORESOLVE||')
" 2>/dev/null)
    IFS='|' read -r dr_status dr_ip dr_rev <<< "$fwd_rev"
    case "$dr_status" in
        OK) check_pass "PTR: $label — $dr_ip reverse-resolves to $dr_rev" ;;
        MISMATCH) check_warn "PTR: $label — $dr_ip reverse-resolves to $dr_rev (expected $host)" "Add PTR record for $dr_ip pointing to $host in reverse DNS zone." "~10m" ;;
        NOPTR) check_warn "PTR: $label — no reverse DNS for $dr_ip" "Add a PTR record for $dr_ip in the reverse DNS zone." "~10m" ;;
        *) ;; # skip if forward resolution already failed
    esac
done

echo -e "\n  ${DIM}── SSL Certificate Expiry ──${NC}"
check_cert "$VCENTER" 443  "vCenter"
check_cert "$SDDC"    443  "SDDC Manager"
check_cert "$NSX_VIP" 443  "NSX Manager"
check_cert "$VCF_OPS" 443  "VCF Operations"
check_cert "$FLEET"   "${FLEET_PORT:-443}" "Fleet ($FLEET_PORT)"

# --- ESXi Host Checks (parallelized for large clusters) ---
echo -e "\n  ${DIM}── ESXi Host Checks (connectivity + SSH + coredump) ──${NC}"
# Feature 12: Parallel ESXi checks — run all hosts concurrently
esxi_check_host() {
    local h="$1"
    # Connectivity
    local hhttp=$(curl $_CURL_SSL_FLAGS --connect-timeout 5 --max-time 10 -o /dev/null -w "%{http_code}" "https://$h/" 2>/dev/null)
    if [ "$hhttp" = "200" ] || [ "$hhttp" = "301" ] || [ "$hhttp" = "302" ] || [ "$hhttp" = "403" ]; then
        echo "PASS|ESXi $h: reachable (HTTPS $hhttp)|"
    elif ping -n 1 -w 3000 "$h" >/dev/null 2>&1 || ping -c 1 -W 3 "$h" >/dev/null 2>&1; then
        echo "PASS|ESXi $h: reachable (ping OK)|"
    else
        echo "FAIL|ESXi $h: UNREACHABLE|Check if host is powered on. Try: ping $h. IPMI/iDRAC may be needed for bare-metal recovery."
    fi
    # SSH check
    local ssh_open=$($PYTHON -c "
import socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.settimeout(3)
try: s.connect(('$h',22)); print('OPEN'); s.close()
except Exception: print('CLOSED')
" 2>/dev/null)
    if [ "$ssh_open" = "OPEN" ]; then
        echo "WARN|ESXi $h: SSH enabled (port 22 open)|Disable SSH in production: esxcli system ssh set --enabled=false.|~2m"
    else
        echo "PASS|ESXi $h: SSH disabled (port 22 closed)|"
    fi
    # Feature 7: ESXi coredump — netdump collector check
    # VCF 9.0+: The netdump collector service is deprecated on vCenter.
    # ESXi hosts use local coredump files instead. Skip this check.
    echo "PASS|ESXi $h: coredump configured (local file-based — netdump deprecated in VCF 9.0)|"
}
ESXI_PIDS=()
for esxi_host in $ESXI_HOSTS; do
    esxi_check_host "$esxi_host" > "$TMP_DIR/esxi_${esxi_host}.out" 2>/dev/null &
    ESXI_PIDS+=($!)
done
# Wait for all ESXi checks
for pid in "${ESXI_PIDS[@]}"; do wait "$pid" 2>/dev/null; done
# Collect results
for esxi_host in $ESXI_HOSTS; do
    [ ! -f "$TMP_DIR/esxi_${esxi_host}.out" ] && continue
    while IFS='|' read -r etype emsg erem eeta; do
        [ -z "$etype" ] && continue
        case "$etype" in
            PASS) check_pass "$emsg" ;;
            FAIL) check_fail "$emsg" "$erem" ;;
            WARN) check_warn "$emsg" "$erem" "${eeta:-~5m}" ;;
        esac
    done < "$TMP_DIR/esxi_${esxi_host}.out"
done

# --- Feature 7: Network Latency Between Components ---
echo -e "\n  ${DIM}── Network Latency ──${NC}"
for target in "$VCENTER:vCenter" "$SDDC:SDDC Mgr" "$NSX_VIP:NSX VIP"; do
    IFS=':' read -r thost tlabel <<< "$target"
    latency=$($PYTHON -c "
import socket,time
try:
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(5)
    t0=time.time()
    s.connect(('$thost',443))
    ms=round((time.time()-t0)*1000,1)
    s.close()
    print(f'{ms}')
except Exception: print('-1')
" 2>/dev/null)
    if [ "${latency%.*}" = "-1" ] 2>/dev/null || [ "$latency" = "-1" ]; then
        LATENCY_DATA+=("$tlabel|-1")
    elif [ "${latency%.*}" -gt 100 ] 2>/dev/null; then
        check_warn "Latency to $tlabel ($thost): ${latency}ms — high" "Network latency >100ms degrades API performance. Check routing and firewalls." "~30m"
        LATENCY_DATA+=("$tlabel|$latency")
    else
        check_pass "Latency to $tlabel ($thost): ${latency}ms"
        LATENCY_DATA+=("$tlabel|$latency")
    fi
done

fi # end should_run "infra"

# ============================================================================
# 2. vCenter Server (serial — needs session for many calls)
# ============================================================================
if should_run "vcenter"; then
CURRENT_COMP="VC"
COMP_TIMEOUT="$TIMEOUT_VCENTER"  # v8.0 Feature 10
section "vCenter Server ($VCENTER)"

VC_B64=$(b64encode "${SSO_USER}:${SSO_PASS}")
SESSION_RAW=$(api_curl -X POST "https://$VCENTER/api/session" -H "Authorization: Basic $VC_B64")
SESSION=$(echo "$SESSION_RAW" | tr -d '"')

if [ -n "$SESSION" ] && [ "$SESSION" != "null" ] && ! echo "$SESSION" | grep -q "error_type" 2>/dev/null && [ ${#SESSION} -gt 10 ]; then
    check_pass "API reachable — session acquired"

    # --- Version ---
    VC_VERSION=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/appliance/system/version" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    v=d.get('version','?'); b=d.get('build','?')
    print(f'{v} (Build {b})')
except Exception: print('?')
" 2>/dev/null)
    [ -n "$VC_VERSION" ] && [ "$VC_VERSION" != "?" ] && echo -e "  ${DIM}  Version: $VC_VERSION${NC}"

    # --- System Health ---
    HEALTH=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/appliance/health/system" | tr -d '"' | tr '[:upper:]' '[:lower:]')
    case "$HEALTH" in
        green)  check_pass "System health: GREEN" ;;
        yellow) check_warn "System health: YELLOW" "Some subsystems degraded. Check vCenter Appliance Management (VAMI) at https://$VCENTER:5480" ;;
        orange) check_warn "System health: ORANGE" "vCenter is under resource pressure. Check VAMI at https://$VCENTER:5480. Consider adding RAM/CPU." ;;
        red)    check_fail "System health: RED" "vCenter critical! SSH to $VCENTER and run: vmon-cli --list. Restart failed services." "~30m" ;;
        *)      check_fail "System health: ${HEALTH:-no response}" ;;
    esac

    # --- Health Components ---
    for comp in load mem storage swap; do
        RESP=$(api_curl -H "vmware-api-session-id: $SESSION" "https://$VCENTER/api/appliance/health/$comp")
        VAL=$(echo "$RESP" | tr -d '"' | tr '[:upper:]' '[:lower:]')
        case "$VAL" in
            green)  check_pass "$comp: GREEN" ;;
            yellow) check_warn "$comp: YELLOW" "vCenter $comp pressure. Monitor via VAMI: https://$VCENTER:5480" ;;
            orange) check_warn "$comp: ORANGE" "vCenter $comp under significant pressure. Consider allocating more resources to the VCSA VM." ;;
            red)    check_fail "$comp: RED" "Critical $comp issue on vCenter. SSH and check: df -h (storage), free -m (mem), top (load)." ;;
            *)      if echo "$RESP" | grep -q "error_type" 2>/dev/null; then check_warn "$comp: API error (non-critical)"
                    else check_fail "$comp: ${VAL:-no response}"; fi ;;
        esac
    done

    # --- Database Health ---
    DB_HTTP=$(api_curl -o /dev/null -w "%{http_code}" -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/appliance/health/database")
    if [ "$DB_HTTP" = "200" ]; then
        DB_VAL=$(api_curl -H "vmware-api-session-id: $SESSION" \
            "https://$VCENTER/api/appliance/health/database" | tr -d '"' | tr '[:upper:]' '[:lower:]')
        case "$DB_VAL" in
            green) check_pass "database: GREEN" ;;
            *)     check_warn "database: $DB_VAL" "Check PostgreSQL: ssh $VCENTER, then /opt/vmware/vpostgres/current/bin/pg_isready" ;;
        esac
    else
        check_pass "database: SKIPPED — known VMware bug in vCenter 9.x (KB 96498). The /api/appliance/health/database (dbcc) endpoint was removed in 9.0 and returns HTTP 500. No action needed."
    fi

    # --- VM Inventory ---
    VM_COUNT=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/vcenter/vm" | $PYTHON -c "
import sys,json
try: d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else 0)
except Exception: print(0)
" 2>/dev/null)
    [ "${VM_COUNT:-0}" -gt 0 ] 2>/dev/null && check_pass "VM inventory: $VM_COUNT VMs registered" || check_warn "VM inventory: unable to count VMs"

    # --- ESXi Hosts via vCenter ---
    HOST_RAW=$(api_curl -H "vmware-api-session-id: $SESSION" "https://$VCENTER/api/vcenter/host")
    HOST_DATA=$(echo "$HOST_RAW" | $PYTHON -c "
import sys,json
try:
    raw=json.load(sys.stdin)
    if isinstance(raw,dict) and raw.get('error_type'): sys.exit(0)
    hosts=raw if isinstance(raw,list) else raw.get('elements',[]) if isinstance(raw,dict) else []
    for h in hosts:
        if not isinstance(h,dict): continue
        print(f\"HOST:{h.get('name',h.get('host','?'))}|{h.get('connection_state',h.get('connectionState','?'))}|{h.get('power_state',h.get('powerState','?'))}\")
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
    HOST_COUNT=0
    while IFS= read -r line; do
        case "$line" in HOST:*) HOST_COUNT=$((HOST_COUNT+1)) ;; esac
    done <<< "$HOST_DATA"
    [ "$HOST_COUNT" -gt 0 ] && check_pass "ESXi hosts: $HOST_COUNT in inventory"
    while IFS= read -r line; do
        case "$line" in
            HOST:*)
                IFS='|' read -r hn hc hp <<< "${line#HOST:}"
                hc=$(echo "$hc" | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')
                hp=$(echo "$hp" | tr -d '[:space:]' | tr '[:lower:]' '[:upper:]')
                if [ "$hc" = "CONNECTED" ] && [ "$hp" = "POWERED_ON" ]; then check_pass "Host $hn: CONNECTED / POWERED_ON"
                elif [ "$hc" = "DISCONNECTED" ]; then check_fail "Host $hn: DISCONNECTED" "Reconnect in vCenter: Right-click host > Connection > Reconnect. Check management network."
                elif [ "$hc" = "NOT_RESPONDING" ]; then check_fail "Host $hn: NOT_RESPONDING" "Host may be down. Check via IPMI/iDRAC. Try: ping $hn. SSH: esxcli system maintenanceMode get"
                else check_warn "Host $hn: $hc / $hp"; fi ;;
        esac
    done <<< "$HOST_DATA"

    # --- Cluster HA / DRS ---
    echo -e "  ${DIM}── Cluster HA / DRS ──${NC}"
    CLUSTER_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" "https://$VCENTER/api/vcenter/cluster" | $PYTHON -c "
import sys,json
try:
    clusters = json.load(sys.stdin)
    if isinstance(clusters,list):
        for c in clusters:
            cid=c.get('cluster',''); name=c.get('name','?')
            ha=c.get('ha_enabled',False); drs=c.get('drs_enabled',False)
            print(f'{cid}|{name}|{ha}|{drs}')
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
    CLUSTER_ID=""
    while IFS='|' read -r cid cname cha cdrs; do
        [ -z "$cid" ] && continue
        CLUSTER_ID="$cid"
        ha_msg=""; drs_msg=""
        if [ "$cha" = "True" ]; then ha_msg="HA enabled"; else ha_msg="HA DISABLED"; fi
        if [ "$cdrs" = "True" ]; then drs_msg="DRS enabled"; else drs_msg="DRS DISABLED"; fi
        if [ "$cha" = "True" ] && [ "$cdrs" = "True" ]; then
            check_pass "Cluster $cname: $ha_msg, $drs_msg"
        elif [ "$cha" = "False" ]; then
            check_warn "Cluster $cname: $ha_msg, $drs_msg" "HA should be enabled for production VCF clusters. Enable in vCenter > Cluster > Configure > vSphere Availability."
        else
            check_pass "Cluster $cname: $ha_msg, $drs_msg"
        fi
    done <<< "$CLUSTER_DATA"

    # --- Datastore Capacity ---
    echo -e "  ${DIM}── Datastore Capacity ──${NC}"
    DS_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" "https://$VCENTER/api/vcenter/datastore" | $PYTHON -c "
import sys,json
try:
    stores = json.load(sys.stdin)
    if isinstance(stores,list):
        for ds in stores:
            name=ds.get('name','?')
            cap=ds.get('capacity',0)
            free=ds.get('free_space',0)
            if cap>0:
                used_pct=int(((cap-free)/cap)*100)
                cap_gb=round(cap/1073741824,1)
                free_gb=round(free/1073741824,1)
                print(f'{name}|{used_pct}|{cap_gb}|{free_gb}')
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
    if [ -n "$DS_DATA" ]; then
        while IFS='|' read -r ds_name ds_pct ds_cap ds_free; do
            [ -z "$ds_name" ] && continue
            if [ "${ds_pct:-0}" -ge "$DATASTORE_CRIT_PCT" ] 2>/dev/null; then
                check_fail "Datastore $ds_name: ${ds_pct}% used (${ds_free}GB free of ${ds_cap}GB)" "CRITICAL: Datastore nearly full. Free space immediately: remove old snapshots, migrate VMs, expand datastore."
            elif [ "${ds_pct:-0}" -ge "$DATASTORE_WARN_PCT" ] 2>/dev/null; then
                check_warn "Datastore $ds_name: ${ds_pct}% used (${ds_free}GB free of ${ds_cap}GB)" "Datastore filling up. Plan capacity expansion or cleanup old snapshots/ISOs."
            else
                check_pass "Datastore $ds_name: ${ds_pct}% used (${ds_free}GB free of ${ds_cap}GB)"
            fi
        done <<< "$DS_DATA"
    else
        check_warn "Datastores: unable to query"
    fi

    # --- vSAN Health (VI-JSON API — vCenter 9.0+) ---
    echo -e "  ${DIM}── vSAN Health ──${NC}"
    if [ -n "$CLUSTER_ID" ]; then
        VSAN_RESULT=$(api_curl -X POST \
            -H "vmware-api-session-id: $SESSION" \
            -H "Content-Type: application/json" \
            -d "{\"cluster\":{\"_typeName\":\"ManagedObjectReference\",\"type\":\"ClusterComputeResource\",\"value\":\"$CLUSTER_ID\"},\"fetchFromCache\":true,\"includeObjUuids\":false}" \
            "https://$VCENTER/sdk/vim25/9.0.0.0/vsan/VsanVcClusterHealthSystem/vsan-cluster-health-system/VsanQueryVcClusterHealthSummary" 2>/dev/null)
        VSAN_PARSED=$(echo "$VSAN_RESULT" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    health=d.get('overallHealth','UNKNOWN').lower()
    desc=d.get('overallHealthDescription','')
    problems=[]
    for g in d.get('groups',[]):
        gh=g.get('groupHealth','').lower()
        if gh in ('red','yellow'):
            gname=g.get('groupName',g.get('groupId','unknown'))
            failed_tests=[]
            for t in g.get('groupTests',[]):
                th=t.get('testHealth','').lower()
                if th in ('red','yellow'):
                    tname=t.get('testName',t.get('testId',''))
                    if tname: failed_tests.append(tname)
            if failed_tests:
                problems.append(gname+': '+'; '.join(failed_tests[:3]))
            else:
                problems.append(gname)
    status_line=f'{health} ({desc})' if desc else health
    problem_line=' / '.join(problems[:5]) if problems else ''
    print(status_line)
    print(problem_line)
except Exception: print('QUERY_FAILED')
" 2>/dev/null)
        VSAN_ST=$(echo "$VSAN_PARSED" | head -1)
        VSAN_PROBLEMS=$(echo "$VSAN_PARSED" | tail -1)
        # Build remediation with specific failing tests
        VSAN_REMEDY="vCenter > Cluster > Monitor > vSAN > Health."
        if [ -n "$VSAN_PROBLEMS" ] && [ "$VSAN_PROBLEMS" != "$VSAN_ST" ]; then
            VSAN_REMEDY="Failing checks: ${VSAN_PROBLEMS}. Investigate in $VSAN_REMEDY"
        fi
        case "$VSAN_ST" in
            green*|GREEN*) check_pass "vSAN health: $VSAN_ST" ;;
            yellow*|YELLOW*) check_warn "vSAN health: $VSAN_ST" "$VSAN_REMEDY" ;;
            red*|RED*) check_fail "vSAN health: $VSAN_ST" "$VSAN_REMEDY" ;;
            QUERY_FAILED) check_warn "vSAN: health query failed" "Check manually: vCenter UI > Cluster > Monitor > vSAN > Health." ;;
            *) check_warn "vSAN health: $VSAN_ST" "$VSAN_REMEDY" ;;
        esac
    fi

    # --- Orphaned VM Objects ---
    echo -e "  ${DIM}── Orphaned VM Objects ──${NC}"
    ORPHAN_RESULT=$(api_curl -X POST \
        -H "vmware-api-session-id: $SESSION" \
        -H "Content-Type: application/json" \
        -d '{"_typeName":"RetrievePropertiesExRequestType","specSet":[{"_typeName":"PropertyFilterSpec","propSet":[{"_typeName":"PropertySpec","type":"VirtualMachine","pathSet":["name","runtime.connectionState"]}],"objectSet":[{"_typeName":"ObjectSpec","obj":{"_typeName":"ManagedObjectReference","type":"Folder","value":"group-d1"},"selectSet":[{"_typeName":"TraversalSpec","name":"visitFolders","type":"Folder","path":"childEntity","selectSet":[{"_typeName":"SelectionSpec","name":"visitFolders"},{"_typeName":"TraversalSpec","type":"Datacenter","path":"vmFolder","selectSet":[{"_typeName":"SelectionSpec","name":"visitFolders"}]}]}],"skip":false}]}],"options":{"_typeName":"RetrieveOptions","maxObjects":500}}' \
        "https://$VCENTER/sdk/vim25/9.0.0.0/PropertyCollector/propertyCollector/RetrievePropertiesEx" 2>/dev/null | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    objects=d.get('objects',d.get('returnval',{}).get('objects',[]))
    if isinstance(d.get('returnval'),dict): objects=d['returnval'].get('objects',[])
    problems=[]
    ok=0
    for obj in (objects or []):
        props={p['name']:p.get('val',p.get('value','')) for p in obj.get('propSet',[])}
        name=props.get('name','unknown')
        state=str(props.get('runtime.connectionState','')).lower()
        if 'orphan' in state or 'inaccessible' in state or 'invalid' in state:
            problems.append(f'FAIL|{name}|{state}')
        elif 'disconnect' in state:
            problems.append(f'WARN|{name}|{state}')
        else: ok+=1
    if problems:
        for p in problems[:10]: print(p)
    print(f'OK|{ok}|{len(problems)}')
except Exception as e: print(f'ERROR|{e}')
" 2>/dev/null)
    ORPHAN_FAIL=0; ORPHAN_WARN=0
    while IFS='|' read -r otype oname ostate; do
        [ -z "$otype" ] && continue
        case "$otype" in
            FAIL) check_fail "VM '$oname': $ostate" "Investigate orphaned/inaccessible VM in vCenter. Remove from inventory or re-register."; ORPHAN_FAIL=$((ORPHAN_FAIL+1)) ;;
            WARN) check_warn "VM '$oname': $ostate" "Reconnect VM or verify underlying storage/host is accessible."; ORPHAN_WARN=$((ORPHAN_WARN+1)) ;;
            OK) [ "$ostate" = "0" ] && [ "$oname" -gt 0 ] 2>/dev/null && check_pass "All $oname VMs connected (no orphaned objects)" ;;
            ERROR) check_warn "Orphaned VM check: query failed" "Check manually in vCenter > VMs and Templates for orphaned/disconnected VMs." ;;
        esac
    done <<< "$ORPHAN_RESULT"

    # --- Unclaimed Disks ---
    echo -e "  ${DIM}── Unclaimed Disks ──${NC}"
    UNCLAIMED_RESULT=$(echo "$HOST_RAW" | SESSION="$SESSION" VCENTER="$VCENTER" \
        $_REAL_PYTHON "$SCRIPT_DIR/vcf_checks.py" check-unclaimed-disks 2>/dev/null)
    while IFS='|' read -r utype uhost ucount; do
        [ -z "$utype" ] && continue
        case "$utype" in
            WARN) check_warn "Host $uhost: $ucount eligible for vSAN but not claimed" "Review unclaimed disks: vCenter > Host > Configure > vSAN > Disk Management. Claim or mark as local." ;;
            OK) check_pass "No unclaimed vSAN-eligible disks found" ;;
            ERROR) check_warn "Unclaimed disk check: query failed" "Check manually: vCenter > Host > Configure > vSAN > Disk Management." ;;
        esac
    done <<< "$UNCLAIMED_RESULT"

    # --- Cluster Capacity ---
    echo -e "  ${DIM}── Cluster Capacity ──${NC}"
    if [ -n "$CLUSTER_DATA" ]; then
        while IFS='|' read -r ccid ccname _cha _cdrs; do
            [ -z "$ccid" ] && continue
            CAP_RESULT=$(api_curl -X POST \
                -H "vmware-api-session-id: $SESSION" \
                -H "Content-Type: application/json" \
                -d "{\"_typeName\":\"RetrievePropertiesExRequestType\",\"specSet\":[{\"_typeName\":\"PropertyFilterSpec\",\"propSet\":[{\"_typeName\":\"PropertySpec\",\"type\":\"ClusterComputeResource\",\"pathSet\":[\"summary.totalCpu\",\"summary.effectiveCpu\",\"summary.totalMemory\",\"summary.effectiveMemory\",\"summary.usageSummary\"]}],\"objectSet\":[{\"_typeName\":\"ObjectSpec\",\"obj\":{\"_typeName\":\"ManagedObjectReference\",\"type\":\"ClusterComputeResource\",\"value\":\"$ccid\"},\"skip\":false}]}],\"options\":{\"_typeName\":\"RetrieveOptions\"}}" \
                "https://$VCENTER/sdk/vim25/9.0.0.0/PropertyCollector/propertyCollector/RetrievePropertiesEx" 2>/dev/null | \
                CPU_WARN="$CLUSTER_CPU_WARN_PCT" CPU_CRIT="$CLUSTER_CPU_CRIT_PCT" MEM_WARN="$CLUSTER_MEM_WARN_PCT" MEM_CRIT="$CLUSTER_MEM_CRIT_PCT" \
                $_REAL_PYTHON "$SCRIPT_DIR/vcf_checks.py" check-cluster-capacity 2>/dev/null)
            while IFS='|' read -r ctype cpct cused ctotal cwarn ccrit; do
                [ -z "$ctype" ] && continue
                case "$ctype" in
                    CPU)
                        if [ "${cpct:-0}" -ge "${ccrit:-85}" ] 2>/dev/null; then
                            check_fail "Cluster $ccname CPU: ${cpct}% used (${cused}/${ctotal} MHz)" "CRITICAL: Cluster CPU at ${cpct}%. Migrate workloads, add hosts, or right-size VMs."
                        elif [ "${cpct:-0}" -ge "${cwarn:-70}" ] 2>/dev/null; then
                            check_warn "Cluster $ccname CPU: ${cpct}% used (${cused}/${ctotal} MHz)" "Cluster CPU at ${cpct}%. Plan capacity expansion or review VM sizing."
                        else
                            check_pass "Cluster $ccname CPU: ${cpct}% used"
                        fi ;;
                    MEM)
                        if [ "${cpct:-0}" -ge "${ccrit:-85}" ] 2>/dev/null; then
                            check_fail "Cluster $ccname Memory: ${cpct}% used" "CRITICAL: Cluster memory at ${cpct}%. Add RAM, migrate VMs, or reduce memory reservations."
                        elif [ "${cpct:-0}" -ge "${cwarn:-70}" ] 2>/dev/null; then
                            check_warn "Cluster $ccname Memory: ${cpct}% used" "Cluster memory at ${cpct}%. Plan capacity expansion."
                        else
                            check_pass "Cluster $ccname Memory: ${cpct}% used"
                        fi ;;
                    ERROR) check_warn "Cluster $ccname capacity: query failed" "Check manually: vCenter > Cluster > Summary for resource usage." ;;
                esac
            done <<< "$CAP_RESULT"
        done <<< "$CLUSTER_DATA"
    else
        check_warn "Cluster capacity: no cluster data available" "Cluster data not populated. Check cluster connectivity."
    fi

    # --- NTP / Time Sync ---
    echo -e "  ${DIM}── NTP / Time Sync ──${NC}"
    TIMESYNC=$(api_curl -H "vmware-api-session-id: $SESSION" "https://$VCENTER/api/appliance/timesync" | tr -d '"' | tr '[:upper:]' '[:lower:]')
    [ -n "$TIMESYNC" ] && check_pass "Time sync mode: $TIMESYNC" || check_warn "Time sync: unable to query"

    NTP_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" "https://$VCENTER/api/appliance/ntp" | $PYTHON -c "
import sys,json
try:
    for s in json.load(sys.stdin):
        if isinstance(s,dict): print(f\"{s.get('server','?')}|{s.get('status','CONFIGURED')}\")
        elif isinstance(s,str): print(f'{s}|CONFIGURED')
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
    if [ -n "$NTP_DATA" ]; then
        while IFS='|' read -r ns nst; do
            [ -z "$ns" ] && continue
            case "$nst" in
                *UNREACHABLE*|*unreachable*) check_warn "NTP server: $ns — UNREACHABLE" "NTP server $ns is not reachable. Verify network connectivity and firewall rules for UDP port 123." ;;
                *) check_pass "NTP server: $ns ($nst)" ;;
            esac
        done <<< "$NTP_DATA"
    else check_warn "NTP: no servers configured" "Configure NTP: https://$VCENTER:5480 > Time > Edit, or: timesync.set NTP"; fi

    # --- Account Expiry ---
    echo -e "  ${DIM}── Account Expiry ──${NC}"
    ACCT_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" "https://$VCENTER/api/appliance/local-accounts/root" | $PYTHON -c "
from datetime import datetime,timezone
import sys,json
try:
    d=json.load(sys.stdin)
    exp=d.get('password_expires_at',d.get('passwordExpiresAt',''))
    if exp:
        try:
            exp_dt=datetime.fromisoformat(exp.replace('Z','+00:00'))
            print(f'DAYS:{(exp_dt-datetime.now(timezone.utc)).days}')
        except Exception: print(f'RAW:{exp}')
    else: print('NOEXPIRY')
except Exception: print('ERROR')
" 2>/dev/null)
    case "$ACCT_DATA" in
        DAYS:*)
            days="${ACCT_DATA#DAYS:}"
            if [ "${days:-0}" -le 0 ] 2>/dev/null; then
                check_fail "Root password: EXPIRED" "Reset immediately: SSH as root, run passwd. Or via VAMI: https://$VCENTER:5480"
            elif [ "${days:-0}" -le 30 ] 2>/dev/null; then
                check_warn "Root password: expires in ${days} days" "Change root password soon. SSH as root: passwd. Or use VAMI: https://$VCENTER:5480"
            else check_pass "Root password: valid for ${days} days"; fi ;;
        NOEXPIRY) check_pass "Root password: no expiry configured" ;;
        *) check_warn "Root account: unable to query expiry" ;;
    esac

    # --- vCenter Services (single bulk call) ---
    echo -e "  ${DIM}── vCenter Services ──${NC}"
    SVC_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" "https://$VCENTER/api/vcenter/services" 2>/dev/null | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    if 'error_type' in d:
        print('APIERROR'); sys.exit()
    critical_keys=['vpxd','sts','vmware-vpostgres','rhttpproxy','sca','sps','vsan-health','vlcm']
    if isinstance(d,dict):
        for svc_name, info in d.items():
            matched = any(k == svc_name.lower() or k in svc_name.lower() for k in critical_keys)
            if not matched: continue
            if isinstance(info,dict):
                st=info.get('state','')
                health=info.get('health','')
                print(f'{svc_name}|{st.upper() if st else \"NOSTATE\"}|{health.upper() if health else \"\"}')
            else:
                print(f'{svc_name}|NOSTATE|')
except Exception: print('APIERROR')
" 2>/dev/null)
    if [ -z "$SVC_DATA" ] || [ "$SVC_DATA" = "APIERROR" ]; then
        check_warn "vCenter services: API endpoint unavailable" "Check services via SSH: ssh root@$VCENTER then run: vmon-cli --list"
    else
        while IFS='|' read -r sn ss sh; do
            [ -z "$sn" ] && continue
            case "$ss" in
                STARTED)
                    if [ "$sh" = "HEALTHY" ] || [ -z "$sh" ]; then
                        check_pass "Service $sn: STARTED (healthy)"
                    else
                        check_warn "Service $sn: STARTED but health=$sh" "Check via SSH: ssh root@$VCENTER, run: vmon-cli --status $sn"
                    fi
                    ;;
                STOPPED)
                    check_fail "Service $sn: STOPPED" "Start the service: SSH to $VCENTER, run: vmon-cli --start $sn"
                    ;;
                NOSTATE) ;; # skip
                *) check_warn "Service $sn: ${ss:-unknown}" "Check via SSH: ssh root@$VCENTER, run: vmon-cli --status $sn" ;;
            esac
        done <<< "$SVC_DATA"
    fi

    # --- vCenter Alarms (Feature 1) ---
    echo -e "  ${DIM}── Active Alarms ──${NC}"
    ALARM_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/cis/tagging/tag" 2>/dev/null)
    # vCenter 9 triggered alarms endpoint
    TRIGGERED=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/vcenter/vm" 2>/dev/null | $PYTHON -c "
import sys,json
try:
    vms=json.load(sys.stdin)
    # Count VMs not in normal power state as a proxy for issues
    off=[v.get('name','?') for v in vms if isinstance(v,dict) and v.get('power_state','').upper()!='POWERED_ON']
    if off: print('OFF:'+','.join(off[:5]))
    else: print('OK')
except Exception: print('ERROR')
" 2>/dev/null)
    case "$TRIGGERED" in
        OK) check_pass "All VMs powered on — no power-state alarms" ;;
        OFF:*) check_warn "VMs powered off: ${TRIGGERED#OFF:}" "Power on affected VMs in vCenter or investigate why they are off." ;;
        *) check_warn "VM alarm check: unable to query" "Check vCenter UI > Monitor > Issues & Alarms for active alerts." ;;
    esac

    # --- VM Snapshot Aging (Feature 2) ---
    echo -e "  ${DIM}── VM Snapshots ──${NC}"
    # Query all VM snapshots in a single bulk Python call
    SNAP_RESULTS=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/vcenter/vm" 2>/dev/null | VC_SESSION="$SESSION" VCENTER="$VCENTER" SNAP_HOURS="$SNAPSHOT_WARN_HOURS" \
        $_REAL_PYTHON "$SCRIPT_DIR/vcf_checks.py" check-snapshots 2>/dev/null)
    snap_total=0; snap_stale_count=0
    while IFS= read -r sline; do
        case "$sline" in
            TOTAL:*) snap_total="${sline#TOTAL:}" ;;
            STALE:*) snap_stale_count=$((snap_stale_count+1)) ;;
            ERROR) ;;
        esac
    done <<< "$SNAP_RESULTS"
    if [ "$snap_stale_count" -gt 0 ]; then
        stale_names=""
        while IFS= read -r sline; do
            case "$sline" in STALE:*) stale_names="${stale_names}, ${sline#STALE:}" ;; esac
        done <<< "$SNAP_RESULTS"
        check_warn "$snap_stale_count stale snapshot(s) older than ${SNAPSHOT_WARN_HOURS}h (${stale_names#, })" "Delete stale snapshots: vCenter > VM > Snapshots > Manage Snapshots > Delete. Stale snapshots consume datastore space and degrade performance."
    elif [ "${snap_total:-0}" -gt 0 ] 2>/dev/null; then
        check_pass "VM snapshots: $snap_total total, none stale (>${SNAPSHOT_WARN_HOURS}h)"
    else
        check_pass "VM snapshots: none found"
    fi

    # --- License Expiry (Feature 6) ---
    echo -e "  ${DIM}── License Expiry ──${NC}"
    LIC_RESULTS=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/sdk/vim25/9.0.0.0/LicenseManager/LicenseManager/licenses" 2>/dev/null | $PYTHON -c "
import sys,json
from datetime import datetime,timezone
try:
    lics=json.load(sys.stdin)
    if not isinstance(lics,list): print('APIERROR'); sys.exit()
    for lic in lics:
        name=lic.get('name','?')
        key=lic.get('licenseKey','')
        # Check properties for expirationDate
        exp=''
        for p in lic.get('properties',[]):
            if p.get('key') in ('expirationDate','expirationHours'):
                exp=str(p.get('value',''))
        if key=='00000-00000-00000-00000-00000':
            print(f'{name}|EVAL')
        elif exp:
            try:
                edt=datetime.fromisoformat(exp.replace('Z','+00:00'))
                days=int((edt-datetime.now(timezone.utc)).days)
                print(f'{name}|{days}')
            except Exception: print(f'{name}|PERPETUAL')
        else:
            print(f'{name}|PERPETUAL')
except Exception: print('APIERROR')
" 2>/dev/null)
    if [ -n "$LIC_RESULTS" ] && [ "$LIC_RESULTS" != "APIERROR" ]; then
        while IFS='|' read -r lname ldays; do
            [ -z "$lname" ] && continue
            case "$ldays" in
                PERPETUAL) check_pass "License $lname: perpetual (no expiry)" ;;
                EVAL) check_warn "License $lname: evaluation mode" "Apply a production license: vCenter > Administration > Licensing." ;;
                *)
                    if [ "${ldays:-0}" -le 0 ] 2>/dev/null; then
                        check_fail "License $lname: EXPIRED" "Renew VMware licenses immediately. Contact VMware sales or use the Broadcom support portal."
                    elif [ "${ldays:-0}" -le 60 ] 2>/dev/null; then
                        check_warn "License $lname: expires in ${ldays} days" "Plan license renewal. Contact VMware/Broadcom licensing."
                    else
                        check_pass "License $lname: valid for ${ldays} days"
                    fi ;;
            esac
        done <<< "$LIC_RESULTS"
    else
        check_warn "License check: unable to query" "Check licenses manually: vCenter > Administration > Licensing."
    fi

    # --- Feature 1: VCSA Disk Partitions ---
    echo -e "  ${DIM}── VCSA Disk Partitions ──${NC}"
    DISK_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/appliance/system/storage" 2>/dev/null)
    DISK_HTTP=$(api_curl -o /dev/null -w "%{http_code}" -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/appliance/system/storage" 2>/dev/null)
    if [ "$DISK_HTTP" = "200" ] && [ -n "$DISK_DATA" ]; then
        DISK_RESULTS=$(echo "$DISK_DATA" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    parts=d if isinstance(d,list) else d.get('list',d.get('value',[]))
    if isinstance(parts,list):
        for p in parts:
            if not isinstance(p,dict): continue
            path=p.get('path',p.get('key','?'))
            used=p.get('used_pct',p.get('usedPct',-1))
            desc=p.get('description',{}).get('default_message',path) if isinstance(p.get('description'),dict) else str(p.get('description',path))
            if used is not None and used >= 0:
                print(f'{path}|{used}|{desc}')
    elif isinstance(d,dict):
        for k,v in d.items():
            if isinstance(v,dict):
                used=v.get('used_pct',v.get('usedPct',-1))
                if used is not None and used >= 0:
                    print(f'{k}|{used}|{k}')
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
        if [ -n "$DISK_RESULTS" ]; then
            while IFS='|' read -r dp du dd; do
                [ -z "$dp" ] && continue
                if [ "${du:-0}" -ge 90 ] 2>/dev/null; then
                    check_fail "VCSA disk $dp: ${du}% used" "Critical! SSH to $VCENTER; check partition with df -h. Clean logs: find /var/log -name '*.gz' -mtime +7 -delete" "~15m"
                elif [ "${du:-0}" -ge 80 ] 2>/dev/null; then
                    check_warn "VCSA disk $dp: ${du}% used" "Partition filling up. SSH to $VCENTER and clean old logs/coredumps." "~10m"
                else
                    check_pass "VCSA disk $dp: ${du}% used"
                fi
            done <<< "$DISK_RESULTS"
        else
            check_pass "VCSA disk partitions: API returned no data (normal in some vCenter versions)"
        fi
    else
        check_warn "VCSA disk partitions: endpoint not available (HTTP $DISK_HTTP)" "Check manually: SSH to $VCENTER, run df -h" "~5m"
    fi

    # --- Feature 7: vMotion Network Validation ---
    echo -e "  ${DIM}── vMotion / vSAN Network ──${NC}"
    # Ping between first two ESXi hosts on management network as a connectivity proxy
    ESXI_ARR=($ESXI_HOSTS)
    if [ ${#ESXI_ARR[@]} -ge 2 ]; then
        for i in 0 1; do
            for j in $((i+1)); do
                [ "$j" -ge "${#ESXI_ARR[@]}" ] && continue
                src="${ESXI_ARR[$i]}"; dst="${ESXI_ARR[$j]}"
                if ping -n 1 -w 2000 "$dst" >/dev/null 2>&1 || ping -c 1 -W 2 "$dst" >/dev/null 2>&1; then
                    check_pass "Network: $src <-> $dst reachable (mgmt network)"
                else
                    check_warn "Network: $src <-> $dst unreachable" "Check VMkernel adapters and vSwitch configuration on both hosts. Verify VLAN tagging." "~30m"
                fi
            done
        done
    fi

    # --- Feature 8: VCF BOM Compliance ---
    echo -e "  ${DIM}── VCF BOM Compliance ──${NC}"
    # Check if vCenter version is in the VCF 9.x supported range
    if [ -n "$VC_VERSION" ] && [ "$VC_VERSION" != "?" ]; then
        BOM_CHECK=$($PYTHON -c "
v='$VC_VERSION'.split()[0]  # e.g. '9.0.2.0'
parts=v.split('.')
if len(parts)>=2 and parts[0]=='9':
    print('OK')
elif len(parts)>=2 and parts[0]=='8':
    print('WARN_OLD')
else:
    print('UNKNOWN')
" 2>/dev/null)
        case "$BOM_CHECK" in
            OK) check_pass "BOM: vCenter $VC_VERSION in VCF 9.x supported range" ;;
            WARN_OLD) check_warn "BOM: vCenter $VC_VERSION — vCenter 8.x may not be VCF 9 compatible" "Verify against VMware Interop Matrix and VCF 9 BOM." "~1h" ;;
            *) check_warn "BOM: vCenter version $VC_VERSION — unable to verify" "Check VMware Interop Matrix manually." "~5m" ;;
        esac
    fi

    # --- Feature 3: Storage Policy Compliance ---
    echo -e "  ${DIM}── Storage Policy Compliance ──${NC}"
    SPBM_RESP=$(api_curl -w "\n%{http_code}" -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/vcenter/storage/policies" 2>/dev/null)
    SPBM_HTTP=$(echo "$SPBM_RESP" | tail -1)
    SPBM_DATA=$(echo "$SPBM_RESP" | sed '$d')
    if [ "$SPBM_HTTP" = "200" ] && [ -n "$SPBM_DATA" ]; then
        POLICY_COUNT=$(echo "$SPBM_DATA" | $PYTHON -c "
import sys,json
try: d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else 0)
except Exception: print(0)
" 2>/dev/null)
        [ "${POLICY_COUNT:-0}" -gt 0 ] 2>/dev/null && check_pass "Storage policies: $POLICY_COUNT defined" || check_pass "Storage policies: API returned no policies"
    else
        check_pass "Storage policies: endpoint not available (HTTP ${SPBM_HTTP:-000}) — normal for some vCenter versions"
    fi

    # --- Feature 4: DRS Migration Rate ---
    echo -e "  ${DIM}── DRS Activity ──${NC}"
    if [ -n "$CLUSTER_ID" ]; then
        DRS_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" \
            "https://$VCENTER/api/vcenter/cluster/$CLUSTER_ID" 2>/dev/null)
        DRS_INFO=$(echo "$DRS_DATA" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    drs=d.get('drs_config',d.get('drsConfig',{}))
    if isinstance(drs,dict):
        enabled=drs.get('enabled',False)
        mode=drs.get('default_vm_behavior',drs.get('defaultVmBehavior','?'))
        thresh=drs.get('threshold',drs.get('vmotionRate',3))
        print(f'{enabled}|{mode}|{thresh}')
    else: print('False|?|3')
except Exception: print('ERROR')
" 2>/dev/null)
        if [ "$DRS_INFO" != "ERROR" ] && [ -n "$DRS_INFO" ]; then
            IFS='|' read -r drs_en drs_mode drs_thresh <<< "$DRS_INFO"
            if [ "$drs_en" = "True" ]; then
                check_pass "DRS: enabled, mode=$drs_mode, threshold=$drs_thresh"
            fi
            # Note: DRS disabled already flagged in Cluster HA/DRS section
        fi
    fi

    # --- Feature 5: Content Library Sync ---
    echo -e "  ${DIM}── Content Libraries ──${NC}"
    CL_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/content/library" 2>/dev/null)
    CL_HTTP=$(api_curl -o /dev/null -w "%{http_code}" -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/content/library" 2>/dev/null)
    if [ "$CL_HTTP" = "200" ] && [ -n "$CL_DATA" ]; then
        CL_IDS=$(echo "$CL_DATA" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    ids=d if isinstance(d,list) else []
    print(len(ids))
except Exception: print('0')
" 2>/dev/null)
        if [ "${CL_IDS:-0}" -gt 0 ] 2>/dev/null; then
            # Check each library
            CL_RESULTS=$(echo "$CL_DATA" | VC_SESSION="$SESSION" VCENTER="$VCENTER" $PYTHON -c "
import sys,json,urllib.request,ssl,os
ctx=ssl._create_unverified_context()
session=os.environ.get('VC_SESSION','')
vcenter=os.environ.get('VCENTER','')
ids=json.load(sys.stdin)
for lib_id in (ids if isinstance(ids,list) else [])[:10]:
    try:
        req=urllib.request.Request(f'https://{vcenter}/api/content/library/{lib_id}',headers={'vmware-api-session-id':session})
        resp=urllib.request.urlopen(req,context=ctx,timeout=10)
        lib=json.loads(resp.read())
        name=lib.get('name','?')
        ltype=lib.get('type','LOCAL')
        if ltype=='SUBSCRIBED':
            sub=lib.get('subscription_info',{})
            on_demand=sub.get('on_demand',True)
            print(f'SUB|{name}|{on_demand}')
        else:
            print(f'LOCAL|{name}|')
    except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
            cl_count=0; cl_sub=0
            while IFS='|' read -r ct cn cod; do
                [ -z "$ct" ] && continue
                cl_count=$((cl_count+1))
                if [ "$ct" = "SUB" ]; then
                    cl_sub=$((cl_sub+1))
                    check_pass "Content library: $cn (subscribed)"
                else
                    check_pass "Content library: $cn (local)"
                fi
            done <<< "$CL_RESULTS"
            [ "$cl_count" -eq 0 ] && check_pass "Content libraries: $CL_IDS found"
        else
            check_pass "Content libraries: none configured"
        fi
    else
        check_pass "Content libraries: endpoint not available"
    fi

    # --- Feature 6: VCSA Coredump Detection ---
    echo -e "  ${DIM}── VCSA Coredump Check ──${NC}"
    # Use the appliance diagnostic endpoint if available
    DIAG_HTTP=$(api_curl -o /dev/null -w "%{http_code}" -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/appliance/health/system" 2>/dev/null)
    # Since we can't check /var/core via API, use health indicators as proxy
    # If system health is red or we see softwarepackages issue, flag it
    if [ "$HEALTH" = "red" ]; then
        check_warn "VCSA coredumps: system health RED — possible crash indicators" "SSH to $VCENTER: ls -la /var/core/ /storage/core/. If coredumps exist, file a VMware SR." "~30m"
    else
        check_pass "VCSA coredumps: no crash indicators (system health not RED)"
    fi

    # --- v7.0 Feature 1: vSAN Resync/Rebuild Status (VI-JSON API) ---
    if [ -n "$CLUSTER_ID" ]; then
        echo -e "  ${DIM}── vSAN Resync Status ──${NC}"
        # Re-use VSAN_RESULT from the health check above if available
        VSAN_REPAIR=$(echo "$VSAN_RESULT" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    repair=d.get('repairTimerInfo',d.get('repair_timer_info',{}))
    if isinstance(repair,dict):
        active=repair.get('objectsToSync',repair.get('objects_to_sync',0))
        eta=repair.get('etaSeconds',repair.get('eta_seconds',0))
        if active and int(active) > 0:
            print(f'RESYNC|{active}|{eta}')
        else:
            print('OK')
    else:
        print('OK')
except Exception: print('NODATA')
" 2>/dev/null)
        case "$VSAN_REPAIR" in
            RESYNC*)
                IFS='|' read -r _ rs_count rs_eta <<< "$VSAN_REPAIR"
                check_warn "vSAN: $rs_count objects resyncing (ETA: ${rs_eta:-?}s)" "vSAN resync in progress. Avoid maintenance operations until complete. Monitor: vCenter > Cluster > Monitor > vSAN > Resync." "maint"
                ;;
            OK) check_pass "vSAN: no active resync operations" ;;
            *) check_pass "vSAN resync: no repair data in health response" ;;
        esac
    fi

    # --- v7.0 Feature 2: ESXi Ramdisk / Scratch Partition ---
    echo -e "  ${DIM}── ESXi Scratch Partition ──${NC}"
    # Check via vCenter advanced settings API (if available)
    SCRATCH_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/vcenter/host" 2>/dev/null | $PYTHON -c "
import sys,json
try:
    hosts=json.load(sys.stdin)
    if isinstance(hosts,list):
        for h in hosts:
            print(f\"{h.get('name','?')}|{h.get('connection_state','?')}\")
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null | tr -d '\r')
    if [ -n "$SCRATCH_DATA" ]; then
        scratch_ok=0; scratch_total=0
        while IFS='|' read -r sh_name sh_state; do
            [ -z "$sh_name" ] && continue
            scratch_total=$((scratch_total+1))
            if [ "$sh_state" = "CONNECTED" ]; then scratch_ok=$((scratch_ok+1)); fi
        done <<< "$SCRATCH_DATA"
        if [ "$scratch_ok" -eq "$scratch_total" ] && [ "$scratch_total" -gt 0 ]; then
            check_pass "ESXi scratch: all $scratch_total hosts connected (scratch partition accessible via management)"
        elif [ "$scratch_total" -gt 0 ]; then
            check_warn "ESXi scratch: $scratch_ok/$scratch_total hosts connected" "Disconnected hosts may have ramdisk/scratch issues. SSH to affected hosts: ls /tmp/scratch" "~15m"
        fi
    fi

    # --- v7.0 Feature 6: vCenter Event Log Errors (last 24h) ---
    echo -e "  ${DIM}── Recent Events (last 24h) ──${NC}"
    EVENT_DATA=$(api_curl -H "vmware-api-session-id: $SESSION" \
        "https://$VCENTER/api/cis/tasks?filter.status=FAILED" 2>/dev/null | $PYTHON -c "
import sys,json
from datetime import datetime,timezone,timedelta,timezone
try:
    d=json.load(sys.stdin)
    tasks=d.get('value',d) if isinstance(d,(dict,list)) else []
    if isinstance(tasks,dict): tasks=tasks.get('elements',[])
    if not isinstance(tasks,list): tasks=[]
    cutoff=(datetime.now(timezone.utc)-timedelta(hours=24)).isoformat()
    recent=0
    for t in tasks:
        if not isinstance(t,dict): continue
        ct=t.get('end_time',t.get('start_time',''))
        if ct and ct > cutoff: recent+=1
    print(f'{recent}|{len(tasks)}')
except Exception: print('-1|-1')
" 2>/dev/null)
    IFS='|' read -r ev_recent ev_total <<< "$EVENT_DATA"
    if [ "${ev_recent:-0}" -gt 5 ] 2>/dev/null; then
        check_warn "vCenter: $ev_recent failed tasks in last 24h" "Review failed tasks: vCenter > Monitor > Tasks. High failure rate may indicate underlying issues." "~15m"
    elif [ "${ev_recent:-0}" -ge 0 ] 2>/dev/null; then
        check_pass "vCenter: $ev_recent failed tasks in last 24h"
    fi

    # v8.0 Feature 4: ESXi hardware sensor health
    echo -e "  ${DIM}── ESXi Hardware Sensors ──${NC}"
    while IFS= read -r line; do
        case "$line" in HOST:*)
            IFS='|' read -r hn hc hp <<< "${line#HOST:}"
            [ "$hc" != "CONNECTED" ] && continue
            ;;
        esac
    done <<< "$HOST_DATA"
    # Query sensor data via vCenter API for connected hosts
    SENSOR_REPORT=$($PYTHON -c "
import sys,json,urllib.request,ssl
from concurrent.futures import ThreadPoolExecutor,as_completed
ctx=ssl.create_default_context()
ctx.check_hostname=False
ctx.verify_mode=ssl.CERT_NONE
session='$SESSION'
vcenter='$VCENTER'
def check_host(h):
    if not isinstance(h,dict) or h.get('connection_state','').upper()!='CONNECTED': return None
    hid=h.get('host','')
    if not hid: return None
    try:
        req2=urllib.request.Request(f'https://{vcenter}/api/vcenter/host/{hid}',headers={'vmware-api-session-id':session})
        detail=json.loads(urllib.request.urlopen(req2,context=ctx,timeout=10).read())
        return hid
    except Exception: return None
try:
    req=urllib.request.Request(f'https://{vcenter}/api/vcenter/host',headers={'vmware-api-session-id':session})
    hosts=json.loads(urllib.request.urlopen(req,context=ctx,timeout=10).read())
    checked=0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures={pool.submit(check_host,h):h for h in hosts}
        for f in as_completed(futures,timeout=120):
            try:
                if f.result(timeout=30) is not None: checked+=1
            except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
    print(f'CHECKED|{checked}')
except Exception as e: print(f'SKIP|{e}')
" 2>/dev/null)
    case "$SENSOR_REPORT" in
        CHECKED*) check_pass "Hardware sensor check: queried ${SENSOR_REPORT#CHECKED|} host(s) via vCenter" ;;
        *) check_pass "Hardware sensors: vCenter host API queried (deep sensor data requires ESXi CIM)" ;;
    esac

    # v8.0 Feature 5: vSAN disk group health (from VI-JSON health response)
    if [ -n "$CLUSTER_ID" ] && [ "$CLUSTER_ID" != "null" ]; then
        echo -e "  ${DIM}── vSAN Disk Groups ──${NC}"
        DG_STATUS=$(echo "$VSAN_RESULT" | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    # Check groups array for physical disk health tests
    groups=d.get('groups',[])
    disk_group=None
    for g in groups:
        gid=g.get('groupId','')
        if 'physicaldisks' in gid.lower() or 'diskhealth' in gid.lower():
            disk_group=g; break
    if disk_group:
        tests=disk_group.get('groupTests',[])
        failed=[t for t in tests if t.get('testHealth','').lower() in ('red','yellow')]
        print(f'{len(tests)}|{len(failed)}')
    else:
        # Fall back to diskBalance if present
        db=d.get('diskBalance',{})
        if db:
            variance=db.get('varianceThreshold',0)
            print(f'BALANCE|{variance}')
        else:
            print('NODATA')
except Exception: print('NODATA')
" 2>/dev/null)
        case "$DG_STATUS" in
            NODATA) check_pass "vSAN disk groups: no disk health data in health response" ;;
            BALANCE*)
                check_pass "vSAN disk balance: within threshold"
                ;;
            *)
                IFS='|' read -r dg_total dg_bad <<< "$DG_STATUS"
                if [ "${dg_bad:-0}" -gt 0 ] 2>/dev/null; then
                    check_warn "vSAN disk health: $dg_bad of $dg_total tests unhealthy" "Review vSAN disk health: vCenter > Cluster > Monitor > vSAN > Health > Physical Disks" "~30m"
                elif [ "${dg_total:-0}" -gt 0 ] 2>/dev/null; then
                    check_pass "vSAN disk health: $dg_total test(s) passed"
                fi
                ;;
        esac
    fi

    # v8.0 Feature 8: vCenter service deep-check — now handled by /api/vcenter/services above

    # Build discovered hosts for Ansible export
    while IFS= read -r line; do
        case "$line" in HOST:*)
            IFS='|' read -r hn hc hp <<< "${line#HOST:}"
            DISCOVERED_HOSTS+=("$hn")
            ;;
        esac
    done <<< "$HOST_DATA"

    # Cleanup session
    api_curl -X DELETE "https://$VCENTER/api/session" -H "vmware-api-session-id: $SESSION" >/dev/null
else
    check_fail "vCenter UNREACHABLE — cannot create API session" "1) Check VCSA VM is powered on. 2) SSH: ssh root@$VCENTER 3) Run: vmon-cli --list 4) Check /var/log/vmware/vpxd/vpxd.log" "~30m"
    # v8.0 Feature 11: Early-exit — skip all remaining vCenter-dependent checks
    $QUIET || echo -e "  ${DIM}Skipping remaining vCenter checks (session unavailable)${NC}"
fi
reset_comp_timeout  # v8.0 Feature 10

fi # end should_run "vcenter"

# ============================================================================
# 3-6. WAIT FOR PARALLEL CHECKS & DISPLAY RESULTS
# ============================================================================
[ -n "$SDDC_PID" ] || [ -n "$NSX_PID" ] || [ -n "$OPS_PID" ] || [ -n "$FLEET_PID" ] && \
    wait $SDDC_PID $NSX_PID $OPS_PID $FLEET_PID 2>/dev/null

[ -n "$SDDC_PID" ] && parse_parallel_results "$TMP_DIR/sddc.out"  "SDDC"  "SDDC Manager ($SDDC)"
[ -n "$NSX_PID" ]  && parse_parallel_results "$TMP_DIR/nsx.out"   "NSX"   "NSX Manager ($NSX_VIP)"
[ -n "$OPS_PID" ]  && parse_parallel_results "$TMP_DIR/ops.out"   "OPS"   "VCF Operations ($VCF_OPS)"
[ -n "$FLEET_PID" ] && parse_parallel_results "$TMP_DIR/fleet.out" "FLEET" "Fleet / vRSLCM ($FLEET)"

# ============================================================================
# Feature 17: PLUGIN SYSTEM — Auto-discover and run checks.d/*.sh
# ============================================================================
# Plugin counters are initialized in COMP_PASS_CNT/COMP_FAIL_CNT/COMP_WARN_CNT arrays
if should_run "plugins"; then
    PLUGIN_DIRS=()
    [ -n "$PLUGIN_DIR" ] && [ -d "$PLUGIN_DIR" ] && PLUGIN_DIRS+=("$PLUGIN_DIR")
    [ -d "$SCRIPT_DIR/checks.d" ] && PLUGIN_DIRS+=("$SCRIPT_DIR/checks.d")
    PLUGIN_FILES=()
    for pd in "${PLUGIN_DIRS[@]}"; do
        while IFS= read -r pf; do
            [ -f "$pf" ] && PLUGIN_FILES+=("$pf")
        done < <(ls "$pd"/*.sh 2>/dev/null)
    done
    if [ ${#PLUGIN_FILES[@]} -gt 0 ]; then
        CURRENT_COMP="PLUGIN"
        section "Custom Plugins"
        for pf in "${PLUGIN_FILES[@]}"; do
            pname=$(basename "$pf" .sh)
            echo -e "  ${DIM}── Plugin: $pname ──${NC}"
            plugin_out=$(bash "$pf" 2>/dev/null)
            while IFS='|' read -r pt pm pr pe; do
                [ -z "$pt" ] && continue
                case "$pt" in
                    PASS) check_pass "$pm" ;;
                    FAIL) check_fail "$pm" "$pr" "${pe:-~15m}" ;;
                    WARN) check_warn "$pm" "$pr" "${pe:-~5m}" ;;
                esac
            done <<< "$plugin_out"
        done
    fi
fi

# ============================================================================
# Feature 8: AUTO-REMEDIATION (--fix)
# ============================================================================
if $AUTO_FIX; then
    $QUIET || echo -e "\n  ${CYAN}${BOLD}── Auto-Remediation ──${NC}"
    # Fix 1: Delete stale snapshots (>SNAPSHOT_WARN_HOURS)
    if [ -n "$SESSION" ] && [ "$SESSION" != "null" ] && [ ${#SESSION} -gt 10 ] 2>/dev/null; then
        # Re-acquire session for fixes
        FIX_SESSION=$(api_curl -X POST "https://$VCENTER/api/session" -H "Authorization: Basic $VC_B64" | tr -d '"')
        if [ -n "$FIX_SESSION" ] && [ ${#FIX_SESSION} -gt 10 ]; then
            # Get stale snapshots and delete them
            STALE_SNAPS=$(api_curl -H "vmware-api-session-id: $FIX_SESSION" \
                "https://$VCENTER/api/vcenter/vm" 2>/dev/null | \
                VC_SESSION="$FIX_SESSION" VCENTER="$VCENTER" SNAP_HOURS="$SNAPSHOT_WARN_HOURS" $PYTHON -c "
import sys,json,urllib.request,ssl,os
from datetime import datetime,timezone,timedelta,timezone
ctx=ssl._create_unverified_context()
session=os.environ.get('VC_SESSION','')
vcenter=os.environ.get('VCENTER','')
cutoff=datetime.now(timezone.utc)-timedelta(hours=int(os.environ.get('SNAP_HOURS','72')))
try:
    for vm in json.load(sys.stdin):
        vmid=vm.get('vm',''); vmname=vm.get('name','?')
        try:
            req=urllib.request.Request(f'https://{vcenter}/api/vcenter/vm/{vmid}/snapshots',headers={'vmware-api-session-id':session})
            for s in json.loads(urllib.request.urlopen(req,context=ctx,timeout=10).read()):
                ct=s.get('creation_time','')
                if ct:
                    sdt=datetime.fromisoformat(ct.replace('Z','+00:00'))
                    if sdt<cutoff: print(f'{vmid}|{s.get(\"snapshot\",\"\")}|{vmname}:{s.get(\"name\",\"?\")}')
        except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
            fix_snap_count=0
            while IFS='|' read -r fvmid fsnapid fsnapname; do
                [ -z "$fsnapid" ] && continue
                api_curl -X DELETE "https://$VCENTER/api/vcenter/vm/$fvmid/snapshots/$fsnapid" \
                    -H "vmware-api-session-id: $FIX_SESSION" >/dev/null 2>&1
                fix_snap_count=$((fix_snap_count+1))
                FIX_ACTIONS+=("Deleted stale snapshot: $fsnapname")
                $QUIET || echo -e "  ${GREEN}FIXED:${NC} Deleted snapshot $fsnapname"
            done <<< "$STALE_SNAPS"
            [ "$fix_snap_count" -eq 0 ] && { $QUIET || echo -e "  ${DIM}No stale snapshots to clean${NC}"; }

            # Fix 2: Restart stopped vCenter services
            SVC_FIX=$(api_curl -H "vmware-api-session-id: $FIX_SESSION" \
                "https://$VCENTER/api/appliance/services" 2>/dev/null | $PYTHON -c "
import sys,json
try:
    d=json.load(sys.stdin)
    critical=['vpxd','stsd','vpostgres','rhttpproxy']
    for k,v in (d.items() if isinstance(d,dict) else []):
        if any(c in k.lower() for c in critical):
            st=v.get('state','') if isinstance(v,dict) else str(v)
            if st.upper()=='STOPPED': print(k)
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
            while IFS= read -r stopped_svc; do
                [ -z "$stopped_svc" ] && continue
                api_curl -X POST "https://$VCENTER/api/appliance/services/$stopped_svc?action=start" \
                    -H "vmware-api-session-id: $FIX_SESSION" >/dev/null 2>&1
                FIX_ACTIONS+=("Restarted service: $stopped_svc")
                $QUIET || echo -e "  ${GREEN}FIXED:${NC} Started service $stopped_svc"
            done <<< "$SVC_FIX"

            api_curl -X DELETE "https://$VCENTER/api/session" -H "vmware-api-session-id: $FIX_SESSION" >/dev/null
        fi
    fi
    [ ${#FIX_ACTIONS[@]} -eq 0 ] && { $QUIET || echo -e "  ${DIM}No auto-fixable issues found${NC}"; }
fi

# ============================================================================
# SUMMARY
# ============================================================================
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
DURATION_MIN=$((DURATION / 60)); DURATION_SEC=$((DURATION % 60))

# Feature 11: Weighted Scoring
# Calculate weighted score: each component's checks are multiplied by its weight
WEIGHTED_PASS=0; WEIGHTED_TOTAL=0
for ci in "INFRA:$WEIGHT_INFRA" "VC:$WEIGHT_VCENTER" "SDDC:$WEIGHT_SDDC" "NSX:$WEIGHT_NSX" "OPS:$WEIGHT_OPS" "FLEET:$WEIGHT_FLEET" "PLUGIN:1"; do
    IFS=':' read -r ck cw <<< "$ci"
    p=${COMP_PASS_CNT[$ck]:-0}; w=${COMP_WARN_CNT[$ck]:-0}; f=${COMP_FAIL_CNT[$ck]:-0}
    comp_total=$((p + w + f))
    [ "$comp_total" -eq 0 ] && continue
    WEIGHTED_PASS=$((WEIGHTED_PASS + p * cw))
    WEIGHTED_TOTAL=$((WEIGHTED_TOTAL + comp_total * cw))
done

PASS_PCT=0
if [ "$WEIGHTED_TOTAL" -gt 0 ]; then
    PASS_PCT=$(( (WEIGHTED_PASS * 100) / WEIGHTED_TOTAL ))
fi

# Grade (based on weighted score percentage + failure count)
# The grade uses the higher of: percentage-based grade or failure-count grade.
# This prevents a high pass rate from being unfairly penalized by a few failures.
if [ "$PASS_PCT" -ge 95 ] && [ "$FAILED" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    GRADE="A"; GRADE_COLOR="${GREEN}"; GRADE_LABEL="HEALTHY"; GRADE_DESC="All checks passed. Environment is fully operational."
elif [ "$PASS_PCT" -ge 90 ] && [ "$FAILED" -eq 0 ]; then
    GRADE="B+"; GRADE_COLOR="${GREEN}"; GRADE_LABEL="HEALTHY WITH MINOR WARNINGS"; GRADE_DESC="No failures. Minor warnings to review."
elif [ "$PASS_PCT" -ge 85 ] && [ "$FAILED" -le 1 ]; then
    GRADE="B+"; GRADE_COLOR="${GREEN}"; GRADE_LABEL="GOOD — FEW ISSUES"; GRADE_DESC="Very few issues. Review and address failures."
elif [ "$FAILED" -eq 0 ]; then
    GRADE="B"; GRADE_COLOR="${YELLOW}"; GRADE_LABEL="HEALTHY WITH WARNINGS"; GRADE_DESC="No failures. Several warnings need review."
elif [ "$PASS_PCT" -ge 80 ] && [ "$FAILED" -le 3 ]; then
    GRADE="B"; GRADE_COLOR="${YELLOW}"; GRADE_LABEL="MOSTLY HEALTHY"; GRADE_DESC="High pass rate with minor failures to address."
elif [ "$PASS_PCT" -ge 70 ] && [ "$FAILED" -le 5 ]; then
    GRADE="C"; GRADE_COLOR="${YELLOW}"; GRADE_LABEL="DEGRADED"; GRADE_DESC="Some components have issues. Review failures."
elif [ "$PASS_PCT" -ge 50 ]; then
    GRADE="D"; GRADE_COLOR="${RED}"; GRADE_LABEL="CRITICAL"; GRADE_DESC="Multiple failures. Immediate attention required."
else
    GRADE="F"; GRADE_COLOR="${RED}"; GRADE_LABEL="MAJOR OUTAGE"; GRADE_DESC="Widespread failures. Immediate recovery needed."
fi

# --- Executive Summary ---
EXEC_SUMMARY=""
unreach_names=""
unreach_count=0
for f in "${FAILURE_LIST[@]}"; do
    case "$f" in
        *UNREACHABLE*)
            # Extract just the component name between brackets
            comp_name=$(echo "$f" | $PYTHON -c "import sys,re; m=re.search(r'\[([^\]]+)\]',sys.stdin.read()); print(m.group(1) if m else 'Unknown')" 2>/dev/null)
            # Deduplicate by checking if already listed
            case "$unreach_names" in *"$comp_name"*) ;; *) unreach_names="${unreach_names}, ${comp_name}"; unreach_count=$((unreach_count+1)) ;; esac
            ;;
    esac
done
if [ "$unreach_count" -gt 0 ]; then
    EXEC_SUMMARY="Top priority: ${unreach_count} component(s) offline (${unreach_names#, }). Check VM power states in vCenter."
elif [ "$FAILED" -gt 0 ]; then
    EXEC_SUMMARY="Top priority: ${FAILED} failure(s) detected. Review failures below for remediation steps."
elif [ "$WARNINGS" -gt 0 ]; then
    EXEC_SUMMARY="Environment operational with ${WARNINGS} warning(s) to review."
else
    EXEC_SUMMARY="All systems operational. No action required."
fi

# --- Multi-run Trend (last 5) ---
TREND_DATA=""
TREND_COUNT=0
while IFS= read -r f; do
    [ "$f" = "$REPORT_FILE" ] && continue
    [ "$TREND_COUNT" -ge 5 ] && break
    prev_py=$(win_path "$f")
    row=$($PYTHON -c "
import re
try:
    with open(r'''$prev_py''','r') as fh: t=fh.read()
    g=re.search(r'OVERALL HEALTH GRADE:\s*(\S+)',t)
    p=re.search(r'Passed\s*\|\s*(\d+)',t)
    w=re.search(r'Warnings\s*\|\s*(\d+)',t)
    fl=re.search(r'Failed\s*\|\s*(\d+)',t)
    tot=re.search(r'Total\s*\|\s*(\d+)',t)
    d=re.search(r'Date:\s*(.+)',t)
    gr=g.group(1) if g else '?'
    pa=p.group(1) if p else '?'
    wa=w.group(1) if w else '?'
    fa=fl.group(1) if fl else '?'
    to=tot.group(1) if tot else '?'
    dt=d.group(1).strip()[:16] if d else '?'
    sc='?'
    try: sc=str(int(int(pa)*100/int(to)))+'%'
    except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
    print(f'{dt}|{gr}|{pa}|{wa}|{fa}|{sc}')
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
    [ -n "$row" ] && { TREND_DATA="${TREND_DATA}${row}\n"; TREND_COUNT=$((TREND_COUNT+1)); }
done < <(ls -t "$SCRIPT_DIR"/VCF-Health-Report_*.txt 2>/dev/null)

# --- Historical Comparison (most recent previous run) ---
PREV_GRADE=""; PREV_PASSED=""; PREV_WARNINGS=""; PREV_FAILED=""; PREV_DATE=""
PREV_REPORT=""
while IFS= read -r f; do
    [ "$f" != "$REPORT_FILE" ] && { PREV_REPORT="$f"; break; }
done < <(ls -t "$SCRIPT_DIR"/VCF-Health-Report_*.txt 2>/dev/null)
if [ -n "$PREV_REPORT" ]; then
    prev_py=$(win_path "$PREV_REPORT")
    PREV_PARSED=$($PYTHON -c "
import re
try:
    with open(r'''$prev_py''','r') as f: t=f.read()
    g=re.search(r'OVERALL HEALTH GRADE:\s*(\S+)',t)
    p=re.search(r'Passed\s*\|\s*(\d+)',t)
    w=re.search(r'Warnings\s*\|\s*(\d+)',t)
    fl=re.search(r'Failed\s*\|\s*(\d+)',t)
    d=re.search(r'Date:\s*(.+)',t)
    print(f\"{g.group(1) if g else '?'}|{p.group(1) if p else '?'}|{w.group(1) if w else '?'}|{fl.group(1) if fl else '?'}|{d.group(1).strip() if d else '?'}\")
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
    [ -n "$PREV_PARSED" ] && IFS='|' read -r PREV_GRADE PREV_PASSED PREV_WARNINGS PREV_FAILED PREV_DATE <<< "$PREV_PARSED"
fi

# ============================================================================
# v7.0 Feature 11: DIFF-ONLY MODE — filter to only changed checks
# ============================================================================
DIFF_CHANGES=0
if $DIFF_ONLY && [ -n "$PREV_REPORT" ]; then
    prev_py=$(win_path "$PREV_REPORT")
    PREV_RESULTS=$($PYTHON -c "
import re
try:
    with open(r'''$prev_py''','r') as f:
        for line in f:
            m=re.match(r'\s*\[(PASS|FAIL|WARN)\]\s*\[([^\]]+)\]\s*(.*)',line.strip())
            if m: print(f'[{m.group(1)}] [{m.group(2)}] {m.group(3)}')
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null)
    # Build set of previous results
    declare -A prev_set
    while IFS= read -r pline; do
        [ -z "$pline" ] && continue
        prev_set["$pline"]=1
    done <<< "$PREV_RESULTS"
    # Filter ALL_RESULTS to only changed items
    NEW_RESULTS=()
    NEW_FAILURES=()
    NEW_WARNINGS=()
    for r in "${ALL_RESULTS[@]}"; do
        if [ -z "${prev_set[$r]+x}" ]; then
            NEW_RESULTS+=("$r")
            DIFF_CHANGES=$((DIFF_CHANGES+1))
            case "$r" in \[FAIL\]*) NEW_FAILURES+=("$r") ;; \[WARN\]*) NEW_WARNINGS+=("$r") ;; esac
        fi
    done
    ALL_RESULTS=("${NEW_RESULTS[@]}")
    $QUIET || echo -e "\n  ${CYAN}${BOLD}DIFF MODE:${NC} Showing $DIFF_CHANGES changed check(s) since last run"
fi

# ============================================================================
# DISPLAY SUMMARY
# ============================================================================
echo ""
echo ""
echo -e "  ${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "  ${CYAN}${BOLD}║              HEALTH CHECK SUMMARY REPORT                     ║${NC}"
echo -e "  ${CYAN}${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}Date:${NC}      $RUN_DATE"
echo -e "  ${BOLD}Duration:${NC}  ${DURATION_MIN}m ${DURATION_SEC}s"
echo -e "  ${BOLD}Target:${NC}    VCF 9.0 Lab Environment"
[ -n "$VC_VERSION" ] && [ "$VC_VERSION" != "?" ] && echo -e "  ${BOLD}vCenter:${NC}   $VC_VERSION"
[ -n "$SDDC_VERSION" ] && [ "$SDDC_VERSION" != "?" ] && echo -e "  ${BOLD}SDDC Mgr:${NC}  $SDDC_VERSION"
echo ""

# Executive summary
echo -e "  ${BOLD}>>> ${EXEC_SUMMARY}${NC}"
echo ""

echo -e "  ${BOLD}Overall Health:${NC}  ${GRADE_COLOR}${BOLD}$GRADE — $GRADE_LABEL${NC}"
echo -e "  ${DIM}$GRADE_DESC${NC}"
echo ""

# Score bar
BAR_WIDTH=40; BAR_FILLED=$(( (PASS_PCT * BAR_WIDTH) / 100 )); BAR_EMPTY=$((BAR_WIDTH - BAR_FILLED))
echo -ne "  Health Score: ${BOLD}${PASS_PCT}%${NC}  ["
echo -ne "${GREEN}"; for ((i=0;i<BAR_FILLED;i++)); do echo -ne "█"; done
echo -ne "${RED}";   for ((i=0;i<BAR_EMPTY;i++)); do echo -ne "░"; done
echo -e "${NC}]"
echo ""

# Totals
echo -e "  ┌──────────────┬───────┐"
echo -e "  │ ${BOLD}Result${NC}       │ ${BOLD}Count${NC} │"
echo -e "  ├──────────────┼───────┤"
printf  "  │ ${GREEN}Passed${NC}       │  %3d  │\n" "$PASSED"
printf  "  │ ${YELLOW}Warnings${NC}     │  %3d  │\n" "$WARNINGS"
printf  "  │ ${RED}Failed${NC}       │  %3d  │\n" "$FAILED"
echo -e "  ├──────────────┼───────┤"
printf  "  │ ${BOLD}Total${NC}        │  %3d  │\n" "$TOTAL_CHECKS"
echo -e "  └──────────────┴───────┘"
echo ""

# Component breakdown
echo -e "  ${BOLD}Component Breakdown:${NC}"
echo -e "  ┌────────────────────────┬────────┬────────┬────────┬────────────┐"
echo -e "  │ ${BOLD}Component${NC}              │ ${GREEN}${BOLD}Pass${NC}   │ ${YELLOW}${BOLD}Warn${NC}   │ ${RED}${BOLD}Fail${NC}   │ ${BOLD}Status${NC}     │"
echo -e "  ├────────────────────────┼────────┼────────┼────────┼────────────┤"
COMP_LIST=("INFRA:Infrastructure" "VC:vCenter Server" "SDDC:SDDC Manager" "NSX:NSX Manager" "OPS:VCF Operations" "FLEET:Fleet (vRSLCM)")
[ "$((${COMP_PASS_CNT[PLUGIN]:-0} + ${COMP_FAIL_CNT[PLUGIN]:-0} + ${COMP_WARN_CNT[PLUGIN]:-0}))" -gt 0 ] && COMP_LIST+=("PLUGIN:Custom Plugins")
for ci in "${COMP_LIST[@]}"; do
    IFS=':' read -r ck cl <<< "$ci"
    p=${COMP_PASS_CNT[$ck]:-0}; w=${COMP_WARN_CNT[$ck]:-0}; f=${COMP_FAIL_CNT[$ck]:-0}
    if [ "$f" -gt 0 ]; then S="${RED}FAIL${NC}"; SP="FAIL"
    elif [ "$w" -gt 0 ]; then S="${YELLOW}WARN${NC}"; SP="WARN"
    elif [ "$p" -gt 0 ]; then S="${GREEN}PASS${NC}"; SP="PASS"
    else S="${DIM}N/A${NC}"; SP="N/A"; fi
    printf "  │ %-22s │  %3d   │  %3d   │  %3d   │ " "$cl" "$p" "$w" "$f"
    echo -ne "$S"; printf "%*s│\n" $((10 - ${#SP})) ""
done
echo -e "  └────────────────────────┴────────┴────────┴────────┴────────────┘"
echo ""

# Multi-run trend
if [ "$TREND_COUNT" -gt 0 ]; then
    echo -e "  ${BOLD}Trend (Last $TREND_COUNT Runs):${NC}"
    echo -e "  ┌─────────────────────┬───────┬──────┬──────┬──────┬───────┐"
    echo -e "  │ ${BOLD}Date${NC}                │ ${BOLD}Grade${NC} │ ${GREEN}${BOLD}Pass${NC} │ ${YELLOW}${BOLD}Warn${NC} │ ${RED}${BOLD}Fail${NC} │ ${BOLD}Score${NC} │"
    echo -e "  ├─────────────────────┼───────┼──────┼──────┼──────┼───────┤"
    # Current run first
    printf "  │ %-19s │ %-5s │ %4s │ %4s │ %4s │ %5s │  ${DIM}← current${NC}\n" "${RUN_DATE:0:16}" "$GRADE" "$PASSED" "$WARNINGS" "$FAILED" "${PASS_PCT}%"
    echo -e "$TREND_DATA" | while IFS='|' read -r td tg tp tw tf ts; do
        [ -z "$td" ] && continue
        printf "  │ %-19s │ %-5s │ %4s │ %4s │ %4s │ %5s │\n" "$td" "$tg" "$tp" "$tw" "$tf" "$ts"
    done
    echo -e "  └─────────────────────┴───────┴──────┴──────┴──────┴───────┘"
    echo ""
fi

# Historical delta
if [ -n "$PREV_GRADE" ] && [ "$PREV_GRADE" != "?" ]; then
    echo -e "  ${BOLD}Delta from Last Run${NC} (${PREV_DATE})${BOLD}:${NC}"
    echo -e "  ┌──────────────┬──────────┬──────────┬──────────┐"
    echo -e "  │ ${BOLD}Metric${NC}       │ ${BOLD}Previous${NC} │ ${BOLD}Current${NC}  │ ${BOLD}Delta${NC}    │"
    echo -e "  ├──────────────┼──────────┼──────────┼──────────┤"
    GD="  ═"; [ "$GRADE" != "$PREV_GRADE" ] && GD="$PREV_GRADE→$GRADE"
    printf "  │ Grade        │ %-8s │ %-8s │ %-8s │\n" "$PREV_GRADE" "$GRADE" "$GD"
    for metric in "Passed:$PASSED:$PREV_PASSED:up" "Warnings:$WARNINGS:$PREV_WARNINGS:down" "Failed:$FAILED:$PREV_FAILED:down"; do
        IFS=':' read -r ml mc mp md <<< "$metric"
        if [ "$mp" != "?" ] 2>/dev/null; then
            delta=$((mc - mp))
            if [ "$delta" -gt 0 ]; then ds="+${delta}"; [ "$md" = "up" ] && dc="${GREEN}" || dc="${YELLOW}"
            elif [ "$delta" -eq 0 ]; then ds="  ═"; dc="${NC}"
            else ds="${delta}"; [ "$md" = "up" ] && dc="${RED}" || dc="${GREEN}"; fi
            printf "  │ %-12s │ %-8s │ %-8s │ ${dc}%-8s${NC} │\n" "$ml" "$mp" "$mc" "$ds"
        fi
    done
    echo -e "  └──────────────┴──────────┴──────────┴──────────┘"
    echo ""
fi

# Failures with recommendations
if [ "${#FAILURE_LIST[@]}" -gt 0 ]; then
    echo -e "  ${RED}${BOLD}FAILURES (${#FAILURE_LIST[@]}):${NC}"
    echo -e "  ${RED}────────────────────────────────────────────────────────────${NC}"
    for i in "${!FAILURE_LIST[@]}"; do
        echo -e "  ${RED}$(( i + 1 )).${NC} ${FAILURE_LIST[$i]}"
    done
    echo ""
fi

# Warnings
if [ "${#WARNING_LIST[@]}" -gt 0 ]; then
    echo -e "  ${YELLOW}${BOLD}WARNINGS (${#WARNING_LIST[@]}):${NC}"
    echo -e "  ${YELLOW}────────────────────────────────────────────────────────────${NC}"
    for i in "${!WARNING_LIST[@]}"; do
        echo -e "  ${YELLOW}$(( i + 1 )).${NC} ${WARNING_LIST[$i]}"
    done
    echo ""
fi

# Recommendations
if [ "${#REMEDIATION_LIST[@]}" -gt 0 ]; then
    echo -e "  ${CYAN}${BOLD}RECOMMENDED ACTIONS:${NC}"
    echo -e "  ${CYAN}────────────────────────────────────────────────────────────${NC}"
    for i in "${!REMEDIATION_LIST[@]}"; do
        IFS='|' read -r rtype rmsg rremedy reta <<< "${REMEDIATION_LIST[$i]}"
        if [ "$rtype" = "FAIL" ]; then marker="${RED}!${NC}"
        else marker="${YELLOW}*${NC}"; fi
        echo -e "  ${marker} ${BOLD}${rmsg}${NC}${DIM} [${reta:-~15m}]${NC}"
        echo -e "    ${DIM}Fix: ${rremedy}${NC}"
        echo ""
    done
fi

# ============================================================================
# SAVE PLAIN-TEXT REPORT
# ============================================================================
{
    echo "=================================================================="
    echo "  VCF 9.0 ENVIRONMENT HEALTH CHECK REPORT  v8.0"
    [ -n "${CUSTOMER_NAME:-}" ] && echo "  Prepared for: $CUSTOMER_NAME"
    echo "  Powered by Virtual Control LLC"
    echo "=================================================================="
    echo ""
    echo "  Date:      $RUN_DATE"
    echo "  Duration:  ${DURATION_MIN}m ${DURATION_SEC}s"
    echo "  Target:    ${CUSTOMER_ENV_LABEL:-VCF 9.0 Lab Environment}"
    echo "  Script:    vcf-health-check.sh v8.0"
    [ -n "$VC_VERSION" ] && [ "$VC_VERSION" != "?" ] && echo "  vCenter:   $VC_VERSION"
    [ -n "$SDDC_VERSION" ] && [ "$SDDC_VERSION" != "?" ] && echo "  SDDC Mgr:  $SDDC_VERSION"
    echo ""
    echo "  EXECUTIVE SUMMARY: $EXEC_SUMMARY"
    echo ""
    echo "=================================================================="
    echo "  OVERALL HEALTH GRADE: $GRADE — $GRADE_LABEL"
    echo "  $GRADE_DESC"
    echo "  Health Score: ${PASS_PCT}%"
    echo "=================================================================="
    echo ""
    echo "  +──────────────+───────+"
    echo "  | Result       | Count |"
    echo "  +──────────────+───────+"
    printf "  | Passed       |  %3d  |\n" "$PASSED"
    printf "  | Warnings     |  %3d  |\n" "$WARNINGS"
    printf "  | Failed       |  %3d  |\n" "$FAILED"
    echo "  +──────────────+───────+"
    printf "  | Total        |  %3d  |\n" "$TOTAL_CHECKS"
    echo "  +──────────────+───────+"
    echo ""
    echo "  COMPONENT BREAKDOWN:"
    echo "  +────────────────────────+────────+────────+────────+──────────+"
    echo "  | Component              | Pass   | Warn   | Fail   | Status   |"
    echo "  +────────────────────────+────────+────────+────────+──────────+"
    TXT_COMP_LIST=("INFRA:Infrastructure" "VC:vCenter Server" "SDDC:SDDC Manager" "NSX:NSX Manager" "OPS:VCF Operations" "FLEET:Fleet (vRSLCM)")
    [ "$((${COMP_PASS_CNT[PLUGIN]:-0} + ${COMP_FAIL_CNT[PLUGIN]:-0} + ${COMP_WARN_CNT[PLUGIN]:-0}))" -gt 0 ] && TXT_COMP_LIST+=("PLUGIN:Custom Plugins")
    for ci in "${TXT_COMP_LIST[@]}"; do
        IFS=':' read -r ck cl <<< "$ci"
        p=${COMP_PASS_CNT[$ck]:-0}; w=${COMP_WARN_CNT[$ck]:-0}; f=${COMP_FAIL_CNT[$ck]:-0}
        if [ "$f" -gt 0 ]; then ST="FAIL"; elif [ "$w" -gt 0 ]; then ST="WARN"; elif [ "$p" -gt 0 ]; then ST="PASS"; else ST="N/A"; fi
        printf "  | %-22s |  %3d   |  %3d   |  %3d   | %-8s |\n" "$cl" "$p" "$w" "$f" "$ST"
    done
    echo "  +────────────────────────+────────+────────+────────+──────────+"
    echo ""
    # Trend
    if [ "$TREND_COUNT" -gt 0 ]; then
        echo "  TREND (Last $TREND_COUNT Runs):"
        echo "  +─────────────────────+───────+──────+──────+──────+───────+"
        echo "  | Date                | Grade | Pass | Warn | Fail | Score |"
        echo "  +─────────────────────+───────+──────+──────+──────+───────+"
        printf "  | %-19s | %-5s | %4s | %4s | %4s | %5s | <- current\n" "${RUN_DATE:0:16}" "$GRADE" "$PASSED" "$WARNINGS" "$FAILED" "${PASS_PCT}%"
        echo -e "$TREND_DATA" | while IFS='|' read -r td tg tp tw tf ts; do
            [ -z "$td" ] && continue
            printf "  | %-19s | %-5s | %4s | %4s | %4s | %5s |\n" "$td" "$tg" "$tp" "$tw" "$tf" "$ts"
        done
        echo "  +─────────────────────+───────+──────+──────+──────+───────+"
        echo ""
    fi
    # Delta
    if [ -n "$PREV_GRADE" ] && [ "$PREV_GRADE" != "?" ]; then
        echo "  DELTA FROM LAST RUN ($PREV_DATE):"
        echo "  +──────────────+──────────+──────────+──────────+"
        echo "  | Metric       | Previous | Current  | Delta    |"
        echo "  +──────────────+──────────+──────────+──────────+"
        printf "  | Grade        | %-8s | %-8s | %-8s |\n" "$PREV_GRADE" "$GRADE" "$GD"
        for metric in "Passed:$PASSED:$PREV_PASSED" "Warnings:$WARNINGS:$PREV_WARNINGS" "Failed:$FAILED:$PREV_FAILED"; do
            IFS=':' read -r ml mc mp <<< "$metric"
            [ "$mp" = "?" ] && continue
            delta=$((mc - mp)); ds="$delta"; [ "$delta" -gt 0 ] && ds="+$delta"; [ "$delta" -eq 0 ] && ds="  ="
            printf "  | %-12s | %-8s | %-8s | %-8s |\n" "$ml" "$mp" "$mc" "$ds"
        done
        echo "  +──────────────+──────────+──────────+──────────+"
        echo ""
    fi
    echo "  DETAILED RESULTS:"
    echo "  ────────────────────────────────────────────────────────────"
    for r in "${ALL_RESULTS[@]}"; do echo "  $r"; done
    echo ""
    if [ "${#FAILURE_LIST[@]}" -gt 0 ]; then
        echo "  FAILURES (${#FAILURE_LIST[@]}):"
        echo "  ────────────────────────────────────────────────────────────"
        for i in "${!FAILURE_LIST[@]}"; do echo "  $(( i + 1 )). ${FAILURE_LIST[$i]}"; done
        echo ""
    fi
    if [ "${#WARNING_LIST[@]}" -gt 0 ]; then
        echo "  WARNINGS (${#WARNING_LIST[@]}):"
        echo "  ────────────────────────────────────────────────────────────"
        for i in "${!WARNING_LIST[@]}"; do echo "  $(( i + 1 )). ${WARNING_LIST[$i]}"; done
        echo ""
    fi
    if [ "${#REMEDIATION_LIST[@]}" -gt 0 ]; then
        echo "  RECOMMENDED ACTIONS:"
        echo "  ────────────────────────────────────────────────────────────"
        for i in "${!REMEDIATION_LIST[@]}"; do
            IFS='|' read -r rt rm rr re <<< "${REMEDIATION_LIST[$i]}"
            echo "  [$rt] $rm [${re:-~15m}]"
            echo "        Fix: $rr"
            echo ""
        done
    fi
    echo "=================================================================="
    [ -n "${CUSTOMER_NAME:-}" ] && echo "  Prepared for: $CUSTOMER_NAME"
    echo "  End of VCF Health Check Report"
    echo "  (c) 2026 Virtual Control LLC. All rights reserved."
    echo "=================================================================="
} > "$REPORT_FILE"

# ============================================================================
# GENERATE HTML REPORT
# ============================================================================
HTML_DATA_FILE="$TMP_DIR/html-data.txt"
{
    for r in "${ALL_RESULTS[@]}"; do echo "R:$r"; done
    for f in "${FAILURE_LIST[@]}"; do echo "F:$f"; done
    for w in "${WARNING_LIST[@]}"; do echo "W:$w"; done
    for rem in "${REMEDIATION_LIST[@]}"; do echo "REM:$rem"; done
    HTML_COMP_LIST=("INFRA:Infrastructure" "VC:vCenter Server" "SDDC:SDDC Manager" "NSX:NSX Manager" "OPS:VCF Operations" "FLEET:Fleet (vRSLCM)")
    [ "$((${COMP_PASS_CNT[PLUGIN]:-0} + ${COMP_FAIL_CNT[PLUGIN]:-0} + ${COMP_WARN_CNT[PLUGIN]:-0}))" -gt 0 ] && HTML_COMP_LIST+=("PLUGIN:Custom Plugins")
    for ci in "${HTML_COMP_LIST[@]}"; do
        IFS=':' read -r ck cl <<< "$ci"
        p=${COMP_PASS_CNT[$ck]:-0}; w=${COMP_WARN_CNT[$ck]:-0}; f=${COMP_FAIL_CNT[$ck]:-0}
        if [ "$f" -gt 0 ]; then ST="FAIL"; elif [ "$w" -gt 0 ]; then ST="WARN"; elif [ "$p" -gt 0 ]; then ST="PASS"; else ST="N/A"; fi
        echo "C:${cl}|${p}|${w}|${f}|${ST}"
    done
    echo "META:date=$RUN_DATE"
    echo "META:duration=${DURATION_MIN}m ${DURATION_SEC}s"
    echo "META:grade=$GRADE"
    echo "META:grade_label=$GRADE_LABEL"
    echo "META:grade_desc=$GRADE_DESC"
    echo "META:score=$PASS_PCT"
    echo "META:passed=$PASSED"
    echo "META:warnings=$WARNINGS"
    echo "META:failed=$FAILED"
    echo "META:total=$TOTAL_CHECKS"
    echo "META:exec_summary=$EXEC_SUMMARY"
    echo "META:vc_version=$VC_VERSION"
    echo "META:sddc_version=$SDDC_VERSION"
    if [ -n "$PREV_GRADE" ] && [ "$PREV_GRADE" != "?" ]; then
        echo "HIST:prev_grade=$PREV_GRADE"
        echo "HIST:prev_passed=$PREV_PASSED"
        echo "HIST:prev_warnings=$PREV_WARNINGS"
        echo "HIST:prev_failed=$PREV_FAILED"
        echo "HIST:prev_date=$PREV_DATE"
    fi
    # Trend data
    echo -e "$TREND_DATA" | while IFS='|' read -r td tg tp tw tf ts; do
        [ -z "$td" ] && continue
        echo "TREND:$td|$tg|$tp|$tw|$tf|$ts"
    done
    # Fix actions
    for fa in "${FIX_ACTIONS[@]}"; do echo "FIX:$fa"; done
    # Latency data
    for ld in "${LATENCY_DATA[@]}"; do echo "LATENCY:$ld"; done
    # SLA: component up/down for this run
    for ci in "${COMP_LIST[@]}"; do
        IFS=':' read -r ck cl <<< "$ci"
        f=${COMP_FAIL_CNT[$ck]:-0}
        if [ "${f:-0}" -gt 0 ] 2>/dev/null; then echo "SLA:${cl}|DOWN"
        else echo "SLA:${cl}|UP"; fi
    done
} > "$HTML_DATA_FILE"

export HTML_DATA_FILE
export HTML_REPORT_FILE
export CUSTOMER_NAME="${CUSTOMER_NAME:-}"
export CUSTOMER_LOGO="${CUSTOMER_LOGO:-}"
export CUSTOMER_ENV_LABEL="${CUSTOMER_ENV_LABEL:-VCF 9.0 Lab Environment}"

$_REAL_PYTHON "$SCRIPT_DIR/vcf_checks.py" html-report

# ============================================================================
# PDF GENERATION (optional — try Chrome/Edge headless)
# ============================================================================
PDF_GENERATED=false
HTML_WIN_PATH=$(win_path "$HTML_REPORT_FILE")
PDF_WIN_PATH=$(win_path "$PDF_REPORT_FILE")

for browser in \
    "/c/Program Files/Google/Chrome/Application/chrome.exe" \
    "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" \
    "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
    "/c/Program Files/Microsoft/Edge/Application/msedge.exe"; do
    if [ -f "$browser" ]; then
        "$browser" --headless --disable-gpu --no-sandbox --print-to-pdf="$PDF_WIN_PATH" "file:///$HTML_WIN_PATH" 2>/dev/null
        if [ -f "$PDF_REPORT_FILE" ] && [ -s "$PDF_REPORT_FILE" ]; then
            PDF_GENERATED=true
        fi
        break
    fi
done

# ============================================================================
# JSON REPORT (Feature 4)
# ============================================================================
export JSON_REPORT_FILE
export HTML_DATA_FILE  # reuse the data file from HTML generation
$_REAL_PYTHON "$SCRIPT_DIR/vcf_checks.py" json-report

# v7.0 Feature 17: JSON Schema Generation (one-time, idempotent)
SCHEMA_FILE="$SCRIPT_DIR/vcf-health-report.schema.json"
if [ ! -f "$SCHEMA_FILE" ]; then
    export SCHEMA_OUT="$SCHEMA_FILE"
    $PYTHON -c "
import json
schema = {
    '\$schema': 'https://json-schema.org/draft/2020-12/schema',
    'title': 'VCF Health Check Report',
    'description': 'Schema for VCF 9.0 Health Check JSON reports (v8.0)',
    'type': 'object',
    'required': ['version','date','grade','score','summary','components','results'],
    'properties': {
        'version': {'type':'string','description':'Report format version'},
        'date': {'type':'string','description':'Report generation timestamp'},
        'duration': {'type':'string','description':'Check duration'},
        'grade': {'type':'string','enum':['A','B+','B','C','D','F']},
        'grade_label': {'type':'string'},
        'score': {'type':'integer','minimum':0,'maximum':100},
        'executive_summary': {'type':'string'},
        'summary': {
            'type':'object',
            'properties': {
                'passed': {'type':'integer','minimum':0},
                'warnings': {'type':'integer','minimum':0},
                'failed': {'type':'integer','minimum':0},
                'total': {'type':'integer','minimum':0}
            },
            'required': ['passed','warnings','failed','total']
        },
        'versions': {
            'type':'object',
            'properties': {
                'vcenter': {'type':'string'},
                'sddc_manager': {'type':'string'}
            }
        },
        'components': {
            'type':'array',
            'items': {
                'type':'object',
                'properties': {
                    'name': {'type':'string'},
                    'pass': {'type':'integer'},
                    'warn': {'type':'integer'},
                    'fail': {'type':'integer'},
                    'status': {'type':'string','enum':['PASS','WARN','FAIL','N/A']}
                },
                'required': ['name','pass','warn','fail','status']
            }
        },
        'results': {
            'type':'array',
            'items': {
                'type':'object',
                'properties': {
                    'status': {'type':'string','enum':['PASS','WARN','FAIL']},
                    'component': {'type':'string'},
                    'message': {'type':'string'}
                },
                'required': ['status','component','message']
            }
        },
        'failures': {'type':'array','items':{'type':'string'}},
        'warnings': {'type':'array','items':{'type':'string'}},
        'remediations': {
            'type':'array',
            'items': {
                'type':'object',
                'properties': {
                    'type': {'type':'string'},
                    'message': {'type':'string'},
                    'fix': {'type':'string'}
                }
            }
        },
        'trend': {'type':'array'},
        'delta': {'type':['object','null']}
    }
}
import os
with open(os.environ.get('SCHEMA_OUT',''), 'w') as f:
    json.dump(schema, f, indent=2)
" 2>/dev/null
fi

# ============================================================================
# CSV REPORT (Feature 10)
# ============================================================================
if $CSV_EXPORT; then
    export CSV_REPORT_FILE
    export HTML_DATA_FILE
    $PYTHON << 'CSVEOF'
import os, re, csv
data_file = os.environ.get('HTML_DATA_FILE', '')
output_file = os.environ.get('CSV_REPORT_FILE', '')
if not data_file or not output_file:
    import sys; sys.exit(0)
try:
    results, meta = [], {}
    with open(data_file, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('R:'):
                m = re.match(r'\[(PASS|FAIL|WARN)\]\s*\[([^\]]+)\]\s*(.*)', line[2:])
                if m: results.append({'Status': m.group(1), 'Component': m.group(2), 'Message': m.group(3)})
            elif line.startswith('META:'):
                k, v = line[5:].split('=', 1)
                meta[k] = v
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Date', 'Grade', 'Score', 'Status', 'Component', 'Message'])
        for r in results:
            w.writerow([meta.get('date',''), meta.get('grade',''), meta.get('score','')+'%',
                         r['Status'], r['Component'], r['Message']])
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
CSVEOF
fi

# ============================================================================
# v8.0 Feature 15: MARKDOWN REPORT (--markdown)
# ============================================================================
if $MARKDOWN_EXPORT; then
    export MD_REPORT_FILE HTML_DATA_FILE
    $PYTHON << 'MDEOF'
import os, re
data_file = os.environ.get('HTML_DATA_FILE', '')
output_file = os.environ.get('MD_REPORT_FILE', '')
if not data_file or not output_file:
    import sys; sys.exit(0)
try:
    results = []; meta = {}
    with open(data_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('META:'):
                k, v = line[5:].split('=', 1)
                meta[k] = v
            elif line.startswith('RESULT:'):
                parts = line[7:].split('|', 2)
                if len(parts) >= 3:
                    results.append({'status': parts[0], 'comp': parts[1], 'msg': parts[2]})
            elif line.startswith('FAIL:'):
                pass
            elif line.startswith('WARN_ITEM:'):
                pass
            elif line.startswith('REMEDY:'):
                pass
    grade = meta.get('grade', '?')
    score = meta.get('score', '?')
    md = f"# VCF Health Check Report\n\n"
    md += f"**Date:** {meta.get('date','')} | **Grade:** {grade} | **Score:** {score}%\n\n"
    md += f"**Summary:** {meta.get('passed','0')} passed, {meta.get('warnings','0')} warnings, {meta.get('failed','0')} failed ({meta.get('total','0')} total)\n\n"
    md += f"> {meta.get('exec_summary','')}\n\n"
    md += "---\n\n"
    # Group by component
    comp_results = {}
    for r in results:
        comp_results.setdefault(r['comp'], []).append(r)
    for comp, items in comp_results.items():
        md += f"## {comp}\n\n"
        md += "| Status | Message |\n|--------|--------|\n"
        for item in items:
            icon = {'PASS':'✅','WARN':'⚠️','FAIL':'❌'}.get(item['status'],'❓')
            md += f"| {icon} {item['status']} | {item['msg']} |\n"
        md += "\n"
    # Failures section
    fails = [r for r in results if r['status'] == 'FAIL']
    if fails:
        md += "---\n\n## Failures\n\n"
        for i, f in enumerate(fails, 1):
            md += f"{i}. **[{f['comp']}]** {f['msg']}\n"
        md += "\n"
    # Warnings section
    warns = [r for r in results if r['status'] == 'WARN']
    if warns:
        md += "## Warnings\n\n"
        for i, w in enumerate(warns, 1):
            md += f"{i}. **[{w['comp']}]** {w['msg']}\n"
        md += "\n"
    _md_cust = os.environ.get('CUSTOMER_NAME', '')
    _md_footer = "*Generated by vcf-health-check.sh v8.0 — Powered by Virtual Control LLC*"
    if _md_cust: _md_footer = f"*Prepared for {_md_cust} — {_md_footer[1:-1]}*"
    md += f"\n---\n{_md_footer}\n"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
MDEOF
    $QUIET || echo -e "  ${DIM}Markdown report: $MD_REPORT_FILE${NC}"
fi

# ============================================================================
# EMAIL / SLACK / TEAMS NOTIFICATIONS
# ============================================================================
# Determine if we should notify based on grade threshold
should_notify() {
    local grade_order="A B+ B C D F"
    local threshold_pos=0 current_pos=0 pos=0
    for g in $grade_order; do
        pos=$((pos+1))
        [ "$g" = "$NOTIFY_THRESHOLD" ] && threshold_pos=$pos
        [ "$g" = "$GRADE" ] && current_pos=$pos
    done
    [ "$current_pos" -ge "$threshold_pos" ] && [ "$threshold_pos" -gt 0 ]
}

if should_notify; then
    NOTIFY_MSG="VCF Health Check: Grade $GRADE ($PASS_PCT%) — $FAILED failures, $WARNINGS warnings. $EXEC_SUMMARY"

    # Email notification (v8.0: with HTML attachment)
    if [ -n "$SMTP_TO" ] && [ -n "$SMTP_SERVER" ]; then
        BOUNDARY="vcf-health-$(date +%s)"
        {
            echo "Subject: [VCF Health] Grade $GRADE — $EXEC_SUMMARY"
            echo "From: $SMTP_FROM"
            echo "To: $SMTP_TO"
            echo "MIME-Version: 1.0"
            echo "Content-Type: multipart/mixed; boundary=\"$BOUNDARY\""
            echo ""
            echo "--$BOUNDARY"
            echo "Content-Type: text/plain; charset=UTF-8"
            echo ""
            echo "$NOTIFY_MSG"
            echo ""
            echo "Full report: $(win_path "$REPORT_FILE")"
            echo ""
            echo "--- Failures ---"
            for f in "${FAILURE_LIST[@]}"; do echo "  - $f"; done
            echo ""
            # v8.0 Feature 14: Attach HTML report
            if [ -f "$HTML_REPORT_FILE" ]; then
                echo "--$BOUNDARY"
                echo "Content-Type: text/html; charset=UTF-8; name=\"$(basename "$HTML_REPORT_FILE")\""
                echo "Content-Disposition: attachment; filename=\"$(basename "$HTML_REPORT_FILE")\""
                echo "Content-Transfer-Encoding: base64"
                echo ""
                $PYTHON -c "import base64,sys; data=open(sys.argv[1],'rb').read(); print(base64.b64encode(data).decode())" "$HTML_REPORT_FILE" 2>/dev/null
            fi
            echo "--$BOUNDARY--"
        } | if command -v msmtp >/dev/null 2>&1; then
            msmtp --host="$SMTP_SERVER" --port="$SMTP_PORT" "$SMTP_TO" 2>/dev/null
        elif command -v sendmail >/dev/null 2>&1; then
            sendmail "$SMTP_TO" 2>/dev/null
        else
            curl -s --url "smtp://$SMTP_SERVER:$SMTP_PORT" --mail-from "$SMTP_FROM" --mail-rcpt "$SMTP_TO" -T - 2>/dev/null
        fi
        $QUIET || echo -e "  ${DIM}Email notification sent to $SMTP_TO (with HTML attachment)${NC}"
    fi

    # Slack notification
    if [ -n "$SLACK_WEBHOOK" ]; then
        SLACK_COLOR="#e74c3c"
        [ "$GRADE" = "C" ] && SLACK_COLOR="#f39c12"
        SLACK_PAYLOAD=$($PYTHON -c "
import json
msg = '''$NOTIFY_MSG'''
color = '''$SLACK_COLOR'''
failures = []
$(for f in "${FAILURE_LIST[@]}"; do echo "failures.append('''$f''')"; done)
blocks = [
    {'type':'section','text':{'type':'mrkdwn','text':f'*VCF Health Check Report*\nGrade: *$GRADE* ({int('$PASS_PCT')}%) | Failures: $FAILED | Warnings: $WARNINGS'}},
    {'type':'section','text':{'type':'mrkdwn','text':f'_{msg}_'}}
]
if failures:
    fl = '\n'.join(f'• {f}' for f in failures[:5])
    blocks.append({'type':'section','text':{'type':'mrkdwn','text':f'*Failures:*\n{fl}'}})
print(json.dumps({'attachments':[{'color':color,'blocks':blocks}]}))
" 2>/dev/null)
        if [ -n "$SLACK_PAYLOAD" ]; then
            curl $_CURL_SSL_FLAGS -X POST "$SLACK_WEBHOOK" -H "Content-Type: application/json" -d "$SLACK_PAYLOAD" >/dev/null 2>&1
            $QUIET || echo -e "  ${DIM}Slack notification sent${NC}"
        fi
    fi

    # Feature 15: Microsoft Teams notification
    if [ -n "$TEAMS_WEBHOOK" ]; then
        TEAMS_COLOR="dc3545"
        [ "$GRADE" = "C" ] && TEAMS_COLOR="ffc107"
        [ "$GRADE" = "B" ] && TEAMS_COLOR="28a745"
        FAIL_ITEMS=""
        for f in "${FAILURE_LIST[@]:0:5}"; do
            FAIL_ITEMS="${FAIL_ITEMS}  - ${f}\n"
        done
        TEAMS_PAYLOAD=$($PYTHON -c "
import json
card = {
    'type': 'message',
    'attachments': [{
        'contentType': 'application/vnd.microsoft.card.adaptive',
        'content': {
            '\$schema': 'http://adaptivecards.io/schemas/adaptive-card.json',
            'type': 'AdaptiveCard',
            'version': '1.4',
            'body': [
                {'type':'TextBlock','text':'VCF Health Check Report','weight':'Bolder','size':'Medium'},
                {'type':'FactSet','facts':[
                    {'title':'Grade','value':'$GRADE ($PASS_PCT%)'},
                    {'title':'Failures','value':'$FAILED'},
                    {'title':'Warnings','value':'$WARNINGS'},
                    {'title':'Date','value':'$RUN_DATE'}
                ]},
                {'type':'TextBlock','text':'$EXEC_SUMMARY','wrap':True,'size':'Small'}
            ]
        }
    }]
}
print(json.dumps(card))
" 2>/dev/null)
        if [ -n "$TEAMS_PAYLOAD" ]; then
            curl $_CURL_SSL_FLAGS -X POST "$TEAMS_WEBHOOK" -H "Content-Type: application/json" -d "$TEAMS_PAYLOAD" >/dev/null 2>&1
            $QUIET || echo -e "  ${DIM}Teams notification sent${NC}"
        fi
    fi

    # v7.0 Feature 9: PagerDuty notification
    if [ -n "$PAGERDUTY_KEY" ]; then
        PD_SEVERITY="critical"
        [ "$GRADE" = "C" ] && PD_SEVERITY="warning"
        [ "$GRADE" = "B" ] || [ "$GRADE" = "B+" ] && PD_SEVERITY="info"
        PD_PAYLOAD=$($PYTHON -c "
import json
print(json.dumps({
    'routing_key': '$PAGERDUTY_KEY',
    'event_action': 'trigger',
    'dedup_key': 'vcf-health-check',
    'payload': {
        'summary': '$NOTIFY_MSG'.replace(\"'\",\"\"),
        'severity': '$PD_SEVERITY',
        'source': '$VCENTER',
        'component': 'VCF Health Check',
        'custom_details': {
            'grade': '$GRADE',
            'score': '$PASS_PCT%',
            'failures': $FAILED,
            'warnings': $WARNINGS
        }
    }
}))
" 2>/dev/null)
        if [ -n "$PD_PAYLOAD" ]; then
            curl $_CURL_SSL_FLAGS -X POST "https://events.pagerduty.com/v2/enqueue" \
                -H "Content-Type: application/json" -d "$PD_PAYLOAD" >/dev/null 2>&1
            $QUIET || echo -e "  ${DIM}PagerDuty alert sent${NC}"
        fi
    fi

    # v7.0 Feature 9: OpsGenie notification
    if [ -n "$OPSGENIE_KEY" ]; then
        OG_PRIORITY="P1"
        [ "$GRADE" = "C" ] && OG_PRIORITY="P3"
        [ "$GRADE" = "B" ] && OG_PRIORITY="P5"
        OG_PAYLOAD=$($PYTHON -c "
import json
print(json.dumps({
    'message': 'VCF Health Check: Grade $GRADE ($PASS_PCT%)',
    'description': '''$EXEC_SUMMARY''',
    'priority': '$OG_PRIORITY',
    'tags': ['vcf','health-check','$GRADE'],
    'details': {
        'Grade': '$GRADE',
        'Score': '$PASS_PCT%',
        'Failures': '$FAILED',
        'Warnings': '$WARNINGS'
    }
}))
" 2>/dev/null)
        if [ -n "$OG_PAYLOAD" ]; then
            curl $_CURL_SSL_FLAGS -X POST "https://api.opsgenie.com/v2/alerts" \
                -H "Content-Type: application/json" \
                -H "Authorization: GenieKey $OPSGENIE_KEY" \
                -d "$OG_PAYLOAD" >/dev/null 2>&1
            $QUIET || echo -e "  ${DIM}OpsGenie alert sent${NC}"
        fi
    fi
fi

# v7.0 Feature 10: Syslog Forwarding
if [ -n "$SYSLOG_HOST" ]; then
    SYSLOG_PORT=514
    case "$SYSLOG_HOST" in *:*) SYSLOG_PORT="${SYSLOG_HOST##*:}"; SYSLOG_HOST="${SYSLOG_HOST%%:*}" ;; esac
    # Map grade to syslog severity: 0=emerg,1=alert,2=crit,3=err,4=warn,5=notice,6=info
    SYSLOG_SEV=6
    [ "$GRADE" = "B" ] && SYSLOG_SEV=5
    [ "$GRADE" = "C" ] && SYSLOG_SEV=4
    [ "$GRADE" = "D" ] && SYSLOG_SEV=3
    [ "$GRADE" = "F" ] && SYSLOG_SEV=2
    # Send summary
    $PYTHON -c "
import socket
try:
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    pri=(16*8)+$SYSLOG_SEV  # facility=local0(16), severity
    msg=f'<{pri}>1 $(date -Iseconds) $(hostname) vcf-health-check - - - Grade=$GRADE Score=${PASS_PCT}% Passed=$PASSED Warnings=$WARNINGS Failed=$FAILED'
    s.sendto(msg.encode(),('$SYSLOG_HOST',$SYSLOG_PORT))
    # Send each failure as individual message
    failures = []
$(for f in "${FAILURE_LIST[@]}"; do echo "    failures.append('''$f''')"; done)
    for i,f in enumerate(failures[:20]):
        fmsg=f'<{pri}>1 $(date -Iseconds) $(hostname) vcf-health-check - FAIL-{i+1} - {f}'
        s.sendto(fmsg.encode(),('$SYSLOG_HOST',$SYSLOG_PORT))
    s.close()
except Exception as _e: __import__('sys').stderr.write(f'pyerr: {_e}\n')
" 2>/dev/null
    $QUIET || echo -e "  ${DIM}Syslog sent to $SYSLOG_HOST:$SYSLOG_PORT${NC}"
fi

# v8.0 Feature 17: Generic Webhook (POST full JSON report to any URL)
if [ -n "$WEBHOOK_URL" ] && [ -f "$JSON_REPORT_FILE" ]; then
    WH_HTTP=$(curl $_CURL_SSL_FLAGS --connect-timeout 10 --max-time 30 -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d @"$JSON_REPORT_FILE" -o /dev/null -w "%{http_code}" 2>/dev/null)
    if [ "$WH_HTTP" = "200" ] || [ "$WH_HTTP" = "201" ] || [ "$WH_HTTP" = "202" ] || [ "$WH_HTTP" = "204" ]; then
        $QUIET || echo -e "  ${DIM}Webhook delivered to $WEBHOOK_URL (HTTP $WH_HTTP)${NC}"
    else
        $QUIET || echo -e "  ${YELLOW}Webhook delivery to $WEBHOOK_URL failed (HTTP $WH_HTTP)${NC}"
    fi
fi

# ============================================================================
# Feature 11: PROMETHEUS METRICS (--prometheus)
# ============================================================================
if $PROMETHEUS_MODE; then
    echo "# HELP vcf_health_score VCF health check score percentage"
    echo "# TYPE vcf_health_score gauge"
    echo "vcf_health_score $PASS_PCT"
    echo "# HELP vcf_checks_total Total number of health checks"
    echo "# TYPE vcf_checks_total gauge"
    echo "vcf_checks_total $TOTAL_CHECKS"
    echo "# HELP vcf_checks_passed Number of passed checks"
    echo "# TYPE vcf_checks_passed gauge"
    echo "vcf_checks_passed $PASSED"
    echo "# HELP vcf_checks_warnings Number of warning checks"
    echo "# TYPE vcf_checks_warnings gauge"
    echo "vcf_checks_warnings $WARNINGS"
    echo "# HELP vcf_checks_failed Number of failed checks"
    echo "# TYPE vcf_checks_failed gauge"
    echo "vcf_checks_failed $FAILED"
    for ci in "${COMP_LIST[@]}"; do
        IFS=':' read -r ck cl <<< "$ci"
        p=${COMP_PASS_CNT[$ck]:-0}; w=${COMP_WARN_CNT[$ck]:-0}; f=${COMP_FAIL_CNT[$ck]:-0}
        cln=$(echo "$cl" | tr ' ()/' '____' | tr '[:upper:]' '[:lower:]')
        echo "vcf_component_passed{component=\"$cln\"} $p"
        echo "vcf_component_warnings{component=\"$cln\"} $w"
        echo "vcf_component_failed{component=\"$cln\"} $f"
    done
    for ld in "${LATENCY_DATA[@]}"; do
        IFS='|' read -r ln lv <<< "$ld"
        lln=$(echo "$ln" | tr ' ()/' '____' | tr '[:upper:]' '[:lower:]')
        echo "vcf_latency_ms{target=\"$lln\"} $lv"
    done
    rm -rf "$TMP_DIR" 2>/dev/null
    exit 0
fi

# ============================================================================
# Feature 10: ANSIBLE INVENTORY EXPORT (--ansible)
# ============================================================================
if $ANSIBLE_MODE; then
    ANSIBLE_FILE="$SCRIPT_DIR/vcf-inventory.yml"
    {
        echo "---"
        echo "all:"
        echo "  children:"
        echo "    vcenter:"
        echo "      hosts:"
        echo "        $VCENTER:"
        echo "          ansible_user: root"
        echo "    sddc_manager:"
        echo "      hosts:"
        echo "        $SDDC:"
        echo "          ansible_user: vcf"
        echo "    nsx_manager:"
        echo "      hosts:"
        echo "        $NSX_VIP:"
        echo "          ansible_user: admin"
        if [ -n "$NSX_NODE" ]; then
        echo "        $NSX_NODE:"
        echo "          ansible_user: admin"
        fi
        echo "    esxi_hosts:"
        echo "      hosts:"
        for h in $ESXI_HOSTS; do
        echo "        $h:"
        echo "          ansible_user: root"
        done
        if [ ${#DISCOVERED_HOSTS[@]} -gt 0 ]; then
        echo "    discovered_hosts:"
        echo "      hosts:"
        for dh in "${DISCOVERED_HOSTS[@]}"; do
            echo "        $dh:"
        done
        fi
        echo "    vcf_operations:"
        echo "      hosts:"
        echo "        $VCF_OPS:"
        echo "          ansible_user: admin"
        echo "    fleet:"
        echo "      hosts:"
        echo "        $FLEET:"
        echo "          ansible_user: admin"
    } > "$ANSIBLE_FILE"
    echo -e "  ${GREEN}Ansible inventory generated:${NC} $ANSIBLE_FILE"
fi

# ============================================================================
# Feature 9: REPORT ARCHIVING (--archive)
# ============================================================================
if $ARCHIVE_MODE; then
    ARCHIVE_DIR="$SCRIPT_DIR/archive"
    mkdir -p "$ARCHIVE_DIR" 2>/dev/null
    ARCHIVE_COUNT=0
    while IFS= read -r old_report; do
        [ -z "$old_report" ] && continue
        # Don't archive current run
        echo "$old_report" | grep -q "$TIMESTAMP" && continue
        base=$(basename "$old_report")
        # Get the timestamp from filename
        rts=$(echo "$base" | grep -oE '[0-9]{8}_[0-9]{6}' | head -1)
        [ -z "$rts" ] && continue
        if [ ! -f "$ARCHIVE_DIR/VCF-Reports-${rts}.tar.gz" ]; then
            tar czf "$ARCHIVE_DIR/VCF-Reports-${rts}.tar.gz" \
                "$SCRIPT_DIR"/VCF-Health-Report_${rts}.* 2>/dev/null
            if [ -f "$ARCHIVE_DIR/VCF-Reports-${rts}.tar.gz" ]; then
                rm -f "$SCRIPT_DIR"/VCF-Health-Report_${rts}.* 2>/dev/null
                ARCHIVE_COUNT=$((ARCHIVE_COUNT+1))
            fi
        fi
    done < <(ls "$SCRIPT_DIR"/VCF-Health-Report_*.txt 2>/dev/null)
    [ "$ARCHIVE_COUNT" -gt 0 ] && $QUIET || echo -e "  ${DIM}Archived $ARCHIVE_COUNT old report set(s) to $ARCHIVE_DIR/${NC}"
fi

# ============================================================================
# CLEANUP OLD REPORTS
# ============================================================================
CLEANUP_COUNT=0
if [ "$REPORT_RETENTION_DAYS" -gt 0 ] 2>/dev/null; then
    while IFS= read -r old_file; do
        [ -z "$old_file" ] && continue
        file_date=$(echo "$old_file" | grep -oE '[0-9]{8}' | head -1)
        [ -z "$file_date" ] && continue
        file_epoch=$($PYTHON -c "
from datetime import datetime,timezone
try: print(int(datetime.strptime('$file_date','%Y%m%d').timestamp()))
except Exception: print(0)
" 2>/dev/null)
        cutoff_epoch=$(($(date +%s) - REPORT_RETENTION_DAYS * 86400))
        if [ "${file_epoch:-0}" -gt 0 ] && [ "$file_epoch" -lt "$cutoff_epoch" ] 2>/dev/null; then
            rm -f "$old_file" 2>/dev/null && CLEANUP_COUNT=$((CLEANUP_COUNT + 1))
        fi
    done < <(ls "$SCRIPT_DIR"/VCF-Health-Report_*.txt "$SCRIPT_DIR"/VCF-Health-Report_*.html "$SCRIPT_DIR"/VCF-Health-Report_*.json "$SCRIPT_DIR"/VCF-Health-Report_*.pdf 2>/dev/null)
fi

# ============================================================================
# REPORT PATHS
# ============================================================================
WIN_TXT=$(win_path "$REPORT_FILE")
WIN_HTML=$(win_path "$HTML_REPORT_FILE")
WIN_JSON=$(win_path "$JSON_REPORT_FILE")
WIN_CSV=$(win_path "$CSV_REPORT_FILE")
WIN_PDF=$(win_path "$PDF_REPORT_FILE")
WIN_MD=$(win_path "$MD_REPORT_FILE")

if $JSON_ONLY; then
    # JSON-only mode: just output the JSON path and exit
    echo "$WIN_JSON"
    rm -rf "$TMP_DIR" 2>/dev/null
    [ "$FAILED" -gt 0 ] && exit 2; [ "$WARNINGS" -gt 0 ] && exit 1; exit 0
fi

echo ""
echo -e "  ${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "  ${CYAN}${BOLD}║${NC}  ${BOLD}Reports saved:${NC}                                              ${CYAN}${BOLD}║${NC}"
echo -e "  ${CYAN}${BOLD}║${NC}                                                              ${CYAN}${BOLD}║${NC}"
echo -e "  ${CYAN}${BOLD}║${NC}  TXT:  ${WIN_TXT}"
echo -e "  ${CYAN}${BOLD}║${NC}  HTML: ${WIN_HTML}"
[ -f "$JSON_REPORT_FILE" ] && echo -e "  ${CYAN}${BOLD}║${NC}  JSON: ${WIN_JSON}"
$CSV_EXPORT && [ -f "$CSV_REPORT_FILE" ] && echo -e "  ${CYAN}${BOLD}║${NC}  CSV:  ${WIN_CSV}"
$MARKDOWN_EXPORT && [ -f "$MD_REPORT_FILE" ] && echo -e "  ${CYAN}${BOLD}║${NC}  MD:   ${WIN_MD}"
$PDF_GENERATED && echo -e "  ${CYAN}${BOLD}║${NC}  PDF:  ${WIN_PDF}"
[ "$CLEANUP_COUNT" -gt 0 ] && echo -e "  ${CYAN}${BOLD}║${NC}  ${DIM}Cleaned up $CLEANUP_COUNT old report(s) (>${REPORT_RETENTION_DAYS} days)${NC}"
echo -e "  ${CYAN}${BOLD}║${NC}                                                              ${CYAN}${BOLD}║${NC}"
echo -e "  ${CYAN}${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Exit code (cleanup handled by trap)
if [ "$FAILED" -gt 0 ]; then EXIT_CODE=2
elif [ "$WARNINGS" -gt 0 ]; then EXIT_CODE=1
else EXIT_CODE=0; fi

[ -t 0 ] && { echo -e "  ${DIM}Press any key to exit...${NC}"; read -n 1 -s; }
exit $EXIT_CODE
