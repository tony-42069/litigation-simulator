"""
Case Prediction API Endpoints

This module provides API endpoints for the case prediction functionality.
It interfaces with the case_prediction.py module to predict case and motion
outcomes based on various factors.
"""

import logging
import os
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from case_prediction import CaseOutcomePredictor
from auth import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the case predictor
MODEL_DIR = os.getenv("MODEL_DIR", "./models")
try:
    case_predictor = CaseOutcomePredictor(model_dir=MODEL_DIR)
    logger.info("Case prediction module initialized successfully")
except ImportError:
    logger.error("Failed to initialize case prediction module. Required packages may be missing.")
    case_predictor = None

# Create router
router = APIRouter(
    prefix="/api/case-prediction",
    tags=["case-prediction"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request/response validation
class JudgeInfo(BaseModel):
    """Model for judge information."""
    id: Optional[str] = None
    name: Optional[str] = None
    experience_years: Optional[int] = None
    court: Optional[str] = None
    
class JurisdictionInfo(BaseModel):
    """Model for jurisdiction information."""
    federal: Optional[int] = Field(None, description="1 for federal, 0 for state")
    state: Optional[str] = None
    district: Optional[str] = None
    circuit: Optional[str] = None

class CasePredictionRequest(BaseModel):
    """Model for case prediction request."""
    case_type: str = Field(..., description="Type of case (e.g., 'civil', 'criminal', 'administrative')")
    facts: str = Field(..., description="Text description of case facts")
    jurisdiction: JurisdictionInfo
    judge: Optional[JudgeInfo] = None
    precedent_strength: Optional[float] = Field(None, description="Strength of precedent (0-1)")
    claim_amount: Optional[float] = Field(None, description="Amount claimed in monetary damages")
    
class MotionPredictionRequest(BaseModel):
    """Model for motion prediction request."""
    case_type: str
    facts: str
    motion_type: str = Field(..., description="Type of motion (e.g., 'summary_judgment', 'dismiss')")
    jurisdiction: JurisdictionInfo
    judge: Optional[JudgeInfo] = None
    precedent_strength: Optional[float] = None
    
class PredictionResponse(BaseModel):
    """Model for prediction response."""
    outcome: str
    probability: float
    confidence: str
    feature_impact: Dict[str, float]
    
class FactorAnalysisResponse(BaseModel):
    """Model for factor analysis response."""
    base_prediction: PredictionResponse
    factors: Dict[str, float]
    what_if: Dict[str, Dict[str, Dict[str, Any]]]

@router.post("/case", response_model=PredictionResponse)
async def predict_case_outcome(
    request: CasePredictionRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict the outcome of a case.
    
    This endpoint predicts the outcome of a case based on various factors such as
    case type, jurisdiction, judge, etc.
    
    Args:
        request: Case prediction request data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PredictionResponse: Prediction results including outcome, confidence, and probabilities
    """
    if case_predictor is None:
        raise HTTPException(status_code=503, detail="Case prediction service unavailable. Required dependencies missing.")
        
    try:
        logger.info(f"Predicting outcome for case type: {request.case_type}")
        
        # Convert request to the format expected by CaseOutcomePredictor
        case_data = request.dict()
        
        # Predict case outcome
        prediction = case_predictor.predict_case_outcome(case_data)
        
        # Store prediction in database (optional)
        # This would be implemented with SQLAlchemy
        
        return prediction
    except ValueError as e:
        logger.error(f"Error predicting case outcome: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error predicting case outcome: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/motion", response_model=PredictionResponse)
async def predict_motion_outcome(
    request: MotionPredictionRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict the outcome of a motion.
    
    This endpoint predicts the outcome of a motion based on various factors such as
    motion type, case type, jurisdiction, judge, etc.
    
    Args:
        request: Motion prediction request data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        PredictionResponse: Prediction results including outcome, confidence, and probabilities
    """
    if case_predictor is None:
        raise HTTPException(status_code=503, detail="Case prediction service unavailable. Required dependencies missing.")
        
    try:
        logger.info(f"Predicting outcome for motion type: {request.motion_type}")
        
        # Convert request to the format expected by CaseOutcomePredictor
        case_data = request.dict()
        
        # Predict motion outcome
        prediction = case_predictor.predict_motion_outcome(case_data)
        
        # Store prediction in database (optional)
        # This would be implemented with SQLAlchemy
        
        return prediction
    except ValueError as e:
        logger.error(f"Error predicting motion outcome: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error predicting motion outcome: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/analyze-factors", response_model=FactorAnalysisResponse)
async def analyze_case_factors(
    request: CasePredictionRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze the impact of different factors on case outcome.
    
    This endpoint analyzes how different factors like judge, jurisdiction, precedent, etc.
    affect the predicted outcome of a case.
    
    Args:
        request: Case prediction request data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        FactorAnalysisResponse: Factor analysis results
    """
    if case_predictor is None:
        raise HTTPException(status_code=503, detail="Case prediction service unavailable. Required dependencies missing.")
        
    try:
        logger.info(f"Analyzing factors for case type: {request.case_type}")
        
        # Convert request to the format expected by CaseOutcomePredictor
        case_data = request.dict()
        
        # Analyze factors
        analysis = case_predictor.analyze_factors(case_data)
        
        return analysis
    except ValueError as e:
        logger.error(f"Error analyzing case factors: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error analyzing case factors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/history/{case_id}", response_model=Dict[str, Any])
async def get_prediction_history(
    case_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get prediction history for a case.
    
    This endpoint retrieves the history of predictions for a case,
    including when they were made and how they've changed over time.
    
    Args:
        case_id: ID of the case
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Dict: Prediction history for the case
    """
    try:
        # Here we would normally fetch from database
        # For now, we'll just return an error because we haven't stored anything
        raise HTTPException(status_code=404, detail=f"Prediction history for case ID {case_id} not found")
    except Exception as e:
        logger.error(f"Error fetching prediction history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}") 