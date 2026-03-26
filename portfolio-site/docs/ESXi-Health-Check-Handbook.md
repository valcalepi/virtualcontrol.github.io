---
title: "ESXi Hosts Health Check Handbook"
subtitle: "Comprehensive Health Verification for ESXi Hosts in VCF 9"
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
  headerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">ESXi Hosts Health Check Handbook &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  footerTemplate: '<div style="font-size:8px;color:#666;width:100%;text-align:center;padding:0 15mm;">Page <span class="pageNumber"></span> of <span class="totalPages"></span> &nbsp;|&nbsp; &copy; 2026 Virtual Control LLC</div>'
  displayHeaderFooter: true
---

<div class="cover-page">

# ESXi Hosts Health Check Handbook

<div class="subtitle">Comprehensive Health Verification for ESXi Hosts in VCF 9</div>

<div class="meta">

**Author:** Virtual Control LLC
**Date:** March 2026
**Version:** 1.0
**Classification:** Internal Use
**Platform:** VMware Cloud Foundation 9.0 / ESXi 8.0 U3+

</div>
</div>


<div class="toc">

## Table of Contents

<ul>
<li><a href="#overview">1. Overview &amp; Purpose</a></li>
<li><a href="#prerequisites">2. Prerequisites</a></li>
<li><a href="#quick-reference">3. Quick Reference &mdash; All Checks Summary</a></li>
<li><a href="#hardware">4. Hardware Health</a>
  <ul>
  <li><a href="#hw-sensors">4.1 Hardware Sensors (IPMI)</a></li>
  <li><a href="#hw-memory">4.2 Memory Hardware Errors</a></li>
  <li><a href="#hw-cpu">4.3 CPU Health</a></li>
  <li><a href="#hw-pci">4.4 PCI Devices</a></li>
  <li><a href="#hw-firmware">4.5 Firmware Versions</a></li>
  </ul>
</li>
<li><a href="#storage">5. Storage Health</a>
  <ul>
  <li><a href="#stor-vmfs">5.1 VMFS Datastores</a></li>
  <li><a href="#stor-scsi">5.2 SCSI Device Status</a></li>
  <li><a href="#stor-hba">5.3 HBA Health &amp; Multipathing</a></li>
  <li><a href="#stor-nfs">5.4 NFS Mounts</a></li>
  <li><a href="#stor-latency">5.5 Disk Latency &amp; SMART</a></li>
  </ul>
</li>
<li><a href="#networking">6. Networking Health</a>
  <ul>
  <li><a href="#net-vmknics">6.1 VMkernel Adapters</a></li>
  <li><a href="#net-vswitches">6.2 vSwitch / vDS Configuration</a></li>
  <li><a href="#net-uplinks">6.3 Physical Uplink Status</a></li>
  <li><a href="#net-drivers">6.4 NIC Driver &amp; Firmware</a></li>
  <li><a href="#net-cdp">6.5 CDP / LLDP Neighbor Info</a></li>
  <li><a href="#net-vmkping">6.6 vmkping Connectivity Tests</a></li>
  </ul>
</li>
<li><a href="#services">7. Services Health</a>
  <ul>
  <li><a href="#svc-list">7.1 Service Listing</a></li>
  <li><a href="#svc-critical">7.2 Critical Services</a></li>
  </ul>
</li>
<li><a href="#ntp">8. NTP Configuration</a></li>
<li><a href="#syslog">9. Syslog Configuration</a></li>
<li><a href="#scratch">10. Scratch Partition</a></li>
<li><a href="#coredump">11. Core Dump Configuration</a></li>
<li><a href="#security">12. Security Health</a>
  <ul>
  <li><a href="#sec-ssh">12.1 SSH Status</a></li>
  <li><a href="#sec-lockdown">12.2 Lockdown Mode</a></li>
  <li><a href="#sec-firewall">12.3 ESXi Firewall Rules</a></li>
  <li><a href="#sec-certs">12.4 Certificate Validity</a></li>
  <li><a href="#sec-accounts">12.5 Account Lockout Policy</a></li>
  </ul>
</li>
<li><a href="#performance">13. Performance Health</a>
  <ul>
  <li><a href="#perf-cpu">13.1 CPU Ready &amp; Co-Stop</a></li>
  <li><a href="#perf-mem">13.2 Memory Ballooning &amp; Swap</a></li>
  <li><a href="#perf-overcommit">13.3 Host Overcommit Ratio</a></li>
  </ul>
</li>
<li><a href="#boot">14. Boot Configuration</a></li>
<li><a href="#patches">15. Patch / VIB Level</a></li>
<li><a href="#ports">16. Port Reference Table</a></li>
<li><a href="#common-issues">17. Common Issues &amp; Remediation</a></li>
<li><a href="#cli-reference">18. CLI Quick Reference Card</a></li>
</ul>

</div>


## <span id="overview"></span>1. Overview & Purpose

This handbook provides a **complete, step-by-step health check procedure** for ESXi 8.0 hosts deployed within a VCF 9.0 environment. Use this during:

- **Routine maintenance** — Weekly/monthly proactive host verification
- **Pre/post-upgrade** — Before and after ESXi patches or VCF lifecycle operations
- **Incident response** — When VMs are experiencing performance or connectivity issues
- **Capacity planning** — Evaluating host resource utilization and VM density

### Scope

| Category | Checks Performed |
|----------|-----------------|
| Hardware | Sensors, IPMI, memory errors, CPU, PCI, firmware |
| Storage | VMFS, SCSI, HBA, multipathing, NFS, latency, SMART |
| Networking | VMkernel, vSwitches, uplinks, drivers, CDP/LLDP, connectivity |
| Services | All ESXi services, hostd, vpxa, NTP, syslog |
| Security | SSH, lockdown mode, firewall, certificates, account lockout |
| Performance | CPU ready, co-stop, memory balloon/swap, overcommit |
| Boot/Patch | Boot device, boot banks, image profile, VIB compliance |

