---
title: "vSAN Health Check Handbook"
subtitle: "Comprehensive Health Verification for vSAN in VCF 9"
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
  headerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">vSAN Health Check Handbook &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  footerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">Page <span class="pageNumber"></span> of <span class="totalPages"></span> &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  displayHeaderFooter: true
---

<div class="cover-page">

# vSAN Health Check Handbook

<div class="subtitle">Comprehensive Health Verification for vSAN in VMware Cloud Foundation 9</div>

<div class="meta">
<strong>Prepared by:</strong> Virtual Control LLC<br>
<strong>Date:</strong> March 2026<br>
<strong>Version:</strong> 1.0<br>
<strong>Classification:</strong> Internal Use<br>
<strong>Platform:</strong> VMware Cloud Foundation 9.x / vSAN 8.x ESA &amp; OSA
</div>

</div>

---

<div class="toc">

## Table of Contents

<ul>
  <li><a href="#overview-and-purpose">1. Overview &amp; Purpose</a>
    <ul>
      <li><a href="#scope">1.1 Scope</a></li>
      <li><a href="#when-to-run">1.2 When to Run Health Checks</a></li>
      <li><a href="#audience">1.3 Target Audience</a></li>
    </ul>
  </li>
  <li><a href="#prerequisites">2. Prerequisites</a>
    <ul>
      <li><a href="#access-requirements">2.1 Access Requirements</a></li>
      <li><a href="#tools-and-utilities">2.2 Tools &amp; Utilities</a></li>
      <li><a href="#rvc-setup">2.3 RVC Setup</a></li>
      <li><a href="#powercli-setup">2.4 PowerCLI Setup</a></li>
    </ul>
  </li>
  <li><a href="#quick-reference-summary">3. Quick Reference Summary Table</a></li>
  <li><a href="#vsan-cluster-health">4. vSAN Cluster Health</a>
    <ul>
      <li><a href="#cluster-health-list">4.1 Cluster Health List</a></li>
      <li><a href="#proactive-health-tests">4.2 Proactive Health Tests</a></li>
      <li><a href="#vsan-health-service">4.3 vSAN Health Service</a></li>
      <li><a href="#cluster-membership">4.4 Cluster Membership</a></li>
    </ul>
  </li>
  <li><a href="#disk-group-status">5. Disk Group Status</a>
    <ul>
      <li><a href="#disk-group-listing">5.1 Disk Group Listing</a></li>
      <li><a href="#cache-capacity-tier">5.2 Cache &amp; Capacity Tier Status</a></li>
      <li><a href="#smart-data">5.3 SMART Data Analysis</a></li>
      <li><a href="#vsan-storage-list">5.4 vSAN Storage List</a></li>
    </ul>
  </li>
  <li><a href="#capacity-analysis">6. Capacity Analysis</a>
    <ul>
      <li><a href="#capacity-overview">6.1 Capacity Overview</a></li>
      <li><a href="#dedup-compression">6.2 Dedup &amp; Compression Savings</a></li>
      <li><a href="#thin-provisioning">6.3 Thin Provisioning</a></li>
      <li><a href="#slack-space">6.4 Slack Space Calculation</a></li>
      <li><a href="#capacity-thresholds">6.5 Capacity Thresholds</a></li>
    </ul>
  </li>
  <li><a href="#resync-status">7. Resync Status</a>
    <ul>
      <li><a href="#active-resyncs">7.1 Active Resyncs</a></li>
      <li><a href="#resync-eta">7.2 Resync ETA</a></li>
      <li><a href="#resync-performance-impact">7.3 Performance Impact</a></li>
    </ul>
  </li>
  <li><a href="#vsan-network-health">8. vSAN Network Health</a>
    <ul>
      <li><a href="#vmkernel-adapters">8.1 vSAN VMkernel Adapters</a></li>
      <li><a href="#multicast-unicast">8.2 Multicast &amp; Unicast Check</a></li>
      <li><a href="#jumbo-frames">8.3 Jumbo Frame Validation</a></li>
      <li><a href="#network-partition">8.4 Network Partition Detection</a></li>
      <li><a href="#witness-connectivity">8.5 Witness Host Connectivity</a></li>
    </ul>
  </li>
  <li><a href="#performance-health">9. Performance Health</a>
    <ul>
      <li><a href="#iops-latency">9.1 IOPS &amp; Latency</a></li>
      <li><a href="#congestion">9.2 Congestion</a></li>
      <li><a href="#outstanding-io">9.3 Outstanding IO</a></li>
      <li><a href="#vscsistats">9.4 vscsiStats</a></li>
      <li><a href="#performance-service">9.5 Performance Service</a></li>
    </ul>
  </li>
  <li><a href="#object-health-compliance">10. Object Health &amp; Compliance</a>
    <ul>
      <li><a href="#object-count">10.1 Object Count</a></li>
      <li><a href="#compliance-state">10.2 Compliance State</a></li>
      <li><a href="#inaccessible-objects">10.3 Inaccessible Objects</a></li>
      <li><a href="#reduced-redundancy">10.4 Reduced Redundancy Objects</a></li>
    </ul>
  </li>
  <li><a href="#stretched-cluster-health">11. Stretched Cluster Health</a>
    <ul>
      <li><a href="#preferred-secondary-site">11.1 Preferred &amp; Secondary Site</a></li>
      <li><a href="#witness-host">11.2 Witness Host</a></li>
      <li><a href="#site-affinity-rules">11.3 Site Affinity Rules</a></li>
      <li><a href="#inter-site-latency">11.4 Inter-Site Latency</a></li>
    </ul>
  </li>
  <li><a href="#fault-domains">12. Fault Domains</a>
    <ul>
      <li><a href="#fd-configuration">12.1 Fault Domain Configuration</a></li>
      <li><a href="#fd-host-distribution">12.2 Host Distribution</a></li>
      <li><a href="#fd-policy-compliance">12.3 Policy Compliance with Fault Domains</a></li>
    </ul>
  </li>
  <li><a href="#vsan-health-service-detail">13. vSAN Health Service Detail</a>
    <ul>
      <li><a href="#health-service-status">13.1 Health Service Status</a></li>
      <li><a href="#test-categories">13.2 Test Categories</a></li>
      <li><a href="#silenced-alarms">13.3 Silenced Alarms</a></li>
    </ul>
  </li>
  <li><a href="#hcl-compliance">14. HCL Compliance</a>
    <ul>
      <li><a href="#controller-driver-firmware">14.1 Controller, Driver &amp; Firmware</a></li>
      <li><a href="#hcl-database-update">14.2 HCL Database Update</a></li>
    </ul>
  </li>
  <li><a href="#port-reference-table">15. Port Reference Table</a></li>
  <li><a href="#common-issues-remediation">16. Common Issues &amp; Remediation</a>
    <ul>
      <li><a href="#disk-failures">16.1 Disk Failures</a></li>
      <li><a href="#network-partition-issues">16.2 Network Partition</a></li>
      <li><a href="#resync-storms">16.3 Resync Storms</a></li>
      <li><a href="#performance-degradation">16.4 Performance Degradation</a></li>
      <li><a href="#clom-errors">16.5 CLOM Errors</a></li>
    </ul>
  </li>
  <li><a href="#cli-quick-reference-card">17. CLI Quick Reference Card</a></li>
  <li><a href="#powercli-quick-reference">18. PowerCLI Quick Reference</a></li>
</ul>

</div>

<div class="page-break"></div>

<a id="overview-and-purpose"></a>

# 1. Overview & Purpose

This handbook provides a systematic, step-by-step approach to verifying the health and operational readiness of vSAN clusters running within VMware Cloud Foundation (VCF) 9 environments. It covers both vSAN Original Storage Architecture (OSA) and the vSAN Express Storage Architecture (ESA), which is the recommended configuration in VCF 9.

<a id="scope"></a>

## 1.1 Scope

This document covers the following health check domains:

| Domain | Description |
|--------|-------------|
| **Cluster Health** | Overall cluster status, membership, and health service results |
| **Disk Group Status** | Physical disk health, SMART data, cache and capacity tiers |
| **Capacity Analysis** | Space utilization, deduplication, compression, slack space |
| **Resync Operations** | Active resyncs, component movement, ETA, and impact |
| **Network Health** | VMkernel configuration, connectivity, jumbo frames, partitions |
| **Performance** | IOPS, latency, congestion, outstanding IO metrics |
| **Object Health** | Object compliance, accessibility, redundancy state |
| **Stretched Cluster** | Site configuration, witness host, inter-site latency |
| **Fault Domains** | Domain layout, host distribution, policy interaction |
| **HCL Compliance** | Controller, driver, and firmware compatibility verification |

<div class="info-box">
<strong>VCF 9 Context:</strong> In VCF 9, vSAN is the default and only supported principal storage for the management domain. Workload domains may use vSAN, NFS, VMFS on FC, or vVols. This handbook focuses on the vSAN principal storage layer but applies to any vSAN-backed workload domain as well.
</div>

<a id="when-to-run"></a>

## 1.2 When to Run Health Checks

Health checks should be executed at these critical intervals:

| Trigger | Frequency | Checks |
|---------|-----------|--------|
| Routine maintenance | Weekly | Full suite |
| Pre-upgrade (VCF lifecycle) | Before each LCM bundle | Full suite |
| Post-upgrade | Immediately after LCM completes | Full suite |
| Host addition/removal | After cluster change | Cluster, disk, network, capacity |
| Disk replacement | After replacement completes | Disk group, resync, object health |
| Network change | After vDS/vmkernel modification | Network health, connectivity |
| Performance complaint | On demand | Performance, congestion, resync |
| After power event | After datacenter power restoration | Full suite |
| Pre-expansion | Before adding workload domains | Capacity, performance baseline |

<a id="audience"></a>

## 1.3 Target Audience

This handbook is intended for:

- **VCF Administrators** managing day-to-day operations
- **Storage Engineers** responsible for vSAN health and capacity
- **Network Engineers** validating vSAN transport configuration
- **Operations Teams** performing routine maintenance windows
- **Escalation Engineers** troubleshooting vSAN issues

<div class="page-break"></div>

<a id="prerequisites"></a>

# 2. Prerequisites

<a id="access-requirements"></a>

## 2.1 Access Requirements

| Requirement | Detail |
|-------------|--------|
| **vCenter SSO Admin** | `administrator@vsphere.local` or equivalent role |
| **ESXi Root Access** | SSH enabled on target hosts (temporarily, disable after) |
| **SDDC Manager Access** | Admin-level access for LCM and inventory queries |
| **vSAN Witness Host** | Root access if stretched cluster is deployed |
| **Network Access** | Ability to reach vSAN VMkernel IPs on port 2233 |

<div class="warn-box">
<strong>Security Note:</strong> SSH access to ESXi hosts should be enabled only for the duration of the health check. In VCF 9, SSH is disabled by default and locked down via the Security Configuration Guide. Always disable SSH and re-enable lockdown mode after completing CLI-based checks.
</div>

<a id="tools-and-utilities"></a>

## 2.2 Tools & Utilities

#### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| `esxcli` | Built into ESXi 8.x | Primary CLI for vSAN health checks |
| `vSAN Health Service` | Built into vCenter 8.x | Automated health test framework |
| PowerCLI | 13.3+ | Scripted health checks and reporting |
| RVC (Ruby vSphere Console) | Built into vCenter appliance | Deep vSAN diagnostics |
| `vmkping` | Built into ESXi | vSAN network validation |
| `vsanDiskMgmt` | Built into ESXi | Disk management and SMART queries |
| Python (`pyVmomi`) | 8.0+ | API-driven automation |

#### Optional Tools

| Tool | Purpose |
|------|---------|
| vSAN Observer | Real-time performance monitoring (HTML5 dashboard) |
| vRealize Operations / Aria Operations | Trending, capacity forecasting |
| VDT (VMware Diagnostic Tool) | Automated diagnostic collection |
| SOS Report | Support bundle generation |

<a id="rvc-setup"></a>

## 2.3 RVC Setup

The Ruby vSphere Console is accessed directly from the vCenter Server Appliance (VCSA).

