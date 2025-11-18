import os
import re
import json
import secrets
import sqlite3
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse
import requests
from flask import Flask, render_template, request, jsonify, session, send_file, url_for
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fpdf import FPDF, XPos, YPos
import anthropic
from io import BytesIO

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Get Claude API key from environment
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
if not CLAUDE_API_KEY:
    print("WARNING: CLAUDE_API_KEY not found in environment variables!")

# SMTP settings
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', '')

# Optional donate URL
DONATE_URL = os.getenv('DONATE_URL', '')

# Database file
DB_FILE = 'summaries.db'

# Client will be initialized when needed
_client = None


def get_claude_client():
    """Get or create the Anthropic client."""
    global _client
    if _client is None:
        if not CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY not set in environment variables")
        _client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    return _client


def init_db():
    """Initialize SQLite database for shareable summaries."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id TEXT PRIMARY KEY,
            created_at TEXT,
            grade_level TEXT,
            category TEXT,
            title TEXT,
            explanation TEXT,
            bullets TEXT,
            vocabulary TEXT,
            source_url TEXT,
            mla_citation TEXT
        )
    ''')

    # Add new columns to existing tables (migration for older databases)
    try:
        cursor.execute('ALTER TABLE summaries ADD COLUMN source_url TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

    try:
        cursor.execute('ALTER TABLE summaries ADD COLUMN mla_citation TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()


def get_grade_category(grade_level):
    """Map grade level to category A/B/C/D."""
    if grade_level in ['Kindergarten', '1st grade', '2nd grade', '3rd grade', '4th grade', '5th grade']:
        return 'A'  # K-5
    elif grade_level in ['6th grade', '7th grade', '8th grade']:
        return 'B'  # 6-8
    elif grade_level in ['9th grade', '10th grade', '11th grade', '12th grade']:
        return 'C'  # 9-12
    elif grade_level == 'Adult TLDR':
        return 'D'  # Adult
    return 'A'  # Default to K-5


def get_bullet_count(category):
    """Get bullet count based on category."""
    bullet_counts = {
        'A': 2,  # K-5
        'B': 3,  # 6-8
        'C': 5,  # 9-12
        'D': 5   # Adult TLDR
    }
    return bullet_counts.get(category, 2)


def build_prompt(content, grade_level, category):
    """Build Claude prompt based on grade level and category."""
    bullet_count = get_bullet_count(category)

    # Safe summary instructions for K-5
    if category == 'A':
        safe_instructions = """
IMPORTANT - SAFE SUMMARY MODE FOR YOUNG LEARNERS:
- Avoid graphic violence, gore, explicit content, self-harm, or detailed crime descriptions
- If the content contains sensitive topics, acknowledge them gently (e.g., "something serious happened") without graphic details
- Use age-appropriate language and avoid partisan political framing or inflammatory language
- Focus on educational value and positive learning outcomes

"""
    else:
        safe_instructions = ""

    # Adult TLDR format - EXTREMELY CONCISE, NO VOCABULARY
    if category == 'D':
        prompt = f"""{safe_instructions}You are producing an Adult TLDR summary. Follow these rules strictly:

GOAL:
Provide a fast, high-signal summary an adult can read in under 10 seconds.

STRUCTURE (mandatory - use these exact labels):

TITLE:
[Write a clear, factual, concise title in 1 line max. No drama. No phrases like "Why this matters" or "Summary of..."]

TLDR:
[Write 1-2 sentences capturing the essential fact or change. Stay extremely compact.]

KEY TAKEAWAYS:
[Write 3-5 bullet points using this format: "• [point]"]
[Each bullet must be SHORT and DIRECT - one line each]
[No storytelling. No restating the TLDR.]
[Focus on impact, implications, or what changed]

ADDITIONAL RULES:
- Do NOT include vocabulary definitions or extra sections
- Do NOT mimic a school assignment
- Remove redundancy between TLDR and bullets
- Total output should be very brief (aim for roughly 60-70 words total)
- This is for busy adults who need information fast

