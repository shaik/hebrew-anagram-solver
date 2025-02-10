"""
Unit tests for the anagram solver module.
"""
import pytest
from anagram.dictionary import HebrewDictionary
from anagram.solver import AnagramSolver

@pytest.fixture
def mock_dictionary(tmp_path):
    """Create a dictionary with test words."""
    dict_file = tmp_path / "test_dict.txt"
    with open(dict_file, "w", encoding="utf-8") as f:
        # Include test words that can form anagrams
        f.write("ספר\nפרס\nרפס\n")
    return HebrewDictionary(str(dict_file))

@pytest.fixture
def solver(mock_dictionary):
    """Create an AnagramSolver instance with the mock dictionary."""
    return AnagramSolver(mock_dictionary)

def test_freq_map_subtraction(solver):
    """Test frequency map subtraction."""
    target = {"א": 2, "ב": 1, "ג": 3}
    word = {"א": 1, "ג": 2}
    result = solver.subtract_freq_maps(target, word)
    assert result == {"א": 1, "ב": 1, "ג": 1}

def test_freq_map_subtraction_impossible(solver):
    """Test frequency map subtraction when impossible."""
    target = {"א": 1, "ב": 1}
    word = {"א": 2}
    result = solver.subtract_freq_maps(target, word)
    assert result is None

def test_freq_map_subset(solver):
    """Test frequency map subset checking."""
    target = {"א": 2, "ב": 1, "ג": 3}
    word = {"א": 1, "ג": 2}
    assert solver.is_freq_map_subset(word, target)
    
    word2 = {"א": 3}
    assert not solver.is_freq_map_subset(word2, target)

def test_single_word_anagram(solver):
    """Test finding single-word anagrams."""
    solutions = list(solver.find_anagrams("ספר", max_words=1))
    assert len(solutions) == 2  # פרס, רפס (original input ספר is excluded)
    assert ["פרס"] in solutions
    assert ["רפס"] in solutions

def test_no_solutions(solver):
    """Test when no solutions exist."""
    solutions = list(solver.find_anagrams("טסט"))
    assert len(solutions) == 0

def test_final_forms(solver):
    """Test handling of final forms."""
    solutions = list(solver.find_anagrams("ספר"))
    assert len(solutions) == 2  # Should find same solutions regardless of final forms, excluding original input
