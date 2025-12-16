import re
from typing import Optional, Dict, Any, List
from app.models.pddl_domain import PDDLDomain
from app.models.pddl_problem import PDDLProblem
from app.services.llm_service import LLMService


class PDDLService:
    """Service for PDDL domain and problem handling with AI generation and refinement."""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    @staticmethod
    def _clean_pddl(content: str) -> str:
        """
        Clean PDDL content by extracting only valid PDDL code and removing comments/extra text.
        
        This function:
        - Removes AI explanations before/after PDDL code
        - Strips markdown code blocks (```pddl ... ```)
        - Removes single-line comments (;)
        - Removes multi-line comments if present
        - Preserves only valid PDDL structure
        
        Args:
            content: Raw PDDL content potentially containing extra text and comments
            
        Returns:
            Cleaned PDDL code with only valid structure
        """
        # Remove markdown code blocks (```pddl ... ``` or ``` ... ```)
        content = re.sub(r'```(?:pddl)?\s*\n', '', content)
        content = re.sub(r'\n```', '', content)
        
        # Extract PDDL blocks that start with (define and end with closing parenthesis
        # This handles cases where there's explanatory text before/after the PDDL
        pddl_pattern = r'(\(define[^)]*(?:\([^)]*\))*\))'
        matches = re.findall(pddl_pattern, content, re.DOTALL)
        
        if matches:
            # If we found PDDL blocks, use the first complete one
            content = matches[0]
        
        # Remove single-line comments (everything after ;)
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove comment part (everything from ; onwards)
            if ';' in line:
                line = line[:line.index(';')]
            # Strip whitespace and keep non-empty lines
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Remove extra whitespace while preserving structure
        content = re.sub(r'\n\s*\n', '\n', content)  # Remove blank lines
        content = re.sub(r'\s+', ' ', content)  # Normalize spaces
        
        # Re-add newlines for readability after parentheses
        content = re.sub(r'\)\s*\(', ')\n(', content)
        content = content.strip()
        
        return content
    
    def generate_pddl_domain(
        self,
        domain_name: str,
        problem_description: str,
        requirements: Optional[List[str]] = None
    ) -> PDDLDomain:
        """
        Generate a PDDL domain using AI based on problem description.
        
        Args:
            domain_name: Name for the PDDL domain
            problem_description: Description of the domain problem
            requirements: Optional list of PDDL requirements
            
        Returns:
            PDDLDomain object with generated content
        """
        requirements_str = ", ".join(requirements) if requirements else "basic requirements"
        
        prompt = f"""Generate a complete PDDL domain definition for the following problem:

Problem: {problem_description}
Domain Name: {domain_name}
Requirements: {requirements_str}

Generate only valid PDDL code without any explanation. The domain should include:
- Proper (define (domain ...)) structure
- Predicates section
- Actions section with appropriate preconditions and effects

Ensure the PDDL syntax is valid and well-structured."""
        
        raw_content = self.llm_service.generate_content(prompt)
        cleaned_content = self._clean_pddl(raw_content)
        
        return PDDLDomain(
            name=domain_name,
            content=cleaned_content,
            raw_ai_response=raw_content
        )
    
    def generate_pddl_problem(
        self,
        problem_name: str,
        domain_name: str,
        problem_description: str
    ) -> PDDLProblem:
        """
        Generate a PDDL problem using AI based on problem description.
        
        Args:
            problem_name: Name for the PDDL problem
            domain_name: Name of the domain this problem uses
            problem_description: Description of the specific problem instance
            
        Returns:
            PDDLProblem object with generated content
        """
        prompt = f"""Generate a complete PDDL problem definition for the following:

Problem Name: {problem_name}
Domain: {domain_name}
Description: {problem_description}

Generate only valid PDDL code without any explanation. The problem should include:
- Proper (define (problem ...)) structure
- Objects section
- Initial state section
- Goal section

Ensure the PDDL syntax is valid and references the correct domain."""
        
        raw_content = self.llm_service.generate_content(prompt)
        cleaned_content = self._clean_pddl(raw_content)
        
        return PDDLProblem(
            name=problem_name,
            domain_name=domain_name,
            content=cleaned_content,
            raw_ai_response=raw_content
        )
    
    def refine_pddl_domain(
        self,
        domain: PDDLDomain,
        feedback: str
    ) -> PDDLDomain:
        """
        Refine an existing PDDL domain based on user feedback.
        
        Args:
            domain: The PDDLDomain to refine
            feedback: User feedback for refinement
            
        Returns:
            Updated PDDLDomain with refined content
        """
        prompt = f"""Refine the following PDDL domain based on the feedback provided:

Current Domain:
{domain.content}

Feedback for Refinement:
{feedback}

Generate the refined PDDL domain code. Make only the necessary changes to address the feedback.
Generate only valid PDDL code without any explanation."""
        
        raw_content = self.llm_service.generate_content(prompt)
        cleaned_content = self._clean_pddl(raw_content)
        
        domain.content = cleaned_content
        domain.raw_ai_response = raw_content
        domain.version = (domain.version or 0) + 1
        
        return domain
    
    def refine_pddl_problem(
        self,
        problem: PDDLProblem,
        feedback: str
    ) -> PDDLProblem:
        """
        Refine an existing PDDL problem based on user feedback.
        
        Args:
            problem: The PDDLProblem to refine
            feedback: User feedback for refinement
            
        Returns:
            Updated PDDLProblem with refined content
        """
        prompt = f"""Refine the following PDDL problem based on the feedback provided:

Current Problem:
{problem.content}

Domain: {problem.domain_name}

Feedback for Refinement:
{feedback}

Generate the refined PDDL problem code. Make only the necessary changes to address the feedback.
Generate only valid PDDL code without any explanation."""
        
        raw_content = self.llm_service.generate_content(prompt)
        cleaned_content = self._clean_pddl(raw_content)
        
        problem.content = cleaned_content
        problem.raw_ai_response = raw_content
        problem.version = (problem.version or 0) + 1
        
        return problem
    
    def validate_pddl_syntax(self, content: str) -> Dict[str, Any]:
        """
        Validate PDDL syntax (basic validation).
        
        Args:
            content: PDDL content to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        
        # Check for balanced parentheses
        if content.count('(') != content.count(')'):
            issues.append("Unbalanced parentheses")
        
        # Check for required keywords
        if not re.search(r'\(define\s+\(', content):
            issues.append("Missing '(define' declaration")
        
        # Check for domain or problem definition
        if not re.search(r'\(domain\s+\w+\)', content) and not re.search(r'\(problem\s+\w+\)', content):
            issues.append("Missing domain or problem definition")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "content_length": len(content)
        }
