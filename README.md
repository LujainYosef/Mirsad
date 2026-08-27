# مِرصاد (Mirsad) — AI Security Investigator

> بعينِ مِرصاد، للمحتالين بالمرصاد.
> *With Mirsad's watchful eye, fraudsters are under watch.*

Mirsad is an AI-powered security investigation web application. It takes
suspicious evidence — phishing emails, screenshots, links, SIEM log exports,
PDFs, or files — and investigates it the way a senior SOC (L2/L3) analyst
would: what happened, how severe it is, what evidence supports the
conclusion, what's still unknown, and what to do next. Arabic (RTL) is the
default language; English is fully supported.

---

## 1. Project Overview

Mirsad turns raw, messy security evidence into a structured investigation
instead of a generic chatbot summary. For every submission it produces:

- **Verdict** — Safe / Suspicious / Malicious / Inconclusive
- **Severity** — Critical / High / Medium / Low / Informational, with a stated reason
- **Confidence** — High / Medium / Low, with a stated reason (confidence reflects
  evidence *strength*, not how sure the writing sounds)
- **Confirmed evidence** vs **hypotheses** vs **evidence gaps** — kept strictly separate
- **IOCs**, a **timeline**, **suspicious findings**, **next investigation steps**, and
  **defensive recommendations**
- A follow-up **investigator chat** grounded in the same evidence, so analysts
  can ask "why?" or "what should I check next?"

The investigator's behavior, evidence-handling rules, and prompt-injection
defenses are defined in [`Agents.md`](./Agents.md) — this file is loaded
**verbatim** as the model's system prompt and is treated as part of the
application's security boundary, not optional documentation. All
user-supplied content (file contents, pasted text, chat messages) is always
treated as **untrusted evidence to analyze**, never as instructions — see
`app/prompts.py`.

Mirsad never executes uploaded files, never claims to have taken an action it
didn't actually take, and never presents an assumption as a confirmed fact.
When evidence is insufficient, it says so and asks for the smallest useful
additional artifact instead of guessing.

---

## 2. Project Structure

```
mirsad/
├── app/
│   ├── main.py                 # FastAPI app, static file serving, health check
│   ├── config.py                # Settings loaded from environment variables (.env locally)
│   ├── schemas.py                # Pydantic models for the dashboard JSON contract & chat
│   ├── prompts.py                # Builds the system prompt from Agents.md + output rules
│   ├── routes/
│   │   ├── investigate.py        # POST /api/investigate — ingest evidence, call the LLM
│   │   └── chat.py                # POST /api/chat — grounded follow-up chat
│   └── services/
│       ├── llm_client.py         # OpenRouter API client (timeouts, retries, no key leakage)
│       ├── extraction.py          # Safe file parsing: PDF text, image validation, plain text
│       ├── result_parser.py       # Validates model JSON output; safe "Inconclusive" fallback
│       └── case_store.py          # In-memory per-case store (evidence + chat history, TTL)
├── static/
│   ├── index.html                # Single-page app (Arabic RTL default, English toggle)
│   ├── css/style.css             # Brand theme (dark/light), dashboard, chat panel, animations
│   ├── js/app.js                  # i18n, upload, dashboard rendering, chat — vanilla JS
│   └── img/favicon.svg
├── tests/
│   └── test_basic.py              # Health check, input validation, output-parsing safety net
├── Agents.md                      # Investigator role, rules, and prompt-injection defenses
├── requirements.txt
├── render.yaml                    # Optional Render infra-as-code blueprint
├── .env.example                   # Copy to .env and fill in your own values
└── .gitignore
```

---

## 3. Technologies & AI Tools Used

