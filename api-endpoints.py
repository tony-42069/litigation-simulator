"""
FastAPI endpoints for the Litigation Simulator

This module defines all API endpoints for the Litigation Simulator application,
including user management, judge profiles, case analysis, prediction, and
simulation interfaces.
"""

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import json
import os
import asyncio
from datetime import datetime, timedelta
import logging
import uuid

from judge_analysis import JudgeProfiler
from case_prediction import CaseOutcomePredictor
from simulation_engine import SimulationEngine
from court_listener_api import CourtListenerAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Litigation Simulator API",
    description="API for simulating litigation outcomes and judicial behavior",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize components
judge_profiler = JudgeProfiler()
case_predictor = CaseOutcomePredictor()
simulation_engine = SimulationEngine()

# Data models
class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class JudgeQuery(BaseModel):
    name: Optional[str] = None
    court: Optional[str] = None
    position_type: Optional[str] = None
    limit: int = 20
    offset: int = 0

class JudgeProfile(BaseModel):
    judge_id: str
    name: str
    position: Optional[str] = None
    court: Optional[str] = None
    stats: Dict[str, Any]
    writing_style: Dict[str, Any]
    topics: Dict[str, Any]

class CaseData(BaseModel):
    case_type: str
    case_facts: str
    jurisdiction: Dict[str, Any]
    judge: Optional[Dict[str, Any]] = None
    precedent_strength: Optional[float] = 0.5
    motion_type: Optional[str] = None

class PredictionResponse(BaseModel):
    predicted_outcome: str
    confidence: float
    class_probabilities: Dict[str, float]
    feature_impact: Optional[Dict[str, Any]] = None

class SimulationRequest(BaseModel):
    case_data: CaseData
    judge_id: Optional[str] = None

class SimulationResponse(BaseModel):
    simulation_id: str
    judge_id: Optional[str] = None
    case_type: str
    status: str

class QuestionRequest(BaseModel):
    simulation_id: str
    category: Optional[str] = None

class QuestionResponse(BaseModel):
    question: str
    category: str
    simulation_id: str
    round: int

class ResponseSubmission(BaseModel):
    simulation_id: str
    question_id: int
    response_text: str

class FeedbackResponse(BaseModel):
    feedback: Dict[str, Any]
    simulation_id: str
    question_id: int

class OpposingArgumentRequest(BaseModel):
    simulation_id: str

class OpposingArgumentResponse(BaseModel):
    argument: str
    simulation_id: str
    round: int

class SimulationSummaryRequest(BaseModel):
    simulation_id: str

class SimulationSummary(BaseModel):
    simulation_id: str
    date: str
    case_type: str
    judge_id: Optional[str] = None
    rounds_completed: int
    metrics: Dict[str, float]
    strengths: List[str]
    areas_for_improvement: List[str]
    overall_feedback: str

# Authentication functions
def get_user(db, username: str):
    """Get user from database"""
    # Mock database function
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(db, username: str, password: str):
    """Authenticate user"""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Mock database
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
    }
}

# Authentication and token endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get access token"""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

# Judge endpoints
@app.post("/judges/search", response_model=Dict[str, Any])
async def search_judges(
    query: JudgeQuery,
    current_user: User = Depends(get_current_user)
):
    """Search for judges based on criteria"""
    async with CourtListenerAPI() as api:
        results = await api.search_judges(
            name=query.name,
            court=query.court,
            position_type=query.position_type,
            limit=query.limit,
            offset=query.offset
        )
    return results

