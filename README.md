# SlideForage - AI-Powered Presentation Generation System

> Intelligent full-stack platform that autonomously creates professional PowerPoint presentations from natural language prompts using an agentic architecture with Model Context Protocol (MCP) integration.

**Status:** Production Ready | **Version:** 1.0.0 | **Updated:** April 2026

---

## What is SlideForage?

SlideForage is a complete AI-driven presentation generation system that transforms simple text prompts into fully formatted, styled PowerPoint presentations. The system intelligently plans, builds, and delivers presentations without manual intervention.

### The Core Idea

```
Your Prompt: "Create a 5-slide presentation on machine learning"
                            ↓
                    [Intelligent Agent]
                            ↓
                 (Plans structure, searches web,
                  builds slides, applies theme)
                            ↓
        Output: presentation_20240405_123045.pptx
                   (Ready to download/edit)
```

### What Makes It Special

- **🧠 Intelligent Planning** - Agent plans the entire presentation structure before execution
- **🌐 Real-time Web Content** - Integrates web search to provide current, relevant information for each slide
- **🔧 Multiple MCP Servers** - 4 specialized servers with 16 tools handle distinct aspects
- **💪 Robust Error Handling** - Gracefully degrades if any service fails, still delivers partial presentations
- **🔐 Secure Authentication** - JWT-based user authentication with session management
- **🎨 Professional Styling** - Built-in themes (default, ocean, forest, sunset, midnight)

---

## 🚀 Quick Demo

### 1. User Request
```
User Input: "Create a 5-slide presentation on climate change"
```

### 2. Agent Planning (1-2 seconds)
```
Agent analyzes prompt and generates plan:
  Slide 1: Introduction to Climate Change
  Slide 2: Causes & Greenhouse Gases
  Slide 3: Global Effects & Impacts
  Slide 4: Solutions & Mitigation Strategies
  Slide 5: Individual & Collective Action
```

### 3. Presentation Building (3-5 seconds)
```
Agent executes 5-phase pipeline:
  ✓ Phase 1: PLAN structure
  ✓ Phase 2: CREATE PowerPoint file
  ✓ Phase 3: BUILD slides with web content
  ✓ Phase 4: APPLY professional theme
  ✓ Phase 5: SAVE to disk
```

### 4. Result
```
Output: presentation_20240405_153042.pptx
Status: Ready for download

User can:
  • Download the PPTX file
  • Edit in PowerPoint
  • Share with others
  • View in history
```

---

## 🏗️ Architecture Overview

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (Next.js + React)                     │
│  • Landing Page      • Auth (login/register)                │
│  • Dashboard         • Job History          • Settings      │
│  • Download Files    • Real-time Status Updates             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST (Port 3000)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│         BACKEND (FastAPI + Python)                          │
│  • Auth Layer (JWT)                                         │
│  • Agent Engine (5-phase agentic loop)                      │
│  • Job Manager & Database                                   │
│  • MCP Client (communicates with 4 servers)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┬────────────────┐
        ↓                ↓                ↓                ↓
    ┌────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ PPT Server │ │ Web Search   │ │ Filesystem   │ │ Theme Server │
    │ (6 tools)  │ │ (2 tools)    │ │ (4 tools)    │ │ (4 tools)    │
    └────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │                │                │                │
        └────────────────┴────────────────┴────────────────┘
                         │
        ┌────────────────┴──────────────┐
        ↓                               ↓
    ┌──────────────┐           ┌──────────────────┐
    │ SQLite/      │           │ Output Directory │
    │ PostgreSQL   │           │                  │
    │ (User & Job  │           │ Generated PPTX   │
    │  tracking)   │           │ Files            │
    └──────────────┘           └──────────────────┘
```

### Component Interaction Flow

```
1. USER REGISTRATION/LOGIN
   Frontend → Backend Auth → JWT Token → User Session in DB

2. PPT GENERATION REQUEST
   Frontend (Prompt) → Backend → Agent Engine

3. AGENT EXECUTION (5 Phases)
   a) PLANNING      - Agent plans slide structure
   b) CREATE        - Initialize PowerPoint
   c) BUILD SLIDES  - Add slides with content from web search
   d) APPLY THEME   - Style the presentation
   e) SAVE & OUTPUT - Save PPTX to outputs folder

4. RESULT DELIVERY
   Backend → Frontend → PPTX Download
