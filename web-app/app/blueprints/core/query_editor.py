from flask import Blueprint, render_template

query_editor_bp = Blueprint("query_editor", __name__)

@query_editor_bp.route("/query-editor")
def query_editor():
    return render_template("core/query_editor.html")
