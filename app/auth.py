from flask import render_template, request, redirect, url_for, session
from functools import wraps
from email_validator import validate_email, EmailNotValidError
import bcrypt

from . import app, db

def login_required(original_function):
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        if "user_id" in session:
            return original_function(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # handle the form submission
        email = request.form.get('email')
        password = request.form.get('password')
        user = db.get_user_by_email(email)
        if user is None or not bcrypt.checkpw(password.encode('utf-8'), user[2]):
            return render_template('login.html', error="Invalid email or password")
        session['user_id'] = user[0]
        return redirect(url_for('main'))
    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if email is None or password is None:
            return render_template('signup.html', error="Invalid email or password")

        try:
            validate_email(email)
        except EmailNotValidError:
            return render_template('signup.html', error="Invalid email")

        if db.get_user_by_email(email):
            return render_template('signup.html', error="Email already taken")

        if password != confirm_password:
            return render_template('signup.html', error="Password does not match")

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        db.create_user(email, hashed_password)
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route("/logout", methods=['POST'])
def logout():
    session.pop("user_id", None)
    return redirect(url_for('login'))
