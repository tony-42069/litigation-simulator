"""
Judge Analysis Module for the Litigation Simulator.

This module implements machine learning functionality to analyze judge writing style,
topic modeling, and ruling patterns from judicial opinions.
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import Counter
import re
import string
import pickle

# Import required ML and NLP libraries
import spacy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("SpaCy model loaded successfully")
except OSError:
    logger.error("SpaCy model not found. Please install it with 'python -m spacy download en_core_web_sm'")
    raise RuntimeError("Required SpaCy model 'en_core_web_sm' not found")

class JudgeProfiler:
    """
    Class for analyzing judge writing style, topics, and ruling patterns.
    
    This class provides methods to analyze judicial opinions and generate
    profiles for judges based on their writing style, topics they discuss,
    and patterns in their rulings.
    """
    
    def __init__(self, model_dir: str = None):
        """
        Initialize the JudgeProfiler.
        
        Args:
            model_dir: Directory to store/load trained models
        """
        self.model_dir = model_dir or os.getenv("MODEL_DIR", "./models")
        self.vectorizer = None
        self.topic_model = None
        self.style_clusters = None
        
        # Create model directory if it doesn't exist
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Try to load pre-trained models
        self._load_models()
        
    def _load_models(self) -> bool:
        """
        Load pre-trained models if available.
        
        Returns:
            bool: True if models were loaded, False otherwise
        """
        try:
            logger.info("Attempting to load pre-trained models...")
            
            model_files = {
                'vectorizer': os.path.join(self.model_dir, 'vectorizer.pkl'),
                'topic_model': os.path.join(self.model_dir, 'topic_model.pkl'),
                'style_clusters': os.path.join(self.model_dir, 'style_clusters.pkl')
            }
            
            if not all(os.path.exists(path) and os.path.getsize(path) > 0 for path in model_files.values()):
                logger.info("One or more model files missing or empty. Will train new models.")
                return False
            
            # Load models
            self.vectorizer = pickle.load(open(model_files['vectorizer'], 'rb'))
            self.topic_model = pickle.load(open(model_files['topic_model'], 'rb'))
            self.style_clusters = pickle.load(open(model_files['style_clusters'], 'rb'))
            
            logger.info("Pre-trained models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading pre-trained models: {str(e)}")
            return False
    
    def _save_models(self) -> bool:
        """
        Save trained models to disk.
        
        Returns:
            bool: True if models were saved, False otherwise
        """
        try:
            logger.info("Saving trained models...")
            
            if not all([self.vectorizer, self.topic_model, self.style_clusters]):
                logger.warning("Models not available for saving")
                return False
            
            # Save models
            pickle.dump(self.vectorizer, open(os.path.join(self.model_dir, 'vectorizer.pkl'), 'wb'))
            pickle.dump(self.topic_model, open(os.path.join(self.model_dir, 'topic_model.pkl'), 'wb'))
            pickle.dump(self.style_clusters, open(os.path.join(self.model_dir, 'style_clusters.pkl'), 'wb'))
            
            logger.info("Models saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            return False
    
    def analyze_judge(self, judge_id: str, opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a judge based on their opinions.
        
        Args:
            judge_id: ID of the judge
            opinions: List of opinions authored by the judge
                Each opinion should have at least: 
                - text (str): The opinion text
                - outcome (str): The case outcome
                - case_type (str): The type of case
                
        Returns:
            dict: Judge profile with writing style, topic distribution, and ruling patterns
        """
        logger.info(f"Analyzing judge {judge_id} with {len(opinions)} opinions")
        
        if not opinions:
            logger.warning(f"No opinions provided for judge {judge_id}")
            return {
                "judge_id": judge_id,
                "statistics": {"opinion_count": 0},
                "writing_style": {},
                "topics": {},
                "ruling_patterns": {}
            }
        
        # Extract text from opinions
        texts = [op.get("text", "") for op in opinions if op.get("text")]
        
        if not texts:
            logger.warning(f"No valid text found in opinions for judge {judge_id}")
            return {
                "judge_id": judge_id,
                "statistics": {"opinion_count": 0},
                "writing_style": {},
                "topics": {},
                "ruling_patterns": {}
            }
        
        # Analyze writing style
        writing_style = self._analyze_writing_style(texts)
        
        # Analyze topics
        topics = self._analyze_topics(texts)
        
        # Analyze ruling patterns
        ruling_patterns = self._analyze_ruling_patterns(opinions)
        
        # Compile statistics
        statistics = {
            "opinion_count": len(opinions),
            "avg_length": sum(len(text) for text in texts) / len(texts),
            "date_range": self._get_date_range(opinions)
        }
        
        # Combine results
        profile = {
            "judge_id": judge_id,
            "statistics": statistics,
            "writing_style": writing_style,
            "topics": topics,
            "ruling_patterns": ruling_patterns
        }
        
        return profile
    
    def _analyze_writing_style(self, texts: List[str]) -> Dict[str, Any]:
        """
        Analyze the writing style of opinions.
        
        Args:
            texts: List of opinion texts
            
        Returns:
            dict: Writing style metrics
        """
        logger.info("Analyzing writing style")
        
        # Concatenate texts to form a representative sample
        sample_text = " ".join(text[:10000] for text in texts[:5])  # Limit for performance
        
        # Parse with spaCy
        doc = nlp(sample_text)
        
        # Calculate metrics
        sentence_lengths = [len(sent) for sent in doc.sents]
        word_lengths = [len(token.text) for token in doc if not token.is_punct and not token.is_space]
        
        # Readability metrics (approximate Flesch Reading Ease)
        sentences = list(doc.sents)
        words = [token for token in doc if not token.is_punct and not token.is_space]
        syllables = sum(self._count_syllables(token.text) for token in words)
        
        if len(sentences) > 0 and len(words) > 0:
            avg_sentence_length = len(words) / len(sentences)
            avg_syllables_per_word = syllables / len(words)
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        else:
            avg_sentence_length = 0
            avg_syllables_per_word = 0
            flesch_score = 0
        
        # Calculate formality score (ratio of nouns and prepositions to pronouns and adverbs)
        pos_counts = Counter([token.pos_ for token in doc])
        formal_pos = ['NOUN', 'ADP', 'ADJ', 'DET']
        informal_pos = ['PRON', 'ADV', 'INTJ', 'PART']
        formal_count = sum(pos_counts[pos] for pos in formal_pos)
        informal_count = sum(pos_counts[pos] for pos in informal_pos)
        formality_score = formal_count / (informal_count + 1)  # Add 1 to avoid division by zero
        
        return {
            "readability": {
                "flesch_score": float(flesch_score),
                "interpretation": self._interpret_flesch_score(flesch_score),
                "avg_sentence_length": float(avg_sentence_length),
                "avg_word_length": float(np.mean(word_lengths) if word_lengths else 0),
                "sentence_length_distribution": self._get_distribution(sentence_lengths)
            },
            "formality": {
                "score": float(formality_score),
                "level": self._interpret_formality(formality_score),
                "pos_distribution": {pos: count / len(doc) for pos, count in pos_counts.items()}
            },
            "complexity": {
                "unique_words_ratio": len(set(token.text.lower() for token in doc if not token.is_punct)) / len(doc) if len(doc) > 0 else 0,
                "subordinate_clauses_ratio": len([token for token in doc if token.dep_ == 'mark']) / len(list(doc.sents)) if len(list(doc.sents)) > 0 else 0
            }
        }
    
    def _analyze_topics(self, texts: List[str]) -> Dict[str, Any]:
        """
        Analyze the topics discussed in opinions.
        
        Args:
            texts: List of opinion texts
            
        Returns:
            dict: Topic modeling results
        """
        logger.info("Analyzing opinion topics")
        
        # Initialize or use existing vectorizer
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
            X = self.vectorizer.fit_transform(texts)
        else:
            X = self.vectorizer.transform(texts)
        
        # Initialize or use existing topic model
        if self.topic_model is None:
            self.topic_model = LatentDirichletAllocation(n_components=10, random_state=42)
            topic_distribution = self.topic_model.fit_transform(X)
            self._save_models()
        else:
            topic_distribution = self.topic_model.transform(X)
        
        # Get average topic distribution
        avg_topic_dist = np.mean(topic_distribution, axis=0)
        
        # Get top terms for each topic
        feature_names = self.vectorizer.get_feature_names_out()
        top_terms = {}
        for topic_idx, topic in enumerate(self.topic_model.components_):
            top_term_indices = topic.argsort()[:-10 - 1:-1]
            top_terms[topic_idx] = [feature_names[i] for i in top_term_indices]
        
        return {
            "topic_distribution": {f"Topic {i}": float(prob) for i, prob in enumerate(avg_topic_dist)},
            "top_terms": {f"Topic {topic_idx}": terms for topic_idx, terms in top_terms.items()},
            "dominant_topic": int(np.argmax(avg_topic_dist))
        }
    
    def _analyze_ruling_patterns(self, opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in the judge's rulings.
        
        Args:
            opinions: List of opinions with outcome and case_type
            
        Returns:
            dict: Ruling pattern analysis
        """
        logger.info("Analyzing ruling patterns")
        
        # Get outcomes by case type
        case_types = {}
        for opinion in opinions:
            case_type = opinion.get('case_type', 'unknown')
            outcome = opinion.get('outcome', 'unknown')
            
            if case_type not in case_types:
                case_types[case_type] = {'total': 0, 'outcomes': Counter()}
            
            case_types[case_type]['total'] += 1
            case_types[case_type]['outcomes'][outcome] += 1
        
        # Calculate overall statistics
        total_opinions = len(opinions)
        outcome_counts = Counter(opinion.get('outcome', 'unknown') for opinion in opinions)
        
        # Simplify outcomes for analysis
        plaintiff_favorable = ['plaintiff_win', 'plaintiff_partial', 'affirmed', 'granted']
        defendant_favorable = ['defendant_win', 'denied', 'reversed', 'dismissed']
        
        plaintiff_count = sum(outcome_counts[outcome] for outcome in plaintiff_favorable if outcome in outcome_counts)
        defendant_count = sum(outcome_counts[outcome] for outcome in defendant_favorable if outcome in outcome_counts)
        
        if total_opinions > 0:
            plaintiff_rate = plaintiff_count / total_opinions
            defendant_rate = defendant_count / total_opinions
        else:
            plaintiff_rate = 0
            defendant_rate = 0
        
        return {
            "overall": {
                "plaintiff_favorable_rate": float(plaintiff_rate),
                "defendant_favorable_rate": float(defendant_rate),
                "outcome_distribution": {outcome: count / total_opinions for outcome, count in outcome_counts.items()} if total_opinions > 0 else {}
            },
            "by_case_type": {
                case_type: {
                    "outcome_distribution": {outcome: count / stats['total'] for outcome, count in stats['outcomes'].items()} if stats['total'] > 0 else {},
                    "count": stats['total']
                }
                for case_type, stats in case_types.items()
            }
        }
    
    def _get_date_range(self, opinions: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Get the date range of opinions.
        
        Args:
            opinions: List of opinions
            
        Returns:
            dict: Date range information
        """
        dates = []
        for opinion in opinions:
            date_filed = opinion.get('date_filed')
            if date_filed:
                try:
                    dates.append(datetime.fromisoformat(date_filed.replace('Z', '+00:00')))
                except (ValueError, TypeError):
                    continue
        
        if not dates:
            return {"earliest": None, "latest": None, "span_years": 0}
        
        earliest = min(dates)
        latest = max(dates)
        span = latest - earliest
        span_years = span.days / 365.25
        
        return {
            "earliest": earliest.isoformat(),
            "latest": latest.isoformat(),
            "span_years": float(span_years)
        }
    
    def _count_syllables(self, word: str) -> int:
        """
        Count the syllables in a word (approximate method).
        
        Args:
            word: The word to count syllables for
            
        Returns:
            int: Number of syllables
        """
        word = word.lower()
        # Remove punctuation
        word = ''.join(c for c in word if c not in string.punctuation)
        
        # Count vowel groups
        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel
        
        # Adjust for special cases
        if word.endswith('e') and not word.endswith('le'):
            count -= 1
        if count == 0:
            count = 1
            
        return count
    
    def _interpret_flesch_score(self, score: float) -> str:
        """
        Interpret the Flesch Reading Ease score.
        
        Args:
            score: Flesch Reading Ease score
            
        Returns:
            str: Interpretation of the score
        """
        if score < 30:
            return "Very difficult to read, likely understood by college graduates"
        elif score < 50:
            return "Difficult to read, likely understood by college students"
        elif score < 60:
            return "Fairly difficult to read, likely understood by 10-12th graders"
        elif score < 70:
            return "Plain English, likely understood by 8-9th graders"
        elif score < 80:
            return "Fairly easy to read, likely understood by 7th graders"
        elif score < 90:
            return "Easy to read, likely understood by 6th graders"
        else:
            return "Very easy to read, likely understood by 5th graders"
    
    def _interpret_formality(self, score: float) -> str:
        """
        Interpret the formality score.
        
        Args:
            score: Formality score
            
        Returns:
            str: Interpretation of the score
        """
        if score < 1.5:
            return "Informal"
        elif score < 2.5:
            return "Moderately formal"
        elif score < 3.5:
            return "Formal"
        else:
            return "Very formal"
    
    def _get_distribution(self, values: List[int]) -> Dict[str, int]:
        """
        Get the distribution of values.
        
        Args:
            values: List of values
            
        Returns:
            dict: Distribution of values in bins
        """
        if not values:
            return {}
            
        bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
        counts = [0] * (len(bins) + 1)
        
        for value in values:
            bin_idx = next((i for i, bin_val in enumerate(bins) if value < bin_val), len(bins))
            counts[bin_idx] += 1
        
        dist = {}
        for i, count in enumerate(counts):
            if i < len(bins):
                bin_label = f"<{bins[i]}"
            else:
                bin_label = f"≥{bins[-1]}"
            dist[bin_label] = count
        
        return dist 