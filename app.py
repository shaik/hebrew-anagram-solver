"""
Main Flask application for the Hebrew anagram solver.
Provides web interface and API endpoints for solving anagrams with pagination support.
"""
import os
import uuid
from time import time
from typing import List, Iterator, Optional
from dataclasses import dataclass
from flask import Flask, render_template, request, jsonify, session
from anagram.dictionary import HebrewDictionary
from anagram.solver import AnagramSolver

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

# Initialize the dictionary and solver
dict_path = os.path.join(os.path.dirname(__file__), 'data', 'hebrew_dict.txt')
dictionary = HebrewDictionary(dict_path)
solver = AnagramSolver(dictionary)

# In-memory cache for pagination
class SolutionCache:
    def __init__(self, letters: str, max_words: int):
        self.letters = letters
        self.max_words = max_words
        self.solutions: List[List[str]] = []
        self.generator: Optional[Iterator[List[str]]] = None
        self.is_complete = False
        self.created_at = time()
        
    def ensure_solutions(self, count: int) -> bool:
        """Ensure we have at least count solutions, if possible."""
        if self.is_complete or len(self.solutions) >= count:
            return True
            
        if self.generator is None:
            self.generator = solver.find_anagrams(self.letters, self.max_words)
            
        try:
            while len(self.solutions) < count:
                self.solutions.append(next(self.generator))
        except StopIteration:
            self.is_complete = True
            self.generator = None
            
        return len(self.solutions) >= count

# Global cache of active searches
from typing import Dict

solution_caches: Dict[str, SolutionCache] = {}

@app.route('/')
def index():
    """Render the main page with the anagram solver interface."""
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    """
    API endpoint for solving anagrams with pagination support.
    
    Expects JSON input with:
        - letters: string of Hebrew letters
        - max_words: maximum number of words in solutions
        - page: page number (default: 1)
        - per_page: results per page (default: 50, max: 100)
        - search_id: ID of an existing search for subsequent page requests
    
    Returns JSON with:
        - solutions: list of valid anagrams for the requested page
        - total_found: number of solutions found so far
        - is_complete: whether all solutions have been found
        - page: current page number
        - per_page: number of results per page
        - search_id: unique identifier for this search
        - elapsed_ms: time taken for this request
        - error: error message if any
    """
    start_time = time()
    
    try:
        # Parse and validate input parameters
        data = request.get_json()
        
        # Validate search parameters
        letters = data.get('letters', '').strip()
        requested_max_words = int(data.get('max_words', 4))
        max_words = min(requested_max_words, 4)  # Ensure it never exceeds 4
        search_id = data.get('search_id')
        
        # Validate pagination parameters
        try:
            page = int(data.get('page', 1))
            if page < 1:
                return jsonify({'error': 'Invalid page number. Page must be greater than 0'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid page number format'}), 400
            
        try:
            per_page = min(int(data.get('per_page', 50)), 100)  # Cap at 100
            if per_page < 1:
                return jsonify({'error': 'Invalid per_page value. Must be greater than 0'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid per_page format'}), 400
        
        # Validate that either letters or search_id is provided
        if not letters and not search_id:
            return jsonify({'error': 'No input provided'}), 400
            
        # Get or create cache for this search
        if search_id and search_id in solution_caches:
            cache = solution_caches[search_id]
        else:
            search_id = str(uuid.uuid4())
            cache = SolutionCache(letters, max_words)
            solution_caches[search_id] = cache
            
        # Calculate required number of solutions
        required_solutions = page * per_page
        cache.ensure_solutions(required_solutions)
        
        # Get the slice for current page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_solutions = cache.solutions[start_idx:end_idx]
        
        # Clean up old caches (older than 1 hour)
        current_time = time()
        old_searches = [sid for sid, c in solution_caches.items() 
                       if current_time - c.created_at > 3600]
        for sid in old_searches:
            del solution_caches[sid]
        
        return jsonify({
            'solutions': page_solutions,
            'total_found': len(cache.solutions),
            'is_complete': cache.is_complete,
            'page': page,
            'per_page': per_page,
            'search_id': search_id,
            'elapsed_ms': int((time() - start_time) * 1000)
        })
        
    except Exception as e:
        app.logger.error(f"Error solving anagram: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug)
