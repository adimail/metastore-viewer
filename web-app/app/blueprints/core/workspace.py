from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Workspace, WorkspaceUser, User
from app.extensions import db
import datetime

workspace_bp = Blueprint("workspace", __name__)


@workspace_bp.route("/workspace/create", methods=["GET", "POST"])
@login_required
def create_workspace():
    if request.method == "POST":
        name = request.form.get("name")
        status = request.form.get("status")
        region = request.form.get("region")
        cloud = request.form.get("cloud")
        catalog = request.form.get("catalog")
        clusters = request.form.get("clusters")
        description = request.form.get("description")

        # Check if workspace with the same name already exists
        if Workspace.query.filter_by(name=name).first():
            flash(
                "Workspace name already exists. Please choose a different name.",
                "error",
            )
            return redirect(url_for("workspace.create_workspace"))

        new_workspace = Workspace(
            name=name,
            status=status,
            region=region,
            cloud=cloud,
            catalog=catalog,
            clusters=clusters,
            description=description,
            created_by_id=current_user.id,
            created_by_name=current_user.username,
            owner_id=current_user.id,
            owner_name=current_user.username,
            created_at=datetime.datetime.utcnow(),
            updated_on=datetime.datetime.utcnow(),
        )
        db.session.add(new_workspace)
        db.session.commit()

        # Add the current user as admin of the newly created workspace
        ws_user = WorkspaceUser(
            user_id=current_user.id, workspace_id=new_workspace.id, role="admin"
        )
        db.session.add(ws_user)
        db.session.commit()

        flash("Workspace created successfully!", "success")
        return redirect(
            url_for("workspace.view_workspace", workspace_id=new_workspace.id)
        )

    return render_template("workspace/create_workspace.html")


@workspace_bp.route("/workspace/<int:workspace_id>")
@login_required
def view_workspace(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    members = WorkspaceUser.query.filter_by(workspace_id=workspace_id).all()
    return render_template(
        "workspace/view_workspace.html", workspace=workspace, members=members
    )


@workspace_bp.route("/workspace/<int:workspace_id>/add_member", methods=["GET", "POST"])
@login_required
def add_member(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    if request.method == "POST":
        username = request.form.get("username")
        role = request.form.get("role")
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("workspace.add_member", workspace_id=workspace_id))
        # Check if the user is already a member.
        if WorkspaceUser.query.filter_by(
            workspace_id=workspace_id, user_id=user.id
        ).first():
            flash("User is already a member of this workspace.", "error")
            return redirect(url_for("workspace.add_member", workspace_id=workspace_id))
        new_member = WorkspaceUser(
            user_id=user.id, workspace_id=workspace_id, role=role
        )
        db.session.add(new_member)
        db.session.commit()
        flash("Member added successfully!", "success")
        return redirect(url_for("workspace.view_workspace", workspace_id=workspace_id))
    return render_template("workspace/add_member.html", workspace=workspace)


@workspace_bp.route("/my_workspaces")
@login_required
def my_workspaces():
    # current_user.workspaces is a list of WorkspaceUser entries.
    # To display the workspace details, we extract the workspace from each association.
    user_workspaces = [ws.workspace for ws in current_user.workspaces]
    return render_template("workspace/my_workspaces.html", workspaces=user_workspaces)


@workspace_bp.route("/workspace/<int:workspace_id>/update", methods=["GET", "POST"])
@login_required
def update_workspace(workspace_id):
    flash(f"Update workspace {workspace_id} feature coming soon!", "info")
    return redirect(url_for("workspace.view_workspace", workspace_id=workspace_id))


@workspace_bp.route("/workspace/<int:workspace_id>/disable", methods=["POST", "GET"])
@login_required
def disable_workspace(workspace_id):
    flash(f"Workspace {workspace_id} has been disabled (simulation).", "warning")
    return redirect(url_for("workspace.view_workspace", workspace_id=workspace_id))


@workspace_bp.route("/workspace/<int:workspace_id>/delete", methods=["POST", "GET"])
@login_required
def delete_workspace(workspace_id):
    flash(f"Workspace {workspace_id} has been deleted (simulation).", "danger")
    return redirect(url_for("home.home"))
