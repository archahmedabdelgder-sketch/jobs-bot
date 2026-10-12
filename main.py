import requests, os
from bs4 import BeautifulSoup

KEYWORDS = ["3d visualizer", "architectural visualizer", "archviz", "3d artist", "v-ray"]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def get_remotive():
    jobs=[]
    try:
        data=requests.get("https://remotive.com/api/remote-jobs?limit=100").json()
        for j in data['jobs']:
            if any(k in j['title'].lower() for k in KEYWORDS):
                jobs.append(f"💼 {j['title']}\n🏢 {j['company_name']}\n🔗 {j['url']}")
    except: pass
    return jobs

def get_linkedin():
    jobs=[]
    headers={"User-Agent":"Mozilla/5.0"}
    for kw in ["3d visualizer", "architectural visualizer"]:
        try:
            url=f"https://www.linkedin.com/jobs/search/?keywords={kw}&location=Worldwide&f_WT=2"
            r=requests.get(url, headers=headers, timeout=15)
            soup=BeautifulSoup(r.text,'html.parser')
            for card in soup.select('.base-card')[:5]:
                t=card.select_one('.base-search-card__title')
                l=card.select_one('.base-card__full-link')
                if t and l:
                    jobs.append(f"💼 {t.text.strip()} - LinkedIn 🌚\n🔗 {l['href']}")
        except: pass
    return jobs

all_jobs=get_remotive()+get_linkedin()
if not all_jobs:
    send("🔍 مافي وظائف 3D جديدة اليوم، حافتش بعد 6 ساعات")
else:
    for job in all_jobs[:10]:
        send(job)
