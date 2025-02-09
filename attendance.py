from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ladyb:newpassword@localhost:5432/mynewdatabase"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Define Attendance Model
class Attendance(db.Model):
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Attendance {self.user_id} - {self.timestamp}>"

# Create tables if they don't exist
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating tables: {e}")

# Mark Attendance Route
@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    device_id = data.get('id')
    timestamp = data.get('ts')
    payload = data.get('pd', {})
    user_ids = payload.get('user_ids', [])
    timestamps = payload.get('timestamps', [])

    if not device_id or not timestamp or not user_ids or not timestamps:
        return jsonify({"message": "Invalid request payload"}), 400

    if len(user_ids) != len(timestamps):
        return jsonify({"message": "Mismatched user_ids and timestamps"}), 400

    # Save attendance records to the database
    for user_id, ts in zip(user_ids, timestamps):
        attendance = Attendance(user_id=user_id, timestamp=datetime.fromisoformat(ts[:-1]))
        db.session.add(attendance)
    db.session.commit()

    response = {
        "id": device_id,
        "ts": datetime.utcnow().isoformat() + "Z",
        "res": {"status": "success"},
        "sig": "signature456"
    }
    return jsonify(response), 200

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
