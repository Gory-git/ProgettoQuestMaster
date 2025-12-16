"""
Narrative Generation Service
Generates narrative text and optional images for story gameplay
"""

import os
import openai
from typing import Dict, List, Optional


class NarrativeService:
    """
    Service for generating narrative content during gameplay
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        openai.api_key = self.api_key
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.dalle_enabled = os.getenv('DALLE_ENABLED', 'False').lower() == 'true'
        self.dalle_model = os.getenv('DALLE_MODEL', 'dall-e-3')
        self.dalle_size = os.getenv('DALLE_SIZE', '1024x1024')
    
    def generate_narrative(self, lore: str, current_state: str, 
                          action_taken: Optional[str], 
                          available_actions: List[str]) -> str:
        """
        Generate narrative text for current game state
        
        Args:
            lore: Story lore for context
            current_state: Current PDDL state description
            action_taken: Action that was just taken (None for initial state)
            available_actions: List of actions currently available
            
        Returns:
            Generated narrative text
        """
        
        prompt = self._create_narrative_prompt(lore, current_state, action_taken, available_actions)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative storyteller. Generate engaging, immersive narrative text "
                                  "that brings the story world to life. Write in second person present tense."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,  # Higher temperature for creative writing
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"[Narrative generation error: {str(e)}]"
    
    def _create_narrative_prompt(self, lore: str, state: str, 
                                 action: Optional[str], actions: List[str]) -> str:
        """Create prompt for narrative generation"""
        
        if action:
            action_text = f"\n\nThe player just chose: {action}"
        else:
            action_text = "\n\nThis is the beginning of the story."
        
        actions_text = '\n'.join(f"- {a}" for a in actions)
        
        return f"""Generate engaging narrative text for this interactive story.

STORY CONTEXT:
{lore[:500]}

CURRENT SITUATION:
{state}{action_text}

AVAILABLE CHOICES (don't list these - they'll be shown separately):
{actions_text}

Write a vivid, immersive paragraph (3-5 sentences) that:
1. Describes the current situation dramatically
2. Reflects the consequences of the recent action (if any)
3. Sets up the tension/decision for what comes next
4. Uses sensory details and atmosphere

Write in second person ("You...") and present tense.
"""
    
    def generate_image(self, narrative_text: str, lore_context: str) -> Optional[str]:
        """
        Generate an image for the current narrative scene
        
        Args:
            narrative_text: The narrative text for this scene
            lore_context: Brief lore context for style consistency
            
        Returns:
            URL of generated image, or None if generation fails or is disabled
        """
        
        if not self.dalle_enabled:
            return None
        
        try:
            # Create image prompt from narrative
            image_prompt = self._create_image_prompt(narrative_text, lore_context)
            
            response = openai.Image.create(
                model=self.dalle_model,
                prompt=image_prompt,
                size=self.dalle_size,
                quality=os.getenv('DALLE_QUALITY', 'standard'),
                n=1
            )
            
            return response.data[0].url
            
        except Exception as e:
            print(f"Image generation error: {str(e)}")
            return None
    
    def _create_image_prompt(self, narrative: str, lore: str) -> str:
        """
        Create DALL-E prompt from narrative text
        
        Args:
            narrative: Narrative text
            lore: Story lore for style
            
        Returns:
            Image generation prompt
        """
        # Extract key visual elements from narrative
        # This is a simplified version - could use LLM to extract better
        
        style_context = lore[:200] if lore else "fantasy adventure"
        
        prompt = f"""A cinematic scene from an interactive story: {narrative[:200]}

Style: {style_context}

Create a dramatic, atmospheric illustration with rich details and mood lighting.
Fantasy art style, high quality, professional illustration."""
        
        return prompt[:1000]  # DALL-E has prompt length limits
    
    def format_actions_for_display(self, actions: List[str], 
                                   action_descriptions: Dict[str, str]) -> List[Dict]:
        """
        Format actions for display in the UI
        
        Args:
            actions: List of action names
            action_descriptions: Mapping of action names to descriptions
            
        Returns:
            List of formatted action dictionaries
        """
        formatted = []
        
        for i, action in enumerate(actions):
            formatted.append({
                'id': i,
                'action': action,
                'description': action_descriptions.get(action, action),
                'display_text': self._humanize_action(action)
            })
        
        return formatted
    
    def _humanize_action(self, action: str) -> str:
        """
        Convert PDDL action to human-readable text
        
        Args:
            action: PDDL action string
            
        Returns:
            Humanized action text
        """
        # Remove parentheses and underscores
        clean = action.replace('(', '').replace(')', '').replace('_', ' ')
        
        # Capitalize first letter of each word
        words = clean.split()
        humanized = ' '.join(word.capitalize() for word in words)
        
        return humanized