```bash
# SSH to VCSA
ssh root@vcsa-01.vcf.local

# Launch RVC
rvc administrator@vsphere.local@localhost

# Navigate to the vSAN cluster
cd /localhost/SDDC-Datacenter/computers/SDDC-Cluster1

# Run the vSAN health check
vsan.health.health_summary .
```

#### Key RVC Commands for vSAN

```bash
# Full cluster health summary
vsan.health.health_summary /localhost/datacenter/computers/cluster

# Disk balance check
vsan.disks_stats /localhost/datacenter/computers/cluster

# Object placement info
vsan.object_info /localhost/datacenter/computers/cluster

# Network partition check
vsan.cluster_info /localhost/datacenter/computers/cluster

# Resync dashboard
vsan.resync_dashboard /localhost/datacenter/computers/cluster

# Performance diagnostics
vsan.perf.stats_object_list /localhost/datacenter/computers/cluster
```

<a id="powercli-setup"></a>

## 2.4 PowerCLI Setup

```powershell
# Install or update PowerCLI
Install-Module -Name VMware.PowerCLI -Scope CurrentUser -Force

# Configure certificate handling for lab/internal environments
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false

# Connect to vCenter
Connect-VIServer -Server vcsa-01.vcf.local -User administrator@vsphere.local -Password '<password>'

# Verify vSAN module is loaded
Get-Module VMware.VimAutomation.Storage -ListAvailable
```

<div class="info-box">
<strong>PowerCLI 13.3+:</strong> VCF 9 ships with vCenter 8.x which requires PowerCLI 13.3 or later for full vSAN ESA cmdlet support. Ensure you are running the latest version before executing vSAN commands.
</div>

<div class="page-break"></div>

<a id="quick-reference-summary"></a>

# 3. Quick Reference Summary Table

The following table provides a consolidated view of every health check in this handbook with pass/warn/fail criteria.

| # | Check | CLI / Method | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|---|-------|-------------|------|------|------|
| 1 | Cluster Health Status | `esxcli vsan health cluster list` | All tests green | Any test yellow | Any test red |
| 2 | Cluster Membership | `esxcli vsan cluster get` | All hosts in cluster | Host count mismatch | Partitioned cluster |
| 3 | Disk Group Status | `esxcli vsan storage list` | All disks healthy | Disk degraded | Disk absent/failed |
| 4 | SMART Health | `esxcli vsan debug disk smart get` | All attributes OK | Wear leveling > 80% | Reallocated sectors > 0 |
| 5 | Capacity Used % | vSAN UI / PowerCLI | < 70% | 70-80% | > 80% |
| 6 | Slack Space | Calculated | >= 25% of raw | 15-25% of raw | < 15% of raw |
| 7 | Dedup/Compression Ratio | vSAN UI | > 1.5x | 1.0-1.5x | < 1.0x (overhead) |
| 8 | Active Resyncs | `esxcli vsan debug resync summary` | 0 active | < 100 components | > 100 components |
| 9 | Resync ETA | vSAN UI | < 1 hour | 1-8 hours | > 8 hours |
| 10 | vSAN VMkernel Config | `esxcli network ip interface list` | vSAN vmk on each host | MTU mismatch | vmk missing |
| 11 | Jumbo Frame Test | `vmkping -s 8972 -d` | 0% packet loss | Intermittent loss | Complete failure |
| 12 | Network Partition | Health service | No partition | N/A | Partition detected |
| 13 | Read Latency | vSAN perf service | < 1 ms | 1-5 ms | > 5 ms |
| 14 | Write Latency | vSAN perf service | < 2 ms | 2-10 ms | > 10 ms |
| 15 | Congestion | `esxcli vsan debug controller list` | 0 | 1-40 | > 40 |
| 16 | Outstanding IO | `vsish` | < 32 | 32-64 | > 64 |
| 17 | Object Health | `esxcli vsan debug object health summary` | All healthy | Reduced redundancy | Inaccessible objects |
| 18 | Policy Compliance | vSAN UI / PowerCLI | All compliant | Non-compliant (rebuilding) | Non-compliant (stuck) |
| 19 | Witness Host | `esxcli vsan cluster get` | Connected | High latency | Disconnected |
| 20 | Inter-Site Latency | `vmkping` | < 5 ms RTT | 5-100 ms | > 200 ms / timeout |
| 21 | Fault Domain Count | vSAN UI | >= 3 FDs | 2 FDs | 1 FD (no protection) |
| 22 | HCL Controller | Health service | Certified | DB outdated > 90 days | Not on HCL |
| 23 | HCL Driver/Firmware | Health service | Matched | Minor mismatch | Critical mismatch |
| 24 | Health Service Status | vCenter UI | Running, recent test | Last test > 24h ago | Service not running |
| 25 | Silenced Alarms | Health service | 0 silenced | 1-3 silenced | > 3 silenced |

<div class="page-break"></div>

<a id="vsan-cluster-health"></a>

# 4. vSAN Cluster Health

<a id="cluster-health-list"></a>

## 4.1 Cluster Health List

The primary entry point for vSAN health is the `esxcli vsan health cluster list` command. This queries the vSAN health service and returns the state of every registered health test.

#### Command

```bash
esxcli vsan health cluster list
```

#### Expected Output (Healthy)

```
Group: Cluster
   Overall Health: green
   Tests:
      vSAN Health Service Up-To-Date:                green
      vSAN Build Recommendation Engine Health:       green
      vSAN CLOMD Liveness:                           green
      vSAN Disk Balance:                             green
      vSAN Object Health:                            green
      vSAN Cluster Partition:                        green

Group: Network
   Overall Health: green
   Tests:
      All Hosts Have a vSAN VMkernel Adapter:        green
      All Hosts Have Matching Subnets:               green
      vSAN: Basic (Unicast) Connectivity Check:      green
      vSAN: MTU Check (Ping with Large Packet Size): green
      vMotion: Basic Connectivity Check:             green

Group: Physical Disk
   Overall Health: green
   Tests:
      vSAN Disk Health:                              green
      Metadata Health:                               green
      Component Metadata Health:                     green
      Congestion:                                    green
      Disk Space Usage:                              green

Group: Data
   Overall Health: green
   Tests:
      vSAN Object Health:                            green
      vSAN VM Health:                                green

Group: Limits
   Overall Health: green
   Tests:
      Current Cluster Situation:                     green
      After 1 Additional Host Failure:               green
      Host Component Limit:                          green
```

#### Pass / Warn / Fail Criteria

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | All groups show `green` | No action required |
| <span class="badge-warn">WARN</span> | One or more tests show `yellow` | Investigate the specific test; see relevant section of this handbook |
| <span class="badge-fail">FAIL</span> | Any test shows `red` | Immediate investigation required; do NOT proceed with maintenance |

<div class="fix-box">
<strong>Remediation:</strong> If any test returns red, drill into the specific group. Run <code>esxcli vsan health cluster list -t "test name"</code> to get details on the specific failing test. Cross-reference with the relevant section of this handbook for targeted remediation steps.
</div>

<a id="proactive-health-tests"></a>

## 4.2 Proactive Health Tests

vSAN proactive tests simulate failure scenarios to predict cluster behavior under stress.

#### Proactive Rebalance Test

```bash
esxcli vsan health cluster list -t "vSAN Disk Balance"
```

#### What It Checks

- Disk usage variance across all capacity disks
- Whether any single disk has > 30% more usage than the average
- Recommendations for proactive rebalancing

#### Expected Output (Healthy)

```
Health Test: vSAN Disk Balance
   Status: green
   Description: Disks are well balanced. Max variance: 8%
```

#### Triggering a Manual Rebalance

```bash
# From RVC
vsan.proactive_rebalance /localhost/datacenter/computers/cluster --start
```

<div class="warn-box">
<strong>Caution:</strong> Proactive rebalance generates resync traffic. Only run during maintenance windows or periods of low IO activity. The rebalance operation can be throttled or stopped at any time.
</div>

<a id="vsan-health-service"></a>

## 4.3 vSAN Health Service

The vSAN Health Service runs within vCenter and executes periodic health tests.

#### Verify Health Service Status

```bash
# On any ESXi host in the cluster
esxcli vsan health cluster list -t "vSAN Health Service Up-To-Date"
```

#### Force a Health Check Run via PowerCLI

```powershell
# Get the vSAN cluster
$cluster = Get-Cluster -Name "SDDC-Cluster1"

# Get vSAN view
$vsanClusterHealthSystem = Get-VsanView -Id "VsanVcClusterHealthSystem-vsan-cluster-health-system"

# Run health check
$vsanClusterHealthSystem.VsanQueryVcClusterHealthSummary(
    $cluster.ExtensionData.MoRef,
    $null, $null, $true, $null, $null, "defaultView"
)
```

#### Expected Behavior

| Attribute | Expected |
|-----------|----------|
| Service Running | Yes |
| Last Test Time | Within 60 minutes |
| Test Result Format | Per-group green/yellow/red |
| Auto-Run Interval | Every 60 minutes (configurable) |

<a id="cluster-membership"></a>

## 4.4 Cluster Membership

Every host in a vSAN cluster must be an active member. Use `esxcli vsan cluster get` to verify.

#### Command

```bash
esxcli vsan cluster get
```

#### Expected Output (Healthy)

```
Cluster Information
   Enabled: true
   Current Local Time: 2026-03-26T14:30:00Z
   Local Node UUID: 5f3e8c7a-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Local Node Type: NORMAL
   Local Node State: MASTER
   Member Count: 4
   Sub-Cluster Member UUIDs: 5f3e8c7a-..., 6a4f9d8b-..., 7b5a0e9c-..., 8c6b1fad-...
   Sub-Cluster Membership Entry Revision: 12
   Sub-Cluster Member Count: 4
   Maintenance Mode State: OFF
```

#### Verify From All Hosts

```bash
# Run on each ESXi host to ensure consistent membership
for host in esx01 esx02 esx03 esx04; do
  echo "=== $host ==="
  ssh root@$host 'esxcli vsan cluster get | grep "Member Count"'
done
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | Member Count matches expected host count on ALL hosts | Healthy |
| <span class="badge-warn">WARN</span> | A host shows `BACKUP` instead of `MASTER`/`AGENT` | Verify roles; may be transitional |
| <span class="badge-fail">FAIL</span> | Member count differs between hosts (split-brain) | Network partition detected -- see Section 8.4 |

<div class="fix-box">
<strong>Remediation (Split-Brain):</strong><br>
1. Check vSAN network connectivity between all hosts: <code>vmkping -I vmk1 &lt;target_ip&gt;</code><br>
2. Verify the vSAN portgroup is consistent across all hosts<br>
3. Check for physical switch issues on the vSAN VLAN<br>
4. If a host is isolated, restart the vSAN CLOMD service: <code>/etc/init.d/clomd restart</code><br>
5. As a last resort, remove and re-add the host to the vSAN cluster
</div>

<div class="page-break"></div>

<a id="disk-group-status"></a>

# 5. Disk Group Status

<a id="disk-group-listing"></a>

## 5.1 Disk Group Listing

In vSAN OSA, storage is organized into disk groups (1 cache SSD + 1-7 capacity disks). In vSAN ESA (VCF 9 default), all NVMe devices participate in a single storage pool without a separate cache tier.

#### Command (OSA)

```bash
esxcli vsan storage list
```

#### Expected Output (OSA Healthy)

```
Device: naa.55cd2e414f5356c0
   Display Name: naa.55cd2e414f5356c0
   Is SSD: true
   In CMMDS: true
   On-disk Format Version: 15
   Is Capacity Tier: false
   Is Cache Tier: true
   RAID Level: NA
   vSAN UUID: 52e9a1f4-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   vSAN Disk Group UUID: 52e9a1f4-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   vSAN Disk Group Name: naa.55cd2e414f5356c0
   Health Status: Healthy

Device: naa.55cd2e414f53789a
   Display Name: naa.55cd2e414f53789a
   Is SSD: true
   In CMMDS: true
   On-disk Format Version: 15
   Is Capacity Tier: true
   Is Cache Tier: false
   RAID Level: NA
   vSAN UUID: 63fa2b05-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Health Status: Healthy