<div class="info-box">
<strong>Notation:</strong> All commands in this document are run via SSH as <code>root</code> on the ESXi host unless otherwise specified. Replace <code>&lt;esxi-host&gt;</code> with your actual hostname or IP.
</div>



## <span id="prerequisites"></span>2. Prerequisites

### Required Access

| Access Type | Target | Credentials |
|-------------|--------|-------------|
| SSH (22) | Each ESXi host | root / password |
| HTTPS (443) | Each ESXi host | root / password |
| vCenter API | vCenter Server | administrator@vsphere.local |

### Enable SSH on ESXi (if disabled)

```bash
# Via DCUI: F2 → Troubleshooting Options → Enable SSH
# Via PowerCLI:
Get-VMHost -Name <esxi-host> | Get-VMHostService | Where {$_.Key -eq "TSM-SSH"} | Start-VMHostService
# Via esxcli (from vCenter or DCUI):
vim-cmd hostsvc/enable_ssh
vim-cmd hostsvc/start_ssh
```

### Environment Variables

```bash
# Set per-host or iterate across all hosts
export ESXI_HOSTS="192.168.1.201 192.168.1.202 192.168.1.203 192.168.1.204"
export ESXI_USER="root"
export ESXI_PASS="YourPassword123!"

# Loop template for multi-host checks
for HOST in $ESXI_HOSTS; do
  echo "======== $HOST ========"
  ssh root@$HOST '<command>'
done
```



## <span id="quick-reference"></span>3. Quick Reference — All Checks Summary

| # | Check | Command | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|---|-------|---------|------|------|------|
| 4.1 | Hardware Sensors | `esxcli hardware ipmi sdr list` | All `0x01` (Normal) | Any `0x02` (Warning) | Any `0x04` (Critical) |
| 4.2 | Memory Errors | `esxcli hardware memory get` | 0 uncorrectable | Correctable ECC errors | Uncorrectable ECC errors |
| 5.1 | VMFS Datastores | `esxcli storage vmfs extent list` | All mounted | Snapshot consolidation needed | Datastore unmounted |
| 5.3 | Multipathing | `esxcli storage nmp path list` | All paths `active` | Any path `standby` unexpected | Any path `dead` |
| 5.5 | Disk Latency | `esxtop` (d for disk) | < 20ms avg | 20-50ms avg | > 50ms avg |
| 6.1 | VMkernel NICs | `esxcli network ip interface list` | All enabled, IPs assigned | MTU mismatch | VMkernel missing/down |
| 6.3 | Uplinks | `esxcli network nic list` | All `Up` | Any NIC not at expected speed | Any NIC `Down` |
| 7.2 | Critical Services | `esxcli system process list` | hostd, vpxa running | Non-critical service stopped | hostd or vpxa not running |
| 8 | NTP | `esxcli system ntp get` | Synchronized, drift < 1s | Drift 1-5s | NTP not configured or drift > 5s |
| 9 | Syslog | `esxcli system syslog config get` | Remote target configured | Local-only logging | Syslog service not running |
| 10 | Scratch | `vim-cmd hostsvc/advopt/get ScratchConfig.ConfiguredScratchLocation` | Persistent storage | Ramdisk (non-persistent) | Not configured |
| 11 | Core Dump | `esxcli system coredump partition get` | Partition configured, active | Network dump only | No dump configured |
| 12.1 | SSH | `esxcli system process list \| grep SSH` | Disabled (production) | Enabled with timeout | Enabled, no timeout |
| 12.2 | Lockdown Mode | `vim-cmd hostsvc/hostsummary \| grep lockdownMode` | `lockdownNormal` or `lockdownStrict` | `lockdownDisabled` (lab OK) | `lockdownDisabled` (production) |
| 13.1 | CPU Ready | `esxtop` (c for CPU) | < 5% %RDY | 5-10% %RDY | > 10% %RDY |
| 13.2 | Balloon/Swap | `esxcli hardware memory get` | 0 balloon, 0 swap | Balloon active | Swap active |
| 14 | Boot Banks | `bootbank-util status` | Both banks healthy | Alt bank outdated | Primary bank corrupt |
| 15 | Patch Level | `esxcli software profile get` | Matches VCF BOM | 1 patch behind | 2+ patches behind |



## <span id="hardware"></span>4. Hardware Health

### <span id="hw-sensors"></span>4.1 Hardware Sensors (IPMI)

**What:** Read IPMI sensor data to verify temperatures, voltages, fan speeds, and power supply status.

**Why:** Hardware sensor warnings precede failures. Catching them early prevents unplanned outages.

#### CLI Method

```bash
esxcli hardware ipmi sdr list
```

**Expected Output (Healthy):**

```
Name                    Entity ID  Sensor Type     Reading  Units    Status
---------------------------------------------------------------------------
Inlet Temp              0x01.0x01  Temperature     22       C        0x01
Exhaust Temp            0x01.0x02  Temperature     35       C        0x01
CPU1 Temp               0x03.0x01  Temperature     48       C        0x01
CPU2 Temp               0x03.0x02  Temperature     45       C        0x01
FAN1                    0x1d.0x01  Fan             6200     RPM      0x01
FAN2                    0x1d.0x02  Fan             6100     RPM      0x01
P1-DIMMA1 Temp          0x20.0x01  Temperature     32       C        0x01
PSU1 Status             0x0a.0x01  Power Supply    —        —        0x01
PSU2 Status             0x0a.0x02  Power Supply    —        —        0x01
```

#### Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| `0x01` | Normal | No action |
| `0x02` | Warning | Monitor closely |
| `0x04` | Critical | Immediate attention |
| `0x08` | Non-recoverable | Hardware replacement |

#### Pass / Warn / Fail

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All sensors `0x01` (Normal) | Hardware healthy |
| <span class="badge-warn">WARN</span> | Any sensor `0x02` (Warning) | Monitor / schedule maintenance |
| <span class="badge-fail">FAIL</span> | Any sensor `0x04` or `0x08` | Replace hardware component |

#### Additional Sensor Commands

```bash
# Detailed hardware platform info
esxcli hardware platform get

# BMC/IPMI firmware info
esxcli hardware ipmi bmc get
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. High temps: Check datacenter cooling, airflow, dust<br>
2. Fan failure: Replace fan module; most servers continue with N-1 fans<br>
3. PSU warning: Check power cables; replace PSU under warranty<br>
4. Always cross-reference with vendor BMC (iDRAC, iLO, IPMI web UI)
</div>


### <span id="hw-memory"></span>4.2 Memory Hardware Errors

**What:** Check for correctable (CE) and uncorrectable (UE) memory errors.

```bash
# Memory overview
esxcli hardware memory get

# Check DIMM status
esxcli hardware memory dimm list
```

**Expected Output:**

```
Physical Memory: 549,755,813,888 Bytes (512 GB)
Reliable Memory: 549,755,813,888 Bytes

DIMM Locator     Bank     Type   Speed   Size      Status
----------------------------------------------------------
P1-DIMMA1        Bank 0   DDR5   4800    32768 MB  ok
P1-DIMMB1        Bank 1   DDR5   4800    32768 MB  ok
P1-DIMMC1        Bank 2   DDR5   4800    32768 MB  ok
...
```

#### Check VMkernel Log for Memory Errors

```bash
grep -i "machine check\|memory error\|ECC\|CECC\|UECC" /var/log/vmkernel.log | tail -20
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All DIMMs `ok`, no errors in vmkernel log | Healthy |
| <span class="badge-warn">WARN</span> | Correctable ECC errors (CE) present | Schedule DIMM replacement |
| <span class="badge-fail">FAIL</span> | Uncorrectable errors (UE) or DIMM status not `ok` | Immediate replacement |


### <span id="hw-cpu"></span>4.3 CPU Health

```bash
# CPU info
esxcli hardware cpu list | head -30

# CPU global stats
esxcli hardware cpu global get
```

**Expected Output:**

```
CPU Packages: 2
CPU Cores: 32
CPU Threads: 64
Hyperthreading Active: true
Hyperthreading Supported: true
```


### <span id="hw-pci"></span>4.4 PCI Devices

```bash
# List all PCI devices
esxcli hardware pci list | grep -E "Device Name|Vendor Name|Address"
```


### <span id="hw-firmware"></span>4.5 Firmware Versions

```bash
# BIOS info
esxcli hardware platform get

# Storage controller firmware
esxcli storage core adapter list
```



## <span id="storage"></span>5. Storage Health

### <span id="stor-vmfs"></span>5.1 VMFS Datastores

**What:** Verify all VMFS datastores are mounted, accessible, and have adequate free space.

```bash
# List VMFS extents
esxcli storage vmfs extent list
```

**Expected Output:**

```
Volume Name  VMFS UUID                             Extent #  Device Name                           Partition
-----------------------------------------------------------------------------------------------------------------
datastore1   61234567-abcdef01-2345-001122334455   0         naa.600508b4001234567890abcdef012345   3
vsanDatastore 71234567-abcdef01-2345-001122334455  0         —                                     —
```

#### Check Datastore Free Space

```bash
# Datastore capacity (via df equivalent)
esxcli storage filesystem list
```

**Expected Output:**

```
Mount Point              Volume Name    UUID                                  Mounted  Type  Size            Free
------------------------------------------------------------------------------------------------------------------
/vmfs/volumes/ds1        datastore1     61234567-abcdef01...                  true     VMFS-6  1099511627776  549755813888
/vmfs/volumes/vsanDs     vsanDatastore  71234567-abcdef01...                  true     vsan    4398046511104  2199023255552
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All datastores mounted, > 20% free | Healthy |
| <span class="badge-warn">WARN</span> | Any datastore 10-20% free | Plan capacity expansion |
| <span class="badge-fail">FAIL</span> | Any datastore < 10% free or unmounted | Critical — VMs may not power on |


### <span id="stor-scsi"></span>5.2 SCSI Device Status

```bash
# List all SCSI devices
esxcli storage core device list

# Check for devices in APD/PDL state
esxcli storage core device list | grep -E "Display Name|Status|Is Perennially Reserved"
```

**Key Indicators:**

| Status | Meaning |
|--------|---------|
| `on` | Device is online and accessible |
| `off` | Device is offline — APD or PDL |
| `APD` | All Paths Down — temporary, may recover |
| `PDL` | Permanent Device Loss — device is gone |

<div class="danger">
<strong>APD / PDL Warning:</strong> If any device shows APD or PDL, VMs on that storage may be inaccessible. APD triggers automatic VM termination after 140 seconds by default. Check <code>Misc.APDHandlingEnable</code> and <code>Misc.APDTimeout</code>.
</div>


### <span id="stor-hba"></span>5.3 HBA Health & Multipathing

**What:** Verify all storage paths are active and HBAs are functioning.

```bash
# List HBAs
esxcli storage core adapter list
```

**Expected Output:**

```
HBA Name  Driver       Link State  UID                            Description
------------------------------------------------------------------------------
vmhba0    lsi_mr3      link-up     sas.5001636001234567           LSI Logic SAS3108
vmhba1    lsi_mr3      link-up     sas.5001636001234568           LSI Logic SAS3108
vmhba32   iscsi_vmk    online      iqn.1998-01.com.vmware:esxi01  VMware iSCSI
```

#### Multipathing Status

```bash
# List all paths and their state
esxcli storage nmp path list
```

**Expected Output:**

```
Runtime Name: vmhba0:C0:T0:L0
  Device: naa.600508b400123456...
  Adapter: vmhba0
  LUN: 0
  State: active
  Transport: sas

