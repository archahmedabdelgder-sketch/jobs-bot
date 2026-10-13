import os, json, requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

print("Scoring started")

try:
    with open("jobs_today.json", "r", encoding="utf-8") as f:
        jobs = json.load(f)
except:
    jobs = []

MY = ["3ds max", "v-ray", "corona", "revit", "lumion"]
BAD = ["graphic", "logo", "social media", "video"]

count = 0
for job in jobs:
    title = job.get("title","").lower()
    if any(b in title for b in BAD):
        continue
    score = 60
    if "3ds max" in title:
        score += 20
    if "v-ray" in title:
        score += 15
    if "visualizer" in title:
        score += 10
    if score >= 75:
        count += 1
        send(f"SCORE {score}% \n {job.get('title')} \n {job.get('link')}")

print(f"Done - {count} jobs")
