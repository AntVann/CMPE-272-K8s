from flask import Flask, render_template, request, jsonify
import logging
from jinja2.exceptions import TemplateNotFound

app = Flask(__name__, template_folder="../../templates")
logging.basicConfig(level=logging.INFO)


@app.route("/health", methods=["GET"])
def health_check():
    try:
        # Try to render a simple template to check if the template engine is working
        render_template("base.html")
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/render", methods=["POST"])
def render():
    data = request.json
    if not data or "template" not in data or "context" not in data:
        return jsonify(
            {"error": "Invalid request. 'template' and 'context' are required."}
        ), 400

    template_name = data["template"]
    context = data["context"]

    if not isinstance(context, dict):
        return jsonify({"error": "Invalid context. Must be a dictionary."}), 400

    try:
        rendered_template = render_template(template_name, **context)
        return jsonify({"rendered": rendered_template}), 200
    except TemplateNotFound:
        logging.error(f"Template not found: {template_name}")
        return jsonify({"error": f"Template '{template_name}' not found"}), 404
    except Exception as e:
        logging.error(f"Error rendering template {template_name}: {str(e)}")
        return jsonify({"error": f"Error rendering template: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(port=5004)
