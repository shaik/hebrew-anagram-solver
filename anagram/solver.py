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
from typing import List, Dict, Set, Tuple, Optional, FrozenSet
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
        
        # Precompute frequency maps for all valid words
        self._word_freq_maps: Dict[str, FreqMap] = {}
        for word in self._dictionary_words:
            self._word_freq_maps[word] = self.dictionary.get_word_frequency_map(word)
        
        # Create a static helper function with lru_cache for memoization
        self._find_anagrams_helper = lru_cache(maxsize=10000)(self._find_anagrams_helper_impl)

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

    def _find_anagrams_helper_impl(self, remaining_freq_tuple: FreqMapTuple, words_limit: int) -> FrozenSet[Tuple[str, ...]]:
        """
        Helper function that does the actual recursive search with memoization.
        Returns a frozenset of solutions (as tuples) for the given state.
        """
        if not remaining_freq_tuple:  # Found a solution
            return frozenset([()])  # Empty tuple represents a complete solution
            
        if words_limit <= 0:  # No more words allowed
            return frozenset()
            
        remaining_freq = dict(remaining_freq_tuple)
        remaining_letters = sum(count for _, count in remaining_freq_tuple)
        
        solutions = set()
        # Try each word in the dictionary
        for word in self._dictionary_words:
            # Skip words that are too long
            if len(word) > remaining_letters:
                continue
                
            word_freq = self._word_freq_maps[word]
            if self.is_freq_map_subset(word_freq, remaining_freq):
                new_freq = self.subtract_freq_maps(remaining_freq, word_freq)
                if new_freq is not None:
                    # Recursively find solutions for remaining letters
                    sub_solutions = self._find_anagrams_helper(
                        self._freq_map_to_tuple(new_freq),
                        words_limit - 1
                    )
                    # Add current word to each sub-solution
                    for sub_solution in sub_solutions:
                        solutions.add((word,) + sub_solution)
        
        return frozenset(solutions)
    
    def find_anagrams(self, letters: str, max_words: int = 5) -> List[Solution]:
        """
        Find all valid multi-word anagrams for the given letters using optimized algorithms.
        
        Args:
            letters: Input string of Hebrew letters
            max_words: Maximum number of words in each anagram
            
        Returns:
            List of anagram solutions, where each solution is a list of words
        """
        # Remove spaces and normalize
        normalized = self.dictionary.normalize_word(letters.replace(' ', ''))
        target_freq = self.dictionary.get_word_frequency_map(normalized)
        target_tuple = self._freq_map_to_tuple(target_freq)
        
        # Clear the LRU cache to avoid memory issues between runs
        self._find_anagrams_helper.cache_clear()
        
        # Get all solutions as tuples
        solution_tuples = self._find_anagrams_helper(target_tuple, max_words)
        
        # Convert solutions to lists and filter out empty solutions
        solutions = [list(solution) for solution in solution_tuples if solution]
        
        # Filter out solutions that are just the original input
        solutions = [
            solution for solution in solutions 
            if not (len(solution) == 1 and 
                   self.dictionary.normalize_word(solution[0]) == normalized)
        ]
        
        # Sort solutions for consistent ordering
        solutions.sort(key=lambda x: (len(x), x))
        
        return solutions
