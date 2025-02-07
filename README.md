# Hebrew Anagram Solver

A Flask web application that finds multi-word anagrams from Hebrew input, handling final letter forms and providing a beautiful, responsive UI.

## Features

- Finds all possible combinations of Hebrew words that form anagrams
- Handles Hebrew final letter forms (ך, ם, ן, ף, ץ)
- Modern, responsive web interface with RTL support
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

The application provides a REST API endpoint at `/solve`:

```bash
curl -X POST http://localhost:5000/solve \
  -H "Content-Type: application/json" \
  -d '{"letters": "שלום", "max_words": 3}'
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
