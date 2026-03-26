---
title: "Fleet / SDDC Manager Health Check Handbook"
subtitle: "Comprehensive Health Verification for Fleet & SDDC Manager in VCF 9"
author: "Virtual Control LLC"
date: "March 2026"
version: "1.0"
classification: "Internal Use"
css: |-
  body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; color: #1a1a1a; max-width: 100%; line-height: 1.5; }
  h1 { color: #ffffff; background: linear-gradient(135deg, #0b3d6b, #1565c0); padding: 16px 22px; border-radius: 6px; font-size: 22pt; margin-top: 30px; }
  h2 { color: #0b3d6b; border-bottom: 3px solid #1565c0; padding-bottom: 6px; font-size: 15pt; margin-top: 28px; page-break-before: always; }
  h3 { color: #0d47a1; font-size: 12pt; margin-top: 18px; border-left: 4px solid #1565c0; padding-left: 10px; }
  h4 { color: #1565c0; font-size: 10.5pt; margin-top: 14px; }
  table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9pt; }
  th { background-color: #0b3d6b; color: white; padding: 7px 10px; text-align: left; }
  td { border: 1px solid #cfd8dc; padding: 6px 10px; }
  tr:nth-child(even) { background-color: #e3f2fd; }
  code { background-color: #e3f2fd; padding: 2px 5px; border-radius: 3px; font-size: 9pt; font-family: 'Cascadia Code', Consolas, monospace; color: #0b3d6b; }
  pre { background-color: #f5f5f5; padding: 12px; border-radius: 5px; border-left: 4px solid #1565c0; font-size: 9pt; line-height: 1.4; overflow-x: auto; }
  pre code { background: none; padding: 0; color: #1a1a1a; }
  a { color: #1565c0; text-decoration: none; }
  a:hover { text-decoration: underline; }
  blockquote { border-left: 4px solid #f39c12; background: #fef9e7; padding: 10px 14px; margin: 10px 0; font-size: 9pt; }
  .toc { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px 30px; margin: 20px 0; }
  .toc ul { list-style: none; padding-left: 0; }
  .toc > ul > li { margin-bottom: 6px; }
  .toc > ul > li > a { font-weight: bold; font-size: 11pt; color: #0b3d6b; }
  .toc ul ul { padding-left: 22px; margin-top: 3px; }
  .toc ul ul li { margin-bottom: 2px; }
  .toc ul ul li a { font-size: 9.5pt; color: #333; }
  .info-box { background: #e3f2fd; border-left: 4px solid #1565c0; padding: 12px 16px; border-radius: 4px; margin: 12px 0; font-size: 9.5pt; }
  .warn-box { background: #fff3e0; border-left: 4px solid #f57c00; padding: 12px 16px; border-radius: 4px; margin: 12px 0; font-size: 9.5pt; }
  .fix-box { background: #e8f5e9; border-left: 4px solid #43a047; padding: 12px 16px; border-radius: 4px; margin: 12px 0; font-size: 9.5pt; }
  .danger { background: #ffebee; border-left: 4px solid #e53935; padding: 12px 16px; border-radius: 4px; margin: 12px 0; font-size: 9.5pt; }
  .badge-pass { background: #43a047; color: white; padding: 2px 8px; border-radius: 12px; font-size: 8pt; font-weight: bold; }
  .badge-warn { background: #f57c00; color: white; padding: 2px 8px; border-radius: 12px; font-size: 8pt; font-weight: bold; }
  .badge-fail { background: #e53935; color: white; padding: 2px 8px; border-radius: 12px; font-size: 8pt; font-weight: bold; }
  .cover-page { text-align: center; padding: 80px 20px; page-break-after: always; }
  .cover-page h1 { font-size: 28pt; background: linear-gradient(135deg, #0b3d6b, #1565c0); padding: 30px; border-radius: 10px; }
  .cover-page .subtitle { font-size: 14pt; color: #1565c0; margin-top: 20px; }
  .cover-page .meta { font-size: 10pt; color: #666; margin-top: 40px; line-height: 2; }
  .page-break { page-break-before: always; }
pdf_options:
  format: Letter
  margin: 18mm 15mm 18mm 15mm
  headerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">Fleet / SDDC Manager Health Check Handbook &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  footerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">Page <span class="pageNumber"></span> of <span class="totalPages"></span> &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  displayHeaderFooter: true
---

<div class="cover-page">

# Fleet / SDDC Manager Health Check Handbook

<div class="subtitle">Comprehensive Health Verification for Fleet & SDDC Manager in VCF 9</div>

<div class="meta">

**Author:** Virtual Control LLC
**Date:** March 2026
**Version:** 1.0
**Classification:** Internal Use
**Platform:** VMware Cloud Foundation 9.0 / SDDC Manager 5.2.x

</div>
</div>


<div class="toc">

## Table of Contents

<ul>
<li><a href="#overview">1. Overview &amp; Purpose</a></li>
<li><a href="#prerequisites">2. Prerequisites</a></li>
<li><a href="#quick-reference">3. Quick Reference &mdash; All Checks Summary</a></li>
<li><a href="#service-status">4. Service Status</a>
  <ul>
  <li><a href="#svc-systemctl">4.1 All Services via systemctl</a></li>
  <li><a href="#svc-script">4.2 VCF Service Status Script</a></li>
  <li><a href="#svc-critical">4.3 Critical vs Non-Critical Services</a></li>
  </ul>
</li>
<li><a href="#database">5. Database Health</a>
  <ul>
  <li><a href="#db-postgres">5.1 PostgreSQL Status</a></li>
  <li><a href="#db-size">5.2 Database Size &amp; Connections</a></li>
  <li><a href="#db-vacuum">5.3 Vacuum Status</a></li>
  <li><a href="#db-backup">5.4 Database Backup</a></li>
  </ul>
</li>
<li><a href="#inventory">6. Component Inventory</a>
  <ul>
  <li><a href="#inv-components">6.1 System Components</a></li>
  <li><a href="#inv-domains">6.2 Workload Domains</a></li>
  <li><a href="#inv-hosts">6.3 Host Inventory</a></li>
  </ul>
</li>
<li><a href="#lifecycle">7. Lifecycle Management (LCM)</a>
  <ul>
  <li><a href="#lcm-version">7.1 Current Version</a></li>
  <li><a href="#lcm-updates">7.2 Available Updates</a></li>
  <li><a href="#lcm-prechecks">7.3 Upgrade Prechecks</a></li>
  </ul>
</li>
<li><a href="#bundles">8. Bundle Management</a></li>
<li><a href="#dns-ntp">9. DNS &amp; NTP Verification</a></li>
<li><a href="#certificates">10. Certificate Health</a></li>
<li><a href="#tasks">11. Task &amp; Workflow History</a></li>
<li><a href="#commissioning">12. Host Commissioning Status</a></li>
<li><a href="#domains">13. Workload Domain Health</a></li>
<li><a href="#backup">14. Backup &amp; Restore</a></li>
<li><a href="#api-health">15. API Health Verification</a></li>
<li><a href="#resources">16. Resource Utilization</a></li>
<li><a href="#ports">17. Port Reference Table</a></li>
<li><a href="#common-issues">18. Common Issues &amp; Remediation</a></li>
<li><a href="#cli-reference">19. CLI Quick Reference Card</a></li>
<li><a href="#api-reference">20. API Quick Reference</a></li>
</ul>

</div>


## <span id="overview"></span>1. Overview & Purpose

This handbook provides a **complete health check procedure** for the SDDC Manager (Fleet Manager) in a VCF 9.0 environment. SDDC Manager is the **central orchestration and lifecycle management** component of VCF. Its health directly affects your ability to:

- Deploy and manage workload domains
- Perform lifecycle updates (patches, upgrades)
- Commission/decommission ESXi hosts
- Manage certificates across all VCF components
- Monitor component inventory and compliance

### When to Run This Health Check

| Trigger | Priority |
|---------|----------|
| Before any LCM operation (upgrade/patch) | **Critical** |
| After any LCM operation | **Critical** |
| Weekly routine maintenance | **Recommended** |
| After infrastructure changes | **Recommended** |
| When tasks are failing/stuck | **Troubleshooting** |

<div class="info-box">
<strong>Environment Variables:</strong> Throughout this document:<br>
<code>$SDDC</code> = SDDC Manager FQDN (e.g., sddc-manager.lab.local)<br>
<code>$SDDC_USER</code> = admin@local (or SSO admin)<br>
<code>$SDDC_PASS</code> = SDDC Manager password<br>
<code>$TOKEN</code> = Bearer token acquired via API
</div>



## <span id="prerequisites"></span>2. Prerequisites

### Required Access

| Access Type | Target | Credentials |
|-------------|--------|-------------|
| HTTPS (443) | SDDC Manager | admin@local or administrator@vsphere.local |
| SSH (22) | SDDC Manager appliance | vcf / password |
| SSH (22) | SDDC Manager appliance | root / password |
| REST API | SDDC Manager :443 | Bearer token |

### Token Acquisition

```bash
export SDDC="sddc-manager.lab.local"
export SDDC_USER="admin@local"
export SDDC_PASS="YourPassword123!"

# Acquire access token
TOKEN=$(curl -sk -X POST "https://$SDDC/v1/tokens" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$SDDC_USER\",\"password\":\"$SDDC_PASS\"}" | jq -r '.accessToken')

echo "Token: ${TOKEN:0:20}..."

# Convenience function
sddc_api() {
  curl -sk -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "https://$SDDC$1" 2>/dev/null
}
```

<div class="warn-box">
<strong>Token Expiry:</strong> SDDC Manager tokens expire after 30 minutes. Re-acquire if you get 401 responses.
</div>



## <span id="quick-reference"></span>3. Quick Reference — All Checks Summary

| # | Check | Method | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|---|-------|--------|------|------|------|
| 4.1 | Service Status | SSH/systemctl | All services active | Non-critical stopped | Critical service down |
| 5.1 | PostgreSQL | SSH | Running, accepting connections | High connection count | Not running |
| 5.2 | DB Size | SQL | < 5 GB | 5-10 GB | > 10 GB |
| 6.1 | Component Inventory | API | All components `ACTIVE` | Any `WARNING` | Any `ERROR` |
| 7.1 | Current Version | API | Latest VCF version | 1 version behind | 2+ versions behind |
| 8 | Bundles | API | Bundles available | Download in progress | Download failed |
| 9 | DNS/NTP | API/CLI | All resolving, time sync | Intermittent DNS | DNS failure or NTP > 5s |
| 10 | Certificates | API | All > 30 days | Any 7-30 days | Any < 7 days or expired |
| 11 | Tasks | API | No failed tasks | Old failed tasks | Recent critical failures |
| 12 | Hosts | API | All `ASSIGNED` or `UNASSIGNED_USEABLE` | Any `COMMISSIONING` | Any `ERROR` |
| 13 | Domains | API | All `ACTIVE` | Any `ACTIVATING` | Any `ERROR` |
| 14 | Backup | API/SSH | Configured, recent success | > 24h since last | Not configured |
| 15 | API Health | API | Token acquired, < 2s response | 2-5s response | API unresponsive |
| 16 | Resources | SSH | CPU < 70%, Mem < 80%, Disk < 70% | CPU/Mem/Disk warn | Any critical |



## <span id="service-status"></span>4. Service Status

### <span id="svc-systemctl"></span>4.1 All Services via systemctl

**What:** Verify all SDDC Manager services are running.

```bash
ssh vcf@$SDDC
# Then switch to root or use sudo:
sudo systemctl list-units --type=service --state=running | grep -E "vcf|sddc|operationsd|commonsvcs|domainmanager|lcm"
```

**Expected Output:**

```
  commonsvcs.service               loaded active running   VCF Common Services
  domainmanager.service            loaded active running   VCF Domain Manager
  lcm.service                      loaded active running   VCF Lifecycle Manager
  operationsd.service              loaded active running   VCF Operations
  sddc-manager-ui-app.service      loaded active running   SDDC Manager UI
  sddc-support.service             loaded active running   VCF Support Service
```

### <span id="svc-script"></span>4.2 VCF Service Status Script

```bash
# Comprehensive service check
for SVC in commonsvcs domainmanager lcm operationsd sddc-manager-ui-app sddc-support; do
  STATUS=$(systemctl is-active $SVC 2>/dev/null)
  if [ "$STATUS" = "active" ]; then
    echo "[PASS] $SVC: $STATUS"
  else
    echo "[FAIL] $SVC: $STATUS"
  fi
done
```

### <span id="svc-critical"></span>4.3 Critical vs Non-Critical Services

| Service | Critical | Function | Impact if Down |
|---------|----------|----------|----------------|
| `commonsvcs` | **Yes** | Shared services (auth, config) | All SDDC Manager functions fail |
| `domainmanager` | **Yes** | Domain operations | Cannot create/modify workload domains |
| `lcm` | **Yes** | Lifecycle management | Cannot patch/upgrade |
| `operationsd` | **Yes** | Task orchestration | No task execution |
| `sddc-manager-ui-app` | No | Web UI | UI unavailable (API still works) |
| `sddc-support` | No | Support bundle | Cannot generate support bundles |
| `postgresql` | **Yes** | Database | Complete SDDC Manager failure |
| `nginx` | **Yes** | Reverse proxy / API gateway | API and UI unreachable |

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All services `active` | Healthy |
| <span class="badge-warn">WARN</span> | Non-critical service stopped | Limited functionality |
| <span class="badge-fail">FAIL</span> | Any critical service not `active` | SDDC Manager degraded/down |

<div class="fix-box">
<strong>Remediation:</strong><br>
1. Restart specific service: <code>sudo systemctl restart &lt;service-name&gt;</code><br>
2. Restart all VCF services: <code>sudo systemctl restart commonsvcs domainmanager lcm operationsd</code><br>
3. Check logs: <code>journalctl -u &lt;service-name&gt; --since "1 hour ago"</code><br>
4. Full service restart: <code>sudo /opt/vmware/vcf/operationsmanager/scripts/cli/vcf-service-status.sh</code>
</div>



## <span id="database"></span>5. Database Health

### <span id="db-postgres"></span>5.1 PostgreSQL Status

```bash
ssh root@$SDDC
systemctl status postgresql
```

**Expected Output:**

```
● postgresql.service - PostgreSQL database server
     Loaded: loaded (/usr/lib/systemd/system/postgresql.service; enabled)
     Active: active (running) since Mon 2026-03-20 08:00:00 UTC; 6 days ago
   Main PID: 1234 (postgres)
     Memory: 256.0M
```

#### Connection Test

```bash
sudo -u postgres psql -c "SELECT version();"
```

**Expected Output:**

```
                                  version
---------------------------------------------------------------------------
 PostgreSQL 14.x on x86_64-pc-linux-gnu, compiled by gcc ...
(1 row)
```

### <span id="db-size"></span>5.2 Database Size & Connections

```bash
# Database size
sudo -u postgres psql -c "
SELECT datname, pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database WHERE datname NOT IN ('template0','template1','postgres')
ORDER BY pg_database_size(datname) DESC;"
```

**Expected Output:**

```
    datname     |  size
-----------------+---------
 sddc_manager_db | 2.1 GB
 lcm_db          | 512 MB
 operations_db   | 256 MB
```

```bash
# Active connections
sudo -u postgres psql -c "
SELECT datname, count(*) as connections
FROM pg_stat_activity
GROUP BY datname ORDER BY connections DESC;"
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | DB size < 5 GB, connections < 100 | Healthy |
| <span class="badge-warn">WARN</span> | DB size 5-10 GB or connections 100-200 | Monitor |
| <span class="badge-fail">FAIL</span> | DB size > 10 GB or connections > 200 | Investigate bloat |

### <span id="db-vacuum"></span>5.3 Vacuum Status

```bash
sudo -u postgres psql -d sddc_manager_db -c "
SELECT schemaname, relname, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC LIMIT 10;"
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. Manual vacuum: <code>sudo -u postgres vacuumdb --all --analyze</code><br>
2. If bloated: <code>sudo -u postgres vacuumdb --full --all</code> (requires downtime)<br>
3. Check autovacuum: <code>SHOW autovacuum;</code> should return <code>on</code>
</div>

### <span id="db-backup"></span>5.4 Database Backup

```bash
# Check if database backups exist
ls -la /opt/vmware/vcf/sddc-manager/backup/ 2>/dev/null
ls -la /nfs-mount/vcf-backups/ 2>/dev/null
```



## <span id="inventory"></span>6. Component Inventory

### <span id="inv-components"></span>6.1 System Components

**What:** Verify all VCF-managed components are in a healthy state.

```bash
# List all VCF components
sddc_api "/v1/system" | jq .
```

#### Get all vCenters

```bash
sddc_api "/v1/vcenter" | jq '.elements[] | {
  id: .id,
  fqdn: .fqdn,
  version: .version,
  status: .status
}'
```

#### Get all NSX Managers

```bash
sddc_api "/v1/nsxt-clusters" | jq '.elements[] | {
  id: .id,
  vipFqdn: .vipFqdn,
  version: .version
}'
```

### <span id="inv-domains"></span>6.2 Workload Domains

```bash
sddc_api "/v1/domains" | jq '.elements[] | {
  id: .id,
  name: .name,
  type: .type,
  status: .status
}'
```

**Expected Output:**

```json
{
  "id": "abc123...",
  "name": "MGMT",
  "type": "MANAGEMENT",
  "status": "ACTIVE"
}
{
  "id": "def456...",
  "name": "WLD-01",
  "type": "VI",
  "status": "ACTIVE"
}
```

### <span id="inv-hosts"></span>6.3 Host Inventory

```bash
sddc_api "/v1/hosts" | jq '.elements[] | {
  id: .id,
  fqdn: .fqdn,
  status: .status,
  domain: .domain.name
}'
```

| Status | Meaning |
|--------|---------|
| `ASSIGNED` | Host is part of a workload domain |
| `UNASSIGNED_USEABLE` | Commissioned, available for assignment |
| `COMMISSIONING` | Being added to inventory |
| `DECOMMISSIONING` | Being removed |
| `ERROR` | Host in error state |



## <span id="lifecycle"></span>7. Lifecycle Management (LCM)

### <span id="lcm-version"></span>7.1 Current Version

```bash
# SDDC Manager version
sddc_api "/v1/system" | jq '{
  version: .version,
  build: .build,
  fips_enabled: .fipsEnabled
}'
```

### <span id="lcm-updates"></span>7.2 Available Updates

```bash
# Check available updates
sddc_api "/v1/system/prechecks" | jq .
```

#### Bundle Availability

```bash
sddc_api "/v1/bundles" | jq '.elements[] | {
  id: .id,
  bundleType: .bundleType,
  version: .version,
  status: .downloadStatus,
  components: [.components[].type]
}'
```

### <span id="lcm-prechecks"></span>7.3 Upgrade Prechecks

```bash
# Trigger precheck
curl -sk -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://$SDDC/v1/system/prechecks" \
  -d '{"bundleId":"<bundle-id>"}'

# Check precheck results
sddc_api "/v1/system/prechecks/<precheck-id>" | jq '.results[] | {
  check: .description,
  status: .status,
  severity: .severity,
  resolution: .resolution
}'
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All prechecks pass | Ready to upgrade |
| <span class="badge-warn">WARN</span> | Warning-level prechecks | Review before proceeding |
| <span class="badge-fail">FAIL</span> | Any critical precheck failure | Must resolve before upgrade |



## <span id="bundles"></span>8. Bundle Management

```bash
# List all bundles
sddc_api "/v1/bundles" | jq '.elements[] | {
  id: .id,
  type: .bundleType,
  version: .version,
  downloadStatus: .downloadStatus,
  applicableVersions: .applicableVersions
}'
```

**Download Statuses:**

| Status | Meaning |
|--------|---------|
| `SUCCESSFUL` | Bundle downloaded successfully |
| `IN_PROGRESS` | Currently downloading |
| `FAILED` | Download failed |
| `NOT_STARTED` | Available but not downloaded |

#### Check Depot Connectivity

```bash
# Test connectivity to VMware depot (online mode)
ssh vcf@$SDDC
curl -sk https://depot.vmware.com/PROD2/vcf/manifest.json | head -5
```

<div class="info-box">
<strong>Offline Depot:</strong> If using an offline depot, verify the depot server is reachable and the depot path is configured correctly in SDDC Manager → Administration → Depot Settings.
</div>


## <span id="dns-ntp"></span>9. DNS & NTP Verification

### DNS Configuration

```bash
# Get DNS config via API
sddc_api "/v1/system/dns-configuration" | jq .
```

**Expected Output:**

```json
{
  "dnsServers": [
    {"ipAddress": "192.168.1.1", "isPrimary": true},
    {"ipAddress": "192.168.1.2", "isPrimary": false}
  ]
}
```

#### DNS Resolution Test

```bash
ssh vcf@$SDDC
# Test forward resolution for all VCF components
for HOST in vcenter.lab.local nsx-vip.lab.local sddc-manager.lab.local; do
  echo "$HOST: $(nslookup $HOST | grep Address | tail -1)"
done

# Test reverse resolution
for IP in 192.168.1.70 192.168.1.71 192.168.1.60; do
  echo "$IP: $(nslookup $IP | grep name | head -1)"
done
```

### NTP Configuration

```bash
# Get NTP config
sddc_api "/v1/system/ntp-configuration" | jq .

# Check time sync on appliance
ssh vcf@$SDDC
timedatectl status
chronyc tracking
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | DNS resolves all components, NTP synced < 1s | Healthy |
| <span class="badge-warn">WARN</span> | Slow DNS or NTP drift 1-5s | Monitor |
| <span class="badge-fail">FAIL</span> | DNS failure or NTP not synced | LCM operations will fail |



## <span id="certificates"></span>10. Certificate Health

```bash
# List all certificates managed by VCF
sddc_api "/v1/certificate-authorities" | jq .

# Get certificates for a specific resource
sddc_api "/v1/domains/<domain-id>/resource-certificates" | jq '.elements[] | {
  resource: .resourceFqdn,
  type: .certificateType,
  expiresAt: .expirationDate,
  issuedBy: .issuedBy
}'
```

#### Check Certificate Expiry via OpenSSL

```bash
# Check SDDC Manager certificate
echo | openssl s_client -connect $SDDC:443 2>/dev/null | \
  openssl x509 -noout -dates -subject
```

#### CSR Status

```bash
sddc_api "/v1/certificate-authorities/csr" | jq .
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All certificates > 30 days from expiry | Healthy |
| <span class="badge-warn">WARN</span> | Any certificate 7-30 days from expiry | Plan renewal |
| <span class="badge-fail">FAIL</span> | Any certificate < 7 days or expired | Immediate action |

<div class="danger">
<strong>Certificate Expiry Impact:</strong> Expired SDDC Manager certificates will prevent:<br>
- API access (token acquisition fails)<br>
- LCM operations<br>
- Communication with vCenter, NSX, ESXi<br>
<strong>Action:</strong> Use Certificate Manager or API to replace certificates before expiry.
</div>


## <span id="tasks"></span>11. Task & Workflow History

```bash
# List recent tasks (last 20)
sddc_api "/v1/tasks?limit=20" | jq '.elements[] | {
  id: .id,
  name: .name,
  status: .status,
  type: .type,
  creationTimestamp: .creationTimestamp,
  completionTimestamp: .completionTimestamp
}'
```

**Task Statuses:**

| Status | Meaning |
|--------|---------|
| `SUCCESSFUL` | Completed successfully |
| `FAILED` | Failed — check subtasks for details |
| `IN_PROGRESS` | Currently executing |
| `CANCELLED` | Cancelled by user |

#### Check for Failed Tasks

```bash
sddc_api "/v1/tasks?status=FAILED&limit=10" | jq '.elements[] | {
  id: .id,
  name: .name,
  creationTimestamp: .creationTimestamp,
  errorMessage: .errors
}'
```

#### Retry a Failed Task

```bash
curl -sk -X PATCH -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://$SDDC/v1/tasks/<task-id>" \
  -d '{"status":"IN_PROGRESS"}'
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | No failed tasks in last 7 days | Clean |
| <span class="badge-warn">WARN</span> | Older failed tasks present | Review and clean up |
| <span class="badge-fail">FAIL</span> | Recent critical task failures | Investigate immediately |



## <span id="commissioning"></span>12. Host Commissioning Status

```bash
# All hosts with their status
sddc_api "/v1/hosts" | jq '.elements[] | {
  fqdn: .fqdn,
  status: .status,
  domain: .domain.name,
  clusterId: .cluster.id
}'

# Count by status
sddc_api "/v1/hosts" | jq '[.elements[] | .status] | group_by(.) | map({status: .[0], count: length})'
```

<div class="fix-box">
<strong>Remediation for stuck COMMISSIONING:</strong><br>
1. Check task status: <code>sddc_api "/v1/tasks?type=HOST_COMMISSION"</code><br>
2. Verify host SSH access and credentials<br>
3. Check DNS resolution for the host<br>
4. Retry: Cancel and recommission
</div>


## <span id="domains"></span>13. Workload Domain Health

```bash
# List all domains with health
sddc_api "/v1/domains" | jq '.elements[] | {
  name: .name,
  type: .type,
  status: .status,
  clusters: [.clusters[].name]
}'
```

#### Cluster Health per Domain

```bash
# List clusters
sddc_api "/v1/clusters" | jq '.elements[] | {
  name: .name,
  status: .status,
  domain: .domainName,
  hostCount: (.hosts | length),
  primaryDatastore: .primaryDatastoreType
}'
```


## <span id="backup"></span>14. Backup & Restore

```bash
# Get backup configuration
sddc_api "/v1/system/backup-configuration" | jq .
```

**Expected Output:**

```json
{
  "backupEnabled": true,
  "backupSchedule": {
    "frequency": "DAILY",
    "daysOfWeek": null,
    "hourOfDay": 2,
    "minuteOfHour": 0
  },
  "server": {
    "protocol": "SFTP",
    "host": "backup-server.lab.local",
    "port": 22,
    "directory": "/backups/sddc/"
  },
  "encryption": {
    "passphrase": "***"
  }
}
```

#### Check Backup History

```bash
sddc_api "/v1/system/backup-configuration/backups" | jq '.elements[0:3]'
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | Backup configured, last success < 24h | Protected |
| <span class="badge-warn">WARN</span> | Backup configured, last success > 24h | Check schedule |
| <span class="badge-fail">FAIL</span> | No backup configured or all recent failed | Critical risk |



## <span id="api-health"></span>15. API Health Verification

### Token Acquisition Test

```bash
# Time the token acquisition
time curl -sk -X POST "https://$SDDC/v1/tokens" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$SDDC_USER\",\"password\":\"$SDDC_PASS\"}" | jq -r '.accessToken' > /dev/null
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | Token acquired in < 2 seconds | API responsive |
| <span class="badge-warn">WARN</span> | Token acquired in 2-5 seconds | API slow |
| <span class="badge-fail">FAIL</span> | Token acquisition fails or > 5 seconds | API issue |

### Endpoint Health Check Script

```bash
ENDPOINTS="/v1/system /v1/domains /v1/hosts /v1/clusters /v1/bundles"
for EP in $ENDPOINTS; do
  START=$(date +%s%N)
  HTTP_CODE=$(curl -sk -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "https://$SDDC$EP")
  END=$(date +%s%N)
  DURATION=$(( (END - START) / 1000000 ))
  echo "$EP: HTTP $HTTP_CODE (${DURATION}ms)"
done
```


## <span id="resources"></span>16. Resource Utilization

```bash
ssh root@$SDDC

# CPU
uptime
top -b -n 1 | head -5

# Memory
free -m

# Disk
df -h
```

#### Critical Partitions

| Partition | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|-----------|------|------|------|
| `/` (root) | < 70% | 70-85% | > 85% |
| `/var/log` | < 70% | 70-85% | > 85% |
| `/opt` | < 70% | 70-85% | > 85% |
| DB partition | < 70% | 70-85% | > 85% |

<div class="fix-box">
<strong>Remediation:</strong><br>
1. Clean old logs: <code>find /var/log -name "*.gz" -mtime +30 -delete</code><br>
2. Clean old task data: <code>sddc_api "/v1/tasks?status=SUCCESSFUL" | jq '.elements | length'</code><br>
3. Check large files: <code>du -sh /var/log/* | sort -rh | head -10</code>
</div>



## <span id="ports"></span>17. Port Reference Table

### Inbound Ports

| Source | Port | Protocol | Purpose |
|--------|------|----------|---------|
| Admin Browser | 443 | TCP | Web UI / REST API |
| Admin | 22 | TCP | SSH |
| vCenter | 443 | TCP | Inventory sync |
| NSX Manager | 443 | TCP | Component registration |
| ESXi Hosts | 443 | TCP | Host commissioning |

### Outbound Ports

| Destination | Port | Protocol | Purpose |
|-------------|------|----------|---------|
| vCenter | 443 | TCP | vCenter management |
| NSX Manager | 443 | TCP | NSX lifecycle |
| ESXi Hosts | 443 | TCP | Host preparation |
| ESXi Hosts | 22 | TCP | Host configuration (SSH) |
| DNS Server | 53 | TCP/UDP | Name resolution |
| NTP Server | 123 | UDP | Time synchronization |
| SFTP Backup | 22 | TCP | Backup transfer |
| VMware Depot | 443 | TCP | Bundle downloads (online) |
| Offline Depot | 443 | TCP | Bundle downloads (offline) |
| PostgreSQL (local) | 5432 | TCP | Database (localhost) |



## <span id="common-issues"></span>18. Common Issues & Remediation

### 18.1 Service Failures

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| UI inaccessible | nginx or UI service down | `systemctl restart nginx sddc-manager-ui-app` |
| API returns 503 | Backend services down | `systemctl restart commonsvcs domainmanager lcm operationsd` |
| Slow API responses | Database issue or resource exhaustion | Check DB connections and disk space |

### 18.2 Database Issues

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Connection refused | PostgreSQL not running | `systemctl restart postgresql` |
| Slow queries | Table bloat / missing vacuum | `vacuumdb --all --analyze` |
| Disk full (DB) | Large transaction logs | Clean WAL files, increase disk |

### 18.3 LCM Failures

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Precheck fails | Component version mismatch | Review precheck report, resolve each item |
| Bundle download fails | Network/proxy issue | Check depot connectivity, proxy settings |
| Upgrade stuck | Task hung | Check subtasks, cancel and retry |

### 18.4 Task Stuck in IN_PROGRESS

```bash
# Find stuck tasks (running > 2 hours)
sddc_api "/v1/tasks?status=IN_PROGRESS" | jq '.elements[] | {
  id: .id,
  name: .name,
  creationTimestamp: .creationTimestamp
}'
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. Check subtask status for the stuck task<br>
2. If safe to cancel: <code>PATCH /v1/tasks/&lt;id&gt;</code> with <code>{"status":"CANCELLED"}</code><br>
3. Restart VCF services: <code>systemctl restart commonsvcs domainmanager lcm operationsd</code><br>
4. Check for locks: <code>sddc_api "/v1/tasks?type=LOCK" | jq .</code>
</div>

### 18.5 Certificate Problems

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| 401 on all API calls | SDDC Manager cert expired | Replace via Certificate Manager |
| LCM fails with cert error | Component cert expired | Replace component certificates first |
| Trust verification fails | CA not in trust store | Add CA to SDDC Manager trust store |



## <span id="cli-reference"></span>19. CLI Quick Reference Card

### Service Management

| Command | Purpose |
|---------|---------|
| `systemctl status commonsvcs` | Common services status |
| `systemctl status domainmanager` | Domain manager status |
| `systemctl status lcm` | Lifecycle manager status |
| `systemctl status operationsd` | Operations daemon status |
| `systemctl status postgresql` | Database status |
| `systemctl status nginx` | Web server / proxy status |
| `systemctl restart <service>` | Restart a service |

### Database Commands

| Command | Purpose |
|---------|---------|
| `sudo -u postgres psql` | Enter PostgreSQL shell |
| `sudo -u postgres psql -c "SELECT version();"` | Check DB version |
| `sudo -u postgres psql -l` | List databases |
| `sudo -u postgres vacuumdb --all --analyze` | Vacuum all databases |

### System Commands

| Command | Purpose |
|---------|---------|
| `df -h` | Disk usage |
| `free -m` | Memory usage |
| `uptime` | Load average |
| `timedatectl` | Time sync status |
| `chronyc tracking` | NTP tracking details |
| `cat /etc/vmware/vcf/sddc-manager-version` | SDDC Manager version |
| `nslookup <hostname>` | DNS test |
| `openssl s_client -connect <host>:443` | Certificate check |

### Log Files

| Log File | Purpose |
|----------|---------|
| `/var/log/vmware/vcf/commonsvcs/commonsvcs.log` | Common services |
| `/var/log/vmware/vcf/domainmanager/domainmanager.log` | Domain manager |
| `/var/log/vmware/vcf/lcm/lcm.log` | Lifecycle manager |
| `/var/log/vmware/vcf/operationsmanager/operationsmanager.log` | Operations |
| `/var/log/vmware/vcf/sddc-support/sddc-support.log` | Support service |
| `/var/log/nginx/access.log` | Nginx access log |
| `/var/log/nginx/error.log` | Nginx error log |



## <span id="api-reference"></span>20. API Quick Reference

### Authentication

```bash
# Acquire token
curl -sk -X POST "https://$SDDC/v1/tokens" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@local","password":"password"}'

# Use token
curl -sk -H "Authorization: Bearer $TOKEN" "https://$SDDC/v1/..."
```

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/tokens` | POST | Acquire access token |
| `/v1/system` | GET | System info / version |
| `/v1/system/dns-configuration` | GET | DNS config |
| `/v1/system/ntp-configuration` | GET | NTP config |
| `/v1/system/backup-configuration` | GET | Backup config |
| `/v1/system/prechecks` | POST | Trigger upgrade precheck |
| `/v1/domains` | GET | List workload domains |
| `/v1/domains/<id>` | GET | Domain details |
| `/v1/clusters` | GET | List clusters |
| `/v1/hosts` | GET | List hosts |
| `/v1/hosts/<id>` | GET | Host details |
| `/v1/vcenter` | GET | List vCenters |
| `/v1/nsxt-clusters` | GET | List NSX clusters |
| `/v1/bundles` | GET | List bundles |
| `/v1/tasks` | GET | List tasks |
| `/v1/tasks/<id>` | GET | Task details |
| `/v1/tasks/<id>` | PATCH | Retry/cancel task |
| `/v1/certificate-authorities` | GET | CA configuration |
| `/v1/sddc-managers` | GET | SDDC Manager info |

### Common Query Parameters

| Parameter | Example | Purpose |
|-----------|---------|---------|
| `limit` | `?limit=50` | Results per page |
| `offset` | `?offset=0` | Pagination offset |
| `status` | `?status=FAILED` | Filter by status |
| `sort` | `?sort=creationTimestamp,DESC` | Sort results |
| `type` | `?type=HOST_COMMISSION` | Filter by task type |


<div style="text-align: center; margin-top: 40px; padding: 20px; border-top: 2px solid #1565c0; color: #666; font-size: 9pt;">

**Fleet / SDDC Manager Health Check Handbook**
Version 1.0 | March 2026
© 2026 Virtual Control LLC — All Rights Reserved

</div>
