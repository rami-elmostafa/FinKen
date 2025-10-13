# FinKen React Migration Documentation

## Overview
This document tracks the migration of FinKen's Flask-based frontend from Jinja2 templates to a modern React + Tailwind CSS + Material React Table V3 application.

## Migration Status

### Completed Pages
1. **Project Bootstrap** ✅ (Completed: [Date])
   - Initialized Vite + React with JavaScript
   - Configured Tailwind CSS with custom design tokens
   - Installed Material React Table V3, React Router, React Hook Form, Zod
   - Set up testing with Vitest and React Testing Library
   - Created base app structure with routing
   - Configured API proxy for Flask backend

2. **Shared UI Components** ✅ (Completed: [Date])
   - `AppLayout` - Main layout with header and sidebar
   - `Header` - Top navigation with branding and user info
   - `Sidebar` - Collapsible navigation menu
   - `Button` - Reusable button with variants
   - `Input` - Form input with error handling
   - `FlashMessage` - Alert/notification component

3. **Login Page** ✅ (Completed: [Date])
   - **Legacy**: `templates/index.html`
   - **React**: `src/pages/LoginPage.jsx`
   - **Route**: `/` and `/login`
   - **Features**:
     - Form validation with react-hook-form + zod
     - Flash message support
     - Responsive Tailwind layout
     - Accessibility (ARIA labels, keyboard nav)
   - **Tests**: Basic render and validation tests
   - **Status**: Ready for PR

### Outstanding Pages
- [ ] Home.html → HomePage.jsx (`/home`)
- [ ] CreateNewUser.html → CreateNewUserPage.jsx (`/create-new-user`)
- [ ] ForgotPassword.html → ForgotPasswordPage.jsx (`/forgot-password`)
- [ ] SecurityQuestion.html → SecurityQuestionPage.jsx (`/security-question/:userid`)
- [ ] ResetPassword.html → ResetPasswordPage.jsx (`/reset-password/:userid`)
- [ ] FinishSignUp.html → FinishSignUpPage.jsx (`/finish-signup`)
- [ ] Users.html → UsersPage.jsx (`/users`) - **With Material React Table V3**
- [ ] ManageRegistrations.html → ManageRegistrationsPage.jsx (`/manage-registrations`) - **With Material React Table V3**
- [ ] ExpiringPasswords.html → ExpiringPasswordsPage.jsx (`/expiring-passwords`) - **With Material React Table V3**
- [ ] ChartOfAccounts.html → ChartOfAccountsPage.jsx (`/chart-of-accounts`) - **With Material React Table V3**
- [ ] Ledger.html → LedgerPage.jsx (`/ledger/:account_number`) - **With Material React Table V3**

## Design Tokens (Tailwind Config)

### Colors
- **Primary**: `#FFD100` (gold/yellow)
- **Primary Dark**: `#FFC900`
- **Secondary**: `#333333` (dark gray)
- **Accent Blue**: `#0b6ea8`
- **Success**: `#28a745`
- **Danger**: `#dc3545`
- **Warning**: `#ffc107`

### Typography
- **Font Family**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Responsive**: Mobile-first approach

### Border Radius
- **Card**: `25px` for major containers
- **Standard**: `6-8px` for buttons/inputs

## Architecture Decisions

### State Management
- Local component state for UI concerns
- Context API for auth/user data (to be implemented)
- No Redux/Zustand initially (add if needed)

### API Integration
- Vite proxy configured to Flask backend (`localhost:8000`)
- All API calls use `/api/*` prefix
- Session-based authentication maintained
- Credentials included in fetch requests

### Form Handling
- React Hook Form for all forms
- Zod for validation schemas
- Accessible error messaging

### Styling Approach
- Tailwind utility classes for layout and styling
- Component-specific styles when needed
- Material React Table V3 for all tabular data
- Minimal custom CSS (only in index.css)

### Testing Strategy
- Vitest for unit tests
- React Testing Library for component tests
- Focus on critical user flows
- Accessibility testing with jest-dom

## Technical Debt & Known Issues

### Current Gaps
1. Authentication context not yet implemented
2. Role-based access control needs integration
3. API service layer to be created
4. Error boundary components needed
5. Loading states/skeletons to be standardized

### Accessibility Notes
- All forms have proper labels and ARIA attributes
- Keyboard navigation supported
- Focus management for modals/sidebars
- Color contrast meets WCAG AA standards

## File Structure

```
react-frontend/
├── public/
│   ├── finkenlogo.png
│   └── default_profile.webp
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.jsx
│   │   │   ├── Header.jsx
│   │   │   └── Sidebar.jsx
│   │   ├── ui/
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   └── FlashMessage.jsx
│   │   └── data/
│   │       └── DataTable.jsx (to be created)
│   ├── pages/
│   │   └── LoginPage.jsx
│   ├── services/
│   │   └── api.js (to be created)
│   ├── hooks/
│   ├── utils/
│   ├── test/
│   │   ├── setup.js
│   │   └── LoginPage.test.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── tailwind.config.js
├── vite.config.js
└── package.json
```

## Development Workflow

### Starting Dev Server
```bash
cd react-frontend
npm run dev
# Runs on http://localhost:5173
# API proxied to http://localhost:8000
```

### Running Tests
```bash
npm test        # Run tests in watch mode
npm run test:ui # Run with Vitest UI
```

### Building for Production
```bash
npm run build
# Outputs to react-frontend/dist/
```

## Next Steps

1. ✅ Complete project bootstrap
2. ✅ Create shared UI primitives
3. ✅ Convert Login page (index.html)
4. 🔄 Create authentication context and API service
5. ⏳ Convert Home page (Home.html)
6. ⏳ Convert registration pages (CreateNewUser, FinishSignUp)
7. ⏳ Convert password reset flow
8. ⏳ Convert admin pages with Material React Table V3
9. ⏳ Integration testing and deployment setup

## Contributors
- AI Assistant (GitHub Copilot)
- Project Team

## Last Updated
[Current Date - to be filled in]
