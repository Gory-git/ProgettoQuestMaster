import re
import logging
from typing import Optional, Tuple
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class PDDLGenerationService:
    """Service for generating and refining PDDL domain and problem files using Claude AI."""

    def __init__(self, api_key: str):
        """
        Initialize the PDDL Generation Service.
        
        Args:
            api_key: Anthropic API key for Claude AI access
        """
        self.client = Anthropic()
        self.conversation_history = []

    def _clean_pddl(self, content: str) -> str:
        """
        Extract valid PDDL code from AI-generated content by removing comments and extra text.
        
        Args:
            content: Raw content from AI that may contain explanations and comments
            
        Returns:
            Cleaned PDDL code without comments or extra text
        """
        # Remove markdown code blocks if present
        content = re.sub(r'```pddl\n?', '', content)
        content = re.sub(r'```\n?', '', content)
        
        # Split by lines for processing
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove inline comments (anything after ;)
            if ';' in line:
                line = line.split(';')[0]
            
            # Strip whitespace
            line = line.strip()
            
            # Skip empty lines and lines that look like explanations
            if not line or line.startswith('Note:') or line.startswith('Explanation:'):
                continue
                
            cleaned_lines.append(line)
        
        # Join the cleaned lines
        pddl_code = '\n'.join(cleaned_lines).strip()
        
        # Remove any remaining markdown artifacts
        pddl_code = re.sub(r'\*\*.*?\*\*', '', pddl_code)
        
        return pddl_code

    def generate_pddl(
        self,
        game_description: str,
        domain_name: str = "quest_domain"
    ) -> Tuple[str, str]:
        """
        Generate PDDL domain and problem files from a natural language game description.
        
        Args:
            game_description: Natural language description of the game scenario
            domain_name: Name for the PDDL domain (default: "quest_domain")
            
        Returns:
            Tuple of (domain_pddl, problem_pddl) as strings
            
        Raises:
            ValueError: If the AI response cannot be parsed into domain and problem files
        """
        try:
            # Clear conversation history for new generation
            self.conversation_history = []
            
            # Create the initial prompt for PDDL generation
            initial_prompt = f"""You are an expert in PDDL (Planning Domain Definition Language).
            
Convert the following game description into valid PDDL domain and problem files.

Game Description:
{game_description}

Please provide:
1. A PDDL domain file (with predicates, actions, etc.)
2. A PDDL problem file (with initial state and goals)

Format your response with clear sections labeled "DOMAIN:" and "PROBLEM:"."""

            # Add the initial message to history
            self.conversation_history.append({
                "role": "user",
                "content": initial_prompt
            })
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Parse the response to extract domain and problem
            domain_match = re.search(r'DOMAIN:\s*(.*?)(?=PROBLEM:|$)', assistant_message, re.DOTALL)
            problem_match = re.search(r'PROBLEM:\s*(.*?)$', assistant_message, re.DOTALL)
            
            if not domain_match or not problem_match:
                raise ValueError("Could not parse domain and problem sections from AI response")
            
            domain_pddl = self._clean_pddl(domain_match.group(1))
            problem_pddl = self._clean_pddl(problem_match.group(1))
            
            logger.info(f"Generated PDDL domain and problem for: {domain_name}")
            
            return domain_pddl, problem_pddl
            
        except Exception as e:
            logger.error(f"Error generating PDDL: {str(e)}")
            raise

    def refine_pddl(
        self,
        domain_pddl: str,
        problem_pddl: str,
        feedback: str
    ) -> Tuple[str, str]:
        """
        Refine existing PDDL domain and problem files based on user feedback.
        
        Args:
            domain_pddl: Current PDDL domain file content
            problem_pddl: Current PDDL problem file content
            feedback: User feedback for refinement
            
        Returns:
            Tuple of (refined_domain_pddl, refined_problem_pddl) as strings
            
        Raises:
            ValueError: If the refinement cannot be completed
        """
        try:
            # Add the refinement request to conversation history
            refinement_prompt = f"""Based on the following feedback, please refine the PDDL files:

Feedback: {feedback}

Current Domain:
{domain_pddl}

Current Problem:
{problem_pddl}

Please provide the refined PDDL files with clear sections labeled "DOMAIN:" and "PROBLEM:"."""

            self.conversation_history.append({
                "role": "user",
                "content": refinement_prompt
            })
            
            # Call Claude API with conversation history for context
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=self.conversation_history
            )
            
            assistant_message = response.content[0].text
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Parse the response to extract refined domain and problem
            domain_match = re.search(r'DOMAIN:\s*(.*?)(?=PROBLEM:|$)', assistant_message, re.DOTALL)
            problem_match = re.search(r'PROBLEM:\s*(.*?)$', assistant_message, re.DOTALL)
            
            if not domain_match or not problem_match:
                raise ValueError("Could not parse refined domain and problem sections from AI response")
            
            refined_domain = self._clean_pddl(domain_match.group(1))
            refined_problem = self._clean_pddl(problem_match.group(1))
            
            logger.info("Successfully refined PDDL files based on feedback")
            
            return refined_domain, refined_problem
            
        except Exception as e:
            logger.error(f"Error refining PDDL: {str(e)}")
            raise
