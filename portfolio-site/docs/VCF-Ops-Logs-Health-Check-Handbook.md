---
title: "VCF Operations for Logs Health Check Handbook"
subtitle: "Comprehensive Health Verification for VCF Ops for Logs in VCF 9"
author: "Virtual Control LLC"
date: "March 2026"
version: "1.0"
classification: "Internal Use"
css: |-
  body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; color: #1a1a1a; max-width: 100%; line-height: 1.5; }
  h1 { color: #ffffff; background: linear-gradient(135deg, #0b3d6b, #1565c0); padding: 16px 22px; border-radius: 6px; font-size: 22pt; margin-top: 30px; }
  h2 { color: #0b3d6b; border-bottom: 3px solid #1565c0; padding-bottom: 6px; font-size: 15pt; margin-top: 28px; }
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
  headerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">VCF Operations for Logs Health Check Handbook &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  footerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">Page <span class="pageNumber"></span> of <span class="totalPages"></span> &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  displayHeaderFooter: true
---

<div class="cover-page">

# VCF Operations for Logs Health Check Handbook

<div class="subtitle">Comprehensive Health Verification for VCF Ops for Logs in VCF 9</div>

<div class="meta">
<strong>Prepared by:</strong> Virtual Control LLC<br>
<strong>Date:</strong> March 2026<br>
<strong>Version:</strong> 1.0<br>
<strong>Classification:</strong> Internal Use<br>
<strong>Platform:</strong> VMware Cloud Foundation 9.0<br>
<strong>Product:</strong> VCF Operations for Logs (formerly VMware Aria Operations for Logs / vRealize Log Insight)
</div>

</div>

<div class="toc">

## Table of Contents

<ul>
<li><a href="#overview-purpose">1. Overview & Purpose</a>
  <ul>
    <li><a href="#scope">1.1 Health Check Scope</a></li>
    <li><a href="#when-to-run">1.2 When to Run This Health Check</a></li>
    <li><a href="#component-overview">1.3 Component Overview</a></li>
  </ul>
</li>
<li><a href="#prerequisites">2. Prerequisites</a>
  <ul>
    <li><a href="#ssh-access">2.1 SSH Access</a></li>
    <li><a href="#api-access">2.2 API Access & Credentials</a></li>
    <li><a href="#env-variables">2.3 Environment Variables</a></li>
    <li><a href="#tools-required">2.4 Required Tools</a></li>
  </ul>
</li>
<li><a href="#quick-reference">3. Quick Reference Summary Table</a></li>
<li><a href="#service-status">4. Service Status</a>
  <ul>
    <li><a href="#loginsight-daemon">4.1 Log Insight Daemon</a></li>
    <li><a href="#cassandra-service">4.2 Cassandra Service</a></li>
    <li><a href="#apache-service">4.3 Apache / HTTPD Service</a></li>
    <li><a href="#fluentd-service">4.4 Fluentd Service</a></li>
    <li><a href="#all-services-summary">4.5 All Services Summary Check</a></li>
  </ul>
</li>
<li><a href="#cluster-health">5. Cluster Health</a>
  <ul>
    <li><a href="#node-roles">5.1 Node Roles (Master / Worker)</a></li>
    <li><a href="#cluster-api">5.2 Cluster Status via API</a></li>
    <li><a href="#ilb-status">5.3 Integrated Load Balancer (ILB)</a></li>
    <li><a href="#node-connectivity">5.4 Node-to-Node Connectivity</a></li>
  </ul>
</li>
<li><a href="#disk-storage">6. Disk & Storage Health</a>
  <ul>
    <li><a href="#partition-layout">6.1 Storage Partition Layout</a></li>
    <li><a href="#storage-usage">6.2 Storage Usage Thresholds</a></li>
    <li><a href="#cassandra-data">6.3 Cassandra Data Size</a></li>
    <li><a href="#retention-policy">6.4 Retention Policy</a></li>
    <li><a href="#archive-config">6.5 Archive Configuration</a></li>
  </ul>
</li>
<li><a href="#ingestion-rate">7. Ingestion Rate Monitoring</a>
  <ul>
    <li><a href="#events-per-second">7.1 Events Per Second</a></li>
    <li><a href="#ingestion-pipeline">7.2 Ingestion Pipeline Health</a></li>
    <li><a href="#dropped-events">7.3 Dropped Events & Queue Depth</a></li>
  </ul>
</li>
<li><a href="#log-forwarding">8. Log Forwarding Configuration</a>
  <ul>
    <li><a href="#forwarding-destinations">8.1 Forwarding Destinations</a></li>
    <li><a href="#forwarding-protocols">8.2 Protocol & TLS Configuration</a></li>
    <li><a href="#forwarding-health">8.3 Forwarding Health Verification</a></li>
    <li><a href="#test-forwarding">8.4 Test Forwarding</a></li>
  </ul>
</li>
<li><a href="#content-packs">9. Content Packs</a>
  <ul>
    <li><a href="#installed-packs">9.1 Installed Content Packs</a></li>
    <li><a href="#pack-versions">9.2 Version Status & Updates</a></li>
    <li><a href="#auto-update">9.3 Auto-Update Configuration</a></li>
  </ul>
</li>
<li><a href="#integration-ops">10. Integration with VCF Operations</a>
  <ul>
    <li><a href="#launch-in-context">10.1 Launch-in-Context Configuration</a></li>
    <li><a href="#shared-auth">10.2 Shared Authentication</a></li>
    <li><a href="#data-flow">10.3 Data Flow Verification</a></li>
  </ul>
</li>
<li><a href="#agent-status">11. Agent Status</a>
  <ul>
    <li><a href="#connected-agents">11.1 Connected Agents</a></li>
    <li><a href="#agent-groups">11.2 Agent Groups</a></li>
    <li><a href="#stale-agents">11.3 Stale Agent Detection</a></li>
  </ul>
</li>
<li><a href="#api-health">12. API Health</a>
  <ul>
    <li><a href="#token-acquisition">12.1 Token Acquisition</a></li>
    <li><a href="#api-responsiveness">12.2 API Responsiveness</a></li>
    <li><a href="#rate-limiting">12.3 Rate Limiting</a></li>
  </ul>
</li>
<li><a href="#certificate-health">13. Certificate Health</a>
  <ul>
    <li><a href="#ssl-check">13.1 SSL Certificate Verification</a></li>
    <li><a href="#custom-ca">13.2 Custom CA Configuration</a></li>
    <li><a href="#cert-expiry">13.3 Certificate Expiry Monitoring</a></li>
  </ul>
</li>
<li><a href="#ntp-dns">14. NTP & DNS</a>
  <ul>
    <li><a href="#time-sync">14.1 Time Synchronization</a></li>
    <li><a href="#dns-resolution">14.2 DNS Resolution</a></li>
  </ul>
</li>
<li><a href="#backup-config">15. Backup Configuration</a>
  <ul>
    <li><a href="#backup-status">15.1 Backup Status</a></li>
    <li><a href="#backup-location">15.2 Backup Location & Retention</a></li>
  </ul>
</li>
<li><a href="#resource-utilization">16. Resource Utilization</a>
  <ul>
    <li><a href="#cpu-memory">16.1 CPU & Memory per Node</a></li>
    <li><a href="#jvm-heap">16.2 JVM Heap Usage</a></li>
    <li><a href="#disk-io">16.3 Disk I/O Performance</a></li>
  </ul>
</li>
<li><a href="#port-reference">17. Port Reference Table</a></li>
<li><a href="#common-issues">18. Common Issues & Remediation</a>
  <ul>
    <li><a href="#cassandra-issues">18.1 Cassandra Issues</a></li>
    <li><a href="#ingestion-drops">18.2 Ingestion Drops</a></li>
    <li><a href="#disk-full">18.3 Disk Full Scenarios</a></li>
    <li><a href="#cluster-split">18.4 Cluster Split-Brain</a></li>
    <li><a href="#cert-problems">18.5 Certificate Problems</a></li>
    <li><a href="#agent-disconnects">18.6 Agent Disconnects</a></li>
  </ul>
</li>
<li><a href="#cli-reference">19. CLI Quick Reference Card</a></li>
<li><a href="#api-reference">20. API Quick Reference</a></li>
</ul>

</div>

<div class="page-break"></div>

<a id="overview-purpose"></a>

# 1. Overview & Purpose

This handbook provides a comprehensive, repeatable methodology for verifying the health of **VCF Operations for Logs** (formerly VMware Aria Operations for Logs / vRealize Log Insight) within a **VMware Cloud Foundation 9** environment. It is designed for infrastructure engineers, VCF administrators, and operations teams who need to validate that the centralized logging platform is functioning correctly, ingesting events at expected rates, and maintaining cluster integrity.

<a id="scope"></a>

## 1.1 Health Check Scope

This health check covers the following areas:

- **Service-level health** -- All critical daemons and processes running on each Ops for Logs node
- **Cluster integrity** -- Master/worker node relationships, quorum, and ILB status
- **Storage and retention** -- Disk utilization, Cassandra data footprint, retention and archival policies
- **Ingestion pipeline** -- Event throughput rates, dropped events, and queue depth
- **Log forwarding** -- Outbound syslog/CFAPI forwarding destinations and TLS configuration
- **Content packs** -- Installed packs, versioning, and compatibility with VCF 9
- **Integration health** -- Connectivity between Ops for Logs and VCF Operations (Aria Operations)
- **Agent management** -- Agent connectivity, grouping, and stale agent detection
- **API availability** -- REST API authentication and response times
- **Certificate validity** -- SSL/TLS certificate chain, custom CA, and expiry monitoring
- **Infrastructure services** -- NTP time synchronization and DNS resolution
- **Backup readiness** -- Backup configuration, schedule, and recoverability
- **Resource consumption** -- CPU, memory, disk I/O, and JVM heap on each node

<a id="when-to-run"></a>

## 1.2 When to Run This Health Check

| Trigger | Frequency | Priority |
|---------|-----------|----------|
| Scheduled proactive review | Monthly | Standard |
| Pre-upgrade validation (VCF lifecycle) | Before each upgrade cycle | High |
| Post-upgrade verification | Immediately after upgrade | Critical |
| After cluster node addition or removal | As needed | High |
| After certificate renewal | As needed | High |
| Performance degradation reported | Reactive | Critical |
| Ingestion rate anomalies detected | Reactive | Critical |
| After datacenter-level maintenance window | As needed | Standard |
| Disaster recovery rehearsal | Quarterly | High |

<a id="component-overview"></a>

## 1.3 Component Overview

VCF Operations for Logs in VCF 9 consists of the following architectural components:

| Component | Description | Default Port(s) |
|-----------|-------------|-----------------|
| **Log Insight Daemon** | Core ingestion and query engine | 9000, 9543 |
| **Apache HTTPD** | Reverse proxy for the web UI and API | 443 (HTTPS), 80 (redirect) |
| **Cassandra** | Embedded data store for log metadata and indexes | 9042, 7000, 7199 |
| **Fluentd** | Log collection agent framework (embedded) | Various |
| **ILB (Integrated Load Balancer)** | Virtual IP distribution across cluster nodes | Same as service ports |
| **REST API** | Programmatic access for queries, config, and management | 443, 9543 |
| **Agents (li-agent)** | Remote log collection agents on ESXi and VMs | 1514, 514, 6514 |

<div class="info-box">
<strong>Note:</strong> In VCF 9, Operations for Logs is deployed and lifecycle-managed through SDDC Manager. The product was previously known as VMware Aria Operations for Logs (8.x) and vRealize Log Insight (pre-8.x). API endpoints and CLI commands remain largely consistent across naming transitions.
</div>

<div class="page-break"></div>

<a id="prerequisites"></a>

# 2. Prerequisites

<a id="ssh-access"></a>

## 2.1 SSH Access

SSH access to each Ops for Logs node is required for service-level and OS-level checks. The default administrative user is `root` or a configured `admin` account.

```bash
# Test SSH connectivity to each node
ssh root@ops-for-logs-node1.vcf.local "hostname && uptime"
ssh root@ops-for-logs-node2.vcf.local "hostname && uptime"
ssh root@ops-for-logs-node3.vcf.local "hostname && uptime"
```

**Expected output:**
```
ops-for-logs-node1
 10:23:45 up 45 days,  3:12,  1 user,  load average: 0.42, 0.38, 0.35
```

<div class="warn-box">
<strong>Warning:</strong> If SSH access is disabled or restricted by policy, coordinate with the security team. Many checks in this handbook require shell-level access. API-only alternatives are noted where available.
</div>

<a id="api-access"></a>

## 2.2 API Access & Credentials

All API calls in this handbook target the Ops for Logs REST API at `https://<ops-for-logs-vip>/api/v1/` or `https://<ops-for-logs-vip>/api/v2/`. An authentication token is required for most endpoints.

#### Obtain an API Session Token

```bash
# Authenticate and retrieve bearer token
curl -sk -X POST "https://ops-for-logs.vcf.local/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "<ADMIN_PASSWORD>",
    "provider": "Local"
  }'
```

**Expected response:**
```json
{
  "userId": "012345ab-cdef-6789-abcd-ef0123456789",
  "sessionId": "aBcDeFgHiJkLmNoPqRsTuVwXyZ123456",
  "ttl": 1800
}
```

Store the `sessionId` for subsequent API calls:

```bash
export TOKEN="aBcDeFgHiJkLmNoPqRsTuVwXyZ123456"
```

<a id="env-variables"></a>

## 2.3 Environment Variables

Set these variables at the start of your health check session for convenience:

```bash
# Ops for Logs VIP or FQDN
export OFL_HOST="ops-for-logs.vcf.local"

# Individual node FQDNs
export OFL_NODE1="ops-for-logs-node1.vcf.local"
export OFL_NODE2="ops-for-logs-node2.vcf.local"
export OFL_NODE3="ops-for-logs-node3.vcf.local"

# API base URL
export OFL_API="https://${OFL_HOST}/api/v1"

# Authenticate and store token
export TOKEN=$(curl -sk -X POST "${OFL_API}/sessions" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"'"${OFL_PASS}"'","provider":"Local"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['sessionId'])")

echo "Token acquired: ${TOKEN:0:8}..."
```

<a id="tools-required"></a>

## 2.4 Required Tools

| Tool | Purpose | Install Check |
|------|---------|---------------|
| `curl` | REST API calls | `curl --version` |
| `jq` | JSON parsing | `jq --version` |
| `openssl` | Certificate inspection | `openssl version` |
| `ssh` | Remote node access | `ssh -V` |
| `python3` | Scripting and JSON parsing | `python3 --version` |
| `ntpq` / `chronyc` | NTP verification | `ntpq -V` or `chronyc --version` |
| `dig` / `nslookup` | DNS resolution testing | `dig -v` |

<div class="page-break"></div>

<a id="quick-reference"></a>

# 3. Quick Reference Summary Table

This table provides a single-glance view of every health check in this handbook, with pass/warn/fail criteria.

| # | Check | Command / Method | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|---|-------|-----------------|------|------|------|
| 4.1 | Log Insight Daemon | `systemctl status loginsight` | `active (running)` | Restarting frequently | `inactive` / `failed` |
| 4.2 | Cassandra Service | `systemctl status cassandra` | `active (running)` | High compaction pending | `inactive` / `failed` |
| 4.3 | Apache HTTPD | `systemctl status httpd` | `active (running)` | High connection count | `inactive` / `failed` |
| 4.4 | Fluentd | `systemctl status fluentd` | `active (running)` | Buffer warnings | `inactive` / `failed` |
| 5.1 | Node Roles | `GET /api/v1/cluster` | All nodes present | Node degraded | Node missing |
| 5.2 | Cluster Status | `GET /api/v1/cluster/status` | All nodes `RUNNING` | Node in `JOINING` | Node `OFFLINE` |
| 5.3 | ILB VIP | `curl -sk https://<VIP>/` | HTTP 200/302 | High latency (>2s) | Connection refused |
| 6.1 | `/storage/var` Usage | `df -h /storage/var` | < 70% | 70-85% | > 85% |
| 6.2 | Cassandra Data Size | `du -sh /storage/var/cassandra` | < 60% of disk | 60-80% | > 80% |
| 7.1 | Ingestion Rate | `GET /api/v1/stats` | Stable EPS | > 20% deviation | Ingestion stopped |
| 7.2 | Dropped Events | Log analysis | 0 dropped | < 0.1% dropped | > 0.1% dropped |
| 8.1 | Forwarding Status | `GET /api/v1/forwarding` | All destinations up | Intermittent failures | Destination unreachable |
| 9.1 | Content Packs | `GET /api/v1/content/contentpack/list` | All current version | Updates available | Pack errors |
| 10.1 | Ops Integration | Launch-in-context test | Works correctly | Partial function | Not configured |
| 11.1 | Agent Count | `GET /api/v1/agent/groups` | All agents connected | > 5% stale | > 20% stale |
| 12.1 | API Auth | `POST /api/v1/sessions` | Token returned < 2s | Token returned 2-5s | Auth failure |
| 13.1 | SSL Certificate | `openssl s_client` | Valid > 30 days | Valid 7-30 days | Expired / < 7 days |
| 14.1 | NTP Sync | `chronyc tracking` | Offset < 100ms | Offset 100ms-500ms | Offset > 500ms / unsync |
| 14.2 | DNS Resolution | `dig <FQDN>` | Resolves correctly | Slow resolution (>1s) | Resolution fails |
| 15.1 | Backup Status | Backup config check | Recent backup exists | Backup > 7 days old | No backup configured |
| 16.1 | CPU Utilization | `top` / `mpstat` | < 70% sustained | 70-90% sustained | > 90% sustained |
| 16.2 | Memory Usage | `free -m` | < 80% used | 80-90% used | > 90% used |
| 16.3 | JVM Heap | JMX / log analysis | < 75% heap | 75-90% heap | > 90% heap / OOM |

<div class="page-break"></div>

<a id="service-status"></a>

# 4. Service Status

All Ops for Logs nodes run a set of critical services. Each must be verified on **every node** in the cluster. Execute the following checks via SSH to each node.

<a id="loginsight-daemon"></a>

## 4.1 Log Insight Daemon

The `loginsight` daemon is the core process responsible for log ingestion, indexing, querying, and the web UI.

#### CLI Check

```bash
# Check loginsight service status on each node
ssh root@${OFL_NODE1} "systemctl status loginsight"
```

**Expected output (healthy):**

```
● loginsight.service - VMware Aria Operations for Logs
     Loaded: loaded (/etc/systemd/system/loginsight.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-03-20 08:15:22 UTC; 6 days ago
   Main PID: 1842 (loginsight)
      Tasks: 187 (limit: 37253)
     Memory: 4.2G
        CPU: 2d 5h 32min 14.221s
     CGroup: /system.slice/loginsight.service
             └─1842 /usr/lib/loginsight/application/sbin/loginsight ...
```

#### Uptime and Restart Count Check

```bash
# Check for recent restarts (indicates instability)
ssh root@${OFL_NODE1} "journalctl -u loginsight --since '7 days ago' | grep -c 'Started VMware'"
```

**Expected:** `1` (single start in the past 7 days). Values greater than 2 indicate restarts that should be investigated.

#### Process-Level Verification

```bash
# Verify the process is running and check resource consumption
ssh root@${OFL_NODE1} "ps aux | grep loginsight | grep -v grep"
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Service state | `active (running)` | Restarted > 2 times in 7 days | `inactive`, `failed`, or not found |
| Memory usage | < 80% of allocated | 80-90% of allocated | > 90% or OOM killed |
| Process PID | Stable (same PID for days) | Changed in last 24h | Process not found |

<div class="fix-box">
<strong>Remediation:</strong> If the loginsight daemon is not running:<br>
1. Check logs: <code>journalctl -u loginsight --no-pager -n 100</code><br>
2. Check application log: <code>tail -200 /storage/var/loginsight/runtime.log</code><br>
3. Restart the service: <code>systemctl restart loginsight</code><br>
4. If the service fails repeatedly, check disk space on <code>/storage/var</code> and Cassandra health.
</div>

<a id="cassandra-service"></a>

## 4.2 Cassandra Service

Cassandra is the embedded database that stores log metadata, indexes, and cluster state. Its health is critical to overall Ops for Logs function.

#### CLI Check

```bash
# Check Cassandra service status
ssh root@${OFL_NODE1} "systemctl status cassandra"
```

**Expected output (healthy):**

```
● cassandra.service - VMware Ops for Logs Cassandra
     Loaded: loaded (/etc/systemd/system/cassandra.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-03-20 08:14:55 UTC; 6 days ago
   Main PID: 1523 (java)
      Tasks: 94 (limit: 37253)
     Memory: 2.8G
        CPU: 1d 12h 45min 33.109s
     CGroup: /system.slice/cassandra.service
             └─1523 /usr/bin/java -Xms2048m -Xmx2048m ...
```

#### Cassandra Node Status (nodetool)

```bash
# Check Cassandra ring status
ssh root@${OFL_NODE1} "nodetool status"
```

**Expected output:**

```
Datacenter: datacenter1
=======================
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
--  Address        Load       Tokens  Owns    Host ID                               Rack
UN  192.168.1.101  12.45 GiB  256     33.3%   a1b2c3d4-e5f6-7890-abcd-ef0123456789  rack1
UN  192.168.1.102  11.82 GiB  256     33.3%   b2c3d4e5-f6a7-8901-bcde-f01234567890  rack1
UN  192.168.1.103  12.01 GiB  256     33.4%   c3d4e5f6-a7b8-9012-cdef-012345678901  rack1
```

The `UN` prefix means **Up** and **Normal**. Any other state requires investigation.

#### Compaction Check

```bash
# Check pending compactions
ssh root@${OFL_NODE1} "nodetool compactionstats"
```

**Expected:** `pending tasks: 0` or a small number (< 10). High pending compactions (> 50) indicate storage I/O pressure.

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Service state | `active (running)` | Frequent GC pauses | `inactive` / `failed` |
| nodetool status | All nodes `UN` | Node in `UJ` (joining) | Node `DN` (down) |
| Pending compactions | 0 - 10 | 10 - 50 | > 50 |
| Data load balance | Within 10% across nodes | 10-25% variance | > 25% variance |

<div class="fix-box">
<strong>Remediation:</strong> If Cassandra is down or degraded:<br>
1. Check Cassandra logs: <code>tail -200 /storage/var/cassandra/logs/system.log</code><br>
2. Check for heap issues: <code>grep -i "OutOfMemoryError" /storage/var/cassandra/logs/system.log</code><br>
3. Restart Cassandra: <code>systemctl restart cassandra</code><br>
4. If a node shows <code>DN</code>, check network connectivity between nodes and verify <code>/storage/var</code> has free space.<br>
5. For high compaction backlog, avoid restarting -- allow compaction to complete. Consider increasing compaction throughput: <code>nodetool setcompactionthroughput 128</code>
</div>

<a id="apache-service"></a>

## 4.3 Apache / HTTPD Service

Apache serves as the reverse proxy for the Ops for Logs web UI and REST API over HTTPS (port 443).

#### CLI Check

```bash
# Check Apache HTTPD status
ssh root@${OFL_NODE1} "systemctl status httpd"
```

**Expected output (healthy):**

```
● httpd.service - The Apache HTTP Server
     Loaded: loaded (/usr/lib/systemd/system/httpd.service; enabled; vendor preset: disabled)
     Active: active (running) since Mon 2026-03-20 08:15:30 UTC; 6 days ago
       Docs: man:httpd.service(8)
   Main PID: 2103 (httpd)
     Status: "Total requests: 48231; Idle/Busy workers 8/2"
      Tasks: 213 (limit: 37253)
     Memory: 345.2M
```

#### Connection Count

```bash
# Check active connections to port 443
ssh root@${OFL_NODE1} "ss -tuln | grep ':443' && ss -s"
```

#### Apache Error Log

```bash
# Check for recent errors
ssh root@${OFL_NODE1} "tail -50 /var/log/httpd/error_log | grep -i 'error\|warn'"
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Service state | `active (running)` | High worker utilization (> 80%) | `inactive` / `failed` |
| Port 443 listening | Yes | -- | Not listening |
| Error log | No critical errors | Occasional warnings | Persistent errors |

<div class="fix-box">
<strong>Remediation:</strong> If Apache is down:<br>
1. Check config syntax: <code>httpd -t</code><br>
2. Check error log: <code>tail -100 /var/log/httpd/error_log</code><br>
3. Verify SSL certificate files exist and are readable<br>
4. Restart: <code>systemctl restart httpd</code>
</div>

<a id="fluentd-service"></a>

## 4.4 Fluentd Service

Fluentd handles local log collection and forwarding on each node.

#### CLI Check

```bash
# Check Fluentd service status
ssh root@${OFL_NODE1} "systemctl status fluentd"
```

**Expected output (healthy):**

```
● fluentd.service - Fluentd Log Collector
     Loaded: loaded (/etc/systemd/system/fluentd.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2026-03-20 08:15:25 UTC; 6 days ago
   Main PID: 1955 (ruby)
      Tasks: 18 (limit: 37253)
     Memory: 128.5M
```

#### Buffer Health

```bash
# Check Fluentd buffer directory size
ssh root@${OFL_NODE1} "du -sh /storage/var/fluentd/buffer/ 2>/dev/null || echo 'No buffer directory'"

# Check for buffer overflow warnings in Fluentd logs
ssh root@${OFL_NODE1} "grep -c 'buffer is full' /var/log/fluentd/fluentd.log 2>/dev/null || echo '0'"
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Service state | `active (running)` | Buffer warnings present | `inactive` / `failed` |
| Buffer size | < 100 MB | 100 MB - 500 MB | > 500 MB (backlog) |
| Buffer overflow events | 0 | 1-5 in past 24h | > 5 in past 24h |

<div class="fix-box">
<strong>Remediation:</strong> If Fluentd has buffer issues:<br>
1. Check log: <code>tail -100 /var/log/fluentd/fluentd.log</code><br>
2. Clear stale buffers (if safe): <code>rm -f /storage/var/fluentd/buffer/*.log</code><br>
3. Restart: <code>systemctl restart fluentd</code><br>
4. Investigate downstream destination availability if buffers are growing.
</div>

<a id="all-services-summary"></a>

## 4.5 All Services Summary Check

Run this consolidated command on each node to verify all critical services in a single pass:

```bash
# Quick service health summary for a single node
ssh root@${OFL_NODE1} 'echo "=== Service Status Summary ===" && \
  for svc in loginsight cassandra httpd fluentd; do \
    STATUS=$(systemctl is-active $svc 2>/dev/null); \
    ENABLED=$(systemctl is-enabled $svc 2>/dev/null); \
    printf "%-15s Active: %-12s Enabled: %s\n" "$svc" "$STATUS" "$ENABLED"; \
  done'
```

**Expected output:**

```
=== Service Status Summary ===
loginsight      Active: active       Enabled: enabled
cassandra       Active: active       Enabled: enabled
httpd           Active: active       Enabled: enabled
fluentd         Active: active       Enabled: enabled
```

#### Check All Nodes at Once

```bash
# Loop across all cluster nodes
for NODE in ${OFL_NODE1} ${OFL_NODE2} ${OFL_NODE3}; do
  echo "===== ${NODE} ====="
  ssh root@${NODE} 'for svc in loginsight cassandra httpd fluentd; do \
    printf "%-15s %s\n" "$svc" "$(systemctl is-active $svc)"; done'
  echo ""
done
```

<div class="page-break"></div>

<a id="cluster-health"></a>

# 5. Cluster Health

VCF Operations for Logs operates as a clustered appliance with a minimum of three nodes for high availability. Cluster health verification ensures that all nodes are online, roles are correctly assigned, and the integrated load balancer is distributing traffic.

<a id="node-roles"></a>

## 5.1 Node Roles (Master / Worker)

Each Ops for Logs cluster has exactly one **master** node and one or more **worker** nodes. The master manages cluster coordination, schema, and configuration replication.

#### API Check

```bash
# Retrieve cluster node roles
curl -sk -X GET "${OFL_API}/cluster" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "clusterSize": 3,
  "nodes": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
      "hostname": "ops-for-logs-node1.vcf.local",
      "ipAddress": "192.168.1.101",
      "role": "MASTER",
      "status": "RUNNING",
      "version": "9.0.0-12345678"
    },
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f01234567890",
      "hostname": "ops-for-logs-node2.vcf.local",
      "ipAddress": "192.168.1.102",
      "role": "WORKER",
      "status": "RUNNING",
      "version": "9.0.0-12345678"
    },
    {
      "id": "c3d4e5f6-a7b8-9012-cdef-012345678901",
      "hostname": "ops-for-logs-node3.vcf.local",
      "ipAddress": "192.168.1.103",
      "role": "WORKER",
      "status": "RUNNING",
      "version": "9.0.0-12345678"
    }
  ]
}
```

#### Validation Criteria

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Master node present | Exactly 1 master | -- | 0 or > 1 master |
| All nodes reporting | Count matches `clusterSize` | -- | Missing node(s) |
| Version consistency | All nodes same version | -- | Version mismatch |
| All nodes RUNNING | All status = `RUNNING` | Node in `JOINING`/`LEAVING` | Node `OFFLINE`/`ERROR` |

<div class="fix-box">
<strong>Remediation:</strong> If a node is missing or offline:<br>
1. SSH to the affected node and check <code>systemctl status loginsight</code><br>
2. Check network connectivity: <code>ping ${OFL_NODE1}</code> from other nodes<br>
3. Verify the node can reach the master on port 9000: <code>curl -sk https://${OFL_NODE1}:9000</code><br>
4. Review cluster join logs: <code>tail -200 /storage/var/loginsight/runtime.log | grep -i cluster</code><br>
5. If a node is stuck in JOINING, it may need to be removed and re-added via the admin UI.
</div>

<a id="cluster-api"></a>

## 5.2 Cluster Status via API

#### Detailed Cluster Status

```bash
# Get detailed cluster health
curl -sk -X GET "${OFL_API}/cluster/status" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "clusterStatus": "RUNNING",
  "masterNodeId": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
  "nodesHealth": [
    {
      "nodeId": "a1b2c3d4-e5f6-7890-abcd-ef0123456789",
      "hostname": "ops-for-logs-node1.vcf.local",
      "state": "RUNNING",
      "diskUsagePercent": 42.5,
      "cpuUsagePercent": 23.1,
      "memoryUsagePercent": 65.8,
      "eventsPerSecond": 3245
    },
    {
      "nodeId": "b2c3d4e5-f6a7-8901-bcde-f01234567890",
      "hostname": "ops-for-logs-node2.vcf.local",
      "state": "RUNNING",
      "diskUsagePercent": 41.2,
      "cpuUsagePercent": 21.8,
      "memoryUsagePercent": 63.4,
      "eventsPerSecond": 3198
    },
    {
      "nodeId": "c3d4e5f6-a7b8-9012-cdef-012345678901",
      "hostname": "ops-for-logs-node3.vcf.local",
      "state": "RUNNING",
      "diskUsagePercent": 43.1,
      "cpuUsagePercent": 22.5,
      "memoryUsagePercent": 64.2,
      "eventsPerSecond": 3210
    }
  ]
}
```

<a id="ilb-status"></a>

## 5.3 Integrated Load Balancer (ILB)

The ILB provides a single virtual IP (VIP) that distributes incoming log traffic and API requests across all cluster nodes.

#### VIP Reachability

```bash
# Test VIP is responding
curl -sk -o /dev/null -w "HTTP_CODE: %{http_code}\nTIME_TOTAL: %{time_total}s\n" \
  "https://${OFL_HOST}/"
