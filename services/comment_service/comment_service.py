from flask import Flask, request, jsonify
import sqlite3
import logging
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

AUTH_SERVICE_URL = "http://localhost:5003"


def get_db_connection():
    conn = sqlite3.connect("comments.db")
    conn.row_factory = sqlite3.Row
    return conn


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
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/comments/<int:post_id>", methods=["GET"])
def get_comments(post_id):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    offset = (page - 1) * per_page

    try:
        with get_db_connection() as conn:
            comments = conn.execute(
                "SELECT * FROM comments WHERE post_id = ? LIMIT ? OFFSET ?",
                (post_id, per_page, offset),
            ).fetchall()
            total = conn.execute(
                "SELECT COUNT(*) FROM comments WHERE post_id = ?", (post_id,)
            ).fetchone()[0]

        return jsonify(
            {
                "comments": [dict(comment) for comment in comments],
                "total": total,
                "page": page,
                "per_page": per_page,
            }
        )
    except Exception as e:
        logging.error(f"Error fetching comments: {str(e)}")
        return jsonify({"error": "Failed to fetch comments"}), 500


@app.route("/comments", methods=["POST"])
def add_comment():
    data = request.json
    if (
        not data
        or "post_id" not in data
        or "content" not in data
        or "token" not in data
    ):
        return jsonify(
            {
                "error": "Invalid request. 'post_id', 'content', and 'token' are required."
            }
        ), 400

    user_data = validate_token(data["token"])
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO comments (post_id, content, author) VALUES (?, ?, ?)",
                (data["post_id"], data["content"], user_data["username"]),
            )
            conn.commit()
            comment_id = cursor.lastrowid

        return jsonify({"id": comment_id, "message": "Comment added successfully"}), 201
    except Exception as e:
        logging.error(f"Error adding comment: {str(e)}")
        return jsonify({"error": "Failed to add comment"}), 500


@app.route("/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    token = request.json.get("token")
    if not token:
        return jsonify({"error": "Token is required"}), 400

    user_data = validate_token(token)
    if not user_data:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        with get_db_connection() as conn:
            # Check if the user is the author of the comment
            comment = conn.execute(
                "SELECT author FROM comments WHERE id = ?", (comment_id,)
            ).fetchone()
            if not comment or comment["author"] != user_data["username"]:
                return jsonify({"error": "Unauthorized to delete this comment"}), 403

            conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
            conn.commit()

        return jsonify({"message": "Comment deleted successfully"})
    except Exception as e:
        logging.error(f"Error deleting comment: {str(e)}")
        return jsonify({"error": "Failed to delete comment"}), 500


if __name__ == "__main__":
    app.run(port=5005)
