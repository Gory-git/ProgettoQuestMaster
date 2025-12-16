# QuestMaster API Documentation

## Base URL
```
http://localhost:5000/api
```

## Endpoints

### Health Check

#### GET /health
Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "QuestMaster API",
  "version": "1.0.0"
}
```

#### GET /config
Get configuration status (for debugging).

**Response:**
```json
{
  "openai_configured": true,
  "dalle_enabled": false,
  "fast_downward_available": true,
  "database": "configured"
}
```

---

## Story Management (Phase 1)

### GET /stories
List all stories.

**Response:**
```json
{
  "stories": [
    {
      "id": 1,
      "title": "The Crystal Cave",
      "description": "An adventure story",
      "status": "validated",
      "is_validated": true,
      "created_at": "2025-12-16T10:00:00",
      ...
    }
  ]
}
```

### GET /stories/:id
Get a specific story by ID.

**Response:**
```json
{
  "id": 1,
  "title": "The Crystal Cave",
  "lore_content": "...",
  "pddl_domain": "...",
  "pddl_problem": "...",
  ...
}
```

### POST /stories
Create a new story.

**Request Body:**
```json
{
  "title": "The Crystal Cave",
  "description": "An epic adventure",
  "lore_content": "You are a brave adventurer...",
  "branching_factor_min": 2,
  "branching_factor_max": 4,
  "depth_min": 3,
  "depth_max": 10
}
```

**Response:** Created story object (201)

### PUT /stories/:id
Update story details.

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response:** Updated story object

### DELETE /stories/:id
Delete a story.

**Response:** 
```json
{
  "message": "Story deleted"
}
```

### POST /stories/:id/generate-pddl
Generate PDDL files for a story using LLM.

**Response:**
```json
{
  "message": "PDDL generated successfully",
  "story": { ... }
}
```

### POST /stories/:id/validate
Validate the PDDL files for a story.

**Response (Valid):**
```json
{
  "valid": true,
  "message": "PDDL is valid",
  "story": { ... }
}
```

**Response (Invalid):**
```json
{
  "valid": false,
  "errors": ["Error 1", "Error 2"],
  "reflection": {
    "analysis": "The Reflection Agent's analysis...",
    "suggestions": ["Fix 1", "Fix 2"],
    "severity": "medium"
  },
  "refinement_id": 1
}
```

### POST /stories/:id/refine
Refine PDDL based on validation errors.

**Request Body:**
```json
{
  "refinement_id": 1,
  "author_input": "Please fix the syntax errors"
}
```

**Response:**
```json
{
  "message": "PDDL refined successfully",
  "story": { ... }
}
```

### POST /stories/:id/chat
Interactive chat with the Reflection Agent.

**Request Body:**
```json
{
  "conversation_history": [
    {"role": "user", "content": "Can you help me with this?"},
    {"role": "assistant", "content": "Of course!"}
  ],
  "message": "How do I fix this error?"
}
```

**Response:**
```json
{
  "response": "To fix this error, you should..."
}
```

### GET /stories/:id/refinement-history
Get the refinement history for a story.

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "iteration": 1,
      "validation_errors": [...],
      "reflection_feedback": "...",
      "created_at": "2025-12-16T10:00:00"
    }
  ]
}
```

---

## Game Play (Phase 2)

### POST /game/sessions
Create a new game session.

**Request Body:**
```json
{
  "story_id": 1
}
```

**Response:**
```json
{
  "session": {
    "id": 1,
    "session_key": "uuid",
    "story_id": 1,
    ...
  },
  "narrative": "You stand at the entrance...",
  "image_url": "https://...",
  "available_actions": [
    {
      "id": 0,
      "action": "begin_adventure",
      "description": "Start your adventure",
      "display_text": "Begin Adventure"
    }
  ]
}
```

### GET /game/sessions/:id
Get game session details.

**Response:**
```json
{
  "session": {
    "id": 1,
    "story_id": 1,
    "steps_taken": 5,
    "is_completed": false,
    ...
  },
  "story": {
    "id": 1,
    "title": "The Crystal Cave",
    "description": "..."
  }
}
```

### POST /game/sessions/:id/action
Take an action in the game.

**Request Body:**
```json
{
  "action": "explore_north"
}
```

**Response:**
```json
{
  "session": { ... },
  "narrative": "You venture north and discover...",
  "image_url": "https://...",
  "available_actions": [...],
  "is_completed": false
}
```

### GET /game/sessions/:id/history
Get the narrative history of a session.

**Response:**
```json
{
  "session_id": 1,
  "narrative_history": [
    {
      "step": 1,
      "action": "explore_north",
      "narrative": "You venture north..."
    }
  ],
  "action_history": ["begin", "explore_north", ...]
}
```

### GET /game/sessions
List all game sessions, optionally filtered by story.

**Query Parameters:**
- `story_id` (optional): Filter by story ID

**Response:**
```json
{
  "sessions": [...]
}
```

### DELETE /game/sessions/:id
Delete a game session.

**Response:**
```json
{
  "message": "Session deleted"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error