Runtime Name: vmhba1:C0:T0:L0
  Device: naa.600508b400123456...
  Adapter: vmhba1
  LUN: 0
  State: active
  Transport: sas
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All paths `active`, multiple paths per device | Fully redundant |
| <span class="badge-warn">WARN</span> | Any path `standby` when should be `active` | Check path policy |
| <span class="badge-fail">FAIL</span> | Any path `dead` or single path per device | Path failure — no redundancy |

<div class="fix-box">
<strong>Remediation:</strong><br>
1. Dead path: Check physical cables, HBA, switch ports<br>
2. Re-scan storage: <code>esxcli storage core adapter rescan --all</code><br>
3. Reclaim dead paths: <code>esxcli storage core claiming reclaim -d naa.xxx</code><br>
4. Check multipath policy: <code>esxcli storage nmp device list</code>
</div>


### <span id="stor-nfs"></span>5.4 NFS Mounts

```bash
# List NFS datastores
esxcli storage nfs list
```

**Expected Output:**

```
Volume Name  Host            Share       Accessible  Mounted  Read-Only  Hardware Acceleration
----------------------------------------------------------------------------------------------
nfs-backup   192.168.1.100   /exports   true        true     false      Supported
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All NFS shares `Accessible: true`, `Mounted: true` | Healthy |
| <span class="badge-fail">FAIL</span> | Any NFS share `Accessible: false` | NFS server unreachable |


### <span id="stor-latency"></span>5.5 Disk Latency & SMART

**What:** Check real-time disk latency and SMART health data.

#### Check Latency via esxtop

```bash
# Interactive mode — press 'd' for disk view
esxtop

# Batch mode (3 samples, 5-second intervals)
esxtop -b -d 5 -n 3 | grep -E "DAVG|KAVG|GAVG"
```

**Key Metrics:**

| Metric | Description | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|--------|-------------|------|------|------|
| DAVG/cmd | Device latency (physical disk) | < 20ms | 20-50ms | > 50ms |
| KAVG/cmd | Kernel latency (VMkernel queue) | < 2ms | 2-5ms | > 5ms |
| GAVG/cmd | Guest OS observed latency | < 25ms | 25-50ms | > 50ms |

#### SMART Data (Local Disks)

```bash
# Check SMART status for local disks
esxcli storage core device smart get -d <device-naa-id>
```



## <span id="networking"></span>6. Networking Health

### <span id="net-vmknics"></span>6.1 VMkernel Adapters

**What:** Verify all VMkernel adapters have correct IPs, MTU, and enabled services.

```bash
# List VMkernel interfaces
esxcli network ip interface list
```

**Expected Output:**

```
Name   MAC Address        Enabled  MTU   Portgroup/DVPort    Stack       IPv4 Address
---------------------------------------------------------------------------------------
vmk0   00:50:56:01:aa:01  true     1500  Management Network  defaultTcpipStack  192.168.1.201
vmk1   00:50:56:01:aa:02  true     9000  vMotion             vmotion     192.168.10.201
vmk2   00:50:56:01:aa:03  true     9000  vSAN                defaultTcpipStack  192.168.12.74
vmk10  00:50:56:01:aa:04  true     1600  nsx-overlay         defaultTcpipStack  192.168.14.201
```

#### Check VMkernel Tagged Services

```bash
esxcli network ip interface tag get -i vmk0
esxcli network ip interface tag get -i vmk1
esxcli network ip interface tag get -i vmk2
```

| VMkernel | Expected Service Tags | MTU |
|----------|----------------------|-----|
| vmk0 | Management | 1500 |
| vmk1 | vMotion | 9000 |
| vmk2 | vSAN | 9000 |
| vmk10 | NSX TEP (no tag — NSX managed) | 1600+ |

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All vmknics enabled, correct IPs, correct MTU | Healthy |
| <span class="badge-warn">WARN</span> | MTU mismatch or wrong service tag | Reconfigure |
| <span class="badge-fail">FAIL</span> | VMkernel adapter missing or no IP | Connectivity loss |


### <span id="net-vswitches"></span>6.2 vSwitch / vDS Configuration

```bash
# List standard vSwitches
esxcli network vswitch standard list

# List Distributed vSwitches
esxcli network vswitch dvs vmware list
```

**Expected Output (DVS):**

```
Name: DSwitch-Management
  Configured Ports: 2048
  Max Ports: 2048
  MTU: 9000
  CDP Status: both
  Uplinks: vmnic0, vmnic1

Name: DSwitch-Compute
  Configured Ports: 2048
  Max Ports: 2048
  MTU: 9000
  Uplinks: vmnic2, vmnic3
```


### <span id="net-uplinks"></span>6.3 Physical Uplink Status

**What:** Verify all physical NICs are connected, at expected speed, and link is up.

```bash
esxcli network nic list
```

**Expected Output:**

```
Name    PCI Device  Driver  Admin Status  Link Status  Speed  Duplex  MTU    MAC Address
-------------------------------------------------------------------------------------------
vmnic0  0000:3b:00  i40en   Up            Up           25000  Full    9000   00:50:56:01:aa:10
vmnic1  0000:3b:01  i40en   Up            Up           25000  Full    9000   00:50:56:01:aa:11
vmnic2  0000:5e:00  i40en   Up            Up           25000  Full    9000   00:50:56:01:aa:12
vmnic3  0000:5e:01  i40en   Up            Up           25000  Full    9000   00:50:56:01:aa:13
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | All NICs `Link Status: Up`, expected speed | Healthy |
| <span class="badge-warn">WARN</span> | NIC at lower speed than expected (e.g., 10G vs 25G) | Check cables/switch |
| <span class="badge-fail">FAIL</span> | Any NIC `Link Status: Down` | Cable/switch/NIC failure |

