"""
Main Flask application for the Hebrew anagram solver.
Provides web interface and API endpoints for solving anagrams.
"""
import os
from flask import Flask, render_template, request, jsonify
from anagram.dictionary import HebrewDictionary
from anagram.solver import AnagramSolver

app = Flask(__name__)

# Initialize the dictionary and solver
dict_path = os.path.join(os.path.dirname(__file__), 'data', 'hebrew_dict.txt')
dictionary = HebrewDictionary(dict_path)
solver = AnagramSolver(dictionary)

@app.route('/')
def index():
    """Render the main page with the anagram solver interface."""
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    """
    API endpoint for solving anagrams.
    
    Expects JSON input with:
        - letters: string of Hebrew letters
        - max_words: (optional) maximum number of words in solutions
    
    Returns JSON with:
        - solutions: list of valid word combinations
        - error: error message if any
    """
    try:
        data = request.get_json()
        letters = data.get('letters', '').strip()
        max_words = int(data.get('max_words', 5))
        
        if not letters:
            return jsonify({'error': 'No input provided'}), 400
            
        solutions = solver.find_anagrams(letters, max_words)
        return jsonify({
            'solutions': solutions,
            'count': len(solutions)
        })
        
    except Exception as e:
        app.logger.error(f"Error solving anagram: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug)
