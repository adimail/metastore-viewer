from flask import Blueprint, render_template

metadata_bp = Blueprint("metadata", __name__)

@metadata_bp.route("/metadata")
def metadata():
    return render_template("core/table_metadata_viewer.html")
