# 🤖 SlideForage - Backend Agent Engine

> Intelligent FastAPI-based agent that orchestrates PowerPoint presentation generation through a 5-phase agentic loop with MCP server integration.

**Status:** Production Ready | **Version:** 1.0.0 | **Framework:** FastAPI + Python

---

## 📋 Table of Contents

1. [What is the Agent?](#what-is-the-agent)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [The 5-Phase Agentic Loop](#the-5-phase-agentic-loop)
5. [API Endpoints](#api-endpoints)
6. [MCP Servers](#mcp-servers)
7. [Database Models](#database-models)
8. [Error Handling](#error-handling)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 What is the Agent?

The Agent Engine is the intelligent core of SlideForage. It:

1. **Receives user prompts** from the frontend
2. **Plans presentation structure** intelligently
3. **Orchestrates MCP servers** to execute the plan
4. **Handles errors gracefully** with retry logic
5. **Delivers complete PPTX files** to users

### Key Concept: Agentic Loop

The agent uses a **5-phase execution pipeline** (PLAN → CREATE → BUILD → THEME → SAVE) that ensures:
- ✅ Structured planning before execution
- ✅ Distributed computation across MCP servers
- ✅ Graceful error handling and degradation
- ✅ Professional, themed output

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **pip** (Python package manager)

### Installation Steps

#### Step 1: Create Virtual Environment
```bash
cd agent

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# (Optional) Update pip
pip install --upgrade pip
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**What gets installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - Database ORM
- `python-jose` & `bcrypt` - Authentication
- `python-pptx` - PowerPoint manipulation
- `duckduckgo-search` - Web search
- `mcp` - Model Context Protocol

#### Step 3: Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env  # Use your preferred editor
```

**Essential .env Variables:**
```env
HOST=0.0.0.0
PORT=8000
DEBUG=False
DATABASE_URL=sqlite:///./ppt_agent.db
SECRET_KEY=your-super-secret-key-change-in-production
MCP_SERVERS_PATH=../mcp/servers
```

#### Step 4: Initialize Database
```bash
python -c "from models import init_db; init_db()"

# Verify database created
ls -la ppt_agent.db
```

#### Step 5: Start the Server
```bash
# Method 1: Direct Python
python main.py

# Method 2: With Uvicorn (recommended for development)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### Step 6: Verify Installation
```bash
# In another terminal
curl http://localhost:8000/health

# Response:
# {"status":"healthy","message":"Auto-PPT Agent is running"}
```

#### Step 7: Access API Docs
```
Interactive Docs: http://localhost:8000/docs
Alternative Docs: http://localhost:8000/redoc
```

---

## ⚙️ Configuration

### Environment Variables

```env
# ===== SERVER CONFIGURATION =====
HOST=0.0.0.0                          # Bind address
PORT=8000                             # Port number
DEBUG=False                           # Debug mode (True for development)

# ===== DATABASE =====
DATABASE_URL=sqlite:///./ppt_agent.db # SQLite for dev
# For production, use PostgreSQL:
# DATABASE_URL=postgresql://user:pass@localhost/dbname

# ===== SECURITY (CRITICAL IN PRODUCTION!) =====
SECRET_KEY=your-super-secret-key     # JWT signing key
                                     # Generate new one: openssl rand -hex 32

# ===== MCP SERVERS =====
MCP_SERVERS_PATH=../mcp/servers      # Path to MCP server directory

# ===== OPTIONAL =====
HF_TOKEN=your-huggingface-token      # For accessing distilled models
```

### Production Checklist

**Security:**
- [ ] Change `SECRET_KEY` to a random, secure value
- [ ] Set `DEBUG=False`
- [ ] Use HTTPS/TLS (SSL certificate)
- [ ] Use environment variables for all secrets

**Database:**
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure database backups
- [ ] Set up connection pooling

**API:**
- [ ] Configure CORS properly (specify allowed origins)
- [ ] Set up rate limiting
- [ ] Enable request logging

**Operations:**
- [ ] Set up log rotation
- [ ] Configure monitoring & alerting
- [ ] Set up backup strategy
- [ ] Test disaster recovery

---

## 🔄 The 5-Phase Agentic Loop

The agent executes presentation generation in 5 distinct phases:

### Phase 1: PLANNING (1-2 seconds)

**What Happens:**
1. Agent receives user prompt: "Create 5-slide presentation on AI"
2. Agent uses LLM reasoning to generate ideal slide structure
3. Agent plans detailed outline with titles and bullet points

**Example Plan:**
```
Slide 1: Introduction to AI
  - Brief history
  - Definition & scope
  - Why important

Slide 2: AI Techniques
  - Machine Learning
  - Deep Learning
  - Neural Networks

Slide 3: Real-world Applications
  - Healthcare
  - Finance
  - Transportation

Slide 4: Challenges & Ethics
  - Privacy concerns
  - Bias in AI
  - Ethical considerations

Slide 5: Future of AI
  - Emerging trends
  - Impact on society
  - Call to action
```

**Why It Matters:**
- Ensures coherent presentation structure
- Prevents random/disconnected slide generation
- Meets requirement: "Agent must plan before executing"

**Code Location:** `agent_engine.py` Phase 1 section

---

### Phase 2: CREATE (< 1 second)

**What Happens:**
1. Agent calls MCP PPT Server: `create_presentation()`
2. PowerPoint file created in memory
3. Title slide added with main title and subtitle

**MCP Call Example:**
```json
{
  "tool": "create_presentation",
  "arguments": {
    "title": "Artificial Intelligence",
    "subtitle": "A comprehensive overview"
  }
}
```

**Result:**
- PowerPoint object ready for population
- Title slide created

**Code Location:** `agent_engine.py` Phase 2 section

---

### Phase 3: BUILD SLIDES (3-5 seconds for 5 slides)

**What Happens:**
For each slide in the plan:
1. Call MCP PPT Server: `add_slide()` - Add blank slide
2. (Optional) Call Web Search Server: `search_topic()` - Get real content
3. Call PPT Server: `write_text_to_slide()` - Write title and bullets
4. (Optional) Add image placeholder

**Detailed Example for Slide 2:**
```
Build Slide 2 ("AI Techniques"):
  1. add_slide(layout_type="title_and_content")
     → New blank slide added

  2. search_topic("AI Machine Learning Deep Learning Neural Networks")
     → Web results: "ML is subset of AI...", "Deep learning uses artificial neurons..."
     → Agent extracts and summarizes key points

  3. write_text_to_slide(
       slide_index=2,
       title="AI Techniques",
       content=[
         "Machine Learning: Learn patterns from data",
         "Deep Learning: Neural networks with multiple layers",
         "Natural Language Processing: Understand human language"
       ]
     )
     → Slide populated with content
```

**Graceful Error Handling:**
- If web search fails → Use planned content (continue normally)
- If one slide fails → Log error and continue with next slide
- Result: Partial presentation still delivered

**Code Location:** `agent_engine.py` Phase 3 section

---

### Phase 4: APPLY THEME (1 second)

**What Happens:**
1. Agent calls MCP Theme Server: `apply_theme()`
2. Consistent styling applied across all slides
3. Professional appearance guaranteed

**MCP Call:**
```json
{
  "tool": "apply_theme",
  "arguments": {
    "theme_name": "ocean"
  }
}
```

**Available Themes:**
- `default` - Professional blue
- `ocean` - Cool blue/teal
- `forest` - Natural green
- `sunset` - Warm orange
- `midnight` - Dark blue/purple

**Code Location:** `agent_engine.py` Phase 4 section

---

### Phase 5: SAVE & OUTPUT (< 1 second)

**What Happens:**
1. Generate timestamp-based filename: `presentation_YYYYMMDD_HHMMSS.pptx`
2. Call MCP PPT Server: `save_presentation()`
3. Save binary file to `outputs/` directory
4. Return file path to user

**MCP Call:**
```json
{
  "tool": "save_presentation",
  "arguments": {
    "file_path": "output/presentation_20240405_153042.pptx"
  }
}
```

**Result:**
- PPTX file saved to disk
- Path returned to frontend
- User can download

**Code Location:** `agent_engine.py` Phase 5 section

---

### Complete Execution Timeline

```
User Input: "Create 5-slide presentation on machine learning"

T+0s:    PHASE 1: PLANNING
         Agent generates slide structure plan

T+2s:    PHASE 2: CREATE
         PowerPoint file created in memory

T+3s:    PHASE 3: BUILD SLIDES
         Slide 1: Added (no search needed for intro)
         Slide 2: Added + web search executed
         Slide 3: Added + web search executed
         Slide 4: Added + web search executed
         Slide 5: Added (conclusion)

T+8s:    PHASE 4: APPLY THEME
         Theme applied to all slides

T+9s:    PHASE 5: SAVE
         File saved to outputs/

T+10s:   RESPONSE SENT
         Return: {file_path: "output/presentation_20240405_153042.pptx"}

[Total: ~10 seconds for complete generation]
```

---

## 📡 API Endpoints

Complete reference of all backend endpoints.

### Authentication Endpoints

#### 1. Register New User

**Endpoint:**
```http
POST /register HTTP/1.1
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password_123"
  }'
```

---

#### 2. Login User

**Endpoint:**
```http
POST /login HTTP/1.1
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password_123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password_123"
  }'

# Save token for future requests
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### PPT Generation Endpoints

#### 3. Create Presentation

**Endpoint:**
```http
POST /create-ppt HTTP/1.1
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "prompt": "Create a 5-slide presentation on machine learning for beginners"
}
```

**Response (200):**
```json
{
  "status": "success",
  "file_path": "output/presentation_20240405_153042.pptx",
  "num_slides": 5,
  "message": "Presentation created successfully"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/create-ppt" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a 5-slide presentation on the history of AI"
  }'
```

**What Happens Behind the Scenes:**
```
T+0s:   Request received
        Job created in database (status: pending)

T+1-2s: Phase 1: Agent plans structure

T+2-3s: Phase 2: PowerPoint created

T+3-8s: Phase 3: Slides built with web content

T+8-9s: Phase 4: Theme applied

T+9-10s: Phase 5: File saved

T+10s:  Response returned with file path
```

---

#### 4. Download Presentation

**Endpoint:**
```http
GET /download/presentation_20240405_153042.pptx HTTP/1.1
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response:** Binary PPTX file (downloaded to client machine)

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/download/presentation_20240405_153042.pptx" \
  -H "Authorization: Bearer $TOKEN" \
  -o my_presentation.pptx

# File saved as: my_presentation.pptx
```

---

#### 5. Get User's Job History

**Endpoint:**
```http
GET /jobs HTTP/1.1
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (200):**
```json
{
  "status": "success",
  "jobs": [
    {
      "id": "job-uuid-123",
      "prompt": "Create a 5-slide presentation on machine learning",
      "status": "completed",
      "created_at": "2024-04-05T15:30:42.123456",
      "file_path": "output/presentation_20240405_153042.pptx",
      "num_slides": 5
    },
    {
      "id": "job-uuid-456",
      "prompt": "Create presentation on Python",
      "status": "failed",
      "created_at": "2024-04-05T14:20:00.123456",
      "file_path": null,
      "error": "Web search service unavailable"
    }
  ]
}
```

**Job Status Values:**
- `pending` - Queued, not started yet
- `processing` - Currently generating
- `completed` - Successfully created, ready for download
- `failed` - Error occurred during creation

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/jobs" \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 6. Get Specific Job Status

**Endpoint:**
```http
GET /jobs/{job_id} HTTP/1.1
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (200):**
```json
{
  "status": "success",
  "job": {
    "id": "job-uuid-123",
    "prompt": "Create a 5-slide presentation on AI",
    "status": "completed",
    "progress": 100,
    "current_phase": "SAVE",
    "created_at": "2024-04-05T15:30:42",
    "completed_at": "2024-04-05T15:30:52",
    "file_path": "output/presentation_20240405_153042.pptx"
  }
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/jobs/job-uuid-123" \
  -H "Authorization: Bearer $TOKEN"
```

---

#### 7. Health Check

**Endpoint:**
```http
GET /health HTTP/1.1
```

**Response (200):**
```json
{
  "status": "healthy",
  "message": "SlideForage Agent is running"
}
```

**cURL Example:**
```bash
curl http://localhost:8000/health
```

---

## 🔗 MCP Servers

The agent communicates with 4 specialized MCP servers through the MCP client.

### How MCP Integration Works

```
Agent Engine
    ↓
MCP Client (mcp_client.py)
    ↓
[Startup MCP Servers as Subprocesses]
    ↓
┌─────────────────────────────────────────────────┐
│  4 MCP Servers (running in parallel)            │
├─────────────────────────────────────────────────┤
│  1. PPT Server       - PowerPoint manipulation  │
│  2. Web Search       - Content fetching         │
│  3. Filesystem       - File I/O                 │
│  4. Theme Server     - Styling                  │
└─────────────────────────────────────────────────┘
    ↓
[Servers respond to tool calls]
    ↓
Agent processes results
```

### Server Details

**See detailed MCP documentation:** [mcp/README.md](../mcp/README.md)

| Server | Location | Tools | Purpose |
|--------|----------|-------|---------|
| **1. PPT Server** | `mcp/servers/1.ppt_server.py` | 6 | PowerPoint creation |
| **2. Web Search** | `mcp/servers/2.web_search_server.py` | 2 | Web search & content |
| **3. Filesystem** | `mcp/servers/3.filesystem_server.py` | 4 | File operations |
| **4. Theme Server** | `mcp/servers/4.theme_server.py` | 4 | Styling & themes |

---

## 📊 Database Models

The agent uses SQLAlchemy ORM for database operations.

### Models Overview

#### 1. User Model

```python
class User(Base):
    __tablename__ = "users"

    id: str              # UUID primary key
    username: str        # Unique username
    email: str          # Unique email
    hashed_password: str # bcrypt hashed
    created_at: datetime # Account creation time
    updated_at: datetime # Last update

    # Relationships
    sessions: List[Session]  # User's sessions
    jobs: List[PPTJob]       # User's presentations
```

**Purpose:** Store user account information securely

---

#### 2. Session Model

```python
class Session(Base):
    __tablename__ = "sessions"

    id: str              # UUID primary key
    user_id: str         # Foreign key to User
    token: str          # JWT token
    created_at: datetime # Session start
    expires_at: datetime # Token expiration (24h)

    # Relationships
    user: User          # Back-reference to user
```

**Purpose:** Track active sessions and JWT tokens

---

#### 3. PPTJob Model

```python
class PPTJob(Base):
    __tablename__ = "ppt_jobs"

    id: str              # UUID primary key
    user_id: str         # Foreign key to User (owns this job)
    prompt: str         # User's original prompt
    status: str         # pending, processing, completed, failed
    file_path: str      # output/presentation_*.pptx
    num_slides: int     # Number of slides created
    error_message: str  # Error details if failed
    created_at: datetime # Job creation time
    started_at: datetime # Generation start
    completed_at: datetime # Generation completion

    # Relationships
    user: User          # Back-reference to user
```

**Purpose:** Track presentation generation jobs

---

## 🛡️ Error Handling

### Retry Logic

When calling MCP servers, the agent retries on failure:

```
Attempt 1: Call tool
  ├─ Success? → Return result
  └─ Fail? → Wait 1 second

Attempt 2: Call tool again
  ├─ Success? → Return result
  └─ Fail? → Wait 2 seconds

Attempt 3: Final attempt
  ├─ Success? → Return result
  └─ Fail? → Return error to user
```

**Configuration:**
- Max retries: 3
- Initial backoff: 1 second
- Max backoff: 2 seconds
- Timeout per call: 30 seconds

---

### Graceful Degradation

The agent gracefully handles failures at each phase:

```
Scenario 1: Web Search Fails
  ├─ User: "Create presentation on AI"
  ├─ Agent tries web search
  ├─ Web search times out
  ├─ Agent continues with planned content
  └─ Result: SUCCESS (with planned bullets)

Scenario 2: Single Slide Fails
  ├─ Building 5 slides...
  ├─ Slide 3 fails
  ├─ Agent logs error and continues
  └─ Result: 4 good slides + 1 placeholder

Scenario 3: Theme Fails (non-critical)
  ├─ All slides created successfully
  ├─ Theme application fails
  ├─ Agent continues without theme
  └─ Result: SUCCESS (unthemed presentation)

Scenario 4: File Save Fails (critical)
  ├─ All slides created and themed
  ├─ Save operation fails
  └─ Result: FAILURE (data lost)
```

---

## 🚀 Deployment

### Production Deployment

#### Pre-deployment Checklist

**Security:**
- [ ] Change SECRET_KEY to random value
  ```bash
  openssl rand -hex 32
  ```
- [ ] Set DEBUG=False
- [ ] Enable HTTPS/TLS
- [ ] Use environment variables for secrets
- [ ] Configure CORS for specific origins

**Database:**
- [ ] Migrate to PostgreSQL
  ```bash
  DATABASE_URL=postgresql://user:password@host/dbname
  ```
- [ ] Configure connection pooling
- [ ] Set up automated backups
- [ ] Test backup restoration

**Deployment:**
- [ ] Use production ASGI server (Gunicorn)
- [ ] Set up process manager (systemd, supervisor)
- [ ] Configure logging
- [ ] Set up monitoring & alerting

---

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build & Run:**
```bash
docker build -t slideforge-agent .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=... \
  slideforge-agent
```

---

### Kubernetes Deployment

**K8s Manifest (deployment.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: slideforge-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: slideforge-agent
  template:
    metadata:
      labels:
        app: slideforge-agent
    spec:
      containers:
      - name: agent
        image: slideforge-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: secret-key
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Error: "Database locked"

**Cause:** SQLite conflict with concurrent writes

**Solution:**
- Development: Restart server
- Production: Use PostgreSQL
  ```bash
  DATABASE_URL=postgresql://user:pass@localhost/dbname
  ```

---

### Error: "MCP server not responding"

**Solution:**
```bash
# Check if MCP servers started
ps aux | grep python | grep ppt_server

# Run server manually to see errors
python ../mcp/servers/1.ppt_server.py
```

---

### Error: "Token expired"

**Cause:** JWT token exceeded 24-hour validity

**Solution:** User must login again to get new token

---

### Slow Presentation Generation

**Expected Timeline (5 slides):**
```
Planning:     1-2s (agent reasoning)
Creating:     <1s  (initialize file)
Building:     3-5s (add slides + web search)
Theming:      1s   (apply styling)
Saving:       <1s  (write to disk)
─────────────────
Total:        8-12s
```

**If slower:** Check internet connection (web search may be bottleneck)

---

## 📚 File Reference

### Core Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application & routes |
| `agent_engine.py` | 5-phase agentic loop logic |
| `mcp_client.py` | MCP server communication |
| `models.py` | SQLAlchemy database models |
| `auth.py` | JWT & password utilities |
| `config.py` | Configuration loading |
| `db.py` | Database operations |

---

## 📞 Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review application logs: `DEBUG=True python main.py`
3. Check database: `sqlite3 ppt_agent.db`
4. Review [Root README](../README.md) for system overview

---

**Ready to generate amazing presentations!** 🚀

See [Frontend README](../frontend/README.md) for client-side documentation.
