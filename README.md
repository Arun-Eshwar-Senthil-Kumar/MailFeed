# MailFeed — web version (run this first)
cd backend
python -m venv venv
venv\Scripts\activate         (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env        (Mac/Linux: cp .env.example .env)  -> fill in Gmail + app password
uvicorn app.main:app --reload
Open http://localhost:8000

The mobile/ folder is the React Native version (for later).
"# MailFeed" 
