"""
Test script for the Judge Analysis module.

This script tests the functionality of the judge_analysis.py module
using sample judicial opinions.
"""

import os
import json
import logging
from typing import Dict, List, Any
from judge_analysis import JudgeProfiler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample judicial opinions for testing
SAMPLE_OPINIONS = [
    {
        "text": """
        The court has considered the motion for summary judgment filed by the defendant.
        After reviewing the evidence, it is clear that there are no material facts in dispute
        that would require a trial. The plaintiff has failed to establish a prima facie case 
        for negligence under the applicable law. The evidence clearly shows that the defendant
        exercised reasonable care under the circumstances. Therefore, the motion for summary
        judgment is GRANTED and the case is DISMISSED with prejudice.
        """,
        "outcome": "defendant_win",
        "case_type": "civil",
        "date_filed": "2024-01-15"
    },
    {
        "text": """
        This matter comes before the court on plaintiff's motion for a preliminary injunction.
        The plaintiff has demonstrated a substantial likelihood of success on the merits of their
        copyright infringement claim. The evidence presented indicates that defendant's product
        contains elements that are substantially similar to plaintiff's copyrighted work.
        Moreover, plaintiff has shown that they will suffer irreparable harm without injunctive relief.
        The balance of equities tips in favor of the plaintiff, and an injunction is in the public interest.
        Therefore, plaintiff's motion for preliminary injunction is GRANTED.
        """,
        "outcome": "plaintiff_win",
        "case_type": "copyright",
        "date_filed": "2024-02-10"
    },
    {
        "text": """
        After careful consideration of the briefs and oral arguments, the court finds that
        the district court did not err in its application of the relevant legal standards.
        The appellant has failed to demonstrate that the district court's factual findings
        were clearly erroneous. The evidence in the record adequately supports the district
        court's conclusions. For the foregoing reasons, the judgment of the district court
        is hereby AFFIRMED.
        """,
        "outcome": "affirmed",
        "case_type": "appellate",
        "date_filed": "2024-03-05"
    },
    {
        "text": """
        The defendant's motion to suppress evidence obtained during the search of his residence
        is before the court. After reviewing the affidavit supporting the search warrant, the court
        finds that it failed to establish probable cause. The affidavit contained conclusory statements
        without specific factual support, and the good faith exception to the exclusionary rule does not
        apply in this instance. Accordingly, the defendant's motion to suppress is GRANTED.
        """,
        "outcome": "granted",
        "case_type": "criminal",
        "date_filed": "2024-01-30"
    },
    {
        "text": """
        This class action settlement comes before the court for final approval. The court has
        reviewed the terms of the proposed settlement and finds them to be fair, reasonable, and
        adequate under Rule 23(e). The settlement provides substantial monetary relief to class
        members, and the requested attorneys' fees are reasonable in light of the results obtained.
        The objections raised do not warrant rejection of the settlement. Therefore, the motion for
        final approval of the class action settlement is GRANTED.
        """,
        "outcome": "granted",
        "case_type": "class_action",
        "date_filed": "2024-02-25"
    }
]

def test_judge_analysis():
    """Test the judge analysis functionality."""
    # Create output directory if it doesn't exist
    os.makedirs("./test_output", exist_ok=True)
    
    try:
        # Initialize judge profiler
        profiler = JudgeProfiler(model_dir="./models")
        
        # Test with sample judge
        judge_id = "test_judge_1"
        
        logger.info(f"Testing judge analysis for {judge_id} with {len(SAMPLE_OPINIONS)} opinions")
        
        # Analyze judge
        profile = profiler.analyze_judge(judge_id, SAMPLE_OPINIONS)
        
        # Print some key results
        logger.info(f"Judge ID: {profile['judge_id']}")
        logger.info(f"Statistics: {json.dumps(profile['statistics'], indent=2)}")
        logger.info(f"Writing Style Summary:")
        if 'readability' in profile['writing_style']:
            logger.info(f"  - Readability: {profile['writing_style']['readability'].get('interpretation', 'N/A')}")
        if 'formality' in profile['writing_style']:
            logger.info(f"  - Formality: {profile['writing_style']['formality'].get('level', 'N/A')}")
        
        logger.info(f"Ruling Patterns Summary:")
        overall = profile['ruling_patterns'].get('overall', {})
        logger.info(f"  - Plaintiff favorable rate: {overall.get('plaintiff_favorable_rate', 'N/A')}")
        logger.info(f"  - Defendant favorable rate: {overall.get('defendant_favorable_rate', 'N/A')}")
        
        # Save the profile to a JSON file
        output_file = f"./test_output/{judge_id}_profile.json"
        with open(output_file, 'w') as f:
            json.dump(profile, f, indent=2)
        
        logger.info(f"Profile saved to {output_file}")
        
        return profile
    except Exception as e:
        logger.error(f"Error testing judge analysis: {str(e)}")
        logger.error("Make sure scikit-learn and spacy with 'en_core_web_sm' model are installed")
        raise

def test_with_longer_opinions():
    """
    Test with longer, more complex opinions.
    
    In a real implementation, this would use actual judicial opinions
    from a database or API.
    """
    try:
        # This is a placeholder for testing with longer opinions
        logger.info("Testing with longer opinions is not implemented yet")
        logger.info("In a real implementation, this would use actual opinions from Court Listener API")
    except Exception as e:
        logger.error(f"Error testing with longer opinions: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("Starting judge analysis tests")
    
    try:
        # Run the basic test
        test_judge_analysis()
        
        # Test with longer opinions (placeholder)
        test_with_longer_opinions()
        
        logger.info("Judge analysis tests completed")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        logger.error("Please ensure all dependencies are installed: scikit-learn, pandas, spacy, and en_core_web_sm") 