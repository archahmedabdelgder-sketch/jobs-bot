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

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 1- LinkedIn السعودية فقط 🇸🇦
print("Searching LinkedIn Saudi Arabia...")
for kw in KEYWORDS[:3]:
    try:
        print(f" -> LinkedIn SA: {kw}")
        # location = Saudi Arabia
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={kw.replace(' ', '%20')}&location=Saudi%20Arabia&f_TPR=r86400&start=0"
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")
        print(f"Found {len(cards)} cards")
        for card in cards[:6]:
            link_tag = card.find("a", class_="base-card__full-link")
            if not link_tag: continue
            link = link_tag.get("href", "").split("?")[0]
            jid = link.split("/")[-2] if link else ""
            if not jid or jid in seen: continue

            title_tag = card.find("h3", class_="base-search-card__title")
            title = title_tag.text.strip() if title_tag else kw
            loc_tag = card.find("span", class_="job-search-card__location")
            location = loc_tag.text.strip() if loc_tag else "Saudi Arabia"

            # فلتر سعودية فقط
            if "saudi" in location.lower() or "riyadh" in location.lower() or "jeddah" in location.lower() or "ksa" in location.lower() or "dammam" in location.lower() or location.strip() == "Saudi Arabia":
                send(f"🇸🇦 *{title}*\n📍 {location}\n🔗 {link}\n🔍 {kw}\n#LinkedIn_KSA")
                con.execute("INSERT INTO jobs VALUES (?)", (jid,))
                con.commit()
                seen.add(jid)
                time.sleep(2)
    except Exception as e:
        print(f"LinkedIn SA error {kw}: {e}")
        continue

# 2- Naukrigulf السعودية 🇸🇦
print("Searching Naukrigulf Saudi...")
for kw in KEYWORDS[:3]:
    try:
        print(f" -> Naukrigulf: {kw}")
        q = kw.replace(" ", "-")
        url = f"https://www.naukrigulf.com/{q}-jobs-in-saudi-arabia"
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("a", class_="info-position")
        print(f"Found {len(cards)} Naukri cards")
        for card in cards[:6]:
            title = card.text.strip()
            link = "https://www.naukrigulf.com" + card.get("href", "")
            jid = link
            if jid in seen or not title: continue

            if any(x in title.lower() for x in ["3d", "visual", "archviz", "artist", "render", "architect"]):
                send(f"🇸🇦 *{title}* - Naukrigulf\n🔗 {link}\n🔍 {kw}\n#Naukrigulf_KSA")
                con.execute("INSERT INTO jobs VALUES (?)", (jid,))
                con.commit()
                seen.add(jid)
                time.sleep(2)
    except Exception as e:
        print(f"Naukrigulf error {kw}: {e}")
        continue

print("Done Saudi Only!")
