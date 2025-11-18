# Explain This for Kids 📚

A simple web app that takes complex text or article URLs and explains them at any grade level (K-12).

## Features

- **Dual Input**: Paste raw text OR a URL to an article
- **Auto URL Detection**: Automatically detects and fetches content from URLs
- **Article Extraction**: Uses BeautifulSoup to extract readable text from web pages
- **Grade Level Selection**: Choose explanation level from Kindergarten through 12th grade
- **AI-Powered**: Uses Claude AI to generate age-appropriate explanations
- **Clean Results**: Provides a title, explanation, and "Why this matters" bullets

## Project Structure

```
explain-this-for-kids/
├── app.py                  # Flask backend with Claude API integration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── templates/
│   └── index.html         # Main page template
└── static/
    ├── style.css          # Styling
    └── main.js            # Frontend JavaScript
```

## Setup & Installation

### Prerequisites

- Python 3.8 or higher
- A Claude API key from Anthropic

### Step-by-Step Runbook

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

# Edit .env and add your Claude API key
# On Mac/Linux:
nano .env

# On Windows:
notepad .env
```

Inside `.env`, replace `your_api_key_here` with your actual Claude API key:
```
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxx
```

**Getting a Claude API Key:**
- Go to https://console.anthropic.com/
- Sign up or log in
- Navigate to API Keys section
- Create a new API key
- Copy and paste it into your `.env` file

#### 5. Run the Flask application

```bash
python app.py
```

You should see output like:
```
* Running on http://0.0.0.0:5000
* Running on http://127.0.0.1:5000
```

#### 6. Open in your browser

Go to: **http://localhost:5000**

#### 7. Test the application

**Test with raw text:**
1. Paste some complex text into the textarea
2. Select a grade level
3. Click "Explain it!"

**Test with a URL:**
1. Paste an article URL (e.g., from a news site)
2. Select a grade level
3. Click "Explain it!"

## Usage

1. **Enter Content**: Paste text or a URL into the large text area
2. **Select Grade**: Choose the appropriate grade level from the dropdown
3. **Get Explanation**: Click "Explain it!" and wait for the AI-generated explanation
4. **View Results**: See the simplified title, explanation, and "Why this matters" bullets

## How It Works

### Backend (app.py)

1. **URL Detection**: Checks if input starts with `http://` or `https://` and has no line breaks
2. **Article Extraction**:
   - Fetches the URL with proper headers
   - Uses BeautifulSoup to parse HTML
   - Removes scripts, styles, and navigation
   - Extracts text from `<article>`, `<main>`, or `<p>` tags
   - Returns error if extraction yields less than 100 characters
3. **Claude API Call**:
   - Constructs a structured prompt with the content and grade level
   - Calls Claude API (claude-sonnet-4 model)
   - Parses response into title, explanation, and bullet points
4. **Response**: Returns JSON with formatted results

### Frontend

- **index.html**: Clean form with textarea, dropdown, and result display areas
- **main.js**: Handles form submission via fetch API, shows loading state, displays results
- **style.css**: Modern gradient design with responsive layout

## Troubleshooting

### "CLAUDE_API_KEY not found"
- Make sure you created the `.env` file
- Verify the API key is correctly set in `.env`
- Check that you're running the app from the same directory as `.env`

### "Could not read that link"
- The URL might be behind a paywall or require authentication
- Try copying the text manually instead
- Some sites block automated scraping

### Port already in use
```bash
# Kill the process using port 5000
# On Mac/Linux:
lsof -ti:5000 | xargs kill -9

# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP library for fetching URLs
- **beautifulsoup4**: HTML parsing and content extraction
- **python-dotenv**: Environment variable management
- **anthropic**: Official Claude API client

## License

MIT

## Support

For issues or questions, please open an issue in the repository.
