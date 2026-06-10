import requests

# Your active token is already pasted here
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJkZXZhbnNoLnJhdGhpX2NzLmFpbWwyM0BnbGEuYWMuaW4iLCJleHAiOjE3ODEwNzcwODEsImlhdCI6MTc4MTA3NjE4MSwiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6IjAzNDYwNTZhLTdhZjUtNDdmZC1hNWI3LTY3YzVhNmViMGZhYSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6ImRldmFuc2ggcmF0aGkiLCJzdWIiOiI1NGI0YTRlMi0yMzFmLTRhNWYtOTFhOC1mY2Y3Nzc1OGZmMDgifSwiZW1haWwiOiJkZXZhbnNoLnJhdGhpX2NzLmFpbWwyM0BnbGEuYWMuaW4iLCJuYW1lIjoiZGV2YW5zaCByYXRoaSIsInJvbGxObyI6IjIzMTU1MTAwNjYiLCJhY2Nlc3NDb2RlIjoiUlBzZ1l0IiwiY2xpZW50SUQiOiI1NGI0YTRlMi0yMzFmLTRhNWYtOTFhOC1mY2Y3Nzc1OGZmMDgiLCJjbGllbnRTZWNyZXQiOiJ3SE1VSkRjSEJnaGhHYmZ0In0.S5-DA8Tjxh5BIhxT_sDxVDDQfIMHRdcF3TsciOjqNZs"
LOG_URL = "http://4.224.186.213/evaluation-service/logs"

def Log(stack, level, package, message):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Strictly enforcing lowercase for the constraints
    payload = {
        "stack": stack.lower(),
        "level": level.lower(),
        "package": package.lower(),
        "message": message
    }
    try:
        requests.post(LOG_URL, json=payload, headers=headers, timeout=5)
    except Exception:
        pass