```

**Expected output:**

```
HTTP_CODE: 302
TIME_TOTAL: 0.234s
```

#### ILB Configuration via API

```bash
# Check ILB configuration
curl -sk -X GET "${OFL_API}/ilb" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "enabled": true,
  "virtualIp": "192.168.1.100",
  "heartbeatInterval": 3,
  "failoverTimeout": 15
}
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| VIP responds | HTTP 200 or 302 | Response time > 2s | Connection refused / timeout |
| ILB enabled | `true` | -- | `false` |
| All nodes behind ILB | All nodes included | -- | Node excluded |

<div class="fix-box">
<strong>Remediation:</strong> If the VIP is unreachable:<br>
1. Check if the VIP is bound to a node: <code>ssh root@${OFL_NODE1} "ip addr show | grep 192.168.1.100"</code><br>
2. Verify ILB is enabled in the admin UI under <strong>Administration > Cluster > ILB</strong><br>
3. Check for IP conflicts with <code>arping -D -I eth0 192.168.1.100</code><br>
4. Restart ILB by restarting the loginsight service on the master node.
</div>

<a id="node-connectivity"></a>

## 5.4 Node-to-Node Connectivity

All cluster nodes must be able to communicate with each other on required ports.

```bash
# Test connectivity from node1 to node2 and node3 on key ports
ssh root@${OFL_NODE1} "
  echo '--- Port 9000 (loginsight) ---'
  nc -zv ${OFL_NODE2} 9000 2>&1
  nc -zv ${OFL_NODE3} 9000 2>&1
  echo '--- Port 9042 (Cassandra CQL) ---'
  nc -zv ${OFL_NODE2} 9042 2>&1
  nc -zv ${OFL_NODE3} 9042 2>&1
  echo '--- Port 7000 (Cassandra inter-node) ---'
  nc -zv ${OFL_NODE2} 7000 2>&1
  nc -zv ${OFL_NODE3} 7000 2>&1
"
```

