from flask import Blueprint, request, jsonify, session
from functools import wraps
from email_validator import validate_email, EmailNotValidError
import bcrypt

from . import db

api = Blueprint("api", __name__, url_prefix="/api/v1")

STATUSES = ("Applied", "Interview", "Offer", "Rejected")


def error(message, status):
    return jsonify({"error": message}), status


def api_login_required(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return error("Authentication required", 401)
        return original_function(*args, **kwargs)
    return wrapper


def json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


def clean_str(data, key):
    value = data.get(key)
    return value.strip() if isinstance(value, str) else None


def serialize_company(row):
    return {"id": row[0], "name": row[1]}


def serialize_application(row):
    return {
        "id": row[0],
        "company": row[1],
        "role": row[2],
        "status": row[3],
        "date_applied": row[4],
        "notes": row[5],
    }


@api.app_errorhandler(404)
@api.app_errorhandler(405)
def json_http_error(e):
    if request.path.startswith(api.url_prefix + "/"):
        return error(e.name, e.code)
    return e


@api.post("/signup")
def signup():
    data = json_body()
    if data is None:
        return error("Request body must be a JSON object", 400)

    email = clean_str(data, "email")
    password = data.get("password")
    if not email or not isinstance(password, str) or not password:
        return error("email and password are required", 400)

    try:
        validate_email(email)
    except EmailNotValidError:
        return error("Invalid email", 400)

    if db.get_user_by_email(email):
        return error("Email already taken", 409)

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    db.create_user(email, hashed_password)
    return jsonify({"email": email}), 201


@api.post("/login")
def login():
    data = json_body()
    if data is None:
        return error("Request body must be a JSON object", 400)

    email = clean_str(data, "email")
    password = data.get("password")
    user = db.get_user_by_email(email) if email else None
    if user is None or not isinstance(password, str) or not bcrypt.checkpw(password.encode("utf-8"), user[2]):
        return error("Invalid email or password", 401)

    session["user_id"] = user[0]
    return jsonify({"email": user[1]})


@api.post("/logout")
def logout():
    session.pop("user_id", None)
    return "", 204


@api.get("/companies")
@api_login_required
def list_companies():
    companies = db.get_all_companies(session["user_id"])
    return jsonify([serialize_company(c) for c in companies])


@api.post("/companies")
@api_login_required
def create_company():
    data = json_body()
    if data is None:
        return error("Request body must be a JSON object", 400)

    name = clean_str(data, "name")
    if not name:
        return error("name is required", 400)

    company_id, name, created = db.add_company(session["user_id"], name)
    return jsonify({"id": company_id, "name": name}), (201 if created else 200)


@api.get("/applications")
@api_login_required
def list_applications():
    applications = db.get_all_applications(session["user_id"])
    return jsonify([serialize_application(a) for a in applications])


@api.post("/applications")
@api_login_required
def create_application():
    data = json_body()
    if data is None:
        return error("Request body must be a JSON object", 400)

    company = clean_str(data, "company")
    role = clean_str(data, "role")
    status = data.get("status", "Applied")
    date_applied = data.get("date_applied")
    notes = data.get("notes", "")

    if not company or not role:
        return error("company and role are required", 400)
    if status not in STATUSES:
        return error(f"status must be one of: {', '.join(STATUSES)}", 400)
    if date_applied is not None and not isinstance(date_applied, str):
        return error("date_applied must be a string (YYYY-MM-DD)", 400)
    if not isinstance(notes, str):
        return error("notes must be a string", 400)

    application_id = db.add_application(
        session["user_id"], company, role, status, date_applied, notes
    )
    if application_id is None:
        return error("Company not found, create it first via POST /api/v1/companies", 404)

    application = db.get_application(session["user_id"], application_id)
    return jsonify(serialize_application(application)), 201


@api.get("/applications/<int:application_id>")
@api_login_required
def get_application(application_id):
    application = db.get_application(session["user_id"], application_id)
    if application is None:
        return error("Application not found", 404)
    return jsonify(serialize_application(application))


@api.patch("/applications/<int:application_id>")
@api_login_required
def update_application(application_id):
    data = json_body()
    if data is None:
        return error("Request body must be a JSON object", 400)

    current = db.get_application(session["user_id"], application_id)
    if current is None:
        return error("Application not found", 404)

    merged = serialize_application(current)
    for key in ("role", "status", "date_applied", "notes"):
        if key in data:
            merged[key] = data[key]

    if not isinstance(merged["role"], str) or not merged["role"].strip():
        return error("role must be a non-empty string", 400)
    if merged["status"] not in STATUSES:
        return error(f"status must be one of: {', '.join(STATUSES)}", 400)
    for key in ("date_applied", "notes"):
        if merged[key] is not None and not isinstance(merged[key], str):
            return error(f"{key} must be a string", 400)

    db.update_application(
        session["user_id"],
        application_id,
        merged["role"].strip(),
        merged["status"],
        merged["date_applied"],
        merged["notes"],
    )
    updated = db.get_application(session["user_id"], application_id)
    return jsonify(serialize_application(updated))


@api.delete("/applications/<int:application_id>")
@api_login_required
def delete_application(application_id):
    if not db.delete_application(session["user_id"], application_id):
        return error("Application not found", 404)
    return "", 204


@api.delete("/data")
@api_login_required
def clear_data():
    db.clear_companies(session["user_id"])
    return "", 204
