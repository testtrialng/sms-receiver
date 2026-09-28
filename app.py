from flask import Flask, request, jsonify
import os, json
from datetime import datetime

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "change_me_123")
LOG_FILE = "sms_log.json"

@app.route("/", methods=["GET"])
def home():
    return "SMS Receiver Server is Running ✅"

@app.route("/sms", methods=["POST"])
def receive_sms():
    try:
        key = request.headers.get("X-API-KEY", "")
        if key != API_KEY:
            return jsonify({"status": "error", "msg": "Unauthorized"}), 401

        data = request.get_json(force=True, silent=True) or {}
        data["_received_at"] = datetime.utcnow().isoformat()

        try:
            logs = []
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    logs = json.load(f)
            logs.append(data)
            with open(LOG_FILE, "w") as f:
                json.dump(logs[-500:], f, indent=2)
        except Exception as e:
            print("Log error:", e)

        print("📩 SMS RECEIVED:", data)
        return jsonify({"status": "ok", "data": data}), 200

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


@app.route("/logs", methods=["GET"])
def get_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify([])
    with open(LOG_FILE) as f:
        return jsonify(json.load(f))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
