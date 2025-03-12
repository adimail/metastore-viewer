from flask import Blueprint, render_template
from flask_login import login_required

explorer_bp = Blueprint("explorer", __name__)

@explorer_bp.route("/explorer")
@login_required
def explorer():
    return render_template("core/bucket_explorer.html")
