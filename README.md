# MailFeed v2 — run
cd backend
python -m venv venv && venv\Scripts\activate      (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
uvicorn app.main:app --reload
Open http://localhost:8000 and sign in with any email + app password.
(.env is optional now — only for AI summaries: LLM_API_KEY / LLM_BASE_URL / LLM_MODEL)
