---
title: "VCF Operations Health Check Handbook"
subtitle: "Comprehensive Health Verification for VCF Operations in VCF 9"
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
  headerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">VCF Operations Health Check Handbook &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  footerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">Page <span class="pageNumber"></span> of <span class="totalPages"></span> &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  displayHeaderFooter: true
---

<div class="cover-page">

# VCF Operations Health Check Handbook

<div class="subtitle">Comprehensive Health Verification for VCF Operations in VCF 9</div>

<div class="meta">

**Author:** Virtual Control LLC
**Date:** March 2026
**Version:** 1.0
**Classification:** Internal Use
**Platform:** VMware Cloud Foundation 9.0 / VCF Operations 8.18+

</div>
</div>


<div class="toc">

## Table of Contents

<ul>
<li><a href="#overview">1. Overview &amp; Purpose</a></li>
<li><a href="#prerequisites">2. Prerequisites</a></li>
<li><a href="#quick-reference">3. Quick Reference &mdash; All Checks Summary</a></li>
<li><a href="#cluster-status">4. Analytics Cluster Status</a>
  <ul>
  <li><a href="#cluster-state">4.1 Cluster State via CASA</a></li>
  <li><a href="#slice-status">4.2 Slice Status</a></li>
  <li><a href="#node-roles">4.3 Node Roles</a></li>
  </ul>
</li>
<li><a href="#node-health">5. Node Health</a>
  <ul>
  <li><a href="#node-status">5.1 Individual Node Status</a></li>
  <li><a href="#node-resources">5.2 Resource Utilization per Node</a></li>
  <li><a href="#node-heartbeat">5.3 Heartbeat Verification</a></li>
  </ul>
</li>
<li><a href="#adapters">6. Adapter Health</a>
  <ul>
  <li><a href="#adapter-list">6.1 Adapter Instances</a></li>
  <li><a href="#adapter-collection">6.2 Collection Status</a></li>
  <li><a href="#adapter-credentials">6.3 Credential Validation</a></li>
  </ul>
</li>
<li><a href="#collection">7. Collection Status</a></li>
<li><a href="#certificates">8. Certificate Health</a></li>
<li><a href="#licensing">9. Capacity &amp; Licensing</a></li>
<li><a href="#disk-db">10. Disk &amp; Database Health</a></li>
<li><a href="#alerts">11. Alert Engine Health</a></li>
<li><a href="#collectors">12. Remote Collectors</a></li>
<li><a href="#mgmt-packs">13. Management Packs</a></li>
<li><a href="#integrations">14. Integration Health</a></li>
<li><a href="#api-health">15. API Health (Suite API)</a></li>
<li><a href="#ntp-dns">16. NTP &amp; DNS</a></li>
<li><a href="#backup">17. Backup Configuration</a></li>
<li><a href="#resources">18. Resource Utilization</a></li>
<li><a href="#ports">19. Port Reference Table</a></li>
<li><a href="#common-issues">20. Common Issues &amp; Remediation</a></li>
<li><a href="#cli-reference">21. CLI Quick Reference Card</a></li>
<li><a href="#api-reference">22. API Quick Reference (Suite API)</a></li>
</ul>

</div>


## <span id="overview"></span>1. Overview & Purpose

This handbook provides a **complete health check procedure** for VCF Operations (formerly VMware Aria Operations / vRealize Operations) deployed within a VCF 9.0 environment. VCF Operations provides:

- **Performance monitoring** — Real-time and historical analytics for all VCF components
- **Capacity management** — Predictive capacity analysis and right-sizing recommendations
- **Alerting** — Proactive notification of health, risk, and efficiency issues
- **Compliance** — Regulatory and best-practice compliance dashboards
- **Troubleshooting** — Root cause analysis and workload optimization

### When to Run

| Trigger | Priority |
|---------|----------|
| After deployment / node addition | **Critical** |
| Before/after VCF upgrades | **Critical** |
| Weekly routine health check | **Recommended** |
| When dashboards show stale data | **Troubleshooting** |
| When alerts are not firing | **Troubleshooting** |

