# 📘 Project Working — UPI Sound Box Security Demonstration

This document explains **how the project works internally**, including:
- data flow between Sender / Sound Box / Attacker
- Socket.IO events
- “secure mode” verification checks
- how each attack scenario is simulated in `app.py`

---

## 1) High-level Architecture

There are three UIs (frontends) and one backend:

### Frontend pages
1. **Sender (`/sender`)**
   - Creates legitimate payments by calling `POST /api/send_payment`

2. **Sound Box (`/soundbox`)**
   - Receives `payment_result` events in real-time
   - Announces accepted payments using browser text-to-speech (TTS)
   - Can enable/disable backend security checks via Socket event `toggle_security`

3. **Attacker (`/attacker`)**
   - Receives *captured legitimate payments* via `intercepted_payment`
   - Can launch attacks by calling `POST /api/attack`

### Backend (`app.py`)
- Flask routes render the pages
- API endpoints create or modify “payment messages”
- Socket.IO broadcasts results to all connected clients

---

## 2) Payment Message Format

A legitimate (authorized) payment is created by:

## `create_signed_payment(amount, sender_name, upi_app)`

It generates:
- `txn_id` — unique transaction id (e.g., `TXN...`)
- `nonce` — one-time token (anti-replay)
- `timestamp` — current UNIX time (seconds)
- `merchant_id` — fixed demo merchant `MERCH001`
- `device_cert` — fixed demo certificate string
- `signature` — HMAC-SHA256 signature over a canonical string

Canonical sign string:
```
{txn_id}|{amount}|{sender}|{upi_app}|{timestamp}|{nonce}|{merchant_id}
```

Signature:
- computed using `NPCI_GATEWAY_KEY` and SHA-256 HMAC
- represented as hex string

The resulting payment dict also includes:
- `source`: `"authorized"`
- `time_display`: current local time for UI display

---

## 3) Secure Mode vs Insecure Mode

A single runtime state controls security:

- `security_mode["enabled"] = False` by default

### Insecure mode (`enabled = False`)
- Any payment (authorized or attacker) is treated as accepted
- No verification checks are shown

This is intentional to demonstrate:  
> “Without verification, the sound box can be fooled.”

### Secure mode (`enabled = True`)
- Backend calls `verify_payment(payment)`
- If verification passes → accepted and recorded
- If verification fails → rejected and logged with check failures

---

## 4) Security Verification Checks (`verify_payment(p)`)

`verify_payment()` returns:
- `ok` (True/False)
- `checks` (list of check results for UI)

### Check #1: HMAC-SHA256 Digital Signature
- Reconstructs canonical sign string from payment fields
- Computes expected HMAC using `NPCI_GATEWAY_KEY`
- Compares with `p["signature"]` using `hmac.compare_digest`

**Blocks:**
- fake payments (wrong signature)
- tampered fields (amount changed but signature not updated)

### Check #2: Timestamp Freshness (30 seconds)
- Calculates age = `abs(now - p["timestamp"])`
- Must be <= 30 seconds

**Blocks:**
- delayed/replayed traffic outside freshness window

### Check #3: Nonce Uniqueness
- Tracks `used_nonces` (a Python set)
- Rejects if a nonce was already used

**Blocks:**
- replaying the same captured message

### Check #4: Transaction ID uniqueness
- Tracks `processed_txn_ids`
- Rejects if txn_id already processed

**Blocks:**
- duplicate transaction submission with same txn_id

### Check #5: Device Certificate check
- Accepts only certificates present in `REGISTERED_MERCHANTS`

**Blocks:**
- attacker’s fake cert

### Check #6: Merchant Registry check
- Accepts only known merchant ids in `REGISTERED_MERCHANTS`

**Blocks:**
- unknown merchant id from attacker

---

## 5) How Sender Works (`/api/send_payment`)

1. Sender UI calls:
   - `POST /api/send_payment` with `amount`, `sender`, `upi_app`

2. Backend creates an authorized payment:
   - `payment = create_signed_payment(...)`

3. If security mode is ON:
   - backend verifies payment
   - if valid, it “locks in”:
     - `used_nonces.add(payment["nonce"])`
     - `processed_txn_ids.add(payment["txn_id"])`

4. Backend emits Socket.IO:
   - `payment_result` → soundbox UI (accepted/rejected + checks)
   - `intercepted_payment` → attacker UI (to allow replay/tamper demo)

---

## 6) How Attacker Works (`/api/attack`)

Attacker UI sends JSON:
```json
{ "attack_type": "fake" | "replay" | "tamper", ... }
```

### A) Fake Payment Injection
Backend constructs a completely fake payment:
- `txn_id` starts with `"FAKE..."`
- `merchant_id = "FAKE_MERCH"`
- `device_cert = "FAKE-CERT-INVALID"`
- `signature` is random garbage

**Expected result:**
- In insecure mode → accepted (sound box fooled)
- In secure mode → rejected (signature/cert/merchant checks fail)

### B) Replay Attack
Backend copies a previously captured authorized payment:
- `payment = dict(captured)`
- sets `source = "attacker"`
- sets `attack_type = "Replay Attack"`

**Expected result:**
- In secure mode:
  - fails **nonce uniqueness** and/or **txn_id uniqueness**
  - may also fail timestamp freshness if replayed too late

### C) Amount Tampering
Backend copies captured payment but changes:
- `payment["amount"] = new_amount`
- signature is NOT recomputed

**Expected result:**
- In secure mode → fails HMAC signature check

---

## 7) Security Toggle Behavior

Soundbox UI emits:
- `toggle_security` with `{ enabled: true/false }`

Server handler:
- sets `security_mode["enabled"]`
- if turning security OFF:
  - clears `used_nonces` and `processed_txn_ids`
  - this “resets” replay protection for the next demo round
- emits `security_mode_changed` to all clients

---

## 8) Notes / Limitations (intentional for demo)

- The “gateway key” is hardcoded (only for demonstration)
- There is no real NPCI integration
- No TLS termination here (it’s a local demo)
- No database; replay protection sets are in-memory and reset on restart

---

## 9) Where to Extend Next (optional ideas)

- Add per-merchant keys (different HMAC keys)
- Add server-side rate limiting for attacks
- Add persistence (SQLite) for transaction history and replay cache
- Add rotating nonce windows / cleanup for memory safety
- Add device id binding and certificate pinning simulation
