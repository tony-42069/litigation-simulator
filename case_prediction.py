"""
Case Outcome Prediction Module for the Litigation Simulator.

This module implements machine learning functionality to predict
case outcomes and motion outcomes based on various factors.
"""

import os
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Union
import re
import string
import pickle
from datetime import datetime

# Import required ML libraries
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CaseOutcomePredictor:
    """
    Class for predicting case and motion outcomes.
    
    This class uses machine learning to predict the outcomes of cases and motions
    based on various factors such as case facts, judge information, and jurisdiction.
    """
    
    def __init__(self, model_dir: str = None):
        """
        Initialize the CaseOutcomePredictor.
        
        Args:
            model_dir: Directory to store/load trained models
        """
        self.model_dir = model_dir or os.getenv("MODEL_DIR", "./models")
        
        # Models
        self.case_model = None
        self.motion_model = None
        
        # Feature importance tracking
        self.feature_names = []
        
        # Create model directory if it doesn't exist
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Try to load pre-trained models
        self.load_models()
    
    def load_models(self) -> bool:
        """
        Load pre-trained models if available.
        
        Returns:
            bool: True if models were loaded, False otherwise
        """
        try:
            logger.info("Attempting to load pre-trained case prediction models...")
            
            # Path to model files
            case_model_path = os.path.join(self.model_dir, 'case_outcome_model.pkl')
            motion_model_path = os.path.join(self.model_dir, 'motion_outcome_model.pkl')
            feature_names_path = os.path.join(self.model_dir, 'feature_names.json')
            
            # Check if files exist
            if not all(os.path.exists(path) for path in [case_model_path, motion_model_path]):
                logger.info("One or more model files missing. Will train new models when needed.")
                return False
            
            # Load models
            self.case_model = pickle.load(open(case_model_path, 'rb'))
            self.motion_model = pickle.load(open(motion_model_path, 'rb'))
            
            # Load feature names if available
            if os.path.exists(feature_names_path):
                with open(feature_names_path, 'r') as f:
                    self.feature_names = json.load(f)
            
            logger.info("Case prediction models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading pre-trained models: {str(e)}")
            return False
    
    def save_models(self) -> bool:
        """
        Save trained models to disk.
        
        Returns:
            bool: True if models were saved, False otherwise
        """
        try:
            logger.info("Saving trained case prediction models...")
            
            # Check if models exist
            if not self.case_model or not self.motion_model:
                logger.warning("Models not available for saving")
                return False
            
            # Save models
            pickle.dump(self.case_model, open(os.path.join(self.model_dir, 'case_outcome_model.pkl'), 'wb'))
            pickle.dump(self.motion_model, open(os.path.join(self.model_dir, 'motion_outcome_model.pkl'), 'wb'))
            
            # Save feature names
            with open(os.path.join(self.model_dir, 'feature_names.json'), 'w') as f:
                json.dump(self.feature_names, f)
            
            logger.info("Case prediction models saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            return False
    
    def train_case_outcome_model(self, training_data: List[Dict[str, Any]]) -> bool:
        """
        Train a model to predict case outcomes.
        
        Args:
            training_data: List of training examples
                Each example should include:
                - case_type (str): Type of case
                - case_facts (str): Text description of case facts
                - jurisdiction (dict): Jurisdiction info (federal, state)
                - outcome (str): Actual outcome (target)
                - judge (dict, optional): Judge information
                
        Returns:
            bool: True if training was successful, False otherwise
        """
        logger.info(f"Training case outcome model with {len(training_data)} examples")
        
        if not training_data:
            logger.error("No training data provided")
            return False
        
        try:
            # Convert to pandas DataFrame
            df = pd.DataFrame(training_data)
            
            # Extract features and target
            X = df.drop('outcome', axis=1)
            y = df['outcome']
            
            # Prepare feature preprocessing
            preprocessor = self._build_feature_preprocessor()
            
            # Create pipeline with classifier
            self.case_model = Pipeline([
                ('preprocessor', preprocessor),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
            
            # Train model
            self.case_model.fit(X, y)
            
            # Extract feature names (for feature importance analysis)
            self.feature_names = self._extract_feature_names(preprocessor)
            
            # Save trained model
            self.save_models()
            
            return True
            
        except Exception as e:
            logger.error(f"Error training case outcome model: {str(e)}")
            return False
    
    def train_motion_outcome_model(self, training_data: List[Dict[str, Any]]) -> bool:
        """
        Train a model to predict motion outcomes.
        
        Args:
            training_data: List of training examples
                Each example should include:
                - case_type (str): Type of case
                - case_facts (str): Text description of case facts
                - jurisdiction (dict): Jurisdiction info (federal, state)
                - motion_type (str): Type of motion
                - outcome (str): Actual outcome (target)
                - judge (dict, optional): Judge information
                
        Returns:
            bool: True if training was successful, False otherwise
        """
        logger.info(f"Training motion outcome model with {len(training_data)} examples")
        
        if not training_data:
            logger.error("No training data provided")
            return False
        
        try:
            # Convert to pandas DataFrame
            df = pd.DataFrame(training_data)
            
            # Extract features and target
            X = df.drop('outcome', axis=1)
            y = df['outcome']
            
            # Prepare feature preprocessing
            preprocessor = self._build_feature_preprocessor(include_motion_type=True)
            
            # Create pipeline with classifier
            self.motion_model = Pipeline([
                ('preprocessor', preprocessor),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
            
            # Train model
            self.motion_model.fit(X, y)
            
            # Save trained model
            self.save_models()
            
            return True
            
        except Exception as e:
            logger.error(f"Error training motion outcome model: {str(e)}")
            return False
    
    def predict_case_outcome(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict case outcome based on provided case data.
        
        Args:
            case_data: Dictionary containing case information
                - facts: Text description of case facts
                - case_type: Type of case (e.g., 'civil', 'criminal')
                - motion_type: (Optional) Type of motion if applicable
                
        Returns:
            Dict with prediction results:
                - outcome: Predicted outcome (PLAINTIFF/DEFENDANT or GRANTED/DENIED for motions)
                - probability: Confidence score (0-1)
                - confidence: Text representation of confidence (low/medium/high)
                - feature_impact: Dictionary of top features and their impact
        """
        # Determine if this is a motion prediction
        is_motion = 'motion_type' in case_data and case_data['motion_type']
        
        # Select appropriate model
        model = self.motion_model if is_motion else self.case_model
        
        if model is None:
            raise ValueError(f"No {'motion' if is_motion else 'case'} model available")
        
        # Predict with the selected model
        return self._predict_with_model(case_data, model, is_motion)
    
    def predict_motion_outcome(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict outcome of a motion based on provided case data.
        
        Args:
            case_data: Dictionary containing case information
                - facts: Text description of case facts
                - case_type: Type of case (e.g., 'civil', 'criminal')
                - motion_type: Type of motion
                
        Returns:
            Dict with prediction results:
                - outcome: Predicted outcome (GRANTED/DENIED)
                - probability: Confidence score (0-1)
                - confidence: Text representation of confidence (low/medium/high) 
                - feature_impact: Dictionary of top features and their impact
        """
        # Make sure motion_type is included
        if 'motion_type' not in case_data or not case_data['motion_type']:
            raise ValueError("No motion_type provided for motion prediction")
        
        # Check if motion model is available
        if self.motion_model is None:
            raise ValueError("No motion model available")
        
        # Predict with the motion model
        return self._predict_with_model(case_data, self.motion_model, is_motion=True)
    
    def analyze_factors(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the impact of different factors on case outcome.
        
        Args:
            case_data: Case information (see predict_case_outcome for details)
                
        Returns:
            dict: Analysis results, including:
                - factors: List of factors and their impact on outcome
                - what_if: Results of what-if scenarios (changing factors)
        """
        logger.info("Analyzing case factors")
        
        # Base prediction
        base_prediction = self.predict_case_outcome(case_data)
        
        # Factor importance analysis
        factors = self._analyze_feature_importance(case_data)
        
        # What-if scenarios
        what_if = self._generate_what_if_scenarios(case_data)
        
        return {
            "base_prediction": base_prediction,
            "factors": factors,
            "what_if": what_if
        }
    
    def _build_feature_preprocessor(self, include_motion_type: bool = False) -> ColumnTransformer:
        """
        Build a scikit-learn ColumnTransformer for feature preprocessing.
        
        Args:
            include_motion_type: Whether to include motion_type in features
            
        Returns:
            ColumnTransformer: Preprocessor for features
        """
        # Text preprocessor for case facts
        text_features = ['case_facts']
        text_transformer = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english'))
        ])
        
        # Categorical features
        categorical_features = ['case_type']
        
        if include_motion_type:
            categorical_features.append('motion_type')
        
        categorical_transformer = Pipeline([
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        # Combine transformers
        preprocessor = ColumnTransformer(
            transformers=[
                ('text', text_transformer, text_features),
                ('cat', categorical_transformer, categorical_features)
            ],
            remainder='drop'  # Drop other columns not specified
        )
        
        return preprocessor
    
    def _extract_feature_names(self, preprocessor: ColumnTransformer) -> List[str]:
        """
        Extract feature names from ColumnTransformer.
        
        Args:
            preprocessor: The ColumnTransformer object
            
        Returns:
            List of feature names
        """
        try:
            # Get all transformer names
            feature_names = []
            
            # Extract from TfidfVectorizer
            text_transformer = preprocessor.named_transformers_['text'].named_steps['tfidf']
            text_features = [f'tfidf_{i}' for i in text_transformer.get_feature_names_out()]
            feature_names.extend(text_features)
            
            # Extract from OneHotEncoder
            cat_transformer = preprocessor.named_transformers_['cat'].named_steps['onehot']
            cat_features = cat_transformer.get_feature_names_out().tolist()
            feature_names.extend(cat_features)
            
            return feature_names
        except Exception as e:
            logger.error(f"Error extracting feature names: {str(e)}")
            return []
    
    def _predict_with_model(self, case_data: Dict[str, Any], model: Pipeline, is_motion: bool) -> Dict[str, Any]:
        """
        Make prediction with the specified model.
        
        Args:
            case_data: Dictionary containing case information
            model: Trained sklearn Pipeline model
            is_motion: Whether this is a motion prediction
            
        Returns:
            Dict with prediction results
        """
        try:
            # Prepare the features
            features = pd.DataFrame({
                'case_facts': [case_data.get('facts', '')],
                'case_type': [case_data.get('case_type', 'other')]
            })
            
            if is_motion:
                features['motion_type'] = case_data.get('motion_type', 'other')
            
            # Get prediction and probability
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            probability = probabilities[1] if prediction == 1 else probabilities[0]
            
            # Map confidence level
            confidence = "low"
            if probability >= 0.8:
                confidence = "high"
            elif probability >= 0.6:
                confidence = "medium"
            
            # Calculate feature impact
            feature_impact = self._calculate_feature_impact(model, features)
            
            # Map numerical outcome to string
            outcome = "GRANTED" if prediction == 1 else "DENIED" if is_motion else "PLAINTIFF" if prediction == 1 else "DEFENDANT"
            
            return {
                "outcome": outcome,
                "probability": float(probability),
                "confidence": confidence,
                "feature_impact": feature_impact
            }
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            raise ValueError(f"Prediction error: {str(e)}")
    
    def _calculate_feature_impact(self, model: Pipeline, features: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate the impact of features on the prediction.
        
        Args:
            model: Trained sklearn Pipeline model
            features: DataFrame containing case facts and type
            
        Returns:
            dict: Feature importance scores
        """
        feature_impact = {}
        
        try:
            # Get the actual classifier from the pipeline
            classifier = None
            for _, step in model.named_steps.items():
                if hasattr(step, "feature_importances_") or hasattr(step, "coef_"):
                    classifier = step
                    break
            
            if classifier is None:
                return feature_impact
            
            # Extract features from the trained model
            if isinstance(classifier, RandomForestClassifier):
                importances = classifier.feature_importances_
                feature_names = self.feature_names
                
                # Create dictionary of feature importances
                for name, importance in zip(feature_names, importances):
                    if importance > 0.01:  # Only include features with significant impact
                        feature_impact[name] = float(importance)
            
            elif hasattr(classifier, "coef_"):
                # For linear models like LogisticRegression
                coefficients = classifier.coef_[0] if classifier.coef_.ndim > 1 else classifier.coef_
                feature_names = self.feature_names
                
                # Create dictionary of feature coefficients
                for name, coef in zip(feature_names, coefficients):
                    if abs(coef) > 0.01:  # Only include features with significant impact
                        feature_impact[name] = float(coef)
            
            # Sort by absolute importance and keep top 10
            feature_impact = dict(sorted(feature_impact.items(), 
                                          key=lambda x: abs(x[1]), 
                                          reverse=True)[:10])
            
            return feature_impact
            
        except Exception as e:
            logger.error(f"Error calculating feature impact: {str(e)}")
            return {}
    
    def _analyze_feature_importance(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze the importance of different case factors.
        
        Args:
            case_data: Case information
            
        Returns:
            list: List of factors and their impact
        """
        df = pd.DataFrame([case_data])
        return self._calculate_feature_impact(self.case_model, df)
    
    def _generate_what_if_scenarios(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate what-if scenarios by changing case factors.
        
        Args:
            case_data: Case information
            
        Returns:
            dict: Results of what-if scenarios
        """
        scenarios = {}
        
        # Base prediction
        base_prediction = self.predict_case_outcome(case_data)
        
        # Change case type
        case_types = ["contract_dispute", "lease_dispute", "foreclosure", "zoning", "land_use"]
        scenarios["case_type"] = {}
        
        for case_type in case_types:
            if case_type != case_data.get('case_type'):
                modified_data = case_data.copy()
                modified_data['case_type'] = case_type
                
                prediction = self.predict_case_outcome(modified_data)
                scenarios["case_type"][case_type] = {
                    "predicted_outcome": prediction["outcome"],
                    "confidence": prediction["confidence"]
                }
        
        # Change jurisdiction (federal vs. state)
        scenarios["jurisdiction"] = {}
        
        jurisdiction = case_data.get('jurisdiction', {}).copy()
        
        # Federal to state
        if jurisdiction.get('federal', 0) == 1:
            modified_data = case_data.copy()
            modified_jurisdiction = jurisdiction.copy()
            modified_jurisdiction['federal'] = 0
            modified_data['jurisdiction'] = modified_jurisdiction
            
            prediction = self.predict_case_outcome(modified_data)
            scenarios["jurisdiction"]["state"] = {
                "predicted_outcome": prediction["outcome"],
                "confidence": prediction["confidence"]
            }
        
        # State to federal
        if jurisdiction.get('federal', 0) == 0:
            modified_data = case_data.copy()
            modified_jurisdiction = jurisdiction.copy()
            modified_jurisdiction['federal'] = 1
            modified_data['jurisdiction'] = modified_jurisdiction
            
            prediction = self.predict_case_outcome(modified_data)
            scenarios["jurisdiction"]["federal"] = {
                "predicted_outcome": prediction["outcome"],
                "confidence": prediction["confidence"]
            }
        
        # Change precedent strength
        scenarios["precedent_strength"] = {}
        
        for strength in [0.1, 0.3, 0.5, 0.7, 0.9]:
            if abs(strength - case_data.get('precedent_strength', 0.5)) > 0.1:
                modified_data = case_data.copy()
                modified_data['precedent_strength'] = strength
                
                prediction = self.predict_case_outcome(modified_data)
                scenarios["precedent_strength"][str(strength)] = {
                    "predicted_outcome": prediction["outcome"],
                    "confidence": prediction["confidence"]
                }
        
        return scenarios 