<div class="info-box">
<strong>Environment Variables:</strong><br>
<code>$OPS</code> = VCF Operations FQDN (e.g., vcf-ops.lab.local)<br>
<code>$OPS_USER</code> = admin<br>
<code>$OPS_PASS</code> = VCF Operations admin password<br>
<code>$OPS_TOKEN</code> = Suite API auth token
</div>



## <span id="prerequisites"></span>2. Prerequisites

### Required Access

| Access Type | Target | Credentials |
|-------------|--------|-------------|
| HTTPS (443) | VCF Operations VIP | admin / password |
| SSH (22) | Each VCF Operations node | root / password |
| Suite API (443) | VCF Operations VIP | admin / auth token |
| CASA Admin | VCF Operations master node | root / admin |

### Token Acquisition (Suite API)

```bash
export OPS="vcf-ops.lab.local"
export OPS_USER="admin"
export OPS_PASS="YourPassword123!"

# Acquire auth token
OPS_TOKEN=$(curl -sk -X POST \
  "https://$OPS/suite-api/api/auth/token/acquire" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\":\"$OPS_USER\",
    \"password\":\"$OPS_PASS\",
    \"authSource\":\"local\"
  }" | jq -r '.token')

echo "Token: ${OPS_TOKEN:0:20}..."

# Convenience function
ops_api() {
  curl -sk -H "Authorization: vRealizeOpsToken $OPS_TOKEN" \
    -H "Content-Type: application/json" \
    "https://$OPS/suite-api$1" 2>/dev/null
}
```

<div class="warn-box">
<strong>Token Expiry:</strong> Suite API tokens expire after 6 hours by default. Re-acquire if you receive 401 responses.
</div>



## <span id="quick-reference"></span>3. Quick Reference — All Checks Summary

| # | Check | Method | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|---|-------|--------|------|------|------|
| 4.1 | Cluster State | CASA/SSH | `RUNNING` / `INITIALIZED` | `STARTING` | `OFFLINE` / `ERROR` |
| 4.2 | Slice Status | CASA | All `ONLINE` | Any `STARTING` | Any `OFFLINE` |
| 5.1 | Node Status | Suite API | All nodes `ONLINE` | Any `STARTING` | Any `OFFLINE` |
| 5.2 | Node CPU | SSH | < 70% | 70-85% | > 85% |
| 5.3 | Node Memory | SSH | < 75% | 75-90% | > 90% |
| 6.1 | Adapters | Suite API | All `COLLECTING` | Any `NOT_COLLECTING` (non-critical) | vCenter adapter not collecting |
| 6.2 | Collection | Suite API | Last collection < 10 min | 10-30 min gap | > 30 min gap |
| 8 | Certificates | SSH/openssl | > 30 days to expiry | 7-30 days | < 7 days / expired |
| 9 | License | Suite API | Valid, objects < capacity | > 80% capacity | Expired or over capacity |
| 10 | Disk | SSH | < 70% all partitions | 70-85% | > 85% |
| 11 | Active Alerts | Suite API | 0 critical | Warning alerts | Critical alerts |
| 12 | Collectors | Suite API | All `ONLINE` | Any `UNKNOWN` | Any `OFFLINE` |
| 15 | Suite API | curl | Response < 2s | 2-5s | > 5s or error |



## <span id="cluster-status"></span>4. Analytics Cluster Status

### <span id="cluster-state"></span>4.1 Cluster State via CASA

**What:** Verify the VCF Operations analytics cluster is fully initialized and running.

**Why:** A cluster not in `RUNNING` state means data collection, alerting, and dashboards may be stale or non-functional.

#### SSH Method (on master node)

```bash
ssh root@$OPS

# Check cluster status via CASA admin
$VMWARE_PYTHON_PATH/bin/python \
  /usr/lib/vmware-vcops/tools/opscli/admin-cli.py \
  getClusterStatus
```

**Expected Output (Healthy):**

```
Cluster Status: RUNNING
Cluster Uptime: 15 days 8 hours
Master Node: vcf-ops-01.lab.local (ONLINE)
Data Node: vcf-ops-02.lab.local (ONLINE)
Data Node: vcf-ops-03.lab.local (ONLINE)
Remote Collector: rc-01.lab.local (ONLINE)
```

