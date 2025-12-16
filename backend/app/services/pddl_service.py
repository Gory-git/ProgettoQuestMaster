"""
PDDL Generation Service
Uses OpenAI LLM to generate PDDL domain and problem files from lore documents
"""

import os
import openai
from typing import Dict, Tuple


class PDDLGenerationService:
    """
    Service for generating PDDL files using LLM
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        openai.api_key = self.api_key
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
    
    def generate_pddl(self, lore_content: str, branching_factor_min: int, 
                     branching_factor_max: int, depth_min: int, depth_max: int) -> Tuple[str, str]:
        """
        Generate PDDL domain and problem files from lore content
        
        Args:
            lore_content: The story lore document
            branching_factor_min: Minimum number of actions available at each state
            branching_factor_max: Maximum number of actions available at each state
            depth_min: Minimum steps to reach goal
            depth_max: Maximum steps to reach goal
            
        Returns:
            Tuple of (domain_content, problem_content)
        """
        
        # Generate PDDL domain
        domain_prompt = self._create_domain_prompt(lore_content, branching_factor_min, branching_factor_max)
        domain_content = self._call_openai(domain_prompt)
        
        # Generate PDDL problem
        problem_prompt = self._create_problem_prompt(lore_content, domain_content, depth_min, depth_max)
        problem_content = self._call_openai(problem_prompt)
        
        return domain_content, problem_content
    
    def _create_domain_prompt(self, lore: str, bf_min: int, bf_max: int) -> str:
        """Create prompt for domain generation"""
        return f"""You are an expert in PDDL (Planning Domain Definition Language) and interactive storytelling.

Given the following story lore, create a PDDL domain file that models the adventure as a planning problem.

LORE:
{lore}

CONSTRAINTS:
- Branching factor: {bf_min}-{bf_max} actions should be available at each state
- Each action should represent a meaningful story choice
- Include predicates to track story state, character conditions, inventory, locations, etc.

REQUIREMENTS:
1. Use PDDL 2.1 or compatible syntax
2. Add descriptive comments on each line explaining what each element represents
3. Define appropriate types for objects (character, location, item, etc.)
4. Define predicates that capture the story state
5. Define actions with preconditions and effects
6. Ensure actions are logically consistent

Output ONLY the PDDL domain file content, starting with (define (domain ...) and ending with the closing parenthesis.
"""
    
    def _create_problem_prompt(self, lore: str, domain: str, depth_min: int, depth_max: int) -> str:
        """Create prompt for problem generation"""
        return f"""You are an expert in PDDL (Planning Domain Definition Language) and interactive storytelling.

Given the following story lore and PDDL domain, create a PDDL problem file that defines the initial state and goal.

LORE:
{lore}

DOMAIN:
{domain}

CONSTRAINTS:
- The solution should require between {depth_min} and {depth_max} steps to reach the goal
- Initial state should match the story setup described in the lore
- Goal should reflect the story objective

REQUIREMENTS:
1. Define all objects mentioned in the domain
2. Set up initial state predicates that match the story beginning
3. Define a goal that represents story completion/success
4. Add descriptive comments explaining each element
5. Ensure consistency with the domain file

Output ONLY the PDDL problem file content, starting with (define (problem ...) and ending with the closing parenthesis.
"""
    
    def _call_openai(self, prompt: str) -> str:
        """
        Call OpenAI API with the given prompt
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Generated text response
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert PDDL developer and interactive storytelling designer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=3000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def refine_pddl(self, current_pddl: str, validation_errors: str, 
                    reflection_feedback: str, author_input: str) -> str:
        """
        Refine PDDL based on validation errors and feedback
        
        Args:
            current_pddl: Current PDDL content
            validation_errors: Errors from validator
            reflection_feedback: Reflection agent's analysis
            author_input: Author's modification requests
            
        Returns:
            Refined PDDL content
        """
        prompt = f"""You are an expert in PDDL debugging and refinement.

The following PDDL has validation errors. Please fix them based on the feedback provided.

CURRENT PDDL:
{current_pddl}

VALIDATION ERRORS:
{validation_errors}

REFLECTION AGENT ANALYSIS:
{reflection_feedback}

AUTHOR INPUT:
{author_input}

Please provide the corrected PDDL file. Maintain all comments and only fix the issues identified.
Output ONLY the corrected PDDL content.
"""
        return self._call_openai(prompt)