```

#### Command (ESA)

```bash
esxcli vsan storage list
```

#### Expected Output (ESA Healthy)

```
Device: t10.NVMe____Dell_Ent_NVMe_v2_AGN_RI_U.2_1.6TB
   Display Name: Dell Ent NVMe AGN RI U.2 1.6TB
   Is SSD: true
   In CMMDS: true
   On-disk Format Version: 19
   Is Capacity Tier: true
   Is Cache Tier: false
   ESA Eligible: true
   Storage Pool UUID: 74ab3c16-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Health Status: Healthy
```

<a id="cache-capacity-tier"></a>

## 5.2 Cache & Capacity Tier Status

#### Check Individual Disk Status

```bash
# List all vSAN disks with health
esxcli vsan storage list | grep -E "Display Name|Health Status|Is Cache|Is Capacity"
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | All disks: `Health Status: Healthy` | No action |
| <span class="badge-warn">WARN</span> | Any disk: `Health Status: Degraded` | Schedule replacement at next window |
| <span class="badge-fail">FAIL</span> | Any disk: `Health Status: Failed` or missing | Immediate replacement required |

<div class="danger">
<strong>Critical:</strong> If a cache tier disk fails in OSA, the ENTIRE disk group goes offline. All components on capacity disks in that group become unavailable until the cache disk is replaced and the disk group is recreated. In ESA, single disk failures are tolerated without disk group loss.
</div>

<a id="smart-data"></a>

## 5.3 SMART Data Analysis

Self-Monitoring, Analysis, and Reporting Technology (SMART) provides early warning of disk failure.

#### Command

```bash
esxcli vsan debug disk smart get -d naa.55cd2e414f5356c0
```

#### Expected Output (Healthy)

```
Parameter                     Value  Threshold  Worst  Status
----------------------------  -----  ---------  -----  ------
Health Status                 OK     N/A        N/A    OK
Media Wearout Indicator       98     0          98     OK
Write Error Count             0      0          0      OK
Read Error Count              0      0          0      OK
Power-on Hours                14820  0          14820  OK
Power Cycle Count             12     0          12     OK
Reallocated Sector Count      0      0          0      OK
Uncorrectable Error Count     0      0          0      OK
Temperature Celsius           34     0          42     OK
```

#### Critical SMART Attributes to Monitor

| Attribute | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|-----------|------|------|------|
| Media Wearout Indicator | > 20% remaining | 5-20% remaining | < 5% remaining |
| Reallocated Sector Count | 0 | 1-10 | > 10 |
| Uncorrectable Error Count | 0 | 1-5 | > 5 |
| Temperature Celsius | < 50C | 50-70C | > 70C |
| Write Error Count | 0 | 1-10 | > 10 |
| Read Error Count | 0 | 1-10 | > 10 |

<div class="fix-box">
<strong>Remediation (Failing SMART):</strong><br>
1. Open a VMware SR or OEM hardware support case for disk replacement<br>
2. Place the host in maintenance mode (ensure evacuate data): <code>esxcli system maintenanceMode set -e true -m ensureAccessibility</code><br>
3. Remove the disk from the disk group: <code>esxcli vsan storage remove -d naa.xxxx</code><br>
4. Physically replace the disk<br>
5. Add the new disk: <code>esxcli vsan storage add -d naa.xxxx -s naa.cache_disk</code><br>
6. Exit maintenance mode: <code>esxcli system maintenanceMode set -e false</code>
</div>

<a id="vsan-storage-list"></a>

## 5.4 vSAN Storage List -- Complete Output

#### Full Storage Inventory Command

```bash
# Comprehensive disk listing with all properties
esxcli vsan storage list --format=xml
```

#### PowerCLI Alternative

```powershell
# Get all vSAN disk information
$cluster = Get-Cluster "SDDC-Cluster1"
$vsanDisks = Get-VsanDisk -Cluster $cluster

foreach ($disk in $vsanDisks) {
    [PSCustomObject]@{
        Host          = $disk.VsanDiskGroup.VMHost.Name
        DiskGroup     = $disk.VsanDiskGroup.Name
        CanonicalName = $disk.CanonicalName
        IsSSD         = $disk.IsSsd
        IsCacheDisk   = $disk.IsCacheDisk
        CapacityGB    = [math]::Round($disk.CapacityGB, 2)
    }
} | Format-Table -AutoSize
```

<div class="page-break"></div>

<a id="capacity-analysis"></a>

# 6. Capacity Analysis

<a id="capacity-overview"></a>

## 6.1 Capacity Overview

#### Command

```bash
# From any ESXi host in the cluster
esxcli vsan debug object health summary get
```

#### PowerCLI Method (Recommended)

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$spaceReport = Get-VsanSpaceUsage -Cluster $cluster

# Display capacity summary
[PSCustomObject]@{
    "Total Capacity (TB)"     = [math]::Round($spaceReport.TotalCapacityGB / 1024, 2)
    "Used Capacity (TB)"      = [math]::Round($spaceReport.UsedCapacityGB / 1024, 2)
    "Free Capacity (TB)"      = [math]::Round($spaceReport.FreeCapacityGB / 1024, 2)
    "Used %"                  = [math]::Round(($spaceReport.UsedCapacityGB / $spaceReport.TotalCapacityGB) * 100, 1)
}
```

#### Expected Output

```
Total Capacity (TB)    : 23.64
Used Capacity (TB)     :  9.82
Free Capacity (TB)     : 13.82
Used %                 : 41.5
```

<a id="dedup-compression"></a>

## 6.2 Dedup & Compression Savings

When deduplication and compression are enabled (common in vSAN ESA and optional in OSA all-flash), significant space savings are expected.

#### Command

```bash
esxcli vsan debug space show
```

#### PowerCLI Method

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$spaceReport = Get-VsanSpaceUsage -Cluster $cluster

[PSCustomObject]@{
    "Before Dedup & Compression (TB)" = [math]::Round($spaceReport.PhysicalUsedCapacityGB / 1024, 2)
    "After Dedup & Compression (TB)"  = [math]::Round($spaceReport.UsedCapacityGB / 1024, 2)
    "Dedup Ratio"                     = [math]::Round($spaceReport.DedupRatio, 2)
    "Compression Ratio"               = [math]::Round($spaceReport.CompressionRatio, 2)
    "Overall Savings Ratio"           = [math]::Round($spaceReport.DedupCompressionRatio, 2)
}
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | Savings ratio > 1.5x | Good efficiency |
| <span class="badge-warn">WARN</span> | Savings ratio 1.0-1.5x | Review workload data characteristics |
| <span class="badge-fail">FAIL</span> | Savings ratio < 1.0x | Dedup/compression overhead exceeds savings; consider disabling |

<a id="thin-provisioning"></a>

## 6.3 Thin Provisioning

vSAN uses thin provisioning by default for object storage. The logical provisioned space can far exceed physical capacity.

#### Check Provisioned vs. Used Space

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$vms = Get-VM -Location $cluster

$report = foreach ($vm in $vms) {
    $disks = Get-HardDisk -VM $vm
    foreach ($disk in $disks) {
        [PSCustomObject]@{
            VM             = $vm.Name
            Disk           = $disk.Name
            ProvisionedGB  = [math]::Round($disk.CapacityGB, 2)
            UsedGB         = [math]::Round(($disk.CapacityGB - $disk.FreeSpaceGB), 2) # Approximate
            ThinProvisioned = $disk.StorageFormat -eq "Thin"
        }
    }
}

$report | Format-Table -AutoSize
Write-Host "Total Provisioned: $([math]::Round(($report | Measure-Object -Property ProvisionedGB -Sum).Sum, 2)) GB"
Write-Host "Total Used:        $([math]::Round(($report | Measure-Object -Property UsedGB -Sum).Sum, 2)) GB"
```

<a id="slack-space"></a>

## 6.4 Slack Space Calculation

vSAN reserves slack space for resyncs, maintenance operations, and failure recovery. The formula depends on the cluster size and policy.

#### Slack Space Formula

```
Slack Space = Max(HostCapacity, 25% of RawCapacity)

Where:
  HostCapacity = Total raw capacity / Number of hosts
  (i.e., the capacity of the largest single host)
```

#### Example Calculation

```
Cluster: 4 hosts x 10 TB raw each = 40 TB total raw
HostCapacity = 40 TB / 4 = 10 TB
25% of Raw = 40 TB x 0.25 = 10 TB
Slack Space = Max(10 TB, 10 TB) = 10 TB

Usable Capacity = 40 TB - 10 TB = 30 TB
(Before policy overhead)

With FTT=1, RAID-1 mirroring:
  Effective Usable = 30 TB / 2 = 15 TB
```

<a id="capacity-thresholds"></a>

## 6.5 Capacity Thresholds

| Used % | Status | Description | Action |
|--------|--------|-------------|--------|
| 0-70% | <span class="badge-pass">PASS</span> | Healthy capacity headroom | Normal operations |
| 70-75% | <span class="badge-warn">WARN</span> | Approaching capacity limits | Plan expansion or cleanup |
| 75-80% | <span class="badge-warn">WARN</span> | vSAN generates a warning alarm | Active capacity management needed |
| 80-90% | <span class="badge-fail">FAIL</span> | vSAN throttles new writes | Immediate expansion or VM migration |
| 90-95% | <span class="badge-fail">FAIL</span> | Severe performance impact | Emergency capacity action |
| >95% | <span class="badge-fail">FAIL</span> | Risk of data inaccessibility | Emergency: free space immediately |

<div class="danger">
<strong>Critical Threshold - 80%:</strong> When vSAN capacity reaches 80%, the CLOM (Cluster Level Object Manager) stops performing automatic rebalancing and repairs. New VM deployments may fail. This is a hard operational limit that must never be sustained.
</div>

<div class="fix-box">
<strong>Remediation (High Capacity):</strong><br>
1. Identify largest consumers: <code>Get-VsanSpaceUsage -Cluster $cluster | Select -ExpandProperty SpaceDetail</code><br>
2. Remove orphaned snapshots and stale VM files<br>
3. Storage vMotion cold VMs to alternative datastores (NFS, VMFS)<br>
4. Enable or verify deduplication and compression<br>
5. Plan cluster expansion (add hosts or disks)<br>
6. Review and right-size VMDK allocations
</div>

<div class="page-break"></div>

<a id="resync-status"></a>

# 7. Resync Status

<a id="active-resyncs"></a>

## 7.1 Active Resyncs

Resyncs occur when vSAN needs to rebuild or move components. They can be triggered by host maintenance, disk failures, policy changes, or rebalancing.

#### Command

```bash
esxcli vsan debug resync summary
```

#### Expected Output (No Active Resyncs)

```
Resync Summary:
   Total Objects Resyncing: 0
   Total Bytes To Resync: 0 B
   Total Bytes Resynced: 0 B
   Total Recoveries: 0
   Total Rebalance: 0
   Total Policy Change: 0
   Total Evacuating: 0
```

#### Expected Output (Active Resyncs)

```
Resync Summary:
   Total Objects Resyncing: 42
   Total Bytes To Resync: 287.35 GB
   Total Bytes Resynced: 143.67 GB
   Total Recoveries: 38
   Total Rebalance: 4
   Total Policy Change: 0
   Total Evacuating: 0
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | 0 objects resyncing | Cluster fully converged |
| <span class="badge-warn">WARN</span> | < 100 objects, progress advancing | Monitor progress; expected after maintenance |
| <span class="badge-fail">FAIL</span> | > 100 objects or resync stalled | Investigate root cause; check for disk or network issues |

<a id="resync-eta"></a>

## 7.2 Resync ETA

#### Monitoring Resync Progress

```bash
# Real-time resync monitoring
watch -n 10 'esxcli vsan debug resync summary'
```

#### PowerCLI Resync Details

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$vsanHealthSystem = Get-VsanView -Id "VsanVcClusterHealthSystem-vsan-cluster-health-system"
$resyncStatus = $vsanHealthSystem.VsanQuerySyncingVsanObjects(
    $cluster.ExtensionData.MoRef
)

foreach ($obj in $resyncStatus) {
    [PSCustomObject]@{
        UUID           = $obj.Uuid
        BytesToSync    = [math]::Round($obj.BytesToSync / 1GB, 2)
        BytesSynced    = [math]::Round($obj.RecoveryETA, 0)
        Reason         = $obj.Reason
    }
} | Format-Table -AutoSize
```