<div class="fix-box">
<strong>Remediation:</strong><br>
1. NIC down: Check cable, switch port, SFP/transceiver<br>
2. Speed mismatch: Check auto-negotiation, cable category, switch config<br>
3. Replace NIC driver: <code>esxcli software vib install -v /path/to/driver.vib</code>
</div>


### <span id="net-drivers"></span>6.4 NIC Driver & Firmware

```bash
# Driver details per NIC
esxcli network nic get -n vmnic0
```

**Expected Output:**

```
Advertised Auto Negotiation: true
Auto Negotiation: true
Driver Info:
  Bus Info: 0000:3b:00.0
  Driver: i40en
  Firmware Version: 9.20
  Version: 2.5.3.0
Link Detected: true
Link Status: Up
```


### <span id="net-cdp"></span>6.5 CDP / LLDP Neighbor Info

**What:** Discover the physical switch port each ESXi NIC is connected to.

```bash
# CDP (Cisco Discovery Protocol)
esxcli network vswitch dvs vmware lacp config get
# or via vim-cmd:
vim-cmd hostsvc/net/query_networkhint --pnic-name=vmnic0
```

#### Using Python for CDP/LLDP

```bash
# Python one-liner to get CDP info
python3 -c "
from pyVim.connect import SmartConnect
import ssl
# ... (connect to host and query PhysicalNicHintInfo)
"
```


### <span id="net-vmkping"></span>6.6 vmkping Connectivity Tests

```bash
# Management network
vmkping -I vmk0 <vcenter-ip>

# vMotion network (jumbo frame test)
vmkping -I vmk1 -d -s 8972 <other-host-vmotion-ip>

# vSAN network (jumbo frame test)
vmkping -I vmk2 -d -s 8972 <other-host-vsan-ip>

# NSX TEP (MTU 1600)
vmkping -I vmk10 -d -s 1572 <other-host-tep-ip>
```

| Test | <span class="badge-pass">PASS</span> | <span class="badge-fail">FAIL</span> |
|------|------|------|
| Management | 0% loss | Any loss |
| vMotion jumbo | 0% loss with -s 8972 | Loss or "packet too big" |
| vSAN jumbo | 0% loss with -s 8972 | Loss or MTU error |
| NSX TEP | 0% loss with -s 1572 | Loss or MTU error |



## <span id="services"></span>7. Services Health

### <span id="svc-list"></span>7.1 Service Listing

```bash
# List all services and their status
esxcli system process list | head -60

# Alternative — list via chkconfig
chkconfig --list | sort
```

### <span id="svc-critical"></span>7.2 Critical Services

| Service | Process | Function | Impact if Down |
|---------|---------|----------|----------------|
| hostd | `hostd` | ESXi host agent | Host unreachable from vCenter |
| vpxa | `vpxa` | vCenter agent | Host disconnects from vCenter |
| vobd | `vobd` | VMware Observability | Events/alarms not generated |
| fdm | `fdm` | HA agent | HA not functional on host |
| ntpd | `ntpd` | Time sync | Time drift, cert issues |
| sfcbd | `sfcbd` | CIM broker | Hardware monitoring unavailable |
| lbtd | `lbtd` | Load-based teaming | NIC load balancing inactive |
| nsx-mpa | `nsx-mpa` | NSX management plane agent | NSX connectivity loss |
| nsx-proxy | `nsx-proxy` | NSX proxy | NSX data plane issues |

#### Verify Critical Services

```bash
/etc/init.d/hostd status
/etc/init.d/vpxa status
/etc/init.d/fdm status
/etc/init.d/ntpd status
/etc/init.d/nsx-mpa status
/etc/init.d/nsx-proxy status
```

**Expected Output for each:**

```
hostd is running.
```

<div class="fix-box">
<strong>Remediation:</strong><br>
1. Restart hostd: <code>/etc/init.d/hostd restart</code><br>
2. Restart vpxa: <code>/etc/init.d/vpxa restart</code><br>
3. Restart all management agents: <code>/sbin/services.sh restart</code><br>
4. Check logs: <code>/var/log/hostd.log</code>, <code>/var/log/vpxa.log</code>
</div>



## <span id="ntp"></span>8. NTP Configuration

**What:** Verify NTP is configured, running, and the host clock is synchronized.

```bash
# Check NTP configuration
esxcli system ntp get
```

**Expected Output:**

```
Enabled: true
Loglevel: warning
Server:
  - 192.168.1.1
  - 192.168.1.2
```

```bash
# Check NTP service status
/etc/init.d/ntpd status

# Check time offset
esxcli system time get
ntpq -p
```

**Expected ntpq Output:**

```
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
*192.168.1.1     .GPS.            1 u   64  128  377    0.543    0.125   0.043
+192.168.1.2     .GPS.            1 u   32  128  377    0.621    0.213   0.051
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | NTP enabled, offset < 1000ms, `reach` > 0 | Synchronized |
| <span class="badge-warn">WARN</span> | Offset 1-5 seconds | Drifting |
| <span class="badge-fail">FAIL</span> | NTP not configured, offset > 5s, or `reach` = 0 | Unsynchronized |

<div class="danger">
<strong>Time Sync Critical:</strong> ESXi hosts with > 5 seconds clock drift can cause vSAN issues, certificate validation failures, and cluster partition events.
</div>


## <span id="syslog"></span>9. Syslog Configuration

**What:** Verify syslog is forwarding to a remote collector.

```bash
# Get syslog config
esxcli system syslog config get
```

**Expected Output:**

```
Default Network Retry Timeout: 180
Dropped Log File Rotation Size: 100
Dropped Log File Rotations: 10
Log Output: /scratch/log
Log To Unique Subdirectory: false
Remote Host: udp://loginsight.lab.local:514
```

```bash
# Check syslog service
esxcli system syslog mark --message="Health Check Test $(date)"
# Then verify it appears on remote collector
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | Remote host configured, syslog service running | Healthy |
| <span class="badge-warn">WARN</span> | Local logging only (no remote) | Logs may be lost on failure |
| <span class="badge-fail">FAIL</span> | Syslog service not running | No logging |