@app.get("/judges/{judge_id}", response_model=JudgeProfile)
async def get_judge_profile(
    judge_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a judge's profile with analysis"""
    # First get basic info from Court Listener
    async with CourtListenerAPI() as api:
        judge_data = await api.get_judge(judge_id)
        
        # Get opinions authored by this judge
        opinions_data = await api.search_opinions(judge_id=judge_id, limit=50)
        
    # Extract text for each opinion
    opinions = []
    for op in opinions_data.get("results", []):
        try:
            if "id" in op:
                text = await api.download_opinion_text(op["id"])
                opinions.append({
                    "text": text,
                    "author_id": judge_id,
                    "date_filed": op.get("date_filed", ""),
                    "case_type": op.get("nature_of_suit", "unknown"),
                    "outcome": op.get("disposition", "unknown"),
                    "citation_count": op.get("citation_count", 0)
                })
        except Exception as e:
            logger.error(f"Error downloading opinion text: {e}")
    
    # Analyze judge using profiler
    profile = judge_profiler.analyze_judge(judge_id, opinions)
    
    # Combine Court Listener data with analysis
    return {
        "judge_id": judge_id,
        "name": judge_data.get("name", ""),
        "position": judge_data.get("position", ""),
        "court": judge_data.get("court", {}).get("name", ""),
        "stats": profile.get("statistics", {}),
        "writing_style": profile.get("writing_style", {}),
        "topics": profile.get("topics", {})
    }

# Case prediction endpoints
@app.post("/cases/predict", response_model=PredictionResponse)
async def predict_case_outcome(
    case_data: CaseData,
    current_user: User = Depends(get_current_user)
):
    """Predict the outcome of a case"""
    # Ensure models are loaded
    if not case_predictor.load_models():
        # If loading fails, train with sample data
        # In production, you'd want more sophisticated handling
        sample_data = [
            {
                "case_type": "lease_dispute",
                "case_facts": "Plaintiff alleges breach of commercial lease agreement...",
                "jurisdiction": {"federal": 0, "state": "NY"},
                "outcome": "plaintiff_partial"
            },
            {
                "case_type": "foreclosure",
                "case_facts": "Bank seeks to foreclose on commercial property...",
                "jurisdiction": {"federal": 0, "state": "CA"},
                "outcome": "plaintiff_full"
            },
            {
                "case_type": "zoning",
                "case_facts": "Developer challenges city's denial of variance...",
                "jurisdiction": {"federal": 0, "state": "TX"},
                "outcome": "defendant_win"
            }
        ]
        case_predictor.train_case_outcome_model(sample_data)
    
    # Make prediction
    prediction = case_predictor.predict_case_outcome(case_data.dict())
    
    return prediction

@app.post("/motions/predict", response_model=PredictionResponse)
async def predict_motion_outcome(
    case_data: CaseData,
    current_user: User = Depends(get_current_user)
):
    """Predict the outcome of a motion"""
    # Ensure models are loaded
    if not case_predictor.load_models():
        # If loading fails, train with sample data
        sample_data = [
            {
                "case_type": "lease_dispute",
                "case_facts": "Plaintiff moves for summary judgment...",
                "jurisdiction": {"federal": 0, "state": "NY"},
                "motion_type": "summary_judgment",
                "outcome": "granted"
            },
            {
                "case_type": "foreclosure",
                "case_facts": "Defendant moves to dismiss for lack of standing...",
                "jurisdiction": {"federal": 0, "state": "CA"},
                "motion_type": "motion_to_dismiss",
                "outcome": "denied"
            }
        ]
        case_predictor.train_motion_outcome_model(sample_data)
    
    # Make prediction
    prediction = case_predictor.predict_motion_outcome(case_data.dict())
    
    return prediction

@app.post("/cases/analyze", response_model=Dict[str, Any])
async def analyze_case_factors(
    case_data: CaseData,
    current_user: User = Depends(get_current_user)
):
    """Analyze the impact of different factors on case outcome"""
    # Ensure models are loaded
    if not case_predictor.load_models():
        return {"error": "Models not available"}
    
    # Analyze factors
    analysis = case_predictor.analyze_factors(case_data.dict())
    
    return analysis

# Simulation endpoints
@app.post("/simulations/start", response_model=SimulationResponse)
async def start_simulation(
    simulation_request: SimulationRequest,
    current_user: User = Depends(get_current_user)
):
    """Start a new litigation simulation"""
    simulation = simulation_engine.start_simulation(
        case_data=simulation_request.case_data.dict(),
        judge_id=simulation_request.judge_id
    )
    
    return simulation

@app.post("/simulations/question", response_model=QuestionResponse)
async def generate_question(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate a judicial question in the simulation"""
    question = simulation_engine.generate_question(
        simulation_id=request.simulation_id,
        category=request.category
    )
    
    if "error" in question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=question["error"]
        )
    
    return question

@app.post("/simulations/response", response_model=FeedbackResponse)
async def submit_response(
    submission: ResponseSubmission,
    current_user: User = Depends(get_current_user)
):
    """Submit a response to a judicial question and get feedback"""
    feedback = simulation_engine.submit_response(
        simulation_id=submission.simulation_id,
        question_id=submission.question_id,
        response_text=submission.response_text
    )
    
    if "error" in feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=feedback["error"]
        )
    
    return feedback

@app.post("/simulations/opposing-argument", response_model=OpposingArgumentResponse)
async def generate_opposing_argument(
    request: OpposingArgumentRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate an argument from opposing counsel"""
    argument = simulation_engine.generate_opposing_argument(
        simulation_id=request.simulation_id
    )
    
    if "error" in argument:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=argument["error"]
        )
    
    return argument

@app.post("/simulations/summary", response_model=SimulationSummary)
async def get_simulation_summary(
    request: SimulationSummaryRequest,
    current_user: User = Depends(get_current_user)
):
    """Get a summary of the simulation with performance metrics"""
    summary = simulation_engine.get_simulation_summary(
        simulation_id=request.simulation_id
    )
    
    if "error" in summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=summary["error"]
        )
    
    return summary

@app.post("/simulations/save")
async def save_simulation(
    request: SimulationSummaryRequest,
    current_user: User = Depends(get_current_user)
):
    """Save the current simulation to disk"""
    success = simulation_engine.save_simulation(
        simulation_id=request.simulation_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to save simulation"
        )
    
    return {"status": "saved", "simulation_id": request.simulation_id}

