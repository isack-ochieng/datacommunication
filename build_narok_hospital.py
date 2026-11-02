"""Generate an editable Cisco Packet Tracer project for a proposed hospital LAN.

Requires Python 3.10+. The Packet Tracer file is written next to this script.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    from pkt_core import Lab
except ImportError:
    print("Installing the Packet Tracer file generator...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "packet-tracer-pkt-format"])
    from pkt_core import Lab

OUT = Path(__file__).resolve().parent / "Narok_County_Referral_Hospital.pkt"
MASK24 = "255.255.255.0"

VLANs = [
    (10, "ADMINISTRATION", "192.168.10.1"),
    (20, "RECEPTION", "192.168.20.1"),
    (30, "EMERGENCY_WARDS", "192.168.30.1"),
    (40, "LABORATORY", "192.168.40.1"),
    (50, "RADIOLOGY", "192.168.50.1"),
    (60, "PHARMACY", "192.168.60.1"),
    (70, "FINANCE", "192.168.70.1"),
    (80, "SERVERS", "192.168.80.1"),
    (90, "GUEST", "192.168.90.1"),
    (99, "NETWORK_MANAGEMENT", "192.168.99.1"),
]


def core_config() -> list[str]:
    lines = [
        "hostname SW-CORE",
        "no ip domain-lookup",
        "ip routing",
        "spanning-tree mode rapid-pvst",
    ]
    for vlan_id, name, _gateway in VLANs:
        lines += [f"vlan {vlan_id}", f" name {name}"]
    for vlan_id, _name, gateway in VLANs:
        lines += [
            f"interface Vlan{vlan_id}",
            f" description {vlan_id} department gateway",
            f" ip address {gateway} {MASK24}",
            " no shutdown",
        ]
    trunks = [
        (1, "10,20,99", "ADMIN-RECEPTION"),
        (2, "30,99", "EMERGENCY-WARDS"),
        (3, "40,50,99", "LAB-RADIOLOGY"),
        (4, "60,70,99", "PHARMACY-FINANCE"),
        (5, "80,99", "SERVERS"),
        (6, "90,99", "GUEST"),
    ]
    for port, allowed, label in trunks:
        lines += [
            f"interface GigabitEthernet1/0/{port}",
            f" description TRUNK_TO_{label}",
            " switchport mode trunk",
            f" switchport trunk allowed vlan {allowed}",
            " no shutdown",
        ]
    lines += [
        "interface GigabitEthernet1/0/24",
        " description ROUTED_LINK_TO_R-HOSPITAL",
        " no switchport",
        " ip address 192.168.254.1 255.255.255.252",
        " no shutdown",
        "ip access-list extended GUEST-IN",
        " deny ip 192.168.90.0 0.0.0.255 192.168.0.0 0.0.255.255",
        " permit ip any any",
        "interface Vlan90",
        " ip access-group GUEST-IN in",
        "ip route 0.0.0.0 0.0.0.0 192.168.254.2",
        "end",
    ]
    return lines


def access_config(name: str, mgmt_ip: str, allowed: str, port_vlans: list[tuple[int, str]]) -> list[str]:
    lines = ["hostname " + name, "no ip domain-lookup", "spanning-tree mode rapid-pvst"]
    vlan_ids = sorted({99, *[vlan for vlan, _ in port_vlans]})
    vlan_names = {v: n for v, n, _ in VLANs}
    for vlan_id in vlan_ids:
        lines += [f"vlan {vlan_id}", f" name {vlan_names[vlan_id]}"]
    lines += [
        "interface Vlan99",
        f" ip address {mgmt_ip} {MASK24}",
        " no shutdown",
        "ip default-gateway 192.168.99.1",
        "interface GigabitEthernet0/1",
        " description TRUNK_TO_SW-CORE",
        " switchport mode trunk",
        f" switchport trunk allowed vlan {allowed}",
        " no shutdown",
    ]
    for port_number, (vlan_id, description) in enumerate(port_vlans, start=1):
        lines += [
            f"interface FastEthernet0/{port_number}",
            f" description {description}",
            " switchport mode access",
            f" switchport access vlan {vlan_id}",
            " spanning-tree portfast",
            " no shutdown",
        ]
    lines.append("end")
    return lines


def main() -> None:
    lab = Lab()
    lab.prune_seed_devices()

    # Layer-3 core and simulated WAN edge.
    core = lab.add_device("3650-24PS", "SW-CORE", 1200, 330, ios_config=core_config())
    hospital_router = lab.add_device(
        "2911", "R-HOSPITAL", 1700, 330,
        ios_config=[
            "hostname R-HOSPITAL", "no ip domain-lookup",
            "interface GigabitEthernet0/0", " description TO_SW-CORE",
            " ip address 192.168.254.2 255.255.255.252", " no shutdown",
            "interface GigabitEthernet0/1", " description TO_R-ISP",
            " ip address 198.51.100.1 255.255.255.252", " no shutdown",
            "ip route 192.168.0.0 255.255.0.0 192.168.254.1",
            "ip route 0.0.0.0 0.0.0.0 198.51.100.2", "end",
        ],
    )
    isp_router = lab.add_device(
        "2911", "R-ISP", 2100, 170,
        ios_config=[
            "hostname R-ISP", "no ip domain-lookup",
            "interface GigabitEthernet0/0", " description TO_R-HOSPITAL",
            " ip address 198.51.100.2 255.255.255.252", " no shutdown",
            "interface GigabitEthernet0/1", " description SIMULATED_PUBLIC_NETWORK",
            " ip address 203.0.113.1 255.255.255.0", " no shutdown",
            "ip route 192.168.0.0 255.255.0.0 198.51.100.1", "end",
        ],
    )
    lab.link(core, "GigabitEthernet1/0/24", hospital_router, "GigabitEthernet0/0")
    lab.link(hospital_router, "GigabitEthernet0/1", isp_router, "GigabitEthernet0/0")

    # Department access switches: one switch represents multiple nearby departments where practical.
    switch_specs = [
        ("SW-ADMIN-RECEPTION", 1, "10,20,99", [(10, "ADMIN-PC-1"), (10, "ADMIN-PC-2"), (20, "RECEPTION-PC-1"), (20, "RECEPTION-PC-2")], "192.168.99.11", 350, 620),
        ("SW-EMERGENCY-WARDS", 2, "30,99", [(30, "EMERGENCY-PC"), (30, "NURSE-STATION")], "192.168.99.12", 750, 620),
        ("SW-LAB-RADIOLOGY", 3, "40,50,99", [(40, "LAB-PC"), (50, "RADIOLOGY-WORKSTATION")], "192.168.99.13", 1150, 620),
        ("SW-PHARMACY-FINANCE", 4, "60,70,99", [(60, "PHARMACY-PC"), (70, "FINANCE-PC")], "192.168.99.14", 1550, 620),
        ("SW-SERVERS", 5, "80,99", [(80, "PATIENT-RECORDS-SERVER"), (80, "ICT-SERVICES-SERVER")], "192.168.99.15", 1950, 620),
        ("SW-GUEST", 6, "90,99", [(90, "GUEST-ACCESS-PC")], "192.168.99.16", 2350, 620),
    ]

    hosts = [
        ("ADMIN-PC-1", "192.168.10.10", "192.168.10.1", 270, 900),
        ("ADMIN-PC-2", "192.168.10.11", "192.168.10.1", 390, 900),
        ("RECEPTION-PC-1", "192.168.20.10", "192.168.20.1", 510, 900),
        ("RECEPTION-PC-2", "192.168.20.11", "192.168.20.1", 630, 900),
        ("EMERGENCY-PC", "192.168.30.10", "192.168.30.1", 710, 900),
        ("NURSE-STATION", "192.168.30.11", "192.168.30.1", 830, 900),
        ("LAB-PC", "192.168.40.10", "192.168.40.1", 1110, 900),
        ("RADIOLOGY-WORKSTATION", "192.168.50.10", "192.168.50.1", 1230, 900),
        ("PHARMACY-PC", "192.168.60.10", "192.168.60.1", 1510, 900),
        ("FINANCE-PC", "192.168.70.10", "192.168.70.1", 1630, 900),
        ("GUEST-ACCESS-PC", "192.168.90.10", "192.168.90.1", 2310, 900),
    ]
    switch_ids = {}
    host_port_index = {}

    for name, core_port, allowed, port_vlans, mgmt_ip, x, y in switch_specs:
        sw = lab.add_device(
            "2960-24TT", name, x, y,
            ios_config=access_config(name, mgmt_ip, allowed, port_vlans),
        )
        switch_ids[name] = sw
        lab.link(core, f"GigabitEthernet1/0/{core_port}", sw, "GigabitEthernet0/1")
        host_port_index[name] = 1

    # Connect staff workstations to their departmental access switches.
    for name, ip, gateway, x, y in hosts:
        if name.startswith("ADMIN-") or name.startswith("RECEPTION-"):
            sw_name = "SW-ADMIN-RECEPTION"
        elif name in ("EMERGENCY-PC", "NURSE-STATION"):
            sw_name = "SW-EMERGENCY-WARDS"
        elif name in ("LAB-PC", "RADIOLOGY-WORKSTATION"):
            sw_name = "SW-LAB-RADIOLOGY"
        elif name in ("PHARMACY-PC", "FINANCE-PC"):
            sw_name = "SW-PHARMACY-FINANCE"
        else:
            sw_name = "SW-GUEST"
        pc = lab.add_device("PC-PT", name, x, y, pc_ip=(ip, MASK24, gateway))
        port_no = host_port_index[sw_name]
        lab.link(switch_ids[sw_name], f"FastEthernet0/{port_no}", pc, "FastEthernet0")
        host_port_index[sw_name] += 1

    # Internal application / services servers.
    server_records = lab.add_device(
        "Server-PT", "PATIENT-RECORDS-SERVER", 1910, 900,
        pc_ip=("192.168.80.10", MASK24, "192.168.80.1"),
    )
    server_services = lab.add_device(
        "Server-PT", "ICT-SERVICES-SERVER", 2070, 900,
        pc_ip=("192.168.80.20", MASK24, "192.168.80.1"),
    )
    lab.link(switch_ids["SW-SERVERS"], "FastEthernet0/1", server_records, "FastEthernet0")
    lab.link(switch_ids["SW-SERVERS"], "FastEthernet0/2", server_services, "FastEthernet0")

    # External test server to demonstrate routed connectivity beyond the hospital LAN.
    public_server = lab.add_device(
        "Server-PT", "PUBLIC-WEB-SERVER", 2450, 170,
        pc_ip=("203.0.113.10", MASK24, "203.0.113.1"),
    )
    lab.link(isp_router, "GigabitEthernet0/1", public_server, "FastEthernet0")

    lab.save(str(OUT))
    print(f"\nCreated: {OUT}")
    print("Open this .pkt file in Cisco Packet Tracer.")
    print("Suggested first test: ADMIN-PC-1 > Desktop > Command Prompt > ping 192.168.80.10")
    print("Guest isolation test: GUEST-ACCESS-PC > ping 192.168.80.10 (should be blocked by the ACL)")


if __name__ == "__main__":
    main()
