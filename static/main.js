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

                // Update bullets
                const bulletList = document.getElementById('result-why-matters');
                bulletList.innerHTML = '';
                data.why_it_matters.forEach(function(item) {
                    const li = document.createElement('li');
                    li.textContent = item;
                    bulletList.appendChild(li);
                });

                // Update vocabulary
                const vocabList = document.getElementById('result-vocabulary');
                vocabList.innerHTML = '';
                data.vocabulary.forEach(function(item) {
                    const div = document.createElement('div');
                    div.className = 'vocab-item';
                    div.innerHTML = `<strong>${item.word}:</strong> ${item.definition}`;
                    vocabList.appendChild(div);
                });

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
        try {
            await navigator.clipboard.writeText(currentShareUrl);

            // Visual feedback
            const btn = this;
            const originalText = btn.textContent;
            btn.textContent = '✓ Copied!';
            btn.style.background = '#d4edda';

            setTimeout(function() {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 2000);
        } catch (err) {
            alert('Failed to copy link. URL: ' + currentShareUrl);
        }
    });

    // Handle download PDF button
    document.getElementById('download-pdf-btn').addEventListener('click', function() {
        window.location.href = '/download-pdf';
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