**Expected output:**

```
--- Port 9000 (loginsight) ---
Connection to ops-for-logs-node2.vcf.local 9000 port [tcp/*] succeeded!
Connection to ops-for-logs-node3.vcf.local 9000 port [tcp/*] succeeded!
--- Port 9042 (Cassandra CQL) ---
Connection to ops-for-logs-node2.vcf.local 9042 port [tcp/*] succeeded!
Connection to ops-for-logs-node3.vcf.local 9042 port [tcp/*] succeeded!
--- Port 7000 (Cassandra inter-node) ---
Connection to ops-for-logs-node2.vcf.local 7000 port [tcp/*] succeeded!
Connection to ops-for-logs-node3.vcf.local 7000 port [tcp/*] succeeded!
```

<div class="page-break"></div>

<a id="disk-storage"></a>

# 6. Disk & Storage Health

Storage is the most common source of Ops for Logs issues. The appliance stores all ingested log data, Cassandra metadata, and indexes on the `/storage/var` partition.

<a id="partition-layout"></a>

## 6.1 Storage Partition Layout

#### Check Disk Layout

```bash
# Show all mounted partitions and usage
ssh root@${OFL_NODE1} "df -hT"
```

**Expected output:**

```
Filesystem     Type      Size  Used Avail Use% Mounted on
/dev/sda3      ext4       10G  3.2G  6.3G  34% /
/dev/sda1      vfat      512M   12M  500M   3% /boot/efi
/dev/sdb1      ext4      500G  210G  266G  45% /storage/var
tmpfs          tmpfs     7.8G     0  7.8G   0% /dev/shm
```

The critical partitions are:

| Partition | Purpose | Minimum Size | Alert Threshold |
|-----------|---------|-------------|-----------------|
| `/` | OS root filesystem | 10 GB | > 80% used |
| `/storage/var` | Log data, Cassandra, indexes | 500 GB+ | > 70% used |
| `/boot/efi` | EFI boot partition | 512 MB | > 90% used |

<a id="storage-usage"></a>

## 6.2 Storage Usage Thresholds

#### Detailed Storage Check

```bash
# Check /storage/var utilization with breakdown
ssh root@${OFL_NODE1} "
  echo '=== Overall /storage/var ==='
  df -h /storage/var
  echo ''
  echo '=== Top-level directories by size ==='
  du -sh /storage/var/*/ 2>/dev/null | sort -rh | head -20
"
```

**Expected output:**

```
=== Overall /storage/var ===
Filesystem      Size  Used Avail Use% Mounted on
/dev/sdb1       500G  210G  266G  45% /storage/var

=== Top-level directories by size ===
185G    /storage/var/loginsight/
18G     /storage/var/cassandra/
3.2G    /storage/var/fluentd/
1.1G    /storage/var/apache/
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| `/storage/var` usage | < 70% | 70-85% | > 85% |
| Root `/` usage | < 80% | 80-90% | > 90% |
| Inode usage | < 70% | 70-85% | > 85% |

#### Inode Check

```bash
# Check inode usage (often overlooked)
ssh root@${OFL_NODE1} "df -i /storage/var"
```

<div class="warn-box">
<strong>Warning:</strong> When <code>/storage/var</code> exceeds 85%, Ops for Logs will begin aggressively purging old data. At 95%, ingestion may halt entirely. Proactive monitoring is essential.
</div>

<a id="cassandra-data"></a>

## 6.3 Cassandra Data Size

```bash
# Check Cassandra data footprint
ssh root@${OFL_NODE1} "
  echo '=== Cassandra Data Directory ==='
  du -sh /storage/var/cassandra/data/ 2>/dev/null
  echo ''
  echo '=== Cassandra Commit Logs ==='
  du -sh /storage/var/cassandra/commitlog/ 2>/dev/null
  echo ''
  echo '=== Cassandra Saved Caches ==='
  du -sh /storage/var/cassandra/saved_caches/ 2>/dev/null
"
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Data directory | < 60% of `/storage/var` | 60-80% | > 80% |
| Commit log size | < 2 GB | 2-5 GB | > 5 GB (indicates write issues) |

<a id="retention-policy"></a>

## 6.4 Retention Policy

#### Check Retention Configuration via API

```bash
# Get retention settings
curl -sk -X GET "${OFL_API}/time/config" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "retentionPeriod": 30,
  "archiveEnabled": true,
  "archiveRetentionPeriod": 365
}
```

#### Check Retention via CLI

```bash
# Check the loginsight configuration file for retention settings
ssh root@${OFL_NODE1} "grep -i 'retention' /storage/var/loginsight/config/loginsight-config.xml 2>/dev/null"
```

<a id="archive-config"></a>

## 6.5 Archive Configuration

```bash
# Check archive/NFS configuration
curl -sk -X GET "${OFL_API}/archive" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response (when configured):**

```json
{
  "enabled": true,
  "archiveType": "NFS",
  "nfsServer": "nfs-server.vcf.local",
  "nfsPath": "/exports/loginsight-archive",
  "archiveFrequency": "DAILY",
  "compressionEnabled": true
}
```

#### Verify Archive Mount

```bash
# Check if NFS archive is mounted
ssh root@${OFL_NODE1} "mount | grep nfs && df -h /storage/var/loginsight/archive/"
```

<div class="fix-box">
<strong>Remediation:</strong> If storage is critically low:<br>
1. Reduce retention period via API: reduce <code>retentionPeriod</code> value<br>
2. Enable archiving to offload old data to NFS<br>
3. Expand the <code>/storage/var</code> virtual disk in vSphere and grow the filesystem<br>
4. Check for and remove stale Cassandra snapshots: <code>nodetool clearsnapshot</code>
</div>

<div class="page-break"></div>

<a id="ingestion-rate"></a>

# 7. Ingestion Rate Monitoring

The ingestion rate (events per second, or EPS) is a key performance indicator for Ops for Logs. Monitoring this metric ensures that the platform is receiving logs at expected volumes and not silently dropping events.

<a id="events-per-second"></a>

## 7.1 Events Per Second

#### API Check

```bash
# Get current ingestion statistics
curl -sk -X GET "${OFL_API}/stats" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "totalEventsIngested": 285432109,
  "currentEventsPerSecond": 9653,
  "averageEventsPerSecond": 9480,
  "peakEventsPerSecond": 18234,
  "totalBytesIngested": 412983726501,
  "droppedEvents": 0,
  "queueDepth": 12
}
```

#### CLI-Based Ingestion Monitoring

```bash
# Monitor real-time ingestion rate from node logs
ssh root@${OFL_NODE1} "tail -100 /storage/var/loginsight/runtime.log | grep -i 'ingestion\|eps\|events.*second'"
```

#### Historical Ingestion Query

```bash
# Query ingestion rate over the past 24 hours
curl -sk -X POST "${OFL_API}/events/stats" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ingestion_rate",
    "startTimeMillis": '$(date -d "24 hours ago" +%s%3N)',
    "endTimeMillis": '$(date +%s%3N)',
    "bucketDurationMinutes": 60
  }' | jq '.buckets[] | {time: .startTime, eps: .eventsPerSecond}'
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Current EPS | Within 20% of baseline | 20-50% deviation from baseline | > 50% deviation or 0 EPS |
| Dropped events | 0 | < 0.1% of total ingested | > 0.1% of total |
| Queue depth | < 100 | 100-1000 | > 1000 |

<a id="ingestion-pipeline"></a>

## 7.2 Ingestion Pipeline Health

```bash
# Check ingestion pipeline components
ssh root@${OFL_NODE1} "
  echo '=== Listening Ports for Ingestion ==='
  ss -tuln | grep -E ':(514|1514|6514|9000|9543) '
  echo ''
  echo '=== Active Syslog Connections ==='
  ss -tn | grep -E ':(514|1514|6514) ' | wc -l
  echo ''
  echo '=== Active CFAPI Connections ==='
  ss -tn | grep -E ':(9000|9543) ' | wc -l
"
```

**Expected output:**

```
=== Listening Ports for Ingestion ===
tcp   LISTEN  0  128  *:514    *:*
tcp   LISTEN  0  128  *:1514   *:*
tcp   LISTEN  0  128  *:6514   *:*
tcp   LISTEN  0  128  *:9000   *:*
tcp   LISTEN  0  128  *:9543   *:*

=== Active Syslog Connections ===
42

=== Active CFAPI Connections ===
18
```

<a id="dropped-events"></a>

## 7.3 Dropped Events & Queue Depth

```bash
# Check for dropped events in the runtime log
ssh root@${OFL_NODE1} "grep -c 'dropped\|overflow\|backpressure' \
  /storage/var/loginsight/runtime.log 2>/dev/null || echo '0'"

# Check ingestion queue depth
ssh root@${OFL_NODE1} "grep -i 'queue.*depth\|pending.*events' \
  /storage/var/loginsight/runtime.log | tail -5"
```

