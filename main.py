import requests

TOKEN = "8746919756:AAFUtrn6XdP0B5ZbUlA7iA4azr7zAjHLEi0"
CHAT_ID = "5921311298"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=data)

def get_jobs():
    # نجيب وظائف ريموت
    try:
        r = requests.get("https://remotive.com/api/remote-jobs?limit=5").json()
        return r['jobs'][:5]
    except:
        return []

jobs = get_jobs()
if not jobs:
    send_msg("البوت شغال ✅ لكن مافي وظائف هسه، حأجرب تاني بعد 6 ساعات")
else:
    for job in jobs:
        msg = f"💼 *{job['title']}*\n🏢 {job['company_name']}\n📍 {job['candidate_required_location']}\n\n🔗 {job['url']}"
        send_msg(msg)

print("Done")
