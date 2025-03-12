from flask import Blueprint, render_template

explorer_bp = Blueprint("explorer", __name__)

@explorer_bp.route("/explorer")
def explorer():
    return render_template("core/bucket_explorer.html")
