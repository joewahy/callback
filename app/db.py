import sqlite3

def get_connection():
    connect = sqlite3.connect("applications.db")
    connect.execute('PRAGMA foreign_keys = ON')
    return connect

def app_create():
    connect = get_connection()
    cursor = connect.cursor()
    # cursor.execute("DROP TABLE IF EXISTS applications")
    # cursor.execute("DROP TABLE IF EXISTS companies")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            company_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            company_id INTEGER,
            role TEXT,
            status TEXT,
            date_applied TEXT,
            notes TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (company_id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    connect.commit()
    connect.close()

def add_company(user_id, name):
    connect = get_connection()
    cursor = connect.cursor()
    contains = cursor.execute("SELECT name FROM companies WHERE name = ? COLLATE NOCASE AND user_id = ?", (name, user_id))
    if contains.fetchone() is None:
        cursor.execute("""
            INSERT INTO companies (user_id, name) VALUES (?, ?)
        """, (user_id, name))
        print(f"Inserted {name}")
    connect.commit()
    connect.close()

def add_application(user_id, name, role, status, date_applied, notes):
    connect = get_connection()
    cursor = connect.cursor()
    result = cursor.execute("SELECT company_id FROM companies WHERE name = ? COLLATE NOCASE AND user_id = ?", (name, user_id))
    row = result.fetchone()
    if row is None:
        print("add company first")
    else:
        company_id = row[0]
        cursor.execute("""
            INSERT INTO applications (user_id, company_id, role, status, date_applied, notes) VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, company_id, role, status, date_applied, notes,))
        print(f"Inserted application for {name}")
    connect.commit()
    connect.close()

def get_all_companies(user_id):
    connect = get_connection()
    cursor = connect.cursor()
    result = cursor.execute("""
        SELECT companies.company_id, companies.name
        FROM companies
        WHERE companies.user_id = ?
    """, (user_id,))
    data = result.fetchall()
    connect.close()
    return data

def get_all_applications(user_id):
    connect = get_connection()
    cursor = connect.cursor()
    result = cursor.execute("""
                            SELECT applications.id, companies.name, applications.role, applications.status, applications.date_applied, applications.notes
                            FROM applications
                            JOIN companies ON applications.company_id = companies.company_id
                            WHERE applications.user_id = ?
    """, (user_id,))
    data = result.fetchall()
    connect.close()
    return data

def clear_companies(user_id):
    connect = get_connection()
    cursor = connect.cursor()
    cursor.execute("DELETE FROM applications WHERE applications.user_id = ?", (user_id,))
    cursor.execute("DELETE FROM companies WHERE companies.user_id = ?", (user_id,))
    connect.commit()
    connect.close()

def update_application(user_id, application_id, role, status, date_applied, notes):
    connect = get_connection()
    cursor = connect.cursor()
    cursor.execute("""
        UPDATE applications
        SET role = ?, status = ?, date_applied = ?, notes = ?
        WHERE id = ? AND user_id = ?
    """, (role, status, date_applied, notes, application_id, user_id))
    connect.commit()
    connect.close()

def create_user(email, password):
    connect = get_connection()
    cursor = connect.cursor()
    cursor.execute("""
    INSERT INTO users (email, password) VALUES (?, ?)
    """, (email, password,))
    connect.commit()
    connect.close()



def get_user_by_email(email):
    connect = get_connection()
    cursor = connect.cursor()
    result = cursor.execute("""
        SELECT users.id, users.email, users.password
        FROM users
        WHERE users.email = ?
    """,(email,))
    data = result.fetchone()
    connect.close()
    return data
