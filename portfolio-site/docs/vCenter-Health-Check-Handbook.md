---
title: "vCenter Server Health Check Handbook"
subtitle: "Comprehensive Health Verification for vCenter Server in VCF 9"
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
  headerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">vCenter Server Health Check Handbook &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  footerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">Page <span class="pageNumber"></span> of <span class="totalPages"></span> &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  displayHeaderFooter: true
---

<div class="cover-page">

# vCenter Server Health Check Handbook

<div class="subtitle">Comprehensive Health Verification for vCenter Server in VCF 9</div>

<div class="meta">

**Author:** Virtual Control LLC
**Date:** March 2026
**Version:** 1.0
**Classification:** Internal Use
**Platform:** VMware Cloud Foundation 9.0 / vCenter Server 8.x

</div>
</div>


<div class="toc">

## Table of Contents

<ul>
<li><a href="#overview">1. Overview &amp; Purpose</a></li>
<li><a href="#prerequisites">2. Prerequisites</a></li>
<li><a href="#quick-reference">3. Quick Reference &mdash; All Checks Summary</a></li>
<li><a href="#vpxd-health">4. VPXD Service Health</a>
  <ul>
  <li><a href="#vpxd-process">4.1 VPXD Process Status</a></li>
  <li><a href="#vpxd-restart">4.2 VPXD Restart Procedures</a></li>
  <li><a href="#vpxd-logs">4.3 VPXD Log Analysis</a></li>
  </ul>
</li>
<li><a href="#vcenter-services">5. vCenter Services Status</a>
  <ul>
  <li><a href="#vmon-cli">5.1 vmon-cli Service Listing</a></li>
  <li><a href="#service-control">5.2 service-control Commands</a></li>
  <li><a href="#critical-services">5.3 Critical vs Non-Critical Services</a></li>
  </ul>
</li>
<li><a href="#vami-health">6. vCenter Appliance Health (VAMI)</a>
  <ul>
  <li><a href="#vami-system">6.1 System Health</a></li>
  <li><a href="#vami-memory">6.2 Memory Health</a></li>
  <li><a href="#vami-storage">6.3 Storage Health</a></li>
  <li><a href="#vami-database">6.4 Database Storage Health</a></li>
  <li><a href="#vami-load">6.5 CPU Load Health</a></li>
  <li><a href="#vami-swap">6.6 Swap Health</a></li>
  <li><a href="#vami-software">6.7 Software Packages Health</a></li>
  </ul>
</li>
<li><a href="#database-health">7. Database Health</a>
  <ul>
  <li><a href="#db-postgres">7.1 PostgreSQL Embedded DB Status</a></li>
  <li><a href="#db-size">7.2 VCDB Size Monitoring</a></li>
  <li><a href="#db-vacuum">7.3 Vacuum &amp; Maintenance</a></li>
  </ul>
</li>
<li><a href="#vcha">8. vCenter HA (VCHA)</a>
  <ul>
  <li><a href="#vcha-mode">8.1 VCHA Mode &amp; Status</a></li>
  <li><a href="#vcha-nodes">8.2 Active / Passive / Witness Status</a></li>
  <li><a href="#vcha-failover">8.3 Failover Readiness</a></li>
  </ul>
</li>
<li><a href="#certificate-health">9. Certificate Health</a>
  <ul>
  <li><a href="#cert-manager">9.1 Certificate Manager Tool</a></li>
  <li><a href="#cert-vecs">9.2 VECS Store Listing</a></li>
  <li><a href="#cert-sts">9.3 STS Certificate</a></li>
  <li><a href="#cert-machine">9.4 Machine SSL Certificate</a></li>
  <li><a href="#cert-expiry">9.5 Expiry Checks</a></li>
  </ul>
</li>
<li><a href="#storage-health">10. Storage Health</a>
  <ul>
  <li><a href="#disk-partitions">10.1 Disk Partitions &amp; Filesystem</a></li>
  <li><a href="#log-storage">10.2 Log Storage Utilization</a></li>
  <li><a href="#db-storage">10.3 DB Storage Utilization</a></li>
  </ul>
</li>
<li><a href="#performance">11. Performance &amp; Resource Utilization</a>
  <ul>
  <li><a href="#perf-cpu">11.1 CPU Utilization</a></li>
  <li><a href="#perf-memory">11.2 Memory Utilization</a></li>
  <li><a href="#perf-swap">11.3 Swap &amp; Load Average</a></li>
  </ul>
</li>
<li><a href="#sso-health">12. SSO / Identity Source Health</a>
  <ul>
  <li><a href="#sso-domain">12.1 SSO Domain Health</a></li>
  <li><a href="#sso-identity">12.2 Identity Source Connectivity</a></li>
  <li><a href="#sso-ldap">12.3 LDAP / AD Binding Test</a></li>
  <li><a href="#sso-token">12.4 Token Validation</a></li>
  </ul>
</li>
<li><a href="#plugins">13. Plugins &amp; Extensions</a>
  <ul>
  <li><a href="#plugins-list">13.1 Registered Plugins</a></li>
  <li><a href="#plugins-health">13.2 Plugin Health Verification</a></li>
  <li><a href="#plugins-cleanup">13.3 Stale Plugin Cleanup</a></li>
  </ul>
</li>
<li><a href="#lookup-service">14. Lookup Service &amp; PSC</a>
  <ul>
  <li><a href="#ls-registration">14.1 Lookup Service Registration</a></li>
  <li><a href="#ls-sts">14.2 STS Health</a></li>
  <li><a href="#ls-entries">14.3 Service Registration Entries</a></li>
  </ul>
</li>
<li><a href="#inventory">15. Inventory Verification</a>
  <ul>
  <li><a href="#inv-counts">15.1 Datacenter / Cluster / Host / VM Counts</a></li>
  <li><a href="#inv-consistency">15.2 Inventory Consistency</a></li>
  </ul>
</li>
<li><a href="#syslog">16. Syslog &amp; Log Configuration</a>
  <ul>
  <li><a href="#syslog-forward">16.1 Syslog Forwarding</a></li>
  <li><a href="#log-rotation">16.2 Log Rotation</a></li>
  <li><a href="#log-bundle">16.3 Log Bundle Generation</a></li>
  </ul>
</li>
<li><a href="#ntp">17. NTP Configuration</a>
  <ul>
  <li><a href="#ntp-api">17.1 Time Sync via API</a></li>
  <li><a href="#ntp-cli">17.2 Time Sync via CLI</a></li>
  <li><a href="#ntp-drift">17.3 Drift Check</a></li>
  </ul>
</li>
<li><a href="#ports">18. Port Reference Table</a></li>
<li><a href="#common-issues">19. Common Issues &amp; Remediation</a></li>
<li><a href="#cli-reference">20. CLI Quick Reference Card</a></li>
<li><a href="#api-reference">21. API Quick Reference</a></li>
</ul>

</div>


## <span id="overview"></span>1. Overview & Purpose

This handbook provides a **complete, step-by-step health check procedure** for VMware vCenter Server 8.x deployed within a VCF 9.0 environment. It is designed for VMware administrators who need to verify vCenter Server health during:

- **Routine maintenance windows** -- Weekly or monthly proactive checks
- **Pre/post-upgrade validation** -- Before and after vCenter patches or upgrades
- **Incident troubleshooting** -- When service, connectivity, or performance issues occur
- **Environment handover** -- Documenting health state for audits or transfers
- **VCF lifecycle operations** -- Before and after SDDC Manager orchestrated updates

### What This Document Covers

| Area | Components Checked |
|------|--------------------|
| Core Services | VPXD, vmon services, service-control status |
| Appliance Health | VAMI REST API health endpoints for system, memory, storage, load, swap |
| Database | Embedded PostgreSQL health, VCDB size, vacuum status |
| High Availability | VCHA mode, active/passive/witness, failover readiness |
| Certificates | Machine SSL, STS, VECS stores, certificate expiry |
| Storage | Disk partitions, log storage, database storage, filesystem utilization |
| Performance | CPU, memory, swap, load average via API and CLI |
| Identity | SSO domain, identity sources, LDAP/AD binding, token validation |
| Plugins | Registered extensions, plugin health, stale cleanup |
| Lookup Service | Service registrations, STS health, PSC endpoints |
| Inventory | Datacenter/cluster/host/VM counts, consistency |
| Logging | Syslog forwarding, log rotation, log bundle generation |
| Time Sync | NTP configuration, drift check |

### Health Check Methodology

Each check in this handbook follows a consistent format:

1. **What to check** -- Description of the component and why it matters
2. **How to check** -- Exact CLI command or API call (copy-paste ready)
3. **Expected output** -- What a healthy result looks like
4. **Pass / Warn / Fail criteria** -- Clear thresholds with visual indicators
5. **Remediation** -- What to do if the check fails

<div class="info-box">
<strong>Environment Variables:</strong> Throughout this document, replace the following placeholders with your actual values:<br>
<code>$VC_FQDN</code> = vCenter Server FQDN (e.g., vcenter01.lab.local)<br>
<code>$VC_USER</code> = administrator@vsphere.local<br>
<code>$VC_PASS</code> = vCenter SSO administrator password<br>
<code>$VC_TOKEN</code> = Session token obtained via authentication API
</div>



## <span id="prerequisites"></span>2. Prerequisites

### Required Access

| Access Type | Details |
|-------------|---------|
| SSH Access | Root shell access to vCenter Appliance (enable via VAMI if disabled) |
| VAMI Access | https://$VC_FQDN:5480 -- root credentials |
| vSphere Client | https://$VC_FQDN/ui -- administrator@vsphere.local |
| REST API | https://$VC_FQDN/api -- session-based authentication |
| SDDC Manager | For VCF-specific lifecycle checks |

### Required Tools

| Tool | Purpose |
|------|---------|
| `curl` | REST API calls from jump host or local machine |
| `jq` | JSON parsing of API responses |
| `openssl` | Certificate inspection and expiry checks |
| SSH client | Shell access for CLI commands |
| Web browser | VAMI and vSphere Client access |

### Environment Setup

Set these variables before running commands:

```bash
# vCenter connection variables
export VC_FQDN="vcenter01.lab.local"
export VC_USER="administrator@vsphere.local"
export VC_PASS='YourPasswordHere'

# Obtain a session token
export VC_TOKEN=$(curl -sk -X POST \
  "https://${VC_FQDN}/api/session" \
  -u "${VC_USER}:${VC_PASS}" | tr -d '"')

# Verify the token was obtained
echo "Session Token: ${VC_TOKEN}"
```

<div class="warn-box">
<strong>Security Note:</strong> Never store passwords in shell history. Use <code>read -s VC_PASS</code> for interactive password entry. Destroy sessions when finished with: <code>curl -sk -X DELETE "https://${VC_FQDN}/api/session" -H "vmware-api-session-id: ${VC_TOKEN}"</code>
</div>

### Enable SSH on vCenter Appliance

If SSH is not enabled, enable it via VAMI:

1. Navigate to `https://$VC_FQDN:5480`
2. Log in with root credentials
3. Go to **Access** > **SSH Login** > **Edit** > Enable
4. Alternatively via API:

```bash
curl -sk -X PUT \
  "https://${VC_FQDN}/api/appliance/access/ssh" \
  -H "vmware-api-session-id: ${VC_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```



## <span id="quick-reference"></span>3. Quick Reference -- All Checks Summary

| # | Check | Command / Endpoint | Pass | Warn | Fail |
|---|-------|--------------------|------|------|------|
| 4.1 | VPXD Process | `service-control --status vmware-vpxd` | <span class="badge-pass">RUNNING</span> | -- | <span class="badge-fail">STOPPED</span> |
| 5.1 | All vCenter Services | `service-control --status --all` | All STARTED | 1-2 non-critical stopped | <span class="badge-fail">Critical stopped</span> |
| 6.1 | System Health (VAMI) | `/api/appliance/health/system` | <span class="badge-pass">green</span> | <span class="badge-warn">yellow</span> | <span class="badge-fail">orange/red</span> |
| 6.2 | Memory Health | `/api/appliance/health/mem` | <span class="badge-pass">green</span> | <span class="badge-warn">yellow</span> | <span class="badge-fail">orange/red</span> |
| 6.3 | Storage Health | `/api/appliance/health/storage` | <span class="badge-pass">green</span> | <span class="badge-warn">yellow</span> | <span class="badge-fail">orange/red</span> |
| 6.4 | Database Storage | `/api/appliance/health/database-storage` | <span class="badge-pass">green</span> | <span class="badge-warn">yellow</span> | <span class="badge-fail">orange/red</span> |
| 6.5 | CPU Load | `/api/appliance/health/load` | <span class="badge-pass">green</span> | <span class="badge-warn">yellow</span> | <span class="badge-fail">orange/red</span> |
| 6.6 | Swap Health | `/api/appliance/health/swap` | <span class="badge-pass">green</span> | <span class="badge-warn">yellow</span> | <span class="badge-fail">orange/red</span> |
| 6.7 | Software Packages | `/api/appliance/health/softwarepackages` | <span class="badge-pass">green</span> | <span class="badge-warn">yellow</span> | <span class="badge-fail">red</span> |
| 7.1 | PostgreSQL Status | `systemctl status vmware-vpostgres` | <span class="badge-pass">active</span> | -- | <span class="badge-fail">inactive</span> |
| 7.2 | VCDB Size | SQL query | <span class="badge-pass">&lt;50GB</span> | <span class="badge-warn">50-80GB</span> | <span class="badge-fail">&gt;80GB</span> |
| 8.1 | VCHA Mode | `/api/vcenter/vcha/cluster/mode` | <span class="badge-pass">ENABLED</span> | -- | <span class="badge-fail">DISABLED</span> |
| 9.1 | Machine SSL Cert | `openssl` expiry check | <span class="badge-pass">&gt;60 days</span> | <span class="badge-warn">30-60 days</span> | <span class="badge-fail">&lt;30 days</span> |
| 9.3 | STS Certificate | `/usr/lib/vmware-vmca` check | <span class="badge-pass">&gt;60 days</span> | <span class="badge-warn">30-60 days</span> | <span class="badge-fail">&lt;30 days</span> |
| 10.1 | Disk Utilization | `df -h` | <span class="badge-pass">&lt;70%</span> | <span class="badge-warn">70-85%</span> | <span class="badge-fail">&gt;85%</span> |
| 11.1 | CPU Utilization | API + `top` | <span class="badge-pass">&lt;70%</span> | <span class="badge-warn">70-85%</span> | <span class="badge-fail">&gt;85%</span> |
| 11.2 | Memory Utilization | API + `free` | <span class="badge-pass">&lt;80%</span> | <span class="badge-warn">80-90%</span> | <span class="badge-fail">&gt;90%</span> |
| 12.1 | SSO Domain | `sso-config.sh` | <span class="badge-pass">Healthy</span> | -- | <span class="badge-fail">Error</span> |
| 14.1 | Lookup Service | `lstool.py` | <span class="badge-pass">Registered</span> | -- | <span class="badge-fail">Missing</span> |
| 17.1 | NTP Sync | `/api/appliance/ntp` | <span class="badge-pass">Synced</span> | <span class="badge-warn">Drift &gt;1s</span> | <span class="badge-fail">Not configured</span> |



## <span id="vpxd-health"></span>4. VPXD Service Health

The **VPXD** (VMware VirtualCenter Server Daemon) is the core service of vCenter Server. It manages ESXi hosts, virtual machines, storage, and networking. If VPXD is down, the entire vCenter is non-functional.

### <span id="vpxd-process"></span>4.1 VPXD Process Status

#### CLI Check (SSH to vCenter Appliance)

```bash
# Check VPXD service status
service-control --status vmware-vpxd
```

**Expected Output (Healthy):**

```
VMware vCenter Server:Status: RUNNING
```

#### Alternative: systemctl check

```bash
systemctl status vmware-vpxd
```

**Expected Output (Healthy):**

```
● vmware-vpxd.service - VMware vCenter Server
   Loaded: loaded (/usr/lib/systemd/system/vmware-vpxd.service; enabled)
   Active: active (running) since Mon 2026-03-23 10:15:22 UTC; 3 days ago
 Main PID: 5432 (vpxd)
    Tasks: 312
   Memory: 2.1G
   CGroup: /system.slice/vmware-vpxd.service
           └─5432 /usr/lib/vmware-vpxd/vpxd
```

#### API Check

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/services/vmware-vpxd" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq .
```

| Condition | Result | Badge |
|-----------|--------|-------|
| Status = RUNNING, Active (running) | Healthy | <span class="badge-pass">PASS</span> |
| Status = STARTING (briefly during boot) | Transitional | <span class="badge-warn">WARN</span> |
| Status = STOPPED or inactive (dead) | Critical failure | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (VPXD Stopped):</strong><br>
1. Attempt to start: <code>service-control --start vmware-vpxd</code><br>
2. If fails, check logs: <code>tail -200 /var/log/vmware/vpxd/vpxd.log</code><br>
3. Check for port conflicts: <code>netstat -tlnp | grep 443</code><br>
4. Verify database connectivity: <code>systemctl status vmware-vpostgres</code><br>
5. If persistent, restart all services: <code>service-control --stop --all && service-control --start --all</code>
</div>

### <span id="vpxd-restart"></span>4.2 VPXD Restart Procedures

<div class="danger">
<strong>Warning:</strong> Restarting VPXD will disconnect all vSphere Client sessions and temporarily interrupt management operations. VMs continue to run on ESXi hosts unaffected.
</div>

#### Graceful Restart

```bash
# Stop then start VPXD
service-control --stop vmware-vpxd
sleep 10
service-control --start vmware-vpxd

# Verify it came back
service-control --status vmware-vpxd
```

#### Full Service Stack Restart

```bash
# Nuclear option -- restarts all vCenter services
service-control --stop --all
sleep 15
service-control --start --all

# Verify all services
service-control --status --all
```

### <span id="vpxd-logs"></span>4.3 VPXD Log Analysis

#### Key Log Files

| Log File | Purpose |
|----------|---------|
| `/var/log/vmware/vpxd/vpxd.log` | Main VPXD log -- service operations, errors |
| `/var/log/vmware/vpxd/vpxd-alert.log` | Critical alerts only |
| `/var/log/vmware/vpxd/vpxd-profiler.log` | Performance profiling data |
| `/var/log/vmware/vpxd/vpxd-svcs.log` | Service-level operations |

#### Check for Recent Errors

```bash
# Last 50 error entries in VPXD log
grep -i "error\|fatal\|panic\|exception" /var/log/vmware/vpxd/vpxd.log | tail -50
```

```bash
# Check for crash indicators
grep -c "core dump\|segfault\|SIGABRT" /var/log/vmware/vpxd/vpxd.log
```

```bash
# Check VPXD alert log
cat /var/log/vmware/vpxd/vpxd-alert.log | tail -20
```

**Expected Output (Healthy):** No recent fatal errors, no crash indicators, alert log empty or minimal entries.

| Condition | Badge |
|-----------|-------|
| No errors or only informational entries | <span class="badge-pass">PASS</span> |
| Warning-level entries present | <span class="badge-warn">WARN</span> |
| Fatal/crash/exception entries in last 24h | <span class="badge-fail">FAIL</span> |



## <span id="vcenter-services"></span>5. vCenter Services Status

### <span id="vmon-cli"></span>5.1 vmon-cli Service Listing

The `vmon-cli` utility manages vCenter services at the vMon (VMware Service Lifecycle Manager) level.

#### List All Services

```bash
vmon-cli --list
```

**Expected Output (Healthy):**

```
analyticss        STARTED
applmgmt          STARTED
certificateauthority STARTED
certificatemanagement STARTED
cis-license       STARTED
content-library   STARTED
eam               STARTED
envoy             STARTED
hvc               STARTED
imagebuilder      STARTED
infraprofile      STARTED
lookupsvc         STARTED
netdumper         STARTED
observability     STARTED
perfcharts        STARTED
pschealth         STARTED
rbd               STARTED
rhttpproxy        STARTED
sca               STARTED
sps               STARTED
statsmonitor      STARTED
sts               STARTED
topologysvc       STARTED
trustmanagement   STARTED
updatemgr         STARTED
vapi-endpoint     STARTED
vcha              STARTED
vlcm              STARTED
vmcam             STARTED
vmonapi           STARTED
vmware-vpostgres  STARTED
vpxd              STARTED
vpxd-svcs         STARTED
vsan-health       STARTED
vsm               STARTED
vsphere-ui        STARTED
vstats            STARTED
vtsdb             STARTED
wcp               STARTED
```

#### Check Specific Service Status

```bash
# Check a single service
vmon-cli --status vpxd

# Check multiple services
for svc in vpxd lookupsvc sts vmware-vpostgres vsphere-ui; do
  echo "$svc: $(vmon-cli --status $svc)"
done
```

### <span id="service-control"></span>5.2 service-control Commands

#### Check All Services Status

```bash
service-control --status --all
```

**Expected Output (Healthy):**

```
VMware vCenter Server:Status: RUNNING
VMware vAPI Endpoint:Status: RUNNING
VMware Content Library:Status: RUNNING
VMware Certificate Authority:Status: RUNNING
VMware Identity Management Service:Status: RUNNING
VMware Lookup Service:Status: RUNNING
VMware Security Token Service:Status: RUNNING
VMware vSphere Client:Status: RUNNING
VMware vSphere Update Manager:Status: RUNNING
VMware PostgreSQL:Status: RUNNING
VMware HTTP Reverse Proxy:Status: RUNNING
VMware Envoy Service:Status: RUNNING
...
(all services RUNNING)
```

#### Start / Stop / Restart Individual Services

```bash
# Stop a specific service
service-control --stop vmware-updatemgr

# Start a specific service
service-control --start vmware-updatemgr

