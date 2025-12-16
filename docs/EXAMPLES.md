# QuestMaster Usage Examples

## Example 1: Creating "The Crystal Cave" Story

### Step 1: Create the Story

Using the web interface:
1. Navigate to http://localhost:3000/create
2. Fill in the form:
   - **Title**: The Crystal Cave
   - **Description**: A brave adventurer seeks a legendary crystal in an ancient cave
   - **Lore Content**: (see docs/example_story.md)
   - **Branching Factor**: Min 2, Max 4
   - **Depth**: Min 5, Max 8

Or using the API:
```bash
curl -X POST http://localhost:5000/api/stories \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Crystal Cave",
    "description": "A brave adventurer seeks a legendary crystal in an ancient cave",
    "lore_content": "You are a brave adventurer seeking the legendary Crystal of Power...",
    "branching_factor_min": 2,
    "branching_factor_max": 4,
    "depth_min": 5,
    "depth_max": 8
  }'
```

### Step 2: Generate PDDL

The system will use GPT-4 to generate:

**Domain File** (excerpt):
```pddl
(define (domain crystal-cave-adventure)
  ;; Domain for the Crystal Cave story
  
  (:requirements :strips :typing)
  
  (:types
    location      ;; Different places in the cave
    item         ;; Objects the player can carry
    character    ;; NPCs like the hermit or guardian
  )
  
  (:predicates
    (at ?loc - location)              ;; Player is at location
    (has ?item - item)                ;; Player has item
    (connected ?l1 ?l2 - location)    ;; Locations are connected
    (crystal-obtained)                ;; Player has the crystal
    (guardian-pacified)               ;; Guardian is dealt with
    (hermit-helped)                   ;; Hermit provided assistance
  )
  
  (:action move
    :parameters (?from ?to - location)
    :precondition (and 
      (at ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?from))
      (at ?to)
    )
  )
  
  ;; Additional actions...
)
```

**Problem File** (excerpt):
```pddl
(define (problem crystal-cave-quest)
  (:domain crystal-cave-adventure)
  
  (:objects
    entrance tunnel1 tunnel2 chamber river guardian-room - location
    torch rope map crystal - item
    hermit guardian - character
  )
  
  (:init
    (at entrance)              ;; Start at cave entrance
    (has torch)                ;; Player has torch
    (has rope)                 ;; Player has rope
    (has map)                  ;; Player has map
    (connected entrance tunnel1)
    (connected entrance hermit-hut)
    ;; More connections...
  )
  
  (:goal
    (and
      (crystal-obtained)       ;; Got the crystal
      (at entrance)            ;; Returned safely
    )
  )
)
```

### Step 3: Validate PDDL

Click "Validate PDDL" button. The system will:
1. Check syntax (parentheses, structure)
2. Run Fast Downward validator (if installed)
3. Verify a valid plan exists

If validation fails, the Reflection Agent provides analysis:
```
VALIDATION ERRORS:
- Unbalanced parentheses in domain file at line 45
- Action 'take-crystal' missing precondition for guardian
- Goal state references undefined predicate 'safe-exit'

REFLECTION AGENT ANALYSIS:
I've identified three issues:

1. Syntax Error: There's a missing closing parenthesis in the 
   'solve-riddle' action definition. Add ')' after the effect.

2. Logic Error: The 'take-crystal' action should require that 
   the guardian is pacified first. Add (guardian-pacified) to 
   preconditions.

3. Undefined Predicate: The goal uses 'safe-exit' but it's not 
   defined in predicates. Either add it or use existing predicates.

SUGGESTED FIXES:
1. Line 45: Add closing parenthesis
2. Add precondition: (guardian-pacified)
3. Replace goal or add predicate definition
```

### Step 4: Refine (if needed)

You can:
- Use "Auto-Fix" to let GPT-4 correct the issues
- Chat with the Reflection Agent for guidance
- Manually edit and re-validate

### Step 5: Play the Story

Once validated, click "Play Story". The game begins:

**Turn 1:**
```
You stand at the entrance to the Mystic Cave. The morning sun 
illuminates the dark opening before you. Ancient runes are carved 
into the stone archway, warning of dangers within. Your torch 
flickers in the cool breeze. To your left, you notice a small 
hut where the hermit lives. Ahead, the cave beckons.

What do you do?
[Image: Cave entrance at dawn with mysterious runes]

OPTIONS:
○ Enter The Cave Through The Main Tunnel
○ Visit The Hermit's Hut
○ Examine The Ancient Runes
○ Check Your Equipment
```

**Turn 2** (after choosing "Visit The Hermit's Hut"):
```
You approach the weathered hut. An elderly hermit emerges, his 
eyes wise and knowing. "Seeking the Crystal, are you?" he asks 
with a knowing smile. "Many have tried. The cave has three main 
paths - the northern tunnel is treacherous but direct, the 
southern path is longer but safer, and the eastern passage... 
well, few return from there. Take this." He hands you a glowing 
amulet. "It may help with the guardian."

What do you do?
[Image: Wise hermit offering glowing amulet]

OPTIONS:
○ Accept The Amulet And Thank The Hermit
○ Ask About The Guardian
○ Ask About The Eastern Passage
○ Decline And Enter The Cave Alone
```

The game continues with dynamic narrative and choices until you complete the quest!

## Example 2: Sci-Fi Story

### Minimal Example

```bash
# Create story
curl -X POST http://localhost:5000/api/stories \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Space Station Omega",
    "lore_content": "You are the last surviving crew member on Space Station Omega. An alien infection has taken over the station. You must reach the escape pod in the docking bay while avoiding infected crew members and restoring power to locked sections.",
    "branching_factor_min": 2,
    "branching_factor_max": 3,
    "depth_min": 4,
    "depth_max": 6
  }'

# Generate PDDL (assuming story_id = 2)
curl -X POST http://localhost:5000/api/stories/2/generate-pddl

# Validate
curl -X POST http://localhost:5000/api/stories/2/validate

# If valid, start game
curl -X POST http://localhost:5000/api/game/sessions \
  -H "Content-Type: application/json" \
  -d '{"story_id": 2}'
```

## Example 3: Mystery Story

**Title**: The Vanishing Heirloom

**Lore**: You are a private detective hired to find Lady Ashworth's stolen diamond necklace. The theft occurred during her gala last night. Suspects include the butler, the jealous cousin, and a mysterious guest. You must interview suspects, search for clues, and solve the mystery before the thief escapes.

**Constraints**:
- Branching: 3-5 actions per step (multiple suspects to investigate)
- Depth: 6-10 steps (thorough investigation)

This would generate a detective story with interview options, clue gathering, and deduction actions.

## Tips for Best Results

### Writing Good Lore

1. **Be Specific**: Clearly describe the initial state, goal, and obstacles
2. **List Elements**: Mention characters, locations, items explicitly
3. **Define Constraints**: State what the player can and cannot do
4. **Set Tone**: Describe the atmosphere and style

### Choosing Constraints

- **Low Branching (2-3)**: Linear stories, focused narratives
- **High Branching (4-5)**: Open-world feel, exploration
- **Low Depth (3-5)**: Quick adventures, puzzles
- **High Depth (8-12)**: Epic quests, complex plots

### Working with the Reflection Agent

- Ask specific questions: "Why is this action invalid?"
- Request alternatives: "How else could I model this?"
- Seek clarification: "What does this error mean?"
- Get suggestions: "What's the best way to represent time?"

## Common Patterns

### Escape/Rescue Story
- Initial state: Trapped or threatened
- Goal: Reach safety or rescue someone
- Actions: Navigate, hide, collect items, solve puzzles

### Quest/Retrieval Story
- Initial state: Ordinary world
- Goal: Obtain special item
- Actions: Explore, overcome obstacles, interact with NPCs

### Mystery/Investigation
- Initial state: Crime occurred
- Goal: Identify culprit
- Actions: Interview, search, deduce, accuse

### Survival Story
- Initial state: Resources limited
- Goal: Survive duration or reach safety
- Actions: Manage resources, avoid dangers, craft items
