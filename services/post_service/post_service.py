from flask import Flask, jsonify, request
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DB_SERVICE_URL = "http://localhost:5001"
AUTH_SERVICE_URL = "http://localhost:5003"


def validate_token(token):
    try:
        response = requests.post(f"{AUTH_SERVICE_URL}/validate", json={"token": token})
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        logging.error(f"Error validating token: {str(e)}")
        return None


@app.route("/health", methods=["GET"])
def health_check():
    db_health = requests.get(f"{DB_SERVICE_URL}/health").json()
    auth_health = requests.get(f"{AUTH_SERVICE_URL}/health").json()
    if db_health["status"] == "healthy" and auth_health["status"] == "healthy":
        return jsonify({"status": "healthy"}), 200
    return jsonify({"status": "unhealthy"}), 500


@app.route("/")
def index():
    try:
        response = requests.get(f"{DB_SERVICE_URL}/posts")
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        logging.error(f"Error fetching posts: {str(e)}")
        return jsonify({"error": "Failed to fetch posts"}), 500


@app.route("/<int:post_id>")
def post(post_id):
    try:
        response = requests.get(f"{DB_SERVICE_URL}/posts/{post_id}")
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        logging.error(f"Error fetching post {post_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch post"}), 500


@app.route("/create", methods=["POST"])
def create():
    data = request.json
    user_data = validate_token(data.get("token"))
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        response = requests.post(
            f"{DB_SERVICE_URL}/posts",
            json={
                "title": data["title"],
                "content": data["content"],
                "author": user_data["user"],
            },
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        logging.error(f"Error creating post: {str(e)}")
        return jsonify({"error": "Failed to create post"}), 500


@app.route("/<int:post_id>/edit", methods=["PUT"])
def edit(post_id):
    data = request.json
    user_data = validate_token(data.get("token"))
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        response = requests.put(
            f"{DB_SERVICE_URL}/posts/{post_id}",
            json={
                "title": data["title"],
                "content": data["content"],
                "author": user_data["user"],
            },
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        logging.error(f"Error updating post {post_id}: {str(e)}")
        return jsonify({"error": "Failed to update post"}), 500


@app.route("/<int:post_id>/delete", methods=["DELETE"])
def delete(post_id):
    data = request.json
    user_data = validate_token(data.get("token"))
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        response = requests.delete(f"{DB_SERVICE_URL}/posts/{post_id}")
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        logging.error(f"Error deleting post {post_id}: {str(e)}")
        return jsonify({"error": "Failed to delete post"}), 500


if __name__ == "__main__":
    app.run(port=5002)
