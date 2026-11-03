# Narok County Referral Hospital — Network Design Project

A proposed academic design and Cisco Packet Tracer simulation for a secure, resilient hospital LAN. This is a design proposal, not a claim about the hospital's installed network.

## Main deliverables

- [Network Design and Technical Implementation Proposal](docs/Narok_County_Referral_Hospital_Network_Design_Proposal.docx)
- [Packet Tracer Student Guide and Demonstration Checklist](docs/Narok_Hospital_Packet_Tracer_Student_Guide.docx)
- [Latest successful GitHub Actions build](https://github.com/isack-ochieng/datacommunication/actions/runs/41615518077)

## Download the Packet Tracer file

The latest validated build is in the GitHub Actions artifact named **Narok-Council-Referral-Hospital-PKT**.

1. Open the [latest successful workflow run](https://github.com/isack-ochieng/datacommunication/actions/runs/41615518077).
2. Download the artifact and extract its ZIP.
3. Open `Narok_County_Referral_Hospital.pkt` in Cisco Packet Tracer.

No Python installation is required on the student's computer. GitHub Actions runs the generator in its own hosted environment.

## Current simulated design

- 28 devices and 30 logical links.
- Two Catalyst 3650 multilayer core switches with HSRP.
- Two Catalyst 3650 access switches, dual-homed to both core switches.
- Two Cisco 2911 hospital edge routers with HSRP.
- One ASA 5505 perimeter firewall model and one simulated ISP router.
- 19 wired endpoint allocations, including workstations, printer stand-ins, APs, servers, CCTV/NVR and nurse-call gateway stand-ins.
- Two wireless APs with separate SSIDs: `Narok-Staff` and `Narok-Guest`. WPA2-PSK/AES settings are stored; configure a unique temporary lab passphrase manually on each AP in Packet Tracer under Config → Wireless.

Some end devices are generic Packet Tracer stand-ins because the builder's device-template catalogue does not include native printer, biomedical device, NVR or nurse-call gateway models.

## IPv4 addressing and VLAN plan

The proposed private addressing block is **10.40.0.0/16**, subnetted into /24 VLANs. The term “Class A” is the historical classful category; modern networks use CIDR.

| VLAN | Department / service | Network | Virtual gateway |
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
| 130 | Nurse-call systems | 10.40.130.0/24 | 10.40.130.1 |
| 140 | Network management | 10.40.140.0/24 | 10.40.140.1 |

The core-to-router transit uses 10.40.254.0/29. The router-to-firewall and firewall-to-ISP networks use separate TEST-NET documentation ranges, not real public addressing.

## What is and is not verified

GitHub Actions successfully generated and decoded the `.pkt` container, and structurally checked the device count, links, device names, 19 endpoint schedule, HSRP configuration fragments, IP plan and AP SSID/WPA2/AES fields.

**The workflow does not execute Packet Tracer's IOS/ASA runtimes or prove real packet forwarding, working links, ping, DHCP services or failover.** Open the file in the desktop Packet Tracer application and complete the tests in the Student Guide before submission.

The design still needs an on-site survey for building dimensions, actual cable routes and lengths, RF coverage, existing systems, clinical application flows, electrical resilience and procurement. The Packet Tracer project is an academic prototype, not a production-ready or compliance-certified hospital network.
