"""
LLM Agent Module

This module provides the LLMAgent class which integrates with OpenAI's API
to generate PDDL domain/problem files, game narratives, action descriptions,
and image prompts/generations.

The module includes:
- LLMAgent: Main class handling all LLM interactions
- PDDLContent: Dataclass for PDDL domain and problem content
- NarrativeContent: Dataclass for narrative text and metadata
- ImageContent: Dataclass for image generation results

Author: ProgettoQuestMaster Team
Created: 2025-12-15
"""

import logging
import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

import openai
from openai import OpenAI, APIError, RateLimitError, APIConnectionError


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@dataclass
class PDDLContent:
    """
    Dataclass representing PDDL domain and problem content.
    
    Attributes:
        domain (str): PDDL domain definition
        problem (str): PDDL problem definition
        metadata (Dict[str, Any]): Additional metadata about the PDDL content
        generated_at (str): ISO format timestamp of generation
        model_used (str): Name of the model used for generation
    """
    domain: str
    problem: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    model_used: str = "gpt-4"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert PDDLContent to dictionary representation."""
        return {
            'domain': self.domain,
            'problem': self.problem,
            'metadata': self.metadata,
            'generated_at': self.generated_at,
            'model_used': self.model_used
        }


@dataclass
class NarrativeContent:
    """
    Dataclass representing narrative content for game storytelling.
    
    Attributes:
        title (str): Title of the narrative
        story (str): Main narrative text
        action_descriptions (Dict[str, str]): Descriptions for game actions
        metadata (Dict[str, Any]): Additional metadata
        generated_at (str): ISO format timestamp of generation
        model_used (str): Name of the model used for generation
    """
    title: str
    story: str
    action_descriptions: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    model_used: str = "gpt-4"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert NarrativeContent to dictionary representation."""
        return {
            'title': self.title,
            'story': self.story,
            'action_descriptions': self.action_descriptions,
            'metadata': self.metadata,
            'generated_at': self.generated_at,
            'model_used': self.model_used
        }


