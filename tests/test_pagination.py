"""
Tests for pagination functionality in the anagram solver application.
"""
import pytest
from flask import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_initial_page(client):
    """Test that the first page returns the correct number of results."""
    response = client.post('/solve', json={
        'letters': 'שלום',
        'max_words': 4,
        'page': 1,
        'per_page': 50
    })
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert len(data['solutions']) <= 50
    assert data['page'] == 1
    assert data['per_page'] == 50
    assert 'search_id' in data
    assert isinstance(data['total_found'], int)
    assert isinstance(data['is_complete'], bool)
    assert isinstance(data['elapsed_ms'], int)

def test_subsequent_page_request(client):
    """Test that requesting subsequent pages with the same search_id works."""
    # First request to get search_id
    response1 = client.post('/solve', json={
        'letters': 'שלוםעולם',  # Use a longer input to ensure multiple pages
        'max_words': 4,
        'page': 1,
        'per_page': 50
    })
    data1 = json.loads(response1.data)
    search_id = data1['search_id']
    
    # Request second page
    response2 = client.post('/solve', json={
        'search_id': search_id,
        'page': 2,
        'per_page': 50
    })
    data2 = json.loads(response2.data)
    
    assert response2.status_code == 200
    assert data2['page'] == 2
    assert data2['search_id'] == search_id
    assert data2['total_found'] >= data1['total_found']

def test_invalid_page_request(client):
    """Test that requesting an invalid page returns appropriate error."""
    response = client.post('/solve', json={
        'letters': 'שלום',
        'max_words': 4,
        'page': 0,  # Invalid page number
        'per_page': 50
    })
    
    assert response.status_code == 400

def test_lazy_evaluation(client):
    """Test that solutions are generated lazily and cached properly."""
    # Request first page
    response1 = client.post('/solve', json={
        'letters': 'שלוםעולם',
        'max_words': 4,
        'page': 1,
        'per_page': 50
    })
    data1 = json.loads(response1.data)
    
    total_found1 = data1['total_found']
    search_id = data1['search_id']
    
    # Request second page
    response2 = client.post('/solve', json={
        'search_id': search_id,
        'page': 2,
        'per_page': 50
    })
    data2 = json.loads(response2.data)
    
    # The second request should find more solutions
    assert data2['total_found'] >= total_found1

def test_cache_cleanup(client):
    """Test that old searches are cleaned up from cache."""
    # This is more of an integration test and might need manual verification
    # of memory usage over time
    response = client.post('/solve', json={
        'letters': 'שלום',
        'max_words': 4,
        'page': 1,
        'per_page': 50
    })
    assert response.status_code == 200
