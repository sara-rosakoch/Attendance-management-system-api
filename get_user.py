from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ladyb:newpassword@localhost:5432/mynewdatabase"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User Model
class User(db.Model):
    __tablename__ = 'users'  # Rename table to avoid conflict with reserved keyword
    id = db.Column("user_id", db.Integer, primary_key=True, autoincrement=True)
  # Renamed from user_id to id
    name = db.Column(db.String(150), nullable=False)  # User ID provided during creation
    tags = db.Column(JSONB, default=list)  # List of tags associated with the user
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())  # Timestamp when the user was created

    def __repr__(self):
        return f"<User {self.name}>"

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

# Route to Get User IDs Filtered by Tags
@app.route('/get-users', methods=['GET'])
def get_users_by_tags():
    tags = request.args.get('tags')
    if not tags:
        return jsonify({"message": "Tags parameter is required"}), 400
    
    tags_list = tags.split(',')  # Convert comma-separated string to list
    users = User.query.filter(User.tags.op('@>')(db.func.to_jsonb(tags_list))).all()
    user_ids = [user.id for user in users]  # Ensure this is using 'id'

    response = {
        "id": "device123",
        "ts": datetime.utcnow().isoformat() + "Z",
        "kid": "key123",
        "res": {"user_ids": user_ids},
        "sig": "signature456"
    }
    
    return jsonify(response)

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
