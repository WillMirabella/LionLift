from flask import Flask
from routes.example import example_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
import db

app = Flask(__name__)
app.register_blueprint(example_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
