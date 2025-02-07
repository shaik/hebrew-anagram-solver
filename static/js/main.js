document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('anagramForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const solutionsList = document.getElementById('solutionsList');
    const errorDiv = document.getElementById('error');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Reset UI state
        loading.classList.remove('d-none');
        results.classList.add('d-none');
        errorDiv.classList.add('d-none');
        solutionsList.innerHTML = '';
        
        const letters = document.getElementById('letters').value.trim();
        const maxWords = parseInt(document.getElementById('maxWords').value);
        
        try {
            const response = await fetch('/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    letters: letters,
                    max_words: maxWords
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                if (data.solutions.length > 0) {
                    data.solutions.forEach(solution => {
                        const item = document.createElement('div');
                        item.className = 'list-group-item';
                        item.textContent = solution.join(' ');
                        solutionsList.appendChild(item);
                    });
                    results.classList.remove('d-none');
                } else {
                    showError('לא נמצאו אנגרמות מתאימות');
                }
            } else {
                showError(data.error || 'אירעה שגיאה בעיבוד הבקשה');
            }
        } catch (error) {
            showError('אירעה שגיאה בתקשורת עם השרת');
        } finally {
            loading.classList.add('d-none');
        }
    });
    
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('d-none');
    }
});