#### Alternative — CASA API

```bash
curl -sk "https://$OPS/casa/cluster/status" \
  -u "admin:$OPS_PASS" | jq .
```

**Expected Output:**

```json
{
  "cluster_status": "RUNNING",
  "slice_status": "ONLINE",
  "node_statuses": [
    {"node_name": "vcf-ops-01", "status": "ONLINE", "role": "MASTER"},
    {"node_name": "vcf-ops-02", "status": "ONLINE", "role": "DATA"},
    {"node_name": "vcf-ops-03", "status": "ONLINE", "role": "DATA"}
  ]
}
```

#### Pass / Warn / Fail

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | Cluster `RUNNING`, all nodes `ONLINE` | Fully operational |
| <span class="badge-warn">WARN</span> | Cluster `STARTING` or any node `STARTING` | Coming online |
| <span class="badge-fail">FAIL</span> | Cluster `OFFLINE` or `ERROR` | Data collection stopped |

<div class="fix-box">
<strong>Remediation:</strong><br>
1. Bring cluster online: Use CASA admin UI (https://&lt;master&gt;/casa) → Cluster Operations → Start<br>
2. Via CLI: <code>$VMWARE_PYTHON_PATH/bin/python /usr/lib/vmware-vcops/tools/opscli/admin-cli.py bringClusterOnline</code><br>
3. Check cluster logs: <code>/storage/log/vcops/casa/casa.log</code>
</div>


### <span id="slice-status"></span>4.2 Slice Status

**What:** Verify all analytics slices are online.

```bash
# Via CASA API
curl -sk "https://$OPS/casa/slice/status" \
  -u "admin:$OPS_PASS" | jq .
```

**Expected Output:**

```json
{
  "slices": [
    {"slice_id": 0, "status": "ONLINE", "node": "vcf-ops-01"},
    {"slice_id": 1, "status": "ONLINE", "node": "vcf-ops-02"},
    {"slice_id": 2, "status": "ONLINE", "node": "vcf-ops-03"}
  ]
}
```

### <span id="node-roles"></span>4.3 Node Roles

| Role | Description | Count |
|------|-------------|-------|
| MASTER | Primary analytics node, cluster coordinator | 1 |
| MASTER_REPLICA | Failover for master | 1 (if HA) |
| DATA | Analytics processing and storage | 1+ |
| REMOTE_COLLECTOR | Remote data collection proxy | 0+ |



## <span id="node-health"></span>5. Node Health

### <span id="node-status"></span>5.1 Individual Node Status

```bash
# List all nodes via Suite API
ops_api "/api/deployment/node" | jq '.nodeList[] | {
  name: .name,
  ip: .ip,
  role: .role,
  status: .status,
  version: .version
}'
```

### <span id="node-resources"></span>5.2 Resource Utilization per Node

```bash
ssh root@$OPS

# CPU
top -b -n 1 | head -5

# Memory
free -m

# Disk (critical partitions)
df -h /storage /storage/db /storage/log /storage/core
```

#### Critical Partitions

| Partition | Purpose | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|-----------|---------|------|------|------|
| `/storage` | Analytics data | < 70% | 70-85% | > 85% |
| `/storage/db` | Cassandra / xDB | < 70% | 70-85% | > 85% |
| `/storage/log` | Log files | < 70% | 70-85% | > 85% |
| `/` (root) | OS | < 70% | 70-85% | > 85% |

### <span id="node-heartbeat"></span>5.3 Heartbeat Verification

```bash
# Check last heartbeat per node
ops_api "/api/deployment/node" | jq '.nodeList[] | {
  name: .name,
  lastHeartbeat: .lastHeartbeat,
  heartbeatStatus: .heartbeatStatus
}'
```



## <span id="adapters"></span>6. Adapter Health

### <span id="adapter-list"></span>6.1 Adapter Instances

**What:** Verify all configured adapter instances are collecting data.

```bash
# List all adapters
ops_api "/api/adapters" | jq '.adapterInstancesInfoDto[] | {
  id: .id,
  adapterKind: .resourceKey.adapterKindKey,
  name: .resourceKey.name,
  collectorId: .collectorId,
  collectionState: .collectionState,
  collectionStatus: .collectionStatus
}'
```

**Expected Output:**

```json
{
  "id": "abc123",
  "adapterKind": "VMWARE",
  "name": "vCenter - vcenter.lab.local",
  "collectorId": "1",
  "collectionState": "COLLECTING",
  "collectionStatus": "DATA_RECEIVING"
}
```

#### Key Adapters to Verify

| Adapter Kind | Name Pattern | Critical |
|-------------|--------------|----------|
| `VMWARE` | vCenter adapter | **Yes** |
| `NSXTAdapter` | NSX-T adapter | **Yes** |
| `VsanAdapter` | vSAN adapter | **Yes** |
| `SDDCHealthAdapter` | SDDC Health | **Yes** |
| `PythonRemediationVcenterAdapter` | Automation | No |
| `LogInsightAdapter` | Log Insight integration | No |

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All critical adapters `COLLECTING` | Data flowing |
| <span class="badge-warn">WARN</span> | Non-critical adapter not collecting | Limited functionality |
| <span class="badge-fail">FAIL</span> | vCenter or NSX adapter not collecting | Stale data / no monitoring |

### <span id="adapter-collection"></span>6.2 Collection Status

```bash
# Check last collection time for a specific adapter
ADAPTER_ID="<adapter-id>"
ops_api "/api/adapters/$ADAPTER_ID" | jq '{
  name: .resourceKey.name,
  collectionState: .collectionState,
  lastCollected: .lastCollected,
  numberOfMetricsCollected: .numberOfMetricsCollected,
  numberOfResourcesCollected: .numberOfResourcesCollected
}'
```

### <span id="adapter-credentials"></span>6.3 Credential Validation

```bash
# List credentials
ops_api "/api/credentials" | jq '.credentialInstances[] | {
  id: .id,
  name: .name,
  adapterKind: .adapterKindKey
}'

# Test credential (trigger validation)
curl -sk -X POST \
  -H "Authorization: vRealizeOpsToken $OPS_TOKEN" \
  -H "Content-Type: application/json" \
  "https://$OPS/suite-api/api/adapters/$ADAPTER_ID/monitoringstate/start"
```

<div class="fix-box">
<strong>Remediation for adapter not collecting:</strong><br>
1. Verify credential: Update password if changed on target<br>
2. Test connectivity: <code>curl -sk https://&lt;target&gt;:443</code> from OPS node<br>
3. Restart adapter: Suite API → <code>POST /api/adapters/&lt;id&gt;/monitoringstate/stop</code> then <code>/start</code><br>
4. Check adapter logs: <code>/storage/log/vcops/adapterkind/&lt;adapter-kind&gt;/</code>
</div>



## <span id="collection"></span>7. Collection Status

**What:** Verify data collection is current and no gaps exist.

```bash
# Get collection stats
ops_api "/api/resources?adapterKind=VMWARE&resourceKind=VirtualMachine&pageSize=5" | jq '{
  totalCount: .totalCount,
  resources: [.resourceList[].resourceKey.name]
}'
```

#### Check for Collection Gaps

```bash
# Recent collection cycles on the node
ssh root@$OPS
grep "Collection completed" /storage/log/vcops/analytics/analytics.log | tail -10
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | Last collection < 10 minutes ago | Current data |
| <span class="badge-warn">WARN</span> | Last collection 10-30 minutes ago | Slight delay |
| <span class="badge-fail">FAIL</span> | Last collection > 30 minutes ago | Stale data |


## <span id="certificates"></span>8. Certificate Health

```bash
# Check web certificate
echo | openssl s_client -connect $OPS:443 2>/dev/null | \
  openssl x509 -noout -dates -subject

# Check all certificates on the node
ssh root@$OPS
find /storage/vcops/user/conf/ssl -name "*.pem" -exec \
  sh -c 'echo "=== $1 ===" && openssl x509 -in "$1" -noout -enddate' _ {} \;
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All certificates > 30 days from expiry | Healthy |
| <span class="badge-warn">WARN</span> | Any certificate 7-30 days from expiry | Plan renewal |
| <span class="badge-fail">FAIL</span> | Any certificate < 7 days or expired | Immediate action |


## <span id="licensing"></span>9. Capacity & Licensing

```bash
# Check license status
ops_api "/api/deployment/licenses" | jq '.licenseDetails[] | {
  licenseKey: .licenseKey[0:8],
  edition: .edition,
  capacity: .capacity,
  usage: .usage,
  expirationDate: .expirationDate
}'
```

**Expected Output:**

```json
{
  "licenseKey": "XXXXX-XX",
  "edition": "Enterprise",
  "capacity": 500,
  "usage": 320,
  "expirationDate": "2027-03-01"
}
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | License valid, usage < 80% of capacity | Healthy |
| <span class="badge-warn">WARN</span> | Usage > 80% capacity or < 60 days to expiry | Plan expansion |
| <span class="badge-fail">FAIL</span> | License expired or usage > capacity | Functionality limited |



## <span id="disk-db"></span>10. Disk & Database Health

### Disk Usage

```bash
ssh root@$OPS
df -h /storage /storage/db /storage/log
```

### Cassandra / xDB Health

```bash
# Check Cassandra status
ssh root@$OPS
/opt/vmware/vcops/cassandra/apache-cassandra/bin/nodetool status
```

**Expected Output:**

```
Datacenter: vrops
==========================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address         Load       Tokens  Owns    Host ID
UN  192.168.1.77    15.2 GiB   256     100.0%  abc123...
UN  192.168.1.78    14.8 GiB   256     100.0%  def456...
UN  192.168.1.79    15.0 GiB   256     100.0%  ghi789...
```

| Status | Meaning |
|--------|---------|
| `UN` | Up, Normal — **healthy** |
| `DN` | Down, Normal — **node offline** |
| `UL` | Up, Leaving — decommissioning |
| `UJ` | Up, Joining — bootstrapping |

### Data Retention

```bash
# Check retention settings
ops_api "/api/deployment/retention" | jq .
```

<div class="fix-box">
<strong>Remediation for disk full:</strong><br>
1. Reduce retention: Lower data retention period via Administration → Global Settings<br>
2. Clean old logs: <code>find /storage/log -name "*.gz" -mtime +14 -delete</code><br>
3. Cassandra compaction: <code>/opt/vmware/vcops/cassandra/apache-cassandra/bin/nodetool compact</code><br>
4. Expand disk: Power off node → expand VMDK → extend partition
</div>


## <span id="alerts"></span>11. Alert Engine Health

```bash
# Count active alerts by criticality
ops_api "/api/alerts?status=ACTIVE&criticality=CRITICAL" | jq '.totalCount'
ops_api "/api/alerts?status=ACTIVE&criticality=IMMEDIATE" | jq '.totalCount'
ops_api "/api/alerts?status=ACTIVE&criticality=WARNING" | jq '.totalCount'
```

#### Check Alert Plugins (Notifications)

```bash
ops_api "/api/alertplugins" | jq '.notificationPluginInstances[] | {
  id: .id,
  name: .name,
  pluginType: .pluginTypeId,
  enabled: .enabled
}'
```

#### Test SMTP Notification

```bash
# Verify SMTP relay
ssh root@$OPS
echo "Test" | mail -s "VCF Ops Health Check Test" admin@lab.local
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | 0 critical alerts, notifications working | Healthy |
| <span class="badge-warn">WARN</span> | Warning alerts present | Review and tune |
| <span class="badge-fail">FAIL</span> | Critical alerts or notifications broken | Immediate review |



