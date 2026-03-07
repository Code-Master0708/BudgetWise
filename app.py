from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
# SECURITY WARNING: Change this to a random secret key for production
app.secret_key = 'budgetwise_secret_key_2026'

# --- DATABASE CONFIGURATION ---
db_config = {
    'host': 'localhost',
    'user': 'root',       
    'password': '',  # <--- UPDATE THIS with your MySQL password
    'database': 'budgetwise_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- ROUTE: HOME ---
@app.route('/')
def home():
    # If user is already logged in, go to dashboard. Otherwise, login page.
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

# --- AUTH ROUTES (LOGIN & REGISTER) ---

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('register.html')

@app.route('/api/login', methods=['POST'])
def login_logic():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Check credentials
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if user:
        # CRITICAL: This line keeps the user logged in!
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({"status": "success", "message": f"Welcome back, {user['username']}!"})
    else:
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401

@app.route('/api/register', methods=['POST'])
def register_logic():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if len(password) < 8:
        return jsonify({"status": "error", "message": "Password must be at least 8 characters long!"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if email exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Email already exists!"}), 400

        # Create new user
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, password))
        conn.commit()
        
        return jsonify({"status": "success", "message": "Account created! Redirecting..."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# --- DASHBOARD ROUTES ---

@app.route('/dashboard')
def dashboard():
    # Protect the route: If not logged in, kick them back to login page
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    return render_template('dashboard.html', username=session.get('username', 'User'))

@app.route('/reports')
def reports_page():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('reports.html', username=session['username'])

# --- NEW API: HANDLE BUDGETS ---
@app.route('/api/budget', methods=['GET', 'POST'])
def handle_budget():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    user_id = session['user_id']
    current_month = datetime.now().strftime('%Y-%m')

    if request.method == 'POST':
        data = request.get_json()
        amount = data.get('amount')
        
        # Insert or Update (ON DUPLICATE KEY UPDATE)
        query = """
            INSERT INTO budgets (user_id, month, amount) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE amount = %s
        """
        cursor.execute(query, (user_id, current_month, amount, amount))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Budget updated!"})

    elif request.method == 'GET':
        # Fetch budget for current month
        cursor.execute("SELECT amount FROM budgets WHERE user_id = %s AND month = %s", (user_id, current_month))
        result = cursor.fetchone()
        conn.close()
        return jsonify({"budget": float(result['amount']) if result else 0})

@app.route('/api/expenses', methods=['GET', 'POST'])
def handle_expenses():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        data = request.get_json()
        query = "INSERT INTO expenses (user_id, date, category, amount, description) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (user_id, data['date'], data['category'], data['amount'], data['description']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Expense added!"})

    elif request.method == 'GET':
        # 1. Get ALL transactions for Reports (or limit 5 for dashboard)
        limit = request.args.get('limit')
        if limit:
            cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY date DESC LIMIT %s", (user_id, int(limit)))
        else:
            cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY date DESC", (user_id,))
        expenses = cursor.fetchall()
        
        # 2. Get Chart Data
        cursor.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id = %s GROUP BY category", (user_id,))
        chart_data = cursor.fetchall()
        
        # 3. Get Totals
        current_month = datetime.now().strftime('%Y-%m')
        
        # Total Spent
        cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = %s AND date LIKE %s", (user_id, f"{current_month}%"))
        res_spent = cursor.fetchone()
        total_spend = res_spent['total'] if res_spent and res_spent['total'] else 0
        
        # Total Budget
        cursor.execute("SELECT amount FROM budgets WHERE user_id = %s AND month = %s", (user_id, current_month))
        res_budget = cursor.fetchone()
        total_budget = res_budget['amount'] if res_budget else 0

        conn.close()
        
        return jsonify({
            "expenses": expenses,
            "chart_data": chart_data,
            "total_spend": float(total_spend),
            "budget": float(total_budget),
            "remaining": float(total_budget) - float(total_spend)
        })
if __name__ == '__main__':
    app.run(debug=True)
