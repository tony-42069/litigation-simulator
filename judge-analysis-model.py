"""
Judge Analysis Model

This module implements machine learning models to analyze judicial behavior,
writing patterns, and decision-making trends. The primary goal is to build
a comprehensive profile of each judge to inform litigation strategy.
"""

import os
import numpy as np
import pandas as pd
import pickle
import logging
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import torch
from transformers import AutoTokenizer, AutoModel
import spacy
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load spaCy model for text processing
try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    logger.info("Downloading spaCy model...")
    spacy.cli.download("en_core_web_lg")
    nlp = spacy.load("en_core_web_lg")

class JudgeProfiler:
    """
    Builds comprehensive profiles of judges based on their past opinions,
    ruling patterns, and writing style.
    """
    
    def __init__(self, model_dir: str = "./models"):
        """
        Initialize the JudgeProfiler.
        
        Args:
            model_dir: Directory to save/load model files
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize transformers model for embeddings
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.embedding_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
        # Initialize other models
        self.vectorizer = None
        self.topic_model = None
        self.ruling_classifier = None
        self.writing_style_kmeans = None
        
        logger.info("JudgeProfiler initialized")
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings for a list of texts using the sentence transformer model.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Array of embeddings
        """
        embeddings = []
        
        # Process in batches to avoid OOM
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            
            # Tokenize
            inputs = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512
            )
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.embedding_model(**inputs)
                
            # Use mean pooling to get sentence embeddings
            embeddings_batch = outputs.last_hidden_state.mean(dim=1)
            embeddings.extend(embeddings_batch.numpy())
            
        return np.array(embeddings)
    
    def analyze_writing_style(
        self, 
        opinions: List[Dict[str, Any]],
        n_clusters: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze the writing style of opinions using clustering.
        
        Args:
            opinions: List of opinion dictionaries with at least 'text' and 'author_id' fields
            n_clusters: Number of writing style clusters to identify
            
        Returns:
            Analysis results including style clusters and judge assignments
        """
        logger.info(f"Analyzing writing style of {len(opinions)} opinions with {n_clusters} clusters")
        
        # Extract text and judge IDs
        texts = [op['text'] for op in opinions]
        judge_ids = [op['author_id'] for op in opinions]
        
        # Get embeddings
        embeddings = self._get_embeddings(texts)
        
        # Train KMeans model if not already trained
        if self.writing_style_kmeans is None:
            self.writing_style_kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            self.writing_style_kmeans.fit(embeddings)
            logger.info(f"Trained KMeans model with {n_clusters} clusters")
            
            # Save the model
            model_path = os.path.join(self.model_dir, "writing_style_kmeans.pkl")
            with open(model_path, "wb") as f:
                pickle.dump(self.writing_style_kmeans, f)
            logger.info(f"Saved KMeans model to {model_path}")
        
        # Get cluster assignments
        clusters = self.writing_style_kmeans.predict(embeddings)
        
        # Analyze clusters by judge
        judge_clusters = {}
        for judge_id, cluster in zip(judge_ids, clusters):
            if judge_id not in judge_clusters:
                judge_clusters[judge_id] = []
            judge_clusters[judge_id].append(int(cluster))
        
        # Calculate dominant cluster for each judge
        judge_dominant_clusters = {}
        for judge_id, clusters in judge_clusters.items():
            counts = np.bincount(clusters)
            dominant = int(np.argmax(counts))
            percentage = float(counts[dominant] / len(clusters))
            judge_dominant_clusters[judge_id] = {
                "dominant_cluster": dominant,
                "percentage": percentage,
                "cluster_counts": {str(i): int(count) for i, count in enumerate(counts)},
                "total_opinions": len(clusters)
            }
        
        # Calculate cluster centers for interpretation
        cluster_centers = self.writing_style_kmeans.cluster_centers_
        
        return {
            "judge_styles": judge_dominant_clusters,
            "cluster_centers": cluster_centers.tolist(),
            "n_clusters": n_clusters
        }
    
    def extract_topics(
        self, 
        opinions: List[Dict[str, Any]], 
        n_topics: int = 10,
        n_top_words: int = 20
    ) -> Dict[str, Any]:
        """
        Extract topics from opinion texts using NMF.
        
        Args:
            opinions: List of opinion dictionaries with at least 'text' and 'author_id' fields
            n_topics: Number of topics to extract
            n_top_words: Number of top words to include for each topic
            
        Returns:
            Topics with top words and judge affinities
        """
        logger.info(f"Extracting {n_topics} topics from {len(opinions)} opinions")
        
        # Extract text and judge IDs
        texts = [op['text'] for op in opinions]
        judge_ids = [op['author_id'] for op in opinions]
        
        # Create or load vectorizer
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(
                max_df=0.95, 
                min_df=2,
                max_features=10000,
                stop_words='english'
            )
            
        # Transform texts to TF-IDF features
        X = self.vectorizer.fit_transform(texts)
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Train topic model if not already trained
        if self.topic_model is None:
            self.topic_model = NMF(
                n_components=n_topics, 
                random_state=42,
                alpha=0.1,
                l1_ratio=0.5
            )
            
        # Transform the TF-IDF features to topic space
        W = self.topic_model.fit_transform(X)
        H = self.topic_model.components_
        
        # Get top words for each topic
        topics = []
        for i, topic in enumerate(H):
            top_word_indices = topic.argsort()[:-n_top_words-1:-1]
            top_words = [feature_names[idx] for idx in top_word_indices]
            topics.append({
                "id": i,
                "top_words": top_words,
                "weight": float(np.sum(W[:, i]))
            })
        
        # Calculate judge topic affinities
        judge_topics = {}
        for idx, judge_id in enumerate(judge_ids):
            if judge_id not in judge_topics:
                judge_topics[judge_id] = np.zeros(n_topics)
                judge_topics[judge_id + "_count"] = 0
                
            judge_topics[judge_id] += W[idx]
            judge_topics[judge_id + "_count"] += 1
        
        # Normalize judge topic affinities
        judge_topic_affinities = {}
        for judge_id in set(judge_ids):
            count_key = judge_id + "_count"
            if judge_topics[count_key] > 0:
                affinities = judge_topics[judge_id] / judge_topics[count_key]
                judge_topic_affinities[judge_id] = affinities.tolist()
        
        # Save models
        model_path = os.path.join(self.model_dir, "topic_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(self.topic_model, f)
        
        vectorizer_path = os.path.join(self.model_dir, "vectorizer.pkl")
        with open(vectorizer_path, "wb") as f:
            pickle.dump(self.vectorizer, f)
        
        logger.info(f"Saved topic model and vectorizer to {self.model_dir}")
        
        return {
            "topics": topics,
            "judge_affinities": judge_topic_affinities
        }
    
    def train_ruling_classifier(
        self, 
        opinions: List[Dict[str, Any]],
        target_field: str = "outcome"
    ) -> Dict[str, Any]:
        """
        Train a classifier to predict rulings based on opinion text.
        
        Args:
            opinions: List of opinion dictionaries with 'text' and target_field
            target_field: Field in opinions that contains the ruling outcome
            
        Returns:
            Training results including accuracy and feature importance
        """
        logger.info(f"Training ruling classifier on {len(opinions)} opinions")
        
        # Extract text and outcomes
        texts = [op['text'] for op in opinions]
        outcomes = [op.get(target_field) for op in opinions]
        
        # Check if we have enough data with valid outcomes
        valid_indices = [i for i, o in enumerate(outcomes) if o is not None]
        if len(valid_indices) < 10:
            logger.warning(f"Not enough valid outcomes to train classifier: {len(valid_indices)}")
            return {"error": "Not enough valid outcomes to train classifier"}
        
        # Filter to valid examples
        texts = [texts[i] for i in valid_indices]
        outcomes = [outcomes[i] for i in valid_indices]
        
        # Get embeddings
        X = self._get_embeddings(texts)
        y = np.array(outcomes)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train classifier
        self.ruling_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            class_weight='balanced'
        )
        self.ruling_classifier.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.ruling_classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Save the model
        model_path = os.path.join(self.model_dir, "ruling_classifier.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(self.ruling_classifier, f)
        
        logger.info(f"Saved ruling classifier to {model_path} with accuracy {accuracy:.4f}")
        
        return {
            "accuracy": float(accuracy),
            "classification_report": report,
            "n_samples": len(texts),
            "classes": self.ruling_classifier.classes_.tolist()
        }
    
    def analyze_judge(self, judge_id: str, opinions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a comprehensive profile for a judge based on their opinions.
        
        Args:
            judge_id: Court Listener ID of the judge
            opinions: List of opinions authored by the judge
            
        Returns:
            Comprehensive judge profile
        """
        logger.info(f"Analyzing judge {judge_id} with {len(opinions)} opinions")
        
        # Extract basic stats
        case_types = {}
        outcomes = {}
        years = {}
        citation_counts = []
        text_lengths = []
        
        for op in opinions:
            # Case type
            case_type = op.get('case_type', 'unknown')
            case_types[case_type] = case_types.get(case_type, 0) + 1
            
            # Outcome
            outcome = op.get('outcome', 'unknown')
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
            
            # Year
            date = op.get('date_filed', '')
            if date:
                year = date.split('-')[0]
                years[year] = years.get(year, 0) + 1
            
            # Citation count
            citation_count = op.get('citation_count', 0)
            citation_counts.append(citation_count)
            
            # Text length
            text_length = len(op.get('text', ''))
            text_lengths.append(text_length)
        
        # Analyze writing style if enough opinions
        writing_style = {}
        if len(opinions) >= 5:
            writing_style = self.analyze_writing_style(opinions)
        
        # Extract topics if enough opinions
        topics = {}
        if len(opinions) >= 5:
            topics = self.extract_topics(opinions)
        
        # Provide all analyses in a combined profile
        profile = {
            "judge_id": judge_id,
            "analyzed_opinions_count": len(opinions),
            "statistics": {
                "case_types": case_types,
                "outcomes": outcomes,
                "years": years,
                "avg_citation_count": np.mean(citation_counts) if citation_counts else 0,
                "avg_text_length": np.mean(text_lengths) if text_lengths else 0
            },
            "writing_style": writing_style,
            "topics": topics
        }
        
        # Save the profile
        profile_path = os.path.join(self.model_dir, f"judge_profile_{judge_id}.json")
        with open(profile_path, "w") as f:
            json.dump(profile, f, indent=2)
        
        logger.info(f"Saved judge profile to {profile_path}")
        
        return profile
    
    def predict_outcome(self, case_text: str, judge_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Predict the outcome of a case based on its text and optionally the judge.
        
        Args:
            case_text: The text of the case
            judge_id: Optional ID of the judge
            
        Returns:
            Prediction results including outcome and confidence
        """
        if self.ruling_classifier is None:
            return {"error": "Ruling classifier not trained"}
        
        # Get embedding for the case text
        embedding = self._get_embeddings([case_text])[0].reshape(1, -1)
        
        # Predict
        outcome = self.ruling_classifier.predict(embedding)[0]
        probas = self.ruling_classifier.predict_proba(embedding)[0]
        
        # Get confidence
        confidence = float(max(probas))
        
        # Get class names
        classes = self.ruling_classifier.classes_
        class_probas = {str(c): float(p) for c, p in zip(classes, probas)}
        
        # If judge_id is provided, adjust prediction based on judge profile
        judge_adjustment = 0.0
        if judge_id:
            # Load judge profile if available
            profile_path = os.path.join(self.model_dir, f"judge_profile_{judge_id}.json")
            if os.path.exists(profile_path):
                with open(profile_path, "r") as f:
                    profile = json.load(f)
                
                # Check if this judge has a bias toward certain outcomes
                if "statistics" in profile and "outcomes" in profile["statistics"]:
                    outcomes = profile["statistics"]["outcomes"]
                    total = sum(outcomes.values())
                    if total > 0 and str(outcome) in outcomes:
                        judge_bias = outcomes[str(outcome)] / total
                        # Adjust confidence based on judge bias
                        judge_adjustment = (judge_bias - 0.5) * 0.2  # Scale adjustment
        
        # Apply judge adjustment to confidence
        adjusted_confidence = min(1.0, max(0.0, confidence + judge_adjustment))
        
        return {
            "predicted_outcome": str(outcome),
            "confidence": adjusted_confidence,
            "class_probabilities": class_probas,
            "judge_adjustment": judge_adjustment
        }
    
    def load_models(self) -> bool:
        """
        Load trained models from disk.
        
        Returns:
            True if all models loaded successfully, False otherwise
        """
        try:
            # Load vectorizer
            vectorizer_path = os.path.join(self.model_dir, "vectorizer.pkl")
            if os.path.exists(vectorizer_path):
                with open(vectorizer_path, "rb") as f:
                    self.vectorizer = pickle.load(f)
            
            # Load topic model
            topic_model_path = os.path.join(self.model_dir, "topic_model.pkl")
            if os.path.exists(topic_model_path):
                with open(topic_model_path, "rb") as f:
                    self.topic_model = pickle.load(f)
            
            # Load ruling classifier
            classifier_path = os.path.join(self.model_dir, "ruling_classifier.pkl")
            if os.path.exists(classifier_path):
                with open(classifier_path, "rb") as f:
                    self.ruling_classifier = pickle.load(f)
            
            # Load writing style model
            style_path = os.path.join(self.model_dir, "writing_style_kmeans.pkl")
            if os.path.exists(style_path):
                with open(style_path, "rb") as f:
                    self.writing_style_kmeans = pickle.load(f)
            
            logger.info("Successfully loaded models from disk")
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False

# Usage example
if __name__ == "__main__":
    # Initialize profiler
    profiler = JudgeProfiler()
    
    # Example opinions data (would come from Court Listener API)
    example_opinions = [
        {
            "text": "The court finds that the plaintiff has failed to establish a prima facie case...",
            "author_id": "judge1",
            "outcome": "dismissed",
            "case_type": "real property",
            "date_filed": "2020-01-15",
            "citation_count": 3
        },
        {
            "text": "Upon review of the evidence, the court grants summary judgment in favor of the defendant...",
            "author_id": "judge1",
            "outcome": "affirmed",
            "case_type": "contracts",
            "date_filed": "2019-05-22",
            "citation_count": 0
        },
        # More opinions would be here...
    ]
    
    # Analyze judge
    profile = profiler.analyze_judge("judge1", example_opinions)
    print(f"Created profile for judge1 with {len(example_opinions)} opinions")
    
    # Make a prediction
    new_case = "Plaintiff alleges breach of contract regarding commercial lease agreement..."
    prediction = profiler.predict_outcome(new_case, "judge1")
    print(f"Predicted outcome: {prediction['predicted_outcome']} with confidence {prediction['confidence']:.2f}")

            