# Restart a specific service (stop + start)
service-control --stop vmware-vsphere-ui && service-control --start vmware-vsphere-ui
```

### <span id="critical-services"></span>5.3 Critical vs Non-Critical Services

| Service | Criticality | Impact if Stopped |
|---------|-------------|-------------------|
| `vpxd` | **CRITICAL** | vCenter completely non-functional |
| `vmware-vpostgres` | **CRITICAL** | Database unavailable, all services fail |
| `vmware-sts` | **CRITICAL** | SSO authentication fails, no logins |
| `lookupsvc` | **CRITICAL** | Service discovery fails |
| `rhttpproxy` | **CRITICAL** | All HTTPS endpoints inaccessible |
| `envoy` | **CRITICAL** | Reverse proxy down, API unreachable |
| `vpxd-svcs` | HIGH | vCenter sub-services degraded |
| `vsphere-ui` | HIGH | vSphere Client (HTML5) unavailable |
| `vapi-endpoint` | HIGH | REST API unavailable |
| `vmware-sps` | MEDIUM | Storage profile service down |
| `content-library` | MEDIUM | Content library operations fail |
| `updatemgr` | MEDIUM | vSphere Lifecycle Manager offline |
| `vlcm` | MEDIUM | Lifecycle operations unavailable |
| `eam` | MEDIUM | ESX Agent Manager down |
| `perfcharts` | LOW | Performance charts unavailable |
| `imagebuilder` | LOW | Image building unavailable |
| `vstats` | LOW | vStats collection paused |
| `netdumper` | LOW | Network core dump receiver offline |
| `analytics` | LOW | CEIP analytics paused |

| Condition | Badge |
|-----------|-------|
| All services RUNNING | <span class="badge-pass">PASS</span> |
| 1-2 LOW/MEDIUM services stopped | <span class="badge-warn">WARN</span> |
| Any CRITICAL/HIGH service stopped | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (Services Stopped):</strong><br>
1. Start individual service: <code>service-control --start &lt;service-name&gt;</code><br>
2. If dependency failure, start all: <code>service-control --start --all</code><br>
3. Check service logs: <code>journalctl -u &lt;service-name&gt; --no-pager -n 100</code><br>
4. Last resort full restart: <code>reboot</code> (from appliance shell)
</div>



## <span id="vami-health"></span>6. vCenter Appliance Health (VAMI)

The VAMI (vCenter Server Appliance Management Interface) REST API provides health status for all key appliance subsystems. These endpoints return standardized color-coded health states: `green`, `yellow`, `orange`, `red`, `gray`.

<div class="info-box">
<strong>Health Color Key:</strong><br>
<code>green</code> = Healthy | <code>yellow</code> = Warning, degraded | <code>orange</code> = Degraded, action needed | <code>red</code> = Critical failure | <code>gray</code> = Unknown / not available
</div>

### <span id="vami-system"></span>6.1 System Health

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/health/system" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
```

**Expected Output:**

```
"green"
```

#### Detailed System Health (with messages)

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/health/system?messages=true" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq .
```

| Condition | Badge |
|-----------|-------|
| `"green"` | <span class="badge-pass">PASS</span> |
| `"yellow"` | <span class="badge-warn">WARN</span> |
| `"orange"` or `"red"` | <span class="badge-fail">FAIL</span> |

### <span id="vami-memory"></span>6.2 Memory Health

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/health/mem" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
```

**Expected Output:**

```
"green"
```

| Condition | Threshold | Badge |
|-----------|-----------|-------|
| `"green"` | Memory utilization < 80% | <span class="badge-pass">PASS</span> |
| `"yellow"` | Memory utilization 80-95% | <span class="badge-warn">WARN</span> |
| `"orange"` / `"red"` | Memory utilization > 95% or OOM | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (Memory Warning/Critical):</strong><br>
1. Check top memory consumers: SSH to appliance, run <code>top -o %MEM</code><br>
2. Restart heavy services: <code>service-control --stop vmware-vpxd && service-control --start vmware-vpxd</code><br>
3. Check for memory leaks in VPXD: <code>grep -i "out of memory\|oom" /var/log/vmware/vpxd/vpxd.log</code><br>
4. If persistent, increase appliance VM memory allocation (requires shutdown)
</div>

### <span id="vami-storage"></span>6.3 Storage Health

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/health/storage" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
```

**Expected Output:**

```
"green"
```

| Condition | Threshold | Badge |
|-----------|-----------|-------|
| `"green"` | All partitions below warning threshold | <span class="badge-pass">PASS</span> |
| `"yellow"` | One or more partitions 70-85% full | <span class="badge-warn">WARN</span> |
| `"orange"` / `"red"` | Partitions > 85% full | <span class="badge-fail">FAIL</span> |

### <span id="vami-database"></span>6.4 Database Storage Health

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/health/database-storage" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
```

**Expected Output:**

```
"green"
```

| Condition | Threshold | Badge |
|-----------|-----------|-------|
| `"green"` | DB storage utilization < 70% | <span class="badge-pass">PASS</span> |
| `"yellow"` | DB storage utilization 70-85% | <span class="badge-warn">WARN</span> |
| `"orange"` / `"red"` | DB storage utilization > 85% | <span class="badge-fail">FAIL</span> |

### <span id="vami-load"></span>6.5 CPU Load Health

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/health/load" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
```

**Expected Output:**

```
"green"
```

| Condition | Threshold | Badge |
|-----------|-----------|-------|
| `"green"` | Load average within normal range | <span class="badge-pass">PASS</span> |
| `"yellow"` | Load average elevated | <span class="badge-warn">WARN</span> |
| `"orange"` / `"red"` | Load critically high | <span class="badge-fail">FAIL</span> |

### <span id="vami-swap"></span>6.6 Swap Health

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/health/swap" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
```

**Expected Output:**

```
"green"
```

| Condition | Threshold | Badge |
|-----------|-----------|-------|
| `"green"` | Swap usage minimal or zero | <span class="badge-pass">PASS</span> |
| `"yellow"` | Swap usage moderate | <span class="badge-warn">WARN</span> |
| `"orange"` / `"red"` | Swap usage critically high | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (Swap Critical):</strong><br>
1. Check swap usage: <code>free -m</code> and <code>swapon --show</code><br>
2. Identify swap-heavy processes: <code>for pid in /proc/[0-9]*; do awk '/VmSwap/{print FILENAME,$0}' $pid/status 2>/dev/null; done | sort -k3 -rn | head -20</code><br>
3. If persistent, increase VM memory and reduce swap pressure by restarting services
</div>

### <span id="vami-software"></span>6.7 Software Packages Health

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/health/softwarepackages" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
```

**Expected Output:**

```
"green"
```

| Condition | Badge |
|-----------|-------|
| `"green"` -- All packages consistent | <span class="badge-pass">PASS</span> |
| `"yellow"` -- Minor package inconsistencies | <span class="badge-warn">WARN</span> |
| `"red"` -- Package corruption or missing packages | <span class="badge-fail">FAIL</span> |

#### Comprehensive VAMI Health Script

Run all health checks at once:

```bash
echo "=== vCenter Appliance Health Summary ==="
for endpoint in system mem storage database-storage load swap softwarepackages; do
  result=$(curl -sk -X GET \
    "https://${VC_FQDN}/api/appliance/health/${endpoint}" \
    -H "vmware-api-session-id: ${VC_TOKEN}" | tr -d '"')
  printf "%-25s : %s\n" "$endpoint" "$result"
done
```

**Expected Output (All Healthy):**

```
=== vCenter Appliance Health Summary ===
system                    : green
mem                       : green
storage                   : green
database-storage          : green
load                      : green
swap                      : green
softwarepackages          : green
```



## <span id="database-health"></span>7. Database Health

vCenter Server 8.x uses an embedded PostgreSQL database (vPostgres) for all configuration and inventory data. Database health is foundational to vCenter operations.

### <span id="db-postgres"></span>7.1 PostgreSQL Embedded DB Status

#### Service Status

```bash
# Check vPostgres service
systemctl status vmware-vpostgres
```

**Expected Output (Healthy):**

```
● vmware-vpostgres.service - VMware Postgres
   Loaded: loaded (/usr/lib/systemd/system/vmware-vpostgres.service; enabled)
   Active: active (running) since Mon 2026-03-23 10:14:55 UTC; 3 days ago
 Main PID: 4821 (postgres)
    Tasks: 48
   Memory: 512.3M
   CGroup: /system.slice/vmware-vpostgres.service
           ├─4821 /opt/vmware/vpostgres/current/bin/postgres -D /storage/db/vpostgres
           ├─4910 postgres: checkpointer
           ├─4911 postgres: background writer
           └─ ...
```

#### Test Database Connectivity

```bash
# Connect to VCDB and run a basic query
/opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB -c "SELECT version();"
```

**Expected Output:**

```
                                                  version
------------------------------------------------------------------------------------------------------------
 PostgreSQL 14.x (VMware Postgres 14.x) on x86_64-unknown-linux-gnu, compiled by gcc ...
(1 row)
```

| Condition | Badge |
|-----------|-------|
| Service active (running), query succeeds | <span class="badge-pass">PASS</span> |
| Service active but slow queries | <span class="badge-warn">WARN</span> |
| Service inactive or query fails | <span class="badge-fail">FAIL</span> |

### <span id="db-size"></span>7.2 VCDB Size Monitoring

```bash
# Check total VCDB size
/opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB -c \
  "SELECT pg_size_pretty(pg_database_size('VCDB')) AS db_size;"
```

**Expected Output:**

```
 db_size
---------
 12 GB
(1 row)
```

#### Top Tables by Size

```bash
/opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB -c "
SELECT
  schemaname || '.' || tablename AS table_full_name,
  pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS total_size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC
LIMIT 15;"
```

**Expected Output:**

```
         table_full_name          | total_size
----------------------------------+------------
 vc.vpx_event_arg                 | 3200 MB
 vc.vpx_event                     | 2100 MB
 vc.vpx_task_event                | 1800 MB
 vc.vpx_stat_counter              | 980 MB
 vc.vpx_task                      | 850 MB
 ...
(15 rows)
```

| Condition | Badge |
|-----------|-------|
| VCDB size < 50 GB | <span class="badge-pass">PASS</span> |
| VCDB size 50 - 80 GB | <span class="badge-warn">WARN</span> |
| VCDB size > 80 GB | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (Database Too Large):</strong><br>
1. Purge old events and tasks via vSphere Client: <b>Administration > vCenter Server Settings > Runtime Settings</b><br>
2. Reduce task and event retention: set <code>task.maxAge</code> and <code>event.maxAge</code> to 30 days<br>
3. Manual cleanup (careful!): <code>/opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB -c "DELETE FROM vc.vpx_event WHERE create_time < NOW() - INTERVAL '30 days';"</code><br>
4. Run vacuum afterward: <code>/opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB -c "VACUUM FULL ANALYZE;"</code>
</div>

### <span id="db-vacuum"></span>7.3 Vacuum & Maintenance

#### Check Last Vacuum Time

```bash
/opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB -c "
SELECT
  schemaname || '.' || relname AS table_name,
  last_vacuum,
  last_autovacuum,
  last_analyze,
  n_dead_tup
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC
LIMIT 10;"
```

**Expected Output:**

```
       table_name        |      last_vacuum      |   last_autovacuum    |     last_analyze      | n_dead_tup
