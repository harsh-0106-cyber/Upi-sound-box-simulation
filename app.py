"""
UPI Sound Box Security Demonstration
=====================================
Three interfaces:
  /sender    - Authorized Payment Terminal (Laptop)
  /soundbox  - UPI Sound Box Device (Tablet)
  /attacker  - Attacker's Device (Phone)

Two Scenarios:
  1. Insecure Mode -> Attacker succeeds
  2. Secure Mode   -> Attacker is blocked
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import hashlib
import hmac
import uuid
import time
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# ============================
# SECURITY CONFIGURATION
# ============================

NPCI_GATEWAY_KEY = "NPCI_2024_HMAC_SECRET_GATEWAY_KEY_X9K2M"

REGISTERED_MERCHANTS = {
    "MERCH001": {
        "name": "Demo Shop",
        "device_id": "SB-001-2024",
        "certificate": "NPCI-CERT-2024-VALID-SB001"
    }
}

# Runtime state
security_mode = {"enabled": False}
processed_txn_ids = set()
used_nonces = set()
payment_history = []


# ============================
# SECURITY FUNCTIONS
# ============================

#This functions creates Unique Transaction ID
#Generate a NONCE (one time user token)
#Record the Current Time stamp
#Computes HMAC - SHA 256 Signature

def create_signed_payment(amount, sender_name, upi_app):
    txn_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
    nonce = uuid.uuid4().hex
    timestamp = str(time.time())

    sign_string = f"{txn_id}|{amount}|{sender_name}|{upi_app}|{timestamp}|{nonce}|MERCH001"
    signature = hmac.new(
        NPCI_GATEWAY_KEY.encode(), sign_string.encode(), hashlib.sha256
    ).hexdigest()

    return {
        "txn_id": txn_id,
        "amount": str(amount),
        "sender": sender_name,
        "upi_app": upi_app,
        "timestamp": timestamp,
        "nonce": nonce,
        "merchant_id": "MERCH001",
        "device_cert": "NPCI-CERT-2024-VALID-SB001",
        "signature": signature,
        "source": "authorized",
        "time_display": datetime.now().strftime("%H:%M:%S"),
    }


def verify_payment(p):
    checks = []
    ok = True

    # 1. HMAC Signature
    try:
        sign_string = f"{p['txn_id']}|{p['amount']}|{p['sender']}|{p['upi_app']}|{p['timestamp']}|{p['nonce']}|{p['merchant_id']}"
        expected = hmac.new(
            NPCI_GATEWAY_KEY.encode(), sign_string.encode(), hashlib.sha256
        ).hexdigest()
        if hmac.compare_digest(p.get("signature", ""), expected):
            checks.append({"name": "HMAC-SHA256 Digital Signature", "status": "pass",
                           "detail": "Signature matches — message integrity verified"})
        else:
            checks.append({"name": "HMAC-SHA256 Digital Signature", "status": "fail",
                           "detail": "Signature MISMATCH — tampered or unauthorized source"})
            ok = False
    except Exception:
        checks.append({"name": "HMAC-SHA256 Digital Signature", "status": "fail",
                       "detail": "Signature verification error"})
        ok = False

    # 2. Timestamp freshness (30 s window)
    try:
        age = abs(time.time() - float(p.get("timestamp", 0)))
        if age <= 30:
            checks.append({"name": "Timestamp Freshness", "status": "pass",
                           "detail": f"Age {age:.1f}s — within 30 s window"})
        else:
            checks.append({"name": "Timestamp Freshness", "status": "fail",
                           "detail": f"Age {age:.1f}s — EXPIRED (>30 s)"})
            ok = False
    except Exception:
        checks.append({"name": "Timestamp Freshness", "status": "fail",
                       "detail": "Invalid timestamp"})
        ok = False

    # 3. Nonce uniqueness
    nonce = p.get("nonce", "")
    if nonce in used_nonces:
        checks.append({"name": "Nonce Uniqueness", "status": "fail",
                       "detail": "DUPLICATE nonce — replay attack blocked"})
        ok = False
    else:
        checks.append({"name": "Nonce Uniqueness", "status": "pass",
                       "detail": "Nonce is unique — not a replay"})

    # 4. Transaction ID uniqueness
    txn_id = p.get("txn_id", "")
    if txn_id in processed_txn_ids:
        checks.append({"name": "Transaction ID Check", "status": "fail",
                       "detail": "Duplicate Transaction ID — already processed"})
        ok = False
    else:
        checks.append({"name": "Transaction ID Check", "status": "pass",
                       "detail": "Transaction ID is unique"})

    # 5. Device certificate
    valid_certs = [m["certificate"] for m in REGISTERED_MERCHANTS.values()]
    if p.get("device_cert", "") in valid_certs:
        checks.append({"name": "Device Certificate", "status": "pass",
                       "detail": "Certificate trusted & registered with NPCI"})
    else:
        checks.append({"name": "Device Certificate", "status": "fail",
                       "detail": "UNTRUSTED certificate"})
        ok = False

    # 6. Merchant registry
    if p.get("merchant_id", "") in REGISTERED_MERCHANTS:
        checks.append({"name": "Merchant Registry", "status": "pass",
                       "detail": "Merchant is registered"})
    else:
        checks.append({"name": "Merchant Registry", "status": "fail",
                       "detail": "Merchant NOT registered"})
        ok = False

    return ok, checks


# ============================
# ROUTES
# ============================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sender")
def sender_page():
    return render_template("sender.html")

@app.route("/soundbox")
def soundbox_page():
    return render_template("soundbox.html")

@app.route("/attacker")
def attacker_page():
    return render_template("attacker.html")


# ============================
# API ENDPOINTS
# ============================

@app.route("/api/send_payment", methods=["POST"])
def send_payment():
    data = request.json
    payment = create_signed_payment(
        data.get("amount", "0"),
        data.get("sender", "Unknown"),
        data.get("upi_app", "UPI"),
    )

    if security_mode["enabled"]:
        is_valid, checks = verify_payment(payment)
        if is_valid:
            used_nonces.add(payment["nonce"])
            processed_txn_ids.add(payment["txn_id"])
        payment_history.append(payment)
        socketio.emit("payment_result", {
            "payment": payment, "accepted": is_valid,
            "checks": checks, "secure_mode": True,
        })
    else:
        payment_history.append(payment)
        socketio.emit("payment_result", {
            "payment": payment, "accepted": True,
            "checks": [], "secure_mode": False,
        })

    socketio.emit("intercepted_payment", payment)
    return jsonify({"status": "sent", "txn_id": payment["txn_id"]})


@app.route("/api/attack", methods=["POST"])
def attack():
    data = request.json
    attack_type = data.get("attack_type", "fake")

    if attack_type == "fake":
        payment = {
            "txn_id": f"FAKE{uuid.uuid4().hex[:8].upper()}",
            "amount": str(data.get("amount", "999")),
            "sender": data.get("sender", "Fake Sender"),
            "upi_app": data.get("upi_app", "FakeApp"),
            "timestamp": str(time.time()),
            "nonce": uuid.uuid4().hex,
            "merchant_id": "FAKE_MERCH",
            "device_cert": "FAKE-CERT-INVALID",
            "signature": "fakesig_" + uuid.uuid4().hex[:16],
            "source": "attacker",
            "time_display": datetime.now().strftime("%H:%M:%S"),
            "attack_type": "Fake Payment Injection",
        }
    elif attack_type == "replay":
        captured = data.get("captured_payment")
        if not captured:
            return jsonify({"status": "error", "message": "No captured txn"})
        payment = dict(captured)
        payment["source"] = "attacker"
        payment["attack_type"] = "Replay Attack"
        payment["time_display"] = datetime.now().strftime("%H:%M:%S")
    elif attack_type == "tamper":
        captured = data.get("captured_payment")
        if not captured:
            return jsonify({"status": "error", "message": "No captured txn"})
        payment = dict(captured)
        payment["amount"] = str(data.get("new_amount", "10000"))
        payment["source"] = "attacker"
        payment["attack_type"] = "Amount Tampering"
        payment["time_display"] = datetime.now().strftime("%H:%M:%S")
    else:
        return jsonify({"status": "error", "message": "Unknown attack"})

    if security_mode["enabled"]:
        is_valid, checks = verify_payment(payment)
        result = {"payment": payment, "accepted": is_valid,
                  "checks": checks, "secure_mode": True, "is_attack": True}
    else:
        result = {"payment": payment, "accepted": True,
                  "checks": [], "secure_mode": False, "is_attack": True}

    if result["accepted"]:
        payment_history.append(payment)

    socketio.emit("payment_result", result)
    socketio.emit("attack_feedback", result)
    return jsonify({"status": "sent", "accepted": result["accepted"]})


# ============================
# SOCKET EVENTS
# ============================

@socketio.on("toggle_security")
def handle_toggle(data):
    security_mode["enabled"] = data.get("enabled", False)
    if not security_mode["enabled"]:
        used_nonces.clear()
        processed_txn_ids.clear()
    socketio.emit("security_mode_changed", {"enabled": security_mode["enabled"]})


@socketio.on("connect")
def handle_connect():
    emit("security_mode_changed", {"enabled": security_mode["enabled"]})


# ============================
# RUN
# ============================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  UPI SOUND BOX SECURITY DEMONSTRATION")
    print("=" * 60)
    print("  Home:     http://localhost:5000/")
    print("  Sender:   http://localhost:5000/sender")
    print("  SoundBox: http://localhost:5000/soundbox")
    print("  Attacker: http://localhost:5000/attacker")
    print("=" * 60 + "\n")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
