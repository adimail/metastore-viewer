from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Workspace, TableMetadata

explorer_bp = Blueprint("explorer", __name__)

@explorer_bp.route("/explorer")
@login_required
def explorer():
    # Ensure user has a workspace
    if not current_user.workspaces:
        flash("You must be part of a workspace to explore buckets.", "error")
        return redirect(url_for("workspace.create_workspace"))

    # Get the first workspace as the bucket (simplifying for now)
    workspace = Workspace.query.first()
    if not workspace:
        flash("No workspaces found. Please create one.", "error")
        return redirect(url_for("workspace.create_workspace"))

    # Fetch all tables under this workspace (acting as bucket contents)
    tables = TableMetadata.query.filter_by(workspace_id=workspace.id).all()

    return render_template("core/bucket_explorer.html", bucket=workspace, tables=tables)
