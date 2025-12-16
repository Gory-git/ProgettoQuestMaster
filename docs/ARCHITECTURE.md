# QuestMaster Architecture

## System Overview

QuestMaster is a two-phase system for creating and playing interactive narrative experiences using PDDL planning and Large Language Models (LLMs).

```
┌─────────────────────────────────────────────────────────────┐
│                     Phase 1: Story Creation                 │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐              │
│  │   Lore   │──▶│   LLM    │──▶│   PDDL   │              │
│  │  Input   │   │Generator │   │  Files   │              │
│  └──────────┘   └──────────┘   └──────────┘              │
│                       │                │                    │
│                       ▼                ▼                    │
│                  ┌──────────┐   ┌──────────┐              │
│                  │Validator │   │Reflection│              │
│                  │(F.Down.) │◀─▶│  Agent   │              │
│                  └──────────┘   └──────────┘              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Phase 2: Interactive Play                 │
│                                                             │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐              │
│  │  PDDL    │──▶│ Action   │──▶│Narrative │              │
│  │ Planner  │   │Selection │   │Generator │              │
│  └──────────┘   └──────────┘   └──────────┘              │
│                                      │                      │
│                                      ▼                      │
│                                 ┌──────────┐              │
│                                 │ DALL-E   │              │
│                                 │ Images   │              │
│                                 └──────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Backend (Python/Flask)

#### Services
- **PDDLGenerationService**: Generates PDDL domain and problem files from lore using GPT-4
- **PDDLValidationService**: Validates PDDL syntax and solvability (Fast Downward integration)
- **ReflectionAgentService**: Analyzes validation errors and provides refinement suggestions
- **NarrativeService**: Generates narrative text and optional images (DALL-E) during gameplay

#### Models
- **Story**: Stores story metadata, lore, PDDL files, validation status
- **RefinementHistory**: Tracks PDDL refinement iterations and feedback
- **GameSession**: Manages active game sessions with state and history

#### Routes
- **story_routes**: Phase 1 endpoints (create, generate, validate, refine, chat)
- **game_routes**: Phase 2 endpoints (sessions, actions, narrative)
- **health_routes**: Health check and configuration

### Frontend (React)

#### Pages
- **HomePage**: Landing page with feature overview
- **StoryListPage**: Browse and manage stories
- **StoryCreationPage**: Create new stories with lore input
- **StoryDetailPage**: View/edit story, generate/validate PDDL, chat with agent
- **GamePlayPage**: Interactive gameplay with narrative and choices

#### Services
- **api.js**: Axios-based API client for backend communication

### Database (SQLite/PostgreSQL)

#### Schema
```sql
stories
  - id, title, description
  - lore_content
  - branching_factor_min/max, depth_min/max
  - pddl_domain, pddl_problem
  - is_validated, status
  - created_at, updated_at

refinement_history
  - id, story_id
  - iteration, pddl_version
  - validation_errors, reflection_feedback
  - author_response, created_at

game_sessions
  - id, story_id, session_key
  - current_state, action_history, narrative_history
  - is_completed, steps_taken
  - started_at, last_action_at, completed_at
```

## Workflows

### Phase 1: Story Generation Workflow

1. **Author creates story**
   - Inputs title, description, lore
   - Sets constraints (branching factor, depth)

2. **PDDL Generation**
   - LLM generates domain file (types, predicates, actions)
   - LLM generates problem file (objects, init state, goal)
   - Each line includes descriptive comments

3. **Validation**
   - Syntax validation (parentheses, structure)
   - Fast Downward validation (if available)
   - Plan existence check

4. **Refinement Loop** (if validation fails)
   - Reflection Agent analyzes errors
   - Provides suggestions for fixes
   - Author can chat with agent for guidance
   - LLM refines PDDL based on feedback
   - Loop repeats until valid

5. **Story Ready**
   - PDDL validated and marked ready
   - Can be played in Phase 2

### Phase 2: Interactive Play Workflow

1. **Start Game Session**
   - Create session for validated story
   - Initialize PDDL state
   - Generate initial narrative

2. **Game Loop**
   - Display narrative text
   - Show available actions (from PDDL planner)
   - Optionally show generated image
   - Player selects action

3. **Action Processing**
   - Apply action to PDDL state
   - Check if goal reached
   - Generate narrative for new state
   - Get next available actions

4. **Game Completion**
   - When goal reached, mark session complete
   - Show completion message
   - Allow replay or return to library

## Technology Stack

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM
- **OpenAI API**: GPT-4 for generation, DALL-E for images
- **Fast Downward**: PDDL planner (optional)

### Frontend
- **React 18**: UI framework
- **React Router**: Navigation
- **Material-UI**: Component library
- **Axios**: HTTP client
- **Vite**: Build tool

### Database
- **SQLite**: Development
- **PostgreSQL**: Production

## Security Considerations

- API keys stored in environment variables
- No client-side API key exposure
- Input validation on all endpoints
- SQL injection protection via ORM
- CORS configuration for frontend

## Scalability

- Stateless API design
- Database indexing on frequently queried fields
- Session management for long-running games
- Optional Redis caching (future enhancement)
- Horizontal scaling via load balancer

## Future Enhancements

- Multi-user support with authentication
- Story sharing and marketplace
- Advanced PDDL features (temporal, numeric)
- Real-time collaborative editing
- Voice narration
- Save/load game states
- Achievement system