## <span id="scratch"></span>10. Scratch Partition

**What:** Verify the scratch partition points to persistent storage (not ramdisk).

```bash
vim-cmd hostsvc/advopt/get ScratchConfig.ConfiguredScratchLocation
vim-cmd hostsvc/advopt/get ScratchConfig.CurrentScratchLocation
```

**Expected Output:**

```
ConfiguredScratchLocation: /vmfs/volumes/datastore1/.locker-<hostname>
CurrentScratchLocation: /vmfs/volumes/datastore1/.locker-<hostname>
```

<div class="warn-box">
<strong>Warning:</strong> If the scratch location is <code>/tmp/scratch</code> or empty, it's using ramdisk. Logs and coredumps will be lost on reboot. Set it to persistent storage.
</div>


## <span id="coredump"></span>11. Core Dump Configuration

```bash
# Check core dump partition
esxcli system coredump partition get

# Check network core dump
esxcli system coredump network get
```

**Expected Output:**

```
Active: true
Configured: true
Partition: naa.xxx:7

# Network dump:
Enabled: true
Host VmkNic: vmk0
Network Server IP: 192.168.1.50
Network Server Port: 6500
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | Partition configured and active, or network dump enabled | Can capture PSOD |
| <span class="badge-warn">WARN</span> | Only network dump (no local partition) | Depends on network availability |
| <span class="badge-fail">FAIL</span> | No dump target configured | PSOD data will be lost |



## <span id="security"></span>12. Security Health

### <span id="sec-ssh"></span>12.1 SSH Status

```bash
# Check if SSH is running
/etc/init.d/SSH status

# Check SSH timeout
esxcli system settings advanced list -o /UserVars/ESXiShellInteractiveTimeOut
esxcli system settings advanced list -o /UserVars/ESXiShellTimeOut
```

| Environment | Expected SSH State | Timeout |
|-------------|-------------------|---------|
| Production | Disabled (enable only for maintenance) | 300-900 seconds |
| Lab | Enabled acceptable | 900 seconds |


### <span id="sec-lockdown"></span>12.2 Lockdown Mode

```bash
vim-cmd hostsvc/hostsummary | grep lockdownMode
```

**Expected Output:**

```
lockdownMode = "lockdownNormal"
```

| Mode | Description | Recommendation |
|------|-------------|----------------|
| `lockdownDisabled` | No lockdown | Lab only |
| `lockdownNormal` | Only vCenter can manage host | Production recommended |
| `lockdownStrict` | vCenter only, no DCUI | High-security environments |


### <span id="sec-firewall"></span>12.3 ESXi Firewall Rules

```bash
# List all firewall rulesets
esxcli network firewall ruleset list

# Check specific rules
esxcli network firewall ruleset rule list --ruleset-id=sshServer
```

#### Key Rulesets to Verify

| Ruleset | Expected State | Purpose |
|---------|---------------|---------|
| `sshServer` | Enabled (maintenance) / Disabled (production) | SSH access |
| `webAccess` | Enabled | Host client UI |
| `vSphereClient` | Enabled | vCenter connectivity |
| `nsx` | Enabled | NSX communication |
| `ntpClient` | Enabled | NTP synchronization |
| `syslog` | Enabled | Log forwarding |


### <span id="sec-certs"></span>12.4 Certificate Validity

```bash
# Check the ESXi host certificate
openssl x509 -in /etc/vmware/ssl/rui.crt -noout -dates -subject
```

**Expected Output:**

```
notBefore=Jan 15 00:00:00 2026 GMT
notAfter=Jan 15 00:00:00 2028 GMT
subject=CN = esxi-01.lab.local, ...
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | Certificate > 30 days from expiry | Healthy |
| <span class="badge-warn">WARN</span> | Certificate 7-30 days from expiry | Plan renewal |
| <span class="badge-fail">FAIL</span> | Certificate expired or < 7 days | Renew immediately |


### <span id="sec-accounts"></span>12.5 Account Lockout Policy

```bash
esxcli system account policy get
```

**Expected Output:**

```
Maximum Failed Login Attempts: 5
Unlock Time (seconds): 900
```



## <span id="performance"></span>13. Performance Health

### <span id="perf-cpu"></span>13.1 CPU Ready & Co-Stop

**What:** Check if VMs are experiencing CPU scheduling delays (CPU ready time) or NUMA/co-stop issues.

#### esxtop Method

```bash
# Interactive — press 'c' for CPU view
esxtop

# Batch mode
esxtop -b -d 5 -n 3 > /tmp/esxtop-cpu.csv
```

**Key Columns in CPU View:**

| Column | Description | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|--------|-------------|------|------|------|
| %RDY | CPU Ready % | < 5% | 5-10% | > 10% |
| %CSTP | Co-Stop % | < 3% | 3-5% | > 5% |
| %USED | CPU Used % | < 80% | 80-90% | > 90% |

<div class="info-box">
<strong>CPU Ready Explained:</strong> %RDY shows the percentage of time a vCPU wanted to run but had to wait for a physical CPU. High values indicate host CPU overcommitment. Reduce VM vCPU count or migrate VMs to balance load.
</div>


