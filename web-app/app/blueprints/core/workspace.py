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
        region = request.form.get("region")
        cloud = request.form.get("cloud")
        catalog = request.form.get("catalog")
        clusters = request.form.get("clusters")
        description = request.form.get("description")

        if Workspace.query.filter_by(name=name).first():
            flash(
                "Workspace name already exists. Please choose a different name.",
                "error",
            )
            return redirect(url_for("workspace.create_workspace"))

        new_workspace = Workspace(
            name=name,
            region=region,
            cloud=cloud,
            catalog=catalog,
            clusters=clusters,
            description=description,
            created_by_id=current_user.id,
            owner_id=current_user.id,
            created_at=datetime.datetime.utcnow(),
            updated_on=datetime.datetime.utcnow(),
        )
        db.session.add(new_workspace)
        db.session.commit()

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

    owner = User.query.get_or_404(workspace.owner_id)
    created_by = User.query.get_or_404(workspace.created_by_id)

    return render_template(
        "workspace/view_workspace.html",
        workspace=workspace,
        members=members,
        owner=owner,
        created_by=created_by,
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
    return render_template("settings/add_workspace_member.html", workspace=workspace)


@workspace_bp.route("/workspace")
@login_required
def workspace():
    # current_user.workspaces is a list of WorkspaceUser entries.
    # To display the workspace details, we extract the workspace from each association.
    user_workspaces = [ws.workspace for ws in current_user.workspaces]
    return render_template("workspace/workspace.html", workspaces=user_workspaces)


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


@workspace_bp.route(
    "/workspace/<int:workspace_id>/remove_member/<int:user_id>", methods=["POST"]
)
@login_required
def remove_member(workspace_id, user_id):
    try:
        # Fetch the workspace
        workspace = Workspace.query.get_or_404(workspace_id)

        # Check if the current user is an admin
        current_ws_user = WorkspaceUser.query.filter_by(
            user_id=current_user.id, workspace_id=workspace_id
        ).first()
        if not current_ws_user or current_ws_user.role != "admin":
            flash(
                "You do not have permission to remove members from this workspace.",
                "danger",
            )
            return redirect(
                url_for("settings.workspace_settings", workspace_id=workspace_id)
            )

        # Prevent removing oneself
        if user_id == current_user.id:
            flash("You cannot remove yourself from the workspace.", "danger")
            return redirect(
                url_for("settings.workspace_settings", workspace_id=workspace_id)
            )

        # Fetch the WorkspaceUser entry to remove
        ws_user = WorkspaceUser.query.filter_by(
            user_id=user_id, workspace_id=workspace_id
        ).first()
        if not ws_user:
            flash("User not found in this workspace.", "danger")
            return redirect(
                url_for("settings.workspace_settings", workspace_id=workspace_id)
            )

        # Delete the WorkspaceUser entry
        db.session.delete(ws_user)
        db.session.commit()

        flash(
            f"User '{ws_user.user.username}' has been removed from the workspace.",
            "success",
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to remove user: {str(e)}", "danger")
        print(f"Error removing user {user_id} from workspace {workspace_id}: {str(e)}")

    return redirect(url_for("settings.workspace_settings", workspace_id=workspace_id))