```

---

## 📁 Project Structure

```
ppt-agent/
│
├── README.md                          # Root documentation (you are here)
│
├── agent/                             # Backend (FastAPI + Agent)
│   ├── README.md                      # Detailed backend documentation
│   ├── main.py                        # FastAPI application & routes
│   ├── agent_engine.py                # 5-phase agentic loop
│   ├── mcp_client.py                  # MCP server communication
│   ├── models.py                      # Database models (User, Job, Session)
│   ├── auth.py                        # JWT & authentication logic
│   ├── config.py                      # Environment configuration
│   ├── db.py                          # Database utilities
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment template
│   └── output/                        # Generated PPTX files
│
├── frontend/                          # Frontend (Next.js + React)
│   ├── README.md                      # Frontend documentation
│   ├── package.json                   # Node dependencies
│   ├── next.config.js                 # Next.js configuration
│   ├── tailwind.config.ts             # Tailwind CSS config
│   ├── tsconfig.json                  # TypeScript config
│   ├── app/                           # Next.js App Router
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Landing page
│   │   ├── (auth)/                    # Auth routes
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   └── (protected)/               # Protected routes
│   │       ├── dashboard/page.tsx     # Main PPT generator
│   │       ├── history/page.tsx       # Job history
│   │       └── settings/page.tsx      # Settings
│   ├── components/                    # React components
│   │   ├── auth/                      # Auth components
│   │   ├── ppt/                       # PPT components
│   │   │   ├── PromptInput.tsx
│   │   │   ├── GenerationStatus.tsx
│   │   │   └── HistoryList.tsx
│   │   ├── layout/                    # Layout components
│   │   └── ui/                        # shadcn/ui components
│   ├── context/                       # React context
│   ├── hooks/                         # Custom hooks
│   ├── lib/                           # Utilities
│   └── styles/                        # Global styles
│
├── mcp/                               # MCP Servers
│   ├── README.md                      # MCP documentation
│   └── servers/                       # 4 specialized servers
│       ├── 1.ppt_server.py            # PowerPoint manipulation
│       ├── 2.web_search_server.py     # Web search functionality
│       ├── 3.filesystem_server.py     # File I/O operations
│       ├── 4.theme_server.py          # Theming & styling
│       ├── requirements.txt
│       └── __init__.py
│
└── outputs/                           # Generated presentations
    └── presentation_*.pptx            # Output files (git ignored)
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 18+** (for frontend)
- **npm or yarn** (package manager)

### Setup in 5 Steps

#### Step 1: Clone & Navigate
```bash
cd ppt-agent
```

#### Step 2: Backend Setup

```bash
cd agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from models import init_db; init_db()"

# Start backend
python main.py
```
✅ Backend running on http://localhost:8000

#### Step 3: MCP Servers Setup

```bash
cd mcp/servers

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Servers auto-start when backend runs
```

#### Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
✅ Frontend running on http://localhost:3000

#### Step 5: Access Application

```
Landing Page:      http://localhost:3000
API Docs (Swagger): http://localhost:8000/docs
Health Check:      http://localhost:8000/health
```

---

## 🔧 System Components

### 1. **Frontend (Next.js + React)**

Modern, responsive web interface for user interaction.

**Key Features:**
- ✅ User registration & authentication
- ✅ Interactive prompt input with validation
- ✅ Real-time generation status display
- ✅ PPTX download functionality
- ✅ Job history tracking with filters
- ✅ Responsive design (mobile-friendly)
- ✅ Dark mode support

**Technology:**
- Next.js 16 (React 19)
- TypeScript for type safety
- Tailwind CSS + shadcn/ui
- Zod for form validation
- Axios for API communication

**See:** [Frontend README](./frontend/README.md)

---

### 2. **Backend (FastAPI + Python)**

Intelligent agent that orchestrates presentation generation.

**Key Components:**
- **FastAPI Server** - HTTP API for frontend communication
- **Agent Engine** - 5-phase agentic loop (PLAN → CREATE → BUILD → THEME → SAVE)
- **MCP Client** - Communicates with 4 MCP servers for distributed execution
- **Auth Layer** - JWT-based authentication with bcrypt
- **Database Layer** - User & job management (SQLite/PostgreSQL)

**Key Features:**
- ✅ Intelligent slide planning before execution
- ✅ Graceful error handling & partial results
- ✅ Retry logic for failed operations
- ✅ Web search integration for real content
- ✅ Comprehensive logging for debugging

**See:** [Agent README](./agent/README.md)

---

### 3. **MCP Servers (Python)**

Four specialized micro-services handling distinct responsibilities.

**Server Breakdown:**

| Server | Purpose | Tools | Language |
|--------|---------|-------|----------|
| **1. PPT Server** | PowerPoint creation & manipulation | 6 tools | Python |
| **2. Web Search Server** | Real-time content fetching | 2 tools | Python |
| **3. Filesystem Server** | File I/O operations | 4 tools | Python |
| **4. Theme Server** | Presentation styling | 4 tools | Python |

**Total:** 4 servers | 16 tools | Professional separation of concerns

**See:** [MCP README](./mcp/README.md)

---

## ✨ Key Features

### 1. **Intelligent Planning**
- Agent analyzes prompt and plans entire slide structure before creation
- Ensures coherent, well-organized presentations
- Prevents random/disconnected slide generation

### 2. **Real-time Content**
- Integrates DuckDuckGo web search
- Fetches current information for each slide topic
- Provides cited, up-to-date content automatically

