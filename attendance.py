from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mypassword@localhost/attendance_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Attendance Model
class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    attendance_id = db.Column(db.Integer, primary_key=True)  # Auto-incremented ID
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)  # String type user ID
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "attendance_id": self.attendance_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp
        }

# Create the database tables
with app.app_context():
    db.create_all()

# API Route: Mark Attendance
@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        timestamp = data.get("timestamp", datetime.utcnow())

        # Convert timestamp to datetime if provided as a string
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        attendance = Attendance(user_id=user_id, timestamp=timestamp)
        db.session.add(attendance)
        db.session.commit()

        return jsonify({"message": "Attendance marked successfully", "attendance": attendance.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# API Route: Get All Attendance Records
@app.route('/attendance', methods=['GET'])
def get_attendance():
    attendance_records = Attendance.query.all()
    return jsonify([record.to_dict() for record in attendance_records])

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
