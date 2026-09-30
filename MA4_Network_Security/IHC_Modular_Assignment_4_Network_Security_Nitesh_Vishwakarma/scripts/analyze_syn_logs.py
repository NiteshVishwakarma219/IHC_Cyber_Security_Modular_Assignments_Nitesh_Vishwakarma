#!/usr/bin/env python3
from collections import Counter
import re
from pathlib import Path
log=Path(__file__).resolve().parent.parent/"evidence"/"tcpdump_sample.log"
c=Counter()
for line in log.read_text().splitlines():
    if "Flags [S]" in line:
        m=re.search(r"IP\s+(\d+\.\d+\.\d+\.\d+)\.",line)
        if m: c[m.group(1)]+=1
print("MA4 SYN Traffic Summary")
print("SYN observations:",sum(c.values()))
for k,v in c.items(): print(f"  {k}: {v}")
print("Interpretation: high SYN rates with incomplete handshakes can indicate SYN-flood activity. This script only analyzes sample telemetry.")
