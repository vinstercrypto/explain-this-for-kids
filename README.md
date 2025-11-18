# Explain This for Kids 📚

A powerful web app that takes complex text or article URLs and explains them at any grade level (K-12 or Adult TLDR). Perfect for parents, teachers, and anyone who needs to make content accessible to young learners.

## Features

### Core Functionality
- **Dual Input**: Paste raw text OR a URL to an article
- **Auto URL Detection**: Automatically detects and fetches content from URLs
- **Article Extraction**: Uses BeautifulSoup to extract readable text from web pages
- **Grade Level Selection**: Choose from Kindergarten through 12th grade, plus Adult TLDR
- **AI-Powered Explanations**: Uses Claude AI to generate age-appropriate explanations

### Advanced Features
- **Smart Bullet Counts**:
  - K-5: 2 bullets
  - 6-8: 3 bullets
  - 9-12: 5 bullets
  - Adult TLDR: 1-2 sentence TLDR + 5 short bullets (NO vocabulary)
- **Safe Summary Mode**: For K-5, content is filtered to avoid graphic violence, explicit content, and inappropriate topics
- **Vocabulary Builder**: 3-6 key terms with grade-appropriate definitions (K-12 only, not for Adult TLDR)
- **Citation Draft**: AI-generated MLA-style citations for URL sources as a starting point. Always verify against official MLA guidelines or teacher requirements.
- **Shareable Links**: Each explanation gets a unique shareable URL
- **PDF Download**: Download explanations as printable PDFs
- **Email Summary**: Send explanations to any email address
- **API Endpoint**: `/api/explain` for Chrome extensions and integrations
- **Mobile-Friendly**: Fully responsive design works great on phones and tablets

## Project Structure

```
explain-this-for-kids/
├── app.py                  # Flask backend with all routes and logic
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── summaries.db           # SQLite database (auto-created)
├── templates/
│   ├── index.html         # Main page
│   ├── summary.html       # Shared summary view
│   └── 404.html           # Error page
└── static/
    ├── style.css          # Styling with responsive design
    └── main.js            # Frontend JavaScript
```

## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- A Claude API key from Anthropic

### Step-by-Step Installation

#### 1. Clone the repository

```bash
git clone <your-repo-url>
cd explain-this-for-kids
```

#### 2. Create a virtual environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set up environment variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
# On Mac/Linux:
nano .env

# On Windows:
notepad .env
```

**Required Environment Variables:**

```env
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx
SECRET_KEY=your_random_secret_key
```

**Optional (for email feature):**

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your.email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=your.email@gmail.com
```

**Optional (for donation button):**

```env
DONATE_URL=https://www.example.com/donate
```

Set `DONATE_URL` to your PayPal, Ko-fi, Buy Me a Coffee, or any other donation page URL. When set, a "Donate" button will appear on the main page and share pages. If not set or left empty, the donate button will be hidden.

**Getting a Claude API Key:**
- Go to https://console.anthropic.com/
- Sign up or log in
- Navigate to API Keys section
- Create a new API key
- Copy and paste it into your `.env` file

**Setting up Gmail for Email Feature:**
1. Go to https://myaccount.google.com/apppasswords
2. Create an app-specific password
3. Use that password in `SMTP_PASSWORD`

#### 5. Run the Flask application

```bash
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
* Running on http://127.0.0.1:5000
```

#### 6. Open in your browser

Go to: **http://localhost:5000**

## Usage Guide

### Basic Usage

1. **Enter Content**: Paste text or a URL into the large text area
2. **Select Grade Level**: Choose from K-12 or Adult TLDR
3. **Click "Explain it!"**: Wait for the AI-generated explanation
4. **View Results**: See the title, explanation, why it matters, and vocabulary

### Advanced Features

#### Shareable Links
- Click "Copy Link" to get a shareable URL
- Share with students, parents, or colleagues
- Anyone with the link can view the explanation

#### Download PDF
- Click "Download PDF" to get a printable version
- Perfect for homework, handouts, or offline reading

#### Email Summary
- Enter an email address in the "Email me a copy" section
- Click "Send Email" to receive the explanation via email

## API Documentation

### POST /api/explain

Process text or URLs and return structured explanations.

#### Request

```bash
curl -X POST http://localhost:5000/api/explain \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Quantum entanglement is a phenomenon...",
    "grade_level": "8th grade"
  }'
```

#### Python Example

```python
import requests

response = requests.post('http://localhost:5000/api/explain', json={
    'text': 'Your text or URL here',
    'grade_level': '5th grade'
})

data = response.json()
if data['success']:
    print(f"Title: {data['title']}")
    print(f"Explanation: {data['explanation']}")
    print(f"Share URL: {data['share_url']}")
```

#### Response Format