CONTENT:
{content}"""

    else:
        # K-12 format with vocabulary
        if category == 'A':
            age_guidance = "Use simple, age-appropriate language suitable for young children (K-5)."
        elif category == 'B':
            age_guidance = "Use language appropriate for middle school students (6-8 grade)."
        else:  # category == 'C'
            age_guidance = "Use language appropriate for high school students (9-12 grade)."

        prompt = f"""{safe_instructions}Rewrite or summarize the following content so that a {grade_level} student can understand it.

{age_guidance}

STRUCTURE (mandatory - use these exact labels):

TITLE:
[Write a short, clear title]

EXPLANATION:
[Write a {grade_level}-appropriate explanation in 3-5 sentences]

WHY THIS MATTERS:
[Write exactly {bullet_count} bullet points using this format: "• [point]"]
[Each bullet should explain real-world relevance for {grade_level} students]

VOCABULARY:
[List 3-6 key words with simple definitions appropriate for {grade_level}]
[Format each as: "• WORD: definition"]

CONTENT:
{content}"""

    return prompt


def parse_claude_response(response_text, category):
    """Parse Claude's response into structured data with clear markers."""
    lines = response_text.strip().split('\n')

    title = ""
    explanation_lines = []
    why_matters_bullets = []
    vocabulary_items = []

    section = None

    for line in lines:
        line_stripped = line.strip()

        # Skip empty lines and bracket instructions
        if not line_stripped or line_stripped.startswith('['):
            continue

        # Detect section headers
        line_upper = line_stripped.upper()

        if line_upper == "TITLE:":
            section = "title"
            continue
        elif line_upper == "EXPLANATION:":
            section = "explanation"
            continue
        elif line_upper == "TLDR:":
            section = "tldr"
            continue
        elif line_upper in ["WHY THIS MATTERS:", "KEY TAKEAWAYS:"]:
            section = "bullets"
            continue
        elif line_upper == "VOCABULARY:":
            section = "vocabulary"
            continue

        # Process content based on current section
        if section == "title":
            if not title:  # Take only the first line after TITLE:
                title = line_stripped
        elif section == "explanation":
            explanation_lines.append(line_stripped)
        elif section == "tldr":
            explanation_lines.append(line_stripped)
        elif section == "bullets":
            clean_line = line_stripped.lstrip('•-*').strip()
            if clean_line:
                why_matters_bullets.append(clean_line)
        elif section == "vocabulary":
            clean_line = line_stripped.lstrip('•-*').strip()
            if ':' in clean_line:
                parts = clean_line.split(':', 1)
                word = parts[0].strip()
                definition = parts[1].strip()
                vocabulary_items.append({"word": word, "definition": definition})

    # Build explanation
    explanation = ' '.join(explanation_lines) if explanation_lines else response_text

    # Determine mode and finalize vocabulary
    mode = "adult_tldr" if category == 'D' else "kids"

    if category == 'D':
        # Adult TLDR: No vocabulary
        vocabulary_items = []
    else:
        # K-12: Ensure minimum vocabulary items
        if len(vocabulary_items) < 3:
            vocabulary_items = [
                {"word": "Context", "definition": "The circumstances or setting surrounding something"},
                {"word": "Summary", "definition": "A brief statement of the main points"},
                {"word": "Explanation", "definition": "A description that makes something clear"}
            ]
        vocabulary_items = vocabulary_items[:6]  # Limit to 6

    # Enforce bullet count
    expected_count = get_bullet_count(category)
    if len(why_matters_bullets) > expected_count:
        why_matters_bullets = why_matters_bullets[:expected_count]
    elif len(why_matters_bullets) < expected_count and category != 'D':
        # Pad K-12 if needed (Adult TLDR can have 3-5)
        while len(why_matters_bullets) < expected_count:
            why_matters_bullets.append("This helps you understand important ideas in the world.")

    return {
        "title": title or "Summary",
        "explanation": explanation,
        "why_it_matters": why_matters_bullets,
        "vocabulary": vocabulary_items,
        "mode": mode
    }


