from flask import Flask, request, redirect, url_for, flash, jsonify, make_response
from werkzeug.exceptions import abort
import requests
import logging
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your secret key")

POST_SERVICE_URL = os.environ.get("POST_SERVICE_URL", "http://localhost:5002")
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:5003")
TEMPLATE_SERVICE_URL = os.environ.get("TEMPLATE_SERVICE_URL", "http://localhost:5004")
COMMENT_SERVICE_URL = os.environ.get("COMMENT_SERVICE_URL", "http://localhost:5005")

logging.basicConfig(level=logging.INFO)


def get_token():
    return request.cookies.get("token")


def render_template(template_name, **context):
    try:
        response = requests.post(
            f"{TEMPLATE_SERVICE_URL}/render",
            json={"template": template_name, "context": context},
        )
        response.raise_for_status()
        return response.json()["rendered"]
    except requests.RequestException as e:
        logging.error(f"Template service error: {str(e)}")
        abort(500, description="Error rendering template")


@app.route("/health")
def health():
    services = {
        "post": POST_SERVICE_URL,
        "auth": AUTH_SERVICE_URL,
        "template": TEMPLATE_SERVICE_URL,
        "comment": COMMENT_SERVICE_URL,
    }
    health_status = {}
    for service, url in services.items():
        try:
            response = requests.get(f"{url}/health")
            health_status[service] = (
                "healthy" if response.status_code == 200 else "unhealthy"
            )
        except requests.RequestException:
            health_status[service] = "unhealthy"

    overall_health = (
        "healthy"
        if all(status == "healthy" for status in health_status.values())
        else "unhealthy"
    )
    return jsonify({"status": overall_health, "services": health_status})


@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    try:
        response = requests.get(f"{POST_SERVICE_URL}/?page={page}")
        response.raise_for_status()
        data = response.json()
        return render_template(
            "index.html",
            posts=data["posts"],
            page=data["page"],
            total_pages=data["total_pages"],
        )
    except requests.RequestException as e:
        logging.error(f"Post service error: {str(e)}")
        abort(500, description="Error fetching posts")


@app.route("/<int:post_id>")
def post(post_id):
    try:
        post_response = requests.get(f"{POST_SERVICE_URL}/{post_id}")
        post_response.raise_for_status()
        post = post_response.json()

        page = request.args.get("page", 1, type=int)
        comments_response = requests.get(
            f"{COMMENT_SERVICE_URL}/comments/{post_id}?page={page}"
        )
        comments_response.raise_for_status()
        comments_data = comments_response.json()

        return render_template(
            "post.html",
            post=post,
            comments=comments_data["comments"],
            page=comments_data["page"],
            total_pages=comments_data["total_pages"],
        )
    except requests.RequestException as e:
        logging.error(f"Service error: {str(e)}")
        abort(500, description="Error fetching post or comments")


@app.route("/create", methods=("GET", "POST"))
def create():
    token = get_token()
    if not token:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            try:
                response = requests.post(
                    f"{POST_SERVICE_URL}/create",
                    json={"title": title, "content": content, "token": token},
                )
                response.raise_for_status()
                return redirect(url_for("index"))
            except requests.RequestException as e:
                logging.error(f"Post service error: {str(e)}")
                flash("An error occurred while creating the post.")

    return render_template("create.html")


@app.route("/<int:id>/edit", methods=("GET", "POST"))
def edit(id):
    token = get_token()
    if not token:
        return redirect(url_for("login"))

    try:
        response = requests.get(f"{POST_SERVICE_URL}/{id}")
        response.raise_for_status()
        post = response.json()

        if request.method == "POST":
            title = request.form["title"]
            content = request.form["content"]

            if not title:
                flash("Title is required!")
            else:
                response = requests.put(
                    f"{POST_SERVICE_URL}/{id}/edit",
                    json={"title": title, "content": content, "token": token},
                )
                response.raise_for_status()
                return redirect(url_for("index"))
    except requests.RequestException as e:
        logging.error(f"Post service error: {str(e)}")
        flash("An error occurred while updating the post.")

    return render_template("edit.html", post=post)


@app.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    token = get_token()
    if not token:
        return redirect(url_for("login"))

    try:
        response = requests.delete(
            f"{POST_SERVICE_URL}/{id}/delete", json={"token": token}
        )
        response.raise_for_status()
        flash(
            '"{}" was successfully deleted!'.format(
                response.json().get("title", "Post")
            )
        )
    except requests.RequestException as e:
        logging.error(f"Post service error: {str(e)}")
        flash("An error occurred while deleting the post.")
    return redirect(url_for("index"))


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            response = requests.post(
                f"{AUTH_SERVICE_URL}/login",
                json={"username": username, "password": password},
            )
            response.raise_for_status()
            token = response.json()["token"]
            resp = make_response(redirect(url_for("index")))
            resp.set_cookie(
                "token", token, httponly=True, secure=True, samesite="Strict"
            )
            return resp
        except requests.RequestException as e:
            logging.error(f"Auth service error: {str(e)}")
            flash("Invalid credentials or service error")
    return render_template("login.html")


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            response = requests.post(
                f"{AUTH_SERVICE_URL}/register",
                json={"username": username, "password": password},
            )
            response.raise_for_status()
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
        except requests.RequestException as e:
            logging.error(f"Auth service error: {str(e)}")
            flash("Registration failed. " + response.json().get("message", ""))
    return render_template("register.html")


@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("token")
    return resp


@app.route("/add_comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    token = get_token()
    if not token:
        return redirect(url_for("login"))

    content = request.form["content"]
    try:
        response = requests.post(
            f"{COMMENT_SERVICE_URL}/comments",
            json={"post_id": post_id, "content": content, "token": token},
        )
        response.raise_for_status()
        flash("Comment added successfully.")
    except requests.RequestException as e:
        logging.error(f"Comment service error: {str(e)}")
        flash("An error occurred while adding the comment.")
    return redirect(url_for("post", post_id=post_id))


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}, Path: {request.path}")
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
