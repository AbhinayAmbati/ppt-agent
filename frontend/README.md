# 🎨 SlideForage - Frontend Application

> Modern, responsive React-based web interface for AI-powered presentation generation. Built with Next.js, TypeScript, and Tailwind CSS.

**Status:** Production Ready | **Version:** 1.0.0 | **Framework:** Next.js 16 + React 19 and Shadcn/ui

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Quick Start](#quick-start)
4. [Project Structure](#project-structure)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [Component Architecture](#component-architecture)
9. [Authentication Flow](#authentication-flow)
10. [API Integration](#api-integration)
11. [Styling & Theming](#styling--theming)
12. [Development](#development)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

SlideForage Frontend is a full-stack Next.js application providing users with an intuitive interface to:

- ✅ **Register & authenticate** securely with JWT tokens
- ✅ **Input prompts** for presentation generation
- ✅ **Monitor real-time status** of generation
- ✅ **Download generated PPTX** files
- ✅ **View generation history** with filters
- ✅ **Manage account settings** and preferences

**Technology Stack:**
```
Framework:    Next.js 16 (React 19)
Language:     TypeScript
Styling:      Tailwind CSS + shadcn/ui
Forms:        React Hook Form + Zod
HTTP:         Axios
Notifications: Sonner (toast)
Icons:        Lucide React
```

---

## ✨ Features

### User Authentication
- ✅ Secure registration with email validation
- ✅ Login with username/password
- ✅ JWT authentication (24-hour tokens)
- ✅ Automatic token refresh on page load
- ✅ Protected routes (AuthGuard component)
- ✅ Session persistence via localStorage

### Presentation Generation
- ✅ Natural language prompt input
- ✅ Real-time generation status updates
- ✅ Progress visualization with phases
- ✅ PPTX download after generation
- ✅ Error handling with user-friendly messages
- ✅ Retry functionality on failure

### User Dashboard
- ✅ Generation history with timestamps
- ✅ Job status tracking (pending, processing, completed, failed)
- ✅ Quick download actions
- ✅ Delete old presentations
- ✅ Search & filter functionality
- ✅ Responsive table view

### User Experience
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Dark mode support
- ✅ Loading states & skeletons
- ✅ Form validation feedback
- ✅ Toast notifications (success, error, info)
- ✅ Keyboard accessibility
- ✅ Aria labels for screen readers

---

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** ([install](https://nodejs.org))
- **npm 9+** or **yarn 4+** (comes with Node.js)
- **Backend running** on http://localhost:8000

### 5-Minute Setup

#### Step 1: Install Dependencies
```bash
cd frontend

npm install  # or: yarn install / pnpm install / bun install

# Takes ~2-3 minutes first time
```

#### Step 2: Configure Environment
```bash
# Copy template
cp .env.example .env.local

# Edit with your backend URL
nano .env.local

# Content:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Step 3: Start Development Server
```bash
npm run dev

# or: yarn dev, pnpm dev, bun dev
```

#### Step 4: Open in Browser
```
http://localhost:3000
```

#### Step 5: Test Application
1. Go to `http://localhost:3000`
2. Click "Sign Up"
3. Create an account
4. Go to Dashboard
5. Enter a prompt: "Create 5-slide presentation on AI"
6. Click "Generate"
7. Wait for generation (8-12 seconds)
8. Download PPTX file

---

## 📁 Project Structure

```
frontend/
│
├── README.md                          # This file
├── package.json                       # Dependencies & scripts
├── next.config.js                     # Next.js configuration
├── tailwind.config.ts                 # Tailwind CSS config
├── tsconfig.json                      # TypeScript config
│
├── app/                               # Next.js App Router
│   ├── layout.tsx                     # Root layout wrapper
│   ├── page.tsx                       # Landing page (/)
│   │
│   ├── (auth)/                        # Auth route group
│   │   ├── layout.tsx                 # Auth layout (no sidebar)
│   │   ├── login/page.tsx             # Login page (/login)
│   │   └── register/page.tsx          # Registration page (/register)
│   │
│   └── (protected)/                   # Protected routes (auth required)
│       ├── layout.tsx                 # Protected layout (with sidebar)
│       ├── dashboard/page.tsx         # PPT generator (/dashboard)
│       ├── history/page.tsx           # Job history (/history)
│       └── settings/page.tsx          # Settings (/settings)
│
├── components/                        # Reusable React components
│   │
│   ├── auth/                          # Authentication components
│   │   ├── AuthGuard.tsx              # Route protection wrapper
│   │   ├── LoginForm.tsx              # Login form
│   │   └── RegisterForm.tsx           # Registration form
│   │
│   ├── ppt/                           # PPT-specific components
│   │   ├── PromptInput.tsx            # Input form with validation
│   │   ├── GenerationStatus.tsx       # Status display & progress
│   │   └── HistoryList.tsx            # Job history table
│   │
│   ├── layout/                        # Layout components
│   │   ├── Header.tsx                 # Top navigation bar
│   │   ├── Sidebar.tsx                # Left sidebar
│   │   ├── PublicNavbar.tsx           # Public site navbar
│   │   └── PublicFooter.tsx           # Public site footer
│   │
│   └── ui/                            # UI primitives (shadcn/ui)
│       ├── button.tsx
│       ├── input.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── select.tsx
│       └── ... (other components)
│
├── context/                           # React Context API
│   ├── AuthContext.tsx                # Auth state management
│   └── ConfigContext.tsx              # App configuration
│
├── hooks/                             # Custom React hooks
│   ├── usePPT.ts                      # PPT generation hook
│   ├── useAuth.ts                     # Auth hook
│   ├── useLocalStorage.ts             # LocalStorage wrapper
│   └── useDebounce.ts                 # Debounce utility
│
├── lib/                               # Utilities & helpers
│   ├── api.ts                         # Axios API client
│   ├── types.ts                       # TypeScript type definitions
│   ├── validators.ts                  # Zod form validators
│   ├── utils.ts                       # Helper functions
│   └── constants.ts                   # Constants & config
│
├── styles/                            # Global styles
│   ├── globals.css                    # Global styles + Tailwind
│   └── variables.css                  # CSS variables
│
├── public/                            # Static assets
│   ├── favicon.ico
│   └── ... (images, fonts)
│
└── .env.example                       # Environment template
```

---

## ⚙️ Installation

### Prerequisites

- **Node.js 18+** - [Download](https://nodejs.org)
- **Backend running** - See [Agent README](../agent/README.md)

### Install Steps

#### 1. Install Dependencies

```bash
cd frontend

# Using npm (recommended)
npm install

# Or using yarn
yarn install

# Or using pnpm
pnpm install

# Or using bun
bun install
```

**Dependencies Installed:**
- `next` (16) - React framework
- `react` (19) - UI library
- `typescript` - Type safety
- `tailwindcss` - Utility CSS
- `axios` - HTTP client
- `react-hook-form` - Form state
- `zod` - Validation
- `sonner` - Toast notifications
- `lucide-react` - Icons

#### 2. Configure Environment

```bash
# Copy template
cp .env.example .env.local

# Edit configuration
nano .env.local  # Or use your preferred editor
```

**Required Variables:**
```env
# Backend API URL (MUST match your backend!)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: App name
NEXT_PUBLIC_APP_NAME=SlideForage

# Optional: Debug mode
NEXT_PUBLIC_DEBUG=false
```

#### 3. Verify Installation

```bash
# Check Node version
node --version    # Should be 18+

# Try to start
npm run dev

# If successful:
# ✓ Ready on http://localhost:3000
```

---

## 🏃 Running the Application

### Development Mode

```bash
# Start with hot reload (recommended for development)
npm run dev

# Or with other package managers
yarn dev
pnpm dev
bun dev
```

**Server:** http://localhost:3000

**Features:**
- ✅ Hot module replacement (HMR)
- ✅ Fast refresh on file changes
- ✅ Source maps for debugging
- ✅ Console output in terminal

---

### Production Build

```bash
# Build optimized bundle
npm run build

# Check build output
# ✓ Route (pages)
# ✓ Size
# ✓ Duration

# Start production server
npm run start

# Or with PM2 process manager
pm2 start "npm start" --name "slideforge-frontend"
```

---

### Linting & Formatting

```bash
# Check for errors
npm run lint

# Auto-fix linting issues
npm run lint -- --fix

# Format code with Prettier
npm run format
```

---

## 🏗️ Component Architecture

### Authentication Flow

```
        ┌──────────────────┐
        │   Landing Page   │
        │ (Login/Sign Up)  │
        └────────┬─────────┘
                 │
    ┌──────────────────────────┐
    ↓                          ↓
┌──────────────┐      ┌──────────────────┐
│  LoginForm   │      │  RegisterForm    │
│              │      │                  │
│ • Input email│      │ • Input username │
│ • Input pass │      │ • Input email    │
│ • Validate   │      │ • Input password │
│ • API call   │      │ • Validate       │
│ • Store JWT  │      │ • API call       │
└──────┬───────┘      └────────┬─────────┘
       │                       │
       └──────────┬────────────┘
                  ↓
         ┌──────────────────┐
         │  AuthContext     │
         │                  │
         │ • Store token    │
         │ • Store user_id  │
         │ • Auth state     │
         └────────┬─────────┘
                  │
         ┌────────┴──────────┐
         │ AuthGuard Check   │
         │                   │
         │ No token?         │
         │ → Redirect /login │
         │                   │
         │ Valid token?      │
         │ → Render page     │
         └────────┬──────────┘
                  ↓
      ┌──────────────────────┐
      │ Protected Dashboard  │
      │ (render user area)   │
      └──────────────────────┘
```

### PPT Generation Flow

```
User enters prompt
        ↓
┌──────────────────────────┐
│  PromptInput Component   │
│                          │
│ • Accept text input      │
│ • Validate with Zod      │
│ • Character limit check  │
│ • Error messages         │
└──────────┬───────────────┘
           │
           ↓
  ┌────────────────────┐
  │   API Call (POST)  │
  │  /create-ppt       │
  │  + JWT token       │
  └────────┬───────────┘
           │
           ↓
┌─────────────────────────────────┐
│  GenerationStatus Component     │
│                                 │
│ • Show: "Generating..."         │
│ • Show: Current phase           │
│ • Show: Progress bar            │
│ • Poll for updates every 2s     │
│ • Get: /jobs/{job_id}           │
└────────┬────────────────────────┘
         │
   ┌─────┴─────┐
   │           │
Still         Complete?
Processing?
   │            │
   ↓            ↓
Show      ┌──────────────────┐
Progress  │ Success Message  │
          │ • Download link  │
          │ • File info      │
          │ • Add to history │
          └──────────────────┘
```

### Component Hierarchy

```
App Root (layout.tsx)
│
├── Public Routes
│   ├── / (Landing)
│   │   ├── PublicNavbar
│   │   ├── Hero Section
│   │   └── PublicFooter
│   │
│   ├── /login
│   │   └── LoginForm
│   │
│   └── /register
│       └── RegisterForm
│
└── Protected Routes (AuthGuard)
    │
    ├── Layout (Sidebar + Header)
    │   ├── Header (top nav)
    │   └── Sidebar (left nav)
    │
    ├── /dashboard
    │   ├── PromptInput
    │   └── GenerationStatus
    │
    ├── /history
    │   ├── HistoryList
    │   └── Action buttons
    │
    └── /settings
        ├── Profile section
        └── Preferences
```

---

## 🔐 Authentication

### Login / Register Process

```typescript
// User registers
POST /register {username, email, password}
  → Backend hashes password
  → Creates user in database
  → Returns user_id

// User logs in
POST /login {username, password}
  → Backend verifies credentials
  → Generates JWT token
  → Returns {access_token, user_id}

// Frontend stores token
localStorage.setItem('auth_token', access_token)
localStorage.setItem('user_id', user_id)

// All subsequent requests include token
Authorization: Bearer {token}
```

### Token Management

**Storage Method:** LocalStorage
```javascript
// Get token
const token = localStorage.getItem('auth_token');

// Check if logged in
const isLoggedIn = !!token;

// Logout
localStorage.removeItem('auth_token');
localStorage.removeItem('user_id');
```

**Token Validity:** 24 hours (backend enforces expiration)

**Auto Logout:** When token expires, user redirected to /login

---

## 🔗 API Integration

### API Client Setup

**lib/api.ts:**
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
});

// Add JWT token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Available Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/register` | Create account |
| `POST` | `/login` | Get JWT token |
| `POST` | `/create-ppt` | Generate presentation |
| `GET` | `/download/{filename}` | Download PPTX |
| `GET` | `/jobs` | Get job history |
| `GET` | `/jobs/{job_id}` | Get job status |
| `GET` | `/health` | System health |

### Example API Calls

**Generate Presentation:**
```typescript
const createPresentation = async (prompt: string) => {
  try {
    const response = await api.post('/create-ppt', { prompt });

    return {
      jobId: response.data.job_id,
      filePath: response.data.file_path,
      numSlides: response.data.num_slides
    };
  } catch (error) {
    console.error('Generation failed:', error);
    throw error;
  }
};
```

**Poll for Status:**
```typescript
const pollJobStatus = async (jobId: string) => {
  let status = 'processing';

  while (status === 'processing') {
    const response = await api.get(`/jobs/${jobId}`);
    status = response.data.job.status;

    // Update UI with progress
    updateProgress(response.data.job.progress);

    // Wait before polling again
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  return status;
};
```

---

## 🎨 Styling & Theming

### Tailwind CSS

**Configuration:** `tailwind.config.ts`
- Utility-first CSS framework
- Custom color palette
- Dark mode support
- Responsive breakpoints

**Usage Example:**
```tsx
<div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
  <h1 className="text-2xl font-bold text-gray-900">SlideForage</h1>
  <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
    Generate
  </button>
</div>
```

### shadcn/ui Components

Pre-built, accessible UI components:

```tsx
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export function Dashboard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Generate Presentation</CardTitle>
      </CardHeader>
      <CardContent>
        <Input placeholder="Enter your prompt..." />
        <Button className="mt-4">Generate</Button>
      </CardContent>
    </Card>
  );
}
```

### Dark Mode

Implemented via theme provider:

```tsx
import { useTheme } from 'next-themes';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
      {theme === 'dark' ? '☀️' : '🌙'}
    </button>
  );
}
```

---

## 👨‍💻 Development

### Development Workflow

**Terminal 1 - Backend:**
```bash
cd agent
python main.py
# Runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

**Terminal 3 - (Optional) Tools:**
```bash
# Git commands, DB browser, etc.
```

### File Organization Best Practices

**In `/app`:**
- Page components (route files)
- Layout wrappers
- Server components

**In `/components`:**
- Reusable UI components
- Form components
- Display components

**In `/hooks`:**
- Custom React hooks
- State management logic

**In `/lib`:**
- Utility functions
- API clients
- Type definitions
- Validators

---

## 🚀 Deployment

### Vercel (Recommended)

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Create Vercel Project:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import GitHub repository
   - Select `frontend` directory as root
   - Set environment variables:
     ```
     NEXT_PUBLIC_API_URL=https://api.yourdomain.com
     ```

3. **Deploy:**
   - Vercel auto-deploys on push
   - Get live URL in dashboard

---

### Self-Hosted (Docker)

**Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

**Build & Run:**
```bash
docker build -t slideforge-frontend .

docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://api:8000 \
  slideforge-frontend
```

---

### Environment Variables (Production)

```env
# MUST match your production backend URL
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Optional
NEXT_PUBLIC_APP_NAME=SlideForage
```

---

## 🐛 Troubleshooting

### Issue: "Cannot find module 'next'"

**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

---

### Issue: "Connection refused" (can't reach backend)

**Solution:**
```bash
# Check .env.local
cat .env.local

# Should show:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Verify backend running:
curl http://localhost:8000/health
```

---

### Issue: "401 Unauthorized" on requests

**Solution:**
```bash
# Check token in localStorage
localStorage.getItem('auth_token')

# Re-login if expired:
# 1. Clear localStorage
# 2. Go to /login
# 3. Enter credentials
```

---

### Issue: Slow performance / large bundle

**Solution:**
```bash
# Analyze bundle size
npm run build -- --analyze

# Use dynamic imports for heavy components
import dynamic from 'next/dynamic';
const HeavyComponent = dynamic(() => import('@/components/Heavy'));
```

---

## 📚 Resources

### Documentation
- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev)
- [TypeScript Docs](https://typescriptlang.org)
- [Tailwind CSS](https://tailwindcss.com)
- [shadcn/ui](https://ui.shadcn.com)

### Related Docs
- [Agent README](../agent/README.md) - Backend
- [MCP README](../mcp/README.md) - MCP servers

---

## 📞 Support

### Debug Checklist

1. ✅ Check browser console (F12) for errors
2. ✅ Check network tab for failed requests
3. ✅ Verify backend is running: `curl http://localhost:8000/health`
4. ✅ Check .env.local configuration
5. ✅ Restart dev server: `npm run dev`

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Cannot GET /" | Next.js not started | `npm run dev` |
| "CORS error" | API URL wrong | Check `NEXT_PUBLIC_API_URL` |
| "401 Unauthorized" | No token/expired | Login again |
| "Network Error" | Backend down | Check `python main.py` |

---

## 🎉 Next Steps

1. **Start developing:**
   ```bash
   npm run dev
   # Visit http://localhost:3000
   ```

2. **Explore components:**
   - Review `components/` directory
   - Check `app/` for route structure

3. **Add features:**
   - Modify prompt validation
   - Add new status indicators
   - Implement custom themes

4. **Deploy to production:**
   - See [Deployment](#deployment) section
   - Use Vercel or Docker

---

**Ready to build amazing presentations!** 🚀

For backend docs, see [Agent README](../agent/README.md)
