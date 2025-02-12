"""
Tests for input validation in the anagram solver.
"""
import json
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_input_length_limit(client):
    """Test that input length is limited to 14 characters (excluding spaces)."""
    # Test with exactly 14 characters (should pass)
    response = client.post('/solve', json={
        'letters': 'אבגדהוזחטיכלמנ',  # 14 characters
        'max_words': 4,
        'page': 1,
        'per_page': 50
    })
    assert response.status_code == 200
    
    # Test with 14 characters and spaces (should pass)
    response = client.post('/solve', json={
        'letters': 'א ב ג ד ה ו ז ח ט י כ ל מ נ',  # 14 characters with spaces
        'max_words': 4,
        'page': 1,
        'per_page': 50
    })
    assert response.status_code == 200
    
    # Test with more than 14 characters (should fail)
    response = client.post('/solve', json={
        'letters': 'אבגדהוזחטיכלמנס',  # 15 characters
        'max_words': 4,
        'page': 1,
        'per_page': 50
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Input cannot be longer than 14 characters (excluding spaces)'
    
    # Test with more than 14 characters with spaces (should fail)
    response = client.post('/solve', json={
        'letters': 'א ב ג ד ה ו ז ח ט י כ ל מ נ ס',  # 15 characters with spaces
        'max_words': 4,
        'page': 1,
        'per_page': 50
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Input cannot be longer than 14 characters (excluding spaces)'
