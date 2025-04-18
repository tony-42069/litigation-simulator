"""
Judge Analysis API Endpoints

This module provides API endpoints for the judge analysis functionality.
It interfaces with the judge_analysis.py module to analyze judges based on
their opinions.
"""

import logging
import os
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from judge_analysis import JudgeProfiler
from auth import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the judge profiler
MODEL_DIR = os.getenv("MODEL_DIR", "./models")
try:
    judge_profiler = JudgeProfiler(model_dir=MODEL_DIR)
    logger.info("Judge profiler initialized successfully")
except (ImportError, RuntimeError) as e:
    logger.error(f"Failed to initialize judge profiler: {str(e)}")
    judge_profiler = None

# Create router
router = APIRouter(
    prefix="/api/judge-analysis",
    tags=["judge-analysis"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request/response validation
class OpinionData(BaseModel):
    """Model for opinion data."""
    text: str
    outcome: str = Field(..., description="Outcome of the case (e.g., 'affirmed', 'reversed', 'granted', 'denied')")
    case_type: str = Field(..., description="Type of case (e.g., 'civil', 'criminal', 'administrative')")
    date_filed: Optional[str] = None
    
class JudgeAnalysisRequest(BaseModel):
    """Model for judge analysis request."""
    judge_id: str
    opinions: List[OpinionData]
    
class JudgeProfile(BaseModel):
    """Model for judge profile response."""
    judge_id: str
    statistics: Dict[str, Any]
    writing_style: Dict[str, Any]
    topics: Dict[str, Any]
    ruling_patterns: Dict[str, Any]

@router.post("/analyze", response_model=JudgeProfile)
async def analyze_judge(
    request: JudgeAnalysisRequest,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a judge based on their opinions.
    
    This endpoint processes a collection of opinions authored by a judge
    and returns a comprehensive analysis of the judge's writing style,
    topics they discuss, and patterns in their rulings.
    
    Args:
        request: Judge analysis request data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        JudgeProfile: Comprehensive profile of the judge
    """
    if judge_profiler is None:
        raise HTTPException(status_code=503, detail="Judge analysis service unavailable. Required dependencies missing.")
        
    try:
        logger.info(f"Analyzing judge {request.judge_id} with {len(request.opinions)} opinions")
        
        # Convert opinions to the format expected by JudgeProfiler
        opinions_data = [opinion.dict() for opinion in request.opinions]
        
        # Analyze judge
        profile = judge_profiler.analyze_judge(request.judge_id, opinions_data)
        
        # Save results to database (optional)
        # This would be implemented with SQLAlchemy
        
        return profile
    except Exception as e:
        logger.error(f"Error analyzing judge: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/profile/{judge_id}", response_model=JudgeProfile)
async def get_judge_profile(
    judge_id: str,
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the profile of a judge by ID.
    
    This endpoint retrieves a previously generated judge profile from the database.
    If no profile exists, it returns a 404 error.
    
    Args:
        judge_id: ID of the judge
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        JudgeProfile: Profile of the judge
    """
    if judge_profiler is None:
        raise HTTPException(status_code=503, detail="Judge analysis service unavailable. Required dependencies missing.")
        
    try:
        # Here we would normally fetch from database
        # For now, we'll just return an error because we haven't stored anything
        raise HTTPException(status_code=404, detail=f"Judge profile for ID {judge_id} not found")
    except Exception as e:
        logger.error(f"Error fetching judge profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_judges(
    query: str = Query(..., description="Search query for judges"),
    limit: int = Query(10, description="Maximum number of results to return"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for judges matching the query.
    
    This endpoint searches for judges whose names or other properties
    match the provided query string.
    
    Args:
        query: Search query
        limit: Maximum number of results to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[Dict]: List of matching judges
    """
    if judge_profiler is None:
        raise HTTPException(status_code=503, detail="Judge analysis service unavailable. Required dependencies missing.")
        
    try:
        # Here we would normally search in database
        # For demonstration, return empty list
        return []
    except Exception as e:
        logger.error(f"Error searching judges: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/similar-judges/{judge_id}", response_model=List[Dict[str, Any]])
async def get_similar_judges(
    judge_id: str,
    limit: int = Query(5, description="Maximum number of results to return"),
    current_user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Find judges similar to the specified judge.
    
    This endpoint identifies judges with similar ruling patterns,
    writing styles, or topic distributions to the specified judge.
    
    Args:
        judge_id: ID of the reference judge
        limit: Maximum number of similar judges to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[Dict]: List of similar judges with similarity scores
    """
    if judge_profiler is None:
        raise HTTPException(status_code=503, detail="Judge analysis service unavailable. Required dependencies missing.")
        
    try:
        # This would require additional logic to compute similarity
        # For demonstration, return empty list
        return []
    except Exception as e:
        logger.error(f"Error finding similar judges: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Similarity search failed: {str(e)}") 