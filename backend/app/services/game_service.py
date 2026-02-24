"""
Game Service - Core game engine for interactive PDDL-based gameplay
Handles PDDL parsing, state tracking, action calculation, and game orchestration
"""

import re
from typing import Dict, List, Set, Tuple, Optional, Any


def humanize_pddl_action(action: str) -> str:
    """
    Convert PDDL action format to human-readable text
    
    Args:
        action: PDDL action string like "move (agent, loc1, loc2)" or just action name
        
    Returns:
        Humanized action text like "Agent moves from loc1 to loc2"
    """
    # Parse PDDL action format: "action_name (param1, param2, param3)"
    match = re.match(r'([a-z_-]+)\s*\(([^)]+)\)', action, re.IGNORECASE)
    
    if not match:
        # Fallback: just clean up the text
        clean = action.replace('(', '').replace(')', '').replace('_', ' ')
        words = clean.split()
        return ' '.join(word.capitalize() for word in words)
    
    action_name = match.group(1)
    params_str = match.group(2)
    params = [p.strip() for p in params_str.split(',')]
    
    # Create natural language based on action patterns
    action_lower = action_name.lower().replace('_', ' ').replace('-', ' ')
    
    if not params:
        return action_lower.capitalize()
    
    # Common action patterns
    if 'move' in action_lower or 'go' in action_lower:
        # move (character, from, to) -> "Character moves from X to Y"
        if len(params) >= 3:
            return f"{params[0].capitalize()} moves from {params[1]} to {params[2]}"
        elif len(params) >= 2:
            return f"{params[0].capitalize()} moves to {params[1]}"
    
    elif 'take' in action_lower or 'pick' in action_lower or 'get' in action_lower:
        # take_item (character, item, location) -> "Character takes item at location"
        if len(params) >= 3:
            return f"{params[0].capitalize()} takes {params[1]} at {params[2]}"
        elif len(params) >= 2:
            return f"{params[0].capitalize()} takes {params[1]}"
    
    elif 'drop' in action_lower or 'put' in action_lower or 'place' in action_lower:
        # drop_item (character, item, location) -> "Character drops item at location"
        if len(params) >= 3:
            return f"{params[0].capitalize()} drops {params[1]} at {params[2]}"
        elif len(params) >= 2:
            return f"{params[0].capitalize()} drops {params[1]}"
    
    elif 'save' in action_lower or 'rescue' in action_lower:
        # save_man (character, person, location) -> "Character saves person at location"
        if len(params) >= 3:
            return f"{params[0].capitalize()} saves {params[1]} at {params[2]}"
        elif len(params) >= 2:
            return f"{params[0].capitalize()} saves {params[1]}"
    
    elif 'give' in action_lower or 'hand' in action_lower:
        # give_item (giver, receiver, item, location) -> "Giver gives item to receiver at location"
        if len(params) >= 4:
            return f"{params[0].capitalize()} gives {params[2]} to {params[1]} at {params[3]}"
        elif len(params) >= 3:
            return f"{params[0].capitalize()} gives {params[2]} to {params[1]}"
    
    elif 'talk' in action_lower or 'speak' in action_lower or 'converse' in action_lower:
        # talk_to (character, person, location) -> "Character talks to person at location"
        if len(params) >= 3:
            return f"{params[0].capitalize()} talks to {params[1]} at {params[2]}"
        elif len(params) >= 2:
            return f"{params[0].capitalize()} talks to {params[1]}"
    
    # Generic fallback: "Character action_name at/with param2..."
    action_readable = ' '.join(word.capitalize() for word in action_lower.split())
    
    if len(params) == 1:
        return f"{params[0].capitalize()} {action_readable.lower()}"
    elif len(params) == 2:
        return f"{params[0].capitalize()} {action_readable.lower()} {params[1]}"
    else:
        # Multiple params: "Character does action with/at param2, param3..."
        other_params = ', '.join(params[1:])
        return f"{params[0].capitalize()} {action_readable.lower()} involving {other_params}"