-------------------------+-----------------------+----------------------+-----------------------+------------
 vc.vpx_event_arg        | 2026-03-25 02:00:01   | 2026-03-25 14:30:22  | 2026-03-25 02:00:01   |       2341
 vc.vpx_event            | 2026-03-25 02:00:01   | 2026-03-25 14:28:11  | 2026-03-25 02:00:01   |       1822
 ...
```

#### Manual Vacuum (if needed)

```bash
# Standard vacuum (non-blocking)
/opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB -c "VACUUM ANALYZE;"

# Full vacuum (blocking, reclaims space)
/opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB -c "VACUUM FULL ANALYZE;"
```

<div class="warn-box">
<strong>Warning:</strong> <code>VACUUM FULL</code> acquires an exclusive lock on each table and rewrites the entire table. Only run during a maintenance window. Standard <code>VACUUM ANALYZE</code> is safe to run at any time.
</div>

| Condition | Badge |
|-----------|-------|
| Autovacuum ran in last 24h, dead tuples < 10,000 | <span class="badge-pass">PASS</span> |
| Autovacuum > 48h ago or dead tuples 10,000 - 100,000 | <span class="badge-warn">WARN</span> |
| No vacuum in 7+ days or dead tuples > 100,000 | <span class="badge-fail">FAIL</span> |



## <span id="vcha"></span>8. vCenter HA (VCHA)

vCenter High Availability (VCHA) provides automated failover for vCenter Server using an active/passive/witness architecture.

### <span id="vcha-mode"></span>8.1 VCHA Mode & Status

#### API Check

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/vcha/cluster/mode" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq .
```

**Expected Output (VCHA Enabled):**

```json
{
  "mode": "ENABLED"
}
```

#### Get Full VCHA Cluster Status

```bash
curl -sk -X POST \
  "https://${VC_FQDN}/api/vcenter/vcha/cluster?action=get" \
  -H "vmware-api-session-id: ${VC_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"partial": false}' | jq .
```

**Expected Output (Healthy VCHA):**

```json
{
  "config_state": "CONFIGURED",
  "mode": "ENABLED",
  "health_state": "HEALTHY",
  "node1": {
    "state": "UP",
    "role": "ACTIVE",
    "runtime": {
      "ip": {
        "ipv4": { "address": "10.0.0.101" }
      }
    }
  },
  "node2": {
    "state": "UP",
    "role": "PASSIVE",
    "runtime": {
      "ip": {
        "ipv4": { "address": "10.0.0.102" }
      }
    }
  },
  "witness": {
    "state": "UP",
    "runtime": {
      "ip": {
        "ipv4": { "address": "10.0.0.103" }
      }
    }
  }
}
```

| Condition | Badge |
|-----------|-------|
| mode=ENABLED, health_state=HEALTHY, all nodes UP | <span class="badge-pass">PASS</span> |
| mode=ENABLED but one node degraded | <span class="badge-warn">WARN</span> |
| mode=DISABLED or health_state not HEALTHY | <span class="badge-fail">FAIL</span> |

### <span id="vcha-nodes"></span>8.2 Active / Passive / Witness Status

#### CLI Check (from Active Node)

```bash
# Check VCHA state via CLI
/usr/lib/vmware-vcha/vcha-cli cluster-get-state
```

**Expected Output:**

```
VCHA Cluster State: HEALTHY
Active Node State: UP
Passive Node State: UP
Witness Node State: UP
Replication State: IN_SYNC
```

#### Database Replication Lag

```bash
# Check replication lag from active node
/opt/vmware/vpostgres/current/bin/psql -U postgres -c \
  "SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn,
   (sent_lsn - replay_lsn) AS replication_lag
   FROM pg_stat_replication;"
```

| Condition | Badge |
|-----------|-------|
| Replication state IN_SYNC, lag = 0 | <span class="badge-pass">PASS</span> |
| Replication active but lag > 0 | <span class="badge-warn">WARN</span> |
| Replication not running | <span class="badge-fail">FAIL</span> |

### <span id="vcha-failover"></span>8.3 Failover Readiness

#### Manual Failover Test (Planned)

<div class="danger">
<strong>Warning:</strong> Only perform planned failover during a maintenance window. This will temporarily disconnect all vSphere Client sessions.
</div>

```bash
# Initiate planned failover via API
curl -sk -X POST \
  "https://${VC_FQDN}/api/vcenter/vcha/cluster?action=failover" \
  -H "vmware-api-session-id: ${VC_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"planned": true}'
```

<div class="fix-box">
<strong>Remediation (VCHA Degraded):</strong><br>
1. Check network connectivity between all three VCHA nodes (HA network)<br>
2. Verify passive node is reachable: <code>ping &lt;passive-ip&gt;</code><br>
3. Verify witness node is reachable: <code>ping &lt;witness-ip&gt;</code><br>
4. Check VCHA logs: <code>/var/log/vmware/vcha/vcha.log</code><br>
5. If passive node offline, redeploy: remove and re-add VCHA via vSphere Client
</div>



## <span id="certificate-health"></span>9. Certificate Health

Certificate expiry is one of the most common causes of vCenter outages. Regular monitoring of all certificate stores is essential.

### <span id="cert-manager"></span>9.1 Certificate Manager Tool

```bash
# Launch Certificate Manager (interactive)
/usr/lib/vmware-vmca/bin/certificate-manager
```

This interactive tool provides options:
1. Replace Machine SSL certificate with Custom Certificate
2. Replace VMCA Root certificate with Custom Signing Certificate
3. Replace Machine SSL certificate with VMCA Certificate
4. Regenerate a new VMCA Root Certificate
5. Replace Solution user certificates with Custom Certificate
6. Replace Solution user certificates with VMCA certificates
7. Revert last performed operation
8. Reset all Certificates

### <span id="cert-vecs"></span>9.2 VECS Store Listing

#### List All VECS Stores

```bash
/usr/lib/vmware-vmafd/bin/vecs-cli store list
```

**Expected Output:**

```
MACHINE_SSL_CERT
TRUSTED_ROOTS
TRUSTED_ROOT_CRLS
machine
vsphere-webclient
vpxd
vpxd-extension
hvc
data-encipherment
APPLMGMT_PASSWORD
SMS
wcp
backup_store
```

#### List Certificates in a Store

```bash
# List Machine SSL certificate
/usr/lib/vmware-vmafd/bin/vecs-cli entry list --store MACHINE_SSL_CERT
```

**Expected Output:**

```
Alias : __MACHINE_CERT
Entry type : Private Key
```

#### Get Certificate Details from a Store

```bash
/usr/lib/vmware-vmafd/bin/vecs-cli entry getcert \
  --store MACHINE_SSL_CERT --alias __MACHINE_CERT | \
  openssl x509 -noout -subject -issuer -dates -serial
```

**Expected Output:**

```
subject=CN = vcenter01.lab.local
issuer=CN = CA, DC = vsphere, DC = local, C = US, ST = California, O = lab.local
notBefore=Jan 15 00:00:00 2026 GMT
notAfter=Jan 15 00:00:00 2028 GMT
serial=3A4B5C6D7E8F
```

### <span id="cert-sts"></span>9.3 STS Certificate

The Security Token Service (STS) signing certificate is critical for SSO authentication.

#### Check STS Certificate Expiry

```bash
# Extract and check the STS signing certificate
/usr/lib/vmware-vmafd/bin/dir-cli trustedcert list \
  --login administrator@vsphere.local \
  --password "${VC_PASS}" | head -20
```

#### Alternative: Check via Lookup Service

```bash
# Get STS certificate from LDAP
/usr/lib/vmware-vmdir/bin/ldapsearch -h localhost -p 389 \
  -b "cn=TenantCredential-1,cn=local,cn=Tenants,cn=IdentityManager,cn=Services,dc=vsphere,dc=local" \
  -D "cn=administrator,cn=users,dc=vsphere,dc=local" \
  -w "${VC_PASS}" \
  userCertificate 2>/dev/null | grep -A1 "userCertificate"
```

#### Check STS Token Signing Certificate with Python Script

```bash
# VMware-provided STS cert check script
python /usr/lib/vmware-vmca/share/config/checksts.py
```

**Expected Output (Healthy):**

```
STS signing certificate:
  Subject: CN=ssoserver-sign
  Not Before: Jan 15 00:00:00 2026 GMT
  Not After:  Jan 15 00:00:00 2028 GMT
  Days remaining: 661
  Status: VALID
```

| Condition | Badge |
|-----------|-------|
| STS cert > 60 days until expiry | <span class="badge-pass">PASS</span> |
| STS cert 30 - 60 days until expiry | <span class="badge-warn">WARN</span> |
| STS cert < 30 days or expired | <span class="badge-fail">FAIL</span> |

### <span id="cert-machine"></span>9.4 Machine SSL Certificate

```bash
# Check Machine SSL cert expiry remotely
echo | openssl s_client -connect ${VC_FQDN}:443 -servername ${VC_FQDN} 2>/dev/null | \
  openssl x509 -noout -subject -issuer -dates -checkend 2592000
```

**Expected Output (Healthy):**

```
subject=CN = vcenter01.lab.local
issuer=CN = CA, DC = vsphere, DC = local
notBefore=Jan 15 00:00:00 2026 GMT
notAfter=Jan 15 00:00:00 2028 GMT
Certificate will not expire
```

#### Check Expiry of All Solution User Certificates

```bash
for store in machine vsphere-webclient vpxd vpxd-extension; do
  echo "=== Store: ${store} ==="
  /usr/lib/vmware-vmafd/bin/vecs-cli entry getcert \
    --store ${store} --alias ${store} 2>/dev/null | \
    openssl x509 -noout -subject -dates 2>/dev/null
done
```

### <span id="cert-expiry"></span>9.5 Expiry Checks -- All Certificates

#### Comprehensive Certificate Expiry Report

```bash
# Check all VECS stores for certificate expiry
for store in $(/usr/lib/vmware-vmafd/bin/vecs-cli store list); do
  for alias in $(/usr/lib/vmware-vmafd/bin/vecs-cli entry list --store ${store} 2>/dev/null | grep "Alias" | awk '{print $3}'); do
    CERT=$(/usr/lib/vmware-vmafd/bin/vecs-cli entry getcert --store ${store} --alias ${alias} 2>/dev/null)
    if [ -n "$CERT" ]; then
      EXPIRY=$(echo "$CERT" | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
      DAYS=$(echo "$CERT" | openssl x509 -noout -checkend 0 2>/dev/null && echo "VALID" || echo "EXPIRED")
      printf "Store: %-25s Alias: %-25s Expires: %-30s Status: %s\n" "$store" "$alias" "$EXPIRY" "$DAYS"
    fi
  done
done
```

#### API-based Certificate Check

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/certificate-management/vcenter/tls" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq '{
    subject: .subject_dn,
    issuer: .issuer_dn,
    valid_from: .valid_from,
    valid_to: .valid_to
  }'