@dataclass
class ImageContent:
    """
    Dataclass representing generated image content.
    
    Attributes:
        image_url (str): URL of the generated image
        prompt (str): The prompt used to generate the image
        revised_prompt (str): The revised prompt used by the model
        model_used (str): Name of the model used for generation
        size (str): Size of the generated image
        generated_at (str): ISO format timestamp of generation
        metadata (Dict[str, Any]): Additional metadata
    """
    image_url: str
    prompt: str
    revised_prompt: str = ""
    model_used: str = "dall-e-3"
    size: str = "1024x1024"
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ImageContent to dictionary representation."""
        return {
            'image_url': self.image_url,
            'prompt': self.prompt,
            'revised_prompt': self.revised_prompt,
            'model_used': self.model_used,
            'size': self.size,
            'generated_at': self.generated_at,
            'metadata': self.metadata
        }


class LLMAgent:
    """
    LLM Agent for generating PDDL domains, narratives, and images using OpenAI API.
    
    This class provides methods to:
    - Generate PDDL domain and problem files from quest descriptions
    - Analyze and fix PDDL errors
    - Generate game narratives and action descriptions
    - Generate image prompts and images
    - Perform health checks on the API connection
    
    Attributes:
        client (OpenAI): OpenAI API client
        model_gpt4 (str): GPT-4 model identifier for PDDL and narrative generation
        model_image (str): DALL-E model identifier for image generation
        temperature_pddl (float): Temperature setting for PDDL generation
        temperature_narrative (float): Temperature setting for narrative generation
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_gpt4: str = "gpt-4",
        model_image: str = "dall-e-3",
        temperature_pddl: float = 0.3,
        temperature_narrative: float = 0.7
    ):
        """
        Initialize the LLMAgent.
        
        Args:
            api_key (Optional[str]): OpenAI API key. If None, uses OPENAI_API_KEY env var.
            model_gpt4 (str): GPT-4 model identifier. Defaults to "gpt-4".
            model_image (str): DALL-E model identifier. Defaults to "dall-e-3".
            temperature_pddl (float): Temperature for PDDL generation (0.0-2.0). Defaults to 0.3.
            temperature_narrative (float): Temperature for narrative generation (0.0-2.0). Defaults to 0.7.
            
        Raises:
            ValueError: If API key is not provided and OPENAI_API_KEY env var is not set.
        """
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OpenAI API key not provided and OPENAI_API_KEY env var not set")
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=api_key)
        self.model_gpt4 = model_gpt4
        self.model_image = model_image
        self.temperature_pddl = temperature_pddl
        self.temperature_narrative = temperature_narrative
        
        logger.info(f"LLMAgent initialized with models: GPT4={model_gpt4}, Image={model_image}")
    
    def generate_pddl(
        self,
        quest_description: str,
        domain_name: str = "quest_domain",
        additional_context: Optional[str] = None
    ) -> PDDLContent:
        """
        Generate PDDL domain and problem files from a quest description.
        
        Args:
            quest_description (str): Description of the quest to convert to PDDL.
            domain_name (str): Name for the PDDL domain. Defaults to "quest_domain".
            additional_context (Optional[str]): Additional context or constraints for PDDL generation.
            
        Returns:
            PDDLContent: Object containing generated domain and problem PDDL.
            
        Raises:
            APIError: If OpenAI API call fails.
            ValueError: If generated PDDL is invalid or empty.
            
        Example:
            >>> agent = LLMAgent()
            >>> pddl = agent.generate_pddl("A quest to find the lost artifact in the cave")
            >>> print(pddl.domain)
        """
        logger.info(f"Generating PDDL for quest: {quest_description[:100]}...")
        
        context_str = f"\nAdditional context:\n{additional_context}" if additional_context else ""
        
        prompt = f"""Generate PDDL domain and problem files for the following quest:

Quest Description:
{quest_description}
{context_str}

Requirements:
1. Create a PDDL domain definition with predicates and actions relevant to the quest
2. Create a PDDL problem file that instantiates the domain for this specific quest
3. Include realistic objects, locations, and conditions
4. Ensure all actions have preconditions and effects
5. Make the problem solvable with a reasonable sequence of actions

Format your response as two separate PDDL blocks:
1. First, the domain (starting with "(define (domain ...)")
2. Then, the problem (starting with "(define (problem ...)")

Separate them with a line containing exactly: ===PROBLEM==="""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_gpt4,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert PDDL planner. Generate valid, well-structured PDDL domains and problems."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature_pddl,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            logger.info("PDDL generation successful")
            
            # Parse domain and problem from response
            parts = content.split("===PROBLEM===")
            if len(parts) != 2:
                logger.warning("Response doesn't contain clear domain/problem separation")
                raise ValueError("Generated PDDL doesn't contain clear domain and problem sections")
            
            domain = parts[0].strip()
            problem = parts[1].strip()
            
            if not domain or not problem:
                logger.error("Generated PDDL domain or problem is empty")
                raise ValueError("Generated PDDL domain or problem is empty")
            
            return PDDLContent(
                domain=domain,
                problem=problem,
                metadata={
                    'quest_description': quest_description,
                    'domain_name': domain_name
                },
                model_used=self.model_gpt4
            )
            
        except (APIError, RateLimitError, APIConnectionError) as e:
            logger.error(f"OpenAI API error during PDDL generation: {str(e)}")
            raise APIError(f"Failed to generate PDDL: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during PDDL generation: {str(e)}")
            raise
    
    def analyze_pddl_error(
        self,
        pddl_content: str,
        error_message: str,
        context: Optional[str] = None
    ) -> str:
        """
        Analyze a PDDL error and generate a corrected version.
        
        Args:
            pddl_content (str): The PDDL content that has an error.
            error_message (str): The error message or description.
            context (Optional[str]): Additional context about the error.
            
        Returns:
            str: Corrected PDDL content.
            
        Raises:
            APIError: If OpenAI API call fails.
            
        Example:
            >>> agent = LLMAgent()
            >>> corrected = agent.analyze_pddl_error(bad_pddl, "Undefined predicate: location")
        """
        logger.info(f"Analyzing PDDL error: {error_message[:100]}...")
        
        context_str = f"\nContext:\n{context}" if context else ""
        
        prompt = f"""The following PDDL content has an error:

PDDL Content:
{pddl_content}

Error Message:
{error_message}
{context_str}

Please:
1. Identify the root cause of the error
2. Explain what's wrong
3. Provide the corrected PDDL content

Ensure the corrected PDDL is valid and maintains the original intent."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_gpt4,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert PDDL debugger. Help fix PDDL syntax and logical errors."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature_pddl,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            logger.info("PDDL error analysis successful")
            return result
            
        except (APIError, RateLimitError, APIConnectionError) as e:
            logger.error(f"OpenAI API error during PDDL error analysis: {str(e)}")
            raise APIError(f"Failed to analyze PDDL error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during PDDL error analysis: {str(e)}")
            raise
    
    def generate_narrative(
        self,
        quest_title: str,
        quest_description: str,
        setting: Optional[str] = None,
        tone: str = "adventure"
    ) -> NarrativeContent:
        """
        Generate a game narrative from quest parameters.
        
        Args:
            quest_title (str): Title of the quest.
            quest_description (str): Description of the quest.
            setting (Optional[str]): Setting/world description for the narrative.
            tone (str): Tone of the narrative (e.g., "adventure", "dark", "humorous"). Defaults to "adventure".
            
        Returns:
            NarrativeContent: Object containing the generated narrative and metadata.
            
        Raises:
            APIError: If OpenAI API call fails.
            
        Example:
            >>> agent = LLMAgent()
            >>> narrative = agent.generate_narrative(
            ...     "The Lost Artifact",
            ...     "Find the ancient artifact in the forgotten temple"
            ... )
        """
        logger.info(f"Generating narrative for quest: {quest_title}")
        
        setting_str = f"\nWorld Setting:\n{setting}" if setting else ""
        
        prompt = f"""Generate an engaging game narrative for the following quest:

