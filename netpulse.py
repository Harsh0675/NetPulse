#!/usr/bin/env python3
import csv, json, os, socket, statistics, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

BASE=Path(__file__).resolve().parent
CONFIG_FILE=BASE/"config.json"; DATA_DIR=BASE/"data"; LOG_DIR=BASE/"logs"
DATA_DIR.mkdir(exist_ok=True); LOG_DIR.mkdir(exist_ok=True)
DEFAULT={
    "network":"192.168.31.0/24",
    "gateway":"192.168.31.1",
    "max_workers":16,
    "ping_timeout":1,
    "live_interval":5
}

def load_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(DEFAULT, indent=2))
    try:
        x=DEFAULT.copy()
        x.update(json.loads(CONFIG_FILE.read_text()))
        return x
    except Exception:
        return DEFAULT.copy()

C=load_config()
NETWORK=C["network"]
GATEWAY=C["gateway"]
WORKERS=int(C["max_workers"])
TIMEOUT=int(C["ping_timeout"])
INTERVAL=int(C["live_interval"])

def detect_local_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect((GATEWAY,80))
        ip=s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "-"

LOCAL_IP=detect_local_ip()

def stamp(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def log(s):
    with open(LOG_DIR/"netpulse.log","a",encoding="utf8") as f: f.write(f"[{stamp()}] {s}\n")

def ips():
    a,b,c,_=map(int,NETWORK.split("/")[0].split("."))
    return [f"{a}.{b}.{i}" for i in range(1,255)]

def ping(ip):
    try:
        t=time.perf_counter()
        p=subprocess.run(["ping","-c","1","-W",str(TIMEOUT),ip],
                         stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                         timeout=TIMEOUT+2)
        return round((time.perf_counter()-t)*1000,1) if p.returncode==0 else None
    except Exception: return None

def host(ip):
    try: return socket.gethostbyaddr(ip)[0]
    except Exception: return "-"

def probe(ip):
    ms=ping(ip)
    if ms is None: return None
    name="This Device" if ip == LOCAL_IP else host(ip)
    return {"ip":ip,"status":"ONLINE","latency":ms,"hostname":name,"mac":"-","vendor":"-"}

def addresses():

    base = NETWORK.split("/")[0].split(".")
    return [f"{base[0]}.{base[1]}.{base[2]}.{i}" for i in range(1, 255)]

def scan():
    print(f"\nScanning {NETWORK} ...")
    out = []

    # Use concurrent probes for a much faster LAN scan.
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(probe, ip): ip for ip in addresses()}

        for future in as_completed(futures):
            try:
                result = future.result()
                if result["status"] == "ONLINE":
                    out.append(result)
            except Exception:
                pass

    return sorted(
        out,
        key=lambda x: tuple(map(int, x["ip"].split(".")))
    )

def show(rs):
    print("\n"+"="*105); print("NETPULSE"); print("="*105)
    print(f"Local IP : {LOCAL_IP}\nNetwork  : {NETWORK}\nGateway  : {GATEWAY}")
    print("-"*105); print(f"{'IP':<16} {'STATUS':<9} {'LATENCY':<11} {'DEVICE':<24} {'MAC':<18} VENDOR"); print("-"*105)
    for r in rs: print(f'{r["ip"]:<16} {r["status"]:<9} {str(r["latency"])+" ms" if r["latency"] else "-":<11} {r["hostname"]:<24} {r.get("mac","-"):<18} {r.get("vendor","-")}')
    print("-"*105); print("Online devices:",len(rs)); print("="*105)

def gateway():
    print(f"\nTesting gateway: {GATEWAY}")
    ms=ping(GATEWAY)
    print(f"Gateway {'ONLINE — '+str(ms)+' ms' if ms is not None else 'OFFLINE'}")
    return ms is not None

def export(rs):
    if not rs: print("\nRun a scan first."); return
    p=DATA_DIR/f"netpulse-{datetime.now():%Y%m%d-%H%M%S}.csv"
    with open(p,"w",newline="",encoding="utf8") as f:
        w=csv.DictWriter(f,fieldnames=["ip","status","latency","hostname"]); w.writeheader(); w.writerows(rs)
    print("\nExported:",p)

def history(rs):
    with open(DATA_DIR/"history.jsonl","a",encoding="utf8") as f:
        f.write(json.dumps({"timestamp":stamp(),"online":len(rs),"devices":rs})+"\n")

def stats(rs):
    v=[r["latency"] for r in rs if r["latency"] is not None]
    if v: print(f"\nLatency — Min: {min(v):.1f} ms | Avg: {statistics.mean(v):.1f} ms | Max: {max(v):.1f} ms")
    else: print("\nNo latency data.")

def live():
    print("\nLive monitor started. Ctrl+C to stop."); old={}
    try:
        while True:
            rs=scan(); cur={r["ip"]:r for r in rs}; show(rs)
            new=sorted(set(cur)-set(old)); gone=sorted(set(old)-set(cur))
            if new: print("NEW DEVICE(S):",", ".join(new)); log("New: "+",".join(new))
            if gone: print("DEVICE OFFLINE:",", ".join(gone)); log("Offline: "+",".join(gone))
            if GATEWAY in gone: print("ALERT: GATEWAY IS OFFLINE"); log("ALERT: gateway offline")
            history(rs); old=cur; time.sleep(INTERVAL)
    except KeyboardInterrupt: print("\nLive monitor stopped.")

def main():
    last=[]
    while True:
        print("\n[1] Scan LAN\n[2] Gateway test\n[3] Live monitor\n[4] Export CSV\n[5] Latency stats\n[6] Show config\n[Q] Quit")
        x=input("NetPulse > ").strip().lower()
        if x=="1": last=scan(); show(last); history(last)
        elif x=="2": gateway()
        elif x=="3": live()
        elif x=="4": export(last)
        elif x=="5": stats(last)
        elif x=="6": print(json.dumps(C,indent=2))
        elif x=="q": print("Goodbye."); break
        else: print("Invalid option.")
if __name__=="__main__":
    try: main()
    except Exception as e: log("Fatal: "+repr(e)); print("NetPulse error:",e); sys.exit(1)
