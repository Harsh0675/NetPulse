# NetPulse 2.0
Root-free local network dashboard for Android + Termux.

Features: LAN /24 ICMP discovery, hostnames, gateway health, live monitoring,
new/offline alerts, latency statistics, CSV export, JSONL history, local logs,
JSON configuration, standard-library-only Python.

Install:
```bash
pkg install python
cd ~/NetPulse
chmod +x netpulse
./netpulse
```

Edit `config.json` for your LAN values. Runtime scan data and logs are kept local.
Android permissions may block ARP/MAC/netlink access, so NetPulse uses root-free ICMP.
Only scan networks you own or have permission to test.

Recommended GitHub repository: `NetPulse`.
