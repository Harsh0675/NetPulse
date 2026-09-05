# NetPulse
Root-free local network dashboard for Android + Termux.

## 🌐 Live Browser UI

**[Open NetPulse Live](https://harsh0675.github.io/NetPulse/)**

> GitHub Pages hosts the browser interface. Actual LAN scanning requires the NetPulse Python backend running on your device.

## Features

- LAN /24 ICMP discovery
- Hostnames
- Gateway health
- Browser dashboard
- Live monitoring
- New/offline alerts
- Latency statistics
- CSV export
- JSONL history
- Local logs
- JSON configuration
- Root-free Android + Termux support

## Install

```bash
pkg install python
cd ~/NetPulse
chmod +x netpulse
./netpulse
```

For the browser dashboard:

```bash
python3 -m pip install flask
python3 web/app.py
```

Then open `http://127.0.0.1:5000` on the device.

Edit `config.json` for your LAN values. Runtime scan data and logs are kept local.
Android permissions may block ARP/MAC/netlink access, so NetPulse uses root-free ICMP.
Only scan networks you own or have permission to test.

## Repository

**[GitHub Repository](https://github.com/Harsh0675/NetPulse)**
