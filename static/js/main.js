document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('anagramForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const solutionsList = document.getElementById('solutionsList');
    const errorDiv = document.getElementById('error');
    const prevButton = document.getElementById('prevPage');
    const nextButton = document.getElementById('nextPage');
    const pageInfo = document.getElementById('pageInfo');
    
    // Function to check if all letters in mhw are present in the main input
    function validateMustHaveWord(letters, mhw) {
        if (!mhw) return true; // Empty mhw is valid
        
        // Create frequency maps for both strings
        const lettersFreq = {};
        const mhwFreq = {};
        
        // Count frequencies in main input
        for (const char of letters) {
            lettersFreq[char] = (lettersFreq[char] || 0) + 1;
        }
        
        // Count frequencies in must-have word
        for (const char of mhw) {
            mhwFreq[char] = (mhwFreq[char] || 0) + 1;
            // If letter not in main input or frequency exceeds main input
            if (!lettersFreq[char] || mhwFreq[char] > lettersFreq[char]) {
                return false;
            }
        }
        
        return true;
    }

    // Add input event listener for real-time validation
    document.getElementById('mhw').addEventListener('input', function() {
        const letters = document.getElementById('letters').value.trim();
        const mhw = this.value.trim();
        const isValid = validateMustHaveWord(letters, mhw);
        document.getElementById('mhw-error').classList.toggle('d-none', isValid);
    });

    // Pagination state
    let currentState = {
        page: 1,
        perPage: 50,
        searchId: null,
        isComplete: false,
        totalFound: 0,
        letters: '',
        maxWords: 4,
        mhw: ''
    };
    
    // Event listeners for pagination
    prevButton.addEventListener('click', () => loadPage(currentState.page - 1));
    nextButton.addEventListener('click', () => loadPage(currentState.page + 1));
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Reset UI and pagination state
        currentState = {
            page: 1,
            perPage: 50,
            searchId: null,
            isComplete: false,
            totalFound: 0,
            letters: document.getElementById('letters').value.trim(),
            maxWords: parseInt(document.getElementById('maxWords').value),
            mhw: document.getElementById('mhw').value.trim()
        };

        // Validate must-have word before submission
        if (!validateMustHaveWord(currentState.letters, currentState.mhw)) {
            document.getElementById('mhw-error').classList.remove('d-none');
            return;
        }
        
        await loadPage(1);
    });
    
    async function loadPage(page) {
        // Reset UI state
        loading.classList.remove('d-none');
        results.classList.add('d-none');
        errorDiv.classList.add('d-none');
        document.getElementById('searchStats').classList.add('d-none');
        solutionsList.innerHTML = '';
        
        try {
            const response = await fetch('/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    letters: currentState.letters,
                    max_words: currentState.maxWords,
                    page: page,
                    per_page: currentState.perPage,
                    search_id: currentState.searchId,
                    mhw: currentState.mhw || null
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Update pagination state
                currentState.page = data.page;
                currentState.searchId = data.search_id;
                currentState.isComplete = data.is_complete;
                currentState.totalFound = data.total_found;
                
                // Update search stats
                const statsDiv = document.getElementById('searchStats');
                statsDiv.textContent = `נמצאו ${data.total_found} תוצאות ב-${data.elapsed_ms} אלפיות שנייה`;
                statsDiv.classList.remove('d-none');
                
                if (data.solutions.length > 0) {
                    // Display solutions
                    data.solutions.forEach(solution => {
                        const item = document.createElement('div');
                        item.className = 'list-group-item';
                        item.textContent = solution.join(' ');
                        solutionsList.appendChild(item);
                    });
                    
                    // Update pagination UI
                    const startIdx = (currentState.page - 1) * currentState.perPage + 1;
                    const endIdx = Math.min(startIdx + data.solutions.length - 1, currentState.totalFound);
                    pageInfo.textContent = `מציג ${startIdx}-${endIdx} מתוך ${currentState.totalFound}`;
                    
                    // Update pagination buttons
                    prevButton.disabled = currentState.page === 1;
                    nextButton.disabled = currentState.isComplete && 
                                         endIdx === currentState.totalFound;
                    
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
    }
    
    function showError(message) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('d-none');
    }
});
