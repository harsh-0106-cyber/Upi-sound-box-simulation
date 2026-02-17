# 📘 Software Requirements Specification (SRS)

# PayEcho  
### A Real-Time WebSocket-Based UPI Sound Box Simulation System

---

## 1. Introduction

### 1.1 Purpose

This document describes the Software Requirements Specification (SRS) for **PayEcho**, a real-time UPI Sound Box Simulation System.

The purpose of this project is to demonstrate how merchant-side digital payment notification systems function using real-time communication and voice announcements in a controlled educational environment.

⚠️ This system is strictly for academic demonstration purposes.  
It does NOT connect to real UPI systems, banks, or payment gateways.

---

### 1.2 Scope

PayEcho is a LAN-based web application that simulates the working of a UPI merchant sound box.

The system:

- Allows a user (Sender) to simulate a payment.
- Broadcasts payment events in real-time using WebSocket.
- Enables listener devices to:
  - Hear a voice announcement.
  - View transaction history.
- Operates across multiple devices connected to the same WiFi network.

The system does NOT:

- Process real financial transactions.
- Store permanent financial data.
- Connect to any external API.

---

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Meaning |
|------|---------|
| UPI | Unified Payments Interface |
| LAN | Local Area Network |
| WebSocket | Real-time bidirectional communication protocol |
| TTS | Text-to-Speech |
| POS | Point of Sale |
| API | Application Programming Interface |

---

### 1.4 Overview

PayEcho consists of:

- Sender Module (Laptop)
- Listener Module (Tablet/Secondary Device)
- Backend Server (Flask + SocketIO)

The Listener device receives real-time payment events and generates voice announcements using browser-based Speech Synthesis.

---

## 2. Overall Description

### 2.1 Product Perspective

PayEcho is a standalone client-server web application operating within a Local Area Network (LAN).

---

### 📌 Architecture Overview

Sender (Laptop)  
↓  
Flask + SocketIO Server  
↓  
Listener Devices (Tablet)  
↓  
Voice Announcement + Transaction Log  

---

### 2.2 Product Functions

The system performs the following major functions:

1. Accept simulated payment input (Amount, Sender Name, UPI App).
2. Broadcast payment events in real-time via WebSocket.
3. Generate voice announcements on listener devices.
4. Display real-time transaction history.
5. Load existing transaction history when a new listener connects.
6. Maintain temporary in-memory transaction storage during runtime.

---

### 2.3 User Classes and Characteristics

#### Sender User
- Operates from laptop or desktop.
- Inputs payment simulation details.
- Basic computer literacy required.

#### Listener User
- Operates from tablet or secondary device.
- Activates sound manually.
- Monitors payment announcements.

---

### 2.4 Operating Environment

- Programming Language: Python 3.x
- Backend Framework: Flask, Flask-SocketIO
- Frontend: HTML, JavaScript
- Browser: Chrome / Brave / Edge
- Network: Same WiFi LAN
- OS: Windows / Linux / macOS

---

### 2.5 Design Constraints

- Must operate within Local Area Network.
- No external internet dependency required.
- Browser autoplay restrictions require manual sound activation.
- Transaction storage is temporary (in-memory only).

---

### 2.6 Assumptions and Dependencies

- All devices are connected to the same network.
- Browser supports WebSocket and SpeechSynthesis API.
- Server machine remains active during operation.

---

## 3. Specific Requirements

---

### 3.1 Functional Requirements

#### FR1: Payment Input
The system shall allow the sender to input:
- Amount
- Sender Name
- UPI App

#### FR2: Real-Time Broadcast
The system shall broadcast payment events to all connected listener devices using WebSocket.

#### FR3: Voice Announcement
The listener shall generate a TTS voice announcement upon receiving a payment event.

#### FR4: Manual Sound Activation
The listener shall require user interaction to activate sound functionality due to browser security policies.

#### FR5: Transaction Logging
The system shall maintain a list of all simulated payments during runtime.

#### FR6: Auto History Loading
The system shall send complete transaction history to newly connected listener devices.

#### FR7: Multi-Device Support
The system shall support multiple listener devices simultaneously.

---

### 3.2 Non-Functional Requirements

#### NFR1: Performance
Payment announcements shall be delivered within 1 second of submission.

#### NFR2: Reliability
The system shall operate reliably within LAN without internet dependency.

#### NFR3: Usability
The user interface shall be simple and intuitive.

#### NFR4: Security
The system shall not connect to real financial APIs.
The system shall operate only within local network.

#### NFR5: Maintainability
The codebase shall follow modular architecture and readable structure.

---

### 3.3 Interface Requirements

#### User Interface
- Web-based interface accessible through browser.
- Separate routes:
  - `/sender`
  - `/listener`

#### Hardware Interface
- Laptop/Desktop (Sender)
- Tablet/Mobile (Listener)

#### Software Interface
- Flask framework
- Flask-SocketIO
- Browser Speech Synthesis API

#### Communication Interface
- WebSocket over LAN (Port 5000)

---

## 4. System Features

### Feature 1: Payment Simulation
The sender inputs payment details and submits the form.

### Feature 2: Real-Time Event Broadcasting
The backend emits payment event to all connected devices.

### Feature 3: Audio Notification
The listener converts payment message into speech using TTS.

### Feature 4: Live Transaction Dashboard
The listener displays payment entries with timestamp.

---

## 5. Future Enhancements

- Convert amount to words (₹450 → Four Hundred Fifty)
- Add notification tone before speech
- Add daily total calculation
- Add CSV export
- Add authentication module
- Add database persistence (SQLite / MySQL)
- Add mobile app version

---

## 6. Conclusion

PayEcho is a real-time, LAN-based UPI sound box simulation system designed for educational demonstration of event-driven communication and voice notification systems.

It demonstrates:

- Client-server architecture
- WebSocket real-time communication
- Multi-device broadcasting
- Browser-based speech synthesis
- Live transaction logging

The system remains completely safe, isolated, and independent of real financial infrastructure.

---

© 2026 PayEcho Project

