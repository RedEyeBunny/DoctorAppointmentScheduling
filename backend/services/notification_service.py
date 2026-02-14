import requests
from backend.config import SLACK_WEBHOOK

def send_slack_message(text):
    if not SLACK_WEBHOOK:
        print("Slack webhook not configured. Skipping notification.")
        return

    try:
        requests.post(SLACK_WEBHOOK, json={"text": text})
    except Exception as e:
        print("Slack notification failed:", e)