def is_url(text):
    """Check if the input text looks like a URL."""
    text = text.strip()
    if '\n' in text or '\r' in text:
        return False
    return text.startswith('http://') or text.startswith('https://')


def extract_article_text(url):
    """Fetch URL and extract readable article text plus metadata for MLA citation."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract page title for MLA citation
        page_title = None

        # Try og:title first (often cleaner)
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            page_title = og_title.get('content').strip()

        # Fallback to <title> tag
        if not page_title:
            title_tag = soup.find('title')
            if title_tag:
                page_title = title_tag.get_text().strip()

        # Extract domain for MLA citation
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')

        # Extract article text
        for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            script.decompose()

        text = ""
        article = soup.find('article')
        if article:
            text = article.get_text(separator=' ', strip=True)
        else:
            main = soup.find('main')
            if main:
                text = main.get_text(separator=' ', strip=True)
            else:
                paragraphs = soup.find_all('p')
                text = ' '.join([p.get_text(strip=True) for p in paragraphs])

        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) < 100:
            return None

        return {
            'text': text,
            'page_title': page_title,
            'domain': domain
        }

    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None


def generate_mla_citation(url, page_title=None, domain=None):
    """Generate a basic MLA 9 style web citation."""
    # Get current date for access date
    now = datetime.now(timezone.utc)
    access_date = now.strftime("%d %b. %Y")  # e.g., "15 Jan. 2025"

    # Parse URL if domain not provided
    if not domain:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')

    # Use fallback title if not provided
    if not page_title or page_title.strip() == '':
        page_title = f"Web page at {domain}"

    # Clean up page title (remove site name if it appears at end after pipe or dash)
    if ' | ' in page_title:
        page_title = page_title.split(' | ')[0].strip()
    elif ' - ' in page_title:
        page_title = page_title.split(' - ')[0].strip()

    # MLA 9 format: Title. Website/Domain, URL. Accessed Date.
    # Capitalize first letter of domain for site name
    site_name = domain.split('.')[0].capitalize() if domain else "Website"

    citation = f'"{page_title}." {site_name}, {url}. Accessed {access_date}.'

    return citation


def call_claude_api(content, grade_level):
    """Call Claude API to explain content at the specified grade level."""
    category = get_grade_category(grade_level)
    prompt = build_prompt(content, grade_level, category)

    try:
        client = get_claude_client()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response_text = message.content[0].text
        result = parse_claude_response(response_text, category)

        # Ensure correct bullet count
        expected_count = get_bullet_count(category)
        if len(result['why_it_matters']) < expected_count:
            # Pad with generic bullets if needed
            while len(result['why_it_matters']) < expected_count:
                result['why_it_matters'].append("This helps you understand important ideas in the world.")
        result['why_it_matters'] = result['why_it_matters'][:expected_count]

        return result

    except Exception as e:
        print(f"Error calling Claude API: {e}")
        raise


def save_summary_to_db(grade_level, category, title, explanation, bullets, vocabulary, source_url=None, mla_citation=None):
    """Save summary to database and return short ID."""
    summary_id = secrets.token_urlsafe(8)
    created_at = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO summaries (id, created_at, grade_level, category, title, explanation, bullets, vocabulary, source_url, mla_citation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        summary_id,
        created_at,
        grade_level,
        category,
        title,
        explanation,
        json.dumps(bullets),
        json.dumps(vocabulary),
        source_url,
        mla_citation
    ))
    conn.commit()
    conn.close()

    return summary_id


def get_summary_by_id(summary_id):
    """Retrieve summary from database by ID."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM summaries WHERE id = ?', (summary_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        'id': row[0],
        'created_at': row[1],
        'grade_level': row[2],
        'category': row[3],
        'title': row[4],
        'explanation': row[5],
        'bullets': json.loads(row[6]),
        'vocabulary': json.loads(row[7]),
        'source_url': row[8] if len(row) > 8 else None,
        'mla_citation': row[9] if len(row) > 9 else None
    }


