from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# MySQL Configuration using environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': os.getenv('DB_PORT', 3306)
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def home():
    return render_template('homepage.html')

# Book Request Form
@app.route('/request_book', methods=['GET', 'POST'])
def request_book():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        title = request.form['bookTitle']
        author = request.form['author']
        description = request.form['description']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO library_db (student_name, email, book_title, author, description, status) 
                       VALUES (%s, %s, %s, %s, %s, 'pending')''', 
                    (name, email, title, author, description))
        conn.commit()
        cur.close()
        conn.close()
        return render_template('confirmation.html', name=name)
    return render_template('request_book.html')

# User view to check request status
@app.route('/check_status', methods=['GET', 'POST'])
def check_status():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM library_db WHERE email = %s", (email,))
        requests = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('check_status.html', requests=requests)
    return render_template('check_status.html', requests=None)

# Admin Login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'swathi123':
            session['admin'] = True
            return redirect('/admin')
        else:
            return "Invalid credentials. Try again."
    return render_template('admin_login.html')

# Admin Panel
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('admin'):
        return redirect('/admin_login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        request_id = request.form['request_id']
        new_status = request.form['status']
        expected_date = request.form.get('expected_date') or None
        update_query = "UPDATE library_db SET status = %s, expected_date = %s WHERE request_id = %s"
        cursor.execute(update_query, (new_status, expected_date, request_id))
        conn.commit()

    cursor.execute("SELECT * FROM library_db")
    requests = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_requests.html', requests=requests)

@app.route('/admin_request')
def admin_request():
    if not session.get('admin'):
        return redirect('/admin_login')
    return redirect('/admin')

@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    if request.method == 'POST':
        reg = request.form['reg_no']
        department = request.form['department']
        year = request.form['year']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''INSERT INTO book_request (reg, department, year) VALUES (%s, %s, %s)''', (reg, department, year))
        conn.commit()
        cur.close()
        conn.close()
        return render_template('request_book.html')
    return render_template('confirmation.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
