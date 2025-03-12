from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

explorer_bp = Blueprint("explorer", __name__)

@explorer_bp.route("/explorer")
@login_required
def explorer():
    # Check if the current user is attached to at least one workspace.
    if not current_user.workspaces or len(current_user.workspaces) == 0:
        flash("You must have at least one workspace to view bucket details. Please create a workspace.", "error")
        return redirect(url_for("workspace.create_workspace"))
    
    # Dummy bucket data for demonstration.
    buckets = [
        {"name": "Bucket1", "region": "us-east-1", "format": "Parquet", "size": "20 MB"},
        {"name": "Bucket2", "region": "us-west-2", "format": "Delta", "size": "15 MB"}
    ]
    return render_template("core/bucket_explorer.html", buckets=buckets)

@explorer_bp.route("/explorer/add_bucket", methods=["GET", "POST"])
@login_required
def add_bucket():
    # Dummy functionality: Flash a message and redirect back to explorer.
    flash("New bucket added (dummy data).", "success")
    return redirect(url_for("explorer.explorer"))
