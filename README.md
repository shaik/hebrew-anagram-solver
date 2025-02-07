# Hebrew Anagram Solver

A Flask web application that finds multi-word anagrams from Hebrew input, handling final letter forms and providing a beautiful, responsive UI.

## About This Project

This project was developed using an innovative approach where ChatGPT (GPT-3.5-turbo-0125) was used to generate prompts for Windsurf, a powerful AI coding assistant. This two-stage prompt engineering process allowed for more precise and effective code generation.

### Example Prompts

1. Initial prompt to ChatGPT:
```
I want to create a Hebrew anagram solver using Python and Flask. Generate a prompt for Windsurf that will help create this application. The prompt should specify:
- Handling Hebrew final letters (ך, ם, ן, ף, ץ)
- Finding all possible word combinations
- Using a dictionary file for valid words
- Creating a beautiful web interface
```

2. ChatGPT generated this refined prompt for Windsurf:
```
Create a Hebrew anagram solver web application using Flask with the following specifications:

1. Core Features:
   - Load a Hebrew dictionary from a UTF-8 text file
   - Implement a function to normalize Hebrew final letters (ך->כ, ם->מ, etc.)
   - Create an efficient algorithm to find all valid word combinations
   - Support multi-word anagrams up to 4 words

2. Web Interface:
   - Clean, modern design with RTL support
   - Input field for Hebrew text
   - Display results in a clear, organized manner
   - Add loading indicator for longer queries

3. Implementation Details:
   - Use recursive backtracking with memoization
   - Precompute frequency maps for dictionary words
   - Handle edge cases (empty input, no solutions)
   - Add comprehensive test suite
```

3. For optimizations, another prompt to ChatGPT:
```
Generate a prompt for Windsurf to optimize the anagram solver by:
- Using lru_cache for memoization
- Improving the frequency map comparisons
- Adding proper test cases for edge cases
```

This iterative process of using ChatGPT to refine prompts for Windsurf resulted in high-quality, optimized code with proper error handling and test coverage.

## Features

- Finds all possible combinations of Hebrew words that form anagrams
- Handles Hebrew final letter forms (ך, ם, ן, ף, ץ)
- Modern, responsive web interface with RTL support
- Support for must-have word in solutions (יש להחזיר צרופים המכילים את המילה)
- Lazy evaluation and server-side pagination for efficient memory usage
- RESTful API endpoint for programmatic access
- Comprehensive test suite
- Easy deployment to Heroku

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd anagram_gpt
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Place your Hebrew dictionary file at `data/hebrew_dict.txt` (one word per line, UTF-8 encoded)

5. Run the development server:
```bash
FLASK_DEBUG=true flask run
```

The application will be available at http://localhost:5000

## Testing

Run the test suite using pytest:
```bash
pytest
```

## API Usage

The application provides a REST API endpoint at `/solve` that accepts POST requests with JSON data:

```json
{
    "letters": "שלוםעולם",    // Required: Input letters
    "max_words": 4,         // Optional: Maximum words per solution (default: 4)
    "mhw": "שלום",         // Optional: Must-have word to include in solutions
    "page": 1,             // Optional: Page number for pagination (default: 1)
    "per_page": 50,        // Optional: Results per page (default: 50, max: 100)
    "search_id": null      // Optional: ID from previous search for pagination
}
```

Example response:

```json
{
    "solutions": [          // Array of solutions for current page
        ["שלום", "עולם"],
        ["שלום", "על", "ום"]
    ],
    "total_found": 42,      // Total number of solutions found
    "is_complete": false,   // Whether all solutions have been generated
    "page": 1,             // Current page number
    "per_page": 50,        // Results per page
    "search_id": "...",    // Use this ID for subsequent page requests
    "elapsed_ms": 123      // Time taken to process request
}
```

Error responses will have a 400 or 500 status code and include an error message:

```json
{
    "error": "המילה חייבת להיות מורכבת מהאותיות שהוזנו"
}
```

Example usage with curl:

```bash
# Basic search
curl -X POST http://localhost:5000/solve \
     -H "Content-Type: application/json" \
     -d '{"letters": "שלוםעולם", "max_words": 4}'

# Search with must-have word
curl -X POST http://localhost:5000/solve \
     -H "Content-Type: application/json" \
     -d '{"letters": "שלוםעולם", "max_words": 4, "mhw": "שלום"}'

# Paginated search
curl -X POST http://localhost:5000/solve \
     -H "Content-Type: application/json" \
     -d '{"letters": "שלוםעולם", "max_words": 4, "page": 2, "per_page": 10}'
```

Response format:
```json
{
  "solutions": [["שלום"], ["של", "ום"]],
  "count": 2
}
```

## Heroku Deployment

1. Create a new Heroku app:
```bash
heroku create your-app-name
```

2. Push to Heroku:
```bash
git push heroku main
```

3. Ensure you have at least one dyno running:
```bash
heroku ps:scale web=1
```

## Project Structure

```
anagram_gpt/
  ├── app.py                    # Main Flask app
  ├── Procfile                  # For Heroku deployment
  ├── requirements.txt          # Python dependencies
  ├── data/
  │    └── hebrew_dict.txt      # Hebrew dictionary (UTF-8 encoded)
  ├── anagram/
  │    ├── __init__.py
  │    ├── dictionary.py        # Dictionary loading and normalization
  │    └── solver.py            # Recursive anagram solver
  ├── templates/
  │    └── index.html          # HTML template for the UI
  ├── static/
  │    ├── css/
  │    │    └── style.css      # Custom styles
  │    └── js/
  │         └── main.js        # Frontend JavaScript
  ├── tests/
  │    ├── test_dictionary.py  # Dictionary module tests
  │    └── test_solver.py      # Solver module tests
  └── README.md                # This file
```

## License

MIT License - feel free to use this code for any purpose.
