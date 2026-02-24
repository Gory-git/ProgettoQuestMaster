"""
Narrative Generation Service
Generates narrative text and optional images for story gameplay
"""

import os
from openai import OpenAI
from typing import Dict, List, Optional
import re
from .game_service import humanize_pddl_action


class NarrativeService:
    """
    Service for generating narrative content during gameplay
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        self.dalle_enabled = os.getenv('DALLE_ENABLED', 'False').lower() == 'true'
        self.dalle_model = os.getenv('DALLE_MODEL', 'dall-e-3')
        self.dalle_size = os.getenv('DALLE_SIZE', '1024x1024')
    
    def generate_narrative(self, lore: str, current_state: str, 
                          action_taken: Optional[str], 
                          available_actions: List[str],
                          current_facts: Optional[List[str]] = None,
                          action_history: Optional[List[str]] = None) -> str:
        """
        Generate narrative text for current game state
        
        Args:
            lore: Story lore for context
            current_state: Current PDDL state description
            action_taken: Action that was just taken (None for initial state)
            available_actions: List of actions currently available
            current_facts: Optional list of current PDDL facts for richer context
            action_history: Optional list of recent action names for story continuity
            
        Returns:
            Generated narrative text
        """
        
        prompt = self._create_narrative_prompt(
            lore, current_state, action_taken, available_actions,
            current_facts=current_facts, action_history=action_history
        )
        
        try:
            response = self.client.chat.completions.create(
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
                                 action: Optional[str], actions: List[str],
                                 current_facts: Optional[List[str]] = None,
                                 action_history: Optional[List[str]] = None) -> str:
        """Create prompt for narrative generation"""
        
        if action:
            action_text = f"\n\nThe player just chose: {action}"
        else:
            action_text = "\n\nThis is the beginning of the story."
        
        actions_text = '\n'.join(f"- {a}" for a in actions)

        facts_section = ""
        if current_facts:
            facts_section = f"\n\nCURRENT STATE FACTS:\n{'; '.join(current_facts[:15])}"

        history_section = ""
        if action_history:
            history_section = f"\n\nRECENT STORY PATH:\n{' → '.join(action_history[-5:])}"
        
        return f"""Generate engaging narrative text for this interactive story.

STORY CONTEXT:
{lore[:500]}

CURRENT SITUATION:
{state}{action_text}{facts_section}{history_section}

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
            
            response = self.client.images.generate(
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
    
    def narrativize_choices(self, lore: str, current_narrative: str,
                            available_actions: List[str]) -> List[str]:
        """
        Transform PDDL action strings into engaging narrative choices.

        Args:
            lore: Story lore for context
            current_narrative: The current narrative text to provide context
            available_actions: List of PDDL action description strings to transform

        Returns:
            List of narrative choice strings in the same order as available_actions
        """
        if not available_actions:
            return []

        prompt = self._create_narrativize_prompt(lore, current_narrative, available_actions)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative storyteller converting game actions into "
                                   "immersive narrative choices. Keep each choice concise (5-10 words)."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            content = response.choices[0].message.content.strip()
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            # Strip any leading numbering or bullet characters
            narrativized = []
            for line in lines:
                line = re.sub(r'^[\d]+[.)]\s*', '', line)
                line = re.sub(r'^[-*]\s*', '', line)
                if line:
                    narrativized.append(line)

            # Ensure we return exactly as many choices as we received
            if len(narrativized) == len(available_actions):
                return narrativized

            # Fallback: pad with humanized versions if counts don't match
            result = []
            for i, action in enumerate(available_actions):
                result.append(narrativized[i] if i < len(narrativized)
                               else humanize_pddl_action(action))
            return result

        except Exception as e:
            print(f"Narrativize choices error: {str(e)}")
            return [humanize_pddl_action(action) for action in available_actions]

    def _create_narrativize_prompt(self, lore: str, current_narrative: str,
                                   actions: List[str]) -> str:
        """Create prompt for narrativizing action choices"""
        actions_list = '\n'.join(f"{i + 1}. {a}" for i, a in enumerate(actions))
        return f"""Transform these game actions into engaging narrative choices for an interactive story.

STORY LORE:
{lore[:500]}

CURRENT NARRATIVE (this is where the player currently is in the story):
{current_narrative[:300]}

ACTIONS TO TRANSFORM (in order):
{actions_list}

For each action, write a short, immersive narrative choice (5-10 words) that fits the CURRENT story moment.
The choices must feel different from each other and reflect the specific situation described above.
Return EXACTLY {len(actions)} lines, one narrative choice per line, in the same order.
Do not include numbers, bullets, or extra formatting - just the choice text.
"""

    def generate_quest_summary(self, lore: str, story_title: str,
                               narrative_history: List[Dict],
                               action_summary_lines: List[str],
                               steps_taken: int) -> str:
        """
        Generate a narrative summary of the completed quest.

        Args:
            lore: Story lore for context
            story_title: Title of the story
            narrative_history: List of {step, narrative, action} dicts
            action_summary_lines: List of already-humanized action strings (e.g. "Step 1: ...")
            steps_taken: Total number of steps taken

        Returns:
            A narrative summary of the quest
        """
        actions_text = '\n'.join(action_summary_lines) if action_summary_lines else "No actions recorded."

        # Pick key narrative moments (beginning, middle, end)
        key_narratives = []
        if narrative_history:
            key_narratives.append(narrative_history[0].get('narrative', ''))
            if len(narrative_history) > 2:
                mid = len(narrative_history) // 2
                key_narratives.append(narrative_history[mid].get('narrative', ''))
            key_narratives.append(narrative_history[-1].get('narrative', ''))

        key_moments_text = '\n\n'.join(key_narratives) if key_narratives else ''

        prompt = self._create_quest_summary_prompt(
            lore, story_title, actions_text, key_moments_text, steps_taken
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a master storyteller. Write an epic, celebratory summary "
                            "of a completed quest. Write in second person past tense ('You did...', 'You defeated...')."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=600
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Quest summary generation error: {str(e)}")
            return (
                f"🏆 Quest Complete!\n\n"
                f"You completed '{story_title}' in {steps_taken} steps.\n\n"
                f"Your journey:\n{actions_text}"
            )

    def _create_quest_summary_prompt(self, lore: str, story_title: str,
                                     actions_text: str, key_moments: str,
                                     steps_taken: int) -> str:
        return f"""Write an epic narrative summary of a completed quest.

STORY: {story_title}

LORE CONTEXT:
{lore[:400]}

KEY MOMENTS FROM THE ADVENTURE:
{key_moments[:600]}

ACTIONS TAKEN (in order):
{actions_text}

TOTAL STEPS: {steps_taken}

Write a vivid, celebratory 3-5 paragraph summary that:
1. Opens with a dramatic hook about the hero's triumph
2. Recounts the key moments and choices made during the adventure
3. Describes the most important actions taken (use the action list above)
4. Closes with a triumphant conclusion about the hero's achievement

Write in second person past tense ("You ventured...", "You discovered...", "You defeated...").
Make it feel like the end credits of an epic adventure. Use markdown for emphasis where appropriate.
"""

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
            action: PDDL action string like "move (agent, loc1, loc2)" or "take_item (char, item, loc)"
            
        Returns:
            Humanized action text like "Agent moves from loc1 to loc2"
        """
        # Use shared humanization logic from game_service
        return humanize_pddl_action(action)