#### RVC Resync Dashboard

```bash
# Provides a continuously updating view of resync progress
vsan.resync_dashboard /localhost/datacenter/computers/cluster
```

<a id="resync-performance-impact"></a>

## 7.3 Performance Impact

Active resyncs consume disk IO and network bandwidth. vSAN uses a throttling mechanism to limit impact on production workloads.

#### Check Resync Throttle Configuration

```bash
esxcli system settings advanced list -o /LSOM/lsomResyncThrottleEnabled
esxcli system settings advanced list -o /VSAN/ResyncThrottleAdaptive
```

#### Resync Traffic Limits

| Parameter | Default | Impact |
|-----------|---------|--------|
| `ResyncThrottleAdaptive` | 1 (enabled) | vSAN automatically reduces resync bandwidth when VM IO is detected |
| `ResyncBandwidthCap` | 0 (unlimited) | Maximum MB/s for resync traffic per host |
| `lsomResyncThrottleEnabled` | 1 | Enables disk-level resync throttling |

<div class="warn-box">
<strong>Performance Impact:</strong> During large-scale resyncs (e.g., after host failure), expect 10-30% reduction in VM IO performance. Avoid scheduling additional maintenance operations or large deployments until resyncs complete.
</div>

<div class="page-break"></div>

<a id="vsan-network-health"></a>

# 8. vSAN Network Health

<a id="vmkernel-adapters"></a>

## 8.1 vSAN VMkernel Adapters

Every host in the vSAN cluster must have a dedicated VMkernel adapter tagged for vSAN traffic.

#### Command

```bash
esxcli network ip interface list | grep -A5 "vsan"
```

#### Alternative: Full VMkernel Listing

```bash
esxcli network ip interface list
```

#### Expected Output

```
vmk1
   Name: vmk1
   MAC Address: 00:50:56:6a:xx:xx
   Enabled: true
   Portset: DvsPortset-0
   Portgroup: SDDC-DPortGroup-vSAN
   VDS Name: SDDC-Dswitch-Private
   MTU: 9000
   TSO MSS: 65535
   Port ID: 33554435
   Netstack Instance: defaultTcpipStack
   IPv4 Address: 172.16.10.101
   IPv4 Netmask: 255.255.255.0
   IPv4 Broadcast: 172.16.10.255
   IPv6 Enabled: false
   Tags: VSAN
```

#### Verify vSAN Tag on VMkernel

```bash
esxcli vsan network list
```

#### Expected Output

```
Interface
   VmkNic Name: vmk1
   IP Protocol: IP
   Interface UUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Agent Group Multicast Address: 224.2.3.4
   Agent Group IPv6 Multicast Address: ff19::2:3:4
   Agent Group Multicast Port: 23451
   Master Group Multicast Address: 224.1.2.3
   Master Group IPv6 Multicast Address: ff19::1:2:3
   Master Group Multicast Port: 12345
   Host Unicast Channel Bound Port: 12321
   Multicast Enabled: true
   Traffic Type: vsan
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | All hosts have vmk with `Tags: VSAN`, MTU 9000 | Healthy |
| <span class="badge-warn">WARN</span> | MTU mismatch across hosts | Standardize MTU to 9000 |
| <span class="badge-fail">FAIL</span> | Host missing vSAN-tagged vmk adapter | Add vSAN VMkernel adapter immediately |

<a id="multicast-unicast"></a>

## 8.2 Multicast & Unicast Check

vSAN can operate in multicast mode (legacy) or unicast mode (default in vSAN 7+/VCF 5+). VCF 9 clusters should use unicast.

#### Check Current Mode

```bash
esxcli vsan network list | grep "Multicast Enabled"
```

| Mode | VCF 9 Status | Notes |
|------|-------------|-------|
| Unicast (`Multicast Enabled: false`) | Recommended | Default for new VCF 9 clusters |
| Multicast (`Multicast Enabled: true`) | Legacy | Requires IGMP snooping on physical switches |

#### Verify Unicast Connectivity

```bash
# From each host, test connectivity to every other host on vSAN network
vmkping -I vmk1 172.16.10.102
vmkping -I vmk1 172.16.10.103
vmkping -I vmk1 172.16.10.104
```

<a id="jumbo-frames"></a>

## 8.3 Jumbo Frame Validation

Jumbo frames (MTU 9000) are required for optimal vSAN performance. End-to-end validation is critical.

#### Test Jumbo Frames Between Hosts

```bash
# From ESXi host, test jumbo frame path to each peer
# -s 8972 = 9000 - 20 (IP header) - 8 (ICMP header) = 8972
# -d = set DF (Don't Fragment) bit

vmkping -I vmk1 -s 8972 -d 172.16.10.102
vmkping -I vmk1 -s 8972 -d 172.16.10.103
vmkping -I vmk1 -s 8972 -d 172.16.10.104
```

#### Expected Output (Healthy)

```
PING 172.16.10.102 (172.16.10.102): 8972 data bytes
8980 bytes from 172.16.10.102: icmp_seq=0 ttl=64 time=0.254 ms
8980 bytes from 172.16.10.102: icmp_seq=1 ttl=64 time=0.198 ms
8980 bytes from 172.16.10.102: icmp_seq=2 ttl=64 time=0.211 ms

--- 172.16.10.102 ping statistics ---
3 packets transmitted, 3 packets received, 0% packet loss
round-trip min/avg/max = 0.198/0.221/0.254 ms
```

#### Expected Output (FAILURE)

```
PING 172.16.10.102 (172.16.10.102): 8972 data bytes
sendto() failed (Message too long)
--- 172.16.10.102 ping statistics ---
3 packets transmitted, 0 packets received, 100% packet loss
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | 0% packet loss on all hosts with 8972 byte payload | Jumbo frames working end-to-end |
| <span class="badge-warn">WARN</span> | Intermittent packet loss | Check physical switch MTU, NIC firmware |
| <span class="badge-fail">FAIL</span> | 100% loss or "Message too long" | MTU mismatch in path -- check vmk, vDS, physical switch |

<div class="fix-box">
<strong>Remediation (Jumbo Frame Failure):</strong><br>
1. Verify VMkernel MTU: <code>esxcli network ip interface list | grep MTU</code><br>
2. Verify vDS MTU: vCenter > Networking > vDS > Settings > MTU = 9000<br>
3. Verify physical switch port MTU: interface-level <code>mtu 9216</code> (allows for overhead)<br>
4. Verify physical NIC MTU: <code>esxcli network nic list</code><br>
5. Check for any intermediate firewalls or routers that may reduce MTU<br>
6. After fixing, retest: <code>vmkping -I vmk1 -s 8972 -d &lt;target_ip&gt;</code>
</div>

<a id="network-partition"></a>

## 8.4 Network Partition Detection

A vSAN network partition occurs when hosts lose connectivity to each other, causing the cluster to split into sub-clusters.

#### Check via Health Service

```bash
esxcli vsan health cluster list -t "vSAN Cluster Partition"
```

#### Check via Cluster Membership

```bash
# Run on EVERY host and compare Sub-Cluster Member UUIDs
esxcli vsan cluster get
```

#### Detecting Partition via CMMDS

```bash
# Check CMMDS master node
esxcli vsan cluster get | grep "Local Node State"
```

If multiple hosts report `MASTER`, a partition exists -- only one host should be MASTER.

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | Single MASTER, all hosts in same sub-cluster | No partition |
| <span class="badge-fail">FAIL</span> | Multiple MASTERs or mismatched sub-cluster membership | Active partition -- URGENT |

<div class="danger">
<strong>Network Partition Emergency:</strong> A vSAN network partition can cause data inaccessibility, VM failures, and split-brain conditions. This is a P1 severity event.
</div>

<div class="fix-box">
<strong>Remediation (Network Partition):</strong><br>
1. Identify which hosts can communicate with each other<br>
2. Check physical network: <code>esxcli network nic stats get -n vmnic0</code> for errors/drops<br>
3. Verify VLAN tagging consistency across all hosts<br>
4. Check physical switch logs for spanning tree topology changes or port flapping<br>
5. Test L2 connectivity: <code>vmkping -I vmk1 &lt;peer_vsan_ip&gt;</code> from each host<br>
6. If a single host is isolated, restart its networking: <code>esxcli network ip interface set -i vmk1 -e false && esxcli network ip interface set -i vmk1 -e true</code><br>
7. Monitor CLOMD log for partition events: <code>tail -f /var/log/clomd.log | grep -i partition</code>
</div>

<a id="witness-connectivity"></a>

## 8.5 Witness Host Connectivity (Stretched Cluster)

If a stretched cluster is deployed, the witness host must be reachable from both sites.

#### Test Witness Connectivity

```bash
# From preferred site host
vmkping -I vmk1 <witness_vsan_ip>

# From secondary site host
vmkping -I vmk1 <witness_vsan_ip>
```

#### Verify Witness in Cluster

```bash
esxcli vsan cluster get | grep -A2 "Witness"
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | Witness reachable from both sites, < 200ms RTT | Healthy |
| <span class="badge-warn">WARN</span> | Witness reachable but RTT > 100ms | Investigate WAN link quality |
| <span class="badge-fail">FAIL</span> | Witness unreachable from either site | Immediate investigation -- quorum at risk |

<div class="page-break"></div>

<a id="performance-health"></a>

# 9. Performance Health

<a id="iops-latency"></a>

## 9.1 IOPS & Latency

#### vSAN Performance Service (vCenter UI)

Navigate to: **Cluster > Monitor > vSAN > Performance > Virtual Machine Consumption**

#### CLI: Check Per-Host IO Statistics

```bash
# Real-time IOPS and latency from ESXi
vsish -e get /vmkModules/lsom/disks/<disk_uuid>/info
```

#### PowerCLI: Query vSAN Performance Data

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$vsanPerfSystem = Get-VsanView -Id "VsanPerformanceManager-vsan-performance-manager"

# Define time range (last 1 hour)
$endTime = Get-Date
$startTime = $endTime.AddHours(-1)

# Query cluster performance
$spec = New-Object VMware.Vsan.Views.VsanPerfQuerySpec
$spec.EntityRefId = "cluster-domclient:*"
$spec.StartTime = $startTime
$spec.EndTime = $endTime

$perfData = $vsanPerfSystem.VsanPerfQueryPerf(@($spec), $cluster.ExtensionData.MoRef)
```

#### Latency Thresholds

| Metric | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|--------|------|------|------|
| Read Latency (average) | < 1 ms | 1-5 ms | > 5 ms |
| Write Latency (average) | < 2 ms | 2-10 ms | > 10 ms |
| Read IOPS | Per baseline | > 20% below baseline | > 50% below baseline |
| Write IOPS | Per baseline | > 20% below baseline | > 50% below baseline |
| Read Cache Hit Ratio (OSA) | > 90% | 70-90% | < 70% |

<a id="congestion"></a>

## 9.2 Congestion

vSAN congestion values indicate back-pressure in the IO stack. A non-zero congestion value means vSAN is throttling IO.

#### Command

```bash
esxcli vsan debug controller list
```

#### Expected Output (Healthy)

```
Controller: naa.55cd2e414f5356c0
   State: HEALTHY
   Congestion Value: 0
   Congestion Type: None
   Outstanding IO: 0
```

#### Alternative: VSISH Congestion Query

```bash
# Get per-disk congestion
vsish -e get /vmkModules/lsom/disks/<disk_uuid>/info | grep -i congestion
```

