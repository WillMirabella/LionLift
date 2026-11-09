from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from routes.example import example_bp
from routes.auth import auth_bp
import db

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "secret-string-change-this-later"  # Change this to an environmental var soon
Bcrypt().init_app(app)
JWTManager().init_app(app)

app.register_blueprint(example_bp)
app.register_blueprint(auth_bp)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == '__main__':
    db.create_relations()
    app.run(host="0.0.0.0",debug=True,port=8000)
