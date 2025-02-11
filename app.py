"""
Main Flask application for the Hebrew anagram solver.
Provides web interface and API endpoints for solving anagrams with pagination support.
"""
import os
import re
import uuid
import logging
from time import time
from typing import List, Iterator, Optional, Dict
from dataclasses import dataclass
from flask import Flask, render_template, request, jsonify, session
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from anagram.dictionary import HebrewDictionary
from anagram.solver import AnagramSolver

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with security settings
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Use client IP for rate limiting
    default_limits=["200 per day", "50 per hour"],  # Default limits for all routes
    storage_uri="memory://",  # Use in-memory storage for rate limiting
    strategy="fixed-window"  # Use fixed time window for rate counting
)

# Hebrew letter validation regex
HEBREW_LETTERS_REGEX = re.compile(r'^[\u0590-\u05FF\s]+$')  # Only Hebrew letters and spaces allowed

def is_valid_hebrew_text(text: str) -> bool:
    """Validate that text contains only Hebrew letters and spaces."""
    return bool(HEBREW_LETTERS_REGEX.match(text))

# Initialize the dictionary and solver
dict_path = os.path.join(os.path.dirname(__file__), 'data', 'hebrew_dict.txt')
dictionary = HebrewDictionary(dict_path)
solver = AnagramSolver(dictionary)

# In-memory cache for pagination
class SolutionCache:
    def __init__(self, letters: str, max_words: int, mhw: Optional[str] = None):
        self.letters = letters
        self.max_words = max_words
        self.mhw = mhw
        self.solutions: List[List[str]] = []
        self.generator: Optional[Iterator[List[str]]] = None
        self.is_complete = False
        self.created_at = time()
        
    def ensure_solutions(self, count: int) -> bool:
        """Ensure we have at least count solutions, if possible."""
        if self.is_complete or len(self.solutions) >= count:
            return True
            
        if self.generator is None:
            self.generator = solver.find_anagrams(self.letters, self.max_words, self.mhw)
            
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

@app.errorhandler(429)  # Handle rate limit exceeded errors
def ratelimit_handler(e):
    """Return JSON response for rate limit exceeded."""
    return jsonify({
        'error': 'Rate limit exceeded. Please try again later.',
        'retry_after': e.description
    }), 429

def set_security_headers(response):
    """Add security headers to all responses."""
    # Allow Bootstrap CDN and other required resources
    csp = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net",
        "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net",
        "font-src 'self' cdn.jsdelivr.net",
        "img-src 'self' data: blob:"
    ]
    response.headers['Content-Security-Policy'] = "; ".join(csp)
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/solve', methods=['POST'])
@csrf.exempt  # Exempt API endpoint from CSRF as it uses JSON
@limiter.limit("5 per second; 100 per minute")  # Specific limits for /solve endpoint
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
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400
        
        search_id = data.get('search_id')
        
        # For subsequent page requests, we only need search_id
        if not search_id:
            # Initial request validation
            letters = data.get('letters')
            if not letters or not isinstance(letters, str):
                return jsonify({'error': 'Letters field is required'}), 400
            
            letters = letters.strip()
            if not letters:
                return jsonify({'error': 'Letters field cannot be empty'}), 400
            if not is_valid_hebrew_text(letters):
                return jsonify({'error': 'Invalid input. Only Hebrew letters are allowed.'}), 400
                
            # Validate must-have word if present
            mhw = data.get('mhw', '')
            if mhw:
                if not isinstance(mhw, str):
                    return jsonify({'error': 'Must-have word must be a string'}), 400
                mhw = mhw.strip()
                if mhw and not is_valid_hebrew_text(mhw):
                    return jsonify({'error': 'Invalid must-have word. Only Hebrew letters are allowed.'}), 400
            else:
                mhw = ''

            try:
                requested_max_words = int(data.get('max_words', 4))
                if requested_max_words < 1:
                    return jsonify({'error': 'max_words must be at least 1'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid max_words value'}), 400
                
            max_words = min(requested_max_words, 4)  # Ensure it never exceeds 4
        else:
            # For subsequent pages, use values from cache
            if search_id not in solution_caches:
                return jsonify({'error': 'Invalid or expired search_id'}), 400
            cache_entry = solution_caches[search_id]
            letters = cache_entry.letters
            mhw = cache_entry.mhw or ''
            max_words = cache_entry.max_words
        
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
            
        # Get optional must-have word parameter
        mhw = data.get('mhw')
        if mhw:
            mhw = mhw.strip()
            if not mhw:  # If it's just whitespace, treat as None
                mhw = None
                
        # Get or create cache for this search
        if search_id and search_id in solution_caches:
            cache = solution_caches[search_id]
        else:
            search_id = str(uuid.uuid4())
            try:
                cache = SolutionCache(letters, max_words, mhw)
                solution_caches[search_id] = cache
            except ValueError as e:
                return jsonify({
                    'error': 'המילה חייבת להיות מורכבת מהאותיות שהוזנו'
                }), 400
            
        # Calculate required number of solutions
        required_solutions = page * per_page
        cache.ensure_solutions(required_solutions)
        
        # Get the slice for current page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_solutions = cache.solutions[start_idx:end_idx]
        
        # Restore final forms for display
        page_solutions = [
            [dictionary.restore_final_forms(word) for word in solution]
            for solution in page_solutions
        ]
        
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
        
    except ValueError as e:
        # Handle validation errors (like invalid must-have word)
        error_msg = str(e)
        if 'Must-have word contains letters not present in input' in error_msg:
            return jsonify({
                'error': 'המילה חייבת להיות מורכבת מהאותיות שהוזנו'
            }), 400
        return jsonify({'error': error_msg}), 400
        
    except Exception as e:
        # Handle other unexpected errors
        app.logger.error(f"Error solving anagram: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug)
