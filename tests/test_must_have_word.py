"""
Tests for the must-have word functionality in the anagram solver.
"""
import json
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_valid_must_have_word(client):
    """Test that solutions include the must-have word when it's valid."""
    response = client.post('/solve', json={
        'letters': 'שלוםעולם',
        'max_words': 4,
        'mhw': 'שלום',
        'page': 1,
        'per_page': 50
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Verify that each solution contains the must-have word
    for solution in data['solutions']:
        assert 'שלום' in solution

def test_invalid_must_have_word(client):
    """Test that an error is returned when must-have word contains invalid letters."""
    response = client.post('/solve', json={
        'letters': 'שלום',
        'max_words': 4,
        'mhw': 'עולם',  # Contains letters not in input
        'page': 1,
        'per_page': 50
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'המילה חייבת להיות מורכבת מהאותיות שהוזנו'

def test_empty_must_have_word(client):
    """Test that empty must-have word is treated as None."""
    response = client.post('/solve', json={
        'letters': 'שלום',
        'max_words': 4,
        'mhw': '',  # Empty string
        'page': 1,
        'per_page': 50
    })
    assert response.status_code == 200

def test_whitespace_must_have_word(client):
    """Test that whitespace-only must-have word is treated as None."""
    response = client.post('/solve', json={
        'letters': 'שלום',
        'max_words': 4,
        'mhw': '   ',  # Whitespace only
        'page': 1,
        'per_page': 50
    })
    assert response.status_code == 200

def test_must_have_word_pagination(client):
    """Test that pagination works correctly with must-have word."""
    # First page
    response1 = client.post('/solve', json={
        'letters': 'שלוםעולם',
        'max_words': 4,
        'mhw': 'שלום',
        'page': 1,
        'per_page': 2
    })
    assert response1.status_code == 200
    data1 = json.loads(response1.data)
    search_id = data1['search_id']
    
    # Second page using same search_id
    response2 = client.post('/solve', json={
        'search_id': search_id,
        'page': 2,
        'per_page': 2
    })
    assert response2.status_code == 200
    data2 = json.loads(response2.data)
    
    # Verify both pages contain different solutions but all include must-have word
    solutions1 = data1['solutions']
    solutions2 = data2['solutions']
    assert solutions1 != solutions2  # Different solutions on different pages
    for solution in solutions1 + solutions2:
        assert 'שלום' in solution