```

**Expected Output:**

```json
{
  "subject": "CN=vcenter01.lab.local",
  "issuer": "CN=CA, DC=vsphere, DC=local",
  "valid_from": "2026-01-15T00:00:00.000Z",
  "valid_to": "2028-01-15T00:00:00.000Z"
}
```

| Condition | Badge |
|-----------|-------|
| All certificates > 60 days until expiry | <span class="badge-pass">PASS</span> |
| Any certificate 30 - 60 days until expiry | <span class="badge-warn">WARN</span> |
| Any certificate < 30 days or expired | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (Certificate Expiring/Expired):</strong><br>
1. For Machine SSL: Use Certificate Manager option 3 or 1 to replace<br>
2. For STS: Use <code>/usr/lib/vmware-vmca/bin/certificate-manager</code> option 8 (reset) as last resort<br>
3. For Solution Users: Use Certificate Manager option 6 to regenerate with VMCA<br>
4. KB Reference: <a href="https://knowledge.broadcom.com/external/article?legacyId=2111411">KB 2111411</a> for STS certificate renewal
</div>



## <span id="storage-health"></span>10. Storage Health

### <span id="disk-partitions"></span>10.1 Disk Partitions & Filesystem

#### Check All Partitions

```bash
df -h
```

**Expected Output (Healthy):**

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda3        11G  4.2G  6.1G  41% /
tmpfs           6.0G   48M  5.9G   1% /dev/shm
/dev/sda1       128M   32M   97M  25% /boot
/dev/sda5        25G  5.8G   18G  25% /storage/log
/dev/sda6        10G  2.1G  7.4G  22% /storage/db
/dev/sda8        50G  9.2G   38G  20% /storage/seat
/dev/sda9        25G  3.3G   20G  15% /storage/netdump
/dev/sda10       10G  1.2G  8.2G  13% /storage/autodeploy
/dev/sda11       10G  836M  8.6G   9% /storage/imagebuilder
/dev/sda12       10G  2.5G  7.0G  27% /storage/updatemgr
/dev/sda13        5G   63M  4.7G   2% /storage/lifecycle
```

#### Check inode Usage

```bash
df -ih
```

| Partition | Warn Threshold | Fail Threshold | Badge (Healthy) |
|-----------|---------------|----------------|-----------------|
| `/` (root) | > 70% | > 85% | <span class="badge-pass">PASS</span> |
| `/storage/log` | > 70% | > 85% | <span class="badge-pass">PASS</span> |
| `/storage/db` | > 70% | > 85% | <span class="badge-pass">PASS</span> |
| `/storage/seat` | > 70% | > 85% | <span class="badge-pass">PASS</span> |
| All others | > 75% | > 90% | <span class="badge-pass">PASS</span> |

### <span id="log-storage"></span>10.2 Log Storage Utilization

```bash
# Check /storage/log usage
du -sh /storage/log/* 2>/dev/null | sort -rh | head -15
```

**Expected Output:**

```
2.1G    /storage/log/vmware/vpxd
812M    /storage/log/vmware/vsphere-ui
543M    /storage/log/vmware/sso
322M    /storage/log/vmware/eam
210M    /storage/log/vmware/rhttpproxy
...
```

#### Find Large Log Files

```bash
find /storage/log -type f -size +100M -exec ls -lh {} \; 2>/dev/null
```

### <span id="db-storage"></span>10.3 DB Storage Utilization

```bash
# Check /storage/db usage
du -sh /storage/db/*
```

**Expected Output:**

```
8.2G    /storage/db/vpostgres
```

```bash
# Check PostgreSQL WAL files
du -sh /storage/db/vpostgres/pg_wal/
```

| Condition | Badge |
|-----------|-------|
| All partitions < 70% | <span class="badge-pass">PASS</span> |
| Any partition 70 - 85% | <span class="badge-warn">WARN</span> |
| Any partition > 85% | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (Storage Full):</strong><br>
1. Clear old logs: <code>find /storage/log -name "*.log" -mtime +7 -delete</code><br>
2. Rotate logs: <code>logrotate -f /etc/logrotate.conf</code><br>
3. Clean temp files: <code>rm -rf /storage/log/vmware/vpxd/vpxd-*.log.[0-9]*</code><br>
4. Purge old WAL files: <code>/opt/vmware/vpostgres/current/bin/pg_archivecleanup /storage/db/vpostgres/pg_wal/ &lt;oldest_needed_wal&gt;</code><br>
5. Expand disk: Shutdown appliance, expand VMDK, boot, run <code>/usr/lib/applmgmt/support/scripts/expand_disk.sh</code>
</div>



## <span id="performance"></span>11. Performance & Resource Utilization

### <span id="perf-cpu"></span>11.1 CPU Utilization

#### API Check

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/health/load" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
```

#### CLI Check

```bash
# Current CPU load
uptime
```

**Expected Output:**

```
 14:22:33 up 3 days,  4:07,  1 user,  load average: 1.23, 1.45, 1.32
```

```bash
# Top CPU consumers
top -bn1 | head -20
```

```bash
# CPU info
nproc
cat /proc/cpuinfo | grep "model name" | head -1
```

| Condition | Badge |
|-----------|-------|
| Load average < number of CPUs (< 70% per core) | <span class="badge-pass">PASS</span> |
| Load average 70-85% of CPU count | <span class="badge-warn">WARN</span> |
| Load average > 85% of CPU count sustained | <span class="badge-fail">FAIL</span> |

### <span id="perf-memory"></span>11.2 Memory Utilization

#### API Check

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/health/mem" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
```

#### CLI Check

```bash
free -m
```

**Expected Output (Healthy):**

```
              total        used        free      shared  buff/cache   available
Mem:          24576       14234        2180         312        8162        9876
Swap:          3071          32        3039
```

```bash
# Memory usage percentage
free -m | awk 'NR==2{printf "Memory Usage: %.1f%%\n", $3*100/$2}'
```

| Condition | Badge |
|-----------|-------|
| Memory usage < 80% | <span class="badge-pass">PASS</span> |
| Memory usage 80 - 90% | <span class="badge-warn">WARN</span> |
| Memory usage > 90% | <span class="badge-fail">FAIL</span> |

### <span id="perf-swap"></span>11.3 Swap & Load Average

```bash
# Swap usage
swapon --show
```

**Expected Output (Healthy):**

```
NAME      TYPE SIZE USED PRIO
/dev/sda2 partition 3G  32M   -2
```

```bash
# Detailed swap info
cat /proc/swaps
vmstat 1 5
```

| Condition | Badge |
|-----------|-------|
| Swap usage < 5% | <span class="badge-pass">PASS</span> |
| Swap usage 5 - 25% | <span class="badge-warn">WARN</span> |
| Swap usage > 25% | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (Performance Degradation):</strong><br>
1. Identify top consumers: <code>top -bn1 -o %MEM | head -20</code><br>
2. Restart heavy service: <code>service-control --stop vmware-vpxd && service-control --start vmware-vpxd</code><br>
3. Check for runaway Java processes: <code>ps aux | grep java | grep -v grep</code><br>
4. Increase VM resources: Add more vCPUs or memory to the appliance VM<br>
5. Check for DRS/HA tasks in loop: review <code>/var/log/vmware/vpxd/vpxd.log</code> for repeated task patterns
</div>



## <span id="sso-health"></span>12. SSO / Identity Source Health

### <span id="sso-domain"></span>12.1 SSO Domain Health

#### Check SSO Domain Status

```bash
# List SSO domains
/opt/vmware/bin/sso-config.sh -get_identity_sources
```

**Expected Output:**

```
Identity Source: vsphere.local
Type: System Domain
Default: true

Identity Source: lab.local
Type: ActiveDirectory
Default: false
```

#### Verify SSO Configuration

```bash
/opt/vmware/bin/sso-config.sh -get_default_identity_sources
```

### <span id="sso-identity"></span>12.2 Identity Source Connectivity

#### API Check

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/identity/providers" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq .
```

#### Test Authentication

```bash
# Test SSO login via API session creation
curl -sk -w "\nHTTP_CODE: %{http_code}\n" -X POST \
  "https://${VC_FQDN}/api/session" \
  -u "administrator@vsphere.local:${VC_PASS}"
```

**Expected Output (Healthy):**

```
"b1a2c3d4-e5f6-7890-abcd-ef1234567890"
HTTP_CODE: 201
```

| Condition | Badge |
|-----------|-------|
| HTTP 201, session token returned | <span class="badge-pass">PASS</span> |
| HTTP 401 (credentials issue) | <span class="badge-warn">WARN</span> |
| HTTP 500 or connection timeout | <span class="badge-fail">FAIL</span> |

### <span id="sso-ldap"></span>12.3 LDAP / AD Binding Test

#### Test LDAP Connectivity

```bash
# Test LDAP bind to AD (if AD identity source configured)
ldapsearch -h dc01.lab.local -p 389 \
  -D "CN=svc_vcenter,OU=Service Accounts,DC=lab,DC=local" \
  -w 'ServiceAccountPassword' \
  -b "DC=lab,DC=local" \
  -s base "(objectClass=*)" 2>&1 | head -5
```

**Expected Output (Healthy):**

```
# extended LDIF
#
# LDAPv3
# base <DC=lab,DC=local> with scope baseObject
# filter: (objectClass=*)
```

#### Check VMware Directory Service (vmdir)

```bash
# Check vmdir service status
systemctl status vmware-stsd
/opt/vmware/bin/ldapsearch -h localhost -p 389 \
  -b "" -s base "(objectClass=*)" namingContexts 2>/dev/null
```

### <span id="sso-token"></span>12.4 Token Validation

```bash
# Verify existing session token is valid
curl -sk -X GET \
  "https://${VC_FQDN}/api/session" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq .
```

**Expected Output (Valid Token):**

```json
{
  "user": "VSPHERE.LOCAL\\Administrator",
  "created_time": "2026-03-26T10:15:22.000Z"
}
```

| Condition | Badge |
|-----------|-------|
| Token valid, user details returned | <span class="badge-pass">PASS</span> |
| Token expired (HTTP 401) | <span class="badge-warn">WARN</span> |
| SSO service unreachable (HTTP 503) | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (SSO Issues):</strong><br>
1. Restart STS service: <code>service-control --stop vmware-stsd && service-control --start vmware-stsd</code><br>
2. Check STS logs: <code>tail -100 /var/log/vmware/sso/ssoAdminServer.log</code><br>
3. For AD connectivity: verify DNS, network, service account credentials<br>
4. For lockout: unlock admin via <code>/usr/lib/vmware-vmdir/bin/dir-cli password reset --account administrator --new &lt;new_pass&gt;</code><br>
5. STS cert expiry: Replace using KB 79248 procedures
</div>



## <span id="plugins"></span>13. Plugins & Extensions

### <span id="plugins-list"></span>13.1 Registered Plugins

#### API Check

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/namespace-management/software/registries" \
  -H "vmware-api-session-id: ${VC_TOKEN}" 2>/dev/null | jq .
```

#### MOB (Managed Object Browser) Method

Navigate to: `https://$VC_FQDN/mob/?moid=ExtensionManager&doPath=extensionList`

#### PowerCLI Method

```powershell
Connect-VIServer -Server $VC_FQDN -User $VC_USER -Password $VC_PASS
$em = Get-View ExtensionManager
$em.ExtensionList | Select-Object Key, Description, Company, Version | Format-Table -AutoSize
```

