import requests, os, sqlite3, time, random
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

con = sqlite3.connect("jobs.db")
con.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY)")
seen = {r[0] for r in con.execute("SELECT id FROM jobs")}
print(f"Seen {len(seen)} old")

KEYWORDS = ["3d visualizer", "architectural visualizer", "archviz"]
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

print("Searching LinkedIn Saudi KSA 🇸🇦...")
for kw in KEYWORDS:
    try:
        print(f" -> LinkedIn SA: {kw}")
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={kw.replace(' ', '%20')}&location=Saudi%20Arabia&start=0"
        resp = requests.get(url, headers=headers, timeout=20)
        print(f"LinkedIn status {resp.status_code} len {len(resp.text)}")

        if resp.status_code == 429:
            print("Got 429, sleeping 30s...")
            time.sleep(30)
            resp = requests.get(url, headers=headers, timeout=20)

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")
        print(f"Found {len(cards)} cards")
        for card in cards[:7]:
            link_tag = card.find("a", class_="base-card__full-link")
            if not link_tag: continue
            link = link_tag.get("href","").split("?")[0]
            jid = link.split("/")[-2] if link else ""
            if not jid or jid in seen: continue
            title_tag = card.find("h3", class_="base-search-card__title")
            title = title_tag.text.strip() if title_tag else kw
            comp_tag = card.find("h4", class_="base-search-card__subtitle")
            company = comp_tag.text.strip() if comp_tag else ""

            send(f"🇸🇦 *{title}*\n🏢 {company}\n📍 Saudi Arabia\n🔗 {link}\n🔍 {kw}")
            con.execute("INSERT OR IGNORE INTO jobs VALUES (?)", (jid,))
            con.commit()
            seen.add(jid)
            time.sleep(2)

        # نوم بين الكلمات عشان ما يحظرنا
        sleep_time = random.randint(10, 20)
        print(f"Sleeping {sleep_time}s before next keyword...")
        time.sleep(sleep_time)

    except Exception as e:
        print(f"LinkedIn error {kw}: {e}")
        continue

print("Done Saudi KSA!")
