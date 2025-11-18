document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('explainForm');
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const result = document.getElementById('result');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get form data
        const formData = new FormData(form);

        // Hide previous results and errors
        error.style.display = 'none';
        result.style.display = 'none';
        loading.style.display = 'block';

        try {
            // Send POST request
            const response = await fetch('/explain', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            // Hide loading
            loading.style.display = 'none';

            if (data.success) {
                // Show result
                document.getElementById('result-title').textContent = data.title;
                document.getElementById('result-explanation').textContent = data.explanation;

                // Populate bullet points
                const bulletList = document.getElementById('result-why-matters');
                bulletList.innerHTML = '';
                data.why_it_matters.forEach(function(item) {
                    const li = document.createElement('li');
                    li.textContent = item;
                    bulletList.appendChild(li);
                });

                result.style.display = 'block';

                // Scroll to result
                result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            } else {
                // Show error
                error.textContent = data.error;
                error.style.display = 'block';
            }
        } catch (err) {
            // Hide loading
            loading.style.display = 'none';

            // Show error
            error.textContent = 'Something went wrong. Please try again.';
            error.style.display = 'block';
        }
    });
});
