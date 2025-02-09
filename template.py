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

# Define Template Model
class Template(db.Model):
    template_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    template_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Template {self.template_id} for User {self.user_id}>"

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

# Route to Retrieve Fingerprint Templates for Multiple Users
@app.route('/template', methods=['GET'])
def get_templates():
    user_ids = request.args.getlist('user_id')  # Get multiple user IDs from query parameters
    
    if not user_ids:
        return jsonify({"message": "No user IDs provided"}), 400
    
    templates = Template.query.filter(Template.user_id.in_(user_ids)).all()
    
    if not templates:
        return jsonify({"message": "No templates found"}), 404
    
    response = [
        {"user_id": template.user_id, "template_data": template.template_data}
        for template in templates
    ]
    
    return jsonify({
        "templates": response,
        "timestamp": datetime.utcnow().isoformat()
    })

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