<div class="fix-box">
<strong>Remediation:</strong> If ingestion is dropping events:<br>
1. Check disk space -- full storage is the most common cause<br>
2. Review Cassandra health -- Cassandra write failures block ingestion<br>
3. Check for network saturation on ingestion ports<br>
4. Scale out by adding worker nodes if sustained EPS exceeds capacity<br>
5. Review forwarding destinations -- slow downstream targets can cause backpressure
</div>

<div class="page-break"></div>

<a id="log-forwarding"></a>

# 8. Log Forwarding Configuration

Ops for Logs can forward ingested logs to external destinations via syslog (UDP/TCP), syslog over TLS, or the CFAPI protocol. This section verifies that all forwarding destinations are configured correctly and operating.

<a id="forwarding-destinations"></a>

## 8.1 Forwarding Destinations

#### API Check

```bash
# List all configured forwarding destinations
curl -sk -X GET "${OFL_API}/forwarding" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "destinations": [
    {
      "id": "dest-001",
      "name": "SIEM-Primary",
      "host": "siem.vcf.local",
      "port": 6514,
      "protocol": "SYSLOG",
      "transport": "TCP-TLS",
      "enabled": true,
      "status": "CONNECTED",
      "filter": "*",
      "lastEventForwarded": "2026-03-26T09:45:12Z"
    },
    {
      "id": "dest-002",
      "name": "Archive-Collector",
      "host": "log-archive.vcf.local",
      "port": 9543,
      "protocol": "CFAPI",
      "transport": "HTTPS",
      "enabled": true,
      "status": "CONNECTED",
      "filter": "vmw_vc_*",
      "lastEventForwarded": "2026-03-26T09:45:10Z"
    }
  ]
}
```

<a id="forwarding-protocols"></a>

## 8.2 Protocol & TLS Configuration

#### Verify TLS Configuration for Syslog Forwarding

```bash
# Check TLS certificate used for syslog forwarding
ssh root@${OFL_NODE1} "
  echo '=== Forwarding TLS Certificates ==='
  ls -la /storage/var/loginsight/certs/forwarding/ 2>/dev/null || echo 'No forwarding certs directory'
  echo ''
  echo '=== Forwarding Configuration ==='
  grep -A 10 'forwarding' /storage/var/loginsight/config/loginsight-config.xml 2>/dev/null | head -30
"
```

#### Test TLS Connectivity to Forwarding Destination

```bash
# Verify TLS handshake to syslog destination
openssl s_client -connect siem.vcf.local:6514 -servername siem.vcf.local </dev/null 2>/dev/null | \
  openssl x509 -noout -subject -dates -issuer
```

**Expected output:**

```
subject=CN = siem.vcf.local
notBefore=Jan 15 00:00:00 2026 GMT
notAfter=Jan 15 23:59:59 2027 GMT
issuer=CN = VCF Internal CA, O = Virtual Control LLC
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| TLS handshake | Succeeds | Certificate nearing expiry | Handshake fails |
| Protocol match | Matches destination config | -- | Mismatch |
| Certificate trust | CA chain trusted | Self-signed (intentional) | Untrusted / expired |

<a id="forwarding-health"></a>

## 8.3 Forwarding Health Verification

```bash
# Check forwarding statistics per destination
curl -sk -X GET "${OFL_API}/forwarding/stats" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.destinations[] | {name, eventsForwarded, eventsFailed, lastSuccess}'
```

**Expected output:**

```json
{
  "name": "SIEM-Primary",
  "eventsForwarded": 48293012,
  "eventsFailed": 0,
  "lastSuccess": "2026-03-26T09:45:12Z"
}
{
  "name": "Archive-Collector",
  "eventsForwarded": 12045231,
  "eventsFailed": 0,
  "lastSuccess": "2026-03-26T09:45:10Z"
}
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Events forwarded | Increasing steadily | Intermittent pauses | Not increasing / 0 |
| Events failed | 0 | < 0.01% of forwarded | > 0.01% or increasing |
| Last success | Within 5 minutes | 5-60 minutes ago | > 60 minutes ago |
| Destination status | `CONNECTED` | `RECONNECTING` | `DISCONNECTED` / `ERROR` |

<a id="test-forwarding"></a>

## 8.4 Test Forwarding

```bash
# Send a test event via the API to verify end-to-end forwarding
curl -sk -X POST "${OFL_API}/events/ingest/0" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "text": "HEALTH_CHECK_TEST: Forwarding validation event from Ops for Logs health check - '"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",
        "source": "health-check-script",
        "fields": [
          {"name": "test_id", "content": "hc-fwd-'"$(date +%s)"'"}
        ]
      }
    ]
  }'
```

Then verify the test event arrived at the forwarding destination by searching for `HEALTH_CHECK_TEST` in the target SIEM or log collector.

<div class="fix-box">
<strong>Remediation:</strong> If forwarding is failing:<br>
1. Verify destination reachability: <code>nc -zv siem.vcf.local 6514</code><br>
2. Check firewall rules between Ops for Logs nodes and the destination<br>
3. Verify TLS certificate compatibility -- the destination must trust the Ops for Logs CA<br>
4. Restart forwarding by toggling the destination off and on via the UI<br>
5. Check destination-side logs for connection rejections
</div>

<div class="page-break"></div>

<a id="content-packs"></a>

# 9. Content Packs

Content packs provide pre-built dashboards, alerts, extracted fields, and queries for specific products (vSphere, NSX, SDDC Manager, vSAN, etc.). Keeping content packs current ensures full observability.

<a id="installed-packs"></a>

## 9.1 Installed Content Packs

#### API Check

```bash
# List all installed content packs
curl -sk -X GET "${OFL_API}/content/contentpack/list" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.contentPacks[] | {name, namespace, version, installedDate}'
```

**Expected output:**

```json
{
  "name": "VMware vSphere",
  "namespace": "com.vmware.vsphere",
  "version": "9.0.1",
  "installedDate": "2026-02-15T10:30:00Z"
}
{
  "name": "VMware NSX",
  "namespace": "com.vmware.nsx",
  "version": "9.0.0",
  "installedDate": "2026-02-15T10:30:05Z"
}
{
  "name": "VMware SDDC Manager",
  "namespace": "com.vmware.sddc",
  "version": "9.0.0",
  "installedDate": "2026-02-15T10:30:10Z"
}
{
  "name": "VMware vSAN",
  "namespace": "com.vmware.vsan",
  "version": "9.0.0",
  "installedDate": "2026-02-15T10:30:15Z"
}
{
  "name": "VMware Aria Operations",
  "namespace": "com.vmware.vrops",
  "version": "9.0.0",
  "installedDate": "2026-02-15T10:30:20Z"
}
```

#### Essential Content Packs for VCF 9

| Content Pack | Namespace | Minimum Version | Purpose |
|-------------|-----------|----------------|---------|
| VMware vSphere | `com.vmware.vsphere` | 9.0.0 | ESXi and vCenter log parsing |
| VMware NSX | `com.vmware.nsx` | 9.0.0 | NSX manager and edge log parsing |
| VMware SDDC Manager | `com.vmware.sddc` | 9.0.0 | SDDC Manager lifecycle events |
| VMware vSAN | `com.vmware.vsan` | 9.0.0 | vSAN health and performance logs |
| VMware Aria Operations | `com.vmware.vrops` | 9.0.0 | Ops manager integration logs |
| Linux | `com.vmware.linux` | 9.0.0 | General Linux syslog parsing |
| General | `com.vmware.general` | 9.0.0 | Generic field extraction |

<a id="pack-versions"></a>

## 9.2 Version Status & Updates

#### Check for Available Updates

```bash
# Check marketplace for content pack updates
curl -sk -X GET "${OFL_API}/content/contentpack/marketplace" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.contentPacks[] | select(.updateAvailable == true) | {name, currentVersion, availableVersion}'
```

**Expected output (no updates needed):**

```
(empty output -- no updates available)
```

**Output when updates are available:**

```json
{
  "name": "VMware vSphere",
  "currentVersion": "9.0.0",
  "availableVersion": "9.0.1"
}
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| All VCF packs installed | All 7+ packs present | Missing non-critical pack | Missing vSphere or SDDC pack |
| Pack versions | All at latest | Minor update available | Major version behind |
| Pack status | No errors | Warning on extraction | Pack failed to load |

<a id="auto-update"></a>

## 9.3 Auto-Update Configuration

```bash
# Check auto-update settings for content packs
curl -sk -X GET "${OFL_API}/content/contentpack/autoupdate" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "autoUpdateEnabled": true,
  "checkIntervalHours": 24,
  "lastCheckTime": "2026-03-25T02:00:00Z",
  "proxyEnabled": false
}
```

<div class="fix-box">
<strong>Remediation:</strong> If content packs are outdated or missing:<br>
1. Update individual pack: Navigate to <strong>Content Packs</strong> in the UI, select the pack, click <strong>Update</strong><br>
2. Install missing pack via API: <code>POST /api/v1/content/contentpack/install</code> with the pack namespace<br>
3. If marketplace is unreachable, download packs manually from the VMware Marketplace and upload via UI<br>
4. Enable auto-update: <code>PUT /api/v1/content/contentpack/autoupdate</code> with <code>{"autoUpdateEnabled": true}</code>
</div>

<div class="page-break"></div>

<a id="integration-ops"></a>

# 10. Integration with VCF Operations

VCF Operations for Logs integrates with VCF Operations (formerly Aria Operations / vRealize Operations) to provide launch-in-context capabilities, shared authentication, and correlated alerting.

<a id="launch-in-context"></a>

## 10.1 Launch-in-Context Configuration

Launch-in-context enables users to jump directly from VCF Operations alerts and dashboards into relevant log queries in Ops for Logs.

#### Verify Integration Configuration

```bash
# Check VCF Operations integration settings
curl -sk -X GET "${OFL_API}/integration/vrops" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "enabled": true,
  "vropsHost": "ops.vcf.local",
  "vropsPort": 443,
  "connectionStatus": "CONNECTED",
  "lastSyncTime": "2026-03-26T08:00:00Z",
  "ssoIntegrated": true,
  "launchInContextEnabled": true
}
```

#### Test Launch-in-Context URL Generation

```bash
# Verify launch-in-context URL format
curl -sk -X GET "${OFL_API}/integration/vrops/launch-url?resourceId=vm-123&timeRange=3600" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Integration enabled | `true` | -- | `false` or not configured |
| Connection status | `CONNECTED` | `DEGRADED` | `DISCONNECTED` |
| Last sync time | Within 24 hours | 1-7 days ago | > 7 days or never |
| Launch-in-context | URL generated correctly | Partial functionality | Errors on generation |

<a id="shared-auth"></a>

## 10.2 Shared Authentication

```bash
# Verify SSO / shared authentication with VCF Operations
curl -sk -X GET "${OFL_API}/auth/providers" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "providers": [
    {
      "name": "Local",
      "type": "LOCAL",
      "enabled": true
    },
    {
      "name": "vcf-sso.vcf.local",
      "type": "ACTIVE_DIRECTORY",
      "enabled": true,
      "connectionStatus": "CONNECTED"
    },
    {
      "name": "VMware Identity Manager",
      "type": "VIDM",
      "enabled": true,
      "connectionStatus": "CONNECTED"
    }
  ]
}
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| SSO provider configured | Yes, `CONNECTED` | Configured but `DEGRADED` | Not configured |
| AD integration | `CONNECTED` | Intermittent failures | `DISCONNECTED` |
| Local auth backup | Enabled as fallback | -- | Disabled (no fallback) |

<a id="data-flow"></a>

## 10.3 Data Flow Verification

Verify that VCF Operations is sending notification events and that Ops for Logs is receiving them.

```bash
# Search for VCF Operations events in Ops for Logs
curl -sk -X POST "${OFL_API}/events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vmw_product=vrops",
    "startTimeMillis": '$(date -d "24 hours ago" +%s%3N)',
    "endTimeMillis": '$(date +%s%3N)',
    "limit": 5
  }' | jq '.results | length'
```

**Expected:** A positive number indicating events are flowing from VCF Operations to Ops for Logs.

<div class="fix-box">
<strong>Remediation:</strong> If integration is broken:<br>
1. Re-register the integration from VCF Operations: <strong>Administration > Management > Log Insight Integration</strong><br>
2. Verify network connectivity: <code>curl -sk https://ops.vcf.local:443</code> from Ops for Logs nodes<br>
3. Check SSO token validity -- re-authenticate if tokens have expired<br>
4. Verify VIDM (Workspace ONE Access) is operational if using VIDM-based SSO<br>
5. Restart the integration service: <code>systemctl restart loginsight</code> (integration is part of the main daemon)
</div>

<div class="page-break"></div>

<a id="agent-status"></a>

# 11. Agent Status

Ops for Logs agents (li-agent) run on ESXi hosts, VMs, and other endpoints to collect and forward logs to the cluster. Agent health monitoring ensures complete log coverage.

<a id="connected-agents"></a>

## 11.1 Connected Agents

#### API Check

```bash
# Get agent summary statistics
curl -sk -X GET "${OFL_API}/agent/stats" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "totalAgents": 48,
  "connectedAgents": 47,
  "disconnectedAgents": 1,
  "activeAgentGroups": 5,
  "averageEventsPerAgent": 201
}
```

#### List All Connected Agents

```bash
# List agents with their connection status
curl -sk -X GET "${OFL_API}/agent/agents" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.agents[] | {hostname, ipAddress, version, status, lastHeartbeat}' | head -60
```

**Sample output:**

```json
{
  "hostname": "esxi-host-01.vcf.local",
  "ipAddress": "192.168.10.101",
  "version": "9.0.0-12345",
  "status": "CONNECTED",
  "lastHeartbeat": "2026-03-26T09:44:55Z"
}
{
  "hostname": "esxi-host-02.vcf.local",
  "ipAddress": "192.168.10.102",
  "version": "9.0.0-12345",
  "status": "CONNECTED",
  "lastHeartbeat": "2026-03-26T09:44:52Z"
}
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Connected agents | 100% connected | 95-99% connected | < 95% connected |
| Agent version | All same version as cluster | Minor version mismatch | Major version mismatch |
| Heartbeat age | < 5 minutes | 5-30 minutes | > 30 minutes |

