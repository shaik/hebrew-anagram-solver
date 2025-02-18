import json
import pytest
from app import app

@pytest.fixture
def client():
    """Set up a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_pagination_returns_unique_results(client):
    """
    Test that each page of results from the `/solve` API 
    returns unique solutions and does not repeat results.
    
    Expected Behavior:
    - Each page should return different solutions.
    - Pagination should function correctly when using the same `search_id`.
    
    Current Status:
    - This test is expected to FAIL due to a known pagination bug.
    """
    # Request the first page to get a search_id
    response1 = client.post('/solve', json={
        'letters': 'שלוםעולם',
        'max_words': 4,
        'page': 1,
        'per_page': 3  # Small number to force pagination
    })
    assert response1.status_code == 200, "First request failed"
    
    data1 = json.loads(response1.data)
    search_id = data1.get('search_id')
    solutions_page_1 = data1.get('solutions', [])

    assert search_id, "search_id was not returned"
    assert len(solutions_page_1) > 0, "No solutions on first page"
    
    # Request the second page using the same search_id
    response2 = client.post('/solve', json={
        'search_id': search_id,
        'page': 2,
        'per_page': 3
    })
    assert response2.status_code == 200, "Second request failed"
    
    data2 = json.loads(response2.data)
    solutions_page_2 = data2.get('solutions', [])
    
    # Verify solutions are unique across pages
    overlapping_solutions = [sol for sol in solutions_page_2 if sol in solutions_page_1]
    
    assert len(solutions_page_2) > 0, "No solutions on second page"
    assert not overlapping_solutions, (
        f"Pagination error: Same solutions found on both pages: {overlapping_solutions}"
    )
    
    print("This test is expected to FAIL until pagination is fixed.")
