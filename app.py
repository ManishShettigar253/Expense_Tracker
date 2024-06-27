from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['expense_tracker']
users = db.users
expenses = db.expenses

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = users.find_one({'email': email})
        if user_data and check_password_hash(user_data['password'], password):
            user = User(user_data['email'], user_data['password'], user_data['_id'])
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('welcome'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if users.find_one({'email': email}) is None:
            user_id = users.insert_one({'email': email, 'password': password}).inserted_id
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already registered.', 'error')
    return render_template('register.html')

@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html', email=current_user.email)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        user_id = ObjectId(current_user.get_id())
        expenses.insert_one({'user_id': user_id, 'amount': amount, 'category': category, 'description': description})
        flash('Expense added successfully!', 'success')
        return redirect(url_for('add_expense'))
    return render_template('add_expense.html')

@app.route('/report')
@login_required
def report():
    user_id = ObjectId(current_user.get_id())
    user_expenses = list(expenses.find({'user_id': user_id}))
    return render_template('report.html', expenses=user_expenses)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