def process_explanation(input_text, grade_level):
    """Core function to process explanation - used by both form and API."""
    if not input_text:
        raise ValueError('Please enter some text or a URL to explain.')

    # Initialize MLA-related fields
    source_url = None
    mla_citation = None

    # Check if input is a URL
    if is_url(input_text):
        print(f"Detected URL: {input_text}")
        extracted_data = extract_article_text(input_text)

        if not extracted_data:
            raise ValueError('Could not read that link. Please copy and paste the text manually.')

        content = extracted_data['text']
        source_url = input_text

        # Generate MLA citation
        mla_citation = generate_mla_citation(
            url=input_text,
            page_title=extracted_data.get('page_title'),
            domain=extracted_data.get('domain')
        )
    else:
        content = input_text

    # Limit content length
    if len(content) > 10000:
        content = content[:10000] + "..."

    # Call Claude API
    result = call_claude_api(content, grade_level)

    # Save to database
    category = get_grade_category(grade_level)
    summary_id = save_summary_to_db(
        grade_level,
        category,
        result['title'],
        result['explanation'],
        result['why_it_matters'],
        result['vocabulary'],
        source_url,
        mla_citation
    )

    # Add share URL and MLA fields to result
    result['share_url'] = f"/s/{summary_id}"
    result['summary_id'] = summary_id
    result['source_url'] = source_url
    result['mla_citation'] = mla_citation

    return result


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', donate_url=DONATE_URL)


