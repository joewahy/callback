from flask import render_template, request, redirect, url_for, jsonify, session

from . import app, db
from .auth import login_required

@app.route("/", methods=['GET', 'POST'])
@login_required
def main():
    user_id = session['user_id']

    if request.method == 'POST':
        form_type = request.form['form_type']
        if form_type == 'add_company':
            if request.form.get('name').title() != '':
                db.add_company(user_id, request.form.get('name'))
        elif form_type == 'add_application':
            if request.form.get('role') != '':
                db.add_application(
                    user_id,
                    request.form.get('name'),
                    request.form.get('role'),
                    request.form.get('status'),
                    request.form.get('date_applied'),
                    request.form.get('notes')
                )
        elif form_type == 'clear_database':
            db.clear_companies(user_id)
            return redirect(url_for('main', cleared='true'))
        return redirect(url_for('main'))

    companies = db.get_all_companies(user_id)
    applications = db.get_all_applications(user_id)
    return render_template('index.html', companies=companies, applications=applications)

@app.route("/update", methods=['POST'])
@login_required
def update():
    user_id = session['user_id']
    data = request.get_json()
    db.update_application(
        user_id,
        data['id'],
        data['role'],
        data['status'],
        data['date_applied'],
        data['notes']
    )
    return jsonify({'success': True})
