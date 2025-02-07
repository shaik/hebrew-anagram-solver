"""
Integration tests using the real Hebrew dictionary.
"""
import os
import logging
from anagram.dictionary import HebrewDictionary
from anagram.solver import AnagramSolver

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_dictionary_loading():
    """Test loading the real dictionary file and log word count."""
    dict_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'hebrew_dict.txt')
    assert os.path.exists(dict_path), f"Dictionary file not found at {dict_path}"
    
    dictionary = HebrewDictionary(dict_path)
    word_count = len(dictionary.words)
    normalized_count = len(dictionary.normalized_words)
    
    logger.info(f"Loaded {word_count} words from dictionary")
    logger.info(f"Normalized word count: {normalized_count}")
    
    assert word_count > 0, "Dictionary should not be empty"
    assert "חתול" in dictionary.words, "Basic word 'חתול' should be in dictionary"
    assert "לחות" in dictionary.words, "Basic word 'לחות' should be in dictionary"
    
    # Test that one-letter words are ignored
    with open(dict_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'ו' in content or 'ב' in content:  # If one-letter words exist in file
            assert 'ו' not in dictionary.words, "One-letter word 'ו' should be ignored"
            assert 'ב' not in dictionary.words, "One-letter word 'ב' should be ignored"

def test_real_dictionary_anagrams():
    """Test finding anagrams using the real dictionary."""
    dict_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'hebrew_dict.txt')
    dictionary = HebrewDictionary(dict_path)
    solver = AnagramSolver(dictionary)
    
    # Test חתול -> לחות (original input should be excluded)
    solutions = solver.find_anagrams("חתול")
    logger.info(f"Found {len(solutions)} anagrams for 'חתול'")
    for solution in solutions:
        logger.info(f"Solution: {' '.join(solution)}")
    
    assert ["חתול"] not in solutions, "Original input 'חתול' should not be in results"
    assert ["לחות"] in solutions, "'לחות' should be found as an anagram of 'חתול'"
    
    # Test with various space patterns
    space_patterns = ["חת ול", "ח תול", "חתו ל", "ח ת ו ל"]
    for pattern in space_patterns:
        solutions_with_spaces = solver.find_anagrams(pattern)
        logger.info(f"Found {len(solutions_with_spaces)} anagrams for '{pattern}'")
        for solution in solutions_with_spaces:
            logger.info(f"Solution: {' '.join(solution)}")
        
        assert ["לחות"] in solutions_with_spaces, f"'לחות' should be found as an anagram of '{pattern}'"
        assert len(solutions_with_spaces) == 1, f"Only 'לחות' should be found for '{pattern}'"
    
    # Test reverse: לחות -> חתול
    solutions_reverse = solver.find_anagrams("לחות")
    logger.info(f"Found {len(solutions_reverse)} anagrams for 'לחות'")
    for solution in solutions_reverse:
        logger.info(f"Solution: {' '.join(solution)}")
    
    assert ["לחות"] not in solutions_reverse, "Original input 'לחות' should not be in results"
    assert ["חתול"] in solutions_reverse, "'חתול' should be found as an anagram of 'לחות'"
    assert len(solutions_reverse) == 1, "Only 'חתול' should be found for 'לחות'"