**Backend**
- Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/) — routing, validation, static file serving
- [Uvicorn](https://www.uvicorn.org/) — ASGI server
- [httpx](https://www.python-httpx.org/) — async HTTP client for calling OpenRouter
- [pypdf](https://pypdf.readthedocs.io/) — safe, read-only text extraction from PDFs
- [Pillow](https://pillow.readthedocs.io/) — image validation and re-encoding (never trusts raw uploaded bytes directly)
- [Pydantic](https://docs.pydantic.dev/) — strict schema validation of the model's structured output
- [pytest](https://docs.pytest.org/) — test suite

**Frontend**
- Semantic HTML5, CSS3 (custom properties, RTL/LTR-aware logical properties), vanilla JavaScript
- No frontend framework/build step — kept intentionally lightweight per the product requirements
- Google Fonts: IBM Plex Sans Arabic, IBM Plex Sans, IBM Plex Mono

**AI**
- **LLM Gateway:** [OpenRouter](https://openrouter.ai/) — the model is fully configurable via the
  `OPENROUTER_MODEL` environment variable without touching any code
- A vision-capable model is recommended so uploaded screenshots (e.g. phishing
  emails) can be analyzed directly instead of relying on separate OCR

**Deployment**
- Source control: GitHub
- Hosting: [Render](https://render.com/) (Python web service)

---

## 4. Installation & Run Instructions (Local)

### Prerequisites
- Python 3.11 or newer
- An [OpenRouter](https://openrouter.ai/keys) account and API key

### Steps

```bash
# 1. Clone your repository (after you've pushed this project to GitHub)
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key locally
cp .env.example .env
# then open .env and set:
#   OPENROUTER_API_KEY=sk-or-...your key...
#   OPENROUTER_MODEL=anthropic/claude-sonnet-4.5   (or any OpenRouter model slug you prefer)

# 5. Run the app
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** in your browser. The `.env` file is listed in
`.gitignore`, so your real API key is saved on your machine for local testing
and is **never** committed to GitHub.

You can verify the key is loaded correctly by visiting
**http://localhost:8000/api/health** — it should report
`"api_key_configured": true`.

### Running the tests

```bash
pytest
```

---

## 5. Deploying (GitHub → Render)

1. Push this project to a new GitHub repository (your real `.env` will not be
   included, since it's git-ignored — only `.env.example` is committed).
2. In [Render](https://render.com/), create a new **Web Service** from that
   GitHub repo. If you keep `render.yaml`, Render can pick up the
   configuration automatically; otherwise set manually:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. In the service's **Environment** tab, add the same variables from your
   local `.env` — at minimum `OPENROUTER_API_KEY`. Never paste real secrets
   into `render.yaml` or any file you commit.
4. Deploy. Render will build and give you a public URL.

---

## 6. How to Use the Application

1. **Choose your language and theme** from the top bar (Arabic/RTL is the
   default; a light/dark toggle is available).
2. **Submit evidence** in any combination:
   - Drag & drop or browse for files — PDFs, screenshots/images, or
     `.txt/.log/.csv/.json/.eml` files (up to 10MB each, 5 files per case)
   - Paste raw text (an email body, log lines, alert JSON, etc.)
   - Enter a suspicious URL
3. Click **"ابدأ التحقيق" / "Start investigation."** Mirsad extracts the
   evidence safely (no file is ever executed), sends it to the configured
   OpenRouter model together with the `Agents.md` investigator rules, and
   renders the result as a dashboard: verdict, severity, confidence,
   confirmed evidence, suspicious events, IOCs, timeline, hypotheses,
   evidence gaps, next steps, and recommendations.
4. Click **"اسأل المحقق" / "Ask the investigator"** to open the chat panel
   and ask follow-up questions — the investigator stays grounded in the
   evidence already submitted for that case and won't invent new evidence.
5. Use **"تصدير التقرير" / "Export report"** to print/save the dashboard
   (e.g. as a PDF via your browser's print dialog) for retention or sharing.
6. Click **"تحقيق جديد" / "New investigation"** to start over.

If the evidence is insufficient for a confident conclusion, Mirsad will say
so explicitly and tell you what additional evidence (e.g. full email headers,
more log context) would help — rather than guessing.

---

## 7. Future Improvements

- **Persistence:** replace the in-memory case store with a real database
  (e.g. Postgres) so cases and chat history survive restarts/redeploys, and
  add "saved cases" / investigation history per the PRD roadmap.
- **Direct SIEM connectors** and API-based ingestion instead of manual export/upload.
- **Threat-intelligence enrichment** (reputation lookups for IPs/domains/hashes)
  through authorized, clearly-labeled external data sources.
- **MITRE ATT&CK mapping** for findings and hypotheses.
- **Sandboxed dynamic analysis** integration for files/URLs where static
  analysis alone is inconclusive.
- **Structured/schema-constrained output mode** if/when the selected
  OpenRouter model supports native JSON-schema enforcement, as an extra
  validation layer on top of the current Pydantic validation.
- **Authentication & multi-user support**, with per-organization case history
  and role-based access (analyst vs. general user).
- **Export formats:** a dedicated PDF/DOCX report generator in addition to
  browser print, and a structured JSON export for SOAR/ticketing integration.
- **Automated evaluation suite** for the adversarial cases listed in the PRD
  (prompt injection inside PDFs/OCR text, contradictory logs, fake IOCs,
  "stop investigating" requests) as part of CI, expanding on `tests/test_basic.py`.
- **Controlled SOAR integrations** with explicit human approval and audit
  trails, once the product moves beyond advisory-only recommendations.

---

## Security Notes

- `OPENROUTER_API_KEY` is read only from server-side environment variables
  and is never sent to the browser, logged, or hard-coded.
- All uploaded/pasted content is treated as **untrusted evidence**, clearly
  delimited before being sent to the model, and is never treated as
  instructions that could change the investigator's role or output format
  (see `Agents.md` §3 and `app/prompts.py`).
- Files are never executed. PDFs are parsed for their text layer only;
  images are validated and re-encoded before being forwarded to the model.
- Model output is parsed defensively and validated against a strict schema
  before being rendered; malformed output falls back to a safe
  "Inconclusive / Low confidence" result instead of being trusted.
