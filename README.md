# 🔊 UPI Sound Box — Security Demonstration (Authorized vs Attacker)

A small **Flask + Socket.IO** web demo that simulates how a **UPI Sound Box** announces incoming payments, and how basic security controls can **block attacker attempts** like:

- **Fake payment injection** (completely fabricated message)
- **Replay attack** (re-sending a previously captured valid transaction)
- **Amount tampering** (modifying a legitimate transaction amount)

This project is built for learning/presentations: you can run it locally and open the **Sender**, **Sound Box**, and **Attacker** UIs in different browser tabs/devices.

---

## ✨ Features

### Authorized flow
- Sender page creates a *legitimate* payment message
- Payment is broadcast in real-time to the sound box
- Sound box announces it using browser text-to-speech (TTS)

### Security mode (toggle)
When **Security Mode = ON**, the backend verifies a payment using:
- HMAC-SHA256 signature verification
- Timestamp freshness window (30 seconds)
- Nonce uniqueness (anti-replay)
- Transaction ID uniqueness
- Device certificate whitelist check
- Merchant registry verification

When **Security Mode = OFF**, the sound box accepts everything (to show how attacks “work” without verification).

### Attacker flow
Attacker page can:
- Send a **fake** payment message
- **Replay** a captured payment
- **Tamper** the amount of a captured payment

---

## 🧰 Tech Stack

- Python / Flask
- Flask-SocketIO (real-time event broadcast)
- HTML/CSS/JS frontends
- Browser Web Speech API (speechSynthesis) for announcements

---

## 📁 Project Structure (important files)

- `app.py` — Main server (routes, API endpoints, security verification, Socket.IO events)
- `templates/index.html` — Home page (links to Sender/Soundbox/Attacker)
- `templates/sender.html` — Authorized payment sender UI
- `templates/soundbox.html` — Sound box UI + security toggle + logs
- `templates/attacker.html` — Attacker UI (fake/replay/tamper) + feedback log
- `requirements.txt` — Python dependencies

> Note: Your HTML files should be inside a `templates/` folder for `render_template()` to work.

---

## ✅ Requirements

- Python 3.9+ recommended
- A browser with Speech Synthesis support (Chrome/Edge work well)

---

## 🚀 Setup & Run

### 1) Clone and install dependencies
```bash
pip install -r requirements.txt
```

### 2) Run the server
```bash
python app.py
```

You should see output with URLs like:
- Home: `http://localhost:5000/`
- Sender: `http://localhost:5000/sender`
- SoundBox: `http://localhost:5000/soundbox`
- Attacker: `http://localhost:5000/attacker`

---

## 🧪 Demo / Presentation Flow (suggested)

1. Open **Sound Box** on a tablet/second screen (or another tab)
2. Click **Activate Sound Box** (enables voice announcements)
3. Open **Sender** and send a legitimate payment  
   → Sound box announces it
4. Open **Attacker** and launch **Fake Payment Injection** while security is **OFF**  
   → It succeeds (sound box is fooled)
5. On Sound Box, toggle **Security Mode ON**
6. Repeat attacks (Fake / Replay / Tamper)  
   → They are blocked and the security checks are displayed

---

## 🔌 Routes & Endpoints

### Pages
- `GET /` → Home UI
- `GET /sender` → Authorized sender UI
- `GET /soundbox` → Sound box UI
- `GET /attacker` → Attacker UI

### APIs
- `POST /api/send_payment`  
  Creates a signed “authorized” payment and broadcasts it to clients.

- `POST /api/attack`  
  Sends an attacker payment (fake/replay/tamper) and broadcasts it.

---

## 📡 Real-time Events (Socket.IO)

**Server → Clients**
- `payment_result` — Sent to the sound box to display accepted/blocked result (+checks)
- `intercepted_payment` — Sent to attacker UI to populate captured transactions
- `attack_feedback` — Sent to attacker UI to show whether attack succeeded
- `security_mode_changed` — Updates the sound box toggle UI

**Client → Server**
- `toggle_security` — Sent from soundbox UI to enable/disable security mode

---

## 🛡️ Security Disclaimer

This repository is an **educational simulation** and **not** a real UPI/NPCI implementation.  
It demonstrates *concepts* (signatures, replay prevention, freshness checks, etc.) in a simplified way.

---

## 🧩 Troubleshooting

### `TemplateNotFound` error
Make sure your HTML pages are located at:
```
templates/index.html
templates/sender.html
templates/soundbox.html
templates/attacker.html
```

### Sound not speaking
Browsers often require a user interaction first. On Sound Box page:
- Click **Activate Sound Box**
- Ensure tab is not muted
- Try Chrome/Edge

### Socket not connecting
- Confirm you are opening the site using the same host/port shown by Flask
- Check console logs for blocked mixed content or network issues

---

## 📄 More Details
See **`PROJECT_WORKING.md`** for a deeper explanation of internal working, message formats, and how each attack is simulated.
