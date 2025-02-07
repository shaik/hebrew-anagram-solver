"""
Unit tests for the Hebrew dictionary module.
"""
import os
import pytest
from anagram.dictionary import HebrewDictionary

@pytest.fixture
def temp_dict_file(tmp_path):
    """Create a temporary dictionary file for testing."""
    dict_file = tmp_path / "test_dict.txt"
    with open(dict_file, "w", encoding="utf-8") as f:
        f.write("שלום\nמלך\nספר\nרפס\n")
    return str(dict_file)

def test_dictionary_loading(temp_dict_file):
    """Test that dictionary loads words correctly."""
    dictionary = HebrewDictionary(temp_dict_file)
    assert len(dictionary.words) == 4
    assert "שלום" in dictionary.words
    assert "מלך" in dictionary.words

def test_final_form_normalization():
    """Test normalization of Hebrew final forms."""
    dictionary = HebrewDictionary(os.devnull)  # Empty dictionary
    assert dictionary.normalize_word("מלך") == "מלכ"
    assert dictionary.normalize_word("שלום") == "שלומ"
    assert dictionary.normalize_word("ספר") == "ספר"  # No final forms

def test_word_frequency_map():
    """Test frequency map generation for words."""
    dictionary = HebrewDictionary(os.devnull)
    freq_map = dictionary.get_word_frequency_map("שלום")
    assert freq_map == {"ש": 1, "ל": 1, "ו": 1, "מ": 1}

def test_invalid_dictionary_path():
    """Test that loading invalid dictionary raises error."""
    with pytest.raises(FileNotFoundError):
        HebrewDictionary("/nonexistent/path/dict.txt")

def test_empty_dictionary(tmp_path):
    """Test loading empty dictionary file."""
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()
    dictionary = HebrewDictionary(str(empty_file))
    assert len(dictionary.words) == 0

def test_word_validation(temp_dict_file):
    """Test word validation against dictionary."""
    dictionary = HebrewDictionary(temp_dict_file)
    assert dictionary.is_valid_word("ספר")
    assert dictionary.is_valid_word("רפס")
    assert not dictionary.is_valid_word("טסט")