### 3. **Professional Output**
- **PPTX Format** - Native PowerPoint format for editing
- **Built-in Themes** - 5 professional themes (default, ocean, forest, sunset, midnight)
- **Custom Styling** - Color schemes, fonts, layouts
- **Consistent Branding** - Unified design across all slides

### 4. **Robust Error Handling**
- Retry logic for failed operations (3 attempts with backoff)
- Graceful degradation if web search fails
- Partial presentation delivery on partial failures
- Comprehensive logging for debugging

### 5. **User Management**
- Secure registration & login
- JWT-based authentication (24-hour tokens)
- Job history tracking per user
- Per-user output isolation

---

## 🛠️ Technology Stack

### Backend
```
Framework:    FastAPI (Python)
Database:     SQLite (dev) / PostgreSQL (prod)
Auth:         JWT + bcrypt
PowerPoint:   python-pptx
Web Search:   DuckDuckGo Search
Protocol:     Model Context Protocol (MCP)
Server:       Uvicorn
ORM:          SQLAlchemy
```

### Frontend
```
Framework:    Next.js 16 (React 19)
Language:     TypeScript
Styling:      Tailwind CSS + shadcn/ui
HTTP:         Axios
Forms:        React Hook Form + Zod
UI Toolkit:   Radix UI components
Icons:        Lucide React
Notifications: Sonner
```

### DevOps
```
Containerization: Docker (ready for deployment)
Package Manager:  npm (frontend), pip (backend)
Version Control:  Git
Database:         SQLite (dev), PostgreSQL (production)
```

---

## 📦 Deployment

### Development (Local)

```bash
# Terminal 1 - Backend
cd agent
python main.py  # http://localhost:8000

# Terminal 2 - Frontend
cd frontend
npm run dev  # http://localhost:3000
```

### Production

See detailed deployment guides:
- [Agent Deployment](./agent/README.md#deployment)
- [Frontend Deployment](./frontend/README.md#deployment)

**Pre-deployment Checklist:**
- [ ] Enable HTTPS/TLS
- [ ] Change SECRET_KEY in .env
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure CORS properly
- [ ] Set up log rotation
- [ ] Configure environment variables for production

---

## 👨‍💻 Development

### Running All Components

```bash
# Terminal 1 - Backend
cd agent
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Visit http://localhost:3000 to access the application.

### Environment Variables

**Backend (.env)**
```env
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Database
DATABASE_URL=sqlite:///./ppt_agent.db

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-here

# MCP Servers
MCP_SERVERS_PATH=../mcp/servers

# Optional: HuggingFace token
HF_TOKEN=optional-token
```

**Frontend (.env.local)**
```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: App name
NEXT_PUBLIC_APP_NAME=SlideForage
```

### Code Quality

```bash
# Backend
cd agent
flake8 .              # Linting
black .               # Formatting

# Frontend
cd frontend
npm run lint          # ESLint
npm run format        # Prettier
```

---

## 📊 API Endpoints

Quick reference for key endpoints:

### Authentication
```
POST   /register              # Create account
POST   /login                 # Get JWT token
```

### PPT Generation
```
POST   /create-ppt            # Generate presentation
GET    /download/{filename}   # Download PPTX
GET    /jobs                  # Get user's job history
GET    /jobs/{job_id}         # Get specific job status
```

### System
```
GET    /health                # System health check
GET    /docs                  # Swagger UI (interactive)
GET    /redoc                 # ReDoc (alternative docs)
```

**Full API docs available at:** http://localhost:8000/docs

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check MCP servers path
ls ../mcp/servers/
```

### Frontend won't build
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

### Can't reach backend from frontend
```bash
# Check backend is running
curl http://localhost:8000/health

# Verify frontend API URL
cat .env.local | grep NEXT_PUBLIC_API_URL
```

### MCP servers not responding
```bash
# Check if servers are running
ps aux | grep python

# Test MCP server directly
python mcp/servers/1.ppt_server.py
```

---

## 📞 Support & Resources

### Documentation
- **[Agent README](./agent/README.md)** - Backend architecture, API docs, agentic loop details
- **[Frontend README](./frontend/README.md)** - UI components, state management, deployment
- **[MCP README](./mcp/README.md)** - MCP servers, tool documentation, integration guide

### Getting Help
1. Check relevant README for your module
2. Review Troubleshooting section
3. Check application logs
4. Verify configuration files

---

## 🎉 Quick Links

| Resource | Link |
|----------|------|
| **Agent Docs** | [agent/README.md](./agent/README.md) |
| **Frontend Docs** | [frontend/README.md](./frontend/README.md) |
| **MCP Docs** | [mcp/README.md](./mcp/README.md) |
| **API Docs** | http://localhost:8000/docs |
| **Live App** | http://localhost:3000 |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

**Made with ❤️ for intelligent presentation generation**
