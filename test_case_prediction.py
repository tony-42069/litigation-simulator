"""
Test script for the Case Prediction module.

This script tests the functionality of the case_prediction.py module
using sample case data.
"""

import os
import json
import logging
from typing import Dict, List, Any
from case_prediction import CaseOutcomePredictor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample case data for testing
SAMPLE_CASES = [
    {
        "case_type": "contract_dispute",
        "facts": """
        Plaintiff entered into a contract with Defendant for the delivery of 500 units of computer hardware
        by June 1, 2024. Defendant failed to deliver the goods by the specified date, causing Plaintiff to
        lose a major client. Plaintiff claims damages for breach of contract and consequential damages for
        lost business opportunities. Defendant argues that the delay was caused by supply chain disruptions
        that were beyond their control and were not foreseeable at the time of contract formation.
        """,
        "jurisdiction": {
            "federal": 0,
            "state": "California",
            "district": None,
            "circuit": None
        },
        "judge": {
            "id": "judge_1",
            "name": "Judge Smith",
            "experience_years": 15,
            "court": "California Superior Court"
        },
        "precedent_strength": 0.7,
        "claim_amount": 250000
    },
    {
        "case_type": "foreclosure",
        "facts": """
        Defendant homeowner has failed to make mortgage payments for 8 consecutive months. Plaintiff lender
        has filed for foreclosure after sending multiple notices to the Defendant. Defendant claims that they
        attempted to apply for loan modification but were wrongfully denied by the lender. Defendant also
        argues that the foreclosure process contained procedural errors that should invalidate the action.
        """,
        "jurisdiction": {
            "federal": 0,
            "state": "Florida",
            "district": None,
            "circuit": None
        },
        "judge": {
            "id": "judge_2",
            "name": "Judge Martinez",
            "experience_years": 8,
            "court": "Florida Circuit Court"
        },
        "precedent_strength": 0.8,
        "claim_amount": 450000
    },
    {
        "case_type": "employment_discrimination",
        "facts": """
        Plaintiff alleges they were terminated from their position due to age discrimination. They had worked
        for the Defendant company for 22 years and were replaced by a substantially younger employee with less
        experience shortly after a new manager made comments about "bringing in fresh blood." Defendant claims
        the termination was part of a company-wide restructuring that affected employees of various ages, and
        that the Plaintiff's performance had been declining for several years.
        """,
        "jurisdiction": {
            "federal": 1,
            "state": None,
            "district": "Northern District of Illinois",
            "circuit": "Seventh Circuit"
        },
        "judge": {
            "id": "judge_3",
            "name": "Judge Williams",
            "experience_years": 12,
            "court": "U.S. District Court"
        },
        "precedent_strength": 0.6,
        "claim_amount": 850000
    }
]

# Sample motion data for testing
SAMPLE_MOTIONS = [
    {
        "case_type": "contract_dispute",
        "facts": SAMPLE_CASES[0]["facts"],
        "motion_type": "summary_judgment",
        "jurisdiction": SAMPLE_CASES[0]["jurisdiction"],
        "judge": SAMPLE_CASES[0]["judge"],
        "precedent_strength": 0.7
    },
    {
        "case_type": "foreclosure",
        "facts": SAMPLE_CASES[1]["facts"],
        "motion_type": "dismiss",
        "jurisdiction": SAMPLE_CASES[1]["jurisdiction"],
        "judge": SAMPLE_CASES[1]["judge"],
        "precedent_strength": 0.8
    },
    {
        "case_type": "employment_discrimination",
        "facts": SAMPLE_CASES[2]["facts"],
        "motion_type": "compel_discovery",
        "jurisdiction": SAMPLE_CASES[2]["jurisdiction"],
        "judge": SAMPLE_CASES[2]["judge"],
        "precedent_strength": 0.6
    }
]

