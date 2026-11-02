# Narok County Referral Hospital — Packet Tracer Project

A proposed Cisco Packet Tracer LAN design for an academic Data Communication assignment.

## Build the Packet Tracer file

**Windows**
1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Double-click `BUILD.bat`.
4. Open the generated `Narok_County_Referral_Hospital.pkt` in Cisco Packet Tracer.

Or run:

```powershell
py -3 build_narok_hospital.py
```

The script installs the `packet-tracer-pkt-format` Python package automatically if it is not already installed.

## Proposed topology

- 1 Catalyst 3650 multilayer core switch
- 6 Catalyst 2960 departmental access switches
- 2 Cisco 2911 routers (hospital edge and simulated ISP)
- Department PCs, two internal servers and one simulated public web server
- VLANs 10–90 and VLAN 99 for network management
- Inter-VLAN routing, static routing and a guest-network ACL

## VLAN and addressing plan

| VLAN | Department | Default gateway |
|---:|---|---|
| 10 | Administration | 192.168.10.1/24 |
| 20 | Reception | 192.168.20.1/24 |
| 30 | Emergency and wards | 192.168.30.1/24 |
| 40 | Laboratory | 192.168.40.1/24 |
| 50 | Radiology | 192.168.50.1/24 |
| 60 | Pharmacy | 192.168.60.1/24 |
| 70 | Finance | 192.168.70.1/24 |
| 80 | Servers | 192.168.80.1/24 |
| 90 | Guest Wi-Fi | 192.168.90.1/24 |
| 99 | Network management | 192.168.99.1/24 |

## First simulation checks

After opening the generated project:

1. From `ADMIN-PC-1`, open Desktop → Command Prompt and run `ping 192.168.80.10`.
2. From `GUEST-ACCESS-PC`, run `ping 192.168.80.10`. The guest ACL is intended to block access to the hospital's private network.
3. Use Simulation mode to inspect packet movement.

## Important scope note

This is a proposed academic simulation. It is **not** a verified representation of Narok County Referral Hospital's actual network or equipment. The generated file should be opened and checked in the installed Packet Tracer version before submission. The simulation uses representative endpoints and does not implement a production-grade hospital information system or certify regulatory compliance.