**Expected Output:**

```
Key                                      Description              Company              Version
---                                      -----------              -------              -------
com.vmware.vim.sms                       Storage Monitoring       VMware, Inc.         8.0.3
com.vmware.vcIntegrity                   vSphere Lifecycle Mgr    VMware, Inc.         8.0.3
com.vmware.vim.eam                       ESX Agent Manager        VMware, Inc.         8.0.3
com.vmware.rbd                           RBD                      VMware, Inc.         8.0.3
com.vmware.h4.vsphere.client             vSphere Client           VMware, Inc.         8.0.3
com.vmware.nsx.management.nsxt           NSX                      VMware, Inc.         4.2.1
...
```

### <span id="plugins-health"></span>13.2 Plugin Health Verification

```bash
# Check plugin health via REST
curl -sk -X GET \
  "https://${VC_FQDN}/ui/extensionmanager/extensionlist" \
  -H "vmware-api-session-id: ${VC_TOKEN}" 2>/dev/null | jq '.[].key'
```

#### Check for Plugin Load Errors

```bash
# Check vsphere-ui logs for plugin errors
grep -i "plugin\|extension" /var/log/vmware/vsphere-ui/logs/vsphere_client_virgo.log | \
  grep -i "error\|fail\|exception" | tail -20
```

| Condition | Badge |
|-----------|-------|
| All expected plugins registered and loading | <span class="badge-pass">PASS</span> |
| Some plugins failing to load but not critical | <span class="badge-warn">WARN</span> |
| Core plugins missing or all failing | <span class="badge-fail">FAIL</span> |

### <span id="plugins-cleanup"></span>13.3 Stale Plugin Cleanup

<div class="warn-box">
<strong>Warning:</strong> Only remove plugins that have been confirmed as stale (e.g., from decommissioned products). Removing active plugins will break functionality.
</div>

#### Identify Stale Plugins

```bash
# Check for plugins whose server URL is unreachable
curl -sk -X GET \
  "https://${VC_FQDN}/mob/?moid=ExtensionManager" \
  -H "vmware-api-session-id: ${VC_TOKEN}" 2>/dev/null
```

#### Remove Stale Plugin via MOB

1. Navigate to: `https://$VC_FQDN/mob/?moid=ExtensionManager`
2. Click `UnregisterExtension`
3. Enter the extension key (e.g., `com.vendor.stale.plugin`)
4. Click `Invoke Method`

#### Remove via PowerCLI

```powershell
$em = Get-View ExtensionManager
$em.UnregisterExtension("com.vendor.stale.plugin")
```

<div class="fix-box">
<strong>Remediation (Plugin Issues):</strong><br>
1. Restart vSphere Client: <code>service-control --stop vsphere-ui && service-control --start vsphere-ui</code><br>
2. Clear client cache: <code>rm -rf /etc/vmware/vsphere-ui/cm-init-*</code><br>
3. Re-register plugin: reinstall the product that provides the plugin<br>
4. Check plugin compatibility with current vCenter version
</div>



## <span id="lookup-service"></span>14. Lookup Service & PSC

The Lookup Service is the service registry for all vSphere components. Since vCenter 7.0+, the Platform Services Controller (PSC) is embedded.

### <span id="ls-registration"></span>14.1 Lookup Service Registration

#### Check Lookup Service Status

```bash
service-control --status vmware-lookupsvc
```

**Expected Output:**

```
VMware Lookup Service:Status: RUNNING
```

#### List All Service Registrations

```bash
# Use lstool to list registrations
python /usr/lib/vmidentity/tools/scripts/lstool.py list \
  --url "https://localhost/lookupservice/sdk" \
  --no-check-cert 2>/dev/null | head -60
```

**Expected Output (Healthy):**

```
=== Service Registration ===
Service ID: vcenterserver
Owner ID: vcenter01.lab.local@vsphere.local
Service Type: vcenterserver
Endpoints:
  URL: https://vcenter01.lab.local/sdk
  Protocol: vmomi

Service ID: cs.identity
Owner ID: vcenter01.lab.local@vsphere.local
Service Type: cs.identity
Endpoints:
  URL: https://vcenter01.lab.local/sts/STSService/vsphere.local
  Protocol: wsTrust
...
```

### <span id="ls-sts"></span>14.2 STS Health

```bash
# Check STS service status
service-control --status vmware-stsd
```

**Expected Output:**

```
VMware Security Token Service:Status: RUNNING
```

#### Test STS Token Issuance

```bash
# Verify STS can issue tokens by creating an API session
curl -sk -X POST \
  "https://${VC_FQDN}/api/session" \
  -u "${VC_USER}:${VC_PASS}" \
  -w "\nHTTP Status: %{http_code}\n"
```

| Condition | Badge |
|-----------|-------|
| STS running, tokens issued successfully | <span class="badge-pass">PASS</span> |
| STS running but slow token issuance (> 5s) | <span class="badge-warn">WARN</span> |
| STS stopped or tokens not issued | <span class="badge-fail">FAIL</span> |

### <span id="ls-entries"></span>14.3 Service Registration Entries

#### Verify Key Registrations Exist

```bash
python /usr/lib/vmidentity/tools/scripts/lstool.py list \
  --url "https://localhost/lookupservice/sdk" \
  --no-check-cert 2>/dev/null | grep "Service Type" | sort -u
```

**Expected Service Types:**

```
Service Type: cs.authorization
Service Type: cs.identity
Service Type: cs.license
Service Type: cs.lookup
Service Type: cs.privilege
Service Type: sso:admin
Service Type: sso:groupcheck
Service Type: sso:sts
Service Type: vcenterserver
Service Type: cs.inventory
Service Type: cs.envoy
```

| Condition | Badge |
|-----------|-------|
| All expected service types registered | <span class="badge-pass">PASS</span> |
| Some non-critical registrations missing | <span class="badge-warn">WARN</span> |
| Core registrations (sts, identity, vcenterserver) missing | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (Lookup Service Issues):</strong><br>
1. Restart Lookup Service: <code>service-control --stop vmware-lookupsvc && service-control --start vmware-lookupsvc</code><br>
2. Re-register services: <code>/usr/lib/vmware-lookupsvc/tools/ls_update_certs.py --url https://localhost/lookupservice/sdk --fingerprint &lt;thumbprint&gt;</code><br>
3. Check logs: <code>/var/log/vmware/lookupsvc/lookupsvc.log</code><br>
4. If corrupted, run: <code>/usr/lib/vmware-lookupsvc/tools/ls_recover.py</code>
</div>



## <span id="inventory"></span>15. Inventory Verification

### <span id="inv-counts"></span>15.1 Datacenter / Cluster / Host / VM Counts

#### Get Datacenter Count

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/datacenter" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq 'length'
```

#### List All Datacenters

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/datacenter" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq '.[] | {name, datacenter}'
```

**Expected Output:**

```json
{
  "name": "DC-Site-A",
  "datacenter": "datacenter-1"
}
{
  "name": "DC-Site-B",
  "datacenter": "datacenter-2"
}
```

#### Get Cluster Count and List

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/cluster" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq '.[] | {name, cluster, ha_enabled, drs_enabled}'
```

**Expected Output:**

```json
{
  "name": "Management-Cluster",
  "cluster": "domain-c8",
  "ha_enabled": true,
  "drs_enabled": true
}
{
  "name": "Workload-Cluster-01",
  "cluster": "domain-c44",
  "ha_enabled": true,
  "drs_enabled": true
}
```

#### Get Host Count and Status

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/host" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq '.[] | {name, host, connection_state, power_state}'
```

**Expected Output:**

```json
{
  "name": "esxi01.lab.local",
  "host": "host-10",
  "connection_state": "CONNECTED",
  "power_state": "POWERED_ON"
}
{
  "name": "esxi02.lab.local",
  "host": "host-11",
  "connection_state": "CONNECTED",
  "power_state": "POWERED_ON"
}
```

#### Get VM Count

```bash
# Total VM count
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/vm" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq 'length'
```

```bash
# Powered-on VMs
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/vm?power_states=POWERED_ON" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq 'length'
```

#### Full Inventory Summary Script

```bash
echo "=== vCenter Inventory Summary ==="
DC=$(curl -sk "https://${VC_FQDN}/api/vcenter/datacenter" -H "vmware-api-session-id: ${VC_TOKEN}" | jq 'length')
CL=$(curl -sk "https://${VC_FQDN}/api/vcenter/cluster" -H "vmware-api-session-id: ${VC_TOKEN}" | jq 'length')
HO=$(curl -sk "https://${VC_FQDN}/api/vcenter/host" -H "vmware-api-session-id: ${VC_TOKEN}" | jq 'length')
VM=$(curl -sk "https://${VC_FQDN}/api/vcenter/vm" -H "vmware-api-session-id: ${VC_TOKEN}" | jq 'length')
VMon=$(curl -sk "https://${VC_FQDN}/api/vcenter/vm?power_states=POWERED_ON" -H "vmware-api-session-id: ${VC_TOKEN}" | jq 'length')
DS=$(curl -sk "https://${VC_FQDN}/api/vcenter/datastore" -H "vmware-api-session-id: ${VC_TOKEN}" | jq 'length')
NET=$(curl -sk "https://${VC_FQDN}/api/vcenter/network" -H "vmware-api-session-id: ${VC_TOKEN}" | jq 'length')
echo "Datacenters:  ${DC}"
echo "Clusters:     ${CL}"
echo "Hosts:        ${HO}"
echo "Total VMs:    ${VM}"
echo "Powered-On:   ${VMon}"
echo "Datastores:   ${DS}"
echo "Networks:     ${NET}"
```

### <span id="inv-consistency"></span>15.2 Inventory Consistency

#### Check for Disconnected Hosts

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/host?connection_states=DISCONNECTED,NOT_RESPONDING" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq '.[] | {name, connection_state}'
```

**Expected Output (Healthy):** Empty array `[]`

#### Check for Orphaned VMs

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/vcenter/vm?power_states=POWERED_OFF" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq '.[] | {name, vm, power_state}'
```

| Condition | Badge |
|-----------|-------|
| All hosts CONNECTED, inventory counts match expected | <span class="badge-pass">PASS</span> |
| Some hosts in maintenance mode (planned) | <span class="badge-warn">WARN</span> |
| Disconnected/NOT_RESPONDING hosts found | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (Inventory Issues):</strong><br>
1. Reconnect host: Right-click host in vSphere Client > Connection > Connect<br>
2. Via API: <code>curl -sk -X POST "https://${VC_FQDN}/api/vcenter/host/host-XX?action=connect" -H "vmware-api-session-id: ${VC_TOKEN}"</code><br>
3. Remove orphaned objects: Right-click > Remove from Inventory<br>
4. If hosts persistently disconnect, check network, DNS, and host certificates
</div>



## <span id="syslog"></span>16. Syslog & Log Configuration

### <span id="syslog-forward"></span>16.1 Syslog Forwarding

