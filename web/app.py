from flask import Flask, jsonify, render_template
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))

import netpulse

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan")
def api_scan():
    devices = netpulse.scan()
    return jsonify({
        "network": netpulse.NETWORK,
        "gateway": netpulse.GATEWAY,
        "local_ip": netpulse.LOCAL_IP,
        "devices": devices,
        "online": len(devices)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