@app.route('/explain', methods=['POST'])
def explain():
    """Process the explanation request from HTML form."""
    try:
        input_text = request.form.get('input_text', '').strip()
        grade_level = request.form.get('grade_level', '5th grade')

        result = process_explanation(input_text, grade_level)

        # Store in session for PDF/email features
        session['last_result'] = {
            'input_text': input_text[:500],  # Truncate to avoid large session
            'grade_level': grade_level,
            'title': result['title'],
            'explanation': result['explanation'],
            'why_it_matters': result['why_it_matters'],
            'vocabulary': result['vocabulary'],
            'mode': result['mode'],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'summary_id': result['summary_id'],
            'source_url': result.get('source_url'),
            'mla_citation': result.get('mla_citation')
        }

        return jsonify({
            'success': True,
            'title': result['title'],
            'explanation': result['explanation'],
            'why_it_matters': result['why_it_matters'],
            'vocabulary': result['vocabulary'],
            'mode': result['mode'],
            'share_url': result['share_url'],
            'mla_citation': result.get('mla_citation')
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
    except Exception as e:
        print(f"Error in /explain: {e}")
        return jsonify({
            'success': False,
            'error': 'Something went wrong. Please try again.'
        })


@app.route('/api/explain', methods=['POST'])
def api_explain():
    """API endpoint for Chrome extension and other integrations."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON data'
            }), 400

        input_text = data.get('text', '').strip()
        grade_level = data.get('grade_level', '5th grade')

        result = process_explanation(input_text, grade_level)

        return jsonify({
            'success': True,
            'title': result['title'],
            'explanation': result['explanation'],
            'why_it_matters': result['why_it_matters'],
            'vocabulary': result['vocabulary'],
            'mode': result['mode'],
            'share_url': result['share_url'],
            'mla_citation': result.get('mla_citation')
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"Error in /api/explain: {e}")
        return jsonify({
            'success': False,
            'error': 'Something went wrong. Please try again.'
        }), 500


@app.route('/s/<summary_id>')
def view_summary(summary_id):
    """View a shared summary by ID."""
    summary = get_summary_by_id(summary_id)

    if not summary:
        return render_template('404.html'), 404

    return render_template('summary.html', summary=summary, donate_url=DONATE_URL)


@app.route('/download-pdf')
def download_pdf():
    """Generate and download PDF of last result."""
    try:
        if 'last_result' not in session:
            return "No result to download. Please generate an explanation first.", 400

        result = session['last_result']

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title
        pdf.set_font('Helvetica', 'B', 16)
        pdf.multi_cell(0, 10, txt=result['title'])
        pdf.ln(5)

        # Grade level
        pdf.set_font('Helvetica', 'I', 10)
        pdf.cell(0, 10, txt=f"Grade Level: {result['grade_level']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

        # Explanation
        pdf.set_font('Helvetica', '', 11)
        # Clean up any problematic characters
        explanation_text = result['explanation'].replace('\n\n', '\n').strip()
        pdf.multi_cell(0, 6, txt=explanation_text)
        pdf.ln(5)

        # Why this matters
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, txt='Why this matters:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 11)

        for bullet in result['why_it_matters']:
            # Use dash instead of bullet character for compatibility
            bullet_text = bullet.strip()
            # Write bullet with proper indentation
            pdf.set_x(15)  # Indent
            pdf.multi_cell(0, 6, txt=f"- {bullet_text}")
        pdf.ln(5)

        # Vocabulary (only if present - Adult TLDR has no vocab)
        if result.get('vocabulary') and len(result['vocabulary']) > 0:
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, txt='Vocabulary:', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('Helvetica', '', 11)

            for item in result['vocabulary']:
                vocab_text = f"{item['word']}: {item['definition']}"
                pdf.set_x(15)  # Indent
                pdf.multi_cell(0, 6, txt=f"- {vocab_text}")
            pdf.ln(5)

        # MLA Citation (only if source was a URL)
        if result.get('mla_citation'):
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 10, txt='Citation draft (MLA-style):', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('Helvetica', 'I', 9)
            pdf.multi_cell(0, 5, txt=result['mla_citation'])
            pdf.set_font('Helvetica', '', 8)
            pdf.multi_cell(0, 4, txt='Check this citation against official MLA guidelines before use.')
            pdf.ln(3)

        # AI Disclaimer
        pdf.set_font('Helvetica', 'I', 8)
        pdf.multi_cell(0, 5, txt='This summary is AI-generated and may contain errors. Check the original source for full accuracy and context.')
        pdf.ln(5)

        # Timestamp
        pdf.set_font('Helvetica', 'I', 8)
        timestamp_display = result.get('timestamp', '').split('T')[0]  # Just the date
        pdf.cell(0, 10, txt=f"Generated: {timestamp_display}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Output to bytes
        pdf_output = pdf.output()
        buffer = BytesIO(pdf_output)
        buffer.seek(0)

        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='explanation.pdf'
        )

    except Exception as e:
        print(f"Error generating PDF: {e}")
        return f"Error generating PDF: {str(e)}. Please try again.", 500


@app.route('/email-summary', methods=['POST'])
def email_summary():
    """Email the last result to specified address."""
    if 'last_result' not in session:
        return jsonify({
            'success': False,
            'message': 'No result to email'
        }), 400

    email = request.form.get('email', '').strip()

    # Basic email validation
    if not email or '@' not in email or '.' not in email.split('@')[1] if '@' in email else True:
        return jsonify({
            'success': False,
            'message': 'Please enter a valid email address'
        })

    if not all([SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL]):
        return jsonify({
            'success': False,
            'message': 'Email not configured. Please contact administrator.'
        })

    result = session['last_result']

    # Build email content
    email_body = f"""
{result['title']}
{"=" * len(result['title'])}

Grade Level: {result['grade_level']}

EXPLANATION:
{result['explanation']}

WHY THIS MATTERS:
"""
    for bullet in result['why_it_matters']:
        email_body += f"  - {bullet}\n"

    # Only include vocabulary if present (not Adult TLDR)
    if result.get('vocabulary') and len(result['vocabulary']) > 0:
        email_body += "\nVOCABULARY:\n"
        for item in result['vocabulary']:
            email_body += f"  - {item['word']}: {item['definition']}\n"

    email_body += f"\n---\nGenerated by Explain This for Kids\n{result.get('timestamp', '')}"

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = email
        msg['Subject'] = f"Explain This for Kids: {result['title']}"

        msg.attach(MIMEText(email_body, 'plain'))

        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        return jsonify({
            'success': True,
            'message': f'Email sent to {email}'
        })

    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to send email. Please try again.'
        })


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
