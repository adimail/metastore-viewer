from flask import Blueprint, render_template
from flask_login import login_required

metadata_bp = Blueprint("metadata", __name__)

@metadata_bp.route("/metadata")
@login_required
def metadata():
    return render_template("core/table_metadata_viewer.html")
