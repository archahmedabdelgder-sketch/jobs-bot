import requests, os, sqlite3, time, random
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        print(f"Sent: {text[:60]}")
    except Exception as e:
        print(f"Send failed: {e}")

con = sqlite3.connect("jobs.db")
con.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY)")
seen = {r[0] for r in con.execute("SELECT id FROM jobs")}

# كلمات سعودية دقيقة فقط
KEYWORDS = ["architectural visualizer", "archviz", "3d architectural visualizer"]
BAD_WORDS = ["graphic", "logo", "ui", "ux", "motion", "video", "social media", "fashion"]
GOOD_WORDS = ["arch", "viz", "visualizer", "interior", "exterior", "3ds", "render"]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

print("Searching LinkedIn Saudi ARCH only 🇸🇦...")
for kw in KEYWORDS:
    try:
        print(f" -> {kw}")
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={kw.replace(' ', '%20')}&location=Saudi%20Arabia&start=0"
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 429:
            print("429 sleep 40s")
            time.sleep(40)
            resp = requests.get(url, headers=headers, timeout=20)

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")
        print(f"Found {len(cards)}")
        for card in cards[:8]:
            link_tag = card.find("a", class_="base-card__full-link")
            if not link_tag: continue
            link = link_tag.get("href","").split("?")[0]
            jid = link.split("/")[-2] if link else ""
            if not jid or jid in seen: continue
            title_tag = card.find("h3", class_="base-search-card__title")
            title = title_tag.text.strip() if title_tag else ""
            title_lower = title.lower()

            # فلتر مشدد
            if any(b in title_lower for b in BAD_WORDS):
                print(f"Skip BAD: {title}")
                continue
            if not any(g in title_lower for g in GOOD_WORDS):
                print(f"Skip NOT ARCH: {title}")
                continue

            comp_tag = card.find("h4", class_="base-search-card__subtitle")
            company = comp_tag.text.strip() if comp_tag else ""
            send(f"🇸🇦 *{title}*\n🏢 {company}\n📍 KSA\n🔗 {link}")
            con.execute("INSERT OR IGNORE INTO jobs VALUES (?)", (jid,))
            con.commit()
            seen.add(jid)
            time.sleep(2)
        time.sleep(random.randint(15,25))
    except Exception as e:
        print(f"Error {kw}: {e}")

print("Done ARCH only!")
