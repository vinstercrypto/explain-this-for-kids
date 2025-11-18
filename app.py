import os
import re
import requests
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get Claude API key from environment
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
if not CLAUDE_API_KEY:
    print("WARNING: CLAUDE_API_KEY not found in environment variables!")

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


def is_url(text):
    """Check if the input text looks like a URL."""
    text = text.strip()
    # Must start with http:// or https:// and have no line breaks
    if '\n' in text or '\r' in text:
        return False
    return text.startswith('http://') or text.startswith('https://')


def extract_article_text(url):
    """Fetch URL and extract readable article text."""
    try:
        # Fetch the page with a timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            script.decompose()

        # Try to find main content
        # Priority: article tag, main tag, or all paragraphs
        text = ""
        article = soup.find('article')
        if article:
            text = article.get_text(separator=' ', strip=True)
        else:
            main = soup.find('main')
            if main:
                text = main.get_text(separator=' ', strip=True)
            else:
                # Fall back to all paragraphs
                paragraphs = soup.find_all('p')
                text = ' '.join([p.get_text(strip=True) for p in paragraphs])

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Check if we got meaningful content (at least 100 characters)
        if len(text) < 100:
            return None

        return text

    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None


def call_claude_api(content, grade_level):
    """Call Claude API to explain content at the specified grade level."""
    prompt = f"""Rewrite or summarize the following content so that a {grade_level} student can understand it.

Please format your response EXACTLY as follows:
1) First line: A short clear title (no label, just the title)
2) Then a blank line
3) Then 3-5 sentences of explanation
4) Then a blank line
5) Then "Why this matters:" on its own line
6) Then exactly 2 bullet points (use • or -) explaining real-world relevance for kids at this grade level

CONTENT:
{content}"""

    try:
        client = get_claude_client()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the response text
        response_text = message.content[0].text

        # Parse the response
        lines = response_text.strip().split('\n')

        # Extract title (first non-empty line)
        title = ""
        explanation_lines = []
        why_matters_bullets = []

        section = "title"

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if section == "title":
                title = line
                section = "explanation"
            elif "why this matters" in line.lower():
                section = "why_matters"
            elif section == "explanation":
                if "why this matters" in line.lower():
                    section = "why_matters"
                else:
                    explanation_lines.append(line)
            elif section == "why_matters":
                # Extract bullet points
                clean_line = line.lstrip('•-*').strip()
                if clean_line:
                    why_matters_bullets.append(clean_line)

        explanation = ' '.join(explanation_lines)

        # Ensure we have at least 2 bullet points
        if len(why_matters_bullets) < 2:
            why_matters_bullets = [
                "This helps you understand important ideas in the world around you.",
                "Learning this can help you make better decisions and ask good questions."
            ]

        return {
            "title": title or "Explanation",
            "explanation": explanation or response_text,
            "why_it_matters": why_matters_bullets[:2]  # Take only first 2
        }

    except Exception as e:
        print(f"Error calling Claude API: {e}")
        raise


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/explain', methods=['POST'])
def explain():
    """Process the explanation request."""
    try:
        # Get form data
        input_text = request.form.get('input_text', '').strip()
        grade_level = request.form.get('grade_level', '5th grade')

        if not input_text:
            return jsonify({
                'success': False,
                'error': 'Please enter some text or a URL to explain.'
            })

        # Check if input is a URL
        if is_url(input_text):
            print(f"Detected URL: {input_text}")
            extracted_text = extract_article_text(input_text)

            if not extracted_text:
                return jsonify({
                    'success': False,
                    'error': 'Could not read that link. Please copy and paste the text manually.'
                })

            content = extracted_text
        else:
            content = input_text

        # Limit content length to avoid token limits
        if len(content) > 10000:
            content = content[:10000] + "..."

        # Call Claude API
        result = call_claude_api(content, grade_level)

        return jsonify({
            'success': True,
            'title': result['title'],
            'explanation': result['explanation'],
            'why_it_matters': result['why_it_matters']
        })

    except Exception as e:
        print(f"Error in /explain: {e}")
        return jsonify({
            'success': False,
            'error': 'Something went wrong. Please try again.'
        })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