class PDDLParser:
    """Parse PDDL domain and problem files to extract actions, predicates, and state"""
    
    def __init__(self, domain_content: str, problem_content: str):
        self.domain_content = domain_content
        self.problem_content = problem_content
        self.actions = {}
        self.predicates = []
        self.objects = {}
        self.initial_state = set()
        self.goal = {'positive': [], 'negative': []}  # Dict with positive/negative conditions
        self._parse()
    
    def _parse(self):
        """Parse both domain and problem files"""
        self._parse_domain()
        self._parse_problem()
    
    def _parse_domain(self):
        """Parse domain file for actions and predicates"""
        # Parse predicates
        pred_match = re.search(r'\(:predicates\s+(.*?)\s*\)', self.domain_content, re.DOTALL)
        if pred_match:
            pred_text = pred_match.group(1)
            # Extract each predicate
            for pred in re.findall(r'\(([^)]+)\)', pred_text):
                pred_name = pred.split()[0] if pred.split() else pred
                self.predicates.append(pred_name)
        
        # Parse actions using a better approach
        # Find all :action blocks
        action_blocks = []
        i = 0
        while i < len(self.domain_content):
            action_start = self.domain_content.find('(:action', i)
            if action_start == -1:
                break
            
            # Find the matching closing paren for this action
            depth = 0
            j = action_start
            while j < len(self.domain_content):
                if self.domain_content[j] == '(':
                    depth += 1
                elif self.domain_content[j] == ')':
                    depth -= 1
                    if depth == 0:
                        action_blocks.append(self.domain_content[action_start:j+1])
                        break
                j += 1
            i = j + 1
        
        # Now parse each action block
        for action_block in action_blocks:
            # Extract action name (allow hyphens in action names)
            name_match = re.search(r'\(:action\s+([\w-]+)', action_block)
            if not name_match:
                continue
            action_name = name_match.group(1)
            
            # Extract parameters
            params_match = re.search(r':parameters\s+\((.*?)\)', action_block, re.DOTALL)
            parameters = params_match.group(1) if params_match else ''
            
            # Extract precondition
            precond_match = re.search(r':precondition\s+(.+?)\s+:effect', action_block, re.DOTALL)
            precondition = precond_match.group(1).strip() if precond_match else ''
            
            # Extract effect (everything after :effect until the end)
            effect_match = re.search(r':effect\s+(.+?)\s*\)\s*$', action_block, re.DOTALL)
            effect = effect_match.group(1).strip() if effect_match else ''
            
            self.actions[action_name] = {
                'name': action_name,
                'parameters': self._parse_parameters(parameters),
                'precondition': self._parse_condition(precondition),
                'effect': self._parse_effect(effect)
            }
    
    def _parse_parameters(self, param_str: str) -> List[Dict[str, str]]:
        """Parse action parameters"""
        params = []
        # Match patterns like ?c - character or ?item
        param_pattern = r'\?(\w+)(?:\s*-\s*(\w+))?'
        for match in re.finditer(param_pattern, param_str):
            params.append({
                'name': match.group(1),
                'type': match.group(2) if match.group(2) else 'object'
            })
        return params
    
    def _parse_condition(self, cond_str: str) -> Dict[str, Any]:
        """Parse precondition or goal condition"""
        cond_str = cond_str.strip()
        
        # Handle (and ...) wrapper
        if cond_str.startswith('(and'):
            # Find matching closing paren for 'and'
            depth = 0
            start = 4  # after '(and'
            i = start
            while i < len(cond_str) and cond_str[i].isspace():
                i += 1
            start = i
            
            # Find the end of the 'and' expression
            for j in range(len(cond_str)):
                if cond_str[j] == '(':
                    depth += 1
                elif cond_str[j] == ')':
                    depth -= 1
                    if depth == 0:  # Found matching paren for initial 'and'
                        cond_str = cond_str[start:j].strip()
                        break
        
        conditions = {'positive': [], 'negative': []}
        
        # Extract all predicates
        depth = 0
        current = []
        i = 0
        while i < len(cond_str):
            if cond_str[i] == '(':
                depth += 1
                if depth == 1:
                    current = []
                else:
                    current.append(cond_str[i])
            elif cond_str[i] == ')':
                depth -= 1
                if depth == 0 and current:
                    pred_str = ''.join(current).strip()
                    # Check for negation
                    if pred_str.startswith('not'):
                        # Extract the negated predicate
                        neg_match = re.search(r'not\s*\(\s*([^)]+)\)', pred_str)
                        if neg_match:
                            conditions['negative'].append(neg_match.group(1).strip())
                    else:
                        conditions['positive'].append(pred_str)
                    current = []
                else:
                    current.append(cond_str[i])
            else:
                if depth > 0:
                    current.append(cond_str[i])
            i += 1
        
        return conditions
    
    def _parse_effect(self, effect_str: str) -> Dict[str, List[str]]:
        """Parse action effects"""
        effect_str = effect_str.strip()
        
        # Handle (and ...) wrapper
        if effect_str.startswith('(and'):
            # Find matching closing paren for 'and'
            depth = 0
            start = 4  # after '(and'
            i = start
            while i < len(effect_str) and effect_str[i].isspace():
                i += 1
            start = i
            
            # Find the end of the 'and' expression
            for j in range(len(effect_str)):
                if effect_str[j] == '(':
                    depth += 1
                elif effect_str[j] == ')':
                    depth -= 1
                    if depth == 0:  # Found matching paren for initial 'and'
                        effect_str = effect_str[start:j].strip()
                        break
        
        effects = {'add': [], 'delete': []}
        
        # Extract all predicates
        depth = 0
        current = []
        i = 0
        while i < len(effect_str):
            if effect_str[i] == '(':
                depth += 1
                if depth == 1:
                    current = []
                else:
                    current.append(effect_str[i])
            elif effect_str[i] == ')':
                depth -= 1
                if depth == 0 and current:
                    pred_str = ''.join(current).strip()
                    # Check for negation
                    if pred_str.startswith('not'):
                        # Extract the negated predicate
                        neg_match = re.search(r'not\s*\(\s*([^)]+)\)', pred_str)
                        if neg_match:
                            effects['delete'].append(neg_match.group(1).strip())
                    else:
                        effects['add'].append(pred_str)
                    current = []
                else:
                    current.append(effect_str[i])
            else:
                if depth > 0:
                    current.append(effect_str[i])
            i += 1
        
        return effects
    
    def _parse_problem(self):
        """Parse problem file for objects, initial state, and goal"""
        # Parse objects
        obj_match = re.search(r'\(:objects\s+(.*?)\s*\)', self.problem_content, re.DOTALL)
        if obj_match:
            obj_text = obj_match.group(1)
            # Parse typed objects: name1 name2 - type1 name3 - type2
            current_names = []
            tokens = obj_text.split()
            i = 0
            while i < len(tokens):
                if tokens[i] == '-' and i + 1 < len(tokens):
                    # Assign type to all accumulated names
                    obj_type = tokens[i + 1]
                    for name in current_names:
                        self.objects[name] = obj_type
                    current_names = []
                    i += 2
                else:
                    current_names.append(tokens[i])
                    i += 1
            # Remaining names without type
            for name in current_names:
                self.objects[name] = 'object'
        
        # Parse initial state
        init_match = re.search(r'\(:init\s+(.*?)\s*\)\s*\(:goal', self.problem_content, re.DOTALL)
        if init_match:
            init_text = init_match.group(1)
            # Extract all predicates
            for pred in re.findall(r'\(([^)]+)\)', init_text):
                self.initial_state.add(pred.strip())
        
        # Parse goal
        goal_match = re.search(r'\(:goal\s+(.+?)\s*\)\s*\)\s*$', self.problem_content, re.DOTALL)
        if goal_match:
            goal_text = goal_match.group(1)
            goal_cond = self._parse_condition(goal_text)
            self.goal = goal_cond