Quest Title: {quest_title}
Quest Description: {quest_description}
Tone: {tone}
{setting_str}

Create:
1. An engaging opening narrative (2-3 paragraphs) that sets the scene
2. A compelling main narrative (3-5 paragraphs) that describes the quest
3. Narrative hooks that explain why the player should care about this quest

Make the narrative immersive, vivid, and tone-appropriate. Use second person ("you") to address the player."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_gpt4,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a creative game writer specializing in {tone} narratives. Create immersive and engaging quest stories."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature_narrative,
                max_tokens=2000
            )
            
            story = response.choices[0].message.content
            logger.info("Narrative generation successful")
            
            return NarrativeContent(
                title=quest_title,
                story=story,
                metadata={
                    'quest_description': quest_description,
                    'setting': setting,
                    'tone': tone
                },
                model_used=self.model_gpt4
            )
            
        except (APIError, RateLimitError, APIConnectionError) as e:
            logger.error(f"OpenAI API error during narrative generation: {str(e)}")
            raise APIError(f"Failed to generate narrative: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during narrative generation: {str(e)}")
            raise
    
    def generate_action_descriptions(
        self,
        actions: list[str],
        context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate descriptions for game actions.
        
        Args:
            actions (list[str]): List of action names to generate descriptions for.
            context (Optional[str]): Additional context about the game world or actions.
            
        Returns:
            Dict[str, str]: Mapping of action names to their descriptions.
            
        Raises:
            APIError: If OpenAI API call fails.
            
        Example:
            >>> agent = LLMAgent()
            >>> descriptions = agent.generate_action_descriptions(
            ...     ["pick_up_key", "unlock_door", "enter_room"]
            ... )
        """
        logger.info(f"Generating descriptions for {len(actions)} actions")
        
        context_str = f"\nContext:\n{context}" if context else ""
        
        prompt = f"""Generate engaging and clear descriptions for the following game actions:

Actions: {', '.join(actions)}
{context_str}

For each action, provide:
1. A clear, concise description of what the action does
2. Make it player-friendly and immersive
3. Use second person ("you")

Format your response as:
ACTION_NAME: Description text here"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_gpt4,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a game writer creating engaging descriptions for player actions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature_narrative,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            logger.info("Action descriptions generation successful")
            
            # Parse the response
            descriptions = {}
            for line in content.strip().split('\n'):
                if ':' in line:
                    action, desc = line.split(':', 1)
                    descriptions[action.strip()] = desc.strip()
            
            return descriptions
            
        except (APIError, RateLimitError, APIConnectionError) as e:
            logger.error(f"OpenAI API error during action descriptions generation: {str(e)}")
            raise APIError(f"Failed to generate action descriptions: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during action descriptions generation: {str(e)}")
            raise
    
    def generate_image_prompt(
        self,
        scene_description: str,
        art_style: str = "fantasy",
        mood: str = "adventurous",
        additional_details: Optional[str] = None
    ) -> str:
        """
        Generate an image prompt for visual scene generation.
        
        Args:
            scene_description (str): Description of the scene to visualize.
            art_style (str): Art style for the image (e.g., "fantasy", "realistic", "pixel art"). Defaults to "fantasy".
            mood (str): Mood/atmosphere (e.g., "adventurous", "dark", "peaceful"). Defaults to "adventurous".
            additional_details (Optional[str]): Additional details or requirements for the image.
            
        Returns:
            str: Optimized image prompt for DALL-E.
            
        Raises:
            APIError: If OpenAI API call fails.
            
        Example:
            >>> agent = LLMAgent()
            >>> prompt = agent.generate_image_prompt(
            ...     "A mysterious temple entrance in the jungle",
            ...     art_style="fantasy",
            ...     mood="mysterious"
            ... )
        """
        logger.info(f"Generating image prompt for scene: {scene_description[:100]}...")
        
        details_str = f"\nAdditional requirements:\n{additional_details}" if additional_details else ""
        
        prompt = f"""Create an optimized image generation prompt for DALL-E:

Scene Description: {scene_description}
Art Style: {art_style}
Mood: {mood}
{details_str}

Generate a detailed, vivid prompt that will produce a high-quality image. Include:
1. Specific visual elements and composition
2. Color palette suggestions
3. Lighting and atmosphere
4. Any important details from the scene description

Make the prompt concise but comprehensive (50-150 words)."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_gpt4,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating detailed, vivid prompts for image generation models."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            image_prompt = response.choices[0].message.content.strip()
            logger.info("Image prompt generation successful")
            return image_prompt
            
        except (APIError, RateLimitError, APIConnectionError) as e:
            logger.error(f"OpenAI API error during image prompt generation: {str(e)}")
            raise APIError(f"Failed to generate image prompt: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during image prompt generation: {str(e)}")
            raise
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> ImageContent:
        """
        Generate an image using DALL-E based on a prompt.
        
        Args:
            prompt (str): The image generation prompt.
            size (str): Image size ("1024x1024", "1024x1792", "1792x1024"). Defaults to "1024x1024".
            quality (str): Image quality ("standard" or "hd"). Defaults to "standard".
            
        Returns:
            ImageContent: Object containing the generated image URL and metadata.
            
        Raises:
            APIError: If OpenAI API call fails.
            ValueError: If image generation fails to produce a valid URL.
            
        Example:
            >>> agent = LLMAgent()
            >>> image = agent.generate_image("A brave knight standing in a misty forest")
            >>> print(image.image_url)
        """
        logger.info(f"Generating image with DALL-E, size: {size}")
        
        try:
            response = self.client.images.generate(
                model=self.model_image,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            if not response.data or not response.data[0].url:
                logger.error("Image generation returned no URL")
                raise ValueError("Image generation failed to produce a valid URL")
            
            logger.info("Image generation successful")
            
            return ImageContent(
                image_url=response.data[0].url,
                prompt=prompt,
                revised_prompt=getattr(response.data[0], 'revised_prompt', ''),
                size=size,
                model_used=self.model_image,
                metadata={'quality': quality}
            )
            
        except (APIError, RateLimitError, APIConnectionError) as e:
            logger.error(f"OpenAI API error during image generation: {str(e)}")
            raise APIError(f"Failed to generate image: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during image generation: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the OpenAI API connection.
        
        Returns:
            Dict[str, Any]: Health check results including:
                - status (str): "healthy" or "unhealthy"
                - gpt4_available (bool): Whether GPT-4 model is accessible
                - image_generation_available (bool): Whether image generation is available
                - timestamp (str): ISO format timestamp
                - error_message (Optional[str]): Error message if any
                
        Example:
            >>> agent = LLMAgent()
            >>> health = agent.health_check()
            >>> print(health['status'])
        """
        logger.info("Performing health check on OpenAI API")
        
        health_status = {
            'status': 'healthy',
            'gpt4_available': False,
            'image_generation_available': False,
            'timestamp': datetime.utcnow().isoformat(),
            'error_message': None
        }
        
        # Check GPT-4 availability
        try:
            response = self.client.chat.completions.create(
                model=self.model_gpt4,
                messages=[
                    {
                        "role": "user",
                        "content": "Respond with 'ok' only."
                    }
                ],
                max_tokens=5
            )
            health_status['gpt4_available'] = True
            logger.info("GPT-4 model is accessible")
        except Exception as e:
            logger.warning(f"GPT-4 model health check failed: {str(e)}")
            health_status['status'] = 'unhealthy'
            health_status['error_message'] = f"GPT-4 check failed: {str(e)}"
        
        # Check image generation availability
        try:
            response = self.client.images.generate(
                model=self.model_image,
                prompt="A simple red square",
                size="1024x1024",
                n=1
            )
            health_status['image_generation_available'] = response.data is not None
            if health_status['image_generation_available']:
                logger.info("Image generation model is accessible")
        except Exception as e:
            logger.warning(f"Image generation health check failed: {str(e)}")
            health_status['status'] = 'unhealthy'
            health_status['error_message'] = f"Image generation check failed: {str(e)}"
        
        return health_status


# Example usage and testing
if __name__ == "__main__":
    # Initialize the agent
    agent = LLMAgent()
    
    # Health check
    print("=== Health Check ===")
    health = agent.health_check()
    print(f"Status: {health['status']}")
    print(f"GPT-4 Available: {health['gpt4_available']}")
    print(f"Image Generation Available: {health['image_generation_available']}")
