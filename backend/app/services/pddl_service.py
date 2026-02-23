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
8. Ensure the domain is highly connected. Every reachable state (except the goal) must have at least {bf_min} applicable actions. Avoid dead ends by providing 'backtrack' actions or alternative routes for every major decision.
9. Never delete a predicate that is the sole enabler of all remaining story progress without providing an alternative route or action to re-establish it.
10. CRITICAL: Avoid action cycles where two or more actions undo each other indefinitely without a way to reach the goal.
    - Identify every pair of actions where action A adds predicate P and action B deletes predicate P (or vice versa). If applying A then B (or B then A) returns the world to the same state, that is a cycle A↔B.
    - Every such cycle MUST have a concrete exit condition: at least one action in the cycle must also add a one-way "story-progress" predicate (e.g., `clue-discovered`, `door-unlocked-permanently`) that is NEVER deleted by any action, so that the cycle is only possible before that predicate is established and the story can always advance toward the goal.
    - Example of a BAD cycle: `open_door` adds `(door-open)`, `close_door` deletes `(door-open)` - if `open_door` requires `(not (door-open))` and `close_door` requires `(door-open)`, the player can toggle forever with no progress.
    - Example of the FIX: make `open_door` also add `(door-was-opened)` (never deleted), and let the next story step require `(door-was-opened)` rather than `(door-open)`, so progress is irreversible.

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
7. CRITICAL: The initial state and goal MUST be reachable from each other through the defined actions. Verify mentally that there exists at least one sequence of actions leading from the initial state to the goal.

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
                    reflection_feedback: str, author_input: str,
                    context_pddl: str = "") -> str:
        """
        Refine PDDL based on validation errors and feedback
        
        Args:
            current_pddl: Current PDDL content
            validation_errors:  Errors from validator
            reflection_feedback: Reflection agent's analysis
            author_input: Author's modification requests
            context_pddl: Complementary PDDL file (domain if refining problem, or vice versa)
            
        Returns:
            Refined PDDL content
        """
        context_section = ""
        if context_pddl:
            context_section = f"""
COMPLEMENTARY FILE FOR CONTEXT:
{context_pddl}

"""
        prompt = f"""You are an expert in PDDL debugging and refinement. 

The following PDDL has validation errors.  Please fix them based on the feedback provided.

CURRENT PDDL:
{current_pddl}
{context_section}
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
6. If this is the domain file, ensure every action needed to reach the goal is present. If this is the problem file, ensure the goal predicates are reachable from the initial state using the domain actions.
7. ANTI-CYCLE CHECK: Verify that no pair of actions can undo each other indefinitely without a path to the goal. For every pair of actions where action A adds a predicate that action B deletes (or vice versa), confirm that at least one of those actions also adds a one-way story-progress predicate that is never deleted by any action, making progress irreversible. If a cycle is found, fix it by introducing such a predicate (e.g., `event-completed`, `npc-convinced-permanently`) and making subsequent story steps depend on it rather than on the reversible predicate.

Output ONLY the corrected PDDL content without any explanation.  Preserve the domain/problem name if it's correct.
"""
        refined_pddl = self._call_openai(prompt)
        return self._clean_pddl(refined_pddl)

    def auto_fix_pddl(self, domain: str, problem: str,
                      validation_errors: list, reflection_feedback: str) -> tuple:
        """
        Fix both domain and problem files together using full context.

        Args:
            domain: Current PDDL domain content
            problem: Current PDDL problem content
            validation_errors: List of validation error strings
            reflection_feedback: Reflection agent's analysis text

        Returns:
            (fixed_domain, fixed_problem) tuple
        """
        errors_text = '\n'.join(f"- {e}" for e in validation_errors)

        # Fix domain with full context
        domain_prompt = f"""You are an expert PDDL debugger. Fix the PDDL domain file below.

CURRENT DOMAIN (to fix):
{domain}

CURRENT PROBLEM (for context, do NOT output this):
{problem}

VALIDATION ERRORS:
{errors_text}

ANALYSIS:
{reflection_feedback}

REQUIREMENTS FOR THE FIXED DOMAIN:
1. All parentheses must be balanced
2. All action preconditions and effects must be consistent
3. There must exist a sequence of actions from the initial state (in the problem) to the goal (in the problem)
4. No unreachable actions or dead-end states
5. CRITICAL: The goal predicate(s) defined in the problem MUST be achievable using the domain actions

Output ONLY the corrected domain file starting with (define (domain ...
"""
        fixed_domain = self._clean_pddl(self._call_openai(domain_prompt))

        # Fix problem with fixed domain as context
        problem_prompt = f"""You are an expert PDDL debugger. Fix the PDDL problem file below.

FIXED DOMAIN (for context, do NOT output this):
{fixed_domain}

CURRENT PROBLEM (to fix):
{problem}

VALIDATION ERRORS:
{errors_text}

ANALYSIS:
{reflection_feedback}

REQUIREMENTS FOR THE FIXED PROBLEM:
1. All parentheses must be balanced
2. The (:domain ...) reference must match the domain name exactly
3. All objects used in :init and :goal must be declared in :objects
4. All predicates used in :init and :goal must be defined in the domain
5. CRITICAL: The goal state MUST be reachable from the initial state using the domain actions above
6. Verify mentally: trace a path from initial state to goal using the available actions

Output ONLY the corrected problem file starting with (define (problem ...
"""
        fixed_problem = self._clean_pddl(self._call_openai(problem_prompt))

        return fixed_domain, fixed_problem
