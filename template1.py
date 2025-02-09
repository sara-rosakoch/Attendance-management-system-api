from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ladyb:newpassword@localhost:5432/mynewdatabase"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User Model
class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # Assuming user_id is VARCHAR
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Define Template Model
class Template(db.Model):
    template_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    template_data = db.Column(db.Text, nullable=False)  # Storing Base64 fingerprint data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables if they don't exist
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating tables: {e}")

# Home Route
@app.route('/')
def home():
    return "Welcome to the Fingerprint API!"

@app.route('/get-template', methods=['GET'])
def get_templates():
    try:
        user_ids_str = request.args.get('user_ids')

        if not user_ids_str:
            return jsonify({"message": "Missing 'user_ids' parameter"}), 400

        user_ids = user_ids_str.split(',')
        
        # Debugging: Print the extracted user_ids
        print(f"User IDs Received: {user_ids}")

        templates = Template.query.filter(Template.user_id.in_(user_ids)).all()

        # Debugging: Print fetched templates
        print(f"Fetched Templates: {templates}")

        if not templates:
            return jsonify({"message": "No templates found"}), 404

        response_data = {
            "id": request.args.get("id", "unknown"),
            "ts": datetime.utcnow().isoformat(),
            "kid": "key123",
            "res": {
                "templates": [
                    {
                        "user_id": template.user_id,
                        "template_data": template.template_data
                    }
                    for template in templates
                ]
            },
            "sig": "signature456"
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
