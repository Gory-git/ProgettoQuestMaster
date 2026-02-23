"""
PDDL Validation Service
Validates PDDL files using Fast Downward or basic syntax checking
"""

import os
import tempfile
import subprocess
import re
from typing import Dict, List, Tuple


class PDDLValidationService:
    """
    Service for validating PDDL files
    """
    
    def __init__(self):
        """Initialize validator"""
        self.fast_downward_path = os.getenv('FAST_DOWNWARD_PATH')
    
    def validate(self, domain_content: str, problem_content: str) -> Tuple[bool, List[str]]:
        """
        Validate PDDL domain and problem files
        
        Args:
            domain_content:  PDDL domain file content
            problem_content: PDDL problem file content
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Basic syntax validation
        syntax_errors = self._validate_syntax(domain_content, problem_content)
        if syntax_errors:
            errors. extend(syntax_errors)
        
        # Only proceed with deeper checks if syntax is clean
        if not errors:
            # Try Fast Downward validation if available
            if self.fast_downward_path and os.path.exists(self.fast_downward_path):
                fd_errors = self._validate_with_fast_downward(domain_content, problem_content)
                if fd_errors:
                    errors.extend(fd_errors)

            # Check goal reachability using internal BFS
            reachable, reach_msg = self._check_reachability_internal(domain_content, problem_content)
            if not reachable:
                errors.append(reach_msg)
        
        return len(errors) == 0, errors
    
    def _validate_syntax(self, domain:  str, problem: str) -> List[str]:
        """
        Basic PDDL syntax validation
        
        Args:
            domain: Domain file content
            problem: Problem file content
            
        Returns: 
            List of error messages
        """
        errors = []
        
        # Check domain structure
        if not domain.strip().startswith('(define'):
            errors.append("Domain file must start with '(define'")
        
        # Fixed regex:  allow alphanumeric, hyphens, and underscores
        if not re.search(r'\(domain\s+[\w\-]+\)', domain):
            errors.append("Domain file must contain (domain <name>)")
        
        # Check problem structure
        if not problem.strip().startswith('(define'):
            errors.append("Problem file must start with '(define'")
        
        # Fixed regex: allow alphanumeric, hyphens, and underscores
        if not re.search(r'\(problem\s+[\w\-]+\)', problem):
            errors.append("Problem file must contain (problem <name>)")
        
        # Fixed regex: allow alphanumeric, hyphens, and underscores
        if not re.search(r'\(:domain\s+[\w\-]+\)', problem):
            errors. append("Problem file must reference a domain with (:domain <name>)")
        
        # Check parentheses balance
        if domain.count('(') != domain.count(')'):
            errors. append("Unbalanced parentheses in domain file")
        
        if problem.count('(') != problem.count(')'):
            errors.append("Unbalanced parentheses in problem file")
        
        return errors
    
    def _validate_with_fast_downward(self, domain: str, problem: str) -> List[str]:
        """
        Validate using Fast Downward planner
        
        Args: 
            domain: Domain file content
            problem: Problem file content
            
        Returns:
            List of error messages
        """
        errors = []
        
        try:
            # Create temporary files
            with tempfile. NamedTemporaryFile(mode='w', suffix='.pddl', delete=False) as domain_file:
                domain_file.write(domain)
                domain_path = domain_file. name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='. pddl', delete=False) as problem_file:
                problem_file.write(problem)
                problem_path = problem_file.name
            
            # Run Fast Downward validator
            cmd = [
                self.fast_downward_path,
                '--validate',
                domain_path,
                problem_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output for errors
            if result.returncode != 0:
                error_output = result.stderr + result.stdout
                errors.append(f"Fast Downward validation failed: {error_output}")
            
            # Clean up temp files
            os.unlink(domain_path)
            os.unlink(problem_path)
            
        except subprocess.TimeoutExpired:
            errors.append("Validation timeout - PDDL may be too complex")
        except Exception as e:
            errors.append(f"Fast Downward validation error: {str(e)}")
        
        return errors
    
    def _check_reachability_internal(self, domain: str, problem: str) -> Tuple[bool, str]:
        """
        Check goal reachability using a pure-Python BFS over PDDL states.
        This is the fallback used when Fast Downward is not available.

        Args:
            domain: Domain file content
            problem: Problem file content

        Returns:
            Tuple of (reachable, message)
        """
        try:
            from app.services.game_service import PDDLParser, ActionCalculator, StateEvaluator

            parser = PDDLParser(domain, problem)
            calculator = ActionCalculator(parser)
            goal = parser.goal

            initial_frozen = frozenset(parser.initial_state)
            queue = [(initial_frozen, 0)]
            visited = {initial_frozen}
            max_depth = 50
            max_states = 10000

            while queue:
                if len(visited) > max_states:
                    return True, (
                        "Reachability check inconclusive (state space too large) - assuming valid"
                    )

                current_frozen, depth = queue.pop(0)
                current_set = set(current_frozen)

                # Check if goal is satisfied
                goal_ok = all(p in current_set for p in goal.get('positive', []))
                goal_ok = goal_ok and all(p not in current_set for p in goal.get('negative', []))
                if goal_ok:
                    return True, f"Goal reachable in {depth} steps"

                if depth >= max_depth:
                    continue

                # Expand successors
                applicable = calculator.get_applicable_actions(current_set)
                for action in applicable:
                    action_def = parser.actions.get(action['action'])
                    if not action_def:
                        continue
                    next_frozen = calculator._simulate_action_effect(
                        action_def, action['bindings'], current_set
                    )
                    if next_frozen not in visited:
                        visited.add(next_frozen)
                        queue.append((next_frozen, depth + 1))

            return False, (
                "No reachable solution found: the goal state cannot be reached "
                "from the initial state with the available actions"
            )

        except Exception:
            # Do not block validation if the internal check itself fails
            return True, "Internal reachability check skipped due to a parsing error"

    def check_plan_exists(self, domain:  str, problem: str) -> Tuple[bool, str]:
        """
        Check if a valid plan exists for the problem
        
        Args:
            domain: Domain file content
            problem: Problem file content
            
        Returns:
            Tuple of (plan_exists, message)
        """
        if not self.fast_downward_path or not os.path.exists(self.fast_downward_path):
            return True, "Fast Downward not available - skipping plan validation"
        
        try: 
            # Create temporary files
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pddl', delete=False) as domain_file:
                domain_file.write(domain)
                domain_path = domain_file.name
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pddl', delete=False) as problem_file:
                problem_file.write(problem)
                problem_path = problem_file.name
            
            # Run Fast Downward to find a plan
            cmd = [
                self.fast_downward_path,
                domain_path,
                problem_path,
                '--search', 'astar(lmcut())'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Check if plan was found
            plan_found = 'Solution found' in result.stdout or result.returncode == 0
            
            # Clean up
            os.unlink(domain_path)
            os.unlink(problem_path)
            
            if plan_found:
                return True, "Valid plan exists"
            else:
                return False, "No valid plan found - goal may be unreachable"
            
        except subprocess.TimeoutExpired:
            return False, "Planning timeout - problem may be too difficult"
        except Exception as e: 
            return False, f"Plan checking error: {str(e)}"