**Success:**
```json
{
  "success": true,
  "title": "Understanding Quantum Entanglement",
  "explanation": "Quantum entanglement is when two particles...",
  "why_it_matters": [
    "This could lead to super-fast computers",
    "It helps us understand how the universe works"
  ],
  "vocabulary": [
    {
      "word": "Quantum",
      "definition": "The smallest amount of energy"
    }
  ],
  "share_url": "/s/abc123xyz"
}
```

**Error:**
```json
{
  "success": false,
  "error": "Could not read that link. Please copy and paste the text manually."
}
```

#### Supported Grade Levels

- `Kindergarten`
- `1st grade` through `12th grade`
- `Adult TLDR`

## How It Works

### Grade Categories

The app categorizes grade levels into four groups:

- **Category A (K-5)**: 2 bullets, safe summary mode, simple vocabulary
- **Category B (6-8)**: 3 bullets, age-appropriate content
- **Category C (9-12)**: 5 bullets, more advanced vocabulary
- **Category D (Adult TLDR)**: 1-2 sentence TLDR + 5 short bullets, NO vocabulary (truly concise for busy adults)

### Safe Summary Mode (K-5)

For young learners, the AI is instructed to:
- Avoid graphic violence, gore, or explicit content
- Skip detailed descriptions of crime or self-harm
- Use gentle language for sensitive topics
- Avoid partisan political framing
- Focus on educational value

### URL Processing

1. App detects if input looks like a URL
2. Fetches HTML with proper headers
3. Removes scripts, styles, navigation, etc.
4. Extracts main content from `<article>`, `<main>`, or `<p>` tags
5. Falls back to manual text if extraction fails

### Database Schema

```sql
CREATE TABLE summaries (
    id TEXT PRIMARY KEY,          -- Short random ID
    created_at TEXT,              -- ISO timestamp
    grade_level TEXT,             -- Original grade level
    category TEXT,                -- A/B/C/D
    title TEXT,                   -- Generated title
    explanation TEXT,             -- Full explanation
    bullets TEXT,                 -- JSON array of bullets
    vocabulary TEXT               -- JSON array of vocab items
)
```

## Deployment

### Local Development

Already covered above. Just run `python app.py`.

### Production Deployment

For production, consider:

1. **Use a production WSGI server** (gunicorn, uWSGI)
2. **Set proper SECRET_KEY** (not the default)
3. **Use environment variables** (don't commit `.env`)
4. **Enable HTTPS** for secure sessions
5. **Consider database backups** for summaries.db

**Example with Gunicorn:**

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### "CLAUDE_API_KEY not found"
- Make sure you created the `.env` file
- Verify the API key is correctly set in `.env`
- Check that you're running the app from the same directory as `.env`

### "Could not read that link"
- The URL might be behind a paywall or require authentication
- Try copying the article text manually instead
- Some sites block automated scraping

### Email not working
- Verify all SMTP environment variables are set
- For Gmail, use an app-specific password
- Check firewall/network settings for port 587
- Email feature is optional - app works without it

### Port already in use
```bash
# Mac/Linux
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Database locked error
- Make sure only one instance of the app is running
- Check file permissions on summaries.db
- SQLite doesn't handle high concurrent writes well - for production, consider PostgreSQL

## Chrome Extension

A Chrome extension is included in the `chrome-extension/` folder that lets you summarize any webpage directly from your browser.

### Features

- **One-Click Summarization**: Click the extension icon on any webpage to extract and summarize content
- **Grade Level Selection**: Choose from K-12 or Adult TLDR right in the popup
- **Smart Text Extraction**: Automatically extracts main content while filtering out navigation, ads, and other noise
- **Mode-Based Display**:
  - K-12: Shows "Why this matters" heading + Vocabulary Builder
  - Adult TLDR: Shows "Key takeaways" heading (no vocabulary)
- **MLA Citation Draft**: For URL-based summaries, displays AI-generated MLA-style citation with verification warning
- **Copy Share Link**: One-click copying of shareable summary URLs
- **Donate Button**: Optional support link (configurable)

### Installation

#### 1. Configure API Endpoint

Before installing, you need to configure the extension to point to your deployed API:

**Edit `chrome-extension/popup.js`:**

```javascript
// Line 3-4: Replace with your deployed API URL
const API_BASE_URL = 'https://your-app.com';  // TODO: Replace this
const API_ENDPOINT = `${API_BASE_URL}/api/explain`;

// Line 7: Optionally set your donate URL
const DONATE_URL = 'https://your-donate-url.com';  // TODO: Replace this
```

**Edit `chrome-extension/manifest.json`:**

```json
{
  "host_permissions": [
    "https://your-app.com/*"  // TODO: Replace with your domain
  ]
}
```

#### 2. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top right)
3. Click **Load unpacked**
4. Select the `chrome-extension/` folder
5. The extension icon should appear in your toolbar

#### 3. Generate Icons (Optional)

The extension includes placeholder icons. For better quality:

```bash
cd chrome-extension/icons
python3 generate-icons.py
```

Or use ImageMagick/Inkscape (see `chrome-extension/icons/GENERATE-ICONS.md`)

### Usage

1. **Navigate to any article or webpage** you want to summarize
2. **Click the "Summarize It!" extension icon** in your toolbar
3. **Select a grade level** from the dropdown (default: 5th grade)
4. **Click "Simplify It!"**
5. **View the summary** with:
   - Title and explanation
   - Why it matters / Key takeaways (depending on mode)
   - Vocabulary Builder (K-12 only)
   - MLA Citation Draft (if summarizing a URL)
   - AI disclaimer (always shown)
   - Share link copy button

### Extension Structure

```
chrome-extension/
├── manifest.json          # Chrome extension manifest (V3)
├── popup.html            # Extension popup UI
├── popup.css             # Popup styling
├── popup.js              # Main logic and API integration
├── contentScript.js      # Text extraction from webpages
└── icons/
    ├── icon16.png        # 16x16 icon
    ├── icon32.png        # 32x32 icon
    ├── icon48.png        # 48x48 icon
    └── icon128.png       # 128x128 icon
```

### How It Works

1. **Content Extraction**: When you click "Simplify It!", `contentScript.js` extracts visible text from the current page:
   - Prioritizes main content areas (`<article>`, `<main>`, etc.)
   - Excludes navigation, headers, footers, ads, and scripts
   - Handles pages with minimal content gracefully

2. **API Call**: The extension POSTs the extracted text to your `/api/explain` endpoint with the selected grade level

3. **Smart Rendering**: Results are rendered based on the `mode` field:
   - **Kids mode**: "Why this matters" + Vocabulary Builder
   - **Adult TLDR mode**: "Key takeaways" + NO vocabulary

4. **Share Link**: If the API returns a `share_url`, a copy button appears for easy sharing

### Configuration Options

**API Base URL** (`popup.js` line 3):
```javascript
const API_BASE_URL = 'https://your-app.com';
```

**Donate URL** (`popup.js` line 7):
```javascript
const DONATE_URL = 'https://ko-fi.com/yourname';
```

**Host Permissions** (`manifest.json`):
```json
"host_permissions": [
  "https://your-app.com/*"
]
```

### Troubleshooting

**Extension icon doesn't appear:**
- Check that you loaded the `chrome-extension/` folder, not a subfolder
- Verify manifest.json has no syntax errors
- Try reloading the extension from `chrome://extensions/`

**"Not enough readable text found":**
- The page might have very little text content
- Try a different article or webpage
- Some pages use heavy JavaScript rendering that makes extraction difficult

**API connection fails:**
- Verify `API_BASE_URL` in `popup.js` matches your deployed URL
- Check that `host_permissions` in `manifest.json` includes your domain
- Ensure your deployed app has CORS headers enabled (Flask-CORS)
- Open browser DevTools (F12) → Console tab to see detailed errors

**Vocabulary not showing for Adult TLDR:**
- This is expected! Adult TLDR mode intentionally hides vocabulary for brevity
- Choose a K-12 grade level if you want vocabulary terms

**MLA citation not appearing:**
- Citations only appear when summarizing URLs (not pasted text)
- Check that the API response includes `mla_citation` field
- The citation is marked as a draft and requires verification

### Publishing to Chrome Web Store (Optional)

To make the extension publicly available:

1. Create a developer account at https://chrome.google.com/webstore/developer/dashboard
2. Prepare required assets:
   - Promotional images (440x280, 920x680, 1400x560)
   - Detailed description
   - Screenshots
3. Update manifest version before each release
4. Submit for review (usually 1-2 days)

### Privacy & Permissions

The extension requires:
- **activeTab**: Access current page content (only when you click the icon)
- **scripting**: Inject content script to extract text
- **storage**: Cache preferences (grade level selection)
- **Host permissions**: Connect to your API endpoint

**No data is collected or sent to third parties.** All text extraction happens locally, and summaries are only sent to your configured API endpoint.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License

## Support

For issues or questions, please open an issue in the repository.

## Changelog

### Version 2.0 (Latest)
- Added Adult TLDR option
- Implemented smart bullet counts by grade category
- Added Safe Summary Mode for K-5
- Vocabulary Builder with 3-6 terms per explanation
- PDF download functionality
- Email summary feature
- Shareable links with SQLite database
- API endpoint for integrations
- Fully responsive mobile design

### Version 1.0
- Basic explanation functionality
- URL extraction
- Grade level selection K-12
- Simple explanations with 2 bullets