<a id="agent-groups"></a>

## 11.2 Agent Groups

Agent groups organize agents for targeted log collection and configuration distribution.

```bash
# List all agent groups
curl -sk -X GET "${OFL_API}/agent/groups" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.groups[] | {id, name, agentCount, filter}'
```

**Expected output:**

```json
{
  "id": "group-001",
  "name": "ESXi-Hosts",
  "agentCount": 32,
  "filter": "hostname MATCHES esxi-*"
}
{
  "id": "group-002",
  "name": "VCF-Management-VMs",
  "agentCount": 12,
  "filter": "hostname MATCHES vcf-mgmt-*"
}
{
  "id": "group-003",
  "name": "Windows-Servers",
  "agentCount": 4,
  "filter": "os MATCHES Windows*"
}
```

#### Verify Agent Group Configuration

```bash
# Get detailed agent group configuration including collection targets
curl -sk -X GET "${OFL_API}/agent/groups/group-001" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "id": "group-001",
  "name": "ESXi-Hosts",
  "agentCount": 32,
  "config": {
    "fileLogs": [
      {
        "directory": "/var/log",
        "include": "*.log",
        "parser": "AUTO"
      },
      {
        "directory": "/var/run/log",
        "include": "vmkernel*",
        "parser": "VMW_ESXI"
      }
    ],
    "eventLogs": [],
    "destination": {
      "host": "ops-for-logs.vcf.local",
      "port": 9543,
      "protocol": "CFAPI",
      "ssl": true
    }
  }
}
```

<a id="stale-agents"></a>

## 11.3 Stale Agent Detection

Stale agents are agents that have not sent a heartbeat within the expected interval (typically 5 minutes). They may indicate agent crashes, network issues, or decommissioned hosts.

```bash
# Find agents with no heartbeat in the last 30 minutes
curl -sk -X GET "${OFL_API}/agent/agents?status=DISCONNECTED" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.agents[] | {hostname, lastHeartbeat, status}'
```

**Expected output (ideally empty):**

```json
{
  "hostname": "old-vm-decommissioned.vcf.local",
  "lastHeartbeat": "2026-03-10T14:22:00Z",
  "status": "DISCONNECTED"
}
```

<div class="fix-box">
<strong>Remediation:</strong> For stale/disconnected agents:<br>
1. Verify the host is still operational: <code>ping old-vm-decommissioned.vcf.local</code><br>
2. If the host is active, SSH in and check agent status: <code>systemctl status liagentd</code><br>
3. Restart the agent: <code>systemctl restart liagentd</code><br>
4. Check agent logs: <code>tail -100 /var/log/liagent/liagent.log</code><br>
5. For decommissioned hosts, remove the stale agent entry via API: <code>DELETE /api/v1/agent/agents/{agentId}</code><br>
6. Verify agent can reach Ops for Logs on port 9543: <code>nc -zv ops-for-logs.vcf.local 9543</code>
</div>

<div class="page-break"></div>

<a id="api-health"></a>

# 12. API Health

The Ops for Logs REST API is the primary interface for programmatic queries, configuration management, and integration with external tools. Verifying API health ensures automation and integrations function correctly.

<a id="token-acquisition"></a>

## 12.1 Token Acquisition

#### Timed Authentication Test

```bash
# Measure authentication response time
time curl -sk -X POST "${OFL_API}/sessions" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"'"${OFL_PASS}"'","provider":"Local"}' \
  -o /dev/null -w "HTTP_CODE: %{http_code}\nTIME_TOTAL: %{time_total}s\nTIME_CONNECT: %{time_connect}s\n"
```

**Expected output:**

```
HTTP_CODE: 200
TIME_TOTAL: 0.345s
TIME_CONNECT: 0.012s

real    0m0.362s
user    0m0.024s
sys     0m0.012s
```

#### Test Token Validity

```bash
# Verify a token works for an authenticated endpoint
curl -sk -X GET "${OFL_API}/version" \
  -H "Authorization: Bearer ${TOKEN}" \
  -w "\nHTTP_CODE: %{http_code}\n" | jq '.'
```

**Expected response:**

```json
{
  "version": "9.0.0",
  "build": "12345678",
  "releaseName": "VCF Operations for Logs 9.0"
}
HTTP_CODE: 200
```

#### Test Invalid Token Handling

```bash
# Verify that invalid tokens are properly rejected
curl -sk -X GET "${OFL_API}/cluster" \
  -H "Authorization: Bearer INVALID_TOKEN_12345" \
  -w "\nHTTP_CODE: %{http_code}\n"
```

**Expected:** `HTTP_CODE: 401` (Unauthorized).

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Auth response time | < 2 seconds | 2-5 seconds | > 5 seconds or timeout |
| HTTP status | 200 | -- | 401, 403, 500, or connection error |
| Token validity | Token works on subsequent calls | TTL shorter than expected | Token immediately invalid |
| Invalid token rejection | Returns 401 | -- | Returns 200 (security issue) |

<a id="api-responsiveness"></a>

## 12.2 API Responsiveness

Test several key API endpoints for response time under normal load.

```bash
# Benchmark multiple API endpoints
echo "=== API Endpoint Response Times ==="
for ENDPOINT in "version" "cluster" "cluster/status" "stats" "agent/stats" "forwarding"; do
  RESP=$(curl -sk -X GET "${OFL_API}/${ENDPOINT}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -o /dev/null -w "%{http_code} %{time_total}s")
  printf "%-25s %s\n" "${ENDPOINT}" "${RESP}"
done
```

**Expected output:**

```
=== API Endpoint Response Times ===
version                   200 0.089s
cluster                   200 0.156s
cluster/status            200 0.234s
stats                     200 0.312s
agent/stats               200 0.198s
forwarding                200 0.145s
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Average response time | < 1 second | 1-3 seconds | > 3 seconds |
| All endpoints reachable | All return 200 | Some return 503 | Critical endpoints fail |
| Error rate | 0% | < 1% | > 1% |

<a id="rate-limiting"></a>

## 12.3 Rate Limiting

```bash
# Test rate limiting by sending rapid requests
echo "=== Rate Limit Test (20 rapid requests) ==="
for i in $(seq 1 20); do
  CODE=$(curl -sk -X GET "${OFL_API}/version" \
    -H "Authorization: Bearer ${TOKEN}" \
    -o /dev/null -w "%{http_code}")
  echo "Request ${i}: HTTP ${CODE}"
done | sort | uniq -c | sort -rn
```

**Expected output:**

```
     20 Request: HTTP 200
```

If rate limiting is active, you may see `HTTP 429` (Too Many Requests) after a threshold.

<div class="fix-box">
<strong>Remediation:</strong> If the API is slow or unresponsive:<br>
1. Check Apache and loginsight service health (Sections 4.1, 4.3)<br>
2. Verify cluster health -- API calls are proxied to the master node<br>
3. Check CPU and memory utilization on the master node<br>
4. Review <code>/storage/var/loginsight/runtime.log</code> for API error messages<br>
5. Restart Apache: <code>systemctl restart httpd</code><br>
6. As a last resort, restart the loginsight daemon: <code>systemctl restart loginsight</code>
</div>

<div class="page-break"></div>

<a id="certificate-health"></a>

# 13. Certificate Health

SSL/TLS certificates are critical for securing the Ops for Logs web UI, API, agent communication, and log forwarding. Expired or misconfigured certificates cause connection failures across the environment.

<a id="ssl-check"></a>

## 13.1 SSL Certificate Verification

#### Check the Web UI / API Certificate

```bash
# Inspect the SSL certificate served by Ops for Logs
echo | openssl s_client -connect ${OFL_HOST}:443 -servername ${OFL_HOST} 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates -serial -fingerprint -ext subjectAltName
```

**Expected output:**

```
subject=CN = ops-for-logs.vcf.local
issuer=CN = VCF Internal CA, O = Virtual Control LLC, L = Managed
notBefore=Feb  1 00:00:00 2026 GMT
notAfter=Feb  1 23:59:59 2028 GMT
serial=4A3B2C1D0E9F8A7B
SHA256 Fingerprint=AB:CD:EF:12:34:56:78:9A:BC:DE:F0:12:34:56:78:9A:BC:DE:F0:12:34:56:78:9A:BC:DE:F0:12:34:56:78:9A
X509v3 Subject Alternative Name:
    DNS:ops-for-logs.vcf.local, DNS:ops-for-logs-node1.vcf.local, DNS:ops-for-logs-node2.vcf.local, DNS:ops-for-logs-node3.vcf.local, IP Address:192.168.1.100, IP Address:192.168.1.101, IP Address:192.168.1.102, IP Address:192.168.1.103
```

#### Check Certificate on Each Node

```bash
# Verify certificate consistency across all nodes
for NODE in ${OFL_NODE1} ${OFL_NODE2} ${OFL_NODE3}; do
  echo "===== ${NODE} ====="
  echo | openssl s_client -connect ${NODE}:443 -servername ${NODE} 2>/dev/null | \
    openssl x509 -noout -subject -dates -fingerprint
  echo ""
done
```

#### Check Ingestion Port Certificate (9543)

```bash
# Verify the CFAPI ingestion port certificate
echo | openssl s_client -connect ${OFL_HOST}:9543 -servername ${OFL_HOST} 2>/dev/null | \
  openssl x509 -noout -subject -dates
```

<a id="custom-ca"></a>

## 13.2 Custom CA Configuration

```bash
# Check if a custom CA certificate is installed
ssh root@${OFL_NODE1} "
  echo '=== Custom CA Certificates ==='
  ls -la /storage/var/loginsight/certs/ 2>/dev/null
  echo ''
  echo '=== Trust Store Contents ==='
  keytool -list -keystore /storage/var/loginsight/certs/truststore.jks \
    -storepass changeit 2>/dev/null | head -20
"
```

#### Verify Full Certificate Chain

```bash
# Download and verify the full certificate chain
echo | openssl s_client -connect ${OFL_HOST}:443 -showcerts 2>/dev/null | \
  awk '/BEGIN CERTIFICATE/,/END CERTIFICATE/{ print }' > /tmp/ofl_chain.pem

# Verify the chain
openssl verify -verbose /tmp/ofl_chain.pem
```

<a id="cert-expiry"></a>

## 13.3 Certificate Expiry Monitoring

#### Calculate Days Until Expiry

```bash
# Calculate days until certificate expiry
EXPIRY_DATE=$(echo | openssl s_client -connect ${OFL_HOST}:443 -servername ${OFL_HOST} 2>/dev/null | \
  openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "${EXPIRY_DATE}" +%s)
