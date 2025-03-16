from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
import secrets
from datetime import timedelta

secret_key = os.urandom(24)
jwt_secret_key = secrets.token_hex(24)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fashion.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key
app.config['JWT_SECRET_KEY'] = jwt_secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=4)  

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

@app.route('/')
def home():
    return render_template('index2.html')

@app.route('/login/')
def login_page():
    return render_template('login.html')

@app.route('/signup/')
def signup_page():
    return render_template('signup.html')

@app.route('/products')
def products_page():
    return render_template('products.html')

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/account')
@jwt_required()
def account_page():
    return render_template('account.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Error registering user"}), 500
    
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/users', methods=['GET'])
def list_users():
    users = User.query.all()
    user_list = [{'id': user.id, 'username': user.username} for user in users]
    return jsonify(user_list), 200

@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('fashion.db'):
            db.create_all()
            print("Database created!")
    app.run(host='127.0.0.1', port=8080, debug=True)

    