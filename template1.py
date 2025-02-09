from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ladyb:newpassword@localhost:5432/mynewdatabase"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # Updated to match VARCHAR(50)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Template Model
class Template(db.Model):
    template_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)  # Updated to match VARCHAR(50)
    template_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Fetch Fingerprint Templates for Multiple Users
@app.route('/template', methods=['GET'])
def get_templates():
    user_ids = request.args.getlist('user_id')  # Extract user_id list from query params

    if not user_ids:
        return jsonify({"message": "No user IDs provided"}), 400

    # Clean and remove spaces from user IDs
    user_ids = [user_id.strip() for user_id in user_ids if user_id.strip()]

    # Query templates for the given user IDs
    templates = Template.query.filter(Template.user_id.in_(user_ids)).all()

    if not templates:
        return jsonify({"message": "No templates found"}), 404

    # Format response
    response = [
        {"user_id": template.user_id, "template_data": template.template_data}
        for template in templates
    ]

    return jsonify({
        "templates": response,
        "timestamp": datetime.utcnow().isoformat()
    })

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