NOW_EPOCH=$(date +%s)
DAYS_REMAINING=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
echo "Certificate expires: ${EXPIRY_DATE}"
echo "Days remaining: ${DAYS_REMAINING}"
```

**Expected output:**

```
Certificate expires: Feb  1 23:59:59 2028 GMT
Days remaining: 677
```

#### Check All Ports for Expiry

```bash
# Check certificate expiry on all service ports
echo "=== Certificate Expiry by Port ==="
for PORT in 443 9000 9543; do
  EXPIRY=$(echo | openssl s_client -connect ${OFL_HOST}:${PORT} 2>/dev/null | \
    openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
  printf "Port %-6s Expires: %s\n" "${PORT}" "${EXPIRY:-N/A}"
done
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Days until expiry | > 30 days | 7-30 days | < 7 days or expired |
| SAN entries | Include VIP + all nodes | Missing some entries | Missing VIP or critical node |
| Certificate chain | Full chain valid | Intermediate missing (works) | Chain broken / untrusted |
| Consistency across nodes | Same cert on all nodes | -- | Different certs on nodes |
| Ingestion port cert | Valid | Nearing expiry | Expired |

<div class="fix-box">
<strong>Remediation:</strong> If certificates are expiring or invalid:<br>
1. Generate a new CSR from the Ops for Logs admin UI: <strong>Administration > SSL</strong><br>
2. Submit the CSR to your CA and obtain the signed certificate<br>
3. Upload the new certificate via the UI or API: <code>PUT /api/v1/ssl</code><br>
4. For custom CA trust, upload the CA certificate: <code>POST /api/v1/ssl/ca</code><br>
5. Restart Apache after certificate replacement: <code>systemctl restart httpd</code><br>
6. Verify all agents reconnect after certificate change -- agents must trust the new CA
</div>

<div class="page-break"></div>

<a id="ntp-dns"></a>

# 14. NTP & DNS

Accurate time synchronization and reliable DNS resolution are foundational requirements for Ops for Logs. Time skew causes log correlation issues, and DNS failures prevent cluster communication.

<a id="time-sync"></a>

## 14.1 Time Synchronization

#### Check NTP Status (chrony)

```bash
# Check chrony synchronization status on each node
ssh root@${OFL_NODE1} "chronyc tracking"
```

**Expected output:**

```
Reference ID    : C0A80001 (ntp-server.vcf.local)
Stratum         : 3
Ref time (UTC)  : Wed Mar 26 09:30:22 2026
System time     : 0.000023455 seconds fast of NTP time
Last offset     : +0.000012332 seconds
RMS offset      : 0.000034521 seconds
Frequency       : 2.345 ppm slow
Residual freq   : +0.001 ppm
Skew            : 0.023 ppm
Root delay      : 0.001234 seconds
Root dispersion : 0.000456 seconds
Update interval : 1024.0 seconds
Leap status     : Normal
```

#### Check NTP Sources

```bash
# List NTP sources and their status
ssh root@${OFL_NODE1} "chronyc sources -v"
```

**Expected output:**

```
  .-- Source mode  '^' = server, '=' = peer, '#' = local clock.
 / .- Source state '*' = current best, '+' = combined, '-' = not combined,
| /             'x' = may be in error, '~' = too variable, '?' = unusable.
||                                                 .- xxxx [ yyyy ] +/- zzzz
||      Reachability register (octal) -.           |  xxxx = adjusted offset,
||      Log2(Polling interval) --.      |          |  yyyy = measured offset,
||                                \     |          |  zzzz = estimated error.
||                                 |    |           \
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^* ntp-server.vcf.local          2  10   377   234   +0.012ms[ +0.015ms] +/-  1.23ms
^+ ntp-backup.vcf.local          2  10   377   512   -0.034ms[ -0.031ms] +/-  2.45ms
```

#### Compare Time Across All Nodes

```bash
# Check time offset between all nodes
echo "=== Time on each node ==="
for NODE in ${OFL_NODE1} ${OFL_NODE2} ${OFL_NODE3}; do
  TIME=$(ssh root@${NODE} "date -u '+%Y-%m-%d %H:%M:%S.%N UTC'")
  echo "${NODE}: ${TIME}"
done
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| NTP offset | < 100ms | 100ms - 500ms | > 500ms |
| NTP source reachable | At least 1 source with `*` | Sources showing `?` | No reachable source |
| Inter-node time drift | < 200ms between nodes | 200ms - 1s | > 1s between nodes |
| Leap status | `Normal` | -- | `Not synchronised` |

<div class="fix-box">
<strong>Remediation:</strong> If NTP is out of sync:<br>
1. Force an immediate sync: <code>chronyc makestep</code><br>
2. Verify NTP server is reachable: <code>ping ntp-server.vcf.local</code><br>
3. Check chrony configuration: <code>cat /etc/chrony.conf</code><br>
4. Restart chrony: <code>systemctl restart chronyd</code><br>
5. If using ntpd instead: <code>systemctl restart ntpd && ntpq -p</code>
</div>

<a id="dns-resolution"></a>

## 14.2 DNS Resolution

#### Forward DNS Lookup

```bash
# Verify DNS resolution for all Ops for Logs FQDNs
echo "=== Forward DNS Lookups ==="
for FQDN in ${OFL_HOST} ${OFL_NODE1} ${OFL_NODE2} ${OFL_NODE3}; do
  IP=$(dig +short ${FQDN} 2>/dev/null)
  printf "%-45s -> %s\n" "${FQDN}" "${IP:-FAILED}"
done
```

**Expected output:**

```
=== Forward DNS Lookups ===
ops-for-logs.vcf.local                        -> 192.168.1.100
ops-for-logs-node1.vcf.local                  -> 192.168.1.101
ops-for-logs-node2.vcf.local                  -> 192.168.1.102
ops-for-logs-node3.vcf.local                  -> 192.168.1.103
```

#### Reverse DNS Lookup

```bash
# Verify reverse DNS for all node IPs
echo "=== Reverse DNS Lookups ==="
for IP in 192.168.1.100 192.168.1.101 192.168.1.102 192.168.1.103; do
  HOSTNAME=$(dig +short -x ${IP} 2>/dev/null)
  printf "%-18s -> %s\n" "${IP}" "${HOSTNAME:-FAILED}"
done
```

#### DNS Response Time

```bash
# Measure DNS resolution time
echo "=== DNS Response Time ==="
for FQDN in ${OFL_HOST} ${OFL_NODE1}; do
  TIME=$(dig ${FQDN} | grep "Query time" | awk '{print $4, $5}')
  printf "%-45s %s\n" "${FQDN}" "${TIME}"
done
```

#### DNS Configuration on Nodes

```bash
# Check DNS configuration on each node
ssh root@${OFL_NODE1} "cat /etc/resolv.conf"
```

**Expected output:**

```
search vcf.local
nameserver 192.168.1.10
nameserver 192.168.1.11
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Forward DNS | All FQDNs resolve | Slow resolution (> 1s) | Any FQDN fails to resolve |
| Reverse DNS | All IPs resolve to correct FQDN | Missing reverse for VIP | Missing reverse for node |
| DNS response time | < 100ms | 100ms - 1s | > 1s |
| DNS servers configured | 2+ nameservers | 1 nameserver | 0 nameservers |

<div class="fix-box">
<strong>Remediation:</strong> If DNS is failing:<br>
1. Verify DNS server reachability: <code>ping 192.168.1.10</code><br>
2. Check <code>/etc/resolv.conf</code> for correct nameserver entries<br>
3. Test with a specific DNS server: <code>dig @192.168.1.10 ops-for-logs.vcf.local</code><br>
4. Add missing DNS records (forward and reverse) in your DNS infrastructure<br>
5. Clear DNS cache if applicable: <code>systemd-resolve --flush-caches</code>
</div>

<div class="page-break"></div>

<a id="backup-config"></a>

# 15. Backup Configuration

Regular backups of Ops for Logs configuration and data are essential for disaster recovery. This section verifies backup configuration and recency.

<a id="backup-status"></a>

## 15.1 Backup Status

#### Check Backup Configuration via CLI

```bash
# Check backup schedule and recent backup status
ssh root@${OFL_NODE1} "
  echo '=== Backup Configuration ==='
  grep -A 20 'backup' /storage/var/loginsight/config/loginsight-config.xml 2>/dev/null | head -25
  echo ''
  echo '=== Recent Backup Files ==='
  ls -lhrt /storage/var/loginsight/backups/ 2>/dev/null | tail -10
"
```

#### Check Backup via API

```bash
# Get backup configuration and status
curl -sk -X GET "${OFL_API}/backup" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

**Expected response:**

```json
{
  "enabled": true,
  "schedule": "DAILY",
  "lastBackupTime": "2026-03-25T02:00:00Z",
  "lastBackupStatus": "SUCCESS",
  "lastBackupSizeBytes": 245678901,
  "backupDestination": "/storage/var/loginsight/backups",
  "retentionCount": 7
}
```

<a id="backup-location"></a>

## 15.2 Backup Location & Retention

```bash
# Verify backup destination is accessible and has space
ssh root@${OFL_NODE1} "
  echo '=== Backup Directory ==='
  ls -lh /storage/var/loginsight/backups/ 2>/dev/null
  echo ''
  echo '=== Total Backup Size ==='
  du -sh /storage/var/loginsight/backups/ 2>/dev/null
  echo ''
  echo '=== Backup Count ==='
  ls -1 /storage/var/loginsight/backups/*.tar.gz 2>/dev/null | wc -l
"
```

**Expected output:**

```
=== Backup Directory ===
-rw-r--r-- 1 root root 234M Mar 25 02:01 backup-2026-03-25.tar.gz
-rw-r--r-- 1 root root 231M Mar 24 02:01 backup-2026-03-24.tar.gz
-rw-r--r-- 1 root root 228M Mar 23 02:01 backup-2026-03-23.tar.gz

=== Total Backup Size ===
1.6G    /storage/var/loginsight/backups/

=== Backup Count ===
7
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Backup configured | Enabled with schedule | -- | Not configured |
| Last backup status | `SUCCESS` | -- | `FAILED` |
| Last backup age | < 24 hours | 1-7 days | > 7 days |
| Backup retention | >= 3 copies | 1-2 copies | 0 copies |
| Backup destination space | > 20% free | 10-20% free | < 10% free |

<div class="fix-box">
<strong>Remediation:</strong> If backups are not configured or failing:<br>
1. Enable backups via the admin UI: <strong>Administration > Configuration > Backup</strong><br>
2. Configure via API: <code>PUT /api/v1/backup</code> with schedule and destination<br>
3. For external backup, configure NFS mount for backup destination<br>
4. If backups are failing, check disk space at the destination<br>
5. Trigger a manual backup: <code>POST /api/v1/backup/trigger</code><br>
6. Verify backup integrity by testing a restore in a non-production environment
</div>

<div class="page-break"></div>

<a id="resource-utilization"></a>

# 16. Resource Utilization

Monitoring CPU, memory, disk I/O, and JVM heap usage per node ensures Ops for Logs has adequate resources and is not approaching capacity limits.

<a id="cpu-memory"></a>

## 16.1 CPU & Memory per Node

#### CPU Utilization

```bash
# Check CPU utilization on each node
for NODE in ${OFL_NODE1} ${OFL_NODE2} ${OFL_NODE3}; do
  echo "===== ${NODE} ====="
  ssh root@${NODE} "
    echo '--- CPU Summary (mpstat) ---'
    mpstat 1 3 | tail -1
    echo ''
    echo '--- Load Average ---'
    uptime
    echo ''
    echo '--- Top CPU Processes ---'
    ps aux --sort=-%cpu | head -6
  "
  echo ""
done
```

**Expected output (per node):**

```
===== ops-for-logs-node1.vcf.local =====
--- CPU Summary (mpstat) ---
Average:     all    22.15    0.00    3.45    0.12    0.00    0.00    0.00    0.00   74.28

--- Load Average ---
 09:45:12 up 45 days,  3:12,  1 user,  load average: 1.42, 1.38, 1.35

--- Top CPU Processes ---
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root      1842 18.2 52.3 8234560 4312340 ?   Sl   Mar20 3214:23 /usr/lib/loginsight/application/sbin/loginsight
root      1523 12.5 35.2 5234560 2903450 ?   Sl   Mar20 1823:45 /usr/bin/java -Xms2048m -Xmx2048m (cassandra)
root      2103  2.1  4.3  234560  354340 ?   Ss   Mar20  302:12 /usr/sbin/httpd
root      1955  1.3  1.6  198450  132340 ?   Sl   Mar20  189:34 /usr/bin/ruby (fluentd)
```

#### Memory Utilization

```bash
# Check memory utilization on each node
for NODE in ${OFL_NODE1} ${OFL_NODE2} ${OFL_NODE3}; do
  echo "===== ${NODE} ====="
  ssh root@${NODE} "free -m"
  echo ""
done
```

**Expected output (per node):**

```
===== ops-for-logs-node1.vcf.local =====
              total        used        free      shared  buff/cache   available
Mem:          16016       10452        1234         128        4330        5184
Swap:          2048           0        2048
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| CPU utilization | < 70% sustained | 70-90% sustained | > 90% sustained |
| Load average | < (CPU count * 0.7) | < (CPU count * 1.0) | > (CPU count * 1.5) |
| Memory used | < 80% of total | 80-90% of total | > 90% of total |
| Swap usage | 0 MB | < 500 MB | > 500 MB (indicates memory pressure) |

<a id="jvm-heap"></a>

## 16.2 JVM Heap Usage

Cassandra runs on the JVM and is sensitive to heap exhaustion. Log Insight also uses Java components.

#### Cassandra JVM Heap

```bash
# Check Cassandra JVM heap usage via nodetool
ssh root@${OFL_NODE1} "nodetool info | grep -E 'Heap|Off'"
```

**Expected output:**

```
Heap Memory (MB)    : 2048.00 / 2048.00
Off Heap Memory (MB): 123.45
```

#### Check for JVM Garbage Collection Issues

```bash
# Check Cassandra GC log for long pauses
ssh root@${OFL_NODE1} "grep -c 'GC pause.*[0-9]\{4,\}ms' /storage/var/cassandra/logs/gc.log 2>/dev/null || echo '0'"

# Check for OutOfMemoryError
ssh root@${OFL_NODE1} "grep -c 'OutOfMemoryError' /storage/var/cassandra/logs/system.log 2>/dev/null || echo '0'"
```

#### Log Insight JVM Heap

```bash
# Check Log Insight JVM heap from runtime log
ssh root@${OFL_NODE1} "grep -i 'heap\|memory' /storage/var/loginsight/runtime.log | tail -10"
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Cassandra heap usage | < 75% of max | 75-90% | > 90% or OOM errors |
| GC pause duration | < 500ms | 500ms - 2s | > 2s (application stalls) |
| GC pause frequency | < 1 per minute | 1-5 per minute | > 5 per minute |
| OOM errors | 0 | -- | Any OOM errors |

<a id="disk-io"></a>

## 16.3 Disk I/O Performance

```bash
# Check disk I/O statistics
ssh root@${OFL_NODE1} "
  echo '=== Disk I/O Stats (iostat) ==='
  iostat -xz 1 3 | tail -10
  echo ''
  echo '=== Disk Queue Depth ==='
  iostat -x | grep -E 'sdb|nvme' | awk '{print \$1, \"await:\" \$10 \"ms\", \"util:\" \$NF \"%\"}'
"
```

**Expected output:**

```
=== Disk I/O Stats (iostat) ===
Device         r/s     w/s   rkB/s     wkB/s  await  %util
sdb          45.23   128.67  2345.00  8765.00   2.34  18.56

=== Disk Queue Depth ===
sdb await: 2.34ms util: 18.56%
```

| Criteria | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| Disk utilization (`%util`) | < 60% | 60-85% | > 85% |
| Average wait (`await`) | < 10ms | 10-50ms | > 50ms |
| I/O queue depth | < 4 | 4-16 | > 16 |

<div class="fix-box">
<strong>Remediation:</strong> If resource utilization is high:<br>
1. <strong>CPU:</strong> Identify top processes. If Cassandra, check compaction. If loginsight, check ingestion rate.<br>
2. <strong>Memory:</strong> Increase VM memory allocation and adjust JVM heap (-Xmx) accordingly.<br>
3. <strong>Swap:</strong> Any swap usage indicates memory pressure -- increase RAM.<br>
4. <strong>Disk I/O:</strong> Migrate to faster storage (SSD/NVMe). Reduce retention period. Enable compression.<br>
5. <strong>JVM Heap:</strong> Increase Cassandra heap in <code>/storage/var/cassandra/conf/cassandra-env.sh</code>. Restart Cassandra after changes.
</div>

<div class="page-break"></div>

<a id="port-reference"></a>

# 17. Port Reference Table

The following table documents all network ports used by VCF Operations for Logs. Ensure firewall rules permit these ports between the listed source and destination components.

| Port | Protocol | Direction | Source | Destination | Purpose |
|------|----------|-----------|--------|-------------|---------|
| **443** | TCP (HTTPS) | Inbound | Browsers, API clients | Ops for Logs VIP/Nodes | Web UI and REST API access |
| **80** | TCP (HTTP) | Inbound | Browsers | Ops for Logs VIP/Nodes | HTTP redirect to HTTPS |
| **9000** | TCP | Inbound | Ops for Logs agents | Ops for Logs VIP/Nodes | CFAPI log ingestion (non-TLS) |
| **9543** | TCP (TLS) | Inbound | Ops for Logs agents | Ops for Logs VIP/Nodes | CFAPI log ingestion (TLS) |
| **514** | TCP/UDP | Inbound | Syslog sources | Ops for Logs VIP/Nodes | Syslog ingestion (non-TLS) |
| **1514** | TCP | Inbound | Syslog sources | Ops for Logs VIP/Nodes | Syslog ingestion (alternate port) |
| **6514** | TCP (TLS) | Inbound | Syslog sources | Ops for Logs VIP/Nodes | Syslog ingestion (TLS) |
| **7000** | TCP | Inter-node | Ops for Logs Node | Ops for Logs Node | Cassandra inter-node gossip |
| **7001** | TCP (TLS) | Inter-node | Ops for Logs Node | Ops for Logs Node | Cassandra inter-node TLS gossip |
| **7199** | TCP | Inter-node | Ops for Logs Node | Ops for Logs Node | Cassandra JMX monitoring |
| **9042** | TCP | Inter-node | Ops for Logs Node | Ops for Logs Node | Cassandra CQL native transport |
| **9160** | TCP | Inter-node | Ops for Logs Node | Ops for Logs Node | Cassandra Thrift client (legacy) |
| **16520** | TCP | Inter-node | Ops for Logs Node | Ops for Logs Node | Cluster replication and sync |
| **16521** | TCP (TLS) | Inter-node | Ops for Logs Node | Ops for Logs Node | Cluster replication (TLS) |
| **123** | UDP | Outbound | Ops for Logs Nodes | NTP Server | Time synchronization |
| **53** | TCP/UDP | Outbound | Ops for Logs Nodes | DNS Server | DNS resolution |
| **389** | TCP | Outbound | Ops for Logs Nodes | LDAP/AD Server | LDAP authentication |
| **636** | TCP (TLS) | Outbound | Ops for Logs Nodes | LDAP/AD Server | LDAPS authentication |
| **25** | TCP | Outbound | Ops for Logs Nodes | SMTP Server | Email notifications/alerts |
| **587** | TCP (TLS) | Outbound | Ops for Logs Nodes | SMTP Server | Email (TLS STARTTLS) |
| **514/6514** | TCP | Outbound | Ops for Logs Nodes | Forwarding destination | Log forwarding (syslog) |
| **9543** | TCP (TLS) | Outbound | Ops for Logs Nodes | Forwarding destination | Log forwarding (CFAPI) |
| **443** | TCP (HTTPS) | Outbound | Ops for Logs Nodes | VCF Operations | Integration with Ops Manager |
| **443** | TCP (HTTPS) | Outbound | Ops for Logs Nodes | vCenter Server | vSphere integration |
| **443** | TCP (HTTPS) | Outbound | Ops for Logs Nodes | SDDC Manager | VCF lifecycle management |
| **443** | TCP (HTTPS) | Outbound | Ops for Logs Nodes | Workspace ONE Access | VIDM SSO authentication |
| **2049** | TCP | Outbound | Ops for Logs Nodes | NFS Server | Archive storage (NFS) |

#### Port Verification Script

```bash
# Verify all critical ports are listening on a node
ssh root@${OFL_NODE1} "
  echo '=== Listening Ports ==='
  ss -tuln | grep -E ':(443|80|9000|9543|514|1514|6514|7000|7199|9042|16520) ' | sort -t: -k2 -n
"
```

**Expected output:**

```
tcp   LISTEN  0  128  *:80     *:*
tcp   LISTEN  0  128  *:443    *:*
tcp   LISTEN  0  128  *:514    *:*
tcp   LISTEN  0  128  *:1514   *:*
tcp   LISTEN  0  128  *:6514   *:*
tcp   LISTEN  0  128  *:7000   *:*
tcp   LISTEN  0  128  *:7199   *:*
tcp   LISTEN  0  128  *:9000   *:*
tcp   LISTEN  0  128  *:9042   *:*
tcp   LISTEN  0  128  *:9543   *:*
tcp   LISTEN  0  128  *:16520  *:*
```

#### Firewall Rule Validation

```bash
# Check iptables rules (if applicable)
ssh root@${OFL_NODE1} "iptables -L -n --line-numbers 2>/dev/null | head -40 || echo 'iptables not active'"

# Test external connectivity to key ports
for PORT in 443 9000 9543 514 6514; do
  nc -zv ${OFL_HOST} ${PORT} 2>&1 | grep -E 'succeeded|refused|timed'
done
```

<div class="page-break"></div>

<a id="common-issues"></a>

# 18. Common Issues & Remediation

This section provides detailed troubleshooting guidance for the most frequently encountered Ops for Logs problems.

<a id="cassandra-issues"></a>

## 18.1 Cassandra Issues

### 18.1.1 Cassandra Fails to Start

**Symptoms:** `systemctl status cassandra` shows `failed`. Log queries return errors. Web UI shows "Service Unavailable".

**Diagnosis:**

```bash
# Check Cassandra system log for startup errors
ssh root@${OFL_NODE1} "tail -100 /storage/var/cassandra/logs/system.log | grep -i 'error\|exception\|fatal'"

# Check for commit log corruption
ssh root@${OFL_NODE1} "ls -la /storage/var/cassandra/commitlog/"

# Check disk space
ssh root@${OFL_NODE1} "df -h /storage/var"
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. If disk is full, free space by reducing retention or removing old archives<br>
2. If commit log is corrupt, move corrupt files (do NOT delete): <code>mkdir /tmp/corrupt-cl && mv /storage/var/cassandra/commitlog/CommitLog-*.log /tmp/corrupt-cl/</code><br>
3. If JVM heap is insufficient, increase in <code>/storage/var/cassandra/conf/cassandra-env.sh</code><br>
4. Restart Cassandra: <code>systemctl restart cassandra</code><br>
5. Verify ring status: <code>nodetool status</code> -- ensure all nodes rejoin
</div>

### 18.1.2 Cassandra High Compaction Backlog

**Symptoms:** Slow queries, high disk I/O, increasing disk usage despite stable ingestion.

```bash
# Check compaction backlog
ssh root@${OFL_NODE1} "nodetool compactionstats"

# Check compaction throughput
ssh root@${OFL_NODE1} "nodetool getcompactionthroughput"
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. Temporarily increase compaction throughput: <code>nodetool setcompactionthroughput 256</code> (default is 64 MB/s)<br>
2. Do NOT restart Cassandra during active compactions<br>
3. Monitor progress: <code>watch -n 10 'nodetool compactionstats'</code><br>
4. If compaction is stuck, identify and remove stale SSTables (advanced, contact support)
</div>

### 18.1.3 Cassandra Node Shows DN (Down Normal)

**Symptoms:** `nodetool status` shows a node as `DN`. Cluster is degraded.

```bash
# Check connectivity to the down node
ping ${OFL_NODE2}
nc -zv ${OFL_NODE2} 7000
nc -zv ${OFL_NODE2} 9042

# Check logs on the down node
ssh root@${OFL_NODE2} "systemctl status cassandra && tail -50 /storage/var/cassandra/logs/system.log"
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. Verify network connectivity between nodes<br>
2. Restart Cassandra on the down node: <code>systemctl restart cassandra</code><br>
3. Monitor it rejoining the ring: <code>nodetool status</code> (wait for <code>UJ</code> then <code>UN</code>)<br>
4. If the node cannot rejoin, check for clock skew (Section 14.1)<br>
5. As a last resort, decommission and recommission the node
</div>

<a id="ingestion-drops"></a>

## 18.2 Ingestion Drops

**Symptoms:** Missing logs in queries, ingestion EPS drops to zero or significantly below baseline, monitoring alerts on dropped events.

**Diagnosis:**

```bash
# Check for ingestion errors in runtime log
ssh root@${OFL_NODE1} "grep -i 'drop\|overflow\|backpressure\|reject' \
  /storage/var/loginsight/runtime.log | tail -20"

# Check ingestion pipeline ports
ssh root@${OFL_NODE1} "ss -tuln | grep -E ':(514|1514|6514|9000|9543)'"

# Check stats API for dropped events
curl -sk -X GET "${OFL_API}/stats" \
  -H "Authorization: Bearer ${TOKEN}" | jq '{droppedEvents, currentEventsPerSecond, queueDepth}'
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. <strong>Disk full:</strong> The most common cause. Free disk space immediately (Section 6).<br>
2. <strong>Cassandra down:</strong> Ops for Logs cannot index events if Cassandra is unhealthy (Section 18.1).<br>
3. <strong>Network saturation:</strong> Check bandwidth utilization on ingestion NICs.<br>
4. <strong>Too many sources:</strong> Add worker nodes to distribute ingestion load.<br>
5. <strong>Firewall blocking:</strong> Verify ingestion ports are open from all log sources.<br>
6. <strong>Agent misconfiguration:</strong> Verify agent destination points to VIP, not individual node.
</div>

<a id="disk-full"></a>

## 18.3 Disk Full Scenarios

**Symptoms:** Ingestion halts, web UI errors, Cassandra write failures, `df -h /storage/var` shows > 95%.

**Emergency Diagnosis:**

```bash
# Identify what is consuming space
ssh root@${OFL_NODE1} "
  df -h /storage/var
  echo ''
  du -sh /storage/var/*/ 2>/dev/null | sort -rh
  echo ''
  echo '=== Largest files ==='
  find /storage/var -type f -size +1G -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -10
"
```

<div class="danger">
<strong>CRITICAL:</strong> Disk full is an emergency situation. Ops for Logs will stop ingesting logs and may become unresponsive. Address immediately.
</div>

<div class="fix-box">
<strong>Emergency Remediation (in priority order):</strong><br>
1. <strong>Clear Cassandra snapshots:</strong> <code>nodetool clearsnapshot</code> -- can free significant space<br>
2. <strong>Reduce retention period:</strong> Temporarily reduce to force purge of old data<br>
3. <strong>Clear old archives:</strong> If archiving to local disk, remove old archive files<br>
4. <strong>Remove core dumps:</strong> <code>find /storage/var -name "core.*" -delete</code><br>
5. <strong>Clear Fluentd buffers:</strong> <code>rm -f /storage/var/fluentd/buffer/*.log</code><br>
6. <strong>Expand the disk:</strong> In vSphere, increase the VMDK size, then:<br>
   <code>growpart /dev/sdb 1 && resize2fs /dev/sdb1</code><br>
7. <strong>Add NFS archive:</strong> Move old data offload to NFS to free local space
</div>

<a id="cluster-split"></a>

## 18.4 Cluster Split-Brain

**Symptoms:** Two nodes claim to be master, data inconsistency between nodes, cluster API shows conflicting information.

**Diagnosis:**

```bash
# Check cluster state from each node
for NODE in ${OFL_NODE1} ${OFL_NODE2} ${OFL_NODE3}; do
  echo "===== ${NODE} ====="
  ssh root@${NODE} "curl -sk https://localhost/api/v1/cluster 2>/dev/null | python3 -m json.tool | grep -E 'role|status'"
  echo ""
done

# Check Cassandra ring consistency
for NODE in ${OFL_NODE1} ${OFL_NODE2} ${OFL_NODE3}; do
  echo "===== ${NODE} ====="
  ssh root@${NODE} "nodetool describecluster | head -10"
  echo ""
done
```

<div class="danger">
<strong>CRITICAL:</strong> Split-brain is a serious condition that can cause data loss. Do NOT attempt to resolve without understanding which node has the most recent valid data.
</div>

<div class="fix-box">
<strong>Remediation:</strong><br>
1. <strong>Identify the legitimate master:</strong> The node with the most recent successful writes is typically authoritative<br>
2. <strong>Stop the false master:</strong> <code>systemctl stop loginsight</code> on the node incorrectly claiming master<br>
3. <strong>Verify Cassandra consistency:</strong> <code>nodetool repair</code> on the remaining nodes<br>
4. <strong>Restart the stopped node as worker:</strong> The node should rejoin as a worker<br>
5. <strong>Check NTP:</strong> Clock skew is a common cause of split-brain<br>
6. <strong>Check network partitions:</strong> Ensure all nodes can reach each other on all required ports<br>
7. <strong>Contact VMware Support</strong> if the cluster cannot self-heal
</div>

<a id="cert-problems"></a>

## 18.5 Certificate Problems

**Symptoms:** Browser SSL warnings, agent connection failures, API calls return TLS errors, forwarding breaks.

**Diagnosis:**

```bash
# Check certificate details
echo | openssl s_client -connect ${OFL_HOST}:443 2>&1 | grep -E 'Verify|depth|error|subject'

# Check certificate expiry
echo | openssl s_client -connect ${OFL_HOST}:443 2>/dev/null | openssl x509 -noout -dates

# Check if agents can connect (from an agent host)
openssl s_client -connect ${OFL_HOST}:9543 </dev/null 2>&1 | grep "Verify return code"
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. <strong>Expired certificate:</strong> Replace immediately via <strong>Administration > SSL</strong> in the UI<br>
2. <strong>Untrusted CA:</strong> Upload the CA certificate to the trust store: <code>POST /api/v1/ssl/ca</code><br>
3. <strong>SAN mismatch:</strong> Regenerate the certificate with correct Subject Alternative Names<br>
4. <strong>Agent trust:</strong> Deploy the CA certificate to all agent hosts. For ESXi: upload to <code>/etc/vmware/ssl/</code><br>
5. <strong>After certificate change:</strong> Restart Apache (<code>systemctl restart httpd</code>) and verify agents reconnect
</div>

<a id="agent-disconnects"></a>

## 18.6 Agent Disconnects

**Symptoms:** Agents showing `DISCONNECTED` status, gaps in log data from specific hosts, agent heartbeat timeouts.

**Diagnosis (from the agent host):**

```bash
# Check agent status on the remote host
ssh root@<agent-host> "systemctl status liagentd"

# Check agent log
ssh root@<agent-host> "tail -50 /var/log/liagent/liagent.log"

# Test connectivity to Ops for Logs
ssh root@<agent-host> "nc -zv ${OFL_HOST} 9543 && nc -zv ${OFL_HOST} 443"

# Check agent configuration
ssh root@<agent-host> "cat /var/lib/liagent/liagent.ini | grep -v '^;' | grep -v '^$'"
```

**On ESXi hosts:**

```bash
# Check ESXi syslog configuration
ssh root@<esxi-host> "esxcli system syslog config get"

# Check ESXi Log Insight agent
ssh root@<esxi-host> "esxcli software vib list | grep -i loginsight"

# Test connectivity from ESXi
ssh root@<esxi-host> "nc -zv ${OFL_HOST} 9543"
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. <strong>Agent not running:</strong> Restart: <code>systemctl restart liagentd</code><br>
2. <strong>Connectivity blocked:</strong> Check firewall rules between agent and Ops for Logs (port 9543)<br>
3. <strong>Certificate trust:</strong> Ensure the agent trusts the Ops for Logs CA<br>
4. <strong>Wrong destination:</strong> Update <code>liagent.ini</code> to point to the VIP: <code>hostname=ops-for-logs.vcf.local</code><br>
5. <strong>ESXi agent outdated:</strong> Update the VIB: <code>esxcli software vib update -d /path/to/VMware-loginsight-agent.zip</code><br>
6. <strong>DNS issue:</strong> Verify the agent can resolve the Ops for Logs FQDN
</div>

<div class="page-break"></div>

<a id="cli-reference"></a>

# 19. CLI Quick Reference Card

This section provides a consolidated list of all CLI commands used throughout this handbook for quick reference.

### System Service Commands

| Command | Purpose |
|---------|---------|
| `systemctl status loginsight` | Check Log Insight daemon status |
| `systemctl status cassandra` | Check Cassandra service status |
| `systemctl status httpd` | Check Apache HTTPD status |
| `systemctl status fluentd` | Check Fluentd status |
| `systemctl restart loginsight` | Restart the Log Insight daemon |
| `systemctl restart cassandra` | Restart Cassandra |
| `systemctl restart httpd` | Restart Apache |
| `systemctl restart fluentd` | Restart Fluentd |
| `systemctl restart chronyd` | Restart NTP (chrony) |
| `journalctl -u loginsight --no-pager -n 100` | View recent Log Insight journal entries |
| `journalctl -u cassandra --no-pager -n 100` | View recent Cassandra journal entries |

### Cassandra (nodetool) Commands

| Command | Purpose |
|---------|---------|
| `nodetool status` | Show Cassandra ring status and node states |
| `nodetool info` | Show node info including heap memory |
| `nodetool compactionstats` | Show pending and active compactions |
| `nodetool getcompactionthroughput` | Show current compaction throughput limit |
| `nodetool setcompactionthroughput <MB/s>` | Set compaction throughput (e.g., 128 or 256) |
| `nodetool describecluster` | Show cluster name, snitch, and schema versions |
| `nodetool repair` | Run a repair on the local node |
| `nodetool clearsnapshot` | Clear all saved snapshots to free disk space |
| `nodetool tpstats` | Show thread pool statistics |
| `nodetool cfstats` | Show column family (table) statistics |
| `nodetool gcstats` | Show garbage collection statistics |

### Storage & Disk Commands

| Command | Purpose |
|---------|---------|
| `df -hT` | Show all filesystem usage with type |
| `df -h /storage/var` | Show `/storage/var` usage |
| `df -i /storage/var` | Show inode usage |
| `du -sh /storage/var/*/` | Show top-level directory sizes |
| `du -sh /storage/var/cassandra/data/` | Show Cassandra data size |
| `du -sh /storage/var/loginsight/` | Show Log Insight data size |
| `du -sh /storage/var/fluentd/buffer/` | Show Fluentd buffer size |
| `iostat -xz 1 3` | Show disk I/O statistics (3 samples) |

### Network & Connectivity Commands

| Command | Purpose |
|---------|---------|
| `ss -tuln` | Show all listening TCP/UDP ports |
| `ss -tn` | Show all active TCP connections |
| `ss -s` | Show socket statistics summary |
| `nc -zv <host> <port>` | Test TCP connectivity to a specific port |
| `ping <host>` | Test ICMP reachability |
| `dig <fqdn>` | Forward DNS lookup |
| `dig +short <fqdn>` | Forward DNS lookup (short output) |
| `dig +short -x <ip>` | Reverse DNS lookup |
| `ip addr show` | Show network interface addresses |
| `arping -D -I eth0 <ip>` | Check for IP address conflicts |

### Certificate Commands

| Command | Purpose |
|---------|---------|
| `openssl s_client -connect <host>:443` | Inspect the SSL certificate on port 443 |
| `openssl x509 -noout -subject -dates -issuer` | Parse certificate details (piped from s_client) |
| `openssl x509 -noout -enddate` | Show only the expiry date |
| `openssl s_client -connect <host>:443 -showcerts` | Show the full certificate chain |
| `openssl verify <cert.pem>` | Verify a certificate chain |
| `keytool -list -keystore <path> -storepass changeit` | List Java trust store contents |

### Time Synchronization Commands

| Command | Purpose |
|---------|---------|
| `chronyc tracking` | Show NTP tracking status |
| `chronyc sources -v` | Show NTP sources with details |
| `chronyc makestep` | Force an immediate time sync |
| `ntpq -p` | Show NTP peers (if using ntpd) |
| `date -u` | Show current UTC time |
| `timedatectl status` | Show time/date configuration |

### Process & Resource Commands

| Command | Purpose |
|---------|---------|
| `ps aux --sort=-%cpu \| head -10` | Top 10 processes by CPU |
| `ps aux --sort=-%mem \| head -10` | Top 10 processes by memory |
| `free -m` | Show memory usage in MB |
| `uptime` | Show uptime and load average |
| `mpstat 1 3` | Show CPU statistics (3 samples) |
| `top -bn1 \| head -20` | One-shot top output |

### Log File Locations

| Log File | Purpose |
|----------|---------|
| `/storage/var/loginsight/runtime.log` | Main Ops for Logs application log |
| `/storage/var/cassandra/logs/system.log` | Cassandra system log |
| `/storage/var/cassandra/logs/gc.log` | Cassandra garbage collection log |
| `/var/log/httpd/error_log` | Apache error log |
| `/var/log/httpd/access_log` | Apache access log |
| `/var/log/fluentd/fluentd.log` | Fluentd log |
| `/var/log/liagent/liagent.log` | Log Insight agent log (on agent hosts) |

<div class="page-break"></div>

<a id="api-reference"></a>

# 20. API Quick Reference

All API endpoints use the base URL `https://<ops-for-logs-vip>/api/v1/`. Authentication is required for most endpoints via the `Authorization: Bearer <token>` header.

### Authentication

```bash
# POST /api/v1/sessions -- Authenticate and obtain a session token
curl -sk -X POST "https://${OFL_HOST}/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "<PASSWORD>",
    "provider": "Local"
  }'
# Response: { "sessionId": "<TOKEN>", "userId": "<UUID>", "ttl": 1800 }

# DELETE /api/v1/sessions/current -- Invalidate the current session
curl -sk -X DELETE "https://${OFL_HOST}/api/v1/sessions/current" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Version & System Info

```bash
# GET /api/v1/version -- Get product version info
curl -sk -X GET "https://${OFL_HOST}/api/v1/version" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
# Response: { "version": "9.0.0", "build": "12345678", "releaseName": "..." }
```

### Cluster Management

```bash
# GET /api/v1/cluster -- Get cluster configuration and node list
curl -sk -X GET "https://${OFL_HOST}/api/v1/cluster" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# GET /api/v1/cluster/status -- Get detailed cluster health status
curl -sk -X GET "https://${OFL_HOST}/api/v1/cluster/status" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# GET /api/v1/ilb -- Get ILB configuration
curl -sk -X GET "https://${OFL_HOST}/api/v1/ilb" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

### Statistics & Monitoring

```bash
# GET /api/v1/stats -- Get ingestion statistics
curl -sk -X GET "https://${OFL_HOST}/api/v1/stats" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
# Response: { "totalEventsIngested": N, "currentEventsPerSecond": N, "droppedEvents": N, ... }

# POST /api/v1/events/stats -- Query historical ingestion statistics
curl -sk -X POST "https://${OFL_HOST}/api/v1/events/stats" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ingestion_rate",
    "startTimeMillis": 1711411200000,
    "endTimeMillis": 1711497600000,
    "bucketDurationMinutes": 60
  }' | jq '.'
```

### Event Queries

```bash
# POST /api/v1/events -- Search for events
curl -sk -X POST "https://${OFL_HOST}/api/v1/events" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vmw_vc_*",
    "startTimeMillis": 1711411200000,
    "endTimeMillis": 1711497600000,
    "limit": 100
  }' | jq '.'

# POST /api/v1/events/ingest/0 -- Ingest events via API
curl -sk -X POST "https://${OFL_HOST}/api/v1/events/ingest/0" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "text": "Test event from API",
        "source": "api-test",
        "fields": [{"name": "env", "content": "production"}]
      }
    ]
  }'
```

### Log Forwarding

```bash
# GET /api/v1/forwarding -- List all forwarding destinations
curl -sk -X GET "https://${OFL_HOST}/api/v1/forwarding" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# GET /api/v1/forwarding/stats -- Get forwarding statistics
curl -sk -X GET "https://${OFL_HOST}/api/v1/forwarding/stats" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# POST /api/v1/forwarding -- Create a new forwarding destination
curl -sk -X POST "https://${OFL_HOST}/api/v1/forwarding" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New-SIEM",
    "host": "siem.vcf.local",
    "port": 6514,
    "protocol": "SYSLOG",
    "transport": "TCP-TLS",
    "enabled": true,
    "filter": "*"
  }' | jq '.'
```

### Content Packs

```bash
# GET /api/v1/content/contentpack/list -- List installed content packs
curl -sk -X GET "https://${OFL_HOST}/api/v1/content/contentpack/list" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# GET /api/v1/content/contentpack/marketplace -- Check marketplace for updates
curl -sk -X GET "https://${OFL_HOST}/api/v1/content/contentpack/marketplace" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# GET /api/v1/content/contentpack/autoupdate -- Check auto-update configuration
curl -sk -X GET "https://${OFL_HOST}/api/v1/content/contentpack/autoupdate" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# PUT /api/v1/content/contentpack/autoupdate -- Enable/disable auto-update
curl -sk -X PUT "https://${OFL_HOST}/api/v1/content/contentpack/autoupdate" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"autoUpdateEnabled": true, "checkIntervalHours": 24}' | jq '.'
```

### Agent Management

```bash
# GET /api/v1/agent/stats -- Get agent summary statistics
curl -sk -X GET "https://${OFL_HOST}/api/v1/agent/stats" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# GET /api/v1/agent/agents -- List all agents
curl -sk -X GET "https://${OFL_HOST}/api/v1/agent/agents" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# GET /api/v1/agent/agents?status=DISCONNECTED -- List disconnected agents
curl -sk -X GET "https://${OFL_HOST}/api/v1/agent/agents?status=DISCONNECTED" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# GET /api/v1/agent/groups -- List all agent groups
curl -sk -X GET "https://${OFL_HOST}/api/v1/agent/groups" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# GET /api/v1/agent/groups/<groupId> -- Get specific agent group configuration
curl -sk -X GET "https://${OFL_HOST}/api/v1/agent/groups/group-001" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# DELETE /api/v1/agent/agents/<agentId> -- Remove a stale agent
curl -sk -X DELETE "https://${OFL_HOST}/api/v1/agent/agents/<agentId>" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Integration

```bash
# GET /api/v1/integration/vrops -- Check VCF Operations integration status
curl -sk -X GET "https://${OFL_HOST}/api/v1/integration/vrops" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# GET /api/v1/auth/providers -- List authentication providers
curl -sk -X GET "https://${OFL_HOST}/api/v1/auth/providers" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

### SSL / Certificates

```bash
# GET /api/v1/ssl -- Get current SSL certificate information
curl -sk -X GET "https://${OFL_HOST}/api/v1/ssl" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# POST /api/v1/ssl/ca -- Upload a custom CA certificate
curl -sk -X POST "https://${OFL_HOST}/api/v1/ssl/ca" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"certificate": "<PEM-encoded-CA-cert>"}' | jq '.'

# PUT /api/v1/ssl -- Replace the server certificate
curl -sk -X PUT "https://${OFL_HOST}/api/v1/ssl" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "certificate": "<PEM-encoded-cert>",
    "privateKey": "<PEM-encoded-key>",
    "certificateChain": "<PEM-encoded-chain>"
  }' | jq '.'
```

### Backup & Restore

```bash
# GET /api/v1/backup -- Get backup configuration
curl -sk -X GET "https://${OFL_HOST}/api/v1/backup" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# POST /api/v1/backup/trigger -- Trigger an immediate backup
curl -sk -X POST "https://${OFL_HOST}/api/v1/backup/trigger" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# PUT /api/v1/backup -- Configure backup settings
curl -sk -X PUT "https://${OFL_HOST}/api/v1/backup" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "schedule": "DAILY",
    "retentionCount": 7,
    "backupDestination": "/storage/var/loginsight/backups"
  }' | jq '.'
```

### Retention & Archive

```bash
# GET /api/v1/time/config -- Get retention configuration
curl -sk -X GET "https://${OFL_HOST}/api/v1/time/config" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'

# PUT /api/v1/time/config -- Update retention settings
curl -sk -X PUT "https://${OFL_HOST}/api/v1/time/config" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"retentionPeriod": 30}' | jq '.'

# GET /api/v1/archive -- Get archive configuration
curl -sk -X GET "https://${OFL_HOST}/api/v1/archive" \
  -H "Authorization: Bearer ${TOKEN}" | jq '.'
```

<div class="page-break"></div>

---

<div style="text-align: center; padding: 40px 20px; color: #666;">

**VCF Operations for Logs Health Check Handbook**

Version 1.0 -- March 2026

Copyright 2026 Virtual Control LLC. All rights reserved.

This document is intended for internal use by authorized personnel only.

For questions, updates, or feedback regarding this handbook, contact the VCF operations team.

</div>