| Congestion Value | Status | Description |
|-----------------|--------|-------------|
| 0 | <span class="badge-pass">PASS</span> | No congestion |
| 1-20 | <span class="badge-warn">WARN</span> | Mild congestion -- transient during bursts |
| 21-40 | <span class="badge-warn">WARN</span> | Moderate congestion -- sustained IO pressure |
| 41-60 | <span class="badge-fail">FAIL</span> | High congestion -- significant IO throttling |
| 61-100 | <span class="badge-fail">FAIL</span> | Severe congestion -- critical performance impact |

<div class="fix-box">
<strong>Remediation (High Congestion):</strong><br>
1. Identify top IO consumers: vCenter > Cluster > Monitor > vSAN > Performance > VM Consumption<br>
2. Check for active resyncs: <code>esxcli vsan debug resync summary</code><br>
3. Verify no runaway processes: <code>esxtop</code> (press <code>u</code> for disk view)<br>
4. Check disk health -- degraded disks cause elevated congestion<br>
5. Consider distributing workloads across more hosts<br>
6. If persistent, add capacity disks or hosts to reduce per-disk load
</div>

<a id="outstanding-io"></a>

## 9.3 Outstanding IO

Outstanding IO counts indicate the number of IO operations queued but not yet completed.

#### Command

```bash
esxcli vsan debug controller list | grep "Outstanding IO"
```

#### VSISH Deep Inspection

```bash
# Per-device outstanding IO
vsish -e get /vmkModules/lsom/disks/<disk_uuid>/info | grep outstanding
```

| Outstanding IO | Status | Description |
|---------------|--------|-------------|
| 0-16 | <span class="badge-pass">PASS</span> | Normal queue depth |
| 17-32 | <span class="badge-pass">PASS</span> | Moderate load, acceptable |
| 33-64 | <span class="badge-warn">WARN</span> | Elevated queue depth |
| > 64 | <span class="badge-fail">FAIL</span> | Queue saturation -- investigate |

<a id="vscsistats"></a>

## 9.4 vscsiStats

`vscsiStats` provides detailed IO profiling for individual VMs and virtual disks.

#### Enable vscsiStats Collection

```bash
# List all virtual SCSI handles
vscsiStats -l

# Start collection for a specific handle
vscsiStats -s -w <world_id> -i <handle_id>

# Wait for collection period (e.g., 60 seconds)
sleep 60

# Retrieve statistics
vscsiStats -p all -w <world_id> -i <handle_id>

# Stop collection
vscsiStats -x -w <world_id> -i <handle_id>
```

#### Output Metrics

| Metric | Description |
|--------|-------------|
| IO Size Histogram | Distribution of IO sizes (4K, 8K, 16K, etc.) |
| Seek Distance | Sequential vs. random IO pattern |
| Outstanding IO | Per-VMDK queue depth |
| Latency Histogram | Distribution of latency values |
| IO Type | Read/write ratio |

<div class="info-box">
<strong>Best Practice:</strong> Use <code>vscsiStats</code> sparingly in production. It adds minor overhead during collection. Collect for 60-120 seconds to get a representative sample, then stop immediately.
</div>

<a id="performance-service"></a>

## 9.5 Performance Service

The vSAN Performance Service must be enabled for historical performance data.

#### Verify Performance Service Status

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$vsanConfig = Get-VsanClusterConfiguration -Cluster $cluster
$vsanConfig.PerformanceServiceEnabled
```

#### Enable Performance Service

```powershell
Set-VsanClusterConfiguration -Cluster $cluster -PerformanceServiceEnabled $true
```

#### Performance Service Health Check

```bash
esxcli vsan health cluster list -t "Performance Service"
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | Performance service enabled and collecting data | Healthy |
| <span class="badge-warn">WARN</span> | Service enabled but stats database > 80% full | Archive or increase stats DB size |
| <span class="badge-fail">FAIL</span> | Performance service disabled or not functioning | Enable via PowerCLI or vCenter UI |

<div class="page-break"></div>

<a id="object-health-compliance"></a>

# 10. Object Health & Compliance

<a id="object-count"></a>

## 10.1 Object Count

#### Command

```bash
esxcli vsan debug object health summary get
```

#### Expected Output (Healthy)

```
Object Health Summary:
   Total Objects: 2847
   Healthy: 2847
   Objects with Reduced Redundancy: 0
   Inaccessible Objects: 0
   Non-Compliant Objects: 0
   Quorum Not Satisfied: 0
```

#### PowerCLI Object Count

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$vsanHealth = Get-VsanView -Id "VsanVcClusterHealthSystem-vsan-cluster-health-system"
$objHealth = $vsanHealth.VsanQueryVcClusterHealthSummary(
    $cluster.ExtensionData.MoRef, $null, $null, $true, $null, $null, "objectHealth"
)

$objHealth.ObjectHealth.ObjectHealthDetail | ForEach-Object {
    [PSCustomObject]@{
        Category      = $_.NumObjects
        ObjectCount   = $_.ObjHealthState
    }
}
```

<a id="compliance-state"></a>

## 10.2 Compliance State

vSAN object compliance verifies that every object meets its assigned storage policy (FTT, stripe width, etc.).

#### Check Compliance via PowerCLI

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$vms = Get-VM -Location $cluster

foreach ($vm in $vms) {
    $spPolicy = Get-SpbmEntityConfiguration -VM $vm
    foreach ($policy in $spPolicy) {
        if ($policy.ComplianceStatus -ne "compliant") {
            [PSCustomObject]@{
                VM         = $vm.Name
                Entity     = $policy.Entity
                Policy     = $policy.StoragePolicy.Name
                Status     = $policy.ComplianceStatus
            }
        }
    }
}
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | All objects compliant | No action |
| <span class="badge-warn">WARN</span> | Objects non-compliant but actively rebuilding | Monitor resync progress |
| <span class="badge-fail">FAIL</span> | Objects persistently non-compliant | Investigate capacity or host availability |

<a id="inaccessible-objects"></a>

## 10.3 Inaccessible Objects

Inaccessible objects have lost quorum -- they cannot be read or written. This is the most critical vSAN health state.

#### Command

```bash
esxcli vsan debug object health summary get | grep "Inaccessible"
```

#### List Inaccessible Objects

```bash
esxcli vsan debug object list --type=inaccessible
```

#### Trace Object to VM

```bash
# Get the object UUID from the inaccessible list, then:
esxcli vsan debug object list -u <object_uuid>
```

<div class="danger">
<strong>CRITICAL -- Inaccessible Objects:</strong> Any inaccessible object represents potential data loss. This is a P1 severity event requiring immediate action. Do NOT perform any maintenance operations until all objects are accessible.
</div>

<div class="fix-box">
<strong>Remediation (Inaccessible Objects):</strong><br>
1. Identify which hosts own the components: <code>esxcli vsan debug object list -u &lt;uuid&gt;</code><br>
2. Check if hosts are offline or partitioned<br>
3. Verify vSAN network connectivity between all hosts<br>
4. If a host is down, restore it immediately<br>
5. If a disk has failed, initiate replacement<br>
6. Check CLOMD logs: <code>grep -i "inaccessible" /var/log/clomd.log</code><br>
7. If persistent, contact VMware Support with object UUIDs and CLOMD logs
</div>

<a id="reduced-redundancy"></a>

## 10.4 Reduced Redundancy Objects

Objects with reduced redundancy are accessible but have fewer copies than specified by their policy.

#### Command

```bash
esxcli vsan debug object health summary get | grep "Reduced Redundancy"
```

#### Detailed Listing

```bash
esxcli vsan debug object list --type=reducedRedundancy
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | 0 objects with reduced redundancy | Full policy compliance |
| <span class="badge-warn">WARN</span> | Objects in reduced redundancy during resync | Expected after host/disk event; monitor resync |
| <span class="badge-fail">FAIL</span> | Persistent reduced redundancy (no active resync) | Investigate CLOM; check capacity/host availability |

<div class="fix-box">
<strong>Remediation (Persistent Reduced Redundancy):</strong><br>
1. Verify resyncs are not stalled: <code>esxcli vsan debug resync summary</code><br>
2. Check available capacity -- CLOM cannot rebuild if < 20% free<br>
3. Check for component limit violations: <code>esxcli vsan health cluster list -t "Host Component Limit"</code><br>
4. Force a repair on the object: from RVC, <code>vsan.fix_renamed_objects /path/to/cluster</code><br>
5. Restart CLOMD if the service is stuck: <code>/etc/init.d/clomd restart</code>
</div>

<div class="page-break"></div>

<a id="stretched-cluster-health"></a>

# 11. Stretched Cluster Health

<div class="info-box">
<strong>Applicability:</strong> This section applies only to environments with vSAN stretched clusters. If your VCF 9 deployment uses standard (non-stretched) clusters, skip to Section 12.
</div>

<a id="preferred-secondary-site"></a>

## 11.1 Preferred & Secondary Site

In a vSAN stretched cluster, hosts are divided into two fault domains (sites) plus a witness host.

#### Check Site Configuration

```bash
esxcli vsan cluster get
```

Look for:

```
Preferred Fault Domain: site-a
Secondary Fault Domain: site-b
```

#### PowerCLI Site Verification

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$vsanConfig = Get-VsanClusterConfiguration -Cluster $cluster

[PSCustomObject]@{
    StretchedCluster  = $vsanConfig.StretchedClusterEnabled
    PreferredSite     = $vsanConfig.PreferredFaultDomain.Name
    SecondarySite     = ($vsanConfig.FaultDomains | Where-Object { $_.Name -ne $vsanConfig.PreferredFaultDomain.Name }).Name
    WitnessHost       = $vsanConfig.WitnessHost.Name
}
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | Both sites have equal host counts, preferred site set correctly | Healthy |
| <span class="badge-warn">WARN</span> | Uneven host distribution between sites | Rebalance hosts if possible |
| <span class="badge-fail">FAIL</span> | One site has no hosts or stretched cluster misconfigured | Reconfigure stretched cluster |

<a id="witness-host"></a>

## 11.2 Witness Host

The witness host provides the tiebreaker vote in a stretched cluster. It must be in a third fault domain.

#### Verify Witness Host

```bash
# From any cluster host
esxcli vsan cluster get | grep -i witness
```

#### Witness Host Health Checks

```bash
# SSH to witness host
ssh root@witness-host.vcf.local

# Verify vSAN is running
esxcli vsan cluster get

# Check witness disk status
esxcli vsan storage list

# Verify network connectivity to both sites
vmkping -I vmk0 <site-a-host-vsan-ip>
vmkping -I vmk0 <site-b-host-vsan-ip>
```

#### Witness Appliance Resources

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| vCPUs | 2 | 2 |
| Memory | 16 GB (< 750 components) | 32 GB (> 750 components) |
| Witness disk cache | 5 GB SSD | 10 GB SSD |
| Witness disk capacity | 15 GB | 30 GB |

<a id="site-affinity-rules"></a>

## 11.3 Site Affinity Rules

Site affinity rules ensure that specific VMs prefer to run at a particular site during normal operations.

#### Check Site Affinity via PowerCLI

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$rules = Get-DrsRule -Cluster $cluster | Where-Object { $_.Type -eq "VMAffinity" }
$rules | Format-Table Name, Type, Enabled, VMIds -AutoSize
```

#### vSAN Storage Policy Site Affinity

```powershell
# Check vSAN storage policies with site affinity
Get-SpbmStoragePolicy | Where-Object {
    $_.AnyOfRuleSets.AnyOfRules.Capability.Name -match "locality"
} | ForEach-Object {
    [PSCustomObject]@{
        PolicyName  = $_.Name
        Locality    = ($_.AnyOfRuleSets.AnyOfRules | Where-Object {
            $_.Capability.Name -match "locality"
        }).Value
    }
}
```

<a id="inter-site-latency"></a>

## 11.4 Inter-Site Latency

#### Test Inter-Site Latency

```bash
# From a host at Site A to a host at Site B
vmkping -I vmk1 -c 100 <site-b-host-vsan-ip>
```

#### Latency Requirements

| Link | Maximum RTT | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|------|------------|------|------|------|
| Site A to Site B | 5 ms (data) | < 5 ms | 5-100 ms | > 100 ms |
| Either Site to Witness | 200 ms | < 100 ms | 100-200 ms | > 200 ms |
| Bandwidth (data sites) | 10 Gbps | >= 10 Gbps | 1-10 Gbps | < 1 Gbps |

<div class="warn-box">
<strong>Latency Note:</strong> vSAN stretched clusters in VCF 9 support up to 5ms RTT between data sites for write operations (synchronous replication). The witness host can tolerate up to 200ms RTT. Exceeding these limits will cause write performance degradation or cluster instability.
</div>

<div class="page-break"></div>

<a id="fault-domains"></a>

# 12. Fault Domains

<a id="fd-configuration"></a>

## 12.1 Fault Domain Configuration

Fault domains define failure boundaries. vSAN places components across fault domains to ensure that a single domain failure does not cause data loss.

#### View Fault Domains

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$faultDomains = Get-VsanFaultDomain -Cluster $cluster

foreach ($fd in $faultDomains) {
    [PSCustomObject]@{
        Name       = $fd.Name
        HostCount  = ($fd.VMHost | Measure-Object).Count
        Hosts      = ($fd.VMHost.Name -join ", ")
    }
} | Format-Table -AutoSize
```

