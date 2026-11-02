# Narok County Referral Hospital — Packet Tracer Project

Proposed academic LAN design for a Data Communication assignment.

## Build without installing Python

1. Open the repository's **[Actions](https://github.com/isack-ochieng/datacommunication/actions)** tab.
2. Select **Build Hospital Packet Tracer Project**.
3. Click **Run workflow** → **Run workflow**.
4. Open the completed run and download the **Narok-Council-Referral-Hospital-PKT** artifact.
5. Extract the downloaded ZIP and open `Narok_County_Referral_Hospital.pkt` in Cisco Packet Tracer.

## Build locally (optional)

Local building requires Python 3.10 or newer:

```powershell
py -3 build_narok_hospital.py
```

## Proposed topology

- Catalyst 3650 multilayer core switch
- Six Catalyst 2960 departmental access switches
- Two Cisco 2911 routers (hospital edge and simulated ISP)
- Staff PCs, internal services servers and a simulated public web server
- Department VLANs, inter-VLAN routing, static routes and a guest-network ACL

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

## Initial checks

- From `ADMIN-PC-1`, run `ping 192.168.80.10`.
- From `GUEST-ACCESS-PC`, run `ping 192.168.80.10`; the guest ACL is intended to block it.
- Use Packet Tracer's Simulation mode to inspect packets.

## Scope

This is a proposed academic simulation, not a verified representation of the hospital's actual network. Open and test the generated file in Packet Tracer before submission. It does not implement a production hospital information system or certify regulatory compliance.
