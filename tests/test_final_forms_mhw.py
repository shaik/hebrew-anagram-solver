"""
Tests for final form handling in must-have word validation.
"""
import pytest
from anagram.dictionary import HebrewDictionary
from anagram.solver import AnagramSolver

def test_final_forms_in_mhw(tmp_path):
    """Test that final forms in must-have word are handled correctly."""
    # Create a test dictionary file with some Hebrew words
    dict_path = tmp_path / "test_dict.txt"
    with open(dict_path, "w", encoding="utf-8") as f:
        f.write("שלום\nמלך\nשלומ\nמלכ\n")
    
    # Initialize dictionary and solver
    dictionary = HebrewDictionary(dict_path)
    solver = AnagramSolver(dictionary)
    
    # Test case 1: Input with base form, must-have word with final form
    solutions = list(solver.find_anagrams("שלומ", max_words=2, must_have_word="שלום"))
    assert len(solutions) > 0, "Should find solutions when must-have word uses final form"
    assert all("שלום" in solution for solution in solutions), "All solutions should contain must-have word"
    
    # Test case 2: Input with final form, must-have word with base form
    solutions = list(solver.find_anagrams("שלום", max_words=2, must_have_word="שלומ"))
    assert len(solutions) > 0, "Should find solutions when must-have word uses base form"
    assert all("שלומ" in solution for solution in solutions), "All solutions should contain must-have word"
    
    # Test case 3: Invalid must-have word (letters not in input)
    with pytest.raises(ValueError, match="המילה חייבת להיות מורכבת מהאותיות שהוזנו"):
        list(solver.find_anagrams("שלומ", max_words=2, must_have_word="מלך"))
    
    # Test case 4: Multiple final forms
    solutions = list(solver.find_anagrams("מלך", max_words=2, must_have_word="מלכ"))
    assert len(solutions) > 0, "Should find solutions with multiple final forms"
    assert all("מלכ" in solution for solution in solutions), "All solutions should contain must-have word"