#### esxcli Fault Domain Check

```bash
esxcli vsan cluster get | grep "Fault Domain"
```

<a id="fd-host-distribution"></a>

## 12.2 Host Distribution

For optimal fault tolerance, hosts should be evenly distributed across fault domains.

| Configuration | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|--------------|------|------|------|
| Fault Domain Count | >= 3 FDs | 2 FDs | 1 FD or none configured |
| Hosts per FD | Equal distribution | +/- 1 host variance | Severe imbalance |
| FTT=1 compliance | >= 3 FDs | 2 FDs (works but no FD-level protection) | 1 FD |
| FTT=2 compliance | >= 5 FDs | 3-4 FDs | < 3 FDs |

#### Example: Optimal 4-Host, 4-FD Configuration

```
Fault Domain: rack-01 -> esx-01.vcf.local
Fault Domain: rack-02 -> esx-02.vcf.local
Fault Domain: rack-03 -> esx-03.vcf.local
Fault Domain: rack-04 -> esx-04.vcf.local
```

<a id="fd-policy-compliance"></a>

## 12.3 Policy Compliance with Fault Domains

When fault domains are configured, vSAN places mirrors/parity components in different fault domains. The policy must be compatible with the number of fault domains.

#### Validate Policy vs. Fault Domain Count

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$fds = Get-VsanFaultDomain -Cluster $cluster
$fdCount = ($fds | Measure-Object).Count

$policies = Get-SpbmStoragePolicy | Where-Object { $_.Name -like "*vSAN*" }
foreach ($pol in $policies) {
    $ftt = ($pol.AnyOfRuleSets.AnyOfRules | Where-Object {
        $_.Capability.Name -eq "VSAN.hostFailuresToTolerate"
    }).Value

    $requiredFDs = (2 * $ftt) + 1  # For RAID-1

    [PSCustomObject]@{
        Policy        = $pol.Name
        FTT           = $ftt
        RequiredFDs   = $requiredFDs
        AvailableFDs  = $fdCount
        Compliant     = $fdCount -ge $requiredFDs
    }
} | Format-Table -AutoSize
```

<div class="fix-box">
<strong>Remediation (Insufficient Fault Domains):</strong><br>
1. If the cluster has fewer fault domains than required, either:<br>
   a. Add more hosts in new fault domains<br>
   b. Reduce the FTT level in the storage policy<br>
2. To create a new fault domain: vCenter > Cluster > Configure > vSAN > Fault Domains > Add<br>
3. To move a host to a fault domain via PowerCLI:<br>
<code>New-VsanFaultDomain -Name "rack-05" -VMHost (Get-VMHost "esx-05.vcf.local")</code>
</div>

<div class="page-break"></div>

<a id="vsan-health-service-detail"></a>

# 13. vSAN Health Service Detail

<a id="health-service-status"></a>

## 13.1 Health Service Status

#### Verify Health Service is Running

```bash
esxcli vsan health cluster list -t "vSAN Health Service Up-To-Date"
```

#### Expected Output

```
Health Test: vSAN Health Service Up-To-Date
   Status: green
   Description: vSAN Health Service is up-to-date.
   Last Run: 2026-03-26T14:00:00Z
```

#### Check Health Service Database

```bash
# On VCSA, check health service status
vmon-cli --status vsanhealth
```

#### Force Health Check Refresh

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$healthSystem = Get-VsanView -Id "VsanVcClusterHealthSystem-vsan-cluster-health-system"
$healthSystem.VsanQueryVcClusterHealthSummary(
    $cluster.ExtensionData.MoRef,
    $null, $null, $true, $null, $null, "defaultView"
)
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | Service running, last test < 1 hour ago | Healthy |
| <span class="badge-warn">WARN</span> | Service running but last test > 24 hours ago | Force a refresh |
| <span class="badge-fail">FAIL</span> | Service not running | Restart: `vmon-cli --restart vsanhealth` on VCSA |

<a id="test-categories"></a>

## 13.2 Test Categories

The vSAN Health Service organizes tests into the following categories:

| Category | Tests Included | Frequency |
|----------|---------------|-----------|
| **Cluster** | Partition, CLOMD liveness, disk balance, member health | Every 60 min |
| **Network** | VMkernel config, connectivity, MTU, multicast | Every 60 min |
| **Physical Disk** | Disk health, metadata, congestion, capacity | Every 60 min |
| **Data** | Object health, VM health, compliance | Every 60 min |
| **Limits** | Component limits, host failure simulation | Every 60 min |
| **HCL** | Controller, driver, firmware, HCL DB age | Every 24 hours |
| **Performance** | Performance service status, stats integrity | Every 60 min |
| **Stretched Cluster** | Witness, site configuration, inter-site latency | Every 60 min |
| **Encryption** | KMS connectivity, key status, rekey status | Every 60 min |

<a id="silenced-alarms"></a>

## 13.3 Silenced Alarms

Silenced alarms are health tests that have been muted by an administrator. Excessive silencing can mask real problems.

#### Check Silenced Alarms

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$healthSystem = Get-VsanView -Id "VsanVcClusterHealthSystem-vsan-cluster-health-system"
$silenced = $healthSystem.VsanHealthGetVsanClusterSilentChecks($cluster.ExtensionData.MoRef)

Write-Host "Silenced checks count: $($silenced.Count)"
$silenced | ForEach-Object { Write-Host "  - $_" }
```

#### Unsilence All Alarms

```powershell
$healthSystem.VsanHealthSetVsanClusterSilentChecks(
    $cluster.ExtensionData.MoRef,
    $null  # Pass null to clear all silenced checks
)
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | 0 silenced alarms | Full visibility into health |
| <span class="badge-warn">WARN</span> | 1-3 silenced alarms | Review each; unsilence if no longer needed |
| <span class="badge-fail">FAIL</span> | > 3 silenced alarms | Audit all silenced checks; likely masking real issues |

<div class="page-break"></div>

<a id="hcl-compliance"></a>

# 14. HCL Compliance

<a id="controller-driver-firmware"></a>

## 14.1 Controller, Driver & Firmware

HCL (Hardware Compatibility List) compliance ensures that storage controllers, drivers, and firmware are certified for vSAN.

#### Check HCL Status via Health Service

```bash
esxcli vsan health cluster list -t "vSAN HCL Health"
```

#### Detailed HCL Query

```bash
# Controller model
esxcli storage core adapter list

# Driver version
esxcli storage core adapter stats get -a vmhba0

# Firmware version
esxcli storage core adapter list | grep -i firmware
```

#### PowerCLI HCL Check

```powershell
$cluster = Get-Cluster "SDDC-Cluster1"
$healthSystem = Get-VsanView -Id "VsanVcClusterHealthSystem-vsan-cluster-health-system"
$hclResult = $healthSystem.VsanQueryVcClusterHealthSummary(
    $cluster.ExtensionData.MoRef, $null, $null, $true, $null, $null, "hclInfo"
)

$hclResult.HclInfo | ForEach-Object {
    [PSCustomObject]@{
        Host       = $_.Hostname
        Controller = $_.ControllerName
        Driver     = $_.DriverVersion
        Firmware   = $_.FirmwareVersion
        HCLStatus  = $_.HclStatus
    }
} | Format-Table -AutoSize
```

| Result | Condition | Action |
|--------|-----------|--------|
| <span class="badge-pass">PASS</span> | All controllers/drivers/firmware on HCL | Fully certified |
| <span class="badge-warn">WARN</span> | HCL database outdated (> 90 days) | Update HCL DB |
| <span class="badge-fail">FAIL</span> | Controller, driver, or firmware NOT on HCL | Update driver/firmware to certified version |

<div class="danger">
<strong>Non-HCL Hardware:</strong> Running vSAN on non-HCL certified hardware voids VMware support coverage. Disk failures, data loss, and performance issues on non-HCL configurations will not receive VMware engineering assistance. Always maintain HCL compliance.
</div>

<a id="hcl-database-update"></a>

## 14.2 HCL Database Update

The HCL database is bundled with vCenter and should be updated regularly.

#### Check HCL DB Age

```bash
esxcli vsan health cluster list -t "vSAN HCL DB Up-To-Date"
```

#### Update HCL DB Online

```powershell
$healthSystem = Get-VsanView -Id "VsanVcClusterHealthSystem-vsan-cluster-health-system"
$healthSystem.VsanVcUploadHclDb($null)  # Downloads latest from VMware
```

#### Update HCL DB Offline (Air-Gapped Environments)

1. Download the latest HCL JSON from [VMware Partner Connect](https://partnerweb.vmware.com/service/vsan/all.json)
2. Upload via vCenter UI: **Cluster > Monitor > vSAN > Health > HCL Database > Upload from file**

#### Or via PowerCLI:

```powershell
$jsonContent = Get-Content -Path "C:\path\to\all.json" -Raw
$healthSystem.VsanVcUploadHclDb($jsonContent)
```

<div class="fix-box">
<strong>Remediation (Outdated HCL):</strong><br>
1. For internet-connected vCenter: update is automatic; force via PowerCLI if needed<br>
2. For air-gapped environments: download JSON from VMware, upload via UI or PowerCLI<br>
3. Schedule HCL DB updates quarterly at minimum<br>
4. After updating, re-run health checks to verify compliance
</div>

<div class="page-break"></div>

<a id="port-reference-table"></a>

# 15. Port Reference Table

The following ports must be open for vSAN communication between all participating hosts and vCenter.

| Port | Protocol | Direction | Service | Description |
|------|----------|-----------|---------|-------------|
| **2233** | TCP/UDP | Host <-> Host | vSAN Transport | Primary vSAN data transport (IO traffic) |
| **12321** | UDP | Host <-> Host | vSAN Clustering (Unicast) | Unicast agent-to-agent communication |
| **12345** | UDP | Host <-> Host | vSAN Clustering (Multicast) | Multicast master group (legacy) |
| **23451** | UDP | Host <-> Host | vSAN Clustering (Multicast) | Multicast agent group (legacy) |
| **8080** | TCP | Host -> vCenter | vSAN Health | Health check data upload |
| **6500** | TCP | Host -> vCenter | vSAN VASA | VASA provider for storage policies |
| **8006** | TCP | vCenter -> Host | vSAN VASA | VASA provider callback |
| **443** | TCP | Host <-> vCenter | HTTPS | vSphere API, management |
| **902** | TCP/UDP | Host <-> vCenter | NFC/Heartbeat | Network file copy, host heartbeat |
| **8010** | TCP | Host -> vCenter | vSAN Performance | Performance data upload |
| **2233** | TCP | Host <-> Witness | vSAN Transport | Witness traffic (stretched cluster) |
| **12321** | UDP | Host <-> Witness | vSAN Clustering | Witness cluster communication |
| **514** | UDP | Host -> Syslog | Syslog | vSAN log forwarding |
| **8100** | TCP | Host <-> Host | vSAN RDMA | RDMA transport (ESA with RDMA NICs) |
| **8200** | TCP | Host <-> Host | vSAN RDMA | RDMA transport secondary |

#### Firewall Validation Script

```bash
# Verify vSAN firewall rules on ESXi host
esxcli network firewall ruleset list | grep -i vsan

