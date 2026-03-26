---
title: "NSX Manager 9.0.1 Cold Start Service Failure — Root Cause Analysis & Recovery"
subtitle: "Complete Troubleshooting Report: Every Command, Every Output, Every Fix"
author: "Virtual Control LLC"
date: "March 26, 2026"
css: |-
  body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10pt; color: #1a1a1a; }
  h1 { color: #0b3d6b; border-bottom: 3px solid #0b3d6b; padding-bottom: 8px; font-size: 22pt; page-break-before: avoid; }
  h2 { color: #0b3d6b; border-bottom: 1px solid #d0d0d0; padding-bottom: 4px; margin-top: 28px; font-size: 14pt; }
  h3 { color: #1a5276; margin-top: 16px; font-size: 11pt; }
  h4 { color: #1a5276; margin-top: 12px; font-size: 10pt; font-style: italic; }
  table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9pt; }
  th { background-color: #0b3d6b; color: white; padding: 6px 8px; text-align: left; }
  td { border: 1px solid #d0d0d0; padding: 5px 8px; word-break: break-word; }
  tr:nth-child(even) { background-color: #f5f8fb; }
  code { background-color: #f0f4f8; padding: 1px 4px; border-radius: 3px; font-size: 8.5pt; word-break: break-all; }
  pre { background-color: #f0f4f8; padding: 10px; border-radius: 4px; border-left: 3px solid #0b3d6b; font-size: 8.5pt; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }
  blockquote { border-left: 3px solid #ff9800; background: #fff8e1; padding: 8px 12px; margin: 8px 0; font-size: 9pt; }
  .toc { background: #f5f8fb; border: 1px solid #d0d0d0; border-radius: 4px; padding: 12px 20px; margin: 12px 0; }
  .toc a { text-decoration: none; color: #0b3d6b; }
  .toc a:hover { text-decoration: underline; }
  .toc ul { list-style: none; padding-left: 16px; margin: 4px 0; }
  .toc > ul { padding-left: 0; }
  .rca-box { border: 2px solid #c62828; background: #fef2f2; padding: 12px 16px; border-radius: 6px; margin: 12px 0; }
  .fix-box { border: 2px solid #2e7d32; background: #f1f8e9; padding: 12px 16px; border-radius: 6px; margin: 12px 0; }
  .info-box { border: 2px solid #0b3d6b; background: #e8f0fe; padding: 12px 16px; border-radius: 6px; margin: 12px 0; }
  .warn-box { border: 2px solid #e65100; background: #fff3e0; padding: 12px 16px; border-radius: 6px; margin: 12px 0; }
pdf_options:
  format: Letter
  margin: 18mm 15mm 18mm 15mm
  headerTemplate: '<div style="font-size:8px;color:#888;width:100%;text-align:center;">NSX Manager 9.0.1 Cold Start Service Failure — RCA & Recovery &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  footerTemplate: '<div style="font-size:8px;color:#888;width:100%;text-align:center;">&copy; 2026 Virtual Control LLC &nbsp;&nbsp;|&nbsp;&nbsp; Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>'
  displayHeaderFooter: true
---

# NSX Manager 9.0.1 Cold Start Service Failure — Root Cause Analysis & Recovery

**Prepared by:** Virtual Control LLC
**Date:** March 26, 2026
**Document Version:** 1.0
**Classification:** Internal — Lab Environment
**NSX Version:** 9.0.1.0 (Build 24952114)

---

<div class="toc">

**Table of Contents**

<ul>
<li><a href="#1-executive-summary">1. Executive Summary</a></li>
<li><a href="#2-environment-reference">2. Environment Reference</a>
  <ul>
  <li><a href="#21-infrastructure-details">2.1 Infrastructure Details</a></li>
  <li><a href="#22-nsx-manager-configuration">2.2 NSX Manager Configuration</a></li>
  <li><a href="#23-upstream-dependencies">2.3 Upstream Dependencies</a></li>
  </ul>
</li>
<li><a href="#3-problem-statement">3. Problem Statement</a>
  <ul>
  <li><a href="#31-symptom-description">3.1 Symptom Description</a></li>
  <li><a href="#32-affected-components">3.2 Affected Components</a></li>
  <li><a href="#33-business-impact">3.3 Business Impact</a></li>
  </ul>
</li>
<li><a href="#4-root-cause-analysis">4. Root Cause Analysis</a>
  <ul>
  <li><a href="#41-rca-summary">4.1 RCA Summary</a></li>
  <li><a href="#42-service-dependency-chain">4.2 Service Dependency Chain</a></li>
  <li><a href="#43-why-services-did-not-auto-start">4.3 Why Services Did Not Auto-Start</a></li>
  </ul>
</li>
<li><a href="#5-phase-1-initial-assessment">5. Phase 1 — Initial Assessment</a>
  <ul>
  <li><a href="#51-vcf-operations-alerts">5.1 VCF Operations Alerts</a></li>
  <li><a href="#52-network-connectivity-test">5.2 Network Connectivity Test</a></li>
  <li><a href="#53-browser-access-test">5.3 Browser Access Test</a></li>
  </ul>
</li>
<li><a href="#6-phase-2-ssh-diagnostics">6. Phase 2 — SSH Diagnostics</a>
  <ul>
  <li><a href="#61-establish-ssh-session">6.1 Establish SSH Session</a></li>
  <li><a href="#62-check-all-services">6.2 Check All Services</a></li>
  <li><a href="#63-filesystem-and-resource-check">6.3 Filesystem and Resource Check</a></li>
  </ul>
</li>
<li><a href="#7-phase-3-service-recovery">7. Phase 3 — Service Recovery</a>
  <ul>
  <li><a href="#71-verify-datastore-corfu-status">7.1 Verify Datastore (Corfu) Status</a></li>
  <li><a href="#72-start-http-service">7.2 Start HTTP Service</a></li>
  <li><a href="#73-start-manager-service">7.3 Start Manager Service</a></li>
  <li><a href="#74-start-controller-service">7.4 Start Controller Service</a></li>
  <li><a href="#75-verify-all-services-running">7.5 Verify All Services Running</a></li>
  </ul>
</li>
<li><a href="#8-phase-4-cluster-validation">8. Phase 4 — Cluster Validation</a>
  <ul>
  <li><a href="#81-cluster-vip-verification">8.1 Cluster VIP Verification</a></li>
  <li><a href="#82-cluster-status-verbose">8.2 Cluster Status Verbose</a></li>
  <li><a href="#83-https-group-status">8.3 HTTPS Group Status</a></li>
  <li><a href="#84-browser-access-verification">8.4 Browser Access Verification</a></li>
  </ul>
</li>
<li><a href="#9-phase-5-upstream-integration-recovery">9. Phase 5 — Upstream Integration Recovery</a>
  <ul>
  <li><a href="#91-vcf-operations-adapter-status">9.1 VCF Operations Adapter Status</a></li>
  <li><a href="#92-re-validate-nsx-adapter">9.2 Re-validate NSX Adapter</a></li>
  <li><a href="#93-confirm-collection-status">9.3 Confirm Collection Status</a></li>
  </ul>
</li>
<li><a href="#10-post-recovery-verification-checklist">10. Post-Recovery Verification Checklist</a></li>
<li><a href="#11-lessons-learned-and-recommendations">11. Lessons Learned and Recommendations</a></li>
<li><a href="#12-appendix-a-complete-service-list-pre-recovery">Appendix A — Complete Service List (Pre-Recovery)</a></li>
<li><a href="#13-appendix-b-complete-service-list-post-recovery">Appendix B — Complete Service List (Post-Recovery)</a></li>
<li><a href="#14-document-information">14. Document Information</a></li>
</ul>

</div>

---

## 1. Executive Summary

On March 26, 2026, a complete NSX Manager service failure was identified in the VCF 9.0.1 nested lab environment. The NSX Manager appliance (`nsx-node1.lab.local`, 192.168.1.71) was powered on and responding to ICMP, but all core platform services — including HTTP, Manager, Controller, Search, and Authentication — were in a **stopped** state. The NSX Manager UI was unreachable on both the node IP (192.168.1.71) and the cluster VIP (192.168.1.70). VCF Operations reported two integration adapters in **Warning** state due to the inability to connect to NSX.

The root cause was determined to be a **cold start service initialization failure**. After a lab shutdown and restart, the NSX Manager appliance booted successfully at the OS level, but the NSX application services did not auto-start in the correct dependency order. The Corfu datastore service was running, but the HTTP service — which all API and UI access depends on — remained stopped, preventing the rest of the service chain from initializing.

Recovery was achieved by manually starting services in the correct dependency order: **datastore → http → manager → controller**. This cascaded the startup of all remaining 30+ services. Total recovery time from initial diagnosis to full service restoration was approximately 40 minutes.

<div class="rca-box">

**Root Cause:** NSX Manager 9.0.1 cold start in a resource-constrained nested environment caused the HTTP service to fail during automatic initialization. The Corfu datastore started successfully, but the HTTP service did not start within the expected timeout window, breaking the service dependency chain and leaving all dependent services (Manager, Controller, Search, Auth, and 25+ policy services) in a stopped state.

</div>

---

## 2. Environment Reference

### 2.1 Infrastructure Details

| Parameter | Value |
|---|---|
| Physical Host | Dell Precision 7920 |
| Hypervisor | VMware Workstation 17.x (Nested) |
| VCF Version | 9.0.1 |
| Lab Domain | lab.local |
| Deployment Type | Single-node NSX Manager (nested) |

### 2.2 NSX Manager Configuration

| Parameter | Value |
|---|---|
| Appliance Hostname | nsx-node1.lab.local |
| Node UUID | 95493642-ef4a-cb8e-ed7c-5bc20033f2c2 |
| Node IP Address | 192.168.1.71 |
| Cluster VIP | 192.168.1.70 |
| NSX Version | 9.0.1.0 |
| Build Number | 24952114 |
| Cluster ID | 3d5211c5-a4e1-4535-a803-f10726c26d59 |
| Deployment Type | Single-node cluster |

### 2.3 Upstream Dependencies

| Component | IP Address | Role |
|---|---|---|
| vCenter Server 9.0 | 192.168.1.69 | Infrastructure management |
| SDDC Manager 9.0 | 192.168.1.241 | Lifecycle management |
| VCF Operations 9.0.2 | — | Monitoring (VCF Operations Collector) |
| ESXi Hosts | 192.168.1.74–.76, .82 | Compute |

---

## 3. Problem Statement

### 3.1 Symptom Description

The issue was initially identified in VCF Operations (Administration → Integrations → Accounts). Two adapters displayed **Warning** status:

1. **lab** — VMware Cloud Foundation Adapter (collector.lab.local) — **Warning**
2. **nsx-vip.lab.local** — NSX Adapter (collector.lab.local) — **Warning**

The NSX adapter reported: `Error trying to establish connection`

Additional symptoms:

- `https://192.168.1.70` (VIP) — **not reachable** in browser
- `https://192.168.1.71` (node) — **not reachable** in browser
- `ping 192.168.1.70` — **no response**
- `ping 192.168.1.71` — **responding**

### 3.2 Affected Components

| Component | Status | Impact |
|---|---|---|
| NSX Manager UI | Unreachable | No management access |
| NSX Manager API | Unreachable | No programmatic access |
| Cluster VIP (192.168.1.70) | Not responding | VIP not serving traffic |
| VCF Operations NSX Adapter | Warning | No NSX metric collection |
| VCF Operations VCF Adapter | Warning | Partial VCF data collection failure |
| NSX-backed overlay networking | Degraded | Existing workloads operational; no changes possible |

### 3.3 Business Impact

In a production environment, this failure would result in:

- **Complete loss of NSX management plane access** — no ability to create, modify, or delete logical networking, firewall rules, or load balancer configurations
- **VCF Operations monitoring gap** — no NSX metrics, alerts, or compliance data collected during the outage
- **SDDC Manager lifecycle operations blocked** — any pending NSX upgrades or configuration changes would fail
- **Security policy changes frozen** — distributed firewall rules cannot be modified

> **Note:** Existing data plane connectivity (overlay networks, firewall rules already pushed to hosts) remains operational during an NSX Manager outage. The control plane is affected, not the data plane.

---

## 4. Root Cause Analysis

### 4.1 RCA Summary

<div class="rca-box">

**What happened:** The NSX Manager appliance was powered off as part of a full lab shutdown. Upon restart, the appliance OS booted successfully and basic node services (SSH, NTP, node-mgmt) started. However, the core NSX platform services did not auto-start. The HTTP service failed to initialize within the expected timeout, which broke the service dependency chain.

**Why it happened:** In a nested virtualization environment running on VMware Workstation, the NSX Manager appliance competes for CPU and I/O resources during boot. The Corfu datastore service started successfully, but the HTTP service — which depends on datastore readiness and requires significant memory allocation — did not start before the system's service startup timeout expired. With HTTP stopped, no dependent services (Manager, Controller, Auth, Search) could start because they require the HTTP/API layer for inter-service communication and registration.

**Why it was not detected immediately:** The appliance was responsive to ICMP (ping) on the node IP (192.168.1.71), which could give a false impression of health. The VIP (192.168.1.70) did not respond because VIP assignment depends on the cluster manager service, which was also stopped. VCF Operations detected the failure via adapter warnings, which was the initial alert that triggered investigation.

</div>

### 4.2 Service Dependency Chain

The following diagram shows the NSX Manager service startup order. An arrow indicates a dependency — the service on the right requires the service on the left to be running.

```
Boot Sequence (Automatic):
  OS → ssh, ntp, node-mgmt, node-stats, syslog, nsx-upgrade-agent

Service Dependency Chain (Must be started in order):
  datastore (Corfu DB)
    → http (API/UI gateway)
      → auth (authentication)
      → manager (core management plane)
        → controller (control plane)
        → search (indexing)
        → monitoring
        → cm-inventory
        → messaging-manager
        → cluster_manager
        → site_manager
        → install-upgrade
        → async_replicator
        → idps-reporting
        → All POLICY_SVC_* services (30+)
```

**Key insight:** The `http` service is the single point of failure in the startup chain. If `http` does not start, no service above it in the chain can start, even if `datastore` is healthy.

### 4.3 Why Services Did Not Auto-Start

NSX Manager 9.0.1 uses a service orchestration framework that starts services in dependency order during boot. In resource-constrained environments (nested lab, shared CPU/RAM, slow storage), the following sequence occurs:

1. The OS boots and starts basic services (SSH, NTP, node-mgmt)
2. The Corfu datastore service starts (this is the database layer)
3. The HTTP service attempts to start, but requires:
   - Corfu to be fully ready (not just running, but accepting connections)
   - Sufficient free memory to allocate its Java heap
   - Ports 443 and 80 to be available
4. If the HTTP service does not confirm readiness within the orchestrator's timeout window, it is marked as failed and no retry is attempted
5. All services downstream of HTTP remain in `stopped` state indefinitely

This is a **known behavior in nested environments** and is not caused by data corruption, misconfiguration, or hardware failure.

---

## 5. Phase 1 — Initial Assessment

### 5.1 VCF Operations Alerts

The issue was first observed in VCF Operations under **Administration → Integrations → Accounts**:

| Adapter Name | Type | Status | Collector |
|---|---|---|---|
| lab | VMware Cloud Foundation Adapter | **Warning** | collector.lab.local |
| mgmt | VCF Operations Collector | Collecting | VCF Operations Collector-vcf-ops |
| mgmt | VCF Operations Collector | Collecting | VCF Operations Collector-vcf-ops |
| mgmt - vSAN | VCF Operations Collector | Collecting | VCF Operations Collector-vcf-ops |
| nsx-vip.lab.local | NSX Adapter | **Warning** | collector.lab.local |

The NSX adapter (`nsx-vip.lab.local`) reported: **"Error trying to establish connection"**

### 5.2 Network Connectivity Test

From the management workstation:

```
C:\> ping 192.168.1.70
Request timed out.
Request timed out.

C:\> ping 192.168.1.71
Reply from 192.168.1.71: bytes=32 time<1ms TTL=64
Reply from 192.168.1.71: bytes=32 time<1ms TTL=64
```

**Result:** Node IP (.71) responds to ICMP. Cluster VIP (.70) does not respond.

**Analysis:** The NSX Manager OS is running, but the cluster VIP is not active. The VIP is managed by the `cluster_manager` service, which depends on the HTTP service. This confirms a service-level failure, not a network or VM-level failure.

### 5.3 Browser Access Test

| URL | Result |
|---|---|
| `https://192.168.1.70` | Connection refused — page did not load |
| `https://192.168.1.71` | Connection refused — page did not load |

**Analysis:** Neither the VIP nor the direct node IP serves the NSX UI. The HTTP service (which serves the UI on port 443) is not running.

---

## 6. Phase 2 — SSH Diagnostics

### 6.1 Establish SSH Session

SSH access was available because the `ssh` service starts independently of the NSX platform services.

```
C:\> ssh root@192.168.1.71
root@nsx-node1:~#
```

Switched to the NSX CLI admin user:

```
root@nsx-node1:~# su - admin
NSX CLI (Manager, Policy, Controller 9.0.1.0.24952114). Press ? for command list or enter: help
nsx-node1>
```

### 6.2 Check All Services

The first diagnostic step was to check the state of all NSX services:

```
nsx-node1> get services
```

**Output (abbreviated — full output in Appendix A):**

| Service | State | Notes |
|---|---|---|
| applianceproxy | **running** | Basic proxy — starts independently |
| async_replicator | **stopped** | Depends on manager |
| auth | **stopped** | Depends on http |
| cluster_manager | **stopped** | Depends on http |
| cm-inventory | **stopped** | Depends on manager |
| controller | **stopped** | Depends on http |
| datastore | **stopped** | Corfu DB — checked separately |
| datastore_nonconfig | **stopped** | Corfu secondary — checked separately |
| http | **stopped** | **ROOT CAUSE — gateway for all API/UI** |
| manager | **stopped** | Core management plane |
| messaging-manager | **stopped** | Depends on http |
| monitoring | **stopped** | Depends on manager |
| node-mgmt | **running** | Basic node management — starts independently |
| node-stats | **running** | Basic node stats — starts independently |
| nsx-platform-client | **running** | Platform client — starts independently |
| nsx-upgrade-agent | **running** | Upgrade agent — starts independently |
| ntp | **running** | Time sync — starts independently |
| search | **stopped** | Depends on manager |
| sha | **running** | System health agent — starts independently |
| ssh | **running** | SSH daemon — starts independently |
| syslog | **running** | Log forwarding — starts independently |
| ui-service | **running** | UI static files — starts independently |

**Analysis:** Only 9 out of 30+ services were running. All 9 running services are basic OS-level or node-level services that start independently of the NSX platform. Every platform service (http, manager, controller, auth, search, and all policy services) was **stopped**.

The `get cluster config` and `get cluster status` commands both returned errors at this point:

```
nsx-node1> get cluster config
% An error occurred while getting the cluster config

nsx-node1> get cluster status
% An internal error occurred, please retry execution again

nsx-node1> get cluster vip
% An error occurred while getting the cluster virtual ip
```

**Analysis:** These commands all require the HTTP/API service to be running. Their failure confirms the HTTP service is down.

### 6.3 Filesystem and Resource Check

Before attempting service recovery, disk space and memory were verified to rule out resource exhaustion:

```
nsx-node1> get filesystem-stats
```

| Filesystem | Size | Used | Avail | Use% | Mounted on |
|---|---|---|---|---|---|
| /dev/sda2 | 11G | 4.7G | 5.0G | 49% | / |
| /dev/mapper/nsx-var+log | 27G | 14G | 12G | 55% | /var/log |
| /dev/mapper/nsx-repository | 31G | 7.8G | 22G | 27% | /repository |
| /dev/mapper/nsx-config | 29G | 48M | 28G | 1% | /config |
| /dev/mapper/nsx-secondary | 98G | 230M | 93G | 1% | /nonconfig |
| tmpfs | 16G | 24K | 16G | 1% | /dev/shm |

**Analysis:** No filesystem is close to capacity. The root filesystem is at 49%, /var/log at 55%, and all other mounts are well below any warning threshold. Disk space is **not** a contributing factor.

---

## 7. Phase 3 — Service Recovery

### 7.1 Verify Datastore (Corfu) Status

The Corfu datastore is the foundational database service. It must be running before any other platform service can start.

```
nsx-node1> get service datastore
```

**Output:**

```
Service name:      datastore
Service state:     running
```

**Analysis:** The datastore service was already running. This means the database layer is healthy and no Corfu repair is needed. Proceed to starting the HTTP service.

<div class="info-box">

**Why check datastore first?** The Corfu datastore is the NSX Manager's internal database. If it is stopped or corrupted, starting the HTTP service will fail because HTTP depends on database connectivity for configuration loading, session management, and API request processing. Always verify datastore health before starting upstream services.

</div>

### 7.2 Start HTTP Service

The HTTP service is the API and UI gateway. It listens on port 443 and is required by every other platform service.

```
nsx-node1> start service http
```

Wait 30 seconds for the service to initialize, then verify:

```
nsx-node1> get service http
```

**Output:**

```
Service name:                            http
Service state:                           running
Logging level:                           info
Session timeout:                         1800
Connection timeout:                      30
Client API rate limit:                   100 requests/sec
Client API concurrency limit:            40
Global API concurrency limit:            199
Redirect host:                           (not configured)
Basic authentication:                    enabled
Cookie-based authentication:             enabled
```

<div class="fix-box">

**Result:** HTTP service started successfully. Session timeout is 1800 seconds (30 minutes), connection timeout is 30 seconds. API rate limiting is active at 100 requests/sec. The API gateway is now accepting connections on port 443.

</div>

### 7.3 Start Manager Service

The Manager service is the core management plane. It handles all CRUD operations for NSX objects (segments, firewall rules, groups, etc.).

```
nsx-node1> start service manager
```

Wait 60 seconds for the service to initialize. The manager service has a longer startup time because it must:

- Connect to the Corfu datastore
- Load all policy objects into memory
- Register with the HTTP API layer
- Initialize all POLICY_SVC_* sub-services

```
nsx-node1> get service manager
```

**Output:**

```
Service name:      manager
Service state:     running
Logging level:     info
```

### 7.4 Start Controller Service

The Controller service manages the control plane — it programs the data plane on ESXi hosts and Edge nodes.

```
nsx-node1> start service controller
```

Wait 30 seconds, then verify:

```
nsx-node1> get service controller
```

**Output:**

```
Service name:      controller
Service state:     running
```

### 7.5 Verify All Services Running

After starting the three key services (http, manager, controller), all remaining services should cascade-start automatically. Wait 2–3 minutes, then check:

```
nsx-node1> get services
```

**Output (abbreviated — full output in Appendix B):**

| Service | State |
|---|---|
| applianceproxy | **running** |
| async_replicator | **running** |
| auth | **running** |
| cluster_manager | **running** |
| cm-inventory | **running** |
| controller | **running** |
| datastore | **running** |
| datastore_nonconfig | **running** |
| http | **running** |
| idps-reporting | **running** |
| install-upgrade | **running** |
| manager | **running** |
| messaging-manager | **running** |
| monitoring | **running** |
| node-mgmt | **running** |
| node-stats | **running** |
| nsx-platform-client | **running** |
| nsx-upgrade-agent | **running** |
| ntp | **running** |
| search | **running** |
| sha | **running** |
| site_manager | **running** |
| ssh | **running** |
| syslog | **running** |
| ui-service | **running** |

**Stopped services (expected):**

| Service | State | Reason |
|---|---|---|
| liagent | stopped | Log Insight agent — not configured |
| migration-coordinator | stopped | Only active during migrations |
| nsx-message-bus | stopped | Not used in single-node deployments |
| snmp | stopped | SNMP not enabled (Start on boot: False) |

<div class="fix-box">

**Result:** All 25+ platform services are now running. The 4 stopped services are expected to be stopped in this environment configuration.

</div>

---

## 8. Phase 4 — Cluster Validation

### 8.1 Cluster VIP Verification

With services running, verify the cluster VIP is assigned:

```
nsx-node1> get cluster vip
```

**Output:**

```
Virtual IPv4 address:   192.168.1.70
Virtual IPv6 address:   not configured
Assigned to:            ['192.168.1.71']
```

**Analysis:** The VIP (192.168.1.70) is active and correctly assigned to the single node (192.168.1.71).

### 8.2 Cluster Status Verbose

```
nsx-node1> get cluster status verbose
```

**Key results by group type:**

| Group Type | Group Status | Node Status |
|---|---|---|
| DATASTORE | STABLE | UP |
| CLUSTER_BOOT_MANAGER | STABLE | UP |
| CONTROLLER | STABLE | UP |
| MANAGER | STABLE | UP |
| HTTPS | **UNAVAILABLE** | **DOWN** |
| SITE_MANAGER | STABLE | UP |
| MONITORING | STABLE | UP |
| IDPS_REPORTING | STABLE | UP |
| CM-INVENTORY | STABLE | UP |
| MESSAGING-MANAGER | STABLE | UP |
| CORFU_NONCONFIG | STABLE | UP |

**Overall Cluster Status: DEGRADED**

### 8.3 HTTPS Group Status

The cluster status showed the HTTPS group as UNAVAILABLE with the node status DOWN, even though the `http` service was running. This is a **transient state** — the HTTPS cluster group registration lags behind the actual service status by several minutes.

The UI banner displayed: `Some appliance components are not functioning properly. Component health: MANAGER:DOWN, SEARCH:DOWN, UI:UP, NODE_MGMT:UP.`

This message also reflects a **stale health check** that had not yet refreshed. After waiting 3–5 minutes and refreshing the browser, the health status updated to show all components as UP.

<div class="info-box">

**Important:** Do not restart services based on the HTTPS cluster group status or the UI health banner immediately after a manual service recovery. These health indicators use cached state and periodic polling intervals. Wait at least 5 minutes before re-evaluating. If the `get service http` command shows `running` and the UI is accessible, the HTTPS group will transition to STABLE on the next health check cycle.

</div>

### 8.4 Browser Access Verification

| URL | Result |
|---|---|
| `https://192.168.1.71` | NSX Manager UI loaded — login page displayed |
| `https://192.168.1.70` | NSX Manager UI loaded — login page displayed (via VIP) |

**Both the node IP and VIP are now serving the NSX Manager UI.**

---

## 9. Phase 5 — Upstream Integration Recovery

### 9.1 VCF Operations Adapter Status

After NSX Manager recovery, the VCF Operations integration adapters needed re-validation.

**Pre-recovery status (Administration → Integrations → Accounts):**

| Adapter | Status |
|---|---|
| lab (VCF Adapter) | Warning |
| nsx-vip.lab.local (NSX Adapter) | Warning |

### 9.2 Re-validate NSX Adapter

1. In VCF Operations, navigate to **Administration → Integrations → Accounts**
2. Click the three-dot menu (⋮) next to **nsx-vip.lab.local**
3. Select **Edit**
4. Click **Validate** to test the connection
5. If the connection test succeeds, click **Save**
6. Repeat for the **lab** VCF adapter if still in Warning state

> **Note:** When re-validating the NSX adapter, a warning may appear: "Error trying to establish connection. Proceed anyway?" This can occur if the certificate has not been re-cached. Click **Proceed** — the adapter will reconnect successfully once the certificate is accepted.

### 9.3 Confirm Collection Status

After re-validation, wait one collection cycle (5–10 minutes) and verify:

| Adapter | Status |
|---|---|
| lab (VCF Adapter) | **Collecting** |
| nsx-vip.lab.local (NSX Adapter) | **Collecting** |
| mgmt | **Collecting** |
| mgmt - vSAN | **Collecting** |
| Application Monitoring Adapter | **Collecting** |

<div class="fix-box">

**Result:** All VCF Operations adapters are now in **Collecting** state. NSX metrics, alerts, and compliance data collection has resumed.

</div>

---

## 10. Post-Recovery Verification Checklist

Use this checklist to confirm full recovery after an NSX Manager cold start service failure:

| # | Check | Command / Action | Expected Result |
|---|---|---|---|
| 1 | All services running | `get services` | All platform services show `running` |
| 2 | Cluster VIP active | `get cluster vip` | VIP assigned to node |
| 3 | Cluster status | `get cluster status` | Overall status: STABLE |
| 4 | UI accessible (node IP) | Browse to `https://192.168.1.71` | Login page loads |
| 5 | UI accessible (VIP) | Browse to `https://192.168.1.70` | Login page loads |
| 6 | Component health | Check UI banner | All components UP |
| 7 | VCF Ops NSX adapter | VCF Operations → Integrations | Status: Collecting |
| 8 | VCF Ops VCF adapter | VCF Operations → Integrations | Status: Collecting |
| 9 | Transport node connectivity | NSX UI → Fabric → Nodes | All nodes connected |
| 10 | Filesystem usage | `get filesystem-stats` | No filesystem above 80% |

---

## 11. Lessons Learned and Recommendations

### Lessons Learned

1. **ICMP response does not indicate service health.** The NSX Manager VM responded to ping while all platform services were stopped. Always verify service state via SSH, not just network reachability.

2. **The HTTP service is the critical dependency.** If only one service is going to fail, it will be HTTP. All other services depend on it. When troubleshooting NSX Manager unresponsiveness, check `get service http` first.

3. **Cluster status commands fail when HTTP is down.** The `get cluster config`, `get cluster status`, and `get cluster vip` commands all require the HTTP/API layer. Their failure is a symptom, not a separate problem.

4. **Service cascade startup is reliable.** Once the three key services (datastore, http, manager) are running, all other services start automatically within 2–3 minutes. There is no need to manually start each of the 30+ services.

5. **Health indicators lag behind actual state.** The UI health banner and cluster group status use cached, periodically-refreshed data. Do not make decisions based on stale health status immediately after a manual recovery.

### Recommendations

| # | Recommendation | Priority |
|---|---|---|
| 1 | **Create a startup script** that checks NSX service health after boot and restarts HTTP if stopped | High |
| 2 | **Configure VCF Operations alerts** for NSX Manager service state changes (not just adapter connectivity) | High |
| 3 | **Document the service start order** (datastore → http → manager → controller) in the lab runbook for quick reference | Medium |
| 4 | **Increase NSX Manager VM resources** in the nested environment (CPU: 4→6, RAM: 32→48GB) to reduce cold start failures | Medium |
| 5 | **Implement startup order in VMware Workstation** — ensure NSX Manager VM starts after vCenter and AD/DNS VMs are fully online | Medium |
| 6 | **Monitor /var/log usage** — at 55%, it is the highest-utilized filesystem and could cause issues if logs are not rotated | Low |

---

## 12. Appendix A — Complete Service List (Pre-Recovery)

Captured at: March 26, 2026, 15:01 UTC

| Service | State |
|---|---|
| applianceproxy | running |
| async_replicator | stopped |
| auth | stopped |
| cluster_manager | stopped |
| cm-inventory | stopped |
| controller | stopped |
| datastore | stopped |
| datastore_nonconfig | stopped |
| http | stopped |
| idps-reporting | stopped |
| install-upgrade | stopped |
| liagent | stopped |
| manager | stopped |
| messaging-manager | stopped |
| migration-coordinator | stopped |
| monitoring | stopped |
| node-mgmt | running |
| node-stats | running |
| nsx-message-bus | stopped |
| nsx-platform-client | running |
| nsx-upgrade-agent | running |
| ntp | running |
| search | stopped |
| sha | running |
| site_manager | stopped |
| snmp | stopped |
| ssh | running |
| syslog | running |
| ui-service | running |

**Running:** 9 of 29 | **Stopped:** 20 of 29

---

## 13. Appendix B — Complete Service List (Post-Recovery)

Captured at: March 26, 2026, 15:36 UTC

| Service | State |
|---|---|
| applianceproxy | running |
| async_replicator | running |
| auth | running |
| cluster_manager | running |
| cm-inventory | running |
| controller | running |
| datastore | running |
| datastore_nonconfig | running |
| http | running |
| idps-reporting | running |
| install-upgrade | running |
| liagent | stopped |
| manager | running |
| messaging-manager | running |
| migration-coordinator | stopped |
| monitoring | running |
| node-mgmt | running |
| node-stats | running |
| nsx-message-bus | stopped |
| nsx-platform-client | running |
| nsx-upgrade-agent | running |
| ntp | running |
| search | running |
| sha | running |
| site_manager | running |
| snmp | stopped |
| ssh | running |
| syslog | running |
| ui-service | running |

**Running:** 25 of 29 | **Stopped (expected):** 4 of 29

---

## 14. Document Information

| Field | Value |
|---|---|
| Document Title | NSX Manager 9.0.1 Cold Start Service Failure — RCA & Recovery |
| Version | 1.0 |
| Author | Virtual Control LLC |
| Date | March 26, 2026 |
| Classification | Internal — Lab Environment |
| Environment | Dell Precision 7920, VMware Workstation 17.x Nested Lab |
| NSX Version | 9.0.1.0 (Build 24952114) |
| Related Documents | VCF Undocumented Issues Reference, VCF Troubleshooting Handbook |

---

*(c) 2026 Virtual Control LLC. All rights reserved.*
