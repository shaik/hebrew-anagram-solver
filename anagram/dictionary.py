"""
Hebrew dictionary module for loading and normalizing Hebrew words.
Handles final letter forms and provides word validation functionality.
"""
import os
from typing import Set, Dict

class HebrewDictionary:
    # Mapping of Hebrew final forms to their base forms
    FINAL_FORMS = {
        'ך': 'כ',
        'ם': 'מ',
        'ן': 'נ',
        'ף': 'פ',
        'ץ': 'צ'
    }
    
    def __init__(self, dict_path: str):
        """
        Initialize the Hebrew dictionary from a file.
        
        Args:
            dict_path: Path to the UTF-8 encoded dictionary file
        """
        self.words: Set[str] = set()  # Original words
        self.normalized_words: Set[str] = set()  # Normalized forms
        self.load_dictionary(dict_path)

    def load_dictionary(self, dict_path: str) -> None:
        """
        Load words from a dictionary file, storing both original and normalized forms.
        Ignores one-letter words and empty lines.
        
        Args:
            dict_path: Path to the UTF-8 encoded dictionary file
        """
        if not os.path.exists(dict_path):
            raise FileNotFoundError(f"Dictionary file not found: {dict_path}")
            
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word and len(word) > 1:  # Skip empty lines and one-letter words
                    self.words.add(word)
                    self.normalized_words.add(self.normalize_word(word))

    def normalize_word(self, word: str) -> str:
        """
        Normalize a Hebrew word by converting final forms to base forms.
        
        Args:
            word: Hebrew word to normalize
            
        Returns:
            Normalized word with final forms converted to base forms
        """
        return ''.join(self.FINAL_FORMS.get(char, char) for char in word)

    def is_valid_word(self, word: str) -> bool:
        """
        Check if a word exists in the dictionary after normalization.
        
        Args:
            word: Word to check
            
        Returns:
            True if the normalized word exists in the dictionary
        """
        return self.normalize_word(word) in self.normalized_words

    def get_word_frequency_map(self, word: str) -> Dict[str, int]:
        """
        Create a frequency map of characters in a word after normalization.
        
        Args:
            word: Word to analyze
            
        Returns:
            Dictionary mapping each character to its frequency
        """
        normalized = self.normalize_word(word)
        freq_map = {}
        for char in normalized:
            freq_map[char] = freq_map.get(char, 0) + 1
        return freq_map
