import requests

TOKEN = "8746919756:AAFUtrn6XdP0B5ZbU1A7"
CHAT_ID = "5921311298"

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(url, data=data)

def get_jobs():
    try:
        # نبحث بكلمة 3D Architectural في الـ API
        url = "https://remotive.com/api/remote-jobs?search=3d%20architectural%20visualizer"
        r = requests.get(url).json()
        jobs = r.get('jobs', [])
        
        # فلترة إضافية عشان نتأكد
        keywords = ["3d", "visualizer", "archviz", "architectural", "render", "blender", "3ds max", "vray", "corona", "lumion", "revit", "sketchup", "unreal", "visualization"]
        
        filtered = []
        for job in jobs:
            title = (job.get('title','') + " " + job.get('description','')).lower()
            if any(k in title for k in keywords):
                filtered.append(job)
        
        if not filtered:
            # لو ما لقى، جيب أول 3 وظائف من البحث الأصلي
            return jobs[:3]
            
        return filtered[:5]
    except:
        return []

jobs = get_jobs()

if not jobs:
    send_msg("🔍 اليوم ما لقيت وظائف 3D Visualizer جديدة، حأفتش تاني بعد 6 ساعات")
else:
    for job in jobs:
        title = job.get('title','No title')
        company = job.get('company_name','')
        link = job.get('url','')
        msg = f"<b>🎨 {title}</b>\n🏢 {company}\n\n🔗 {link}\n\n#3D #ArchViz"
        send_msg(msg)
