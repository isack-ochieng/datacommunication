"""Build the proposed Narok County Referral Hospital Packet Tracer topology.

The design uses RFC1918 private IPv4 space 10.40.0.0/16, departmental /24
VLANs, a redundant Layer-3 core (HSRP), redundant access uplinks, edge-router
HSRP, an ASA perimeter firewall, and 19 wired endpoint ports.

Printer nodes are represented by generic Packet Tracer PC endpoints because
the bundled offline device-template catalogue does not include Printer-PT.
The README and design report explain this simulation limitation.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    from pkt_core import Lab
except ImportError:
    print("Installing Packet Tracer file generator...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install",
        "packet-tracer-pkt-format==0.4.1",
    ])
    from pkt_core import Lab

OUT = Path(__file__).resolve().parent / "Narok_County_Referral_Hospital.pkt"
MASK24 = "255.255.255.0"
MASK16 = "255.255.0.0"
MASK30 = "255.255.255.252"
MASK29 = "255.255.255.248"

# vlan, descriptive name, third octet, gateway
VLANs = [
    (10, "ADMINISTRATION", 10, "10.40.10.1"),
    (20, "RECEPTION_OPD", 20, "10.40.20.1"),
    (30, "EMERGENCY_WARDS", 30, "10.40.30.1"),
    (40, "LABORATORY", 40, "10.40.40.1"),
    (50, "RADIOLOGY", 50, "10.40.50.1"),
    (60, "PHARMACY", 60, "10.40.60.1"),
    (70, "FINANCE", 70, "10.40.70.1"),
    (80, "SERVERS", 80, "10.40.80.1"),
    (90, "GUEST_WIFI", 90, "10.40.90.1"),
    (100, "STAFF_WIFI", 100, "10.40.100.1"),
    (110, "BIOMEDICAL", 110, "10.40.110.1"),
    (120, "CCTV_SECURITY", 120, "10.40.120.1"),
    (130, "NURSE_CALL", 130, "10.40.130.1"),
    (140, "NETWORK_MANAGEMENT", 140, "10.40.140.1"),
]
VLAN_IDS = ",".join(str(v[0]) for v in VLANs)
ACCESS_VLANS_1 = "10,20,30,40,50,60,70,80,90,100,110,120,130,140"
ACCESS_VLANS_2 = ACCESS_VLANS_1 + ",254"


def core_config(core_name: str, priority: int, own_suffix: int) -> list[str]:
    lines = [
        f"hostname {core_name}",
        "no ip domain-lookup",
        "ip routing",
        "spanning-tree mode rapid-pvst",
    ]
    for vlan_id, name, _third, _gateway in VLANs:
        lines += [f"vlan {vlan_id}", f" name {name}"]

    lines += ["vlan 254", " name ROUTER_TRANSIT"]

    for vlan_id, _name, third, _gateway in VLANs:
        own_ip = f"10.40.{third}.{2 if own_suffix == 2 else 3}"
        lines += [
            f"interface Vlan{vlan_id}",
            f" description { _name.replace('_', ' ').title() } gateway SVI",
            f" ip address {own_ip} {MASK24}",
            f" standby {vlan_id} ip 10.40.{third}.1",
            f" standby {vlan_id} priority {priority}",
            f" standby {vlan_id} preempt",
            " no shutdown",
        ]

    lines += [
        "interface Vlan254",
        f" ip address 10.40.254.{4 if own_suffix == 2 else 5} {MASK29}",
        " no shutdown",
        f"spanning-tree vlan {VLAN_IDS} root {'primary' if priority == 110 else 'secondary'}",
    ]

    # The two cores are interconnected; the access switches are dual-homed.
    for port, label in ((1, "ACCESS_01_PRIMARY"), (2, "ACCESS_02_PRIMARY")):
        lines += [
            f"interface GigabitEthernet1/0/{port}",
            f" description {label}",
            " switchport mode trunk",
            f" switchport trunk allowed vlan {ACCESS_VLANS_1}",
            " no shutdown",
        ]
    lines += [
        "interface GigabitEthernet1/0/23",
        " description INTER_CORE_TRUNK",
        " switchport mode trunk",
        f" switchport trunk allowed vlan {ACCESS_VLANS_2}",
        " no shutdown",
        "interface GigabitEthernet1/0/6",
        " description ROUTER_HSRP_TRANSIT",
        " switchport mode access",
        " switchport access vlan 254",
        " no shutdown",
        "ip route 0.0.0.0 0.0.0.0 10.40.254.1",
        "ip access-list extended GUEST-IN",
        " deny ip 10.40.90.0 0.0.0.255 10.40.0.0 0.0.255.255",
        " permit ip any any",
        "interface Vlan90",
        " ip access-group GUEST-IN in",
        "ip access-list standard NETWORK-MANAGEMENT",
        " permit host 10.40.10.10",
        " deny any",
        "line vty 0 15",
        " access-class NETWORK-MANAGEMENT in",
        "end",
    ]
    return lines


def access_switch_config(name: str, management_ip: str, port_assignments: list[tuple[int, str, str]]) -> list[str]:
    lines = [
        f"hostname {name}",
        "no ip domain-lookup",
        "spanning-tree mode rapid-pvst",
    ]
    for vlan_id, vlan_name, _third, _gateway in VLANs:
        lines += [f"vlan {vlan_id}", f" name {vlan_name}"]
    lines += [
        "vlan 254",
        " name ROUTER_TRANSIT",
        "interface Vlan140",
        f" ip address {management_ip} {MASK24}",
        " no shutdown",
        "ip default-gateway 10.40.140.1",
        "interface GigabitEthernet1/0/23",
        " description UPLINK_TO_CORE_01",
        " switchport mode trunk",
        f" switchport trunk allowed vlan {ACCESS_VLANS_1}",
        " no shutdown",
        "interface GigabitEthernet1/0/24",
        " description UPLINK_TO_CORE_02",
        " switchport mode trunk",
        f" switchport trunk allowed vlan {ACCESS_VLANS_1}",
        " no shutdown",
    ]
    for port, device_label, vlan_id in port_assignments:
        lines += [
            f"interface GigabitEthernet1/0/{port}",
            f" description {device_label}",
            " switchport mode access",
            f" switchport access vlan {vlan_id}",
            " spanning-tree portfast",
            " no shutdown",
        ]
    lines += ["end"]
    return lines


def router_config(name: str, inside_ip: str, outside_ip: str, priority: int, core_primary: str, core_backup: str) -> list[str]:
    lines = [
        f"hostname {name}",
        "no ip domain-lookup",
        "interface GigabitEthernet0/0",
        " description HOSPITAL_LAN_HSRP_TRANSIT",
        f" ip address {inside_ip} {MASK29}",
        " standby 254 ip 10.40.254.1",
        f" standby 254 priority {priority}",
        " standby 254 preempt",
        " no shutdown",
        "interface GigabitEthernet0/1",
        " description TO_PERIMETER_FIREWALL_INSIDE",
        f" ip address {outside_ip} {MASK29}",
        " standby 251 ip 198.51.100.4",
        f" standby 251 priority {priority}",
        " standby 251 preempt",
        " no shutdown",
        f"ip route 10.40.0.0 255.255.0.0 {core_primary}",
        f"ip route 10.40.0.0 255.255.0.0 {core_backup} 200",
        "ip route 0.0.0.0 0.0.0.0 198.51.100.1",
        "end",
    ]
    return lines


def firewall_config() -> list[str]:
    return [
        "hostname FW-Perimeter",
        "interface Vlan1",
        " nameif inside",
        " security-level 100",
        " ip address 198.51.100.1 255.255.255.248",
        " no shutdown",
        "interface Vlan2",
        " nameif outside",
        " security-level 0",
        " ip address 198.51.100.9 255.255.255.252",
        " no shutdown",
        "interface ethernet0/0",
        " switchport access vlan 1",
        " no shutdown",
        "interface ethernet0/1",
        " switchport access vlan 1",
        " no shutdown",
        "interface ethernet0/2",
        " switchport access vlan 2",
        " no shutdown",
        "object network HOSPITAL-LAN",
        " subnet 10.40.0.0 255.255.0.0",
        " nat (inside,outside) dynamic interface",
        "route inside 10.40.0.0 255.255.0.0 198.51.100.4 1",
        "route outside 0.0.0.0 0.0.0.0 198.51.100.10 1",
        "end",
    ]


def main() -> None:
    lab = Lab()
    lab.prune_seed_devices()

    # Core: both Layer-3 switches host the department SVIs and HSRP gateways.
    core1 = lab.add_device(
        "3650-24PS", "SW-Core-01", 520, 300,
        ios_config=core_config("SW-Core-01", priority=110, own_suffix=2),
    )
    core2 = lab.add_device(
        "3650-24PS", "SW-Core-02", 880, 300,
        ios_config=core_config("SW-Core-02", priority=100, own_suffix=3),
    )
    lab.link(core1, "GigabitEthernet1/0/23", core2, "GigabitEthernet1/0/23")

    # Two access switches are dual-homed to both core switches.
    access1_ports = [
        (1, "Admin-PC-01", 10),
        (2, "BIO-Device-01", 110),
        (3, "Reception-PC-01", 20),
        (4, "Emergency-PC-01", 30),
        (5, "ED-NurseStation-01", 30),
        (6, "Ward-NurseStation-01", 30),
        (7, "Lab-PC-01", 40),
        (8, "Radiology-PC-01", 50),
        (9, "Pharmacy-PC-01", 60),
        (10, "Finance-PC-01", 70),
    ]
    access2_ports = [
        (1, "PRN-OPD-01 (simulated printer)", 20),
        (2, "PRN-Lab-01 (simulated printer)", 40),
        (3, "AP-Staff-01", 100),
        (4, "AP-Guest-01", 90),
        (5, "SRV-Clinical-Records", 80),
        (6, "SRV-DHCP-DNS", 80),
        (7, "SRV-Backup", 80),
        (8, "NVR-Security", 120),
        (9, "GW-Nurse-Call", 130),
    ]

    access1 = lab.add_device(
        "3650-24PS", "SW-Access-01", 320, 650,
        ios_config=access_switch_config("SW-Access-01", "10.40.140.11", access1_ports),
    )
    access2 = lab.add_device(
        "3650-24PS", "SW-Access-02", 1080, 650,
        ios_config=access_switch_config("SW-Access-02", "10.40.140.12", access2_ports),
    )
    lab.link(core1, "GigabitEthernet1/0/1", access1, "GigabitEthernet1/0/23")
    lab.link(core2, "GigabitEthernet1/0/1", access1, "GigabitEthernet1/0/24")
    lab.link(core1, "GigabitEthernet1/0/2", access2, "GigabitEthernet1/0/23")
    lab.link(core2, "GigabitEthernet1/0/2", access2, "GigabitEthernet1/0/24")

    # Hospital edge routers use HSRP on a shared transit VLAN.
    r1 = lab.add_device(
        "2911", "R-Hospital-01", 250, 1000,
        ios_config=router_config(
            "R-Hospital-01", "10.40.254.2", "198.51.100.2", 110,
            "10.40.254.4", "10.40.254.5",
        ),
    )
    r2 = lab.add_device(
        "2911", "R-Hospital-02", 1150, 1000,
        ios_config=router_config(
            "R-Hospital-02", "10.40.254.3", "198.51.100.3", 100,
            "10.40.254.5", "10.40.254.4",
        ),
    )
    lab.link(core1, "GigabitEthernet1/0/6", r1, "GigabitEthernet0/0")
    lab.link(core2, "GigabitEthernet1/0/6", r2, "GigabitEthernet0/0")

    # Perimeter firewall and simulated ISP.
    firewall = lab.add_device(
        "5505", "FW-Perimeter", 700, 1200, ios_config=firewall_config()
    )
    isp = lab.add_device(
        "2911", "R-ISP", 1120, 1350,
        ios_config=[
            "hostname R-ISP",
            "interface GigabitEthernet0/0",
            " description TO_FW-PERIMETER_OUTSIDE",
            " ip address 198.51.100.10 255.255.255.252",
            " no shutdown",
            "interface GigabitEthernet0/1",
            " description SIMULATED_PUBLIC_TEST_NETWORK",
            " ip address 203.0.113.1 255.255.255.0",
            " no shutdown",
            "end",
        ],
    )
    lab.link(r1, "GigabitEthernet0/1", firewall, "Ethernet0/0")
    lab.link(r2, "GigabitEthernet0/1", firewall, "Ethernet0/1")
    lab.link(firewall, "Ethernet0/2", isp, "GigabitEthernet0/0")

    # 19 wired endpoint ports: 10 workstations, 2 shared printers, 2 APs,
    # 3 servers, 1 CCTV NVR and 1 nurse-call gateway.
    endpoint_specs = [
        ("Admin-PC-01", "PC-PT", "10.40.10.10", "10.40.10.1", 10, 170, 870),
        ("BIO-Device-01", "PC-PT", "10.40.110.10", "10.40.110.1", 110, 290, 870),
        ("Reception-PC-01", "PC-PT", "10.40.20.10", "10.40.20.1", 20, 410, 870),
        ("Emergency-PC-01", "PC-PT", "10.40.30.10", "10.40.30.1", 30, 530, 870),
        ("ED-NurseStation-01", "PC-PT", "10.40.30.11", "10.40.30.1", 30, 650, 870),
        ("Ward-NurseStation-01", "PC-PT", "10.40.30.12", "10.40.30.1", 30, 770, 870),
        ("Lab-PC-01", "PC-PT", "10.40.40.10", "10.40.40.1", 40, 890, 870),
        ("Radiology-PC-01", "PC-PT", "10.40.50.10", "10.40.50.1", 50, 1010, 870),
        ("Pharmacy-PC-01", "PC-PT", "10.40.60.10", "10.40.60.1", 60, 1130, 870),
        ("Finance-PC-01", "PC-PT", "10.40.70.10", "10.40.70.1", 70, 1250, 870),
    ]
    for i, (name, model, ip, gateway, _vlan, x, y) in enumerate(endpoint_specs, start=1):
        device = lab.add_device(model, name, x, y, pc_ip=(ip, MASK24, gateway))
        lab.link(access1, f"GigabitEthernet1/0/{i}", device, "FastEthernet0")

    # Shared print endpoints are generic host proxies in the offline builder.
    print_specs = [
        ("PRN-OPD-01", "10.40.20.230", "10.40.20.1", 20, 1450, 870, 1),
        ("PRN-Lab-01", "10.40.40.230", "10.40.40.1", 40, 1600, 870, 2),
    ]
    for name, ip, gateway, _vlan, x, y, port in print_specs:
        device = lab.add_device("PC-PT", name, x, y, pc_ip=(ip, MASK24, gateway))
        lab.link(access2, f"GigabitEthernet1/0/{port}", device, "FastEthernet0")

    # Separate APs keep staff and visitor wireless traffic in separate VLANs.
    staff_ap = lab.add_device(
        "AccessPoint-PT", "AP-Staff-01", 1420, 650,
        pc_ip=("10.40.100.230", MASK24, "10.40.100.1"),
    )
    guest_ap = lab.add_device(
        "AccessPoint-PT", "AP-Guest-01", 1570, 650,
        pc_ip=("10.40.90.230", MASK24, "10.40.90.1"),
    )
    lab.set_wireless(staff_ap, ssid="Narok-Staff", auth_type=4, encrypt_type=4, password="DemoOnly-Staff-2026", channel=1)
    lab.set_wireless(guest_ap, ssid="Narok-Guest", auth_type=4, encrypt_type=4, password="DemoOnly-Guest-2026", channel=6)
    lab.link(access2, "GigabitEthernet1/0/3", staff_ap, "Port 0")
    lab.link(access2, "GigabitEthernet1/0/4", guest_ap, "Port 0")

    # Core services are assigned fixed addresses in the server VLAN.
    server_specs = [
        ("SRV-Clinical-Records", "10.40.80.20", 1550, 1000, 5),
        ("SRV-DHCP-DNS", "10.40.80.10", 1720, 1000, 6),
        ("SRV-Backup", "10.40.80.30", 1890, 1000, 7),
    ]
    for name, ip, x, y, port in server_specs:
        device = lab.add_device("Server-PT", name, x, y, pc_ip=(ip, MASK24, "10.40.80.1"))
        lab.link(access2, f"GigabitEthernet1/0/{port}", device, "FastEthernet0")

    nvr = lab.add_device(
        "Server-PT", "NVR-Security", 2060, 1000,
        pc_ip=("10.40.120.10", MASK24, "10.40.120.1"),
    )
    lab.link(access2, "GigabitEthernet1/0/8", nvr, "FastEthernet0")

    nurse_call = lab.add_device(
        "Server-PT", "GW-Nurse-Call", 2230, 1000,
        pc_ip=("10.40.130.10", MASK24, "10.40.130.1"),
    )
    lab.link(access2, "GigabitEthernet1/0/9", nurse_call, "FastEthernet0")

    public_server = lab.add_device(
        "Server-PT", "SRV-Public-Test", 1470, 1350,
        pc_ip=("203.0.113.10", MASK24, "203.0.113.1"),
    )
    lab.link(isp, "GigabitEthernet0/1", public_server, "FastEthernet0")

    lab.save(str(OUT))
    print(f"\nCreated: {OUT}")
    print("Open the file in Cisco Packet Tracer and inspect the topology.")
    print("Connectivity test: Admin-PC-01 -> ping 10.40.80.20")
    print("Guest isolation test: after setting a guest client, ping 10.40.80.20 (should be blocked).")
    print("The 19 wired endpoint ports are allocated across SW-Access-01 and SW-Access-02.")


if __name__ == "__main__":
    main()
