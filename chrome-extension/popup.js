// Configuration
// TODO: Replace with your deployed API URL
const API_BASE_URL = 'https://example.com';
const API_ENDPOINT = `${API_BASE_URL}/api/explain`;

// TODO: Replace with your actual donate URL when ready
const DONATE_URL = 'https://example.com/donate';

// State
let extractedText = '';
let shareUrl = '';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set up donate link
    const donateLink = document.getElementById('donate-link');
    if (donateLink) {
        donateLink.href = DONATE_URL;
    }

    // Set up button click handler
    const simplifyBtn = document.getElementById('simplify-btn');
    simplifyBtn.addEventListener('click', handleSimplify);

    // Set up copy link handler
    const copyLinkBtn = document.getElementById('copy-link-btn');
    if (copyLinkBtn) {
        copyLinkBtn.addEventListener('click', handleCopyLink);
    }

    // Extract text from current page
    extractPageText();
});

/**
 * Extract text from the active tab
 */
async function extractPageText() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Inject and execute content script if needed
        const response = await chrome.tabs.sendMessage(tab.id, { action: 'extractText' });

        if (response && response.text) {
            extractedText = response.text;
            console.log('Extracted text length:', extractedText.length);
        } else {
            console.warn('No text extracted from page');
            extractedText = '';
        }
    } catch (error) {
        console.error('Error extracting text:', error);
        // If content script not ready, the page might not have loaded yet
        extractedText = '';
    }
}

/**
 * Handle "Simplify It!" button click
 */
async function handleSimplify() {
    const gradeLevel = document.getElementById('grade-level').value;

    // Validate extracted text
    if (!extractedText || extractedText.trim().length < 50) {
        showError('Not enough readable text found on this page. Please try a different page with more content.');
        return;
    }

    // Show loading state
    showLoading();

    try {
        // Call API
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: extractedText,
                grade_level: gradeLevel
            })
        });

        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            renderResults(data);
        } else {
            throw new Error(data.error || 'Unknown error');
        }

    } catch (error) {
        console.error('API Error:', error);
        showError('Could not summarize this page. Please try again.');
    } finally {
        hideLoading();
    }
}

/**
 * Render the summary results
 */
function renderResults(data) {
    // Hide input section
    document.getElementById('input-section').style.display = 'none';

    // Show result section
    const resultSection = document.getElementById('result');
    resultSection.style.display = 'block';

    // Render title
    document.getElementById('result-title').textContent = data.title || 'Summary';

    // Render explanation
    document.getElementById('result-explanation').textContent = data.explanation || '';

    // Render bullets with correct heading
    const bulletsHeading = document.getElementById('bullets-heading');
    const bulletsList = document.getElementById('result-bullets');

    if (data.mode === 'adult_tldr') {
        bulletsHeading.textContent = 'Key takeaways:';
    } else {
        bulletsHeading.textContent = 'Why this matters:';
    }

    // Clear and populate bullets
    bulletsList.innerHTML = '';
    if (data.why_it_matters && data.why_it_matters.length > 0) {
        data.why_it_matters.forEach(bullet => {
            const li = document.createElement('li');
            li.textContent = bullet;
            bulletsList.appendChild(li);
        });
    }

    // Render vocabulary (only for kids mode)
    const vocabSection = document.getElementById('vocabulary-section');
    if (data.mode === 'kids' && data.vocabulary && data.vocabulary.length > 0) {
        vocabSection.style.display = 'block';
        const vocabList = document.getElementById('result-vocabulary');
        vocabList.innerHTML = '';

        data.vocabulary.forEach(item => {
            const vocabItem = document.createElement('div');
            vocabItem.className = 'vocab-item';
            vocabItem.innerHTML = `<strong>${item.word}:</strong> ${item.definition}`;
            vocabList.appendChild(vocabItem);
        });
    } else {
        vocabSection.style.display = 'none';
    }

    // Render MLA citation (if provided)
    const mlaSection = document.getElementById('mla-section');
    if (data.mla_citation) {
        mlaSection.style.display = 'block';
        document.getElementById('result-mla-citation').textContent = data.mla_citation;
    } else {
        mlaSection.style.display = 'none';
    }

    // Handle share URL
    const shareSection = document.getElementById('share-section');
    if (data.share_url) {
        shareUrl = `${API_BASE_URL}${data.share_url}`;
        shareSection.style.display = 'block';
    } else {
        shareSection.style.display = 'none';
    }

    // Scroll to top of results
    document.querySelector('.container').scrollTop = 0;
}

/**
 * Handle copy share link
 */
async function handleCopyLink() {
    if (!shareUrl) return;

    try {
        await navigator.clipboard.writeText(shareUrl);
        showCopyFeedback('✓ Link copied!');
    } catch (error) {
        console.error('Copy failed:', error);
        showCopyFeedback('✗ Copy failed');
    }
}

/**
 * Show copy feedback message
 */
function showCopyFeedback(message) {
    const feedback = document.getElementById('copy-feedback');
    feedback.textContent = message;
    feedback.style.color = message.includes('✓') ? '#28a745' : '#dc3545';

    setTimeout(() => {
        feedback.textContent = '';
    }, 2000);
}

/**
 * Show loading state
 */
function showLoading() {
    document.getElementById('input-section').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('result').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
}

/**
 * Hide loading state
 */
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

/**
 * Show error message
 */
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';

    document.getElementById('input-section').style.display = 'block';
    document.getElementById('result').style.display = 'none';
}
