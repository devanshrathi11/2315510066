from flask import Flask, jsonify, request
import requests

# Simple import because logger.py is in the exact same folder!
from logger import Log

app = Flask(__name__)

# Your active token is already pasted here
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJkZXZhbnNoLnJhdGhpX2NzLmFpbWwyM0BnbGEuYWMuaW4iLCJleHAiOjE3ODEwNzk1ODcsImlhdCI6MTc4MTA3ODY4NywiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6IjY5NDEwNzlmLTIxMTMtNDNhOC1hZDY5LTM0NmFlNGNhMWYxMSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6ImRldmFuc2ggcmF0aGkiLCJzdWIiOiI1NGI0YTRlMi0yMzFmLTRhNWYtOTFhOC1mY2Y3Nzc1OGZmMDgifSwiZW1haWwiOiJkZXZhbnNoLnJhdGhpX2NzLmFpbWwyM0BnbGEuYWMuaW4iLCJuYW1lIjoiZGV2YW5zaCByYXRoaSIsInJvbGxObyI6IjIzMTU1MTAwNjYiLCJhY2Nlc3NDb2RlIjoiUlBzZ1l0IiwiY2xpZW50SUQiOiI1NGI0YTRlMi0yMzFmLTRhNWYtOTFhOC1mY2Y3Nzc1OGZmMDgiLCJjbGllbnRTZWNyZXQiOiJ3SE1VSkRjSEJnaGhHYmZ0In0.NPt8OhuflH7FSO7ENRWFzXqb5FO7nmQ2AFDls3FuYQo"
DEPOTS_URL = "http://4.224.186.213/evaluation-service/depots"
VEHICLES_URL = "http://4.224.186.213/evaluation-service/vehicles"

def fetch_protected_data(url, data_key):
    Log("backend", "info", "controller", f"Initiating data fetch from {url}")
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            Log("backend", "info", "controller", f"Successfully parsed data key: {data_key}")
            return response.json().get(data_key, [])
        return []
    except Exception as e:
        Log("backend", "fatal", "controller", f"Network exception: {str(e)}")
        return []

def solve_knapsack(vehicles, max_hours):
    Log("backend", "debug", "controller", f"Starting knapsack optimization for capacity: {max_hours}")
    n = len(vehicles)
    dp = [[0] * (max_hours + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        duration = vehicles[i-1]["Duration"]
        impact = vehicles[i-1]["Impact"]
        for w in range(max_hours + 1):
            if duration <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w - duration] + impact)
            else:
                dp[i][w] = dp[i-1][w]
    selected = []
    w = max_hours
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            selected.append(vehicles[i-1])
            w -= vehicles[i-1]["Duration"]
    return selected, dp[n][max_hours]

@app.route('/api/schedule', methods=['POST'])
def run_scheduler():
    Log("backend", "info", "controller", "API /api/schedule called.")
    depots = fetch_protected_data(DEPOTS_URL, "depots")
    vehicles = fetch_protected_data(VEHICLES_URL, "vehicles")
    
    if not depots or not vehicles:
        return jsonify({"error": "Failed to fetch data from test server"}), 500

    results = []
    for depot in depots:
        selected, total_impact = solve_knapsack(vehicles, depot["MechanicHours"])
        results.append({
            "depot_id": depot["ID"],
            "max_hours": depot["MechanicHours"],
            "calculated_impact": total_impact,
            "scheduled_vehicles": selected
        })
        
    return jsonify({
        "message": "Optimization Complete",
        "data": results
    }), 200

if __name__ == "__main__":
    print("Scheduler API running on http://127.0.0.1:5001")
    app.run(port=5001)