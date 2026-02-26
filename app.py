from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MOCK DATABASE - Empty initially
users_data = []

# Database connection (only used when deployed to Azure)
def get_db_connection():
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except:
        return None

# Create table (only for Azure deployment)
def init_db():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100)
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()

# READ - Display all users
@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()
        cur.close()
        conn.close()
    else:
        users = users_data
    return render_template('index.html', users=users)

# CREATE - Add new user
@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO users (name, email) VALUES (%s, %s)', (name, email))
            conn.commit()
            cur.close()
            conn.close()
        else:
            new_id = len(users_data) + 1
            users_data.append((new_id, name, email))
        
        return redirect(url_for('index'))
    return render_template('form.html')

# UPDATE - Edit user
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute('UPDATE users SET name=%s, email=%s WHERE id=%s', (name, email, id))
            conn.commit()
            cur.close()
            conn.close()
        else:
            for i, user in enumerate(users_data):
                if user[0] == id:
                    users_data[i] = (id, name, email)
        
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE id=%s', (id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
    else:
        user = None
        for u in users_data:
            if u[0] == id:
                user = u
    
    return render_template('form.html', user=user)

# DELETE - Remove user
@app.route('/delete/<int:id>')
def delete_user(id):
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE id=%s', (id,))
        conn.commit()
        cur.close()
        conn.close()
    else:
        global users_data
        users_data = [user for user in users_data if user[0] != id]
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)