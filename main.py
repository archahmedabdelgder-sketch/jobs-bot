import requests, os, sqlite3, time
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except: pass

# ذاكرة عشان ما يكرر
con = sqlite3.connect("jobs.db")
con.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY)")
seen = {r[0] for r in con.execute("SELECT id FROM jobs")}

# 1- Remotive
try:
    data=requests.get("https://remotive.com/api/remote-jobs?search=3d", timeout=20).json()
    for j in data['jobs'][:5]:
        jid=str(j['id'])
        if jid not in seen:
            send(f"💼 {j['title']} - Remotive\n🏢 {j['company_name']}\n🔗 {j['url']}")
            con.execute("INSERT INTO jobs VALUES (?)",(jid,))
            seen.add(jid)
            time.sleep(1)
except: pass

# 2- LinkedIn 🌚
try:
    headers={"User-Agent":"Mozilla/5.0"}
    url="https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=3D%20Visualizer&location=Worldwide&f_WT=2&start=0"
    html=requests.get(url, headers=headers, timeout=20).text
    soup=BeautifulSoup(html, "lxml")
    for li in soup.find_all("li")[:10]:
        a=li.find("a", class_="base-card__full-link")
        h=li.find("h3", class_="base-search-card__title")
        if not a or not h: continue
        link=a['href'].split("?")[0]
        if link not in seen:
            title=h.get_text(strip=True)
            send(f"💼 {title} - LinkedIn 🌚\n🔗 {link}")
            con.execute("INSERT INTO jobs VALUES (?)",(link,))
            seen.add(link)
            time.sleep(1)
except Exception as e:
    print(e)

con.commit()
