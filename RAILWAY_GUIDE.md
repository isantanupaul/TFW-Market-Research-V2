# TFW Detailed Survey · Railway Deployment Guide

## Overview

```
Browser (Survey HTML)
        │  POST /submit  (JSON payload)
        ▼
   Flask Server  ──────►  Google Sheets
   (Railway.app)           "Survey Responses" tab
```

---

## Files in this folder

```
tfw-detailed-survey-deploy/
├── server.py                    ← Flask app + Google Sheets logic
├── trends-detailed-survey.html  ← Survey UI (served at /)
├── requirements.txt             ← Python deps
├── Procfile                     ← Railway start command
├── runtime.txt                  ← Python version
├── .gitignore                   ← Keeps secrets out of Git
└── RAILWAY_GUIDE.md             ← This file
```

---

## STEP 1 — Prepare your credentials (one-time)

Open Terminal and run:

```bash
cat /path/to/your-service-account.json | python3 -c \
  "import sys,json; print(json.dumps(json.load(sys.stdin)))"
```

Copy the **entire single-line output** — this is your `GOOGLE_CREDENTIALS_JSON`.

---

## STEP 2 — Push to GitHub

```bash
cd tfw-detailed-survey-deploy/

git init
git add .
git commit -m "TFW Detailed Survey - initial deploy"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tfw-detailed-survey.git
git push -u origin main
```

---

## STEP 3 — Deploy on Railway

1. Go to → https://railway.app → **New Project**
2. **Deploy from GitHub repo** → select `tfw-detailed-survey`
3. Railway auto-detects Python + Procfile ✅

---

## STEP 4 — Set Environment Variables

In Railway dashboard → your project → **Variables** tab:

| Variable | Value |
|---|---|
| `GOOGLE_CREDENTIALS_JSON` | *(single-line JSON from Step 1)* |
| `SPREADSHEET_ID` | *(your Sheet ID — the long string in the Sheet URL)* |

> Railway sets `PORT` automatically — don't add it manually.

---

## STEP 5 — Generate a domain

Railway → your service → **Settings** → **Networking** → **Generate Domain**

Your live URL:
```
https://tfw-detailed-survey-production.up.railway.app
```

---

## STEP 6 — Test it

1. Open the Railway URL in any browser
2. Fill the survey and hit **Submit Feedback**
3. Open your Google Sheet — a new row appears within seconds ✅

---

## Google Sheet columns (47 total)

| # | Column |
|---|--------|
| 1 | Timestamp |
| 2 | Time (mins) |
| 3 | XP Earned |
| 4 | Name |
| 5 | Gender |
| 6 | Age Range |
| 7 | Phone |
| 8 | Store Visited |
| 9 | Visit Intent |
| 10 | Time Spent In Store |
| 11 | Journey Stage |
| 12 | Staff Interaction (Q4) |
| 13 | Exit Reasons |
| 14 | Exit Reason (Other) |
| 15 | Size Needed |
| 16 | Size Recurring Issue |
| 17 | Expected Price (₹) |
| 18 | Style Category Sought |
| 19 | Service Issues |
| 20 | Return Likelihood (1-5) |
| 21 | Return Reason (Text) |
| 22 | Competitor Stores |
| 23 | Competitor Advantages |
| 24 | Channel Preference |
| 25 | Style Preferences |
| 26 | Budget (₹) |
| 27 | Purchase Frequency |
| 28 | Buying Influences |
| 29 | Rating: Product Variety |
| 30 | Rating: Pricing |
| 31 | Rating: Ambiance |
| 32 | Rating: Staff |
| 33 | Rating: Size Availability |
| 34 | Rating: Overall |
| 35 | Re-engagement Drivers |
| 36 | NPS — Recommend? |
| 37 | Open Feedback |
| 38 | Staff: Wait Time |
| 39 | Staff: Count Visible |
| 40 | Customer Tried to Get Help |
| 41 | Staff Was Doing Instead |
| 42 | Not Helpful: Why |
| 43 | Not Helpful: Duration |
| 44 | Not Helpful: Alternatives Offered |
| 45 | Not Helpful: What Would Have Helped |
| 46 | Self-Approach: Staff Response |
| 47 | Self-Approach: Query Resolved |
| 48 | Self-Approach: Interaction Duration |
| 49 | Self-Approach: Still No Buy Reason |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `GOOGLE_CREDENTIALS_JSON env var is not set` | Add it in Railway → Variables |
| `403 Forbidden` from Sheets | Re-share the Sheet with your service account email (Editor) |
| `Spreadsheet not found` | Check `SPREADSHEET_ID` — copy only the ID, not the full URL |
| Survey submits but no row appears | Check Railway → Logs for the `✅ Saved` line |
| Duplicate header rows | Won't happen — server checks row 1 before writing headers |

---

## Local dev

```bash
export GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
export SPREADSHEET_ID='your_sheet_id_here'

pip install -r requirements.txt
python3 server.py
# → http://localhost:5000
```
