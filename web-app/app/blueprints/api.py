from flask import Blueprint

api_bp = Blueprint("api", __name__)


@api_bp.route("/test")
def api_test():
    return "API blueprint is set up!"
