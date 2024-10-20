import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("database.db")
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
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/posts", methods=["GET"])
def get_posts():
    try:
        with get_db_connection() as conn:
            posts = conn.execute("SELECT * FROM posts").fetchall()
        return jsonify([dict(post) for post in posts])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/posts/<int:post_id>", methods=["GET"])
def get_post(post_id):
    try:
        with get_db_connection() as conn:
            post = conn.execute(
                "SELECT * FROM posts WHERE id = ?", (post_id,)
            ).fetchone()
        if post is None:
            return jsonify({"error": "Post not found"}), 404
        return jsonify(dict(post))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/posts", methods=["POST"])
def create_post():
    if not request.json or "title" not in request.json:
        return jsonify({"error": "Bad request"}), 400
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO posts (title, content) VALUES (?, ?)",
                (request.json["title"], request.json.get("content", "")),
            )
            conn.commit()
            post_id = cursor.lastrowid
        return jsonify({"id": post_id, "message": "Post created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    if not request.json:
        return jsonify({"error": "Bad request"}), 400
    try:
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE posts SET title = ?, content = ? WHERE id = ?",
                (request.json.get("title"), request.json.get("content"), post_id),
            )
            conn.commit()
        return jsonify({"message": "Post updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
            conn.commit()
        return jsonify({"message": "Post deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001)
