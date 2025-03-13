from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Workspace, WorkspaceUser
from werkzeug.security import generate_password_hash

settings_bp = Blueprint('settings', __name__)

# General settings page (lists profile settings & workspaces with admin/editor role)
@settings_bp.route('/settings')
@login_required
def settings():
    workspaces = Workspace.query.join(WorkspaceUser).filter(
        WorkspaceUser.user_id == current_user.id,
        WorkspaceUser.role.in_(["admin", "editor"])
    ).all()
    return render_template('settings/settings.html', workspaces=workspaces)

# User profile settings (change username, password, leave workspace)
@settings_bp.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def profile_settings():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')

        if new_username:
            current_user.username = new_username
        
        if new_password:
            current_user.password = generate_password_hash(new_password, method="pbkdf2:sha256")

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('settings.profile_settings'))

    workspaces = Workspace.query.join(WorkspaceUser).filter(
        WorkspaceUser.user_id == current_user.id
    ).all()
    return render_template('settings/profile_settings.html', workspaces=workspaces)


@login_required
@settings_bp.route("/leave_workspace/<int:workspace_id>", methods=["POST"])
def leave_workspace(workspace_id):
    workspace_user = WorkspaceUser.query.filter_by(
        user_id=current_user.id, workspace_id=workspace_id
    ).first()

    if not workspace_user:
        flash("You are not part of this workspace.", "danger")
        return redirect(url_for("settings.settings"))

    if workspace_user.role == "admin":
        flash("You cannot leave this workspace because you are an admin. "
              "Please delete the workspace first.", "warning")
        return redirect(url_for("settings.settings"))

    db.session.delete(workspace_user)
    db.session.commit()

    flash("You have successfully left the workspace.", "success")
    return redirect(url_for("settings.settings"))

@login_required
@settings_bp.route("/delete_workspace/<int:workspace_id>", methods=["POST"])
def delete_workspace(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)

    workspace_user = WorkspaceUser.query.filter_by(
        user_id=current_user.id, workspace_id=workspace_id
    ).first()

    if not workspace_user or workspace_user.role != "admin":
        flash("You do not have permission to delete this workspace.", "danger")
        return redirect(url_for("settings.settings"))

    WorkspaceUser.query.filter_by(workspace_id=workspace_id).delete()

    db.session.delete(workspace)
    db.session.commit()

    flash("Workspace successfully deleted.", "success")
    return redirect(url_for("settings.settings"))


@settings_bp.route("/settings/<int:workspace_id>", methods=["GET", "POST"])
@login_required
def workspace_settings(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)

    ws_user = WorkspaceUser.query.filter_by(
        user_id=current_user.id, workspace_id=workspace.id
    ).first()
    if not ws_user or ws_user.role not in ["admin", "editor"]:
        flash("You do not have permission to update this workspace.", "error")
        return redirect(url_for("home.home"))

    if request.method == "POST":
        workspace.name = request.form.get("name", workspace.name)
        workspace.status = request.form.get("status", workspace.status)
        workspace.region = request.form.get("region", workspace.region)
        workspace.cloud = request.form.get("cloud", workspace.cloud)
        
        workspace.endpoint_url = request.form.get("endpoint_url", workspace.endpoint_url)
        workspace.storage_access_key = request.form.get("storage_access_key", workspace.storage_access_key)
        workspace.storage_secret_key = request.form.get("storage_secret_key", workspace.storage_secret_key)
        workspace.default_bucket_name = request.form.get("default_bucket_name", workspace.default_bucket_name)
        
        workspace.trino_url = request.form.get("trino_url", workspace.trino_url)
        workspace.trino_user = request.form.get("trino_user", workspace.trino_user)
        workspace.trino_password = request.form.get("trino_password", workspace.trino_password)
        
        db.session.commit()
        flash("Workspace settings updated successfully!", "success")
        return redirect(url_for("settings.workspace_settings", workspace_id=workspace.id))

    return render_template("settings/workspace_settings.html", workspace=workspace)
