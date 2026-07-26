import json

with open("data/insights.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for idx, c in enumerate(data["insights"]):
    print(f"Insight #{idx+1}: Title='{c['insight_title']}', Theme='{c['primary_theme']}', Conf='{c['confidence']}', RQs={c['answers_questions']}")
