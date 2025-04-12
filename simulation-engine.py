"""
Litigation Simulation Engine

This module provides an interactive simulation environment that generates
realistic judicial questioning and opposing counsel arguments based on
historical patterns. It allows attorneys to practice their responses
and provides feedback on effectiveness.
"""

import os
import json
import random
import logging
import numpy as np
from typing import Dict, List, Any, Optional
import spacy
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, PreTrainedTokenizer, PreTrainedModel
import pickle
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimulationEngine:
    """
    Engine for generating interactive legal simulations based on
    historical patterns of judicial behavior and case precedents.
    """
    
    def __init__(self, model_dir: str = "./models"):
        """
        Initialize the SimulationEngine.
        
        Args:
            model_dir: Directory to save/load model files
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Load spaCy for text processing
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            logger.info("Downloading spaCy model...")
            spacy.cli.download("en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")
        
        # Initialize transformers model for text generation
        model_name = "gpt2"  # Can be replaced with more advanced models
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.generator_model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Simulation state
        self.current_simulation = None
        self.judge_patterns = {}
        self.opposing_counsel_patterns = {}
        self.question_templates = self._load_question_templates()
        
        logger.info("SimulationEngine initialized")
    
    def _load_question_templates(self) -> Dict[str, List[str]]:
        """
        Load question templates for different categories of judicial questions.
        
        Returns:
            Dictionary of question templates by category
        """
        # Default templates
        default_templates = {
            "factual": [
                "Can you explain the timeline of events regarding {topic}?",
                "What evidence supports your claim that {topic}?",
                "How do you reconcile the apparent contradiction in {topic}?",
                "Could you clarify the specific terms of {topic}?"
            ],
            "legal": [
                "How does your interpretation of {case} apply to these facts?",
                "What's your response to the precedent established in {case}?",
                "How do you distinguish this case from {case}?",
                "Given the ruling in {case}, why should the court rule in your favor?"
            ],
            "hypothetical": [
                "If we assume {scenario}, how would that affect your argument?",
                "Let's say {scenario}. Would your position change?",
                "Suppose {scenario}. What would be the implications?",
                "In a scenario where {scenario}, would you still maintain your current position?"
            ],
            "challenging": [
                "Your argument seems to contradict {principle}. How do you address that?",
                "The opposing counsel makes a compelling point about {topic}. Your response?",
                "Isn't it true that {counterpoint}?",
                "How do you overcome the substantial hurdle presented by {obstacle}?"
            ]
        }
        
        # Try to load custom templates if available
        template_path = os.path.join(self.model_dir, "question_templates.json")
        if os.path.exists(template_path):
            try:
                with open(template_path, "r") as f:
                    custom_templates = json.load(f)
                    # Merge with defaults, with custom taking precedence
                    templates = {**default_templates, **custom_templates}
                    logger.info(f"Loaded custom question templates from {template_path}")
                    return templates
            except Exception as e:
                logger.warning(f"Error loading question templates: {e}")
        
        return default_templates
    
    def _generate_text(
        self, 
        prompt: str, 
        max_length: int = 150, 
        temperature: float = 0.7,
        num_return_sequences: int = 1
    ) -> List[str]:
        """
        Generate text based on a prompt using the language model.
        
        Args:
            prompt: Text prompt to generate from
            max_length: Maximum length of generated text
            temperature: Higher values produce more diverse text
            num_return_sequences: Number of different sequences to generate
            
        Returns:
            List of generated text sequences
        """
        try:
            # Encode the prompt
            input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate text
            output_sequences = self.generator_model.generate(
                input_ids=input_ids,
                max_length=max_length + input_ids.shape[1],
                temperature=temperature,
                num_return_sequences=num_return_sequences,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode and cleanup the generated text
            generated_texts = []
            for generated_sequence in output_sequences:
                text = self.tokenizer.decode(
                    generated_sequence,
                    skip_special_tokens=True
                )
                # Remove the prompt from the generated text
                if text.startswith(prompt):
                    text = text[len(prompt):].strip()
                generated_texts.append(text)
                
            return generated_texts
            
        except Exception as e:
            logger.error(f"Error in text generation: {e}")
            return ["[Error generating text]"]
    
    def load_judge_patterns(self, judge_id: str) -> bool:
        """
        Load questioning patterns for a specific judge.
        
        Args:
            judge_id: Court Listener ID of the judge
            
        Returns:
            True if patterns loaded successfully, False otherwise
        """
        pattern_path = os.path.join(self.model_dir, f"judge_patterns_{judge_id}.json")
        if os.path.exists(pattern_path):
            try:
                with open(pattern_path, "r") as f:
                    self.judge_patterns[judge_id] = json.load(f)
                logger.info(f"Loaded questioning patterns for judge {judge_id}")
                return True
            except Exception as e:
                logger.error(f"Error loading judge patterns: {e}")
                return False
        else:
            logger.warning(f"No pattern file found for judge {judge_id}")
            return False
    
    def analyze_judge_questioning(
        self, 
        judge_id: str, 
        oral_arguments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze a judge's questioning patterns from oral arguments.
        
        Args:
            judge_id: Court Listener ID of the judge
            oral_arguments: List of oral argument transcripts
            
        Returns:
            Analysis of the judge's questioning patterns
        """
        logger.info(f"Analyzing questioning patterns for judge {judge_id}")
        
        # Initialize pattern statistics
        patterns = {
            "question_frequency": 0,
            "avg_questions_per_session": 0,
            "question_categories": {
                "factual": 0,
                "legal": 0,
                "hypothetical": 0,
                "challenging": 0,
                "other": 0
            },
            "common_topics": {},
            "cited_cases": [],
            "typical_sequences": [],
            "question_samples": {
                "factual": [],
                "legal": [],
                "hypothetical": [],
                "challenging": [],
                "other": []
            }
        }
        
        total_questions = 0
        
        # Process each oral argument
        for argument in oral_arguments:
            # Extract questions by this judge
            transcript = argument.get("transcript", "")
            if not transcript:
                continue
            
            # Simple heuristic to identify questions (can be improved)
            segments = transcript.split("\n")
            judge_segments = [s for s in segments if judge_id in s or "JUDGE" in s or "JUSTICE" in s]
            
            questions = []
            for segment in judge_segments:
                # Extract the actual question text
                text = segment.split(":", 1)[1].strip() if ":" in segment else segment.strip()
                
                # Check if it's a question
                if "?" in text:
                    questions.append(text)
            
            # Update statistics
            total_questions += len(questions)
            
            # Categorize questions (simplified method)
            for question in questions:
                # Parse with spaCy for better analysis
                doc = self.nlp(question)
                
                # Determine category
                category = "other"
                if any(token.text.lower() in ["what", "when", "where", "who", "how"] for token in doc):
                    category = "factual"
                elif any(token.text.lower() in ["case", "precedent", "ruling", "decision", "law", "statute"] for token in doc):
                    category = "legal"
                elif any(token.text.lower() in ["if", "assume", "hypothetical", "suppose", "scenario"] for token in doc):
                    category = "hypothetical"
                elif any(token.text.lower() in ["but", "however", "contradict", "oppose", "challenge"] for token in doc):
                    category = "challenging"
                
                # Update category count
                patterns["question_categories"][category] += 1
                
                # Add sample question if we don't have many yet
                if len(patterns["question_samples"][category]) < 5:
                    patterns["question_samples"][category].append(question)
                
                # Extract topics (using noun chunks as a simple approach)
                topics = [chunk.text.lower() for chunk in doc.noun_chunks]
                for topic in topics:
                    patterns["common_topics"][topic] = patterns["common_topics"].get(topic, 0) + 1
                
                # Extract cited cases (simplified)
                for ent in doc.ents:
                    if ent.label_ == "ORG" and "v." in ent.text:
                        patterns["cited_cases"].append(ent.text)
        
        # Calculate averages
        if oral_arguments:
            patterns["avg_questions_per_session"] = total_questions / len(oral_arguments)
        
        # Sort topics by frequency
        sorted_topics = sorted(patterns["common_topics"].items(), key=lambda x: x[1], reverse=True)
        patterns["common_topics"] = dict(sorted_topics[:20])  # Keep top 20
        
        # Sort and deduplicate cited cases
        patterns["cited_cases"] = list(set(patterns["cited_cases"]))
        
        # Save patterns
        self.judge_patterns[judge_id] = patterns
        
        # Write to file
        pattern_path = os.path.join(self.model_dir, f"judge_patterns_{judge_id}.json")
        with open(pattern_path, "w") as f:
            json.dump(patterns, f, indent=2)
        
        logger.info(f"Saved questioning patterns for judge {judge_id}")
        
        return patterns
    
    def start_simulation(
        self, 
        case_data: Dict[str, Any],
        judge_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start a new litigation simulation.
        
        Args:
            case_data: Dictionary containing case information
            judge_id: Optional ID of the judge to simulate
            
        Returns:
            Simulation session info
        """
        # Generate simulation ID
        sim_id = f"sim_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Initialize simulation state
        self.current_simulation = {
            "id": sim_id,
            "case_data": case_data,
            "judge_id": judge_id,
            "questions": [],
            "responses": [],
            "feedback": [],
            "current_round": 0,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        
        # Load judge patterns if specified
        if judge_id and judge_id not in self.judge_patterns:
            self.load_judge_patterns(judge_id)
        
        logger.info(f"Started simulation {sim_id}")
        
        return {
            "simulation_id": sim_id,
            "judge_id": judge_id,
            "case_type": case_data.get("case_type", "unknown"),
            "status": "active"
        }
    
    def generate_question(
        self, 
        simulation_id: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a judicial question based on the current simulation.
        
        Args:
            simulation_id: ID of the simulation session
            category: Optional category of question to generate
            
        Returns:
            Generated question with metadata
        """
        # Check if we have an active simulation
        if not self.current_simulation or (simulation_id and simulation_id != self.current_simulation["id"]):
            return {"error": "No active simulation or invalid simulation ID"}
        
        # Get case data and judge patterns
        case_data = self.current_simulation["case_data"]
        judge_id = self.current_simulation["judge_id"]
        judge_patterns = self.judge_patterns.get(judge_id, {})
        
        # Select question category
        if not category:
            # If no category specified, select based on judge patterns or randomly
            if judge_patterns and "question_categories" in judge_patterns:
                categories = judge_patterns["question_categories"]
                total = sum(categories.values())
                if total > 0:
                    weights = [categories[cat] / total for cat in ["factual", "legal", "hypothetical", "challenging", "other"]]
                    category = random.choices(["factual", "legal", "hypothetical", "challenging", "other"], weights=weights)[0]
                else:
                    category = random.choice(["factual", "legal", "hypothetical", "challenging"])
            else:
                category = random.choice(["factual", "legal", "hypothetical", "challenging"])
        
        # Get templates for the category
        templates = self.question_templates.get(category, self.question_templates["factual"])
        
        # Select a template
        template = random.choice(templates)
        
        # Fill in template placeholders
        if "{topic}" in template:
            # Use common topics from judge patterns or case facts
            if judge_patterns and "common_topics" in judge_patterns and judge_patterns["common_topics"]:
                topic = random.choice(list(judge_patterns["common_topics"].keys()))
            else:
                # Extract topics from case facts
                case_facts = case_data.get("case_facts", "