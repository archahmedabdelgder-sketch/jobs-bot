import requests, os, sqlite3, time
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        print(f"Sent: {text[:40]}")
    except Exception as e:
        print(f"Send failed: {e}")

con = sqlite3.connect("jobs.db")
con.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY)")
seen = {r[0] for r in con.execute("SELECT id FROM jobs")}
print(f"Seen {len(seen)} old")

KEYWORDS = ["3d visualizer", "architectural visualizer", "archviz", "3d artist"]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8"
}

# 1- Indeed Saudi Arabia - شغال 100% 🇸🇦
print("Searching Indeed Saudi...")
for kw in KEYWORDS[:2]:
    try:
        q = kw.replace(" ", "+")
        url = f"https://sa.indeed.com/jobs?q={q}&l=Saudi+Arabia"
        print(f" -> Indeed SA: {kw}")
        resp = requests.get(url, headers=headers, timeout=25)
        print(f"Indeed status {resp.status_code} len {len(resp.text)}")
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="job_seen_beacon")
        if not cards:
            cards = soup.find_all("a", class_="tapItem")
        print(f"Found {len(cards)} indeed cards")
        for card in cards[:5]:
            title_tag = card.find("h2", class_="jobTitle")
            if not title_tag: continue
            title = title_tag.get_text(strip=True)
            link_tag = card.find("a", href=True)
            link = link_tag["href"] if link_tag else ""
            if not link.startswith("http"):
                link = "https://sa.indeed.com" + link
            jid = link.split("jk=")[-1][:50] if "jk=" in link else link[:100]
            if jid in seen: continue
            if any(x in title.lower() for x in ["3d", "visual", "arch", "render", "artist"]):
                send(f"🇸🇦 *{title}* - Indeed KSA\n🔗 {link}\n🔍 {kw}")
                con.execute("INSERT OR IGNORE INTO jobs VALUES (?)", (jid,))
                con.commit()
                seen.add(jid)
                time.sleep(1)
    except Exception as e:
        print(f"Indeed error {kw}: {e}")

# 2- LinkedIn Saudi بدون فلتر يوم واحد 🇸🇦
print("Searching LinkedIn Saudi v2...")
for kw in KEYWORDS[:2]:
    try:
        print(f" -> LinkedIn SA: {kw}")
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={kw.replace(' ', '%20')}&location=Saudi%20Arabia&start=0"
        resp = requests.get(url, headers=headers, timeout=20)
        print(f"LinkedIn status {resp.status_code} len {len(resp.text)}")
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")
        print(f"Found {len(cards)} linkedin cards")
        for card in cards[:5]:
            link_tag = card.find("a", class_="base-card__full-link")
            if not link_tag: continue
            link = link_tag.get("href","").split("?")[0]
            jid = link.split("/")[-2] if link else ""
            if not jid or jid in seen: continue
            title_tag = card.find("h3", class_="base-search-card__title")
            title = title_tag.text.strip() if title_tag else kw
            send(f"🇸🇦 *{title}* - LinkedIn KSA\n📍 Saudi Arabia\n🔗 {link}\n🔍 {kw}")
            con.execute("INSERT OR IGNORE INTO jobs VALUES (?)", (jid,))
            con.commit()
            seen.add(jid)
            time.sleep(2)
    except Exception as e:
        print(f"LinkedIn error {kw}: {e}")

print("Done Saudi!")