#### Check Syslog Configuration via API

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/logging/forwarding" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq .
```

**Expected Output (Configured):**

```json
[
  {
    "hostname": "syslog.lab.local",
    "port": 514,
    "protocol": "UDP"
  },
  {
    "hostname": "loginsight.lab.local",
    "port": 9000,
    "protocol": "TCP"
  }
]
```

#### Test Syslog Forwarding

```bash
curl -sk -X POST \
  "https://${VC_FQDN}/api/appliance/logging/forwarding?action=test" \
  -H "vmware-api-session-id: ${VC_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"send_test_message": true}' | jq .
```

**Expected Output:**

```json
[
  {
    "hostname": "syslog.lab.local",
    "state": "UP",
    "message": ""
  }
]
```

#### Configure Syslog Forwarding

```bash
curl -sk -X PUT \
  "https://${VC_FQDN}/api/appliance/logging/forwarding" \
  -H "vmware-api-session-id: ${VC_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '[{"hostname": "syslog.lab.local", "port": 514, "protocol": "UDP"}]'
```

| Condition | Badge |
|-----------|-------|
| Syslog configured and test passes (state=UP) | <span class="badge-pass">PASS</span> |
| Syslog configured but test fails | <span class="badge-warn">WARN</span> |
| Syslog not configured | <span class="badge-fail">FAIL</span> |

### <span id="log-rotation"></span>16.2 Log Rotation

#### Check Logrotate Configuration

```bash
# Check logrotate status
cat /etc/logrotate.conf | head -20

# Check vCenter-specific rotation configs
ls -la /etc/logrotate.d/
```

#### Trigger Manual Log Rotation

```bash
logrotate -f /etc/logrotate.conf
```

### <span id="log-bundle"></span>16.3 Log Bundle Generation

#### Generate Support Bundle via API

```bash
curl -sk -X POST \
  "https://${VC_FQDN}/api/appliance/support-bundle" \
  -H "vmware-api-session-id: ${VC_TOKEN}" \
  -H "Content-Type: application/json" | jq .
```

#### Generate via CLI

```bash
# Generate support bundle
/usr/lib/vmware-vpxd/support/vcdb_report.sh

# Generate full log bundle
vc-support-bundle
```

<div class="info-box">
<strong>Tip:</strong> Support bundles can be large (several GB). Ensure sufficient free space in <code>/storage/log</code> before generating. Target directory: <code>/var/log/vmware/support/</code>
</div>



## <span id="ntp"></span>17. NTP Configuration

Time synchronization is critical for vCenter operations, certificate validation, SSO token integrity, and log correlation.

### <span id="ntp-api"></span>17.1 Time Sync via API

#### Get NTP Configuration

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/ntp" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq .
```

**Expected Output:**

```json
[
  "ntp1.lab.local",
  "ntp2.lab.local"
]
```

#### Get Time Sync Mode

```bash
curl -sk -X GET \
  "https://${VC_FQDN}/api/appliance/timesync" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
```

**Expected Output:**

```
"NTP"
```

#### Set NTP Servers via API

```bash
curl -sk -X PUT \
  "https://${VC_FQDN}/api/appliance/ntp" \
  -H "vmware-api-session-id: ${VC_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '["ntp1.lab.local", "ntp2.lab.local"]'
```

### <span id="ntp-cli"></span>17.2 Time Sync via CLI

#### Check NTP Service

```bash
# Check NTP daemon status
systemctl status systemd-timesyncd
```

```bash
# Check NTP synchronization
timedatectl status
```

**Expected Output (Healthy):**

```
               Local time: Thu 2026-03-26 14:22:33 UTC
           Universal time: Thu 2026-03-26 14:22:33 UTC
                 RTC time: Thu 2026-03-26 14:22:33
                Time zone: UTC (UTC, +0000)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no
```

```bash
# Check NTP peers
ntpq -p 2>/dev/null || chronyc sources 2>/dev/null
```

**Expected Output:**

```
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^* ntp1.lab.local                2   6   377    34   +0.234ms[+0.312ms] +/- 12ms
^+ ntp2.lab.local                2   6   377    35   +1.023ms[+1.101ms] +/- 15ms
```

### <span id="ntp-drift"></span>17.3 Drift Check

```bash
# Check clock offset
chronyc tracking 2>/dev/null | grep "System time\|Last offset"
```

**Expected Output:**

```
System time     : 0.000000234 seconds fast of NTP time
Last offset     : +0.000000312 seconds
```

| Condition | Badge |
|-----------|-------|
| NTP configured, synced, drift < 1 second | <span class="badge-pass">PASS</span> |
| NTP configured but drift 1 - 5 seconds | <span class="badge-warn">WARN</span> |
| NTP not configured or drift > 5 seconds | <span class="badge-fail">FAIL</span> |

<div class="fix-box">
<strong>Remediation (NTP Issues):</strong><br>
1. Set NTP servers: <code>curl -sk -X PUT "https://${VC_FQDN}/api/appliance/ntp" -H "vmware-api-session-id: ${VC_TOKEN}" -H "Content-Type: application/json" -d '["pool.ntp.org"]'</code><br>
2. Force time sync: <code>systemctl restart systemd-timesyncd</code><br>
3. Verify mode is NTP (not HOST): <code>curl -sk -X PUT "https://${VC_FQDN}/api/appliance/timesync" -H "vmware-api-session-id: ${VC_TOKEN}" -H "Content-Type: application/json" -d '"NTP"'</code><br>
4. Check firewall allows NTP (UDP 123) outbound
</div>



## <span id="ports"></span>18. Port Reference Table

### vCenter Server Inbound Ports

| Port | Protocol | Service | Source | Description |
|------|----------|---------|--------|-------------|
| 22 | TCP | SSH | Admin workstations | Appliance shell access (should be disabled in production) |
| 80 | TCP | HTTP | All clients | Redirects to HTTPS (443) |
| 443 | TCP | HTTPS | All clients | vSphere Client, REST API, SDK, MOB |
| 389 | TCP | LDAP | PSC components | VMware Directory Service (vmdir) |
| 636 | TCP | LDAPS | PSC components | VMware Directory Service (secure) |
| 902 | TCP/UDP | VMware Auth | ESXi hosts | VM console proxy, host management |
| 1514 | TCP | Syslog (TLS) | ESXi hosts | Syslog collection from hosts |
| 2012 | TCP | Control Interface | Internal | vCenter control interface |
| 2020 | TCP | Auth Framework | Internal | Authentication framework |
| 5480 | TCP | VAMI | Admin workstations | Appliance Management Interface |
| 6501 | TCP | Auto Deploy | ESXi hosts | Auto Deploy service |
| 6502 | TCP | Auto Deploy | ESXi hosts | Auto Deploy reverse proxy |
| 7080 | TCP | Secure Token | Internal | VMware STS (HTTP) |
| 7444 | TCP | Secure Token | Internal | VMware STS (HTTPS) |
| 8084 | TCP | Update Manager | ESXi hosts | vSphere Update Manager |
| 9084 | TCP | Update Manager | ESXi hosts | Update Manager web client |
| 9087 | TCP | Analytics | Internal | Analytics service |
| 9123 | TCP | Migration Assistant | External | vCenter migration |

### vCenter Server Outbound Ports

| Port | Protocol | Destination | Description |
|------|----------|-------------|-------------|
| 53 | TCP/UDP | DNS servers | DNS resolution |
| 88 | TCP/UDP | AD/KDC | Kerberos authentication |
| 123 | UDP | NTP servers | Time synchronization |
| 389 | TCP | AD/LDAP | Identity source queries |
| 443 | TCP | ESXi hosts | Host management via HTTPS |
| 443 | TCP | NSX Manager | NSX integration |
| 443 | TCP | SDDC Manager | VCF lifecycle management |
| 514 | UDP | Syslog server | Syslog forwarding |
| 902 | TCP | ESXi hosts | VM console, host management |

### Port Verification Commands

```bash
# Check listening ports on vCenter appliance
ss -tlnp | sort -t: -k2 -n
```

```bash
# Check specific port connectivity
curl -sk -o /dev/null -w "%{http_code}" https://${VC_FQDN}:443
curl -sk -o /dev/null -w "%{http_code}" https://${VC_FQDN}:5480
```

```bash
# Check outbound connectivity
nc -zv ntp1.lab.local 123 2>&1
nc -zv dc01.lab.local 389 2>&1
nc -zv esxi01.lab.local 443 2>&1
```



## <span id="common-issues"></span>19. Common Issues & Remediation

### 19.1 VPXD Crashes or Won't Start

**Symptoms:** vSphere Client inaccessible, `service-control --status vmware-vpxd` shows STOPPED.

<div class="danger">
<strong>Impact:</strong> Complete vCenter management outage. VMs continue running on ESXi hosts but cannot be managed.
</div>

**Diagnostic Steps:**

```bash
# Check VPXD logs for crash reason
tail -200 /var/log/vmware/vpxd/vpxd.log | grep -i "error\|fatal\|abort"

# Check for core dumps
ls -la /var/core/

# Check if database is reachable
systemctl status vmware-vpostgres

# Check disk space (VPXD won't start if disk full)
df -h /storage/log /storage/db /

# Check for port conflicts
ss -tlnp | grep ":443\b"
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. If disk full: clear logs per Section 10, then start VPXD<br>
2. If DB down: <code>service-control --start vmware-vpostgres</code>, then start VPXD<br>
3. If port conflict: identify and stop conflicting process, then start VPXD<br>
4. If persistent crash: collect support bundle and open VMware SR<br>
5. As last resort: <code>service-control --stop --all && service-control --start --all</code>
</div>

### 19.2 Database Corruption

**Symptoms:** VPXD errors referencing VCDB, inventory inconsistencies, SQL errors in logs.

```bash
# Check PostgreSQL logs
tail -100 /var/log/vmware/vpostgres/postgresql*.log

# Run database integrity check
/opt/vmware/vpostgres/current/bin/pg_isready -h localhost -p 5432

# Check for corruption indicators
/opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB -c \
  "SELECT datname, datallowconn FROM pg_database;"
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. If minor: Run <code>VACUUM FULL ANALYZE;</code> to reclaim and rebuild<br>
2. If tables corrupted: <code>REINDEX DATABASE VCDB;</code><br>
3. If severe: Restore from backup: <code>/opt/vmware/vpostgres/current/bin/pg_restore</code><br>
4. If no backup available: Contact VMware Global Support immediately<br>
5. Prevention: Ensure regular file-based backups are configured
</div>

### 19.3 Certificate Expiry

**Symptoms:** SSO login failures, "certificate expired" errors in browser, service communication failures.