@app.post("/simulations/load")
async def load_simulation(
    request: SimulationSummaryRequest,
    current_user: User = Depends(get_current_user)
):
    """Load a simulation from disk"""
    success = simulation_engine.load_simulation(
        simulation_id=request.simulation_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to load simulation"
        )
    
    return {"status": "loaded", "simulation_id": request.simulation_id}

# Training endpoints (for admin use)
@app.post("/admin/train/judges")
async def train_judge_models(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Train judge analysis models with latest data (admin only)"""
    # In a real implementation, check if user has admin privileges
    
    async def train_task():
        """Background task to train models"""
        async with CourtListenerAPI() as api:
            # Get sample of judges
            judges = await api.search_judges(limit=10)
            
            for judge_data in judges.get("results", []):
                judge_id = judge_data.get("id")
                if not judge_id:
                    continue
                
                # Get opinions
                opinions_data = await api.search_opinions(judge_id=judge_id, limit=20)
                
                # Extract text
                opinions = []
                for op in opinions_data.get("results", []):
                    try:
                        if "id" in op:
                            text = await api.download_opinion_text(op["id"])
                            opinions.append({
                                "text": text,
                                "author_id": judge_id,
                                "date_filed": op.get("date_filed", ""),
                                "case_type": op.get("nature_of_suit", "unknown"),
                                "outcome": op.get("disposition", "unknown"),
                                "citation_count": op.get("citation_count", 0)
                            })
                    except Exception as e:
                        logger.error(f"Error downloading opinion text: {e}")
                
                # Analyze judge
                if opinions:
                    judge_profiler.analyze_judge(judge_id, opinions)
    
    # Add task to background tasks
    background_tasks.add_task(train_task)
    
    return {"status": "training_started"}

@app.post("/admin/train/cases")
async def train_case_models(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Train case outcome prediction models with latest data (admin only)"""
    # In a real implementation, check if user has admin privileges
    
    async def train_task():
        """Background task to train models"""
        async with CourtListenerAPI() as api:
            # Get sample of commercial real estate cases
            opinions_data = await api.search_opinions(
                nature_of_suit="real property",
                limit=50
            )
            
            # Prepare training data
            training_data = []
            for op in opinions_data.get("results", []):
                try:
                    if "id" in op:
                        text = await api.download_opinion_text(op["id"])
                        
                        # Extract case type from nature of suit
                        nature = op.get("nature_of_suit", "").lower()
                        if "foreclosure" in nature:
                            case_type = "foreclosure"
                        elif "lease" in nature:
                            case_type = "lease_dispute"
                        elif "zoning" in nature or "land use" in nature:
                            case_type = "zoning"
                        else:
                            case_type = "other"
                        
                        # Extract outcome from disposition
                        disposition = op.get("disposition", "").lower()
                        if "affirmed" in disposition or "granted" in disposition:
                            outcome = "plaintiff_full"
                        elif "reversed" in disposition or "vacated" in disposition:
                            outcome = "defendant_win"
                        elif "remanded" in disposition:
                            outcome = "remanded"
                        elif "dismissed" in disposition:
                            outcome = "dismissed"
                        else:
                            outcome = "other"
                        
                        # Create training example
                        training_data.append({
                            "case_type": case_type,
                            "case_facts": text[:1000],  # Use first 1000 chars as facts
                            "jurisdiction": {
                                "federal": 1 if op.get("court", {}).get("jurisdiction") == "federal" else 0,
                                "state": op.get("court", {}).get("jurisdiction_code", "")
                            },
                            "judge": {
                                "years_experience": 10,  # Placeholder
                                "plaintiff_favor_rate": 0.5,  # Placeholder
                                "defendant_favor_rate": 0.5  # Placeholder
                            },
                            "outcome": outcome
                        })
                except Exception as e:
                    logger.error(f"Error processing opinion: {e}")
            
            # Train models
            if training_data:
                case_predictor.train_case_outcome_model(training_data)
                
                # Prepare motion data (simplified)
                motion_data = []
                for case in training_data:
                    # Create synthetic motion data
                    motion = case.copy()
                    motion["motion_type"] = "summary_judgment"
                    motion["outcome"] = "granted" if case["outcome"] in ["plaintiff_full", "plaintiff_partial"] else "denied"
                    motion_data.append(motion)
                
                case_predictor.train_motion_outcome_model(motion_data)
    
    # Add task to background tasks
    background_tasks.add_task(train_task)
    
    return {"status": "training_started"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Utility functions
def verify_password(plain_password, hashed_password):
    """Verify password against hash"""
    # In a real app, use a proper password hashing library
    return plain_password == "secret"  # Mock verification

# Global variables
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Change in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Import missing modules
import jwt
from jwt.exceptions import JWTError

# Main function to run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
