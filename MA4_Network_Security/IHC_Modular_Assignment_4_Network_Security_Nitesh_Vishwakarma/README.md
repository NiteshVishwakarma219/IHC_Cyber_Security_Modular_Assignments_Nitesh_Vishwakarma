# Modular Assignment 4 — Network Security

**Student:** Nitesh Vishwakarma  
**Course:** IHC - Practical Approach to Cyber Security (PACS)  
**Assignment:** 4 — Network Security

## Requirements covered
- Network threat model and common attack vectors
- ping, Nmap, traceroute, Wireshark and tcpdump
- Blind spoofing and TCP SYN flooding
- DDoS, botnets and crimeware
- Firewall and VPN defense mechanisms
- Written report, evidence logs, source/configuration files and summary presentation

## Evidence note
This package uses localhost examples and clearly labeled simulated telemetry. It does not claim unauthorized testing against public systems.

## Structure
- `report/` — PDF and editable DOCX
- `evidence/` — outputs, analysis notes, logs and architecture diagram
- `scripts/` — safe log-analysis script
- `configs/` — firewall, VPN and IDS/IPS examples
- `presentation/` — summary slides

## Run the analyzer
`python scripts/analyze_syn_logs.py`

The script analyzes included simulated telemetry; it does not generate attack traffic.
