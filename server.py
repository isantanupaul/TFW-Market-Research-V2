"""
Trends Footwear · Detailed Survey Server (Google Sheets Edition)
================================================================
Reads env vars:
  GOOGLE_CREDENTIALS_JSON  – service-account JSON (as a single-line string)
  SPREADSHEET_ID           – Google Sheet ID from the URL
  PORT                     – set automatically by Railway (default 5000 locally)

Tabs used in the same spreadsheet:
  "Survey Responses"  – one row per full submission (all sections)
"""

import os, json, sys
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials

# ── App setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ── Config ─────────────────────────────────────────────────────────────────────
SPREADSHEET_ID    = os.environ.get("SPREADSHEET_ID", "")
GOOGLE_CREDS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
SURVEY_TAB        = "Survey Responses"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── All column headers (matches flatten_row below exactly) ─────────────────────
SURVEY_HEADERS = [
    # ── Meta ──────────────────────────────────────────────────────────────────
    "Timestamp",
    "Time (mins)",
    "XP Earned",

    # ── Customer Details ───────────────────────────────────────────────────────
    "Name",
    "Gender",
    "Age Range",
    "Phone",
    "Store Visited",

    # ── Section 1 · Visit Context ──────────────────────────────────────────────
    "Visit Intent",
    "Time Spent In Store",
    "Journey Stage",
    "Staff Interaction (Q4)",

    # ── Section 2 · Exit Reasons ───────────────────────────────────────────────
    "Exit Reasons",
    "Exit Reason (Other)",
    "Size Needed",
    "Size Recurring Issue",
    "Expected Price (₹)",
    "Style Category Sought",
    "Service Issues",

    # ── Section 3 · Return Likelihood ──────────────────────────────────────────
    "Return Likelihood (1-5)",
    "Return Reason (Text)",
    "Competitor Stores",
    "Competitor Advantages",
    "Channel Preference",

    # ── Section 4 · Preferences ────────────────────────────────────────────────
    "Style Preferences",
    "Budget (₹)",
    "Purchase Frequency",
    "Buying Influences",

    # ── Section 5 · Ratings ────────────────────────────────────────────────────
    "Rating: Product Variety",
    "Rating: Pricing",
    "Rating: Ambiance",
    "Rating: Staff",
    "Rating: Size Availability",
    "Rating: Overall",

    # ── Section 5 · Re-engagement ──────────────────────────────────────────────
    "Re-engagement Drivers",
    "NPS — Recommend?",
    "Open Feedback",

    # ── Staff Study · No Approach (Pink Panel) ─────────────────────────────────
    "Staff: Wait Time",
    "Staff: Count Visible",
    "Customer Tried to Get Help",
    "Staff Was Doing Instead",

    # ── Staff Study · Not Helpful (Amber Panel) ────────────────────────────────
    "Not Helpful: Why",
    "Not Helpful: Duration",
    "Not Helpful: Alternatives Offered",
    "Not Helpful: What Would Have Helped",

    # ── Staff Study · Self-Approached (Cyan Panel) ─────────────────────────────
    "Self-Approach: Staff Response",
    "Self-Approach: Query Resolved",
    "Self-Approach: Interaction Duration",
    "Self-Approach: Still No Buy Reason",
]


# ── Shared spreadsheet connection ──────────────────────────────────────────────
def _get_spreadsheet():
    if not GOOGLE_CREDS_JSON:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON env var is not set.")
    if not SPREADSHEET_ID:
        raise RuntimeError("SPREADSHEET_ID env var is not set.")

    creds  = Credentials.from_service_account_info(
                 json.loads(GOOGLE_CREDS_JSON), scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)


def _get_or_create_tab(spreadsheet, tab_name):
    try:
        return spreadsheet.worksheet(tab_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=tab_name, rows=5000, cols=len(SURVEY_HEADERS) + 2)


def _ensure_header(sheet):
    """Write bold purple header row if the sheet is empty."""
    if sheet.row_values(1):
        return  # already has a header
    sheet.append_row(SURVEY_HEADERS, value_input_option="USER_ENTERED")
    try:
        sheet.format(f"A1:{chr(64 + len(SURVEY_HEADERS))}1", {
            "textFormat": {
                "bold": True,
                "foregroundColor": {"red": 1, "green": 1, "blue": 1},
            },
            "backgroundColor": {"red": 0.286, "green": 0.149, "blue": 0.890},
            "horizontalAlignment": "CENTER",
        })
    except Exception:
        pass  # formatting is cosmetic — don't crash on it


