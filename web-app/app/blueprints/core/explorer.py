from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Workspace, WorkspaceUser, Bucket

explorer_bp = Blueprint("explorer", __name__)

@explorer_bp.route("/explorer")
@login_required
def explorer():
    """
    Shows all workspaces that the current user is part of,
    along with the buckets in each workspace.
    """
    # Find all workspace-user associations for the current user
    user_ws = WorkspaceUser.query.filter_by(user_id=current_user.id).all()
    if not user_ws:
        flash("You must be part of at least one workspace to explore buckets.", "error")
        return redirect(url_for("workspace.create_workspace"))

    # Gather the workspace IDs and fetch them
    workspace_ids = [ws.workspace_id for ws in user_ws]
    workspaces = Workspace.query.filter(Workspace.id.in_(workspace_ids)).all()

    return render_template("core/explorer.html", workspaces=workspaces)

@explorer_bp.route("/explorer/bucket/<int:bucket_id>")
@login_required
def view_bucket(bucket_id):
    """
    Shows details for a specific bucket, including its tables, etc.
    """
    bucket = Bucket.query.get_or_404(bucket_id)

    # Ensure the user is part of the workspace that owns this bucket
    ws_user = WorkspaceUser.query.filter_by(user_id=current_user.id, workspace_id=bucket.workspace_id).first()
    if not ws_user:
        flash("You do not have access to this bucket.", "error")
        return redirect(url_for("explorer.explorer"))

    return render_template("core/bucket_details.html", bucket=bucket)
