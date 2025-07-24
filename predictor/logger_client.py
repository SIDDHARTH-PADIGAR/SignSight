# predictor/logger_client.py
import requests
from datetime import datetime

def send_log(user_id, target_letter, predicted_letter, correct):
    url = "http://localhost:8080/log"
    data = {
        "user_id": user_id,
        "target_letter": target_letter,
        "predicted_letter": predicted_letter,
        "correct": correct,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("[LOG SUCCESS]")
        else:
            print(f"[LOG FAILED] {response.status_code} {response.text}")
    except Exception as e:
        print(f"[LOG ERROR] {e}")
