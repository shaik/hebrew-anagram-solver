"""
Optimized anagram solver module implementing recursive backtracking algorithm
with memoization and precomputation optimizations for finding multi-word Hebrew anagrams.

Performance optimizations include:
1. Precomputed frequency maps for all dictionary words
2. Memoization using Python's built-in lru_cache
3. Early pruning based on letter counts
4. Efficient data structures for frequency maps
5. Proper handling of all valid solutions including single-word anagrams
"""
from typing import List, Dict, Set, Tuple, Optional, FrozenSet, Iterator
from functools import lru_cache
from collections import Counter
from .dictionary import HebrewDictionary

# Type aliases for clarity
FreqMap = Dict[str, int]
FreqMapTuple = Tuple[Tuple[str, int], ...]
Solution = List[str]

class AnagramSolver:
    def __init__(self, dictionary: HebrewDictionary):
        """
        Initialize solver with a Hebrew dictionary and precompute frequency maps.
        Filters out single-letter words from the dictionary.
        
        Args:
            dictionary: HebrewDictionary instance for word validation
        """
        self.dictionary = dictionary
        
        # Filter out single-letter words and store remaining words
        self._dictionary_words = [word for word in dictionary.words if len(word) > 1]
        
        # Precompute frequency maps for all valid words for better performance
        # This is a key optimization that avoids recomputing frequency maps repeatedly
        self._word_freq_maps: Dict[str, FreqMap] = {}
        for word in self._dictionary_words:
            self._word_freq_maps[word] = self.dictionary.get_word_frequency_map(word)
            
        # Note: We previously used LRU caching with _find_anagrams_helper, but have
        # switched to a pure generator-based approach for better memory efficiency
        # and simpler code. The precomputed frequency maps above provide sufficient
        # optimization for our use case.

    @staticmethod
    def _freq_map_to_tuple(freq_map: FreqMap) -> FreqMapTuple:
        """Convert a frequency map to a hashable tuple representation."""
        return tuple(sorted(freq_map.items()))
    
    @staticmethod
    def _tuple_to_freq_map(freq_tuple: FreqMapTuple) -> FreqMap:
        """Convert a frequency tuple back to a dictionary."""
        return dict(freq_tuple)
    
    def subtract_freq_maps(self, target: FreqMap, word: FreqMap) -> Optional[FreqMap]:
        """
        Optimized subtraction of one frequency map from another.
        Uses direct dictionary operations for better performance.
        
        Args:
            target: Target frequency map
            word: Word frequency map to subtract
            
        Returns:
            New frequency map with frequencies subtracted, or None if impossible
        """
        # Quick check before copying
        if not self.is_freq_map_subset(word, target):
            return None
            
        result = target.copy()
        for char, count in word.items():
            result[char] -= count
            if result[char] == 0:
                del result[char]
        return result

    def is_freq_map_subset(self, word_freq: FreqMap, target_freq: FreqMap) -> bool:
        """
        Optimized check if one frequency map is a subset of another.
        Uses early return for better performance.
        
        Args:
            word_freq: Word frequency map
            target_freq: Target frequency map
            
        Returns:
            True if word_freq is a subset of target_freq
        """
        # Early size check - if word has more unique chars than target, it can't be a subset
        if len(word_freq) > len(target_freq):
            return False
            
        for char, count in word_freq.items():
            if char not in target_freq or target_freq[char] < count:
                return False
        return True

    def _find_anagrams_generator(self, remaining_freq_tuple: FreqMapTuple, words_limit: int) -> Iterator[Tuple[str, ...]]:
        """
        Generator function that lazily yields anagram solutions.
        This is the core recursive function that generates solutions without storing them all in memory.
        
        Args:
            remaining_freq_tuple: Remaining letters as a frequency map tuple
            words_limit: Maximum number of words allowed in solutions
            
        Yields:
            Each valid solution as a tuple of words
        """
        if not remaining_freq_tuple:  # Found a solution
            yield tuple()
            return
            
        if words_limit <= 0:  # No more words allowed
            return
            
        remaining_freq = dict(remaining_freq_tuple)
        remaining_letters = sum(count for _, count in remaining_freq_tuple)
        
        # Try each word in the dictionary
        for word in self._dictionary_words:
            # Skip words that are too long
            if len(word) > remaining_letters:
                continue
                
            word_freq = self._word_freq_maps[word]
            if self.is_freq_map_subset(word_freq, remaining_freq):
                new_freq = self.subtract_freq_maps(remaining_freq, word_freq)
                if new_freq is not None:
                    # Recursively generate solutions for remaining letters
                    for sub_solution in self._find_anagrams_generator(
                        self._freq_map_to_tuple(new_freq),
                        words_limit - 1
                    ):
                        yield (word,) + sub_solution
    
    def find_anagrams(self, letters: str, max_words: int = 5, must_have_word: Optional[str] = None) -> Iterator[Solution]:
        """
        Lazily generate all valid multi-word anagrams for the given letters.
        
        This is a generator function that yields one solution at a time, avoiding
        the need to compute and store all solutions at once. It uses the
        _find_anagrams_generator helper which implements the core recursive logic.
        
        If must_have_word is provided, it will be included in every solution and
        the remaining letters will be used to generate additional words.
        
        Performance optimizations:
        1. Input normalization and frequency map computation done once up front
        2. Generator-based lazy evaluation to avoid storing all solutions in memory
        3. Early filtering of single-word solutions that match the input
        4. Precomputed word frequency maps from __init__
        5. Efficient handling of must-have word by subtracting its frequency map
        
        Args:
            letters: Input string of Hebrew letters
            max_words: Maximum number of words in each anagram
            must_have_word: Optional word that must appear in every solution
            
        Yields:
            Each anagram solution as a list of words, one at a time
            
        Raises:
            ValueError: If must_have_word is provided but its letters are not a subset
                      of the input letters (considering frequencies)
        """
        # Remove spaces and normalize the input once
        normalized = self.dictionary.normalize_word(letters.replace(' ', ''))
        target_freq = self.dictionary.get_word_frequency_map(normalized)
        
        # If must_have_word is provided, validate and subtract its letters
        if must_have_word:
            # Normalize the must-have word
            mhw_normalized = self.dictionary.normalize_word(must_have_word.strip())
            mhw_freq = self.dictionary.get_word_frequency_map(mhw_normalized)
            
            # Verify that must_have_word's letters are a subset of input letters
            for char, freq in mhw_freq.items():
                if char not in target_freq or target_freq[char] < freq:
                    raise ValueError('Must-have word contains letters not present in input')
            
            # Subtract must_have_word's letters from target frequency map
            remaining_freq = {}
            for char, freq in target_freq.items():
                remaining = freq - mhw_freq.get(char, 0)
                if remaining > 0:
                    remaining_freq[char] = remaining
            
            # Convert remaining frequency map to tuple for generator
            target_tuple = self._freq_map_to_tuple(remaining_freq)
            
            # Generate solutions for remaining letters and append must_have_word
            for solution in self._find_anagrams_generator(target_tuple, max_words - 1):
                # Skip solutions that are just the original input minus must_have_word
                if len(solution) == 1 and self.dictionary.normalize_word(solution[0]) == self.dictionary.normalize_word(''.join(remaining_freq.keys())):
                    continue
                # Append must_have_word to each solution
                yield list(solution) + [must_have_word]
        else:
            # Standard case without must_have_word
            target_tuple = self._freq_map_to_tuple(target_freq)
            for solution in self._find_anagrams_generator(target_tuple, max_words):
                # Skip solutions that are just the original input
                if len(solution) == 1 and self.dictionary.normalize_word(solution[0]) == normalized:
                    continue
                yield list(solution)