# Check if vSAN ports are open
esxcli network firewall ruleset rule list -r vsanvp
esxcli network firewall ruleset rule list -r vsanEncryption
esxcli network firewall ruleset rule list -r vsanhealth
```

#### Port Connectivity Test

```bash
# From each ESXi host, test TCP 2233 to peers
nc -z -w3 172.16.10.102 2233 && echo "OK" || echo "FAIL"
nc -z -w3 172.16.10.103 2233 && echo "OK" || echo "FAIL"
nc -z -w3 172.16.10.104 2233 && echo "OK" || echo "FAIL"
```

<div class="info-box">
<strong>VCF 9 Note:</strong> In VCF 9, vSAN ESA may use RDMA transport on ports 8100/8200 when supported NICs are present. Ensure these ports are open if RDMA is enabled in your environment.
</div>

<div class="page-break"></div>

<a id="common-issues-remediation"></a>

# 16. Common Issues & Remediation

<a id="disk-failures"></a>

## 16.1 Disk Failures

#### Symptoms

- Health service shows red for "vSAN Disk Health"
- `esxcli vsan storage list` shows `Health Status: Failed` or disk is missing
- SMART errors in `/var/log/vmkernel.log`
- Components become absent or degraded

#### Diagnostic Commands

```bash
# Check disk status
esxcli vsan storage list | grep -E "Display Name|Health Status"

# Check SMART data
esxcli vsan debug disk smart get -d naa.<disk_id>

# Check kernel log for disk errors
grep -i "disk error\|I/O error\|medium error" /var/log/vmkernel.log | tail -20

# Check vSAN trace for disk events
grep -i "disk" /var/log/vsantraced.log | tail -20
```

<div class="fix-box">
<strong>Remediation (Disk Failure - OSA):</strong><br>
<strong>Cache Disk Failure (Entire Disk Group Lost):</strong><br>
1. Identify the failed disk and its disk group UUID<br>
2. All capacity disks in the group are now offline<br>
3. Replace the cache disk physically<br>
4. Recreate the disk group: <code>esxcli vsan storage add -s naa.new_cache -d naa.cap1 -d naa.cap2</code><br>
5. vSAN will automatically rebuild components from surviving copies<br>
<br>
<strong>Capacity Disk Failure:</strong><br>
1. Remove the failed disk from the disk group: <code>esxcli vsan storage remove -d naa.failed_disk</code><br>
2. Physically replace the disk<br>
3. Add the new disk: <code>esxcli vsan storage add -d naa.new_disk -s naa.cache_disk</code><br>
4. Monitor resync: <code>esxcli vsan debug resync summary</code>
</div>

<div class="fix-box">
<strong>Remediation (Disk Failure - ESA):</strong><br>
1. In ESA, individual NVMe disk failure does not cause disk group loss<br>
2. Remove the failed disk: <code>esxcli vsan storage remove -d naa.failed_nvme</code><br>
3. Physically replace the disk<br>
4. Add the new disk to the storage pool: <code>esxcli vsan storage add -d naa.new_nvme</code><br>
5. Monitor resync: <code>esxcli vsan debug resync summary</code>
</div>

<a id="network-partition-issues"></a>

## 16.2 Network Partition

#### Symptoms

- Health service shows red for "vSAN Cluster Partition"
- Multiple hosts claim MASTER role
- VMs on isolated hosts may become unresponsive
- `esxcli vsan cluster get` shows different Member Counts on different hosts

#### Diagnostic Commands

```bash
# Check cluster membership on each host
esxcli vsan cluster get

# Check network connectivity
vmkping -I vmk1 <peer_vsan_ip>

# Check physical NIC status
esxcli network nic stats get -n vmnic2

# Check for CRC errors, drops, overruns
esxcli network nic stats get -n vmnic2 | grep -i "error\|drop\|overrun"

# Check switch port channel status
esxcli network vswitch dvs vmware lacp status get
```

<div class="fix-box">
<strong>Remediation (Network Partition):</strong><br>
1. Identify the partition boundary -- which hosts can talk to which<br>
2. Check physical connectivity: cables, switch ports, SFP modules<br>
3. Verify VLAN tags: <code>esxcli network vswitch dvs vmware list</code><br>
4. Check for spanning tree issues on physical switches<br>
5. If LACP is in use, verify LACP negotiation: <code>esxcli network vswitch dvs vmware lacp status get</code><br>
6. Test connectivity: <code>vmkping -I vmk1 -s 8972 -d &lt;peer&gt;</code><br>
7. Restart vSAN networking on the isolated host (last resort):<br>
   <code>esxcli vsan network remove -i vmk1</code><br>
   <code>esxcli vsan network ip add -i vmk1</code><br>
8. If spanning tree is blocking, enable PortFast on access ports
</div>

<a id="resync-storms"></a>

## 16.3 Resync Storms

#### Symptoms

- Hundreds or thousands of components resyncing simultaneously
- Severe performance degradation during resync
- High network utilization on vSAN VMkernel interfaces
- VM IO latency spikes

#### Diagnostic Commands

```bash
# Check resync volume
esxcli vsan debug resync summary

# Check network utilization
esxtop  # Press 'n' for network view, look at vmk1 throughput

# Check throttle settings
esxcli system settings advanced list -o /VSAN/ResyncThrottleAdaptive
```

<div class="fix-box">
<strong>Remediation (Resync Storm):</strong><br>
1. Verify adaptive throttle is enabled:<br>
   <code>esxcli system settings advanced set -o /VSAN/ResyncThrottleAdaptive -i 1</code><br>
2. If needed, manually cap resync bandwidth (MB/s per host):<br>
   <code>esxcli system settings advanced set -o /VSAN/ResyncBandwidthCap -i 500</code><br>
3. Avoid performing multiple maintenance operations simultaneously<br>
4. If a single disk failure triggered the storm, it will self-resolve -- monitor progress<br>
5. After the storm subsides, remove any manual bandwidth cap:<br>
   <code>esxcli system settings advanced set -o /VSAN/ResyncBandwidthCap -i 0</code>
</div>

<a id="performance-degradation"></a>

## 16.4 Performance Degradation

#### Symptoms

- High latency (> 5ms read, > 10ms write)
- Non-zero congestion values
- Elevated outstanding IO
- User complaints about slow VMs

#### Diagnostic Commands

```bash
# Check congestion
esxcli vsan debug controller list

# Check disk latency
esxcli vsan debug disk latency get

# Check for noisy neighbor VMs
esxtop  # Press 'v' for VM disk view, sort by DAVG (device average latency)

# Check if resyncs are causing pressure
esxcli vsan debug resync summary

# Check cache tier utilization (OSA only)
vsish -e get /vmkModules/lsom/disks/<cache_uuid>/info | grep -i cache
```

<div class="fix-box">
<strong>Remediation (Performance Degradation):</strong><br>
1. Identify the bottleneck: disk, network, or compute<br>
2. <strong>Disk bottleneck:</strong> Check SMART, replace aging disks, add capacity<br>
3. <strong>Network bottleneck:</strong> Verify jumbo frames, check for errors/drops, upgrade to 25GbE<br>
4. <strong>Compute bottleneck:</strong> Check CPU ready time on hosts, redistribute VMs with DRS<br>
5. <strong>Noisy neighbor:</strong> Identify high-IO VMs with esxtop, apply IO shares/limits via SIOC<br>
6. <strong>Cache saturation (OSA):</strong> Increase cache tier size or migrate to ESA<br>
7. Review storage policies -- RAID-5/6 has lower write performance than RAID-1<br>
8. Enable vSAN performance service to establish baselines for trending
</div>

<a id="clom-errors"></a>

## 16.5 CLOM Errors

CLOM (Cluster Level Object Manager) is the vSAN component responsible for object placement and repair. CLOM errors indicate placement failures.

#### Symptoms

- Objects stuck in non-compliant state
- New VM provisioning fails with "insufficient resources"
- CLOM log shows placement errors

#### Diagnostic Commands

```bash
# Check CLOM log for errors
grep -i "error\|fail\|cannot place" /var/log/clomd.log | tail -30

# Check component limits
esxcli vsan health cluster list -t "Host Component Limit"

# Check CLOM status
/etc/init.d/clomd status

# List objects with placement issues
esxcli vsan debug object list --type=nonCompliant
```

#### Common CLOM Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `Not enough fault domains` | FTT > available FDs | Add hosts/FDs or reduce FTT |
| `Not enough disk space` | Capacity > 80% | Free space or add capacity |
| `Component limit reached` | > 9000 components/host | Reduce FTT, consolidate VMs, or add hosts |
| `Cannot place` | Combination of above | Analyze specific constraint from log |
| `Disk group offline` | Cache disk failure (OSA) | Replace cache disk, recreate DG |

<div class="fix-box">
<strong>Remediation (CLOM Errors):</strong><br>
1. Restart CLOM if hung: <code>/etc/init.d/clomd restart</code><br>
2. Verify sufficient resources: capacity > 20% free, components < 9000/host<br>
3. Check fault domain count meets policy requirements<br>
4. If component limit is reached, reduce FTT on low-priority VMs<br>
5. Review and consolidate storage policies to reduce component count<br>
6. After resolving constraints, CLOM will automatically retry placement
</div>

<div class="page-break"></div>

<a id="cli-quick-reference-card"></a>

# 17. CLI Quick Reference Card

### Cluster Operations

```bash
# Get cluster status
esxcli vsan cluster get

# Join a vSAN cluster
esxcli vsan cluster join -c <cluster-uuid>

# Leave a vSAN cluster
esxcli vsan cluster leave

# Restore cluster from backup
esxcli vsan cluster restore -c <cluster-uuid>
```

### Health Commands

```bash
# List all health checks
esxcli vsan health cluster list

# Run a specific health test
esxcli vsan health cluster list -t "<test name>"

# Get health summary
esxcli vsan health cluster get
```

### Storage Commands

```bash
# List all vSAN disks
esxcli vsan storage list

# Add a disk to vSAN (OSA - with cache disk)
esxcli vsan storage add -d naa.<capacity_disk> -s naa.<cache_disk>

# Add a disk to vSAN (ESA)
esxcli vsan storage add -d naa.<nvme_disk>

# Remove a disk from vSAN
esxcli vsan storage remove -d naa.<disk_id>

# Auto-claim disks
esxcli vsan storage automode set -e true
```

### Network Commands

```bash
# List vSAN network interfaces
esxcli vsan network list

# Add a VMkernel interface to vSAN
esxcli vsan network ip add -i vmk1

# Remove a VMkernel interface from vSAN
esxcli vsan network remove -i vmk1

# Test connectivity with jumbo frames
vmkping -I vmk1 -s 8972 -d <target_ip>

# Test standard connectivity
vmkping -I vmk1 <target_ip>
```

### Debug Commands

```bash
# Resync summary
esxcli vsan debug resync summary

# Object health summary
esxcli vsan debug object health summary get

# List objects by type
esxcli vsan debug object list --type=inaccessible
esxcli vsan debug object list --type=reducedRedundancy
esxcli vsan debug object list --type=nonCompliant

# Disk SMART data
esxcli vsan debug disk smart get -d naa.<disk_id>

# Controller info (congestion, outstanding IO)
esxcli vsan debug controller list

# Space usage details
esxcli vsan debug space show

# Disk latency
esxcli vsan debug disk latency get
```

### Policy Commands

```bash
# List vSAN storage policies applied to a VM's namespace
esxcli vsan policy getdefault

# Set the default vSAN policy
esxcli vsan policy setdefault -c "proportionalCapacity=0" -p "hostFailuresToTolerate=1"
```

### Maintenance Mode

```bash
# Enter maintenance mode (ensure accessibility)
esxcli system maintenanceMode set -e true -m ensureAccessibility

# Enter maintenance mode (full data migration)
esxcli system maintenanceMode set -e true -m evacuateAllData

# Enter maintenance mode (no data migration)
esxcli system maintenanceMode set -e true -m noAction