class StateEvaluator:
    """Evaluate action preconditions against current game state"""
    
    @staticmethod
    def evaluate_precondition(precondition: Dict[str, List[str]], 
                             current_state: Set[str], 
                             bindings: Dict[str, str]) -> bool:
        """
        Check if precondition is satisfied in current state with given bindings
        
        Args:
            precondition: Dict with 'positive' and 'negative' predicate lists
            current_state: Set of current facts
            bindings: Variable to object mappings
            
        Returns:
            True if precondition is satisfied
        """
        # Check positive preconditions
        for pred in precondition['positive']:
            grounded = StateEvaluator._ground_predicate(pred, bindings)
            if grounded not in current_state:
                return False
        
        # Check negative preconditions
        for pred in precondition['negative']:
            grounded = StateEvaluator._ground_predicate(pred, bindings)
            if grounded in current_state:
                return False
        
        return True
    
    @staticmethod
    def _ground_predicate(predicate: str, bindings: Dict[str, str]) -> str:
        """Replace variables in predicate with actual objects"""
        grounded = predicate
        for var, obj in bindings.items():
            grounded = re.sub(r'\?' + var + r'\b', obj, grounded)
        return grounded


class ActionCalculator:
    """Calculate which actions are applicable in the current state"""
    
    def __init__(self, parser: PDDLParser):
        self.parser = parser
    
    def get_applicable_actions(self, current_state: Set[str]) -> List[Dict[str, Any]]:
        """
        Find all actions that can be executed in current state
        
        Args:
            current_state: Set of current facts
            
        Returns:
            List of applicable action instances with bindings
        """
        applicable = []
        
        for action_name, action_def in self.parser.actions.items():
            # Generate all possible bindings for this action
            bindings_list = self._generate_bindings(action_def['parameters'])
            
            for bindings in bindings_list:
                # Check if precondition is satisfied
                if StateEvaluator.evaluate_precondition(
                    action_def['precondition'], 
                    current_state, 
                    bindings
                ):
                    applicable.append({
                        'action': action_name,
                        'bindings': bindings,
                        'description': self._format_action_description(action_name, bindings)
                    })
        
        return applicable

    def _simulate_action_effect(self, action_def: Dict[str, Any], bindings: Dict[str, str],
                                current_state: Set[str]) -> frozenset:
        """
        Simulate the effect of an action without modifying the real state.

        Args:
            action_def: Action definition with 'effect' key
            bindings: Variable to object mappings
            current_state: Current set of facts

        Returns:
            frozenset of facts resulting from the action
        """
        new_state = set(current_state)

        for pred in action_def['effect']['add']:
            grounded = StateEvaluator._ground_predicate(pred, bindings)
            new_state.add(grounded)

        for pred in action_def['effect']['delete']:
            grounded = StateEvaluator._ground_predicate(pred, bindings)
            new_state.discard(grounded)

        return frozenset(new_state)
    
    def _generate_bindings(self, parameters: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Generate all possible variable bindings for action parameters.
        
        Note: This generates the Cartesian product of all possible object combinations,
        which can have exponential complexity. For typical story domains with 5-20 objects
        and 2-3 parameters per action, this is acceptable. For larger domains, consider:
        - Limiting object combinations through type constraints
        - Using heuristics to prune unlikely bindings
        - Implementing lazy evaluation with generators
        """
        if not parameters:
            return [{}]
        
        # Get objects for each parameter type
        bindings_list = [{}]
        
        for param in parameters:
            param_name = param['name']
            param_type = param['type']
            
            # Find all objects of this type
            objects = [obj for obj, obj_type in self.parser.objects.items() 
                      if obj_type == param_type or param_type == 'object']
            
            if not objects:
                objects = list(self.parser.objects.keys())
            
            # Extend bindings with each possible object
            new_bindings = []
            for binding in bindings_list:
                for obj in objects:
                    new_binding = binding.copy()
                    new_binding[param_name] = obj
                    new_bindings.append(new_binding)
            
            bindings_list = new_bindings
        
        return bindings_list
    
    def _format_action_description(self, action_name: str, bindings: Dict[str, str]) -> str:
        """Create human-readable action description in PDDL format"""
        # Format as: action_name (param1, param2, param3)
        # This will be parsed by humanize_pddl_action function
        if bindings:
            params = ', '.join(bindings.values())
            return f"{action_name} ({params})"
        return action_name


class GameState:
    """Track and manage current game state"""
    
    def __init__(self, initial_state: Set[str], goal: Dict[str, List[str]]):
        self.current_facts = initial_state.copy()
        self.goal = goal
        self.step_count = 0
        self.action_history = []
        self.visited_states: Set[frozenset] = set()
        self.visited_states.add(frozenset(self.current_facts))
    
    def apply_action(self, action_def: Dict[str, Any], bindings: Dict[str, str]):
        """Apply action effects to update state"""
        effects = action_def['effect']
        
        # Apply positive effects (add facts)
        for pred in effects['add']:
            grounded = StateEvaluator._ground_predicate(pred, bindings)
            self.current_facts.add(grounded)
        
        # Apply negative effects (delete facts)
        for pred in effects['delete']:
            grounded = StateEvaluator._ground_predicate(pred, bindings)
            self.current_facts.discard(grounded)
        
        # Record the new state
        self.visited_states.add(frozenset(self.current_facts))

        # Update history
        self.step_count += 1
        self.action_history.append({
            'step': self.step_count,
            'action': action_def['name'],
            'bindings': bindings
        })
    
    def is_goal_reached(self) -> bool:
        """Check if current state satisfies goal conditions"""
        # Check positive goal conditions
        for pred in self.goal.get('positive', []):
            if pred not in self.current_facts:
                return False
        
        # Check negative goal conditions
        for pred in self.goal.get('negative', []):
            if pred in self.current_facts:
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for storage"""
        return {
            'facts': list(self.current_facts),
            'step_count': self.step_count,
            'action_history': self.action_history,
            'visited_states': [list(s) for s in self.visited_states]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], goal: Dict[str, List[str]]) -> 'GameState':
        """Reconstruct state from dictionary"""
        state = cls(set(data.get('facts', [])), goal)
        state.step_count = data.get('step_count', 0)
        state.action_history = data.get('action_history', [])
        # Restore visited_states from serialized data if present; otherwise fall back
        # to treating the current (restored) facts as the only visited state.
        raw_visited = data.get('visited_states', [])
        if raw_visited:
            state.visited_states = {frozenset(s) for s in raw_visited}
        else:
            # Fallback: at least the current state is marked as visited
            state.visited_states = {frozenset(state.current_facts)}
        return state