## <span id="collectors"></span>12. Remote Collectors

```bash
# List remote collectors
ops_api "/api/collectors" | jq '.collector[] | {
  id: .id,
  name: .name,
  ip: .ip,
  status: .state,
  version: .version,
  usingVRealize: .usingVRealize
}'
```

**Expected Output:**

```json
{
  "id": "1",
  "name": "vcf-ops-rc-01",
  "ip": "192.168.1.80",
  "status": "ONLINE",
  "version": "8.18.0.12345678"
}
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All collectors `ONLINE` | Healthy |
| <span class="badge-warn">WARN</span> | Any collector `UNKNOWN` | Communication issue |
| <span class="badge-fail">FAIL</span> | Any collector `OFFLINE` | Data collection impacted |


## <span id="mgmt-packs"></span>13. Management Packs

```bash
# List installed management packs (solutions)
ops_api "/api/solutions" | jq '.solution[] | {
  id: .id,
  name: .name,
  version: .version,
  adapterKind: .adapterKindKeys
}'
```


## <span id="integrations"></span>14. Integration Health

### vCenter Adapter

```bash
# Check vCenter adapter specifically
ops_api "/api/adapters?adapterKindKey=VMWARE" | jq '.adapterInstancesInfoDto[] | {
  name: .resourceKey.name,
  collectionState: .collectionState,
  lastCollected: .lastCollected
}'
```

### NSX Adapter

```bash
ops_api "/api/adapters?adapterKindKey=NSXTAdapter" | jq '.adapterInstancesInfoDto[] | {
  name: .resourceKey.name,
  collectionState: .collectionState
}'
```

### vSAN Adapter

```bash
ops_api "/api/adapters?adapterKindKey=VsanAdapter" | jq '.adapterInstancesInfoDto[] | {
  name: .resourceKey.name,
  collectionState: .collectionState
}'
```

### SDDC Health Adapter

```bash
ops_api "/api/adapters?adapterKindKey=SDDCHealthAdapter" | jq '.adapterInstancesInfoDto[] | {
  name: .resourceKey.name,
  collectionState: .collectionState
}'
```



## <span id="api-health"></span>15. API Health (Suite API)

### Token Acquisition Test

```bash
time curl -sk -X POST \
  "https://$OPS/suite-api/api/auth/token/acquire" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$OPS_USER\",\"password\":\"$OPS_PASS\",\"authSource\":\"local\"}" \
  | jq -r '.token' > /dev/null
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | Token acquired in < 2 seconds | API responsive |
| <span class="badge-warn">WARN</span> | 2-5 seconds | API slow |
| <span class="badge-fail">FAIL</span> | > 5 seconds or failed | API issue |