### <span id="perf-mem"></span>13.2 Memory Ballooning & Swap

```bash
# Host memory summary
esxcli hardware memory get

# Check ballooning and swap via esxtop ('m' for memory view)
esxtop
```

**Key Memory Metrics:**

| Metric | Description | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|--------|-------------|------|------|------|
| MCTL (Balloon) | Memory reclaimed by balloon driver | 0 MB | > 0 but < 10% of VM memory | > 10% of VM memory |
| SWCUR (Swap used) | Memory swapped to disk | 0 MB | Any swap used | Swap actively in use (SWR/s > 0) |
| ZIP/s (Compression) | Memory compression rate | 0 | Low compression | High compression |
| CACHEUSD | Host cache used | — | — | > 80% of cache |

<div class="danger">
<strong>Swap Warning:</strong> Active swapping (SWR/s > 0) causes severe VM performance degradation. Add physical memory or reduce VM count.
</div>


### <span id="perf-overcommit"></span>13.3 Host Overcommit Ratio

```bash
# Calculate overcommit ratio
# Total VM vCPUs / Physical threads
esxcli hardware cpu global get
vim-cmd vmsvc/getallvms | wc -l

# Total configured VM memory vs physical memory
esxcli hardware memory get
```

#### Recommended Ratios

| Resource | <span class="badge-pass">PASS</span> | <span class="badge-warn">WARN</span> | <span class="badge-fail">FAIL</span> |
|----------|------|------|------|
| vCPU : pCPU | < 3:1 | 3:1 - 5:1 | > 5:1 |
| vRAM : pRAM | < 1.2:1 | 1.2:1 - 1.5:1 | > 1.5:1 |



## <span id="boot"></span>14. Boot Configuration

**What:** Verify the boot device, boot banks, and acceptance level.

```bash
# Boot device
esxcli system boot device get

# Boot bank status
/bin/bootbank-util status

# Acceptance level
esxcli software acceptance get
```

**Expected Output:**

```
Boot Device: mpx.vmhba0:C0:T0:L0
Boot Filesystem UUID: 61234567-abcdef01...
Boot bank: /bootbank (valid)
Alt boot bank: /altbootbank (valid)
Acceptance Level: VMwareCertified
```

| Result | Criteria | Indicator |
|--------|----------|-----------|
| <span class="badge-pass">PASS</span> | Both boot banks valid, acceptance `VMwareCertified` or `VMwareAccepted` | Healthy |
| <span class="badge-warn">WARN</span> | Alt boot bank outdated | Update after next patch |
| <span class="badge-fail">FAIL</span> | Primary boot bank corrupt or `CommunitySupported` acceptance | Remediation needed |


## <span id="patches"></span>15. Patch / VIB Level

**What:** Verify the installed ESXi image profile matches the VCF BOM.

```bash
# Installed image profile
esxcli software profile get
```

**Expected Output:**

```
Name: (Updated) ESXi-8.0U3-12345678-standard
Vendor: VMware, Inc.
Creation Time: 2026-01-15T00:00:00
Modification Time: 2026-01-15T00:00:00
Stateless Ready: True
```

```bash
# List all installed VIBs
esxcli software vib list | head -30

# Check for specific VIB
esxcli software vib list | grep -i nsx
```

#### VCF 9.0 Expected Versions (check BOM)

| Component | Expected Version |
|-----------|-----------------|
| ESXi | 8.0 U3 (build 12345678+) |
| NSX VIBs | 4.2.x |
| vSAN | Included in ESXi |
| Drivers | Per HCL |



## <span id="ports"></span>16. Port Reference Table

### Inbound Ports (to ESXi)

| Source | Port | Protocol | Purpose |
|--------|------|----------|---------|
| vCenter | 443 | TCP | Host management |
| vCenter | 902 | TCP | VM console (MKS) |
| vCenter | 8080 | TCP | vSphere Update Manager |
| Admin | 22 | TCP | SSH (when enabled) |
| Admin | 443 | TCP | Host Client UI |
| Admin | 5989 | TCP | CIM/WBEM |
| NSX Manager | 443 | TCP | Host preparation |
| Syslog Collector | 514 | UDP/TCP | Syslog (if push) |
| SNMP Manager | 161 | UDP | SNMP queries |

### Outbound Ports (from ESXi)

| Destination | Port | Protocol | Purpose |
|-------------|------|----------|---------|
| vCenter | 443 | TCP | vpxa → VPXD |
| vCenter | 80 | TCP | Reverse proxy |
| NSX Manager | 1234 | TCP | MPA |
| NSX Manager | 1235 | TCP | Central CLI |
| NSX Manager | 5671 | TCP | Message bus |
| ESXi (other) | 8000 | TCP | vMotion |
| ESXi (other) | 902 | TCP | NFC (provisioning) |
| ESXi (other) | 2233 | TCP | vSAN transport |
| ESXi (other) | 4789 | UDP | Geneve overlay |
| NTP Server | 123 | UDP | Time sync |
| DNS Server | 53 | TCP/UDP | Name resolution |
| Syslog | 514/6514 | UDP/TCP | Log forwarding |
| Dump Collector | 6500 | TCP | Network core dump |



## <span id="common-issues"></span>17. Common Issues & Remediation

### 17.1 PSOD (Purple Screen of Death)

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Purple screen on console | Kernel panic — driver/firmware bug, hardware failure, memory corruption | Collect core dump; check `/var/core/`; contact VMware support with dump |
| Recurring PSOD | Driver bug | Update driver/firmware per HCL; check VMware KB |

