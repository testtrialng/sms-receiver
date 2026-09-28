from flask import Flask, request, jsonify
import os, json, urllib.request, urllib.parse
from datetime import datetime

app = Flask(__name__)

# ========================================
# 🔴 কনফিগারেশন
# ========================================
API_KEY    = os.environ.get("API_KEY", "mySecretKey_12345")
BOT_TOKEN  = "8988458629:AAG_soF532b0l2xarRnfxwm7GGsVYzQ-rEU"
CHAT_ID    = "5971752529"
LOG_FILE   = "sms_log.json"


# ========================================
# 🔔 Telegram এ message পাঠানোর helper
# ========================================
def send_telegram(message):
    try:
        url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }).encode("utf-8")

        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("✅ Telegram sent:", resp.status)
            return True
    except Exception as e:
        print("❌ Telegram error:", e)
        return False


# ========================================
# 🏠 Home
# ========================================
@app.route("/", methods=["GET"])
def home():
    return "SMS Receiver Server is Running ✅"


# ========================================
# 📩 SMS Receive Endpoint
# ========================================
@app.route("/sms", methods=["POST"])
def receive_sms():
    try:
        # API key check
        key = request.headers.get("X-API-KEY", "")
        if key != API_KEY:
            return jsonify({"status": "error", "msg": "Unauthorized"}), 401

        data = request.get_json(force=True, silent=True) or {}
        data["_received_at"] = datetime.utcnow().isoformat()

        # Log to file
        try:
            logs = []
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    logs = json.load(f)
            logs.append(data)
            with open(LOG_FILE, "w") as f:
                json.dump(logs[-500:], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Log error:", e)

        # Console log
        print("📩 SMS RECEIVED:", data)

        # ========================================
        # 🔔 Telegram Bot এ Message Format করে পাঠান
        # ========================================
        sms_type = data.get("type", "unknown")
        sender   = data.get("sender", "")
        raw      = data.get("raw", "")
        time_str = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

        # Message format
        if sms_type == "bKash":
            emoji = "💗"
            title = "bKash"
        elif sms_type == "Nagad":
            emoji = "🟠"
            title = "Nagad"
        elif sms_type == "Rocket":
            emoji = "🚀"
            title = "Rocket"
        else:
            emoji = "📨"
            title = "Unknown"

        message = (
            f"{emoji} <b>{title} SMS Received</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>Sender ID:</b> <code>{sender}</code>\n"
            f"⏰ <b>Time:</b> {time_str}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📄 <b>Message:</b>\n"
            f"<code>{raw}</code>"
        )

        send_telegram(message)

        return jsonify({"status": "ok", "data": data}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "msg": str(e)}), 500


# ========================================
# 📜 Logs দেখার endpoint
# ========================================
@app.route("/logs", methods=["GET"])
def get_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify([])
    with open(LOG_FILE) as f:
        return jsonify(json.load(f))


# ========================================
# 🤖 Telegram Test endpoint (manual trigger)
# ========================================
@app.route("/test-telegram", methods=["GET"])
def test_telegram():
    ok = send_telegram("✅ Test message from SMS Receiver Server!")
    return jsonify({"status": "ok" if ok else "error"})


# ========================================
# 🚀 Run
# ========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