def test_case_prediction():
    """Test the case prediction functionality."""
    # Create output directory if it doesn't exist
    os.makedirs("./test_output", exist_ok=True)
    
    # Initialize case predictor
    predictor = CaseOutcomePredictor(model_dir="./models")
    
    logger.info(f"Testing case prediction with {len(SAMPLE_CASES)} cases")
    
    # Test each case
    for i, case_data in enumerate(SAMPLE_CASES):
        case_type = case_data["case_type"]
        logger.info(f"Testing prediction for case {i+1}: {case_type}")
        
        try:
            # Predict case outcome
            prediction = predictor.predict_case_outcome(case_data)
            
            # Print key results
            logger.info(f"Case type: {case_type}")
            logger.info(f"Predicted outcome: {prediction['outcome']}")
            logger.info(f"Probability: {prediction['probability']:.2f}")
            logger.info(f"Confidence: {prediction['confidence']}")
            
            if "feature_impact" in prediction:
                logger.info("Top features:")
                top_features = sorted(prediction["feature_impact"].items(), key=lambda x: abs(x[1]), reverse=True)[:3]
                for feature, impact in top_features:
                    logger.info(f"  - {feature}: {impact:.3f}")
            
            # Save the prediction to a JSON file
            output_file = f"./test_output/case_{i+1}_prediction.json"
            with open(output_file, 'w') as f:
                json.dump(prediction, f, indent=2)
            
            logger.info(f"Prediction saved to {output_file}")
        except Exception as e:
            logger.error(f"Error predicting case {i+1}: {str(e)}")
        
        logger.info("-----")
    
    return True

def test_motion_prediction():
    """Test the motion prediction functionality."""
    # Create output directory if it doesn't exist
    os.makedirs("./test_output", exist_ok=True)
    
    # Initialize case predictor
    predictor = CaseOutcomePredictor(model_dir="./models")
    
    logger.info(f"Testing motion prediction with {len(SAMPLE_MOTIONS)} motions")
    
    # Test each motion
    for i, motion_data in enumerate(SAMPLE_MOTIONS):
        motion_type = motion_data["motion_type"]
        logger.info(f"Testing prediction for motion {i+1}: {motion_type}")
        
        try:
            # Predict motion outcome
            prediction = predictor.predict_motion_outcome(motion_data)
            
            # Print key results
            logger.info(f"Motion type: {motion_type}")
            logger.info(f"Predicted outcome: {prediction['outcome']}")
            logger.info(f"Probability: {prediction['probability']:.2f}")
            logger.info(f"Confidence: {prediction['confidence']}")
            
            if "feature_impact" in prediction:
                logger.info("Top features:")
                top_features = sorted(prediction["feature_impact"].items(), key=lambda x: abs(x[1]), reverse=True)[:3]
                for feature, impact in top_features:
                    logger.info(f"  - {feature}: {impact:.3f}")
            
            # Save the prediction to a JSON file
            output_file = f"./test_output/motion_{i+1}_prediction.json"
            with open(output_file, 'w') as f:
                json.dump(prediction, f, indent=2)
            
            logger.info(f"Prediction saved to {output_file}")
        except Exception as e:
            logger.error(f"Error predicting motion {i+1}: {str(e)}")
        
        logger.info("-----")
    
    return True

def test_factor_analysis():
    """Test the factor analysis functionality."""
    # Create output directory if it doesn't exist
    os.makedirs("./test_output", exist_ok=True)
    
    # Initialize case predictor
    predictor = CaseOutcomePredictor(model_dir="./models")
    
    # Select a case for factor analysis
    case_data = SAMPLE_CASES[0]
    case_type = case_data["case_type"]
    
    logger.info(f"Testing factor analysis for case type: {case_type}")
    
    try:
        # Analyze factors
        analysis = predictor.analyze_factors(case_data)
        
        # Print key results
        logger.info(f"Base prediction: {analysis['base_prediction']['outcome']}")
        logger.info(f"Probability: {analysis['base_prediction']['probability']:.2f}")
        
        logger.info("Important factors:")
        top_factors = sorted(analysis["factors"].items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        for factor, impact in top_factors:
            logger.info(f"  - {factor}: {impact:.3f}")
        
        logger.info("What-if scenarios:")
        for category, scenarios in analysis["what_if"].items():
            logger.info(f"  {category.capitalize()} scenarios:")
            for value, result in scenarios.items():
                logger.info(f"    - {value}: {result['predicted_outcome']} (confidence: {result['confidence']})")
        
        # Save the analysis to a JSON file
        output_file = f"./test_output/factor_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Factor analysis saved to {output_file}")
    except Exception as e:
        logger.error(f"Error during factor analysis: {str(e)}")
    
    return True

if __name__ == "__main__":
    logger.info("Starting case prediction tests")
    
    # Run tests
    test_case_prediction()
    test_motion_prediction()
    test_factor_analysis()
    
    logger.info("Case prediction tests completed") 