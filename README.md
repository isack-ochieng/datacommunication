# Narok County Referral Hospital — Network Design

A proposed secure, segmented and resilient LAN design for the Data Communication assignment. The project models one hospital building; the physical site layout and endpoint count remain subject to a real site survey.

## Download the Packet Tracer project (no local Python required)

**Direct project file:** [generated/Narok_County_Referral_Hospital.pkt](https://github.com/isack-ochieng/datacommunication/raw/refs/heads/main/generated/Narok_County_Referral_Hospital.pkt)

Open the raw file link to download the native `.pkt`, then open it in Cisco Packet Tracer.

To regenerate it, open [GitHub Actions](https://github.com/isack-ochieng/datacommunication/actions), select **Build Hospital Packet Tracer Project**, and click **Run workflow**. The workflow builds the file, decodes and validates the container structure, checks the expected devices, links and configuration fragments, commits the output to `generated/`, and uploads a 30-day artifact. No local Python installation is needed.

## What the simulation contains

- 2 Layer-3 core switches with HSRP departmental gateways.
- 2 dual-homed access switches with Rapid-PVST.
- 2 hospital edge routers with HSRP on the hospital and firewall-facing transit networks.
- 1 ASA 5505 firewall model and 1 simulated ISP router.
- 19 wired endpoint ports: 10 representative PCs/biomedical endpoints, 2 printer stand-ins, 2 wireless APs, 3 servers, 1 CCTV/NVR stand-in and 1 nurse-call gateway stand-in.
- Departmental VLANs, static endpoint addresses, inter-VLAN routing and guest/staff/biomedical ACL examples.

## IPv4 and VLAN design

Private allocation: `10.40.0.0/16` (within the RFC 1918 private `10.0.0.0/8` block), divided into /24 VLAN subnets.

| VLAN | Department / zone | Subnet | HSRP gateway |
|---:|---|---|---|
| 10 | Administration | 10.40.10.0/24 | 10.40.10.1 |
| 20 | Reception / OPD | 10.40.20.0/24 | 10.40.20.1 |
| 30 | Emergency / wards | 10.40.30.0/24 | 10.40.30.1 |
| 40 | Laboratory | 10.40.40.0/24 | 10.40.40.1 |
| 50 | Radiology | 10.40.50.0/24 | 10.40.50.1 |
| 60 | Pharmacy | 10.40.60.0/24 | 10.40.60.1 |
| 70 | Finance | 10.40.70.0/24 | 10.40.70.1 |
| 80 | Servers | 10.40.80.0/24 | 10.40.80.1 |
| 90 | Guest Wi-Fi | 10.40.90.0/24 | 10.40.90.1 |
| 100 | Staff Wi-Fi | 10.40.100.0/24 | 10.40.100.1 |
| 110 | Biomedical | 10.40.110.0/24 | 10.40.110.1 |
| 120 | CCTV / security | 10.40.120.0/24 | 10.40.120.1 |
| 130 | Nurse-call | 10.40.130.0/24 | 10.40.130.1 |
| 140 | Network management | 10.40.140.0/24 | 10.40.140.1 |

### Transit networks

- VLAN 254: `10.40.254.0/29`. Router HSRP VIP: `10.40.254.1`; R-Hospital-01: `.2`; R-Hospital-02: `.3`; Core-01: `.4`; Core-02: `.5`; core HSRP VIP: `.6`.
- Router-to-firewall inside: `198.51.100.0/29`. ASA inside: `.1`; router physical addresses: `.2` and `.3`; edge-router HSRP VIP: `.4`.
- Firewall-to-ISP outside: `198.51.100.8/30`. ASA outside: `.9`; ISP: `.10`.
- Simulated public test LAN: `203.0.113.0/24`.

The 198.51.100.0/24 and 203.0.113.0/24 blocks are documentation-only address ranges. They must be replaced with provider-assigned/private production addressing before any deployment.

## Important simulation limitations

- All generated Packet Tracer cable links are copper straight-through. The real design recommends Cat6A horizontal cabling and fibre for MDF-to-IDF/backbone routes; the simulator file is not proof of installed fibre.
- The Packet Tracer model uses Catalyst 3650, 2911 and ASA 5505 device templates. They are legacy/retired models and are **not** a purchase recommendation. Select currently supported hardware after a traffic, feature, support and budget assessment.
- Packet Tracer's bundled device-template catalogue lacks a native printer device here. The two printer labels are generic PC stand-ins; biomedical, NVR and nurse-call nodes are also simplified stand-ins.
- The APs advertise separate demonstration SSIDs. Wireless encryption/client authentication must be configured and tested separately; do not deploy an open SSID in a real hospital.
- Server nodes have static IP configurations and service-role labels. DHCP, DNS, clinical application, backup, NVR and nurse-call services are not fully implemented as production applications.
- The simulation has one firewall and one ISP path, so those remain single points of failure. Production design calls for an HA firewall pair and diverse WAN paths where available.

## First tests

- From `Admin-PC-01`: `ping 10.40.80.20` (clinical service placeholder).
- From a guest client assigned to VLAN 90: test access to `10.40.80.20`; guest ACL should deny private hospital networks.
- Check HSRP with `show standby brief` on both core switches and both edge routers.
- Check VLANs with `show vlan brief`; check trunks with `show interfaces trunk`.
- Test Core-01, Core-02, edge-router and WAN failure separately in a controlled simulation.

## Local build (optional)

Python 3.10+ is required only when generating locally:

```powershell
py -3 build_narok_hospital.py
```

## Companion documents

The Network Design and Technical Implementation Proposal and the Packet Tracer Walkthrough are provided as separate DOCX deliverables with this project handover.

## Scope notice

This is an academic proposed design for Narok County Referral Hospital. It is not an as-built representation, not a deployment approval and not evidence of the facility's current equipment or network. A site survey, clinical/ICT requirements workshop, security/privacy review and formal hospital sign-off are required before procurement or installation.
