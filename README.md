# QuestMaster - Quest Management System

![QuestMaster](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Architecture](#project-architecture)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**QuestMaster** is a comprehensive quest and task management system designed to streamline workflow management, goal tracking, and collaborative project execution. It provides users with tools to create, manage, prioritize, and monitor quests (tasks) with advanced filtering, progress tracking, and team collaboration features.

The system is built with a modern architecture supporting scalability, security, and user-friendly interfaces.

---

## Features

### Core Features

- **Quest Management**
  - Create, edit, and delete quests
  - Priority levels (Low, Medium, High, Critical)
  - Status tracking (Open, In Progress, Completed, Blocked, On Hold)
  - Due date management and deadline alerts
  - Quest descriptions and detailed notes

- **Task Organization**
  - Category/Tag-based organization
  - Hierarchical quest structure (parent-child relationships)
  - Milestone-based planning
  - Sprint management

- **Progress Tracking**
  - Real-time progress indicators
  - Completion percentage calculations
  - Activity timeline and history
  - Performance analytics and reporting

- **User Management**
  - Role-based access control (Admin, Manager, User)
  - User authentication and authorization
  - Profile management
  - Team assignment and collaboration

- **Advanced Filtering & Search**
  - Filter by status, priority, assignee, due date
  - Full-text search functionality
  - Saved filters and custom views
  - Sorting options

- **Notifications & Alerts**
  - Real-time notifications
  - Email alerts for deadlines
  - Activity updates
  - Reminder system

- **Reporting & Analytics**
  - Quest completion statistics
  - Performance dashboards
  - Timeline reports
  - Team productivity metrics

---

## Project Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│              (React/Vue + UI Components)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                     API Gateway                              │
│            (Request Routing & Authentication)               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    Backend Services                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Quest Service │  │User Service  │  │Report Service│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Data Access Layer                          │
│              (ORM & Database Queries)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                     Database Layer                           │
│         (PostgreSQL/MySQL + Data Persistence)               │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | React.js / Vue.js |
| **Backend** | Node.js / Python (Flask/Django) |
| **Database** | PostgreSQL / MySQL |
| **API** | RESTful API / GraphQL |
| **Authentication** | JWT / OAuth 2.0 |
| **Caching** | Redis |
| **Message Queue** | RabbitMQ / Kafka |
| **Containerization** | Docker |
| **Orchestration** | Kubernetes |

### Directory Structure

```
ProgettoQuestMaster/
├── frontend/                   # Frontend application
│   ├── public/
│   ├── src/
│   │   ├── components/        # React/Vue components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API service calls
│   │   ├── store/             # State management
│   │   └── styles/            # CSS/SCSS files
│   └── package.json
├── backend/                    # Backend API server
│   ├── app/
│   │   ├── controllers/       # Request handlers
│   │   ├── models/            # Data models
│   │   ├── services/          # Business logic
│   │   ├── middleware/        # Custom middleware
│   │   └── routes/            # API routes
│   ├── config/                # Configuration files
│   ├── migrations/            # Database migrations
│   ├── tests/                 # Unit & integration tests
│   └── requirements.txt
├── database/                  # Database scripts
│   ├── schema/
│   └── seeds/
├── docker/                    # Docker files
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/                      # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
└── README.md
```

---

## Prerequisites

Before getting started, ensure you have the following installed:

- **Node.js** v14+ or **Python** 3.8+
- **npm** v6+ or **pip** 3+
- **Docker** v20+ (optional, for containerized setup)
- **PostgreSQL** v12+ or **MySQL** v8+
- **Git** for version control
- **Postman** or similar tool for API testing (optional)

### Optional Tools

- **Redis** for caching
- **Docker Compose** for multi-container orchestration
- **VS Code** or your preferred IDE

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Gory-git/ProgettoQuestMaster.git
cd ProgettoQuestMaster
```

### 2. Backend Setup (Node.js/Express)

```bash
cd backend

# Install dependencies
npm install

# Create environment configuration file
cp .env.example .env

# Edit .env with your settings
nano .env

# Run database migrations
npm run migrate

# Start the backend server
npm start
```

#### Backend .env Template

```env
NODE_ENV=development
PORT=5000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=questmaster
DB_USER=postgres
DB_PASSWORD=your_password
JWT_SECRET=your_jwt_secret_key
REDIS_URL=redis://localhost:6379
API_BASE_URL=http://localhost:5000
LOG_LEVEL=debug
```

### 3. Frontend Setup (React)

```bash
cd frontend

# Install dependencies
npm install

# Create environment configuration file
cp .env.example .env

# Edit .env with your settings
nano .env

# Start the development server
npm start
```

#### Frontend .env Template

```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_API_TIMEOUT=30000
REACT_APP_ENV=development
```

### 4. Database Setup

#### Option A: Using PostgreSQL

```bash
# Create database
psql -U postgres -c "CREATE DATABASE questmaster;"

# Run migrations from backend directory
npm run migrate

# Seed initial data (optional)
npm run seed
```

#### Option B: Using Docker

```bash
# Build and start all services
docker-compose up -d

# Run migrations
docker-compose exec backend npm run migrate

# Seed initial data
docker-compose exec backend npm run seed
```

### 5. Verify Installation

```bash
# Test backend
curl http://localhost:5000/api/health

# Test frontend
# Navigate to http://localhost:3000 in your browser
```

---

## Configuration

### Environment Variables

The application uses environment variables for configuration. Key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment mode (development/production/test) | development |
| `PORT` | Backend server port | 5000 |
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `JWT_SECRET` | Secret key for JWT tokens | - |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379 |
| `LOG_LEVEL` | Logging level (debug/info/warn/error) | info |

### Database Configuration

Database configuration is managed in `backend/config/database.js`:

```javascript
module.exports = {
  development: {
    host: process.env.DB_HOST,
    port: process.env.DB_PORT,
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
  },
  // ... other environments
};
```

---

## Usage

### Running the Application

#### Development Mode

```bash
# Terminal 1: Start backend
cd backend
npm run dev

# Terminal 2: Start frontend
cd frontend
npm start
```

#### Production Mode

```bash
# Build frontend
cd frontend
npm run build

# Start backend with production settings
cd backend
NODE_ENV=production npm start
```

### Key Operations

#### Create a New Quest

1. Navigate to Dashboard
2. Click "New Quest" button
3. Fill in quest details:
   - Title (required)
   - Description
   - Priority level
   - Due date
   - Assignee
   - Categories/Tags
4. Click "Create"

#### Filter and Search Quests

- Use the sidebar filters for quick filtering
- Use the search bar for full-text search
- Combine multiple filters for advanced search

#### Track Progress

- View quest status in the quest list
- Click on a quest to view detailed progress
- Update progress percentage in quest details

---

## API Documentation

### Base URL

```
http://localhost:5000/api/v1
```

### Authentication

All requests require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Main Endpoints

#### Quests

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/quests` | List all quests |
| GET | `/quests/:id` | Get quest details |
| POST | `/quests` | Create new quest |
| PUT | `/quests/:id` | Update quest |
| DELETE | `/quests/:id` | Delete quest |
| PATCH | `/quests/:id/status` | Update quest status |

#### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login |
| GET | `/users/:id` | Get user profile |
| PUT | `/users/:id` | Update user profile |
| POST | `/auth/logout` | User logout |

#### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/summary` | Get summary report |
| GET | `/reports/quests` | Get quest statistics |
| GET | `/reports/team` | Get team metrics |

### Example Requests

#### Get All Quests

```bash
curl -X GET http://localhost:5000/api/v1/quests \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json"
```

#### Create a Quest

```bash
curl -X POST http://localhost:5000/api/v1/quests \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete Project Documentation",
    "description": "Write comprehensive documentation for QuestMaster",
    "priority": "high",
    "dueDate": "2025-12-31",
    "assigneeId": "user123"
  }'
```

---

## Database Schema

### Core Tables

#### Quests Table

```sql
CREATE TABLE quests (
  id UUID PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(50) DEFAULT 'open',
  priority VARCHAR(50) DEFAULT 'medium',
  assignee_id UUID REFERENCES users(id),
  created_by UUID REFERENCES users(id),
  due_date TIMESTAMP,
  completed_date TIMESTAMP,
  progress_percentage INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Users Table

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'user',
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Quest_History Table

```sql
CREATE TABLE quest_history (
  id UUID PRIMARY KEY,
  quest_id UUID REFERENCES quests(id),
  change_type VARCHAR(50),
  old_value TEXT,
  new_value TEXT,
  changed_by UUID REFERENCES users(id),
  changed_at TIMESTAMP DEFAULT NOW()
);
```

---

## Development

### Setting Up Development Environment

```bash
# Install development dependencies
cd backend
npm install --save-dev nodemon jest supertest

# Start development server with auto-reload
npm run dev
```

### Code Style & Linting

```bash
# Run ESLint
npm run lint

# Fix linting issues
npm run lint:fix

# Format code with Prettier
npm run format
```

### Git Workflow

1. Create a feature branch: `git checkout -b feature/feature-name`
2. Make your changes
3. Commit: `git commit -m "feat: add feature description"`
4. Push: `git push origin feature/feature-name`
5. Create a Pull Request

---

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- tests/quests.test.js

# Watch mode
npm test -- --watch
```

### Test Structure

```
backend/
├── tests/
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data
```

### Example Test

```javascript
describe('Quest Service', () => {
  it('should create a new quest', async () => {
    const quest = await questService.create({
      title: 'Test Quest',
      priority: 'high'
    });
    expect(quest.id).toBeDefined();
    expect(quest.title).toBe('Test Quest');
  });
});
```

---

## Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t questmaster:latest .

# Run container
docker run -p 5000:5000 questmaster:latest

# Using docker-compose
docker-compose -f docker/docker-compose.yml up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes configurations
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Scale deployment
kubectl scale deployment/questmaster --replicas=3
```

### Heroku Deployment

```bash
# Login to Heroku
heroku login

# Create app
heroku create questmaster

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## Troubleshooting

### Common Issues

#### Issue: Database Connection Failed

**Solution:**
```bash
# Check PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Verify connection string in .env
# Ensure database exists
psql -U postgres -l
```

#### Issue: Port Already in Use

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

#### Issue: Authentication Token Expired

**Solution:**
- Request a new token by logging in again
- Check JWT_SECRET matches in .env

#### Issue: Frontend Cannot Connect to Backend

**Solution:**
```bash
# Verify REACT_APP_API_URL in .env
# Check backend is running: curl http://localhost:5000/api/health
# Check CORS settings in backend
```

### Debug Mode

```bash
# Enable debug logging
DEBUG=questmaster:* npm start

# Verbose output
NODE_DEBUG=* npm start
```

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow [Node.js Best Practices](https://nodejs.org/en/docs/guides/nodejs-best-practices/)
- Write unit tests for new features
- Update documentation
- Maintain code style consistency
- Use meaningful commit messages

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support & Contact

- **Issues**: [GitHub Issues](https://github.com/Gory-git/ProgettoQuestMaster/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Gory-git/ProgettoQuestMaster/discussions)
- **Email**: support@questmaster.io

---

## Changelog

### Version 1.0.0 (2025-12-15)
- Initial release
- Core quest management features
- User authentication and authorization
- Progress tracking and reporting
- Real-time notifications

---

## Acknowledgments

- Team members and contributors
- Open-source libraries and frameworks
- Community support

---

**Last Updated**: 2025-12-15
**Maintained By**: Gory-git
