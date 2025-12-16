# QuestMaster Setup Guide

## Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 14+** and npm
- **OpenAI API Key** (required for LLM features)
- **Fast Downward** (optional, for PDDL validation)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

5. Run the backend:
```bash
python run.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Fast Downward Setup (Optional)

Fast Downward is used for PDDL validation. If not installed, basic syntax validation will be used instead.

### Installation

1. Download Fast Downward:
```bash
git clone https://github.com/aibasel/downward.git
cd downward
./build.py
```

2. Update `.env` in backend:
```bash
FAST_DOWNWARD_PATH=/path/to/downward/fast-downward.py
```

## Database

By default, SQLite is used for development. The database file will be created automatically at `backend/questmaster.db`.

For production, you can use PostgreSQL by updating the `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/questmaster
```

## Testing the Installation

1. Visit `http://localhost:3000`
2. Click "Create Story"
3. Fill in the form with your story idea
4. Click "Generate PDDL" to test OpenAI integration
5. Click "Validate PDDL" to test validation
6. Once validated, click "Play Story" to test the game interface

## Troubleshooting

### Backend won't start
- Check that Python 3.8+ is installed: `python --version`
- Ensure virtual environment is activated
- Verify all dependencies installed: `pip list`

### Frontend won't start
- Check that Node.js is installed: `node --version`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

### OpenAI errors
- Verify your API key is valid
- Check you have credits available in your OpenAI account
- Ensure the `OPENAI_API_KEY` is set in backend `.env`

### CORS errors
- Ensure backend is running on port 5000
- Check `CORS_ORIGINS` in backend `.env` includes `http://localhost:3000`
