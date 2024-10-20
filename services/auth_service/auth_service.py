from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import jwt
import datetime
import logging

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
logging.basicConfig(level=logging.INFO)


def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/health", methods=["GET"])
def health_check():
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data["username"]
    password = data["password"]

    try:
        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            if user:
                return jsonify({"message": "User already exists"}), 400

            hashed_password = generate_password_hash(password)
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password),
            )
            conn.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        logging.error(f"Error during registration: {str(e)}")
        return jsonify({"message": "Registration failed"}), 500


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    try:
        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):
            token = jwt.encode(
                {
                    "user_id": user["id"],
                    "username": username,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
                },
                app.config["SECRET_KEY"],
                algorithm="HS256",
            )
            return jsonify({"token": token})

        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        return jsonify({"message": "Login failed"}), 500


@app.route("/validate", methods=["POST"])
def validate_token():
    token = request.json["token"]
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return jsonify(
            {"valid": True, "user_id": data["user_id"], "username": data["username"]}
        ), 200
    except jwt.ExpiredSignatureError:
        logging.warning("Expired token")
        return jsonify({"valid": False, "message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        logging.warning("Invalid token")
        return jsonify({"valid": False, "message": "Invalid token"}), 401
    except Exception as e:
        logging.error(f"Error during token validation: {str(e)}")
        return jsonify({"valid": False, "message": "Token validation failed"}), 500


if __name__ == "__main__":
    app.run(port=5003)
