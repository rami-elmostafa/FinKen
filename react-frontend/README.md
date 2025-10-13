# FinKen React Frontend

Modern React frontend for the FinKen Financial Accounting System, built with Vite, Tailwind CSS, and Material React Table V3.

## 🚀 Tech Stack

- **Framework**: React 19 with JavaScript
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS V4
- **Routing**: React Router DOM V7
- **Forms**: React Hook Form + Zod validation
- **Tables**: Material React Table V3 with TanStack Table
- **UI Components**: Material-UI (MUI) for table components
- **Testing**: Vitest + React Testing Library
- **Code Quality**: ESLint

## 📋 Prerequisites

- Node.js 18+ and npm
- Flask backend running on `http://localhost:8000`

## 🛠️ Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
# App runs on http://localhost:5173
# API requests proxied to http://localhost:8000
```

## 📜 Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run test         # Run tests in watch mode
npm run test:ui      # Run tests with UI
npm run test:coverage # Run tests with coverage report
```

## 🏗️ Project Structure

```
src/
├── components/
│   ├── layout/          # Layout components (Header, Sidebar, AppLayout)
│   ├── ui/              # Reusable UI primitives (Button, Input, FlashMessage)
│   └── data/            # Data components (DataTable wrapper for MRT)
├── pages/               # Page components (one per route)
├── services/            # API service functions
├── hooks/               # Custom React hooks
├── utils/               # Utility functions
├── test/                # Test utilities and setup
├── App.jsx              # Main app with routing
├── main.jsx             # App entry point
└── index.css            # Global styles with Tailwind
```

## 🎨 Design System

### Colors (Tailwind Config)
- **Primary**: `#FFD100` (gold) - Main brand color
- **Secondary**: `#333333` (dark gray) - Text and accents
- **Accent Blue**: `#0b6ea8` - Links and interactive elements
- **Success**: `#28a745` - Success states
- **Danger**: `#dc3545` - Error states
- **Warning**: `#ffc107` - Warning states

### Typography
- Font Family: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- Responsive sizing with mobile-first approach

## 🔌 API Integration

Vite development server proxies API requests to Flask:
- `/api/*` → `http://localhost:8000/api/*`
- `/profile_images/*` → `http://localhost:8000/profile_images/*`

All API calls should use `credentials: 'include'` for session cookies.

## 📄 Pages (Migration Status)

### ✅ Completed
1. **LoginPage** (`/`) - User sign-in with form validation

### ⏳ Planned
2. **HomePage** (`/home`) - Dashboard
3. **UsersPage** (`/users`) - User management with MRT V3
4. **ChartOfAccountsPage** (`/chart-of-accounts`) - Accounting with MRT V3
5. And more... (see [MIGRATION.md](../MIGRATION.md))

## 🧪 Testing

```bash
npm test        # Run in watch mode
npm run test:ui # With UI interface
```

## 🚀 Production Build

```bash
npm run build   # Output: dist/
npm run preview # Test production build
```

## 📚 Documentation

- [Migration Plan](../AI_React_Revamp_Plan.txt)
- [Migration Tracking](../MIGRATION.md)

---

**Built for FinKen Financial Accounting System**
