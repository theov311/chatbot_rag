import os
import json
import datetime
from typing import Dict, Any, Optional

class EvaluationSystem:
    def __init__(self, log_dir: str = None):
        """Initialize the evaluation system"""
        if log_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_dir = os.path.join(base_dir, "logs")
        
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"evaluation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")
    
    def log_evaluation(
        self, 
        question: str, 
        answer: str, 
        rating: int, 
        feedback: Optional[str] = None,
        source_ids: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an evaluation entry
        
        Args:
            question: The user's question
            answer: The chatbot's response
            rating: User rating (1-5)
            feedback: Optional user feedback
            source_ids: IDs of source documents used
            metadata: Additional metadata
        """
        timestamp = datetime.datetime.now().isoformat()
        
        eval_data = {
            "timestamp": timestamp,
            "question": question,
            "answer": answer,
            "rating": rating,
            "feedback": feedback,
            "source_ids": source_ids,
            "metadata": metadata or {}
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(eval_data) + '\n')
        
        return eval_data