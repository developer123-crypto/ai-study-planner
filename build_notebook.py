import json

def read(p): return open(p, encoding="utf-8").read()
def md(t): return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(True)}
def code(t): return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": t.splitlines(True)}

planner = read("study_planner/planner.py")
llm = read("study_planner/llm.py")

cells = [
 md("# 📚 AI Study Planner\nFree schedule generator + AI study tips (Gemini / Gemma).\n\n**Setup:** add `GEMINI_API_KEY` in Colab **Secrets** (🔑 icon, left side) and turn on *Notebook access*. The key is optional: the schedule works without it."),
 code("""import os
try:
    from google.colab import userdata
    try:
        os.environ["GEMINI_API_KEY"] = userdata.get("GEMINI_API_KEY")
    except Exception:
        print("GEMINI_API_KEY not set (AI tips will be skipped)")
except ImportError:
    pass  # running outside Colab: use an environment variable
"""),
 md("## 1. Planner code"),
 code(planner),
 md("## 2. AI code (Gemini free tier)"),
 code(llm),
 md("## 3. Your subjects (edit this!)"),
 code("""from datetime import date

HOURS_PER_DAY = 4  # free study hours per day

subjects = [
    Subject("Data Mining",   date(2026, 11, 20), difficulty=3),  # 1 easy, 2 medium, 3 hard
    Subject("Cybersecurity", date(2026, 11, 15), difficulty=2),
    Subject("Computer Graphics", date(2026, 11, 25), difficulty=1),
]
"""),
 md("## 4. Generate the schedule"),
 code("""import pandas as pd

rows = generate_schedule(subjects, HOURS_PER_DAY)
df = pd.DataFrame(rows)
display(df.pivot_table(index="date", columns="subject", values="hours", fill_value=0))
print("Total hours per subject:", summarize(rows))
"""),
 md("## 5. AI study tips (Gemini, with Gemma fallback)"),
 code("""for s in subjects:
    level = {1: "easy", 2: "medium", 3: "hard"}[s.difficulty]
    prompt = (f"Give 3 short, practical study tips for a university student preparing for "
              f"'{s.name}' (difficulty: {level}). Use bullet points. Do not mention any number of days or dates.")
    try:
        model, tips = ask(prompt)
        print(f"\\n### {s.name}  [{model}]\\n{tips}")
    except Exception as e:
        print(f"\\n{s.name}: AI skipped ({e})")
"""),
 md("## 6. Download your plan"),
 code("""export_csv(rows, "study_plan.csv")
export_ics(rows, "study_plan.ics")  # import into Google Calendar
try:
    from google.colab import files
    files.download("study_plan.csv"); files.download("study_plan.ics")
except ImportError:
    print("Saved study_plan.csv and study_plan.ics")
"""),
]

nb = {"cells": cells, "metadata": {"colab": {"name": "AI_Study_Planner.ipynb"}, "kernelspec": {"name": "python3", "display_name": "Python 3"}}, "nbformat": 4, "nbformat_minor": 5}
json.dump(nb, open("AI_Study_Planner.ipynb", "w", encoding="utf-8"), indent=1)
print("notebook written")
