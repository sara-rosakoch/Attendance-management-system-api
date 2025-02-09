from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy # type: ignore
from datetime import datetime

app = Flask(__name__)

# Database Configuration (Ensure PostgreSQL is running & credentials are correct)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ladyb:newpassword@localhost:5432/mynewdatabase"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<User {self.username}>"

# Define Attendance Model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

# Create tables if they don't exist
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating tables: {e}")

# Home Route (Fixes 404 error on '/')
@app.route('/')
def home():
    return "Welcome to the User API!"

# Route to Create a New User
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')

    # Check if username or email exists
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    # Create and save new user
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email}}), 201

# Route to Get All Users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = [{"id": user.id, "username": user.username, "email": user.email, "created_at": user.created_at} for user in users]
    return jsonify(result)

# Route to Get a Specific User by ID
@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({"id": user.id, "username": user.username, "email": user.email, "created_at": user.created_at})

# Route to Update a User by ID
@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()

    # Update username if provided
    if 'username' in data:
        if User.query.filter(User.username == data['username'], User.id != id).first():
            return jsonify({"message": "Username already exists"}), 400
        user.username = data['username']

    # Update email if provided
    if 'email' in data:
        if User.query.filter(User.email == data['email'], User.id != id).first():
            return jsonify({"message": "Email already exists"}), 400
        user.email = data['email']

    db.session.commit()
    return jsonify({"message": "User updated successfully", "user": {"id": user.id, "username": user.username, "email": user.email}})

# Route to Delete a User by ID
@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})

# Route to Mark Attendance
@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    device_id = data.get("id")
    timestamp = data.get("ts")
    payload = data.get("pd", {})
    user_ids = payload.get("user_ids", [])
    timestamps = payload.get("timestamps", [])
    signature = data.get("sig")

    if not all([device_id, timestamp, user_ids, timestamps, signature]) or len(user_ids) != len(timestamps):
        return jsonify({"message": "Invalid request format"}), 400

    try:
        for user_id, ts in zip(user_ids, timestamps):
            attendance_entry = Attendance(user_id=user_id, timestamp=datetime.fromisoformat(ts))
            db.session.add(attendance_entry)
        db.session.commit()

        response = {
            "id": device_id,
            "ts": datetime.utcnow().isoformat(),
            "kid": "key123",
            "res": {"status": "success"},
            "sig": "signature456"
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"message": "Error marking attendance", "error": str(e)}), 500

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
