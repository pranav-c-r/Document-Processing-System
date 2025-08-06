from typing import Dict, Any, List
from models.schemas import ScoreDetails

class ScoringService:
    def __init__(self):
        # Define scoring weights
        self.document_weights = {
            "known": 0.5,
            "unknown": 2.0
        }
        
        # Define question weights (can be customized)
        self.default_question_weight = 2.0
    
    def calculate_score(self, document_type: str, question_weight: float = None) -> float:
        """Calculate score based on document type and question weight"""
        if question_weight is None:
            question_weight = self.default_question_weight
        
        document_weight = self.document_weights.get(document_type, 2.0)
        return question_weight * document_weight
    
    def calculate_batch_score(self, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate total score for a batch of answers"""
        total_score = 0.0
        correct_answers = 0
        total_questions = len(answers)
        
        for answer in answers:
            score_details = answer.get("score_details", {})
            if score_details:
                score = score_details.get("score", 0.0)
                total_score += score
                if score > 0:
                    correct_answers += 1
        
        return {
            "total_score": total_score,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "accuracy": correct_answers / total_questions if total_questions > 0 else 0.0,
            "average_score": total_score / total_questions if total_questions > 0 else 0.0
        }
    
    def evaluate_answer_quality(self, answer: str, confidence: float, matched_clauses: List[str]) -> Dict[str, Any]:
        """Evaluate the quality of an answer"""
        quality_score = 0.0
        quality_factors = []
        
        # Factor 1: Confidence
        if confidence > 0.8:
            quality_score += 0.3
            quality_factors.append("High confidence")
        elif confidence > 0.6:
            quality_score += 0.2
            quality_factors.append("Medium confidence")
        else:
            quality_score += 0.1
            quality_factors.append("Low confidence")
        
        # Factor 2: Answer length (indicates detail)
        if len(answer) > 100:
            quality_score += 0.2
            quality_factors.append("Detailed answer")
        elif len(answer) > 50:
            quality_score += 0.1
            quality_factors.append("Moderate detail")
        
        # Factor 3: Number of matched clauses
        if len(matched_clauses) > 2:
            quality_score += 0.3
            quality_factors.append("Multiple references")
        elif len(matched_clauses) > 0:
            quality_score += 0.2
            quality_factors.append("Some references")
        else:
            quality_score += 0.1
            quality_factors.append("No specific references")
        
        # Factor 4: Answer specificity
        if "not found" in answer.lower() or "information not available" in answer.lower():
            quality_score += 0.2
            quality_factors.append("Honest about limitations")
        
        return {
            "quality_score": min(quality_score, 1.0),
            "quality_factors": quality_factors,
            "confidence": confidence,
            "clause_count": len(matched_clauses)
        }
    
    def get_document_weight(self, document_type: str) -> float:
        """Get the weight for a specific document type"""
        return self.document_weights.get(document_type, 2.0)
    
    def get_question_weight(self, question: str) -> float:
        """Determine question weight based on complexity or type"""
        # This can be customized based on question analysis
        question_lower = question.lower()
        
        # Complex questions get higher weight
        if any(word in question_lower for word in ["compare", "analyze", "explain", "describe", "what are the"]):
            return 2.0
        elif any(word in question_lower for word in ["does", "is", "are", "can", "will"]):
            return 1.5
        else:
            return 1.0 