# Exit maintenance mode
esxcli system maintenanceMode set -e false
```

### Advanced Settings

```bash
# List all vSAN advanced settings
esxcli system settings advanced list -o /VSAN

# Common performance-related settings
esxcli system settings advanced list -o /VSAN/ResyncThrottleAdaptive
esxcli system settings advanced list -o /VSAN/ResyncBandwidthCap
esxcli system settings advanced list -o /LSOM/lsomResyncThrottleEnabled

# Set a vSAN advanced parameter
esxcli system settings advanced set -o /VSAN/ResyncThrottleAdaptive -i 1
```

### Log Locations

```bash
# vSAN trace log
/var/log/vsantraced.log

# CLOMD (object placement) log
/var/log/clomd.log

# vSAN management log (on VCSA)
/var/log/vmware/vpxd/vpxd.log   # (vSAN operations logged here)

# vSAN health log (on VCSA)
/var/log/vmware/vsanHealth/vsanhealth.log

# VMkernel log (disk errors, IO errors)
/var/log/vmkernel.log

# Syslog (general ESXi system log)
/var/log/syslog.log

# vSAN observer data (if enabled)
/var/log/vsan/observer/
```

<div class="page-break"></div>

<a id="powercli-quick-reference"></a>

# 18. PowerCLI Quick Reference

### Connection & Setup

```powershell
# Install PowerCLI
Install-Module -Name VMware.PowerCLI -Scope CurrentUser -Force

# Connect to vCenter
Connect-VIServer -Server vcsa-01.vcf.local -User administrator@vsphere.local

# Ignore certificate errors (lab only)
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false
```

### Cluster Information

```powershell
# Get vSAN cluster configuration
$cluster = Get-Cluster "SDDC-Cluster1"
Get-VsanClusterConfiguration -Cluster $cluster

# Get cluster hosts
Get-VMHost -Location $cluster | Select Name, ConnectionState, PowerState

# Get vSAN datastore
Get-Datastore -RelatedObject $cluster | Where-Object { $_.Type -eq "vsan" }
```

### Health Checks

```powershell
# Get vSAN health summary
$cluster = Get-Cluster "SDDC-Cluster1"
$healthSystem = Get-VsanView -Id "VsanVcClusterHealthSystem-vsan-cluster-health-system"
$summary = $healthSystem.VsanQueryVcClusterHealthSummary(
    $cluster.ExtensionData.MoRef,
    $null, $null, $true, $null, $null, "defaultView"
)

# Display overall health
$summary.OverallHealth
$summary.OverallHealthDescription

# Display per-group health
$summary.Groups | ForEach-Object {
    [PSCustomObject]@{
        Group  = $_.GroupName
        Health = $_.GroupHealth
    }
} | Format-Table -AutoSize
```

### Capacity & Space

```powershell
# Get vSAN space usage
$cluster = Get-Cluster "SDDC-Cluster1"
Get-VsanSpaceUsage -Cluster $cluster

# Detailed space breakdown
$space = Get-VsanSpaceUsage -Cluster $cluster
[PSCustomObject]@{
    "Total (TB)"       = [math]::Round($space.TotalCapacityGB / 1024, 2)
    "Used (TB)"        = [math]::Round($space.UsedCapacityGB / 1024, 2)
    "Free (TB)"        = [math]::Round($space.FreeCapacityGB / 1024, 2)
    "Used %"           = [math]::Round(($space.UsedCapacityGB / $space.TotalCapacityGB) * 100, 1)
    "Dedup Ratio"      = [math]::Round($space.DedupRatio, 2)
    "Compression Ratio"= [math]::Round($space.CompressionRatio, 2)
}
```

### Disk Management

```powershell
# List all vSAN disks
$cluster = Get-Cluster "SDDC-Cluster1"
Get-VsanDisk -Cluster $cluster | Select VsanDiskGroup, CanonicalName, IsCacheDisk, CapacityGB

# Get disk groups per host
$hosts = Get-VMHost -Location $cluster
foreach ($vmHost in $hosts) {
    $dgs = Get-VsanDiskGroup -VMHost $vmHost
    foreach ($dg in $dgs) {
        [PSCustomObject]@{
            Host      = $vmHost.Name
            DiskGroup = $dg.Name
            DiskCount = ($dg | Get-VsanDisk).Count
        }
    }
} | Format-Table -AutoSize
```

### Storage Policies

```powershell
# List all vSAN storage policies
Get-SpbmStoragePolicy | Where-Object { $_.Name -like "*vSAN*" } |
    Select Name, Description

# Check VM compliance
$vms = Get-VM -Location (Get-Cluster "SDDC-Cluster1")
foreach ($vm in $vms) {
    $compliance = Get-SpbmEntityConfiguration -VM $vm
    foreach ($c in $compliance) {
        if ($c.ComplianceStatus -ne "compliant") {
            [PSCustomObject]@{
                VM     = $vm.Name
                Entity = $c.Entity
                Status = $c.ComplianceStatus
                Policy = $c.StoragePolicy.Name
            }
        }
    }
} | Format-Table -AutoSize

# Create a new vSAN storage policy
New-SpbmStoragePolicy -Name "vSAN-FTT1-RAID1" -Description "FTT=1 RAID-1 Mirroring" -RuleSet (
    New-SpbmRuleSet -Name "vSAN" -AllOfRules @(
        New-SpbmRule -Capability (Get-SpbmCapability -Name "VSAN.hostFailuresToTolerate") -Value 1,
        New-SpbmRule -Capability (Get-SpbmCapability -Name "VSAN.replicaPreference") -Value "RAID-1 (Mirroring) - Performance"
    )
)
```

### Fault Domains

```powershell
# List fault domains
$cluster = Get-Cluster "SDDC-Cluster1"
Get-VsanFaultDomain -Cluster $cluster | ForEach-Object {
    [PSCustomObject]@{
        Name  = $_.Name
        Hosts = ($_.VMHost.Name -join ", ")
    }
} | Format-Table -AutoSize

# Create a new fault domain
New-VsanFaultDomain -Name "rack-05" -VMHost (Get-VMHost "esx-05.vcf.local")

# Remove a fault domain
Remove-VsanFaultDomain -VsanFaultDomain (Get-VsanFaultDomain -Name "rack-05")
```

### Stretched Cluster

```powershell
# Get stretched cluster configuration
$cluster = Get-Cluster "SDDC-Cluster1"
$config = Get-VsanClusterConfiguration -Cluster $cluster
[PSCustomObject]@{
    StretchedCluster = $config.StretchedClusterEnabled
    PreferredSite    = $config.PreferredFaultDomain.Name
    WitnessHost      = $config.WitnessHost.Name
}

# Set preferred fault domain
Set-VsanClusterConfiguration -Cluster $cluster -PreferredFaultDomain (
    Get-VsanFaultDomain -Name "site-a"
)
```

### Performance Service

```powershell
# Enable performance service
$cluster = Get-Cluster "SDDC-Cluster1"
Set-VsanClusterConfiguration -Cluster $cluster -PerformanceServiceEnabled $true

# Check performance service status
(Get-VsanClusterConfiguration -Cluster $cluster).PerformanceServiceEnabled

# Query performance data
$vsanPerfMgr = Get-VsanView -Id "VsanPerformanceManager-vsan-performance-manager"
$spec = New-Object VMware.Vsan.Views.VsanPerfQuerySpec
$spec.EntityRefId = "cluster-domclient:*"
$spec.StartTime = (Get-Date).AddHours(-1)
$spec.EndTime = Get-Date
$vsanPerfMgr.VsanPerfQueryPerf(@($spec), $cluster.ExtensionData.MoRef)
```

### Maintenance & Operations

```powershell
# Enter maintenance mode (ensure accessibility)
$vmHost = Get-VMHost "esx-01.vcf.local"
Set-VMHost -VMHost $vmHost -State Maintenance -VsanDataMigrationMode EnsureAccessibility

# Enter maintenance mode (full evacuation)
Set-VMHost -VMHost $vmHost -State Maintenance -VsanDataMigrationMode Full

# Exit maintenance mode
Set-VMHost -VMHost $vmHost -State Connected

# Pre-check maintenance mode (dry run)
$vsanHealthSystem = Get-VsanView -Id "VsanVcClusterHealthSystem-vsan-cluster-health-system"
$vsanHealthSystem.VsanQueryVcClusterHealthSummary(
    (Get-Cluster "SDDC-Cluster1").ExtensionData.MoRef,
    $null, $null, $true, $null, $null, "maintenanceMode"
)
```

### Comprehensive Health Report Script

```powershell
# Full vSAN Health Report
function Get-VsanHealthReport {
    param(
        [string]$ClusterName = "SDDC-Cluster1"
    )

    $cluster = Get-Cluster $ClusterName
    $config = Get-VsanClusterConfiguration -Cluster $cluster
    $space = Get-VsanSpaceUsage -Cluster $cluster
    $hosts = Get-VMHost -Location $cluster

    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " vSAN Health Report: $ClusterName"       -ForegroundColor Cyan
    Write-Host " Generated: $(Get-Date)"                 -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # Cluster Config
    Write-Host "`n--- Cluster Configuration ---" -ForegroundColor Yellow
    Write-Host "  Hosts:           $($hosts.Count)"
    Write-Host "  vSAN Enabled:    $($config.VsanEnabled)"
    Write-Host "  Stretched:       $($config.StretchedClusterEnabled)"
    Write-Host "  Perf Service:    $($config.PerformanceServiceEnabled)"

    # Capacity
    Write-Host "`n--- Capacity ---" -ForegroundColor Yellow
    $usedPct = [math]::Round(($space.UsedCapacityGB / $space.TotalCapacityGB) * 100, 1)
    Write-Host "  Total:  $([math]::Round($space.TotalCapacityGB / 1024, 2)) TB"
    Write-Host "  Used:   $([math]::Round($space.UsedCapacityGB / 1024, 2)) TB ($usedPct%)"
    Write-Host "  Free:   $([math]::Round($space.FreeCapacityGB / 1024, 2)) TB"

    if ($usedPct -gt 80) {
        Write-Host "  STATUS: CRITICAL" -ForegroundColor Red
    } elseif ($usedPct -gt 70) {
        Write-Host "  STATUS: WARNING" -ForegroundColor Yellow
    } else {
        Write-Host "  STATUS: HEALTHY" -ForegroundColor Green
    }

    # Host Status
    Write-Host "`n--- Host Status ---" -ForegroundColor Yellow
    foreach ($h in $hosts) {
        $state = $h.ConnectionState
        $color = if ($state -eq "Connected") { "Green" } else { "Red" }
        Write-Host "  $($h.Name): $state" -ForegroundColor $color
    }

    # Disk Health
    Write-Host "`n--- Disk Health ---" -ForegroundColor Yellow
    $disks = Get-VsanDisk -Cluster $cluster
    Write-Host "  Total Disks: $($disks.Count)"

    # Policy Compliance
    Write-Host "`n--- Policy Compliance ---" -ForegroundColor Yellow
    $vms = Get-VM -Location $cluster
    $nonCompliant = 0
    foreach ($vm in $vms) {
        $compliance = Get-SpbmEntityConfiguration -VM $vm -ErrorAction SilentlyContinue
        $nonCompliant += ($compliance | Where-Object { $_.ComplianceStatus -ne "compliant" }).Count
    }

    if ($nonCompliant -eq 0) {
        Write-Host "  All VMs compliant" -ForegroundColor Green
    } else {
        Write-Host "  Non-compliant entities: $nonCompliant" -ForegroundColor Red
    }

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host " Report Complete"                          -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

# Execute the report
Get-VsanHealthReport -ClusterName "SDDC-Cluster1"
```

<div class="page-break"></div>

---

<div style="text-align: center; padding: 40px 20px; color: #666;">

**vSAN Health Check Handbook**

Version 1.0 -- March 2026

Copyright 2026 Virtual Control LLC. All rights reserved.

This document is for internal use only and may not be distributed without written permission.

VMware, vSAN, vSphere, vCenter, ESXi, and VCF are registered trademarks of Broadcom Inc.

</div>
