import requests, os, sqlite3, time
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        print(f"Sent: {text[:50]}")
    except Exception as e:
        print(f"Send failed: {e}")

# ذاكرة عشان ما يكرر
con = sqlite3.connect("jobs.db")
con.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY)")
seen = {r[0] for r in con.execute("SELECT id FROM jobs")}
print(f"Seen {len(seen)} old jobs")

KEYWORDS = [
    "3d architectural visualizer",
    "architectural visualizer",
    "archviz",
    "3d visualizer",
    "3d artist"
]

# 1- Remotive
print("Searching Remotive...")
for kw in KEYWORDS:
    try:
        print(f" -> Remotive: {kw}")
        data = requests.get(f"https://remotive.com/api/remote-jobs?search={kw}", timeout=15).json()
        for j in data['jobs'][:5]:
            jid = str(j['id'])
            if jid not in seen:
                title = j['title']
                # فلتر بسيط عشان يجيب شغل ثري دي بس
                if any(x in title.lower() for x in ["3d", "visual", "archviz", "artist", "blender", "3ds", "render"]):
                    link = j['url']
                    send(f"💼 *{title}* - Remotive\n{link}\nKeyword: {kw}")
                    con.execute("INSERT INTO jobs VALUES (?)", (jid,))
                    con.commit()
                    seen.add(jid)
                    time.sleep(1)
    except Exception as e:
        print(f"Remotive error {kw}: {e}")
        continue

# 2- LinkedIn Guest
print("Searching LinkedIn...")
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
for kw in KEYWORDS[:3]: # اول 3 كلمات عشان ما يحظرنا
    try:
        print(f" -> LinkedIn: {kw}")
        # LinkedIn remote jobs
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={kw.replace(' ', '%20')}&location=Remote&f_WT=2&start=0"
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")
        print(f"Found {len(cards)} cards for {kw}")
        for card in cards[:5]:
            link_tag = card.find("a", class_="base-card__full-link")
            if not link_tag: continue
            link = link_tag.get("href", "").split("?")[0]
            jid = link.split("/")[-1] if link else ""
            if not jid or jid in seen: continue

            title_tag = card.find("h3", class_="base-search-card__title")
            title = title_tag.text.strip() if title_tag else kw

            send(f"💼 *{title}* - LinkedIn 🌚\n{link}\nKeyword: {kw}")
            con.execute("INSERT INTO jobs VALUES (?)", (jid,))
            con.commit()
            seen.add(jid)
            time.sleep(2)
    except Exception as e:
        print(f"LinkedIn error {kw}: {e}")
        continue

print("Done!")
