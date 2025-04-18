"""
Litigation Simulation Engine

This module provides the core simulation functionality for litigation cases,
allowing users to model different scenarios and outcomes based on case parameters.
"""

import logging
import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from case_prediction import CaseOutcomePredictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simulation_engine")

class SimulationEngine:
    """
    Core engine for simulating litigation cases and their possible outcomes.
    """
    
    def __init__(self, predictor: Optional[CaseOutcomePredictor] = None):
        """
        Initialize the simulation engine.
        
        Args:
            predictor: CaseOutcomePredictor instance for outcome predictions
        """
        self.predictor = predictor or CaseOutcomePredictor()
        self.simulations = {}
        self.load_model_if_needed()
        logger.info("Simulation engine initialized")
        
    def load_model_if_needed(self):
        """Ensure the prediction models are loaded"""
        if not self.predictor.case_model or not self.predictor.motion_model:
            self.predictor.load_models()
        
    def create_simulation(self, case_data: Dict[str, Any]) -> str:
        """
        Create a new simulation based on input case data.
        
        Args:
            case_data: Dictionary containing case parameters
            
        Returns:
            simulation_id: Unique identifier for the simulation
        """
        simulation_id = str(uuid.uuid4())
        
        # Create a timeline of expected events
        timeline = self._generate_timeline(case_data)
        
        # Generate initial predictions
        predictions = {
            "case_outcome": self.predictor.predict_case_outcome(case_data),
            "motion_outcomes": {}
        }
        
        self.simulations[simulation_id] = {
            "id": simulation_id,
            "created_at": datetime.now().isoformat(),
            "case_data": case_data,
            "timeline": timeline,
            "predictions": predictions,
            "scenarios": [],
            "status": "active"
        }
        
        logger.info(f"Created new simulation with ID: {simulation_id}")
        return simulation_id
    
    def _generate_timeline(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a timeline of expected case events.
        
        Args:
            case_data: Dictionary containing case parameters
            
        Returns:
            timeline: List of expected events in chronological order
        """
        timeline = []
        start_date = datetime.now()
        
        # Filing
        timeline.append({
            "event_type": "filing",
            "description": "Case filed",
            "date": start_date.isoformat(),
            "status": "completed"
        })
        
        # Initial hearing
        initial_hearing = start_date + timedelta(days=random.randint(30, 45))
        timeline.append({
            "event_type": "hearing",
            "description": "Initial hearing",
            "date": initial_hearing.isoformat(),
            "status": "scheduled"
        })
        
        # Discovery phase
        discovery_start = initial_hearing + timedelta(days=random.randint(15, 30))
        discovery_end = discovery_start + timedelta(days=random.randint(90, 180))
        timeline.append({
            "event_type": "discovery",
            "description": "Discovery phase",
            "date_start": discovery_start.isoformat(),
            "date_end": discovery_end.isoformat(),
            "status": "scheduled"
        })
        
        # Add some motions based on case type
        if case_data.get("case_type") in ["civil", "commercial"]:
            # Summary judgment motion
            motion_date = discovery_end + timedelta(days=random.randint(30, 60))
            timeline.append({
                "event_type": "motion",
                "motion_type": "summary_judgment",
                "description": "Motion for summary judgment",
                "date": motion_date.isoformat(),
                "status": "scheduled"
            })
        
        # Trial date
        trial_date = discovery_end + timedelta(days=random.randint(60, 120))
        timeline.append({
            "event_type": "trial",
            "description": "Trial begins",
            "date": trial_date.isoformat(),
            "expected_duration": f"{random.randint(1, 10)} days",
            "status": "scheduled"
        })
        
        # Decision
        decision_date = trial_date + timedelta(days=random.randint(15, 45))
        timeline.append({
            "event_type": "decision",
            "description": "Final decision",
            "date": decision_date.isoformat(),
            "status": "scheduled"
        })
        
        return timeline
    
    def get_simulation(self, simulation_id: str) -> Dict[str, Any]:
        """
        Retrieve a simulation by ID.
        
        Args:
            simulation_id: Unique identifier for the simulation
            
        Returns:
            simulation: Dictionary containing simulation data
        """
        if simulation_id not in self.simulations:
            raise ValueError(f"Simulation with ID {simulation_id} not found")
        
        return self.simulations[simulation_id]
    
    def create_scenario(self, simulation_id: str, scenario_data: Dict[str, Any]) -> str:
        """
        Create a what-if scenario for an existing simulation.
        
        Args:
            simulation_id: ID of the parent simulation
            scenario_data: Dictionary containing modified case parameters
            
        Returns:
            scenario_id: Unique identifier for the scenario
        """
        if simulation_id not in self.simulations:
            raise ValueError(f"Simulation with ID {simulation_id} not found")
        
        # Create a new scenario with modified parameters
        base_simulation = self.simulations[simulation_id]
        scenario_id = str(uuid.uuid4())
        
        # Merge original case data with scenario modifications
        modified_case_data = {**base_simulation["case_data"], **scenario_data.get("case_data", {})}
        
        # Generate new predictions based on modified data
        predictions = {
            "case_outcome": self.predictor.predict_case_outcome(modified_case_data),
            "motion_outcomes": {}
        }
        
        # Generate modified timeline if needed
        timeline = self._generate_timeline(modified_case_data)
        
        scenario = {
            "id": scenario_id,
            "parent_simulation_id": simulation_id,
            "created_at": datetime.now().isoformat(),
            "name": scenario_data.get("name", f"Scenario {len(base_simulation['scenarios']) + 1}"),
            "description": scenario_data.get("description", ""),
            "case_data": modified_case_data,
            "timeline": timeline,
            "predictions": predictions,
            "status": "active"
        }
        
        self.simulations[simulation_id]["scenarios"].append(scenario)
        logger.info(f"Created new scenario {scenario_id} for simulation {simulation_id}")
        
        return scenario_id
    
    def run_simulation(self, simulation_id: str) -> Dict[str, Any]:
        """
        Run a complete simulation to calculate outcomes and generate reports.
        
        Args:
            simulation_id: ID of the simulation to run
            
        Returns:
            results: Dictionary containing simulation results
        """
        if simulation_id not in self.simulations:
            raise ValueError(f"Simulation with ID {simulation_id} not found")
        
        simulation = self.simulations[simulation_id]
        case_data = simulation["case_data"]
        
        # Get case outcome prediction
        case_prediction = self.predictor.predict_case_outcome(case_data)
        
        # Calculate financial impact
        financial_impact = self._calculate_financial_impact(
            case_data,
            case_prediction
        )
        
        # Calculate timeline probabilities
        timeline_probabilities = self._calculate_timeline_probabilities(
            simulation["timeline"],
            case_prediction
        )
        
        # Process any scenarios
        scenario_results = []
        for scenario in simulation["scenarios"]:
            scenario_prediction = self.predictor.predict_case_outcome(scenario["case_data"])
            scenario_financial = self._calculate_financial_impact(
                scenario["case_data"],
                scenario_prediction
            )
            
            scenario_results.append({
                "id": scenario["id"],
                "name": scenario["name"],
                "prediction": scenario_prediction,
                "financial_impact": scenario_financial,
                "comparison": self._compare_scenarios(
                    financial_impact,
                    scenario_financial,
                    case_prediction,
                    scenario_prediction
                )
            })
        
        # Generate result summary
        results = {
            "simulation_id": simulation_id,
            "run_date": datetime.now().isoformat(),
            "case_prediction": case_prediction,
            "financial_impact": financial_impact,
            "timeline_probabilities": timeline_probabilities,
            "scenario_results": scenario_results,
            "recommended_actions": self._generate_recommendations(
                case_data,
                case_prediction,
                financial_impact,
                scenario_results
            )
        }
        
        # Update simulation with results
        self.simulations[simulation_id]["results"] = results
        self.simulations[simulation_id]["status"] = "completed"
        
        logger.info(f"Completed simulation run for {simulation_id}")
        return results
    
    def _calculate_financial_impact(
        self, 
        case_data: Dict[str, Any], 
        prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate the financial impact of a case based on its outcome prediction.
        
        Args:
            case_data: Dictionary containing case parameters
            prediction: Dictionary containing outcome predictions
            
        Returns:
            financial_impact: Dictionary with financial impact data
        """
        # Extract relevant data
        claim_amount = float(case_data.get("claim_amount", 0))
        case_type = case_data.get("case_type", "")
        jurisdiction = case_data.get("jurisdiction", "")
        predicted_outcome = prediction.get("outcome", "")
        confidence = prediction.get("confidence", 0.5)
        
        # Calculate expected legal costs
        # This is a simplified estimation
        if case_type == "commercial":
            base_legal_costs = claim_amount * 0.15
        elif case_type == "civil":
            base_legal_costs = claim_amount * 0.12
        else:
            base_legal_costs = claim_amount * 0.10
            
        # Adjust based on jurisdiction
        jurisdiction_multiplier = {
            "federal": 1.2,
            "state": 1.0,
            "local": 0.8
        }.get(jurisdiction, 1.0)
        
        legal_costs = base_legal_costs * jurisdiction_multiplier
        
        # Calculate expected settlement costs
        if predicted_outcome == "settlement":
            settlement_amount = claim_amount * 0.6 * (1 + (confidence - 0.5))
        elif predicted_outcome == "plaintiff_win":
            settlement_amount = claim_amount * 0.8 * (1 + (confidence - 0.5))
        elif predicted_outcome == "defendant_win":
            settlement_amount = claim_amount * 0.3 * (1 - (confidence - 0.5))
        else:
            settlement_amount = claim_amount * 0.5
            
        # Calculate total costs and expected value
        total_cost = legal_costs
        if predicted_outcome in ["settlement", "plaintiff_win"]:
            total_cost += settlement_amount
            
        # Risk-adjusted expected value
        if predicted_outcome == "plaintiff_win":
            win_probability = confidence
            loss_probability = 1 - confidence
            expected_value = (win_probability * claim_amount) - (loss_probability * legal_costs)
        elif predicted_outcome == "defendant_win":
            win_probability = confidence
            loss_probability = 1 - confidence
            expected_value = -(loss_probability * (claim_amount + legal_costs)) - (win_probability * legal_costs)
        else:
            expected_value = (claim_amount * 0.5) - legal_costs
            
        return {
            "legal_costs": round(legal_costs, 2),
            "settlement_amount": round(settlement_amount, 2),
            "total_cost": round(total_cost, 2),
            "expected_value": round(expected_value, 2),
            "best_case": round(claim_amount - legal_costs, 2),
            "worst_case": round(-(claim_amount + legal_costs), 2),
            "risk_profile": "high" if abs(expected_value) > claim_amount * 0.5 else "medium"
        }
    
    def _calculate_timeline_probabilities(
        self, 
        timeline: List[Dict[str, Any]], 
        prediction: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Calculate probabilities of different timeline outcomes.
        
        Args:
            timeline: List of timeline events
            prediction: Dictionary containing outcome predictions
            
        Returns:
            timeline_with_probabilities: Timeline with added probabilities
        """
        outcome = prediction.get("outcome", "")
        confidence = prediction.get("confidence", 0.5)
        
        # Clone the timeline and add probabilities
        timeline_with_probs = []
        
        for event in timeline:
            event_with_prob = event.copy()
            
            # Add probabilities based on event type
            if event["event_type"] == "motion":
                if event["motion_type"] == "summary_judgment":
                    if outcome == "defendant_win":
                        prob = 0.5 + (confidence * 0.3)
                    else:
                        prob = 0.3 - (confidence * 0.2)
                    event_with_prob["success_probability"] = round(max(0.1, min(0.9, prob)), 2)
                    
            elif event["event_type"] == "trial":
                # Add trial duration probabilities
                if outcome == "settlement":
                    event_with_prob["completion_probability"] = 0.3
                else:
                    event_with_prob["completion_probability"] = 0.9
                    
            elif event["event_type"] == "decision":
                event_with_prob["outcomes"] = {
                    "plaintiff_win": round(prediction.get("probabilities", {}).get("plaintiff_win", 0.33), 2),
                    "defendant_win": round(prediction.get("probabilities", {}).get("defendant_win", 0.33), 2),
                    "settlement": round(prediction.get("probabilities", {}).get("settlement", 0.33), 2)
                }
                
            timeline_with_probs.append(event_with_prob)
            
        return timeline_with_probs
    
    def _compare_scenarios(
        self,
        base_financial: Dict[str, Any],
        scenario_financial: Dict[str, Any],
        base_prediction: Dict[str, Any],
        scenario_prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare base simulation with a scenario.
        
        Args:
            base_financial: Financial impact of base simulation
            scenario_financial: Financial impact of scenario
            base_prediction: Prediction for base simulation
            scenario_prediction: Prediction for scenario
            
        Returns:
            comparison: Dictionary containing comparison data
        """
        # Calculate differences
        financial_diff = {
            "legal_costs": scenario_financial["legal_costs"] - base_financial["legal_costs"],
            "total_cost": scenario_financial["total_cost"] - base_financial["total_cost"],
            "expected_value": scenario_financial["expected_value"] - base_financial["expected_value"]
        }
        
        # Calculate outcome probability shifts
        outcome_shifts = {}
        for outcome in ["plaintiff_win", "defendant_win", "settlement"]:
            base_prob = base_prediction.get("probabilities", {}).get(outcome, 0)
            scenario_prob = scenario_prediction.get("probabilities", {}).get(outcome, 0)
            outcome_shifts[outcome] = round(scenario_prob - base_prob, 2)
            
        # Determine if scenario is better or worse
        is_improvement = scenario_financial["expected_value"] > base_financial["expected_value"]
        
        return {
            "financial_differences": financial_diff,
            "outcome_probability_shifts": outcome_shifts,
            "is_improvement": is_improvement,
            "improvement_magnitude": abs(financial_diff["expected_value"]) / abs(base_financial["expected_value"]) 
                if base_financial["expected_value"] != 0 else 0
        }
    
    def _generate_recommendations(
        self,
        case_data: Dict[str, Any],
        prediction: Dict[str, Any],
        financial_impact: Dict[str, Any],
        scenario_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate strategic recommendations based on simulation results.
        
        Args:
            case_data: Dictionary containing case parameters
            prediction: Dictionary containing outcome predictions
            financial_impact: Dictionary with financial impact data
            scenario_results: List of scenario results
            
        Returns:
            recommendations: List of recommended actions
        """
        recommendations = []
        
        # Base recommendation on outcome
        outcome = prediction.get("outcome", "")
        confidence = prediction.get("confidence", 0.5)
        
        # Extract the best scenario if available
        best_scenario = None
        if scenario_results:
            best_scenario = max(
                scenario_results,
                key=lambda x: x["comparison"]["improvement_magnitude"] if x["comparison"]["is_improvement"] else 0
            )
        
        # Generate recommendations based on predicted outcome
        if outcome == "plaintiff_win" and confidence > 0.6:
            recommendations.append({
                "action": "proceed_to_trial",
                "description": "Proceed to trial with current strategy",
                "rationale": "High probability of favorable outcome",
                "expected_impact": "Maximize claim recovery"
            })
        elif outcome == "defendant_win" and confidence > 0.6:
            recommendations.append({
                "action": "settle",
                "description": "Consider settlement options",
                "rationale": "High probability of unfavorable outcome",
                "expected_impact": "Minimize losses and legal costs"
            })
        elif outcome == "settlement":
            recommendations.append({
                "action": "initiate_settlement",
                "description": "Initiate settlement discussions",
                "rationale": "Most probable outcome is settlement",
                "expected_impact": "Reduce time to resolution and legal costs"
            })
        
        # Add scenario-based recommendation if available
        if best_scenario and best_scenario["comparison"]["is_improvement"] and best_scenario["comparison"]["improvement_magnitude"] > 0.1:
            recommendations.append({
                "action": "implement_scenario",
                "scenario_id": best_scenario["id"],
                "description": f"Implement '{best_scenario['name']}' scenario",
                "rationale": "Simulation shows significant improvement in expected outcome",
                "expected_impact": f"Improve expected value by ${abs(best_scenario['comparison']['financial_differences']['expected_value']):.2f}"
            })
        
        # Add cost-saving recommendation if legal costs are high
        if financial_impact["legal_costs"] > financial_impact["expected_value"] * 0.4:
            recommendations.append({
                "action": "optimize_legal_strategy",
                "description": "Optimize legal resources allocation",
                "rationale": "Legal costs represent a high proportion of potential recovery",
                "expected_impact": "Reduce costs without impacting outcome probability"
            })
        
        return recommendations
    
    def export_simulation(self, simulation_id: str, format: str = "json") -> str:
        """
        Export simulation data in the specified format.
        
        Args:
            simulation_id: ID of the simulation to export
            format: Output format (currently only 'json' is supported)
            
        Returns:
            exported_data: String containing the exported data
        """
        if simulation_id not in self.simulations:
            raise ValueError(f"Simulation with ID {simulation_id} not found")
        
        simulation = self.simulations[simulation_id]
        
        if format.lower() == "json":
            return json.dumps(simulation, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}") 