<div class="fix-box">
<strong>Collect PSOD info:</strong><br>
1. Note the error message on purple screen<br>
2. Core dump location: <code>esxcli system coredump partition get</code><br>
3. Extract: <code>vm-support --performance --output /vmfs/volumes/datastore1/</code><br>
4. File SR with VMware including the vm-support bundle
</div>

### 17.2 Storage APD / PDL

| Symptom | Type | Resolution |
|---------|------|------------|
| VMs frozen, "APD timeout" in logs | All Paths Down | Check SAN fabric, zoning, HBA; paths auto-recover |
| VMs terminated, "PDL" in logs | Permanent Device Loss | Storage LUN is permanently gone; restore from backup |

### 17.3 Network Partition

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Host shows disconnected in vCenter | Management network issue | Check vmk0 IP, switch port, VLAN; restart management agents |
| vSAN partition event | vSAN network failure | Check vmk2, switch MTU, VLAN trunking |
| vMotion failures | vMotion network | Check vmk1, MTU 9000, IP routing |

### 17.4 Host Disconnection from vCenter

```bash
# On ESXi host — restart management agents
/sbin/services.sh restart

# If that doesn't work, restart only vpxa
/etc/init.d/vpxa restart

# Check hostd logs for errors
tail -100 /var/log/hostd.log | grep -i error
tail -100 /var/log/vpxa.log | grep -i error
```

### 17.5 Performance Degradation

| Symptom | Check | Resolution |
|---------|-------|------------|
| High CPU Ready | `esxtop` %RDY > 10% | Right-size VMs (reduce vCPUs), DRS rebalance |
| Memory ballooning | `esxtop` MCTLSZ > 0 | Add RAM or migrate VMs |
| Storage latency | `esxtop` DAVG > 50ms | Check SAN, move VM to faster storage |
| Network drops | `esxcli network nic stats get -n vmnicX` | Check NIC errors, replace cable/NIC |



## <span id="cli-reference"></span>18. CLI Quick Reference Card

### System Information

| Command | Purpose |
|---------|---------|
| `esxcli system version get` | ESXi version and build |
| `esxcli system hostname get` | Hostname and domain |
| `esxcli system uuid get` | System UUID |
| `esxcli system boot device get` | Boot device info |
| `esxcli system time get` | Current system time |
| `esxcli system stats uptime get` | Uptime in seconds |
| `esxcli hardware platform get` | Hardware platform info |
| `esxcli hardware cpu global get` | CPU count/threads |
| `esxcli hardware memory get` | Total physical memory |

### Storage Commands

| Command | Purpose |
|---------|---------|
| `esxcli storage filesystem list` | Datastores and capacity |
| `esxcli storage vmfs extent list` | VMFS extents |
| `esxcli storage core device list` | SCSI devices |
| `esxcli storage core adapter list` | HBA adapters |
| `esxcli storage nmp path list` | Multipath status |
| `esxcli storage nmp device list` | Path policy per device |
| `esxcli storage core adapter rescan --all` | Rescan all storage |
| `esxcli storage nfs list` | NFS datastores |

### Networking Commands

| Command | Purpose |
|---------|---------|
| `esxcli network nic list` | Physical NICs |
| `esxcli network nic get -n vmnicX` | NIC detail/driver |
| `esxcli network nic stats get -n vmnicX` | NIC statistics |
| `esxcli network ip interface list` | VMkernel adapters |
| `esxcli network ip interface ipv4 get` | VMkernel IPv4 |
| `esxcli network ip route ipv4 list` | Routing table |
| `esxcli network ip dns server list` | DNS servers |
| `esxcli network vswitch standard list` | Standard vSwitches |
| `esxcli network vswitch dvs vmware list` | Distributed vSwitches |
| `esxcli network firewall ruleset list` | Firewall rules |
| `vmkping -I vmkX <target>` | Ping from VMkernel |

### Service Commands

| Command | Purpose |
|---------|---------|
| `/etc/init.d/hostd status` | Host agent status |
| `/etc/init.d/vpxa status` | vCenter agent status |
| `/etc/init.d/ntpd status` | NTP daemon status |
| `/etc/init.d/SSH status` | SSH service status |
| `/sbin/services.sh restart` | Restart all mgmt agents |
| `esxcli system process list` | Running processes |
| `chkconfig --list` | Service startup config |

### Security Commands

| Command | Purpose |
|---------|---------|
| `esxcli software acceptance get` | Acceptance level |
| `esxcli system account policy get` | Lockout policy |
| `vim-cmd hostsvc/hostsummary \| grep lockdown` | Lockdown mode |
| `esxcli network firewall get` | Firewall status |
| `openssl x509 -in /etc/vmware/ssl/rui.crt -noout -dates` | Cert expiry |

### Software / Patch Commands

| Command | Purpose |
|---------|---------|
| `esxcli software profile get` | Current image profile |
| `esxcli software vib list` | All installed VIBs |
| `esxcli software vib install -v <path>` | Install VIB |
| `esxcli software sources profile list -d <depot>` | Available profiles |

### Performance / Diagnostic Commands

| Command | Purpose |
|---------|---------|
| `esxtop` | Real-time performance |
| `esxtop -b -d 5 -n 3 > /tmp/out.csv` | Batch performance capture |
| `vm-support --performance` | Generate support bundle |
| `vmkbacktrace` | Stack trace |
| `vobd -e` | Event logging |
| `tail -f /var/log/vmkernel.log` | Kernel log (live) |
| `tail -f /var/log/hostd.log` | Host agent log |
| `tail -f /var/log/vpxa.log` | vCenter agent log |


<div style="text-align: center; margin-top: 40px; padding: 20px; border-top: 2px solid #1565c0; color: #666; font-size: 9pt;">

**ESXi Hosts Health Check Handbook**
Version 1.0 | March 2026
© 2026 Virtual Control LLC — All Rights Reserved

</div>