# ── Flatten helpers ────────────────────────────────────────────────────────────
def _j(val):
    """List → comma-separated string, else safe str."""
    if isinstance(val, list):
        return ", ".join(str(x) for x in val if x)
    return str(val) if val is not None else ""


def _v(val):
    return str(val) if val is not None else ""


def flatten_row(data: dict) -> list:
    """
    Turn the full JSON payload from the survey form into a flat list
    that matches SURVEY_HEADERS exactly.
    """
    c  = data.get("customer",         {})
    vi = data.get("visit",            {})
    ex = data.get("exit_reasons",     {})
    rl = data.get("return_likelihood",{})
    pr = data.get("preferences",      {})
    ra = data.get("ratings",          {})
    re = data.get("re_engagement",    {})
    ss = data.get("staff_study",      {})
    nh = ss.get("not_helpful",        {})
    sa = ss.get("self_approached",    {})
    me = data.get("meta",             {})

    return [
        # Meta
        me.get("timestamp")    or datetime.now().isoformat(),
        _v(me.get("time_minutes")),
        _v(me.get("xp_earned")),

        # Customer
        _v(c.get("name")),
        _v(c.get("gender")),
        _v(c.get("age")),
        _v(c.get("phone")),
        _v(c.get("store")),

        # Section 1
        _v(vi.get("intent")),
        _v(vi.get("time_spent")),
        _v(vi.get("journey_stage")),
        _v(vi.get("staff_interaction")),

        # Section 2
        _j(ex.get("selected")),
        _v(ex.get("other")),
        _v(ex.get("size_needed")),
        _v(ex.get("size_recurring")),
        _v(ex.get("expected_price")),
        _j(ex.get("style_sought")),
        _j(ex.get("service_issues")),

        # Section 3
        _v(rl.get("score")),
        _v(rl.get("reason")),
        _j(rl.get("competitors")),
        _j(rl.get("competitor_advantages")),
        _v(rl.get("channel_preference")),

        # Section 4
        _j(pr.get("style_preference") or pr.get("categories")),
        _v(pr.get("budget")),
        _v(pr.get("purchase_frequency")),
        _j(pr.get("influences")),

        # Ratings
        _v(ra.get("variety")),
        _v(ra.get("pricing")),
        _v(ra.get("ambiance")),
        _v(ra.get("staff")),
        _v(ra.get("size_avail")),
        _v(ra.get("overall")),

        # Re-engagement
        _j(re.get("drivers")),
        _v(re.get("nps")),
        _v(re.get("open_ended")),

        # Staff — No Approach
        _v(ss.get("wait_time")),
        _v(ss.get("staff_visible_count")),
        _v(ss.get("customer_attempt")),
        _j(ss.get("staff_was_doing")),

        # Staff — Not Helpful
        _j(nh.get("reasons")),
        _v(nh.get("duration")),
        _v(nh.get("alternatives_offered")),
        _j(nh.get("improvement_suggestions")),

        # Staff — Self Approached
        _v(sa.get("staff_response")),
        _v(sa.get("query_resolved")),
        _v(sa.get("interaction_duration")),
        _j(sa.get("still_no_buy_reason")),
    ]


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def serve_survey():
    """Serve the survey HTML file."""
    base = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base, "trends-detailed-survey.html")


@app.route("/submit", methods=["POST"])
def submit():
    """Receive a survey payload → append one row to Google Sheets."""
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"status": "error", "message": "Empty payload"}), 400

        ss    = _get_spreadsheet()
        sheet = _get_or_create_tab(ss, SURVEY_TAB)
        _ensure_header(sheet)

        row = flatten_row(payload)
        sheet.append_row(row, value_input_option="USER_ENTERED")

        name  = payload.get("customer", {}).get("name", "unknown")
        store = payload.get("customer", {}).get("store", "")
        ts    = payload.get("meta", {}).get("timestamp", "")[:19]
        print(f"  ✅ Saved: {name} | {store} | {ts}", flush=True)

        return jsonify({"status": "ok", "message": "Response saved"})

    except Exception as exc:
        print(f"  ❌ /submit error: {exc}", file=sys.stderr, flush=True)
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "running",
        "sheet_id": SPREADSHEET_ID,
        "tab": SURVEY_TAB,
        "columns": len(SURVEY_HEADERS),
    })


# ── Local entry-point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  TFW Survey → http://localhost:{port}\n", flush=True)
    app.run(debug=True, port=port, host="0.0.0.0")