### Endpoint Responsiveness

```bash
ENDPOINTS="/api/deployment/node /api/adapters /api/resources?pageSize=1 /api/alerts?pageSize=1"
for EP in $ENDPOINTS; do
  START=$(date +%s%N)
  HTTP=$(curl -sk -o /dev/null -w "%{http_code}" \
    -H "Authorization: vRealizeOpsToken $OPS_TOKEN" \
    "https://$OPS/suite-api$EP")
  END=$(date +%s%N)
  MS=$(( (END - START) / 1000000 ))
  echo "$EP: HTTP $HTTP (${MS}ms)"
done
```


## <span id="ntp-dns"></span>16. NTP & DNS

```bash
ssh root@$OPS
# NTP
timedatectl status
chronyc tracking

# DNS
nslookup vcenter.lab.local
nslookup nsx-vip.lab.local
cat /etc/resolv.conf
```


## <span id="backup"></span>17. Backup Configuration

```bash
# Check via CASA
curl -sk "https://$OPS/casa/deployment/backup/schedule" \
  -u "admin:$OPS_PASS" | jq .
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | Backup configured, recent success | Protected |
| <span class="badge-warn">WARN</span> | > 24h since last backup | Check schedule |
| <span class="badge-fail">FAIL</span> | No backup configured | Data at risk |


## <span id="resources"></span>18. Resource Utilization

```bash
ssh root@$OPS
# CPU and Load
uptime
top -b -n 1 | head -5

