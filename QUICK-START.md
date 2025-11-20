# Summarize It! - 5-Minute Quick Start

**For non-developers who just want to test the app**

---

## ⚠️ IMPORTANT: You Need These First

1. **Claude API Key** (costs money - minimum $10 prepaid)
   - Sign up: https://console.anthropic.com/
   - Add payment method
   - Create API key (starts with `sk-ant-`)

2. **Python 3.8+** installed
   - Windows: https://www.python.org/downloads/
   - CHECK "Add Python to PATH" during install

---

## Windows: 5 Steps to Run

### 1. Open Command Prompt
Press `Windows Key + R`, type `cmd`, press Enter

### 2. Go to project folder
```bash
cd C:\path\to\explain-this-for-kids
```
Replace with your actual folder location

### 3. Install dependencies
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Add your API key
```bash
notepad .env
```

Change this line:
```
CLAUDE_API_KEY=your_api_key_here
```

To your REAL key:
```
CLAUDE_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx
```

Save and close Notepad

### 5. Start the app
```bash
python app.py
```

Open browser: http://localhost:5000

---

## Mac/Linux: 5 Steps to Run

### 1. Open Terminal

### 2. Go to project folder
```bash
cd /path/to/explain-this-for-kids
```

### 3. Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Add your API key
```bash
nano .env
```

Change:
```
CLAUDE_API_KEY=your_api_key_here
```

To your real key:
```
CLAUDE_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx
```

Press `Ctrl+X`, then `Y`, then Enter to save

### 5. Start the app
```bash
python app.py
```

Open browser: http://localhost:5000

---

## First Test

1. Paste this in the text box:
   ```
   The Great Wall of China is over 13,000 miles long and was built over many centuries to protect China from invasions.
   ```

2. Select "5th grade" from dropdown

3. Click "Simplify It!"

4. You should see a summary with vocabulary and bullets

**If it works:** ✅ You're done! Try pasting Wikipedia URLs, news articles, etc.

**If it fails:**
- Check that your API key starts with `sk-ant-`
- Make sure you restarted the app after changing `.env`
- Check you have internet connection (needs to call Claude API)

---

## Chrome Extension Setup (Optional)

**Only do this after the web app works.**

### 1. Configure extension

Edit `chrome-extension/popup.js` line 3:

```javascript
const API_BASE_URL = 'http://localhost:5000';  // Change from example.com
```

Edit `chrome-extension/manifest.json`:

```json
"host_permissions": [
  "http://localhost:5000/*"  // Change from example.com
]
```

### 2. Load in Chrome

1. Go to `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder
5. Click the extension icon on any webpage

---

## Costs (Important!)

- Each summary costs ~$0.01-0.05 in Claude API fees
- $10 prepaid = roughly 200-500 summaries
- Monitor usage: https://console.anthropic.com/settings/usage

---

## Help

**"CLAUDE_API_KEY not found"**
- You didn't update `.env` file
- Or you didn't restart the app after changing it

**"Could not read that link"**
- Website is blocking automated access
- Copy/paste the article text instead

**"Error calling Claude API"**
- Check your API key is valid
- Check you have credits: https://console.anthropic.com/settings/billing

**Extension doesn't work**
- Make sure web app is running (localhost:5000)
- Check you edited popup.js and manifest.json
- Reload extension from chrome://extensions

---

**For full documentation, see:** `AUDIT-REPORT.md` or `README.md`
