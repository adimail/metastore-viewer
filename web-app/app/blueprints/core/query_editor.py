from flask import Blueprint, render_template
from flask_login import login_required

query_editor_bp = Blueprint("query_editor", __name__)


@query_editor_bp.route("/query-editor")
@login_required
def query_editor():
    return render_template("core/query_editor.html")
