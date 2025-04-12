"""
Case Outcome Prediction Module

This module implements the prediction engine for the Litigation Simulator.
It combines multiple data sources and models to predict case outcomes
based on case facts, judge profiles, legal precedents, and more.
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler
import torch
from transformers import AutoTokenizer, AutoModel
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CaseOutcomePredictor:
    """
    Predicts the outcomes of legal cases based on various features including
    case facts, judge behavior, jurisdiction, and case type.
    """
    
    CASE_TYPES = [
        "foreclosure",
        "lease_dispute",
        "zoning", 
        "land_use",
        "contract_dispute",
        "financing_dispute",
        "developer_dispute",
        "contractor_dispute",
        "property_tax",
        "eminent_domain",
        "environmental",
        "other"
    ]
    
    MOTION_TYPES = [
        "summary_judgment",
        "motion_to_dismiss",
        "preliminary_injunction",
        "temporary_restraining_order",
        "discovery_motion",
        "class_certification",
        "judgment_as_matter_of_law",
        "other"
    ]
    
    OUTCOME_TYPES = [
        "plaintiff_full",
        "plaintiff_partial",
        "defendant_win",
        "settlement",
        "dismissed",
        "remanded",
        "other"
    ]
    
    def __init__(self, model_dir: str = "./models"):
        """
        Initialize the CaseOutcomePredictor.
        
        Args:
            model_dir: Directory to save/load model files
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize models
        self.case_outcome_model = None
        self.motion_outcome_model = None
        self.feature_scaler = None
        
        # Initialize embeddings model
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.embedding_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
        logger.info("CaseOutcomePredictor initialized")
        
    def _get_text_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for text using the sentence transformer model.
        
        Args:
            text: Text to embed
            
        Returns:
            Text embedding array
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=512
        )
        
        # Generate embeddings
        with torch.no_grad():
            outputs = self.embedding_model(**inputs)
            
        # Use mean pooling to get sentence embeddings
        embeddings = outputs.last_hidden_state.mean(dim=1).numpy()[0]
        
        return embeddings
    
    def _extract_features(self, case_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from case data for prediction.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Feature vector for the case
        """
        features = []
        
        # Case type one-hot encoding
        case_type = case_data.get("case_type", "other")
        case_type_vector = [1 if t == case_type else 0 for t in self.CASE_TYPES]
        features.extend(case_type_vector)
        
        # Text embedding of case facts
        case_facts = case_data.get("case_facts", "")
        if case_facts:
            text_embedding = self._get_text_embedding(case_facts)
            features.extend(text_embedding)
        else:
            # Add zeros if no case facts provided
            features.extend([0] * 384)  # Embedding dimension
        
        # Jurisdiction features
        jurisdiction = case_data.get("jurisdiction", {})
        features.append(jurisdiction.get("federal", 0))
        
        # Judge features
        judge_data = case_data.get("judge", {})
        features.append(judge_data.get("years_experience", 0))
        features.append(judge_data.get("plaintiff_favor_rate", 0.5))
        features.append(judge_data.get("defendant_favor_rate", 0.5))
        
        # Precedent strength
        features.append(case_data.get("precedent_strength", 0.5))
        
        # Motion-specific features (for motion prediction only)
        if "motion_type" in case_data:
            motion_type = case_data["motion_type"]
            motion_vector = [1 if t == motion_type else 0 for t in self.MOTION_TYPES]
            features.extend(motion_vector)
        
        return np.array(features).astype(np.float32)
    
    def train_case_outcome_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the case outcome prediction model.
        
        Args:
            training_data: List of case data with outcomes
            
        Returns:
            Training results
        """
        logger.info(f"Training case outcome model with {len(training_data)} cases")
        
        # Extract features and targets
        X = []
        y = []
        
        for case in training_data:
            # Skip cases without outcome
            if "outcome" not in case:
                continue
                
            # Extract features
            features = self._extract_features(case)
            X.append(features)
            
            # Get outcome
            outcome = case["outcome"]
            if outcome not in self.OUTCOME_TYPES:
                outcome = "other"
            y.append(self.OUTCOME_TYPES.index(outcome))
        
        if len(X) < 10:
            logger.warning("Insufficient training data")
            return {"error": "Insufficient training data"}
        
        # Convert to numpy arrays
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        self.feature_scaler = StandardScaler()
        X_scaled = self.feature_scaler.fit_transform(X)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.case_outcome_model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        self.case_outcome_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.case_outcome_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Feature importance
        importances = self.case_outcome_model.feature_importances_
        
        # Save model
        model_path = os.path.join(self.model_dir, "case_outcome_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(self.case_outcome_model, f)
            
        scaler_path = os.path.join(self.model_dir, "feature_scaler.pkl")
        with open(scaler_path, "wb") as f:
            pickle.dump(self.feature_scaler, f)
            
        logger.info(f"Saved case outcome model with accuracy {accuracy:.4f}")
        
        return {
            "accuracy": float(accuracy),
            "classification_report": report,
            "feature_importance": importances.tolist(),
            "n_samples": len(X)
        }
    
    def train_motion_outcome_model(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the motion outcome prediction model.
        
        Args:
            training_data: List of motion data with outcomes
            
        Returns:
            Training results
        """
        logger.info(f"Training motion outcome model with {len(training_data)} motions")
        
        # Extract features and targets
        X = []
        y = []
        
        for motion in training_data:
            # Skip motions without outcome
            if "outcome" not in motion:
                continue
                
            # Extract features
            features = self._extract_features(motion)
            X.append(features)
            
            # Get outcome (binary: granted or denied)
            outcome = 1 if motion["outcome"] == "granted" else 0
            y.append(outcome)
        
        if len(X) < 10:
            logger.warning("Insufficient training data")
            return {"error": "Insufficient training data"}
        
        # Convert to numpy arrays
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        if self.feature_scaler is None:
            self.feature_scaler = StandardScaler()
            X_scaled = self.feature_scaler.fit_transform(X)
        else:
            X_scaled = self.feature_scaler.transform(X)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.motion_outcome_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.motion_outcome_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.motion_outcome_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
        
        # Feature importance
        importances = self.motion_outcome_model.feature_importances_
        
        # Save model
        model_path = os.path.join(self.model_dir, "motion_outcome_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(self.motion_outcome_model, f)
            
        logger.info(f"Saved motion outcome model with accuracy {accuracy:.4f}")
        
        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "feature_importance": importances.tolist(),
            "n_samples": len(X)
        }
    
    def predict_case_outcome(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict the outcome of a case.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Prediction results including outcome and confidence
        """
        if self.case_outcome_model is None:
            return {"error": "Case outcome model not trained"}
            
        # Extract features
        features = self._extract_features(case_data)
        features = features.reshape(1, -1)
        
        # Scale features
        if self.feature_scaler is not None:
            features = self.feature_scaler.transform(features)
        
        # Predict
        outcome_idx = self.case_outcome_model.predict(features)[0]
        probas = self.case_outcome_model.predict_proba(features)[0]
        
        # Get outcome and confidence
        outcome = self.OUTCOME_TYPES[outcome_idx]
        confidence = float(probas[outcome_idx])
        
        # Get all class probabilities
        class_probas = {outcome: float(prob) for outcome, prob in zip(self.OUTCOME_TYPES, probas)}
        
        # Get feature importance for this prediction
        if hasattr(self.case_outcome_model, 'feature_importances_'):
            importances = self.case_outcome_model.feature_importances_
            feature_impact = {"importance": importances.tolist()}
        else:
            feature_impact = {}
        
        return {
            "predicted_outcome": outcome,
            "confidence": confidence,
            "class_probabilities": class_probas,
            "feature_impact": feature_impact
        }
    
    def predict_motion_outcome(self, motion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict the outcome of a motion.
        
        Args:
            motion_data: Dictionary containing motion information
            
        Returns:
            Prediction results including outcome and confidence
        """
        if self.motion_outcome_model is None:
            return {"error": "Motion outcome model not trained"}
            
        # Extract features
        features = self._extract_features(motion_data)
        features = features.reshape(1, -1)
        
        # Scale features
        if self.feature_scaler is not None:
            features = self.feature_scaler.transform(features)
        
        # Predict
        outcome = self.motion_outcome_model.predict(features)[0]
        probas = self.motion_outcome_model.predict_proba(features)[0]
        
        # Get confidence
        confidence = float(probas[outcome])
        
        # Result as string
        outcome_str = "granted" if outcome == 1 else "denied"
        
        # Get feature importance for this prediction
        if hasattr(self.motion_outcome_model, 'feature_importances_'):
            importances = self.motion_outcome_model.feature_importances_
            feature_impact = {"importance": importances.tolist()}
        else:
            feature_impact = {}
        
        return {
            "predicted_outcome": outcome_str,
            "confidence": confidence,
            "probability_granted": float(probas[1]),
            "probability_denied": float(probas[0]),
            "feature_impact": feature_impact
        }
    
    def analyze_factors(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the impact of different factors on the case outcome.
        
        Args:
            case_data: Dictionary containing case information
            
        Returns:
            Analysis of factor impact
        """
        if self.case_outcome_model is None:
            return {"error": "Case outcome model not trained"}
        
        # Get base prediction
        base_prediction = self.predict_case_outcome(case_data)
        
        # Analyze judge impact
        judge_factors = {}
        if "judge" in case_data:
            original_judge = case_data.get("judge", {})
            
            # Test with a neutral judge
            neutral_judge = {
                "years_experience": 10,
                "plaintiff_favor_rate": 0.5,
                "defendant_favor_rate": 0.5
            }
            
            case_data["judge"] = neutral_judge
            neutral_prediction = self.predict_case_outcome(case_data)
            
            # Calculate impact
            judge_impact = neutral_prediction["confidence"] - base_prediction["confidence"]
            
            judge_factors = {
                "impact": float(judge_impact),
                "neutral_prediction": neutral_prediction["predicted_outcome"],
                "neutral_confidence": neutral_prediction["confidence"]
            }
            
            # Restore original judge
            case_data["judge"] = original_judge
        
        # Analyze case type impact
        case_type_factors = {}
        original_case_type = case_data.get("case_type", "other")
        
        for case_type in self.CASE_TYPES:
            if case_type != original_case_type:
                case_data["case_type"] = case_type
                type_prediction = self.predict_case_outcome(case_data)
                
                case_type_factors[case_type] = {
                    "predicted_outcome": type_prediction["predicted_outcome"],
                    "confidence": type_prediction["confidence"],
                    "impact": float(type_prediction["confidence"] - base_prediction["confidence"])
                }
        
        # Restore original case type
        case_data["case_type"] = original_case_type
        
        # Analyze precedent impact
        precedent_factors = {}
        original_precedent = case_data.get("precedent_strength", 0.5)
        
        for strength in [0.0, 0.25, 0.5, 0.75, 1.0]:
            if abs(strength - original_precedent) > 0.1:
                case_data["precedent_strength"] = strength
                precedent_prediction = self.predict_case_outcome(case_data)
                
                precedent_factors[str(strength)] = {
                    "predicted_outcome": precedent_prediction["predicted_outcome"],
                    "confidence": precedent_prediction["confidence"],
                    "impact": float(precedent_prediction["confidence"] - base_prediction["confidence"])
                }
        
        # Restore original precedent strength
        case_data["precedent_strength"] = original_precedent
        
        return {
            "base_prediction": base_prediction,
            "judge_factors": judge_factors,
            "case_type_factors": case_type_factors,
            "precedent_factors": precedent_factors
        }
    
    def load_models(self) -> bool:
        """
        Load trained models from disk.
        
        Returns:
            True if models loaded successfully, False otherwise
        """
        try:
            # Load case outcome model
            model_path = os.path.join(self.model_dir, "case_outcome_model.pkl")
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    self.case_outcome_model = pickle.load(f)
            
            # Load motion outcome model
            motion_model_path = os.path.join(self.model_dir, "motion_outcome_model.pkl")
            if os.path.exists(motion_model_path):
                with open(motion_model_path, "rb") as f:
                    self.motion_outcome_model = pickle.load(f)
            
            # Load feature scaler
            scaler_path = os.path.join(self.model_dir, "feature_scaler.pkl")
            if os.path.exists(scaler_path):
                with open(scaler_path, "rb") as f:
                    self.feature_scaler = pickle.load(f)
            
            logger.info("Successfully loaded models from disk")
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize predictor
    predictor = CaseOutcomePredictor()
    
    # Example case data
    example_case = {
        "case_type": "lease_dispute",
        "case_facts": "Plaintiff alleges that defendant breached commercial lease agreement by failing to maintain the property as required by Section 8 of the lease. Defendant counterclaims that plaintiff's modifications to the property violated the lease terms.",
        "jurisdiction": {
            "federal": 0,
            "state": "NY"
        },
        "judge": {
            "years_experience": 15,
            "plaintiff_favor_rate": 0.6,
            "defendant_favor_rate": 0.4
        },
        "precedent_strength": 0.7
    }
    
    # Train models with example data (would normally use real data)
    training_data = [
        {**example_case, "outcome": "plaintiff_full"},
        {**example_case, "outcome": "plaintiff_partial", "case_type": "foreclosure"},
        {**example_case, "outcome": "defendant_win", "case_type": "zoning"}
        # More training examples would be here...
    ]
    
    # Try to load existing models first
    if not predictor.load_models():
        # Train new models if loading failed
        predictor.train_case_outcome_model(training_data)
    
    # Make a prediction
    prediction = predictor.predict_case_outcome(example_case)
    print(f"Predicted outcome: {prediction['predicted_outcome']} with confidence {prediction['confidence']:.2f}")
    
    # Analyze factors
    factor_analysis = predictor.analyze_factors(example_case)
    print(f"Judge impact: {factor_analysis['judge_factors'].get('impact', 0):.2f}")
