document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('explainForm');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const result = document.getElementById('result');
    const emailForm = document.getElementById('emailForm');

    let currentShareUrl = '';

    // Handle main explanation form
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(form);

        // Hide previous results and errors
        error.style.display = 'none';
        result.style.display = 'none';
        loading.style.display = 'block';

        try {
            const response = await fetch('/explain', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            loading.style.display = 'none';

            if (data.success) {
                // Update title
                document.getElementById('result-title').textContent = data.title;

                // Update explanation
                document.getElementById('result-explanation').textContent = data.explanation;

                // Update bullets heading based on mode
                const bulletsHeading = document.getElementById('result-bullets-heading');
                if (data.mode === 'adult_tldr') {
                    bulletsHeading.textContent = 'Key takeaways:';
                } else {
                    bulletsHeading.textContent = 'Why this matters:';
                }

                // Update bullets
                const bulletList = document.getElementById('result-why-matters');
                bulletList.innerHTML = '';
                data.why_it_matters.forEach(function(item) {
                    const li = document.createElement('li');
                    li.textContent = item;
                    bulletList.appendChild(li);
                });

                // Update vocabulary (hide section for Adult TLDR)
                const vocabSection = document.querySelector('.vocabulary-section');
                const vocabList = document.getElementById('result-vocabulary');
                vocabList.innerHTML = '';

                if (data.vocabulary && data.vocabulary.length > 0) {
                    // Show vocabulary section
                    vocabSection.style.display = 'block';
                    data.vocabulary.forEach(function(item) {
                        const div = document.createElement('div');
                        div.className = 'vocab-item';
                        div.innerHTML = `<strong>${item.word}:</strong> ${item.definition}`;
                        vocabList.appendChild(div);
                    });
                } else {
                    // Hide vocabulary section (Adult TLDR)
                    vocabSection.style.display = 'none';
                }

                // Update MLA citation (only show if source was a URL)
                const mlaCitationSection = document.getElementById('mla-citation-section');
                const mlaCitationText = document.getElementById('result-mla-citation');

                if (data.mla_citation) {
                    mlaCitationText.textContent = data.mla_citation;
                    mlaCitationSection.style.display = 'block';
                } else {
                    mlaCitationSection.style.display = 'none';
                }

                // Store share URL
                currentShareUrl = window.location.origin + data.share_url;

                // Show result
                result.style.display = 'block';
                result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                error.textContent = data.error;
                error.style.display = 'block';
            }
        } catch (err) {
            loading.style.display = 'none';
            error.textContent = 'Something went wrong. Please try again.';
            error.style.display = 'block';
        }
    });

    // Handle copy link button
    document.getElementById('copy-link-btn').addEventListener('click', async function() {
        const btn = this;
        const originalText = btn.textContent;

        // Try modern clipboard API first
        if (navigator.clipboard && navigator.clipboard.writeText) {
            try {
                await navigator.clipboard.writeText(currentShareUrl);

                // Visual feedback - success
                btn.textContent = '✓ Copied!';
                btn.style.background = '#d4edda';

                setTimeout(function() {
                    btn.textContent = originalText;
                    btn.style.background = '';
                }, 2000);
                return;
            } catch (err) {
                console.log('Clipboard API failed, trying fallback:', err);
            }
        }

        // Fallback method using textarea
        try {
            const textarea = document.createElement('textarea');
            textarea.value = currentShareUrl;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();

            const successful = document.execCommand('copy');
            document.body.removeChild(textarea);

            if (successful) {
                btn.textContent = '✓ Copied!';
                btn.style.background = '#d4edda';

                setTimeout(function() {
                    btn.textContent = originalText;
                    btn.style.background = '';
                }, 2000);
            } else {
                throw new Error('Copy command failed');
            }
        } catch (err) {
            // Show error message with the URL
            const message = document.createElement('div');
            message.className = 'copy-error-message';
            message.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); z-index: 1000; max-width: 90%;';
            message.innerHTML = `
                <p style="margin-bottom: 10px;"><strong>Could not copy link automatically.</strong></p>
                <p style="margin-bottom: 10px;">Please copy this link manually:</p>
                <input type="text" value="${currentShareUrl}" readonly style="width: 100%; padding: 8px; margin-bottom: 10px; font-size: 14px;">
                <button onclick="this.parentElement.remove()" style="padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">Close</button>
            `;
            document.body.appendChild(message);

            // Auto-remove after 10 seconds
            setTimeout(function() {
                if (message.parentElement) {
                    message.remove();
                }
            }, 10000);
        }
    });

    // Handle download PDF button
    document.getElementById('download-pdf-btn').addEventListener('click', function() {
        // Open PDF in new tab so we don't lose the current summary
        window.open('/download-pdf', '_blank');
    });

    // Handle email form
    emailForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(emailForm);
        const messageDiv = document.getElementById('email-message');

        try {
            const response = await fetch('/email-summary', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            messageDiv.textContent = data.message;
            messageDiv.className = 'message ' + (data.success ? 'success' : 'error');
            messageDiv.style.display = 'block';

            if (data.success) {
                emailForm.reset();
            }

            // Hide message after 5 seconds
            setTimeout(function() {
                messageDiv.style.display = 'none';
            }, 5000);

        } catch (err) {
            messageDiv.textContent = 'Failed to send email. Please try again.';
            messageDiv.className = 'message error';
            messageDiv.style.display = 'block';
        }
    });
});
