import os, json
from datetime import datetime

def load_latest_job():
    paths = ["scoring_agent/last_job.json", "last_job.json", "jobs.json"]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        return data[0]
                    if isinstance(data, dict):
                        return data
            except: pass
    return {"title": "3D Visualizer - KSA", "company": "Top Arch Studio", "description": "3ds Max, V-Ray, Corona", "score": 85}

def generate_cover_letter(job):
    title = job.get('title','3D Visualizer')
    company = job.get('company','Company')
    return f"""Dear Hiring Manager at {company},

I am excited to apply for {title}.

With 4+ years in ArchViz, I specialize in:
- 3ds Max + V-Ray / Corona
- Lumion / D5 Render
- Photoshop post-production

Ready to relocate to KSA immediately.
Portfolio: [Your Link]

Thank you,
Sudanese 3D Visualizer - {datetime.now().date()}
"""

if __name__ == "__main__":
    job = load_latest_job()
    letter = generate_cover_letter(job)
    print(letter)
    os.makedirs("cv_agent", exist_ok=True)
    with open("cv_agent/cover_letter.txt", "w", encoding='utf-8') as f:
        f.write(letter)
    with open("cv_agent/tailored_cv.json", "w", encoding='utf-8') as f:
        json.dump({"job": job, "cover_letter": letter}, f, ensure_ascii=False, indent=2)
    print("CV Tailor Done!")
