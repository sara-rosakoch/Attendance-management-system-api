from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy  # type: ignore
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

# Define Fingerprint Enrollment Model
class Fingerprint(db.Model):
    template_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(150), nullable=False, index=True)
    template_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

# Create tables if they don't exist
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating tables: {e}")

# Home Route
@app.route('/')
def home():
    return "Welcome to the User API!"

# Route to Enroll a User with Fingerprint Template Data
@app.route('/enroll', methods=['POST'])
def enroll_user():
    data = request.get_json()
    
    try:
        device_id = data.get("id")
        timestamp = data.get("ts")
        payload = data.get("pd", {})
        user_id = payload.get("user_id")
        template_data = payload.get("template_data")
        signature = data.get("sig")
        
        if not all([device_id, timestamp, user_id, template_data, signature]):
            return jsonify({"message": "Missing required fields"}), 400
        
        new_fingerprint = Fingerprint(user_id=user_id, template_data=template_data)
        db.session.add(new_fingerprint)
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
        return jsonify({"message": "Error processing request", "error": str(e)}), 500

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
