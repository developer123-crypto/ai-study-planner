# 📚 AI Study Planner

Enter your subjects, exam dates and daily free hours. The planner builds a day-by-day
study schedule (harder subjects and closer exams get more time), then a free AI model
gives study tips for each subject. **100% free to run, in Google Colab.**

## AI used (free)
| Model | Used for | Cost |
|---|---|---|
| Gemini (Google AI Studio) | Study tips per subject | Free tier |
| Gemma (same Gemini key) | Automatic fallback | Free tier |

## Run in Colab
1. Open `AI_Study_Planner.ipynb` in Google Colab.
2. Get a free key at [Google AI Studio](https://aistudio.google.com/apikey).
3. In Colab, click the 🔑 **Secrets** icon, add `GEMINI_API_KEY`, and turn on *Notebook access*.
4. Edit the subjects in the "Your subjects" cell, then click **Runtime → Run all**.

The key is optional: the schedule itself works without it.

## Run locally
```bash
pip install -r requirements.txt
python -m pytest
```

## How the schedule works
For each day, a subject's weight is `difficulty / (days_until_exam + 1)`.
Daily hours are split by weight in 30-minute blocks. No study is scheduled after a subject's exam.

## Good first issues (Hacktoberfest)
- Pomodoro mode (25 min study / 5 min break)
- Streamlit web UI
- Rest-day option (e.g. no study on Fridays)
- Input from a CSV file
- More tests for `export_ics`
- Urdu translation of this README

## License
MIT