class GameEngine:
    """Orchestrate gameplay - main entry point for game operations"""
    
    def __init__(self, domain_content: str, problem_content: str):
        self.parser = PDDLParser(domain_content, problem_content)
        self.calculator = ActionCalculator(self.parser)
        self.game_state = GameState(self.parser.initial_state, self.parser.goal)
    
    def initialize_game(self, max_actions: Optional[int] = None) -> Dict[str, Any]:
        """Initialize a new game session"""
        return {
            'step': 0,
            'state': self.game_state.to_dict(),
            'goal_reached': False,
            'available_actions': self.get_available_actions(max_actions)
        }
    
    def get_available_actions(self, max_actions: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all actions available in current state, annotated with revisit info.

        Args:
            max_actions: If set, limit the returned actions to this many, preferring
                         actions that lead to new (unvisited) states.
        """
        applicable = self.calculator.get_applicable_actions(self.game_state.current_facts)

        if not applicable:
            return []

        # Format for display, annotating each action with whether it revisits a known state
        new_actions = []
        revisit_actions = []

        for action in applicable:
            action_def = self.parser.actions.get(action['action'])
            try:
                simulated = (
                    self.calculator._simulate_action_effect(
                        action_def, action['bindings'], self.game_state.current_facts
                    )
                    if action_def else frozenset(self.game_state.current_facts)
                )
            except (KeyError, Exception):
                simulated = frozenset(self.game_state.current_facts)
            revisits = simulated in self.game_state.visited_states

            formatted = {
                'id': f"{action['action']}_{hash(str(action['bindings']))}",
                'action': action['action'],
                'bindings': action['bindings'],
                'display_text': humanize_pddl_action(action['description']),
                'description': self._get_action_narrative(action['action'], action['bindings']),
                'revisits_state': revisits
            }

            if revisits:
                revisit_actions.append(formatted)
            else:
                new_actions.append(formatted)

        # Prefer actions that lead to new states; fall back to revisiting ones if needed
        all_actions = new_actions + revisit_actions
        if max_actions is not None and len(all_actions) > max_actions:
            all_actions = all_actions[:max_actions]
        return all_actions
    
    def execute_action(self, action_name: str, bindings: Dict[str, str],
                       max_actions: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute an action and update state
        
        Args:
            action_name: Name of action to execute
            bindings: Variable to object mappings
            
        Returns:
            Dict with updated state and whether goal is reached
        """
        # Get action definition
        action_def = self.parser.actions.get(action_name)
        if not action_def:
            raise ValueError(f"Unknown action: {action_name}")
        
        # Verify precondition
        if not StateEvaluator.evaluate_precondition(
            action_def['precondition'], 
            self.game_state.current_facts, 
            bindings
        ):
            raise ValueError(f"Action precondition not satisfied")
        
        # Apply action
        self.game_state.apply_action(action_def, bindings)
        
        # Check goal
        goal_reached = self.game_state.is_goal_reached()
        available_actions = [] if goal_reached else self.get_available_actions(max_actions)

        result = {
            'step': self.game_state.step_count,
            'state': self.game_state.to_dict(),
            'goal_reached': goal_reached,
            'available_actions': available_actions
        }

        if not goal_reached and not available_actions:
            result['dead_end'] = True

        return result
    
    def is_goal_reached(self) -> bool:
        """Check if goal state has been reached"""
        return self.game_state.is_goal_reached()
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current game state"""
        return {
            'step': self.game_state.step_count,
            'state': self.game_state.to_dict(),
            'goal_reached': self.is_goal_reached(),
            'available_actions': self.get_available_actions()
        }
    
    def _get_action_narrative(self, action_name: str, bindings: Dict[str, str]) -> str:
        """Generate narrative description for an action"""
        # Create PDDL format string and use shared humanization logic
        if bindings:
            params = ', '.join(bindings.values())
            pddl_action = f"{action_name} ({params})"
        else:
            pddl_action = action_name
        
        return humanize_pddl_action(pddl_action)
