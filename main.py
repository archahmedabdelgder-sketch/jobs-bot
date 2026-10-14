import requests, os, sqlite3, time, random
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("No TOKEN/CHAT_ID")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=20)
        print(f"Sent: {r.status_code} - {text[:60]}")
        return r.status_code == 200
    except Exception as e:
        print(f"Send failed: {e}")
        return False

# --- الذاكرة ---
con = sqlite3.connect("jobs.db")
con.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY)")
seen = {r[0] for r in con.execute("SELECT id FROM jobs")}
print(f"Memory loaded: {len(seen)} jobs already sent")

KEYWORDS = ["architectural visualizer", "archviz", "3d architectural visualizer"]
BAD_WORDS = ["graphic", "logo", "ui", "ux", "motion", "video", "social media", "fashion", "accountant", "sales"]
GOOD_WORDS = ["arch", "viz", "visualizer", "interior", "exterior", "3ds", "render"]

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

print("Searching LinkedIn Saudi ARCH only 🇸🇦...")
for kw in KEYWORDS:
    try:
        print(f" -> Searching: {kw}")
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={kw.replace(' ', '%20')}&location=Saudi%20Arabia&start=0"
        resp = requests.get(url, headers=headers, timeout=25)

        if resp.status_code == 429:
            print("429 Rate limit - sleep 60s")
            time.sleep(60)
            continue
        if resp.status_code!= 200:
            print(f"Failed {resp.status_code}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("div", class_="base-card")
        print(f"Found {len(cards)} cards for {kw}")

        for card in cards[:8]:
            link_tag = card.find("a", class_="base-card__full-link")
            if not link_tag: continue
            link = link_tag.get("href","").split("?")[0].strip()
            if not link: continue

            # استخراج ID بطريقة مضمونة
            try:
                jid = link.split("/view/")[1].split("/")[0]
            except:
                jid = link.rstrip("/").split("/")[-1]

            if not jid or jid in seen or not jid.isdigit():
                continue

            title_tag = card.find("h3", class_="base-search-card__title")
            title = title_tag.text.strip() if title_tag else ""
            title_lower = title.lower()

            if any(b in title_lower for b in BAD_WORDS):
                print(f"Skip BAD: {title}")
                continue
            if not any(g in title_lower for g in GOOD_WORDS):
                print(f"Skip NOT ARCH: {title}")
                continue

            comp_tag = card.find("h4", class_="base-search-card__subtitle")
            company = comp_tag.text.strip() if comp_tag else "Confidential"

            msg = f"🇸🇦 *{title}*\n🏢 {company}\n📍 KSA\n🔗 {link}"

            if send(msg):
                con.execute("INSERT OR IGNORE INTO jobs VALUES (?)", (jid,))
                con.commit()
                seen.add(jid)
                print(f"Saved {jid}")
                time.sleep(3)

        time.sleep(random.randint(20,35))

    except Exception as e:
        print(f"Error {kw}: {e}")

print(f"Done! Total in memory now: {len(seen)}")
