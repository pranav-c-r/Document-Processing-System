import os
import json
import google.generativeai as genai
from typing import List, Dict, Any
from models.schemas import ScoreDetails

class LLMService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # Check if we have a valid API key
        if api_key and api_key != "your_google_api_key_here":
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.api_available = True
                print("✅ Gemini API initialized successfully")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize Gemini API: {e}")
                self.api_available = False
                self.model = None
        else:
            print("⚠️ Warning: No valid Google API key found.")
            self.api_available = False
            self.model = None
    
    def create_prompt(self, question: str, context_chunks: List[str], document_type: str) -> str:
        """Create a structured prompt for the LLM"""
        
        # Determine weights based on document type
        if document_type == "Policy Wordings":
            document_weight = 0.5
            instruction = "Focus on policy terms, coverage details, exclusions, and conditions."
        elif document_type == "Legal Documents":
            document_weight = 0.5
            instruction = "Focus on legal clauses, obligations, rights, and legal implications."
        elif document_type == "Financial Documents":
            document_weight = 0.5
            instruction = "Focus on financial data, revenue, expenses, and financial metrics."
        elif document_type == "Technical Documents":
            document_weight = 0.5
            instruction = "Focus on technical specifications, requirements, and implementation details."
        elif document_type == "Medical Documents":
            document_weight = 0.5
            instruction = "Focus on medical information, diagnoses, treatments, and patient care."
        else:
            document_weight = 2.0  # Unknown documents get higher weight
            instruction = "Analyze the general content and provide comprehensive answers."
        
        question_weight = 2.0  # Default question weight
        
        prompt = f"""
You are an intelligent document analysis assistant specializing in {document_type} documents. Your task is to answer questions based on the provided document context and return a structured JSON response.

CONTEXT FROM DOCUMENT:
{chr(10).join([f"Chunk {i+1}: {chunk}" for i, chunk in enumerate(context_chunks)])}

QUESTION: {question}

DOCUMENT TYPE: {document_type}
DOCUMENT WEIGHT: {document_weight}
QUESTION WEIGHT: {question_weight}

SPECIALIZED INSTRUCTIONS FOR {document_type}:
{instruction}

GENERAL INSTRUCTIONS:
1. Analyze the provided context carefully
2. Answer the question based ONLY on the information in the context
3. If the information is not found in the context, say "Information not found in the provided document"
4. Provide specific references to clauses/sections when possible
5. Be precise and accurate in your response
6. Return a structured JSON response with the following format:

{{
    "answer": "Your detailed answer here",
    "justification": "Explanation of why this answer is correct based on the document",
    "matched_clauses": ["List of relevant clauses/sections from the document"],
    "score_details": {{
        "document_type": "{document_type}",
        "question_weight": {question_weight},
        "document_weight": {document_weight},
        "score": {question_weight * document_weight}
    }},
    "confidence": 0.85
}}

IMPORTANT:
- Only use information from the provided context
- Be specific and cite relevant sections
- If information is missing, clearly state that
- Ensure the response is valid JSON
- Confidence should be between 0.0 and 1.0 based on how certain you are
- Score is calculated as question_weight × document_weight

JSON RESPONSE:
"""
        return prompt
    
    def generate_answer(self, question: str, context_chunks: List[str], document_type: str = "unknown") -> Dict[str, Any]:
        """Generate an answer using Gemini with structured JSON output"""
        
        # If API is not available, return an error response
        if not self.api_available:
            return self._create_error_response("Gemini API not available", document_type)
        
        try:
            prompt = self.create_prompt(question, context_chunks, document_type)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = response_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    # If JSON not found, create a structured response
                    result = self._create_structured_response(response_text, question, document_type)
                    
            except json.JSONDecodeError as e:
                # If JSON parsing fails, create a structured response
                result = self._create_structured_response(response_text, question, document_type)
            
            return result
            
        except Exception as e:
            # Return error response
            return self._create_error_response(str(e), document_type)
    
    def _create_structured_response(self, response_text: str, question: str, document_type: str) -> Dict[str, Any]:
        """Create a structured response when JSON parsing fails"""
        if document_type == "Policy Wordings":
            document_weight = 0.5
        elif document_type in ["Legal Documents", "Financial Documents", "Technical Documents", "Medical Documents"]:
            document_weight = 0.5
        else:
            document_weight = 2.0
        
        question_weight = 2.0
        
        # Extract answer from response text
        answer = response_text.strip()
        if not answer:
            answer = "No answer could be generated from the provided context."
        
        return {
            "answer": answer,
            "justification": f"Response generated from {document_type} context using Gemini AI.",
            "matched_clauses": ["Document context chunks"],
            "score_details": {
                "document_type": document_type,
                "question_weight": question_weight,
                "document_weight": document_weight,
                "score": question_weight * document_weight
            },
            "confidence": 0.8
        }
    
    def _create_error_response(self, error_message: str, document_type: str) -> Dict[str, Any]:
        """Create an error response"""
        if document_type == "Policy Wordings":
            document_weight = 0.5
        elif document_type in ["Legal Documents", "Financial Documents", "Technical Documents", "Medical Documents"]:
            document_weight = 0.5
        else:
            document_weight = 2.0
        
        question_weight = 2.0
        
        return {
            "answer": f"An error occurred while processing your request: {error_message}",
            "justification": "Technical error in the LLM service.",
            "matched_clauses": [],
            "score_details": {
                "document_type": document_type,
                "question_weight": question_weight,
                "document_weight": document_weight,
                "score": question_weight * document_weight
            },
            "confidence": 0.0
        }
    
    def calculate_score(self, document_type: str, question_weight: float = 2.0) -> float:
        """Calculate score based on document type and question weight"""
        if document_type == "Policy Wordings":
            document_weight = 0.5
        elif document_type in ["Legal Documents", "Financial Documents", "Technical Documents", "Medical Documents"]:
            document_weight = 0.5
        else:
            document_weight = 2.0
        return question_weight * document_weight 