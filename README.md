# QuestMaster - Interactive Story Generation System

![QuestMaster](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Architecture](#project-architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**QuestMaster** is a comprehensive two-phase system for creating and experiencing interactive narrative adventures. It combines classical AI planning (PDDL) with modern Large Language Models (LLMs) to enable authors to create logically consistent, branching stories and players to experience dynamic, choice-driven narratives.

### Phase 1: Story Generation
Authors create interactive stories by providing a lore document. The system uses GPT-4 to generate PDDL (Planning Domain Definition Language) files that model the adventure as a planning problem. A Reflection Agent assists with validation and refinement, ensuring logical consistency.

### Phase 2: Interactive Play
Players experience the stories through a web interface that dynamically generates narrative text and presents meaningful choices at each step. Optional DALL-E integration provides visual illustrations for each scene.

---

## Features

### Phase 1: Story Generation

- **LLM-Powered PDDL Generation**
  - Automatic generation of domain and problem files from lore
  - Commented PDDL for clarity and understanding
  - Customizable branching factors and story depth

- **Intelligent Validation**
  - Syntax validation for PDDL correctness
  - Fast Downward integration for plan verification
  - Real-time feedback on logical consistency

- **Reflection Agent**
  - AI-powered error analysis
  - Specific suggestions for fixes
  - Interactive chat interface for guidance
  - Iterative refinement loop

- **Story Management**
  - Create, edit, and organize stories
  - Track validation status
  - Version history for refinements

### Phase 2: Interactive Play

- **Dynamic Narrative Generation**
  - Context-aware storytelling with GPT-4
  - Immersive second-person narration
  - Responsive to player choices

- **Action Selection**
  - Dynamically generated choices from PDDL state
  - Clear action descriptions
  - Branching paths based on decisions

- **Visual Enhancement**
  - Optional DALL-E image generation
  - Scene-specific illustrations
  - Atmospheric visual storytelling

- **Session Management**
  - Save and resume game sessions
  - Track action and narrative history
  - Progress tracking

---

## Project Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│              Material-UI + React Router                      │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────────┐
│                    Backend (Flask API)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │PDDL Service  │  │Reflection Svc│  │Narrative Svc │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   External Services                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  OpenAI API  │  │Fast Downward │  │  Database    │      │
│  │  (GPT-4)     │  │  (PDDL)      │  │  (SQLite/    │      │
│  │  (DALL-E)    │  │              │  │  PostgreSQL) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | React.js 18 | UI framework with hooks |
| **UI Library** | Material-UI (MUI) | Component library |
| **Routing** | React Router 6 | Client-side routing |
| **Build Tool** | Vite | Fast development and builds |
| **Backend** | Flask 3.0 | Python web framework |
| **Database** | SQLite / PostgreSQL | Data persistence |
| **ORM** | SQLAlchemy | Database abstraction |
| **LLM** | OpenAI GPT-4 | Story and PDDL generation |
| **Image Gen** | DALL-E 3 | Scene illustrations |
| **Planner** | Fast Downward | PDDL validation |
| **Containerization** | Docker | Deployment packaging |

### Directory Structure

```
ProgettoQuestMaster/
├── backend/                    # Flask backend application
│   ├── app/
│   │   ├── __init__.py        # App factory
│   │   ├── models/            # SQLAlchemy models
│   │   │   └── story.py       # Story, RefinementHistory, GameSession
│   │   ├── services/          # Business logic
│   │   │   ├── pddl_service.py        # PDDL generation
│   │   │   ├── validation_service.py  # PDDL validation
│   │   │   ├── reflection_service.py  # Reflection agent
│   │   │   └── narrative_service.py   # Narrative generation
│   │   └── routes/            # API endpoints
│   │       ├── story_routes.py        # Phase 1 endpoints
│   │       ├── game_routes.py         # Phase 2 endpoints
│   │       └── health_routes.py       # Health checks
│   ├── config/                # Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment template
│   └── run.py                 # Application entry point
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   │   ├── HomePage.jsx
│   │   │   ├── StoryListPage.jsx
│   │   │   ├── StoryCreationPage.jsx
│   │   │   ├── StoryDetailPage.jsx
│   │   │   └── GamePlayPage.jsx
│   │   ├── services/          # API client
│   │   │   └── api.js
│   │   ├── App.jsx            # Root component
│   │   └── main.jsx           # Entry point
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   └── .env.example           # Environment template
├── docker/                    # Docker configuration
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docs/                      # Documentation
│   ├── SETUP.md              # Setup guide
│   ├── API.md                # API documentation
│   └── ARCHITECTURE.md       # Architecture details
├── setup.sh                   # Automated setup script
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

---

## Prerequisites

Before getting started, ensure you have the following installed:

- **Python 3.8+** (for backend)
- **Node.js 14+** and npm (for frontend)
- **OpenAI API Key** (required for GPT-4 and DALL-E)
- **Fast Downward** (optional, for PDDL validation)
- **Git** for version control

### OpenAI API Access
You'll need an OpenAI API key with access to:
- GPT-4 (for PDDL and narrative generation)
- DALL-E 3 (optional, for image generation)

Get your API key at: https://platform.openai.com/api-keys

---

## Quick Start

Use the automated setup script:

```bash
# Clone the repository
git clone https://github.com/Gory-git/ProgettoQuestMaster.git
cd ProgettoQuestMaster

# Run setup script
chmod +x setup.sh
./setup.sh

# Edit backend/.env and add your OPENAI_API_KEY

# Start backend (Terminal 1)
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py

# Start frontend (Terminal 2)
cd frontend
npm run dev
```

Visit **http://localhost:3000** to use the application.

---

## Detailed Setup

### Backend Setup (Python/Flask)

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the backend
python run.py
```

Backend will run on **http://localhost:5000**

#### Backend Environment Variables (.env)

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Database
DATABASE_URL=sqlite:///questmaster.db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# DALL-E (Optional)
DALLE_ENABLED=False
DALLE_MODEL=dall-e-3

# Fast Downward (Optional)
FAST_DOWNWARD_PATH=/path/to/fast-downward
```

### Frontend Setup (React)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start development server
npm run dev
```

Frontend will run on **http://localhost:3000**

#### Frontend Environment Variables (.env)

```env
VITE_API_URL=http://localhost:5000/api
```

### Docker Setup (Optional)

For containerized deployment:

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

---

## Usage Guide

### Creating Your First Story

1. **Visit the Application**
   - Open http://localhost:3000
   - Click "Create Story" or navigate to `/create`

2. **Enter Story Details**
   - **Title**: Give your story a memorable name
   - **Description**: Brief summary (optional)
   - **Lore Content**: Describe your story world:
     - Initial state (where does it begin?)
     - Goal (what must be achieved?)
     - Obstacles and challenges
     - Characters, locations, items

3. **Set Constraints**
   - **Branching Factor**: Min/max actions per step (e.g., 2-4)
   - **Depth**: Min/max steps to complete (e.g., 3-10)

4. **Generate PDDL**
   - Click "Generate PDDL"
   - Wait for GPT-4 to create domain and problem files
   - Review the generated PDDL with comments

5. **Validate**
   - Click "Validate PDDL"
   - If errors occur:
     - Review Reflection Agent's analysis
     - Chat with agent for guidance
     - Use "Auto-Fix" or manually refine
     - Re-validate

6. **Play Your Story**
   - Once validated, click "Play Story"
   - Make choices and experience your creation!

### Playing an Interactive Story

1. **Browse Stories**
   - Navigate to "Stories" page
   - View all validated stories

2. **Start a Game**
   - Click "Play" on any validated story
   - Read the opening narrative

3. **Make Choices**
   - Read the current situation
   - View available actions
   - Click an action to proceed

4. **Complete the Quest**
   - Progress through the story
   - Each choice affects the narrative
   - Reach the goal to complete

### Using the Reflection Agent

The Reflection Agent helps you refine your PDDL:

1. **Automatic Analysis**
   - Triggered when validation fails
   - Provides error analysis and suggestions

2. **Interactive Chat**
   - Click "Chat with Agent" on story detail page
   - Ask questions about your story
   - Get guidance on fixing issues

---

## API Documentation

Full API documentation is available in [docs/API.md](docs/API.md).

### Key Endpoints

#### Story Management (Phase 1)
- `POST /api/stories` - Create new story
- `GET /api/stories` - List all stories
- `GET /api/stories/:id` - Get story details
- `POST /api/stories/:id/generate-pddl` - Generate PDDL
- `POST /api/stories/:id/validate` - Validate PDDL
- `POST /api/stories/:id/refine` - Refine PDDL
- `POST /api/stories/:id/chat` - Chat with Reflection Agent

#### Game Play (Phase 2)
- `POST /api/game/sessions` - Start game session
- `GET /api/game/sessions/:id` - Get session state
- `POST /api/game/sessions/:id/action` - Take action
- `GET /api/game/sessions/:id/history` - Get history

### Example: Create and Play a Story

```bash
# 1. Create story
curl -X POST http://localhost:5000/api/stories \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Crystal Cave",
    "lore_content": "You seek a magical crystal...",
    "branching_factor_min": 2,
    "branching_factor_max": 4,
    "depth_min": 3,
    "depth_max": 8
  }'

# 2. Generate PDDL (story_id = 1)
curl -X POST http://localhost:5000/api/stories/1/generate-pddl

# 3. Validate PDDL
curl -X POST http://localhost:5000/api/stories/1/validate

# 4. Start game
curl -X POST http://localhost:5000/api/game/sessions \
  -H "Content-Type: application/json" \
  -d '{"story_id": 1}'

# 5. Take action (session_id = 1)
curl -X POST http://localhost:5000/api/game/sessions/1/action \
  -H "Content-Type: application/json" \
  -d '{"action": "explore_north"}'
```

---

## Development

### Project Structure

- **Backend**: Flask application with service-oriented architecture
- **Frontend**: React with functional components and hooks
- **Database**: SQLAlchemy ORM with SQLite (dev) or PostgreSQL (prod)

### Running in Development Mode

```bash
# Backend with auto-reload
cd backend
source venv/bin/activate
export FLASK_ENV=development
python run.py

# Frontend with hot reload
cd frontend
npm run dev
```

### Code Style

#### Python (Backend)
- Follow PEP 8 style guide
- Use docstrings for functions and classes
- Type hints recommended

#### JavaScript (Frontend)
- ESLint configuration included
- Functional components with hooks
- Material-UI for consistent styling

### Adding New Features

1. **New Service** (Backend)
   - Create service in `backend/app/services/`
   - Add routes in `backend/app/routes/`
   - Register blueprint in `backend/app/__init__.py`

2. **New Page** (Frontend)
   - Create component in `frontend/src/pages/`
   - Add route in `frontend/src/App.jsx`
   - Update navigation as needed

---

## Deployment

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose -f docker/docker-compose.yml up -d

# Scale services
docker-compose -f docker/docker-compose.yml up -d --scale backend=3
```

### Manual Deployment

#### Backend (Production)

```bash
# Install production dependencies
pip install -r requirements.txt gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

#### Frontend (Production)

```bash
# Build for production
npm run build

# Serve with nginx or similar
# Build output is in frontend/dist/
```

### Environment Variables (Production)

```env
# Backend
FLASK_ENV=production
SECRET_KEY=<strong-secret-key>
DATABASE_URL=postgresql://user:pass@host:5432/questmaster
OPENAI_API_KEY=<your-key>
DALLE_ENABLED=True
```

---

## Troubleshooting

### Common Issues

#### OpenAI API Errors

**Problem**: "Authentication failed" or rate limit errors

**Solutions:**
- Verify API key is correct in `.env`
- Check OpenAI account has credits
- Ensure you have access to GPT-4 model
- Rate limits: Add delays between requests

#### PDDL Validation Fails

**Problem**: Validation always fails even with correct PDDL

**Solutions:**
- If Fast Downward not installed, only syntax checking runs
- Install Fast Downward for full validation
- Check FAST_DOWNWARD_PATH in `.env` is correct
- Basic syntax validation still works without Fast Downward

#### Frontend Can't Connect to Backend

**Problem**: API calls fail with network errors

**Solutions:**
- Ensure backend is running on port 5000
- Check VITE_API_URL in frontend `.env`
- Verify CORS_ORIGINS in backend `.env` includes frontend URL
- Check firewall settings

#### Database Errors

**Problem**: "Table doesn't exist" or connection errors

**Solutions:**
- Database is created automatically on first run
- For PostgreSQL, ensure database exists and credentials are correct
- Check DATABASE_URL format in `.env`
- For SQLite, ensure write permissions in backend directory

### Debug Mode

Enable detailed logging:

```bash
# Backend
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG
python run.py

# View frontend console
# Open browser DevTools (F12)
```

---

## Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Test thoroughly
5. Commit changes (`git commit -m 'Add AmazingFeature'`)
6. Push to branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Development Guidelines

- Follow existing code style and conventions
- Add comments for complex logic
- Update documentation for new features
- Write clear commit messages
- Test your changes before submitting

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support & Contact

- **Issues**: [GitHub Issues](https://github.com/Gory-git/ProgettoQuestMaster/issues)
- **Documentation**: [docs/](docs/)
- **Email**: support@questmaster.io

---

## Acknowledgments

- OpenAI for GPT-4 and DALL-E APIs
- Fast Downward planning system
- React and Flask communities
- All contributors and supporters

---

**Built with ❤️ for interactive storytelling**

**Last Updated**: 2025-12-16  
**Version**: 1.0.0  
**Maintained By**: Gory-git
