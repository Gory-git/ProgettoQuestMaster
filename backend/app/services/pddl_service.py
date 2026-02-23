"""
PDDL Generation Service
Uses OpenAI LLM to generate PDDL domain and problem files from lore documents
"""

import os
import re
from openai import OpenAI
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
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.temperature = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
    
    @staticmethod
    def _clean_pddl(content:  str) -> str:
        """
        Clean PDDL content by removing only markdown blocks and comments,
        while preserving all PDDL structure and parentheses. 
        
        Args:
            content: Raw PDDL content potentially containing markdown blocks
            
        Returns:
            Cleaned PDDL code preserving all structure
        """
        # Remove markdown code blocks (```pddl ... ``` or ``` ... ```)
        content = re.sub(r'```pddl\s*\n', '', content)
        content = re.sub(r'```\s*\n', '', content)
        content = re.sub(r'\n```\s*$', '', content)
        
        # Split into lines for processing
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove inline comments (everything after ; NOT in a string)
            # But preserve semicolons if they're inside parentheses as part of PDDL syntax
            if ';' in line: 
                # Simple approach: if line has balanced parens before ;, remove comment
                before_comment = line. split(';')[0]
                # Count parens to see if we're inside a structure
                open_count = before_comment.count('(') - before_comment.count(')')
                if open_count >= 0:
                    # Safe to remove comment
                    line = before_comment
            
            line = line.rstrip()  # Remove trailing whitespace only
            
            # Skip empty lines
            if line.strip():
                cleaned_lines.append(line)
        
        # Join lines preserving structure
        result = '\n'.join(cleaned_lines)
        
        # Fix formatting:  add newline before opening paren at root level
        # This helps with readability but preserves structure
        result = re. sub(r'\)\s*\(', ')\n(', result)
        
        return result. strip()
    
    def generate_pddl(self, lore_content: str, branching_factor_min: int, 
                     branching_factor_max: int, depth_min: int, depth_max:  int) -> Tuple[str, str]:
        """
        Generate PDDL domain and problem files from lore content
        
        Args:
            lore_content: The story lore document
            branching_factor_min:  Minimum number of actions available at each state
            branching_factor_max: Maximum number of actions available at each state
            depth_min:  Minimum steps to reach goal
            depth_max: Maximum steps to reach goal
            
        Returns: 
            Tuple of (domain_content, problem_content)
        """
        
        # Generate PDDL domain
        domain_prompt = self._create_domain_prompt(lore_content, branching_factor_min, branching_factor_max)
        domain_content = self._call_openai(domain_prompt)
        domain_content = self._clean_pddl(domain_content)
        
        # Generate PDDL problem
        problem_prompt = self._create_problem_prompt(lore_content, domain_content, depth_min, depth_max)
        problem_content = self._call_openai(problem_prompt)
        problem_content = self._clean_pddl(problem_content)
        
        return domain_content, problem_content
    
    def _create_domain_prompt(self, lore:  str, bf_min: int, bf_max: int) -> str:
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
2. Define appropriate types for objects (character, location, item, etc.)
3. Define predicates that capture the story state; include predicates that track plot progress and character status (e.g., quest-started, npc-ally, clue-found)
4. Define actions with preconditions and effects
5. Use narrative-flavored action names that reflect story events rather than generic movement primitives (e.g., use `investigate_dark_corner` or `negotiate_with_guard` instead of `move_loc1_loc2`)
6. Ensure all parentheses are balanced and valid
7. Ensure actions are logically consistent

Output ONLY the PDDL domain file content, starting with (define (domain .. .) and ending with the final closing parenthesis.  Do NOT include any explanation or comments before or after the PDDL code. 
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
- Problem name should be a slug version of the story (use hyphens, no spaces)
- Domain reference must match the domain name from the domain file

REQUIREMENTS:
1. Define all objects mentioned in the domain
2. Set up initial state predicates that match the story beginning
3. Define a goal that represents story completion/success
4. Ensure consistency with the domain file
5. Ensure all parentheses are balanced and valid
6. Reference the correct domain name with (: domain <name>)

Output ONLY the PDDL problem file content, starting with (define (problem ...) and ending with the final closing parenthesis. Do NOT include any explanation or comments before or after the PDDL code.
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert PDDL developer and interactive storytelling designer. Output valid PDDL syntax without explanations. "},
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
            validation_errors:  Errors from validator
            reflection_feedback: Reflection agent's analysis
            author_input: Author's modification requests
            
        Returns:
            Refined PDDL content
        """
        prompt = f"""You are an expert in PDDL debugging and refinement. 

The following PDDL has validation errors.  Please fix them based on the feedback provided.

CURRENT PDDL:
{current_pddl}

VALIDATION ERRORS: 
{validation_errors}

REFLECTION AGENT ANALYSIS:
{reflection_feedback}

AUTHOR INPUT:
{author_input}

Please provide the corrected PDDL file.  Ensure: 
1. All parentheses are balanced
2. Domain name is consistent
3. Problem name matches requirements
4. All required sections are present (:domain, :objects, :init, :goal)
5. Syntax is valid PDDL

Output ONLY the corrected PDDL content without any explanation.  Preserve the domain/problem name if it's correct.
"""
        refined_pddl = self._call_openai(prompt)
        return self._clean_pddl(refined_pddl)
