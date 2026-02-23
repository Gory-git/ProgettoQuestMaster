"""
Reflection Agent Service
Analyzes PDDL validation errors and provides intelligent feedback for refinement
"""

import os
from openai import OpenAI
from typing import List, Dict


class ReflectionAgentService:
    """
    Reflection agent that analyzes PDDL errors and suggests fixes
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    def analyze_errors(self, pddl_domain: str, pddl_problem: str, 
                      validation_errors: List[str]) -> Dict[str, any]:
        """
        Analyze validation errors and provide structured feedback
        
        Args:
            pddl_domain: PDDL domain file content
            pddl_problem: PDDL problem file content
            validation_errors: List of validation error messages
            
        Returns:
            Dictionary containing analysis and suggestions
        """
        
        prompt = self._create_analysis_prompt(pddl_domain, pddl_problem, validation_errors)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert PDDL debugging assistant. Analyze errors and provide clear, actionable feedback."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more focused analysis
                max_tokens=2000
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            return {
                'analysis': analysis_text,
                'suggestions': self._extract_suggestions(analysis_text),
                'severity': self._assess_severity(validation_errors)
            }
            
        except Exception as e:
            return {
                'analysis': f"Error during reflection: {str(e)}",
                'suggestions': [],
                'severity': 'unknown'
            }
    
    def _create_analysis_prompt(self, domain: str, problem: str, errors: List[str]) -> str:
        """Create prompt for error analysis"""
        errors_text = '\n'.join(f"- {error}" for error in errors)
        
        return f"""Analyze the following PDDL validation errors and provide detailed feedback.

PDDL DOMAIN:
{domain[:2000]}

PDDL PROBLEM:
{problem[:2000]}

VALIDATION ERRORS:
{errors_text}

Please provide:
1. Root cause analysis of each error
2. Specific suggestions for fixing each issue
3. Whether the errors are related or independent
4. Priority order for fixing (what to address first)
5. Any potential side effects of the fixes

IMPORTANT: If one of the errors states that the goal is unreachable from the initial state,
analyze the domain actions and initial state carefully to identify which actions or predicates
are missing or incorrectly defined that would allow the goal to be reached. Suggest concrete
fixes to the domain and/or problem file.

Format your response clearly with numbered sections.
"""    
    def _extract_suggestions(self, analysis: str) -> List[str]:
        """
        Extract actionable suggestions from analysis text
        
        Args:
            analysis: Analysis text from LLM
            
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Simple extraction - look for numbered or bulleted lists
        lines = analysis.split('\n')
        for line in lines:
            line = line.strip()
            if line and (
                line[0].isdigit() or 
                line.startswith('-') or 
                line.startswith('*') or
                line.startswith('•')
            ):
                # Remove numbering/bullets
                clean_line = line.lstrip('0123456789.-*•').strip()
                if clean_line:
                    suggestions.append(clean_line)
        
        return suggestions
    
    def _assess_severity(self, errors: List[str]) -> str:
        """
        Assess severity of errors
        
        Args:
            errors: List of error messages
            
        Returns:
            Severity level: 'low', 'medium', 'high'
        """
        if not errors:
            return 'none'
        
        # Check for critical keywords
        critical_keywords = ['syntax', 'unbalanced', 'invalid', 'undefined', 'missing', 'unreachable', 'no reachable']
        
        critical_count = sum(
            1 for error in errors 
            for keyword in critical_keywords 
            if keyword.lower() in error.lower()
        )
        
        if critical_count >= 3:
            return 'high'
        elif critical_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    def generate_chat_response(self, conversation_history: List[Dict], 
                             user_message: str) -> str:
        """
        Generate a response in the interactive chat refinement loop
        
        Args:
            conversation_history: List of previous messages
            user_message: Latest message from author
            
        Returns:
            Agent's response
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful PDDL assistant helping an author refine their interactive story. "
                          "Be encouraging, provide clear guidance, and ask clarifying questions when needed."
            }
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"