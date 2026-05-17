# SimplifIQ — AI Lead Automation System

> Automatically enriches lead data, generates a personalized PDF audit, and emails it to the prospect — zero human intervention.

## Architecture

```
Lead form (HTML)
    ↓ POST /submit
Flask route (app.py)
    ↓ validate
scraper.py       → scrape website + LinkedIn hints
    ↓
Claude API       → synthesize insights (JSON)
    ↓
pdf_generator.py → build branded PDF report (ReportLab)
    ↓
mailer.py        → send email with PDF attachment (SMTP)
    ↓ (bonus)
sheets.py        → log lead to Google Sheet
drive.py         → archive PDF to Google Drive
```

## Setup

### 1. Clone and install

```bash
git clone <repo>
cd simplifiq_assessment
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in:

```env
ANTHROPIC_API_KEY=sk-ant-...         # from console.anthropic.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your_app_password          # Gmail → Settings → App Passwords
GOOGLE_SHEET_ID=...                  # from the Sheet URL
GOOGLE_DRIVE_FOLDER_ID=...           # from the Drive folder URL
```

### 3. Google API credentials (for bonus features)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → enable **Google Sheets API** and **Google Drive API**
3. Create a **Service Account** → download `credentials.json`
4. Place `credentials.json` in the project root
5. Share your Google Sheet and Drive folder with the service account email

### 4. Run

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## Design Decisions

- **Scraper + Claude**: Website text is scraped first, then passed to Claude for structured synthesis. This avoids hallucination about unknown companies while still producing rich AI-driven insights.
- **Graceful fallbacks**: Every external call (scraping, Claude, Sheets, Drive) is wrapped in try/except. The core pipeline (PDF + email) will succeed even if enrichment or bonus steps fail.
- **ReportLab for PDF**: Chosen over WeasyPrint for more precise layout control and no system-level dependencies.
- **SMTP over SendGrid**: Zero additional accounts needed; works with any Gmail App Password out of the box.

## Limitations & Known Tradeoffs

- Scraping may fail on JavaScript-heavy sites (SPA). Mitigation: fallback enrichment is used automatically.
- Gmail SMTP rate limits to ~500 emails/day. For production, swap in SendGrid or AWS SES.
- Claude API costs money per call. For high volume, cache enrichment results by domain.
- `credentials.json` must NOT be committed to git — add it to `.gitignore`.

## File Structure

```
app.py              Main Flask app and route handler
scraper.py          Website scraping + Claude enrichment
pdf_generator.py    ReportLab PDF builder
mailer.py           SMTP email with PDF attachment
sheets.py           Google Sheets logging (bonus)
drive.py            Google Drive PDF archiving (bonus)
templates/form.html Lead intake HTML form
static/style.css    Form styling
outputs/            Generated PDFs (gitignored)
credentials.json    Google service account (gitignored)
.env                Secrets (gitignored)
```
