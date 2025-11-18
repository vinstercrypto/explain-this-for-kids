# Summarize It! - Chrome Extension

Transform any webpage into a clear, grade-appropriate summary with one click.

## Quick Start

### 1. Configure API Endpoint

**Edit `popup.js` (lines 3-7):**

```javascript
const API_BASE_URL = 'https://your-deployed-app.com';  // TODO: Change this
const DONATE_URL = 'https://your-donate-link.com';     // TODO: Optional
```

**Edit `manifest.json` (host_permissions):**

```json
"host_permissions": [
  "https://your-deployed-app.com/*"  // TODO: Match your API URL
]
```

### 2. Load in Chrome

1. Open `chrome://extensions/`
2. Enable **Developer mode** (top right toggle)
3. Click **Load unpacked**
4. Select this `chrome-extension/` folder
5. Extension icon appears in toolbar

### 3. Use It

1. Navigate to any article or webpage
2. Click the extension icon
3. Select grade level (K-12 or Adult TLDR)
4. Click "Simplify It!"
5. Get instant summary with vocabulary and citation

## Features

✅ **One-click summarization** of any webpage
✅ **Smart text extraction** (filters ads, nav, etc.)
✅ **K-12 + Adult TLDR modes** with appropriate content
✅ **Vocabulary Builder** (K-12 only)
✅ **MLA Citation Draft** for URL sources
✅ **Share link copying**
✅ **Responsive popup design**

## File Structure

```
chrome-extension/
├── manifest.json          # Chrome extension config
├── popup.html            # Extension UI
├── popup.css             # Styling
├── popup.js              # Main logic + API calls
├── contentScript.js      # Text extraction
└── icons/
    ├── generate-icons.py # Icon generator script
    ├── icon16.png        # 16x16 icon
    ├── icon32.png        # 32x32 icon
    ├── icon48.png        # 48x48 icon
    └── icon128.png       # 128x128 icon
```

## How It Works

### Text Extraction (contentScript.js)

When you click "Simplify It!":

1. Searches for main content (`<article>`, `<main>`, etc.)
2. Excludes navigation, headers, footers, ads
3. Extracts visible paragraphs and headings
4. Cleans and normalizes text
5. Sends to API endpoint

### API Integration (popup.js)

```javascript
// POST request to /api/explain
{
  "text": "<extracted text>",
  "grade_level": "5th grade"
}

// Response handling
{
  "success": true,
  "title": "...",
  "explanation": "...",
  "why_it_matters": [...],    // or "key takeaways" for Adult TLDR
  "vocabulary": [...],         // K-12 only
  "mla_citation": "...",       // If URL source
  "share_url": "/s/abc123",
  "mode": "kids" or "adult_tldr"
}
```

### Smart Rendering

**Kids Mode (K-12):**
- Heading: "Why this matters"
- Shows Vocabulary Builder
- Full explanations

**Adult TLDR Mode:**
- Heading: "Key takeaways"
- NO vocabulary (concise)
- Brief bullet points

## Configuration

### Required Changes Before Installing

**1. API URL** (`popup.js` line 3):
```javascript
const API_BASE_URL = 'https://your-app.com';
```

**2. Host Permissions** (`manifest.json`):
```json
"host_permissions": ["https://your-app.com/*"]
```

### Optional Changes

**Donate URL** (`popup.js` line 7):
```javascript
const DONATE_URL = 'https://ko-fi.com/yourname';
```

**Icons** (see `icons/GENERATE-ICONS.md`):
- Run `python3 icons/generate-icons.py`
- Or use ImageMagick/Inkscape for custom designs

## Troubleshooting

### Extension doesn't load
- Check `manifest.json` for syntax errors
- Ensure you selected the `chrome-extension/` folder, not a subfolder
- Reload extension from `chrome://extensions/`

### "Not enough readable text found"
- Page has minimal content
- Try a different article with more text
- Some sites use heavy JavaScript (extraction may fail)

### API errors
- Verify `API_BASE_URL` matches your deployed app
- Check `host_permissions` in manifest
- Enable CORS on your Flask API (use Flask-CORS)
- Open DevTools (F12) → Console for detailed errors

### Vocabulary not showing
- Expected for Adult TLDR mode
- Select a K-12 grade level to see vocabulary

### MLA citation missing
- Citations only appear for URL sources (not pasted text)
- Extension auto-detects webpage URLs
- Check API response includes `mla_citation` field

## Development

### Testing Locally

If testing against `localhost:5000`:

```javascript
// popup.js
const API_BASE_URL = 'http://localhost:5000';
```

```json
// manifest.json
"host_permissions": ["http://localhost:5000/*"]
```

### Debugging

1. Open DevTools in popup: Right-click extension icon → Inspect
2. View content script logs: F12 on any webpage → Console
3. Check network requests: DevTools → Network tab

### Making Changes

After modifying any file:
1. Go to `chrome://extensions/`
2. Click reload icon on the extension card
3. Test the changes

## Publishing to Chrome Web Store

1. Create developer account ($5 one-time fee)
2. Prepare assets:
   - Icons: 16, 32, 48, 128px
   - Screenshots: 1280x800 or 640x400
   - Promotional images: 440x280 (required)
3. Zip the extension folder
4. Upload to Chrome Web Store Developer Dashboard
5. Fill in description, category, pricing
6. Submit for review (1-2 day turnaround)

## Privacy

This extension:
- ✅ Only accesses page content when you click the icon
- ✅ Sends extracted text to YOUR configured API only
- ✅ No third-party data collection
- ✅ No tracking or analytics
- ✅ Open source and transparent

Required permissions:
- **activeTab**: Read current page content (on click only)
- **scripting**: Inject text extraction script
- **storage**: Save grade level preference
- **host_permissions**: Connect to your API

## License

MIT License - Same as the main Summarize It! application

## Support

For issues or questions, see the main repository README or open an issue.
