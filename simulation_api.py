from fastapi import APIRouter
from typing import Optional, Dict, Any
from main import simulation_engine

router = APIRouter(prefix="/api/simulation", tags=["simulation"])

@router.post("/start")
async def start_simulation(case_data: Dict[str, Any], judge_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Start a new simulation session.
    """
    return simulation_engine.start_simulation(case_data, judge_id)

@router.get("/question")
async def generate_question(simulation_id: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a judicial question for the active simulation.
    """
    return simulation_engine.generate_question(simulation_id, category)
