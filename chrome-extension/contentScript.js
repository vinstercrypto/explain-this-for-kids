/**
 * Content Script for Summarize It!
 * Extracts clean, readable text from web pages
 */

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractText') {
        const text = extractPageText();
        sendResponse({ text: text });
    }
    return true; // Keep the message channel open for async response
});

/**
 * Extract clean, readable text from the current page
 */
function extractPageText() {
    // Selectors to include (main content)
    const includeSelectors = [
        'article',
        'main',
        '[role="main"]',
        '.article',
        '.post',
        '.content',
        '.entry-content',
        '#content',
        '.main-content'
    ];

    // Selectors to exclude (navigation, ads, etc.)
    const excludeSelectors = [
        'nav',
        'header',
        'footer',
        'aside',
        '.nav',
        '.navigation',
        '.menu',
        '.sidebar',
        '.header',
        '.footer',
        '.advertisement',
        '.ad',
        '.ads',
        '.social',
        '.share',
        '.comments',
        '.comment',
        'script',
        'style',
        'noscript',
        'iframe',
        'button',
        '[role="navigation"]',
        '[role="banner"]',
        '[role="complementary"]'
    ];

    let extractedText = '';

    // Try to find main content area first
    let mainContent = null;
    for (const selector of includeSelectors) {
        mainContent = document.querySelector(selector);
        if (mainContent) {
            break;
        }
    }

    // If main content found, extract from there; otherwise use body
    const rootElement = mainContent || document.body;

    if (rootElement) {
        extractedText = extractTextFromElement(rootElement, excludeSelectors);
    }

    // Fallback: if very little text extracted, try getting all visible paragraphs
    if (extractedText.length < 200) {
        extractedText = extractFallbackText();
    }

    // Clean up the text
    extractedText = cleanText(extractedText);

    return extractedText;
}

/**
 * Extract text from an element, excluding certain selectors
 */
function extractTextFromElement(element, excludeSelectors) {
    // Clone the element to avoid modifying the DOM
    const clone = element.cloneNode(true);

    // Remove excluded elements
    excludeSelectors.forEach(selector => {
        const excludedElements = clone.querySelectorAll(selector);
        excludedElements.forEach(el => el.remove());
    });

    // Get text from important elements
    const textElements = clone.querySelectorAll('p, article, section, h1, h2, h3, li, blockquote, pre');
    let text = '';

    textElements.forEach(el => {
        // Only include visible elements
        if (isVisible(el)) {
            const elementText = el.textContent.trim();
            if (elementText.length > 20) { // Ignore very short snippets
                text += elementText + '\n\n';
            }
        }
    });

    return text;
}

/**
 * Fallback text extraction - get all visible paragraphs
 */
function extractFallbackText() {
    const paragraphs = document.querySelectorAll('p, h1, h2, h3');
    let text = '';

    paragraphs.forEach(p => {
        if (isVisible(p)) {
            const pText = p.textContent.trim();
            if (pText.length > 20) {
                text += pText + '\n\n';
            }
        }
    });

    return text;
}

/**
 * Check if an element is visible
 */
function isVisible(element) {
    // Check if element exists
    if (!element) return false;

    // Get computed style
    const style = window.getComputedStyle(element);

    // Check visibility
    if (style.display === 'none' ||
        style.visibility === 'hidden' ||
        style.opacity === '0' ||
        element.offsetParent === null) {
        return false;
    }

    return true;
}

/**
 * Clean and normalize extracted text
 */
function cleanText(text) {
    // Remove multiple consecutive newlines
    text = text.replace(/\n{3,}/g, '\n\n');

    // Remove excessive whitespace
    text = text.replace(/[ \t]+/g, ' ');

    // Remove leading/trailing whitespace
    text = text.trim();

    // Limit length to avoid issues (max ~50k characters)
    if (text.length > 50000) {
        text = text.substring(0, 50000) + '...';
    }

    return text;
}
