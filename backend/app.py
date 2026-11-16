from flask import Flask
from routes.example import example_bp
from routes.auth import auth_bp
from routes.users import users_bp
import db
from models.user import User

app = Flask(__name__)
app.register_blueprint(example_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    db.clear_relations()
    db.create_relations()
    u1 = User(None,"Alice", "A", "1234567890", "jd@gmail.com", "female", "This is my description.", 2028, "Computer Science", None, None, "PA", "18940", 40.22840, -74.93234, None, None)
    u2 = User(None,"Bob", "B", "1234567890", "jd@gmail.com", "male", "This is my description.", 2028, "Computer Science", None, None, "PA", "18940", 39.95287, -75.16548, None, None)
    u3 = User(None,"Charlie", "C", "1234567890", "jd@gmail.com", "male", "This is my description.", 2028, "Computer Science", None, None, "PA", "18940", 40.06967, -75.12552, None, None)
    app.run(host="0.0.0.0",debug=True,port=8000)
