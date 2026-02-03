"""
GenAI Feature Extraction Module
================================
This module extracts AI-specific features from text to identify patterns 
characteristic of different Large Language Models (LLMs).

Features Extracted:
1. GPT-style Repetition: Detects repetitive phrases typical of GPT models
2. Gemini Explanatory Overflow: Detects over-explanation patterns
3. Claude Uncertainty Hedging: Detects hedging language patterns
4. Low Burstiness (OpenLLM): Measures sentence length variance
5. Citation Hallucination: Detects potentially fabricated citations
6. Perplexity-based Measures: Estimates text predictability

Author: AI-Generated Scholarly Paper Detection System
For Academic Use Only - IEEE/College-level Project
"""

import re
import math
from collections import Counter
from typing import Dict, List, Tuple, Any


class GenAIFeatureExtractor:
    """
    Extracts GenAI-specific linguistic features from scholarly text.
    
    This class implements detection algorithms for identifying patterns
    that are characteristic of AI-generated content from various LLMs.
    """
    
    def __init__(self):
        """Initialize the feature extractor with pattern definitions."""
        
        # GPT-style repetitive phrases
        self.gpt_repetitive_patterns = [
            r'\b(in conclusion|to summarize|it is important to note)\b',
            r'\b(as mentioned (earlier|above|previously))\b',
            r'\b(this (demonstrates|shows|indicates|suggests) that)\b',
            r'\b(it (is|can be) (argued|said|noted) that)\b',
            r'\b(the (fact|idea|concept|notion) that)\b',
            r'\b(in (this|the) (context|regard|respect))\b',
            r'\b(plays a (crucial|vital|important|significant|key) role)\b',
            r'\b(it is worth (noting|mentioning|pointing out))\b',
            r'\b(one (can|could|might) argue that)\b',
            r'\b(this (paper|study|research|article) (aims|seeks|attempts))\b',
        ]
        
        # Claude uncertainty hedging phrases
        self.claude_hedging_patterns = [
            r'\b(I think|I believe|I would say|I\'d suggest)\b',
            r'\b(perhaps|possibly|potentially|presumably)\b',
            r'\b(it (seems|appears|looks) (like|as if|that))\b',
            r'\b(may or may not)\b',
            r'\b(to some (extent|degree))\b',
            r'\b(it (could|might|may) be (the case|argued|that))\b',
            r'\b(there is a possibility that)\b',
            r'\b(one (possible|potential) (explanation|interpretation))\b',
            r'\b(this (could|might|may) (suggest|indicate|imply))\b',
            r'\b(it is (possible|plausible|conceivable) that)\b',
        ]
        
        # Gemini explanatory overflow patterns
        self.gemini_overflow_patterns = [
            r'\b(let me explain|let me clarify|to be more specific)\b',
            r'\b(in other words|put (simply|differently|another way))\b',
            r'\b(to (elaborate|expand) (on|further))\b',
            r'\b(what (this|I) mean(s)? (is|by this))\b',
            r'\b(essentially|fundamentally|basically)\b',
            r'\b(for (example|instance)|such as|namely)\b',
            r'\b(this (is|means|refers to))\b',
            r'\b(to (understand|grasp|comprehend) this)\b',
            r'\b((first|second|third)(ly)?[,:]?\s*(we|one|you))\b',
            r'\b(it\'s (important|crucial|essential) to (understand|note|realize))\b',
        ]
        
        # Suspicious citation patterns (potential hallucinations)
        self.suspicious_citation_patterns = [
            # Made-up looking citations with generic names
            r'\((?:Smith|Johnson|Williams|Brown|Jones|Davis|Miller)\s+et\s+al\.\s*,?\s*\d{4}\)',
            # Suspiciously round years in future
            r'\(\w+\s+et\s+al\.\s*,?\s*(2025|2026|2027|2028|2029|2030)\)',
            # Generic "Study" or "Research" citations
            r'\((?:Study|Research|Survey|Analysis)\s+\d{4}\)',
            # Incomplete citations
            r'\[?\d+\]?\s*(?=\.|,|;|\s*$)',
            # Vague institutional citations
            r'\((?:University|Institute|Organization)\s+\d{4}\)',
        ]
        
    def extract_all_features(self, text: str) -> Dict[str, Any]:
        """
        Extract all GenAI features from the given text.
        
        Args:
            text: The scholarly paper text to analyze
            
        Returns:
            Dictionary containing all extracted features and scores
        """
        if not text or not text.strip():
            return self._empty_features()
        
        # Extract individual features
        gpt_score, gpt_details = self.detect_gpt_repetition(text)
        gemini_score, gemini_details = self.detect_gemini_overflow(text)
        claude_score, claude_details = self.detect_claude_hedging(text)
        burstiness_score, burstiness_details = self.calculate_burstiness(text)
        citation_score, citation_details = self.detect_citation_hallucination(text)
        perplexity_score, perplexity_details = self.estimate_perplexity(text)
        
        # Calculate composite GenAI score (weighted average)
        composite_score = self._calculate_composite_score(
            gpt_score, gemini_score, claude_score, 
            burstiness_score, citation_score, perplexity_score
        )
        
        return {
            'composite_score': round(composite_score, 3),
            'features': {
                'gpt_repetition': {
                    'score': round(gpt_score, 3),
                    'details': gpt_details
                },
                'gemini_overflow': {
                    'score': round(gemini_score, 3),
                    'details': gemini_details
                },
                'claude_hedging': {
                    'score': round(claude_score, 3),
                    'details': claude_details
                },
                'burstiness': {
                    'score': round(burstiness_score, 3),
                    'details': burstiness_details
                },
                'citation_hallucination': {
                    'score': round(citation_score, 3),
                    'details': citation_details
                },
                'perplexity': {
                    'score': round(perplexity_score, 3),
                    'details': perplexity_details
                }
            },
            'interpretation': self._generate_interpretation(
                gpt_score, gemini_score, claude_score,
                burstiness_score, citation_score, perplexity_score
            )
        }
    
    def detect_gpt_repetition(self, text: str) -> Tuple[float, Dict]:
        """
        Detect GPT-style repetitive phrase patterns.
        
        GPT models tend to use formulaic transitions and 
        repetitive academic phrases.
        
        Returns:
            Tuple of (score, details_dict)
        """
        text_lower = text.lower()
        word_count = len(text.split())
        
        matches = []
        total_matches = 0
        
        for pattern in self.gpt_repetitive_patterns:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            if found:
                total_matches += len(found)
                matches.extend(found[:3])  # Keep first 3 examples
        
        # Normalize by word count (per 1000 words)
        normalized_frequency = (total_matches / max(word_count, 1)) * 1000
        
        # Score: 0-1 scale, higher = more AI-like
        score = min(1.0, normalized_frequency / 15)  # 15 matches per 1000 words = max
        
        return score, {
            'matches_found': total_matches,
            'examples': matches[:5],
            'frequency_per_1000': round(normalized_frequency, 2),
            'description': 'GPT-style repetitive phrases detected'
        }
    
    def detect_gemini_overflow(self, text: str) -> Tuple[float, Dict]:
        """
        Detect Gemini-style explanatory overflow patterns.
        
        Gemini tends to over-explain concepts with multiple
        clarification phrases.
        
        Returns:
            Tuple of (score, details_dict)
        """
        text_lower = text.lower()
        word_count = len(text.split())
        
        matches = []
        total_matches = 0
        
        for pattern in self.gemini_overflow_patterns:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            if found:
                total_matches += len(found)
                matches.extend([str(f) for f in found[:3]])
        
        normalized_frequency = (total_matches / max(word_count, 1)) * 1000
        score = min(1.0, normalized_frequency / 12)
        
        return score, {
            'matches_found': total_matches,
            'examples': matches[:5],
            'frequency_per_1000': round(normalized_frequency, 2),
            'description': 'Over-explanation patterns typical of Gemini'
        }
    
    def detect_claude_hedging(self, text: str) -> Tuple[float, Dict]:
        """
        Detect Claude-style uncertainty hedging patterns.
        
        Claude often uses hedging language and uncertainty markers.
        
        Returns:
            Tuple of (score, details_dict)
        """
        text_lower = text.lower()
        word_count = len(text.split())
        
        matches = []
        total_matches = 0
        
        for pattern in self.claude_hedging_patterns:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            if found:
                total_matches += len(found)
                matches.extend([str(f) for f in found[:3]])
        
        normalized_frequency = (total_matches / max(word_count, 1)) * 1000
        score = min(1.0, normalized_frequency / 10)
        
        return score, {
            'matches_found': total_matches,
            'examples': matches[:5],
            'frequency_per_1000': round(normalized_frequency, 2),
            'description': 'Uncertainty hedging typical of Claude'
        }
    
    def calculate_burstiness(self, text: str) -> Tuple[float, Dict]:
        """
        Calculate burstiness (sentence length variance).
        
        Human writing typically has high burstiness (varied sentence lengths),
        while AI-generated text tends to have low burstiness (uniform lengths).
        
        Returns:
            Tuple of (ai_score, details_dict) - higher score = more AI-like (low burstiness)
        """
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) < 3:
            return 0.0, {'variance': 0, 'mean_length': 0, 'description': 'Insufficient sentences'}
        
        lengths = [len(s.split()) for s in sentences]
        mean_len = sum(lengths) / len(lengths)
        
        # Calculate variance
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        
        # Coefficient of variation (normalized measure)
        cv = std_dev / max(mean_len, 1)
        
        # Low CV = low burstiness = more AI-like
        # Human text typically has CV > 0.5, AI text often < 0.3
        ai_score = max(0, 1 - (cv / 0.6))  # CV of 0.6+ = human-like
        
        return ai_score, {
            'variance': round(variance, 2),
            'std_deviation': round(std_dev, 2),
            'coefficient_of_variation': round(cv, 3),
            'mean_sentence_length': round(mean_len, 1),
            'sentence_count': len(sentences),
            'description': 'Low burstiness indicates uniform AI-generated patterns'
        }
    
    def detect_citation_hallucination(self, text: str) -> Tuple[float, Dict]:
        """
        Detect potentially hallucinated or fabricated citations.
        
        AI models sometimes generate fake citations with generic
        author names or implausible publication details.
        
        Returns:
            Tuple of (score, details_dict)
        """
        suspicious_matches = []
        
        for pattern in self.suspicious_citation_patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            suspicious_matches.extend(found)
        
        # Count total citations for comparison
        all_citations = re.findall(r'\([A-Z][a-z]+.*?\d{4}\)', text)
        all_citations += re.findall(r'\[\d+\]', text)
        
        total_citations = len(all_citations)
        suspicious_count = len(suspicious_matches)
        
        if total_citations == 0:
            return 0.5, {
                'suspicious_count': 0,
                'total_citations': 0,
                'examples': [],
                'description': 'No citations found - unusual for scholarly paper'
            }
        
        # Score based on ratio of suspicious to total
        ratio = suspicious_count / max(total_citations, 1)
        score = min(1.0, ratio * 2)  # Double the ratio for sensitivity
        
        return score, {
            'suspicious_count': suspicious_count,
            'total_citations': total_citations,
            'suspicious_ratio': round(ratio, 3),
            'examples': suspicious_matches[:5],
            'description': 'Potentially fabricated or hallucinated citations'
        }
    
    def estimate_perplexity(self, text: str) -> Tuple[float, Dict]:
        """
        Estimate text perplexity using n-gram frequency analysis.
        
        AI-generated text typically has lower perplexity (more predictable)
        compared to human-written text.
        
        Note: This is a simplified proxy for true perplexity which would
        require a language model to compute accurately.
        
        Returns:
            Tuple of (ai_score, details_dict) - higher score = more AI-like (low perplexity)
        """
        words = text.lower().split()
        
        if len(words) < 10:
            return 0.0, {'estimated_perplexity': 0, 'description': 'Insufficient text'}
        
        # Calculate word frequency entropy as proxy for perplexity
        word_counts = Counter(words)
        total_words = len(words)
        
        # Shannon entropy
        entropy = 0
        for count in word_counts.values():
            prob = count / total_words
            entropy -= prob * math.log2(prob)
        
        # Normalize entropy (higher entropy = more varied = more human-like)
        # Typical range: 6-12 bits for English text
        normalized_entropy = entropy / 12  # Normalize to ~0-1 range
        
        # Bigram repetition rate (another perplexity proxy)
        bigrams = [tuple(words[i:i+2]) for i in range(len(words)-1)]
        unique_bigrams = len(set(bigrams))
        bigram_ratio = unique_bigrams / max(len(bigrams), 1)
        
        # Low entropy + low bigram diversity = low perplexity = more AI-like
        perplexity_proxy = (normalized_entropy + bigram_ratio) / 2
        ai_score = max(0, 1 - perplexity_proxy)
        
        return ai_score, {
            'entropy': round(entropy, 3),
            'normalized_entropy': round(normalized_entropy, 3),
            'bigram_diversity': round(bigram_ratio, 3),
            'vocabulary_size': len(word_counts),
            'total_words': total_words,
            'estimated_perplexity': round((1 - ai_score) * 100, 1),
            'description': 'Low perplexity indicates predictable AI-generated text'
        }
    
    def _calculate_composite_score(
        self, 
        gpt: float, 
        gemini: float, 
        claude: float,
        burstiness: float, 
        citation: float, 
        perplexity: float
    ) -> float:
        """
        Calculate weighted composite GenAI score.
        
        Weights are based on feature reliability and discriminative power.
        """
        weights = {
            'gpt_repetition': 0.15,
            'gemini_overflow': 0.10,
            'claude_hedging': 0.10,
            'burstiness': 0.25,
            'citation_hallucination': 0.15,
            'perplexity': 0.25
        }
        
        composite = (
            gpt * weights['gpt_repetition'] +
            gemini * weights['gemini_overflow'] +
            claude * weights['claude_hedging'] +
            burstiness * weights['burstiness'] +
            citation * weights['citation_hallucination'] +
            perplexity * weights['perplexity']
        )
        
        return min(1.0, max(0.0, composite))
    
    def _generate_interpretation(
        self,
        gpt: float,
        gemini: float,
        claude: float,
        burstiness: float,
        citation: float,
        perplexity: float
    ) -> List[str]:
        """Generate human-readable interpretation of the features."""
        interpretations = []
        
        # Identify dominant patterns
        scores = {
            'GPT-style repetition': gpt,
            'Gemini-like over-explanation': gemini,
            'Claude-style hedging': claude,
            'Low burstiness (uniform sentences)': burstiness,
            'Suspicious citations': citation,
            'Low perplexity (predictable text)': perplexity
        }
        
        # Sort by score and report significant patterns
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        for pattern, score in sorted_scores:
            if score > 0.6:
                interpretations.append(f"High {pattern} detected (score: {score:.2f})")
            elif score > 0.3:
                interpretations.append(f"Moderate {pattern} detected (score: {score:.2f})")
        
        if not interpretations:
            interpretations.append("No significant AI patterns detected")
        
        return interpretations
    
    def _empty_features(self) -> Dict[str, Any]:
        """Return empty feature dictionary for invalid input."""
        return {
            'composite_score': 0.0,
            'features': {
                'gpt_repetition': {'score': 0.0, 'details': {}},
                'gemini_overflow': {'score': 0.0, 'details': {}},
                'claude_hedging': {'score': 0.0, 'details': {}},
                'burstiness': {'score': 0.0, 'details': {}},
                'citation_hallucination': {'score': 0.0, 'details': {}},
                'perplexity': {'score': 0.0, 'details': {}}
            },
            'interpretation': ['No text provided for analysis']
        }


# Convenience function for direct usage
def extract_genai_features(text: str) -> Dict[str, Any]:
    """
    Extract GenAI features from text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary containing all GenAI features and scores
    """
    extractor = GenAIFeatureExtractor()
    return extractor.extract_all_features(text)


if __name__ == "__main__":
    # Test with sample text
    sample = """
    In conclusion, this study demonstrates that the proposed methodology 
    is effective. It is important to note that our findings suggest 
    significant improvements. As mentioned earlier, the results indicate 
    a positive correlation. Perhaps this could be explained by the 
    underlying mechanisms. Let me explain further - essentially, the 
    data shows consistent patterns. Smith et al. (2024) found similar 
    results in their comprehensive study.
    """
    
    features = extract_genai_features(sample)
    print("GenAI Feature Analysis:")
    print(f"Composite Score: {features['composite_score']}")
    print("\nInterpretation:")
    for interp in features['interpretation']:
        print(f"  - {interp}")
