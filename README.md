# UnionHub

Apprenticeship directory admin + public site. One Flask app, deployed to Railway with Postgres.

This is **Step 1**: project skeleton with login. No features yet — just the foundation. Following steps add the union list, scraper, public directory.

## What's in here

```
unionhub/
├── app/
│   ├── __init__.py     ← Flask factory + CLI commands
│   ├── config.py       ← env vars
│   ├── models.py       ← User, Dma, Union, ScrapeJob
│   ├── auth.py         ← /login, /logout
│   ├── admin.py        ← /admin (login required)
│   ├── public.py       ← /, /api/health
│   └── templates/      ← Jinja templates
├── wsgi.py             ← entry point for gunicorn
├── requirements.txt
├── Procfile            ← Railway start command
├── runtime.txt         ← Python version
└── .env.example
```

## Run locally (5 minutes)

```bash
# 1. Set up Python environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env: set SECRET_KEY (any long random string) and ADMIN_EMAIL/ADMIN_PASSWORD

# 3. Create database + bootstrap admin user
export FLASK_APP=wsgi.py
flask init-db

# 4. Run
flask run --port 8000
```

Open http://localhost:8000 — public placeholder.
Open http://localhost:8000/login — log in with the ADMIN_EMAIL/PASSWORD you set.
You should land on the admin dashboard.

## Deploy to Railway

### One-time setup

1. **Push to GitHub** (Railway deploys from a Git repo):
   ```bash
   git init
   git add .
   git commit -m "Initial UnionHub skeleton"
   ```
   Create an empty repo at github.com, then:
   ```bash
   git remote add origin https://github.com/YOUR-USER/unionhub.git
   git branch -M main
   git push -u origin main
   ```

2. **Create Railway project:**
   - Go to https://railway.com (sign up, free tier is fine to start)
   - Click "New Project" → "Deploy from GitHub repo"
   - Connect GitHub, select your `unionhub` repo
   - Railway detects Python/Flask automatically

3. **Add Postgres:**
   - In your Railway project, click "+ New" → "Database" → "Add PostgreSQL"
   - Railway automatically sets `DATABASE_URL` env var on your app — nothing for you to do

4. **Set env vars** (in Railway → your service → Variables):
   ```
   SECRET_KEY=<paste a long random string>
   FLASK_ENV=production
   ADMIN_EMAIL=you@yourdomain.com
   ADMIN_PASSWORD=<strong password>
   ANTHROPIC_API_KEY=sk-ant-...   (only needed when we add the scraper)
   ```

5. **Initialize after first deploy** — run once:
   - Railway dashboard → your service → click the three-dot menu → "Run command" (or use Railway CLI: `railway run flask seed`)
   - Command: `flask seed`
   - This adds the 7 DMAs and creates your admin user from `ADMIN_EMAIL`/`ADMIN_PASSWORD`
   - (Tables themselves are created automatically by `flask db upgrade` in the Procfile's `release:` step on each deploy.)

6. **Get the URL:**
   - Railway → your service → Settings → "Generate Domain"
   - You get something like `unionhub-production.up.railway.app`

7. **Visit `/login`** with your admin email/password.

### Future updates

```bash
git add .
git commit -m "Add feature X"
git push
```
Railway auto-deploys on push.

## Cost

- Free trial credit covers initial development
- After that: ~$5-10/month for app + Postgres on Railway's "Hobby" plan
- Scraper API costs (later): a few dollars per full pass

## What's next

After this is deployed and you can log in, we add:
- **Step 2** — Public directory (job-seeker site reading from DB)
- **Step 3** — Admin: union list, edit, add new
- **Step 4** — Spreadsheet import
- **Step 5** — Scraper integration + review queue
