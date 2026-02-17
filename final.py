from flask import Flask, render_template_string, request
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Store transactions
payment_history = []

# =========================
# SENDER PAGE
# =========================

SENDER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>UPI Sender Panel</title>
</head>
<body style="font-family: Arial; text-align:center; margin-top:50px; background:#f5f5f5;">

<h2>💻 UPI Payment Sender</h2>

<form method="POST">
    Amount:<br>
    <input type="number" name="amount" required><br><br>

    Sender Name:<br>
    <input type="text" name="name" required><br><br>

    UPI App:<br>
    <select name="app">
        <option>Google Pay</option>
        <option>PhonePe</option>
        <option>Paytm</option>
    </select><br><br>

    <button type="submit">Send Payment</button>
</form>

<p style="color:green;">Payments will be broadcast to listener devices.</p>

</body>
</html>
"""

# =========================
# LISTENER PAGE
# =========================

LISTENER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>UPI Listener Dashboard</title>
    <script src="https://cdn.socket.io/4.3.2/socket.io.min.js"></script>
</head>

<body style="font-family: Arial; background:#f5f5f5; margin:30px;">

<h2 style="text-align:center;">📱 UPI Sound Box Dashboard</h2>

<div style="text-align:center;">
<button onclick="unlock()" style="padding:8px 15px;">
Activate Sound 🔊
</button>
<p id="status" style="color:green;"></p>
</div>

<hr>

<h3>📜 Transaction History</h3>
<div id="history" style="background:white; padding:15px; border-radius:8px; max-height:400px; overflow-y:auto;"></div>

<script>
var socket = io();
var unlocked = false;

function unlock() {
    var msg = new SpeechSynthesisUtterance("Sound box connected");
    window.speechSynthesis.speak(msg);
    unlocked = true;
    document.getElementById("status").innerHTML = "Sound Activated ✅";
}

// Load previous history
socket.on('load_history', function(data) {
    document.getElementById("history").innerHTML = "";
    data.forEach(function(txn) {
        addTransaction(txn);
    });
});

// New payment event
socket.on('payment', function(data) {

    addTransaction(data);

    if (!unlocked) return;

    var message = `Rupees ${data.amount} received from ${data.name} via ${data.app}`;

    window.speechSynthesis.cancel();
    var speech = new SpeechSynthesisUtterance(message);
    window.speechSynthesis.speak(speech);
});

// Add entry to UI
function addTransaction(data) {
    var historyDiv = document.getElementById("history");

    var entry = document.createElement("div");
    entry.style.padding = "8px";
    entry.style.borderBottom = "1px solid #ddd";
    entry.innerHTML = `
        <strong>₹${data.amount}</strong> from ${data.name} via ${data.app}
        <br><small>${data.time}</small>
    `;

    historyDiv.prepend(entry);
}
</script>

</body>
</html>
"""

# =========================
# ROUTES
# =========================

@app.route("/sender", methods=["GET", "POST"])
def sender():
    if request.method == "POST":
        amount = request.form["amount"]
        name = request.form["name"]
        app_name = request.form["app"]

        txn = {
            "amount": amount,
            "name": name,
            "app": app_name,
            "time": datetime.now().strftime("%H:%M:%S")
        }

        payment_history.append(txn)

        socketio.emit("payment", txn)

    return render_template_string(SENDER_HTML)


@app.route("/listener")
def listener():
    return render_template_string(LISTENER_HTML)


# Send full history on connect
@socketio.on('connect')
def handle_connect():
    socketio.emit("load_history", payment_history)


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
