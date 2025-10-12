## FinKen — Copilot instructions (quick reference)

Purpose: give an AI coding agent the minimal, concrete facts needed to make safe, useful edits in this repo.

High-level architecture
- Single Flask backend (entry: `app.py`) that renders templates from `templates/` and serves static frontend from `frontend/`.
- Postgres database accessed via Supabase client wrapper in `SupabaseClient.py` (function `_sb()` returns a supabase client).
- Main domain modules: `CreateNewUser.py`, `FinishSignUp.py`, `SignInUser.py`, `AdminManagement.py`, `UserManagement.py`, `ProfilePictureHandler.py`, `EmailUser.py`, `ForgotPassword.py`.
- Frontend assets live in `frontend/`. Profile images are in `profile_images/` and served by `app.py` route `/profile_images/<filename>`.

Key integration points and conventions
- Database access: always go through `SupabaseClient._sb()` (or inject a fake `sb` via functions that accept `sb=None`).
  - `_sb()` will call an RPC `set_audit_user_context` if a context user was set via `set_current_user`.
  - Many functions expect `.execute()` responses and read `.data`. Sometimes a `.count` attribute is present.
- Audit / user context: `SupabaseClient` uses a contextvar `current_user_id` and exposes `set_current_user(user_id)` and `get_current_user()`; `app.py` provides a `@set_user_context` decorator which calls `set_current_user(session['user_id'])` when present. When modifying DB-related functions, preserve use of `sb = sb or _sb()` to allow test injection.
- Session keys: session stores `user_id`, `username`, `user_role`, `user_name` (note: `user_role` is lowercased in `app.py` and compared against strings like `administrator`, `manager`, `accountant`).
- Return shape: most service functions return dicts with at least `success` (bool) and optionally `message` and data keys (`requests`, `users`, `user`, `pagination`). Code checks `if result.get('success')`.
- Error handling pattern: functions catch exceptions and return `{'success': False, 'message': '...'}.` Follow this when adding new functions.

Database / table expectations (discoverable from code)
- Tables used: `users`, `roles`, `registration_requests`, `security_questions`, `user_security_answers`, `event_logs`, `roles`.
- Audit RPC: `set_audit_user_context(user_id)` expected in DB. Keep _sb() behavior intact when adding DB calls.

Developer workflows (how to run/test locally)
- Setup (Windows PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
- Run app:
  - Quick: `python app.py` (app runs on PORT env var or defaults to 8000)
  - Or use Flask dev server: `set-Item Env:FLASK_APP app.py; flask run` (PowerShell) — `app.py` already includes `if __name__ == '__main__':` starter.
- Tests: repository uses pytest. Run from repo root:
```powershell
pytest -q
```
  - Unit tests use `tests/conftest.py` which provides `fake_sb_factory` — prefer injecting `sb` into functions under test (many functions accept `sb=None`).

Patterns & examples to follow when editing code
- Dependency injection: functions like `get_users_paginated(..., sb=None)` accept `sb` and call `sb or _sb()`. Use this pattern to make code testable.
  - Example: `AdminManagement.get_all_registration_requests(page, per_page, search_term, status_filter, sb=None)`.
- Supabase query expectations: chains end with `.execute()` and result is inspected via `response.data`. When writing new queries, mimic the `.select(...).eq(...).order(...).range(...).execute()` style.
- Pagination: many endpoints use `page`, `per_page`, compute `offset = (page-1)*per_page`, and return `pagination` dict. Follow same keys (`current_page`, `per_page`, `total_pages`, `has_next`, `has_prev`).
- Role checks in routes: routes guard by checking `session.get('user_role') != 'administrator'` or membership in `['administrator','manager']`. Keep these string comparisons consistent.
- Profile pictures: use `ProfilePictureHandler.save_user_profile_picture(user_id, file)` and `get_user_profile_picture(user_id)` for reads/writes. Files are stored under `profile_images/`.

Testing tips for AI-generated changes
- Use the `sb` injection parameter in unit tests. `tests/conftest.py` provides a `fake_sb_factory()` that returns FakeTableRouter responses. Example usage pattern:
  - Provide dict keys like `(\'users\', 'select')` mapping to test data.
- For audit-context tests: call `set_current_user(test_user_id)` before `_sb()` to simulate the RPC call path.

Files worth reading before editing
- `app.py` — request routing, session management, decorator `set_user_context`, and where templates/frontend are wired.
- `SupabaseClient.py` — how the supabase client is created and audit context is set.
- `AdminManagement.py`, `UserManagement.py` — canonical examples of `sb or _sb()` usage, pagination, and return shapes.
- `tests/conftest.py` and `tests/test_user_context.py` — show how tests inject fake DB and how audit-context tests behave.

Quick editing rules for safe PRs
- Preserve `sb = sb or _sb()` in any function that accesses the DB.
- Return consistent dict shapes (include `success` boolean). Use `result.get('message')` in callers.
- When adding routes, mirror existing access checks and use `@set_user_context` where appropriate.
- Avoid changing session key names — downstream templates and routes rely on `user_id`, `username`, `user_role`, `user_name`.

If anything here is unclear, reply with which area you'd like expanded (run/test commands, DB schema assumptions, or typical unit-test scaffolding) and I will update this file.
