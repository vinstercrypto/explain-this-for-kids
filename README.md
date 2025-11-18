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
  - Adult TLDR: 5 bullets + TLDR summary
- **Safe Summary Mode**: For K-5, content is filtered to avoid graphic violence, explicit content, and inappropriate topics
- **Vocabulary Builder**: 3-6 key terms with grade-appropriate definitions
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
- **Category D (Adult TLDR)**: TLDR + detailed explanation + 5 bullets

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

## Chrome Extension Integration

The `/api/explain` endpoint is designed for browser extensions. Example use cases:

1. Select text on any webpage
2. Right-click → "Explain This for Kids"
3. Extension calls your API endpoint
4. Show popup with explanation

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
