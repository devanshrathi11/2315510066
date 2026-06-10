from flask import Flask, jsonify, request
from datetime import datetime
import requests

# Simple import because logger.py is in the exact same folder!
from logger import Log

app = Flask(__name__)

# Your active token is already pasted here
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJkZXZhbnNoLnJhdGhpX2NzLmFpbWwyM0BnbGEuYWMuaW4iLCJleHAiOjE3ODEwNzk1ODcsImlhdCI6MTc4MTA3ODY4NywiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6IjY5NDEwNzlmLTIxMTMtNDNhOC1hZDY5LTM0NmFlNGNhMWYxMSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6ImRldmFuc2ggcmF0aGkiLCJzdWIiOiI1NGI0YTRlMi0yMzFmLTRhNWYtOTFhOC1mY2Y3Nzc1OGZmMDgifSwiZW1haWwiOiJkZXZhbnNoLnJhdGhpX2NzLmFpbWwyM0BnbGEuYWMuaW4iLCJuYW1lIjoiZGV2YW5zaCByYXRoaSIsInJvbGxObyI6IjIzMTU1MTAwNjYiLCJhY2Nlc3NDb2RlIjoiUlBzZ1l0IiwiY2xpZW50SUQiOiI1NGI0YTRlMi0yMzFmLTRhNWYtOTFhOC1mY2Y3Nzc1OGZmMDgiLCJjbGllbnRTZWNyZXQiOiJ3SE1VSkRjSEJnaGhHYmZ0In0.NPt8OhuflH7FSO7ENRWFzXqb5FO7nmQ2AFDls3FuYQo"
NOTIFICATIONS_URL = "http://4.224.186.213/evaluation-service/notifications"

def get_priority_weight(notif_type):
    Log("backend", "debug", "controller", f"Calculating weight for: {notif_type}")
    notif_type = notif_type.strip().lower()
    if notif_type == "placement": return 3
    elif notif_type == "result": return 2
    elif notif_type == "event": return 1
    return 0

def fetch_notifications():
    Log("backend", "info", "controller", "Fetching notifications.")
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    try:
        response = requests.get(NOTIFICATIONS_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("notifications", [])
        return []
    except Exception as e:
        Log("backend", "fatal", "controller", f"Network exception: {str(e)}")
        return []

def get_top_notifications(notifications, n=10):
    def sorting_key(notif):
        weight = get_priority_weight(notif.get("Type", ""))
        try:
            time_obj = datetime.strptime(notif.get("Timestamp", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            time_obj = datetime.min
        return (weight, time_obj)
    return sorted(notifications, key=sorting_key, reverse=True)[:n]

@app.route('/api/inbox', methods=['POST'])
def get_inbox():
    Log("backend", "info", "controller", "API /api/inbox called.")
    notifications = fetch_notifications()
    
    if not notifications:
        return jsonify({"error": "No notifications found"}), 404

    top_10 = get_top_notifications(notifications, n=10)
    
    return jsonify({
        "message": "Priority Inbox Sorted",
        "top_10_notifications": top_10
    }), 200

if __name__ == "__main__":
    print("Inbox API running on http://127.0.0.1:5002")
    app.run(port=5002)