```bash
# Quick check all certs
for store in MACHINE_SSL_CERT machine vsphere-webclient vpxd vpxd-extension; do
  echo "=== ${store} ==="
  /usr/lib/vmware-vmafd/bin/vecs-cli entry getcert --store ${store} \
    --alias $(/usr/lib/vmware-vmafd/bin/vecs-cli entry list --store ${store} 2>/dev/null | grep Alias | awk '{print $3}' | head -1) 2>/dev/null | \
    openssl x509 -noout -dates 2>/dev/null
done

# Check STS cert specifically
python /usr/lib/vmware-vmca/share/config/checksts.py 2>/dev/null
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. For Machine SSL: <code>/usr/lib/vmware-vmca/bin/certificate-manager</code> option 3 (VMCA) or 1 (custom)<br>
2. For STS expired: Follow KB 79248 to replace STS signing certificate<br>
3. For Solution User certs: Certificate Manager option 6<br>
4. After renewal: restart all services <code>service-control --stop --all && service-control --start --all</code><br>
5. Schedule proactive monitoring: check certs monthly
</div>

### 19.4 SSO Lockout

**Symptoms:** Cannot log in as administrator@vsphere.local, "invalid credentials" or "account locked."

```bash
# Check lockout policy
/opt/vmware/bin/sso-config.sh -get_lockout_policy

# Check failed login attempts
grep -i "login\|auth\|lock" /var/log/vmware/sso/ssoAdminServer.log | tail -30
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. Wait for lockout period to expire (default: 5 minutes)<br>
2. Unlock via CLI: <code>/usr/lib/vmware-vmdir/bin/dir-cli account unlock --account administrator --password &lt;current_password&gt;</code><br>
3. Reset password: <code>/usr/lib/vmware-vmdir/bin/dir-cli password reset --account administrator --new &lt;new_password&gt;</code><br>
4. If vmdir corrupted: Boot to single-user mode and reset via <code>/usr/lib/vmware-vmdir/bin/vdcadmintool</code><br>
5. As absolute last resort: restore from backup
</div>

### 19.5 Performance Degradation

**Symptoms:** vSphere Client slow, API timeouts, tasks taking excessively long.

```bash
# Identify bottleneck
echo "=== CPU ===" && uptime
echo "=== Memory ===" && free -m
echo "=== Swap ===" && swapon --show
echo "=== Disk I/O ===" && iostat -x 1 3 2>/dev/null || echo "iostat not available"
echo "=== Top Processes ===" && top -bn1 | head -15
echo "=== DB Connections ===" && /opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB -c \
  "SELECT count(*) FROM pg_stat_activity;"
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. If CPU high: check for runaway tasks, reduce DRS sensitivity<br>
2. If memory high: restart VPXD to reclaim, or add VM memory<br>
3. If swap heavy: increase VM memory, check for memory leaks<br>
4. If DB connections high: restart VPXD, check for stuck tasks<br>
5. If disk I/O: move vCenter to faster storage (SSD/NVMe)<br>
6. Long-term: right-size vCenter appliance per VMware sizing guidelines
</div>



## <span id="cli-reference"></span>20. CLI Quick Reference Card

### Service Management

| Command | Description |
|---------|-------------|
| `service-control --status --all` | Show status of all vCenter services |
| `service-control --status vmware-vpxd` | Show VPXD service status |
| `service-control --start --all` | Start all vCenter services |
| `service-control --stop --all` | Stop all vCenter services |
| `service-control --start <service>` | Start a specific service |
| `service-control --stop <service>` | Stop a specific service |
| `vmon-cli --list` | List all vMon-managed services |
| `vmon-cli --status <service>` | Check specific vMon service status |
| `vmon-cli --start <service>` | Start a vMon service |
| `vmon-cli --stop <service>` | Stop a vMon service |
| `vmon-cli --restart <service>` | Restart a vMon service |

### System & Appliance

| Command | Description |
|---------|-------------|
| `uptime` | System uptime and load average |
| `free -m` | Memory usage in MB |
| `df -h` | Disk partition usage |
| `top -bn1` | Process listing (batch mode, single iteration) |
| `timedatectl status` | Time synchronization status |
| `hostnamectl` | Hostname and OS information |
| `cat /etc/applmgmt/appliance/update.conf` | Appliance version info |
| `vpxd -v` | VPXD version |
| `cat /etc/issue` | Photon OS version |

### Database

| Command | Description |
|---------|-------------|
| `/opt/vmware/vpostgres/current/bin/psql -U postgres -d VCDB` | Connect to VCDB |
| `systemctl status vmware-vpostgres` | PostgreSQL service status |
| `VACUUM ANALYZE;` (in psql) | Standard vacuum with analyze |
| `VACUUM FULL ANALYZE;` (in psql) | Full vacuum (blocking) |
| `SELECT pg_size_pretty(pg_database_size('VCDB'));` | VCDB size |

### Certificates

| Command | Description |
|---------|-------------|
| `/usr/lib/vmware-vmca/bin/certificate-manager` | Certificate Manager (interactive) |
| `/usr/lib/vmware-vmafd/bin/vecs-cli store list` | List VECS stores |
| `/usr/lib/vmware-vmafd/bin/vecs-cli entry list --store <store>` | List entries in a VECS store |
| `/usr/lib/vmware-vmafd/bin/vecs-cli entry getcert --store <store> --alias <alias>` | Get certificate from store |
| `/usr/lib/vmware-vmafd/bin/dir-cli trustedcert list` | List trusted root certificates |
| `python /usr/lib/vmware-vmca/share/config/checksts.py` | Check STS certificate |

### SSO & Identity

| Command | Description |
|---------|-------------|
| `/opt/vmware/bin/sso-config.sh -get_identity_sources` | List identity sources |
| `/opt/vmware/bin/sso-config.sh -get_default_identity_sources` | Get default identity source |
| `/opt/vmware/bin/sso-config.sh -get_lockout_policy` | SSO lockout policy |
| `/usr/lib/vmware-vmdir/bin/dir-cli password reset --account <user> --new <pass>` | Reset SSO password |
| `/usr/lib/vmware-vmdir/bin/dir-cli account unlock --account <user>` | Unlock SSO account |

### Lookup Service

| Command | Description |
|---------|-------------|
| `python /usr/lib/vmidentity/tools/scripts/lstool.py list --url https://localhost/lookupservice/sdk --no-check-cert` | List all registrations |

### Logs

| Command | Description |
|---------|-------------|
| `tail -f /var/log/vmware/vpxd/vpxd.log` | Follow VPXD log |
| `tail -f /var/log/vmware/sso/ssoAdminServer.log` | Follow SSO log |
| `tail -f /var/log/vmware/lookupsvc/lookupsvc.log` | Follow Lookup Service log |
| `tail -f /var/log/vmware/vsphere-ui/logs/vsphere_client_virgo.log` | Follow vSphere Client log |
| `tail -f /var/log/vmware/vpostgres/postgresql*.log` | Follow PostgreSQL log |
| `vc-support-bundle` | Generate full support bundle |

### VCHA

| Command | Description |
|---------|-------------|
| `/usr/lib/vmware-vcha/vcha-cli cluster-get-state` | VCHA cluster state |

### Networking

| Command | Description |
|---------|-------------|
| `ss -tlnp` | List all listening TCP ports |
| `ip addr show` | Show network interfaces |
| `ip route show` | Show routing table |
| `cat /etc/resolv.conf` | DNS configuration |
| `nslookup ${VC_FQDN}` | DNS resolution test |



## <span id="api-reference"></span>21. API Quick Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/session` | Create session (Basic Auth) -- returns session token |
| GET | `/api/session` | Get current session info |
| DELETE | `/api/session` | Destroy session (logout) |

### Appliance Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appliance/health/system` | Overall system health |
| GET | `/api/appliance/health/mem` | Memory health |
| GET | `/api/appliance/health/storage` | Storage health |
| GET | `/api/appliance/health/database-storage` | Database storage health |
| GET | `/api/appliance/health/load` | CPU load health |
| GET | `/api/appliance/health/swap` | Swap health |
| GET | `/api/appliance/health/softwarepackages` | Software package health |

### Appliance Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appliance/ntp` | Get NTP servers |
| PUT | `/api/appliance/ntp` | Set NTP servers |
| GET | `/api/appliance/timesync` | Get time sync mode |
| PUT | `/api/appliance/timesync` | Set time sync mode (NTP/HOST) |
| GET | `/api/appliance/access/ssh` | Get SSH access status |
| PUT | `/api/appliance/access/ssh` | Enable/disable SSH |
| GET | `/api/appliance/networking` | Get network configuration |
| GET | `/api/appliance/networking/dns/servers` | Get DNS servers |
| GET | `/api/appliance/networking/dns/hostname` | Get hostname |

### Logging

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appliance/logging/forwarding` | Get syslog forwarding config |
| PUT | `/api/appliance/logging/forwarding` | Set syslog forwarding config |
| POST | `/api/appliance/logging/forwarding?action=test` | Test syslog forwarding |

### Inventory

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vcenter/datacenter` | List datacenters |
| GET | `/api/vcenter/cluster` | List clusters |
| GET | `/api/vcenter/host` | List hosts |
| GET | `/api/vcenter/vm` | List VMs |
| GET | `/api/vcenter/datastore` | List datastores |
| GET | `/api/vcenter/network` | List networks |
| GET | `/api/vcenter/folder` | List folders |
| GET | `/api/vcenter/resource-pool` | List resource pools |

### vCenter HA

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vcenter/vcha/cluster/mode` | Get VCHA mode |
| POST | `/api/vcenter/vcha/cluster?action=get` | Get full VCHA cluster status |
| POST | `/api/vcenter/vcha/cluster?action=failover` | Initiate VCHA failover |

### Certificates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vcenter/certificate-management/vcenter/tls` | Get TLS certificate info |
| GET | `/api/vcenter/certificate-management/vcenter/trusted-root-chains` | List trusted root chains |

### Identity & SSO

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/vcenter/identity/providers` | List identity providers |

### Common curl Pattern

```bash
# GET request pattern
curl -sk -X GET \
  "https://${VC_FQDN}/api/<endpoint>" \
  -H "vmware-api-session-id: ${VC_TOKEN}" | jq .

# POST request pattern
curl -sk -X POST \
  "https://${VC_FQDN}/api/<endpoint>" \
  -H "vmware-api-session-id: ${VC_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "key": "value" }' | jq .

# PUT request pattern
curl -sk -X PUT \
  "https://${VC_FQDN}/api/<endpoint>" \
  -H "vmware-api-session-id: ${VC_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "key": "value" }'
```

### Session Management Best Practice

```bash
# Create session at start
export VC_TOKEN=$(curl -sk -X POST \
  "https://${VC_FQDN}/api/session" \
  -u "${VC_USER}:${VC_PASS}" | tr -d '"')

# ... run all health checks ...

# Destroy session at end
curl -sk -X DELETE \
  "https://${VC_FQDN}/api/session" \
  -H "vmware-api-session-id: ${VC_TOKEN}"
unset VC_TOKEN VC_PASS
```


<div class="info-box">
<strong>Document Information:</strong><br>
<b>Title:</b> vCenter Server Health Check Handbook<br>
<b>Version:</b> 1.0<br>
<b>Author:</b> Virtual Control LLC<br>
<b>Date:</b> March 2026<br>
<b>Classification:</b> Internal Use<br>
<b>Platform:</b> VMware Cloud Foundation 9.0 / vCenter Server 8.x<br>
<b>Disclaimer:</b> Always test commands in a non-production environment first. Virtual Control LLC is not responsible for any issues arising from the use of commands in this document without proper testing.
</div>

*(c) 2026 Virtual Control LLC. All rights reserved.*
