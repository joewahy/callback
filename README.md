# Callback

A full stack web app to track internship and job applications, built with Flask and SQLite — with session-based authentication protecting the dashboard.

> **Note:** This project was built as a learning exercise to explore Flask, relational databases, authentication, and frontend development. It is intended for personal use.

![Callback demo](assets/demo.gif)

## What it does

- Sign up and log in with an email and password — passwords are hashed with bcrypt, never stored in plain text
- All dashboard routes are protected — visiting the app while logged out redirects to the login page
- Each account has its own private set of companies and applications — no user can view or edit another user's data, even by guessing a record's id
- Add companies you are applying to
- Log applications with role, status, date applied, and notes — company name matching is case-insensitive, so "google" and "Google" resolve to the same company
- View all companies and applications in a live dashboard, numbered per-user starting from 1
- Inline edit applications — update role, status, date, and notes without leaving the page
- Archive applications to visually strike them out (currently visual only — resets on reload, see Roadmap)
- Color coded status badges (Applied, Interview, Offer, Rejected)
- Delete individual applications
- Clear all of your own data with a double confirm button
- Toggle between dark and light mode
- Log out from the dashboard header

## Technologies used

- Python
- Flask (with Flask's built-in client-side sessions for auth)
- bcrypt (password hashing)
- email-validator (signup email format validation)
- python-dotenv (loading the app's secret key from environment variables)
- Jinja2
- SQLite3
- HTML/CSS
- JavaScript

## Project structure

- `app/__init__.py` — Flask app setup: config, secret key, database init, route registration
- `app/auth.py` — authentication routes (signup, login, logout) and route protection
- `app/dashboard.py` — main dashboard and inline-update routes
- `app/db.py` — all SQLite database operations (create, insert, query, update, delete, clear), including user account storage
- `app/__main__.py` — dev entry point (`python3 -m app`)
- `templates/index.html` — main dashboard, rendered by Flask
- `templates/login.html` — login page
- `templates/signup.html` — account creation page
- `static/style.css` — styling and dark/light mode theming for the dashboard
- `static/auth.css` — styling for the login/signup pages
- `static/main.js` — all client side JavaScript (theme toggle, inline editing, archive, clear confirm)

## Setup

Clone the repo:
```bash
git clone https://github.com/joewahy/callback.git
cd callback
```

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with a secret key, used to sign login sessions:
```ini
SECRET_KEY=your-randomly-generated-secret-key-here
```
Generate one with:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
`.env` is excluded from version control — never commit your real secret key.

## How to run it

```bash
python3 -m app
```

Then visit `http://127.0.0.1:5000` in your browser. You'll be redirected to the login page — use the "Sign up" link to create an account first.

## Database

Three tables power the app:

- `users` — stores registered accounts (email, bcrypt password hash)
- `companies` — companies a user is applying to, scoped to the account that created them via a `user_id` foreign key
- `applications` — applications linked to a company via `company_id`, and also scoped to their owning account via `user_id`

Both `company_id` and `user_id` are enforced as foreign keys, and every query that reads, updates, or deletes companies/applications filters by the requesting user's id — so ids are shared across the whole table (not reset per account), but no user's data is ever visible or editable by another account. The "#" column shown in the dashboard is a per-user display number generated at render time, separate from the real database id.

The database file `applications.db` is created automatically on first run and is excluded from version control.

## Security notes

- Passwords are hashed with bcrypt before storage — the app never stores or logs a plain-text password.
- Sessions are Flask's built-in client-side sessions: session data is signed (not encrypted) and stored in a cookie, verified against `SECRET_KEY` on every request.
- Login and signup return the same generic error message ("Invalid email or password") on failure, so a failed attempt doesn't reveal whether a given email has an account.
- Logout is a `POST`-only route, so it can't be triggered by a plain link or embedded image.
- Every read, write, update, and delete on companies/applications is scoped to `session['user_id']` at the database level — verified by attempting to edit another account's application id directly, which is correctly rejected.

## Roadmap

- Persist archived state to the database (currently client-side only, so it resets on reload or re-login)
- Filter applications by status
- Add application success rate stats