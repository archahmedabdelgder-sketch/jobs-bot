import requests, os, sqlite3, time
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": False})
    except Exception as e:
        print(f"Send failed: {e}")

con = sqlite3.connect("jobs.db")
con.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY)")
seen = {r[0] for r in con.execute("SELECT id FROM jobs")}

KEYWORDS = ["3d visualizer", "architectural visualizer", "archviz"]
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept-Language": "en-US,en;q=0.9,ar;q=0.8"}

# 1- Jooble Saudi - بيجمع كل شي 🇸🇦
print("Searching Jooble Saudi...")
for kw in KEYWORDS:
    try:
        q = kw.replace(" ", "+")
        url = f"https://sa.jooble.org/jobs-{q}/Riyadh"
        print(f" -> Jooble SA: {kw} : {url}")
        resp = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("article", limit=8)
        print(f"Found {len(cards)} jooble")
        for card in cards:
            link_tag = card.find("a", href=True)
            if not link_tag: continue
            link = link_tag['href']
            if not link.startswith("http"): link = "https://sa.jooble.org" + link
            jid = link.split("/")[-1][:100]
            if jid in seen: continue
            title = link_tag.text.strip() or kw
            if any(x in title.lower() for x in ["3d", "visual", "arch", "render", "artist", "design"]):
                send(f"🇸🇦 *{title}*\n🔗 {link}\n🔍 {kw}\n#Jooble_KSA")
                con.execute("INSERT OR IGNORE INTO jobs VALUES (?)", (jid,))
                con.commit()
                seen.add(jid)
                time.sleep(1)
    except Exception as e:
        print(f"Jooble error {kw}: {e}")

# 2- Bayt.com Saudi 🇸🇦
print("Searching Bayt Saudi...")
for kw in KEYWORDS[:2]:
    try:
        q = kw.replace(" ", "+")
        url = f"https://www.bayt.com/en/saudi-arabia/jobs/{q}-jobs/"
        print(f" -> Bayt: {kw}")
        resp = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("li", class_="has-pointer-d", limit=8)
        if not cards:
            cards = soup.find_all("h2", limit=8)
        print(f"Found {len(cards)} bayt")
        for card in cards:
            link_tag = card.find("a", href=True) if hasattr(card, 'find') else None
            if not link_tag:
                # if h2 directly
                parent = card.find_parent("a") if hasattr(card, 'find_parent') else None
                link_tag = parent if parent else card if card.name=='a' else None
            if not link_tag: continue
            link = link_tag.get("href","")
            if not link.startswith("http"): link = "https://www.bayt.com" + link
            jid = link
            if jid in seen: continue
            title = link_tag.text.strip()
            if len(title) < 5: continue
            send(f"🇸🇦 *{title}* - Bayt\n🔗 {link}\n🔍 {kw}\n#Bayt_KSA")
            con.execute("INSERT OR IGNORE INTO jobs VALUES (?)", (jid,))
            con.commit()
            seen.add(jid)
            time.sleep(1)
    except Exception as e:
        print(f"Bayt error {kw}: {e}")

print("Done Saudi Only!")