# Memory
free -m

# Disk
df -h

# Java heap (analytics process)
ps aux | grep analytics | grep -v grep | awk '{print $6/1024 " MB"}'
```

| Resource | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| CPU | < 70% | 70-85% | > 85% |
| Memory | < 75% | 75-90% | > 90% |
| Disk (any partition) | < 70% | 70-85% | > 85% |
| Java Heap | < 80% allocated | 80-90% | > 90% (OOM risk) |



## <span id="ports"></span>19. Port Reference Table

### Inbound Ports

| Source | Port | Protocol | Purpose |
|--------|------|----------|---------|
| Admin Browser | 443 | TCP | Web UI / Suite API |
| Admin | 22 | TCP | SSH |
| Admin | 443 | TCP | CASA admin interface |
| Remote Collector | 443 | TCP | Collector → cluster |
| vCenter | 443 | TCP | Webhook notifications |

### Outbound Ports

| Destination | Port | Protocol | Purpose |
|-------------|------|----------|---------|
| vCenter | 443 | TCP | Data collection (vSphere API) |
| NSX Manager | 443 | TCP | NSX data collection |
| ESXi Hosts | 443 | TCP | Host metrics |
| SDDC Manager | 443 | TCP | SDDC Health data |
| VCF Ops Logs | 443/9543 | TCP | Log integration |
| SMTP Server | 25/587 | TCP | Email notifications |
| DNS Server | 53 | TCP/UDP | Name resolution |
| NTP Server | 123 | UDP | Time synchronization |

### Inter-Node Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 443 | TCP | HTTPS / Suite API |
| 3091 | TCP | Cluster communication |
| 3092 | TCP | Cluster communication |
| 7000 | TCP | Cassandra inter-node |
| 7001 | TCP | Cassandra SSL inter-node |
| 9042 | TCP | Cassandra native transport |
| 9160 | TCP | Cassandra Thrift |



## <span id="common-issues"></span>20. Common Issues & Remediation

### 20.1 Cluster Offline

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| CASA shows cluster `OFFLINE` | Node crash or network partition | Bring cluster online via CASA admin |
| Cluster won't start | Disk full on master node | Free disk space, then start cluster |
| Split-brain between nodes | Network connectivity loss | Restore network, restart cluster |

<div class="fix-box">
<strong>Bring cluster online:</strong><br>
1. CASA UI: https://&lt;master&gt;/casa → Cluster → Bring Online<br>
2. CLI: <code>$VMWARE_PYTHON_PATH/bin/python /usr/lib/vmware-vcops/tools/opscli/admin-cli.py bringClusterOnline</code><br>
3. Force start (last resort): <code>admin-cli.py forceClusterOnline</code>
</div>

### 20.2 Slice Degraded

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Slice `OFFLINE` on one node | Node resource exhaustion | Check disk/memory, restart node slice |
| Multiple slices offline | Cluster issue | Restart entire cluster |

### 20.3 Adapter Failures

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| `NOT_COLLECTING` | Credential change | Update credential in VCF Ops |
| `COLLECTING` but stale data | Target unreachable | Check network connectivity |
| Adapter crash | Memory issue | Increase adapter memory, restart |

### 20.4 Disk Full

```bash
# Quick disk cleanup
ssh root@$OPS
# 1. Clean old logs
find /storage/log -name "*.gz" -mtime +14 -delete
# 2. Check large files
du -sh /storage/* | sort -rh | head -10
# 3. Compact Cassandra
/opt/vmware/vcops/cassandra/apache-cassandra/bin/nodetool compact
```

### 20.5 Collection Gaps

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Dashboards show gaps | Collection cycle missed | Restart adapter |
| Historical data missing | Retention policy deleted it | Adjust retention |
| New objects not appearing | Discovery cycle pending | Wait for next cycle or force discovery |

### 20.6 Certificate Expiry

| Impact | Resolution |
|--------|------------|
| Suite API returns TLS errors | Replace certificate via CASA admin |
| Remote collectors disconnect | Replace collector certificate, re-register |
| Browser security warnings | Install custom CA certificate |



## <span id="cli-reference"></span>21. CLI Quick Reference Card

### CASA Admin CLI

| Command | Purpose |
|---------|---------|
| `admin-cli.py getClusterStatus` | Cluster status |
| `admin-cli.py bringClusterOnline` | Start cluster |
| `admin-cli.py takeClusterOffline` | Stop cluster |
| `admin-cli.py forceClusterOnline` | Force start cluster |
| `admin-cli.py getNodeStatus` | Node status |
| `admin-cli.py getSliceStatus` | Slice status |

<div class="info-box">
<strong>CLI Path:</strong> <code>$VMWARE_PYTHON_PATH/bin/python /usr/lib/vmware-vcops/tools/opscli/admin-cli.py &lt;command&gt;</code>
</div>

### System Commands

| Command | Purpose |
|---------|---------|
| `df -h /storage /storage/db /storage/log` | Disk usage |
| `free -m` | Memory usage |
| `top -b -n 1 \| head -5` | CPU / load |
| `timedatectl` | Time sync |
| `chronyc tracking` | NTP details |
| `systemctl status vmware-vcops-analytics` | Analytics service |
| `systemctl status vmware-vcops-collector` | Collector service |
| `systemctl status vmware-vcops-web` | Web service |
| `systemctl status vmware-vcops-casa` | CASA service |

### Cassandra Commands

| Command | Purpose |
|---------|---------|
| `nodetool status` | Cassandra cluster status |
| `nodetool info` | Local node info |
| `nodetool compactionstats` | Active compactions |
| `nodetool compact` | Trigger compaction |
| `nodetool repair` | Repair data |
| `nodetool describecluster` | Cluster schema |

### Log Locations

| Log | Path |
|-----|------|
| Analytics | `/storage/log/vcops/analytics/analytics.log` |
| Collector | `/storage/log/vcops/collector/collector.log` |
| CASA | `/storage/log/vcops/casa/casa.log` |
| Web | `/storage/log/vcops/web/web.log` |
| Adapter (per-type) | `/storage/log/vcops/adapterkind/<kind>/` |
| Cassandra | `/storage/log/vcops/cassandra/system.log` |



## <span id="api-reference"></span>22. API Quick Reference (Suite API)

### Authentication

```bash
# Acquire token
curl -sk -X POST "https://$OPS/suite-api/api/auth/token/acquire" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password","authSource":"local"}'

# Release token
curl -sk -X POST "https://$OPS/suite-api/api/auth/token/release" \
  -H "Authorization: vRealizeOpsToken $OPS_TOKEN" \
  -H "Content-Type: application/json"
```

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/token/acquire` | POST | Get auth token |
| `/api/auth/token/release` | POST | Release auth token |
| `/api/deployment/node` | GET | List cluster nodes |
| `/api/deployment/licenses` | GET | License info |
| `/api/deployment/retention` | GET | Data retention config |
| `/api/adapters` | GET | List all adapters |
| `/api/adapters/<id>` | GET | Adapter details |
| `/api/adapters?adapterKindKey=VMWARE` | GET | Filter by adapter kind |
| `/api/adapters/<id>/monitoringstate/start` | POST | Start adapter |
| `/api/adapters/<id>/monitoringstate/stop` | POST | Stop adapter |
| `/api/credentials` | GET | List credentials |
| `/api/resources` | GET | List resources |
| `/api/resources/<id>/stats/latest` | GET | Latest metrics |
| `/api/alerts` | GET | List alerts |
| `/api/alerts?status=ACTIVE` | GET | Active alerts only |
| `/api/alerts?criticality=CRITICAL` | GET | Critical alerts only |
| `/api/alertplugins` | GET | Notification plugins |
| `/api/collectors` | GET | Remote collectors |
| `/api/solutions` | GET | Management packs |
| `/api/reports` | GET | Report definitions |

### Common Query Parameters

| Parameter | Example | Purpose |
|-----------|---------|---------|
| `pageSize` | `?pageSize=100` | Results per page |
| `page` | `?page=0` | Page number |
| `adapterKind` | `?adapterKind=VMWARE` | Filter by adapter |
| `resourceKind` | `?resourceKind=VirtualMachine` | Filter by resource type |
| `status` | `?status=ACTIVE` | Alert status filter |
| `criticality` | `?criticality=CRITICAL` | Alert criticality |


<div style="text-align: center; margin-top: 40px; padding: 20px; border-top: 2px solid #1565c0; color: #666; font-size: 9pt;">

**VCF Operations Health Check Handbook**
Version 1.0 | March 2026
© 2026 Virtual Control LLC — All Rights Reserved

</div>
