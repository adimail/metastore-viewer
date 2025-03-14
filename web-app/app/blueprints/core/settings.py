from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Workspace, WorkspaceUser, Bucket, TableMetadata
from werkzeug.security import generate_password_hash

settings_bp = Blueprint("settings", __name__)


# General settings page (lists profile settings & workspaces with admin/editor role)
@settings_bp.route("/settings")
@login_required
def settings():
    workspaces = (
        Workspace.query.join(WorkspaceUser)
        .filter(
            WorkspaceUser.user_id == current_user.id,
            WorkspaceUser.role.in_(["admin", "editor"]),
        )
        .all()
    )
    return render_template("settings/settings.html", workspaces=workspaces)


# User profile settings (change username, password, leave workspace)
@settings_bp.route("/settings/profile", methods=["GET", "POST"])
@login_required
def profile_settings():
    if request.method == "POST":
        new_username = request.form.get("username")
        new_password = request.form.get("password")

        if new_username:
            current_user.username = new_username

        if new_password:
            current_user.password = generate_password_hash(
                new_password, method="pbkdf2:sha256"
            )

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("settings.profile_settings"))

    workspaces = (
        Workspace.query.join(WorkspaceUser)
        .filter(WorkspaceUser.user_id == current_user.id)
        .all()
    )
    return render_template("settings/profile_settings.html", workspaces=workspaces)


# Leave a workspace
@settings_bp.route("/leave_workspace/<int:workspace_id>", methods=["POST"])
@login_required
def leave_workspace(workspace_id):
    workspace_user = WorkspaceUser.query.filter_by(
        user_id=current_user.id, workspace_id=workspace_id
    ).first()

    if not workspace_user:
        flash("You are not part of this workspace.", "danger")
        return redirect(url_for("settings.settings"))

    if workspace_user.role == "admin":
        flash(
            "You cannot leave this workspace because you are an admin. "
            "Please delete the workspace first.",
            "warning",
        )
        return redirect(url_for("settings.settings"))

    flash("Delete options are prohibited in this prototype.", "danger")
    # db.session.delete(workspace_user)
    # db.session.commit()

    flash("You have successfully left the workspace.", "success")
    return redirect(url_for("settings.settings"))


# Delete a workspace (admin only)
@settings_bp.route("/delete_workspace/<int:workspace_id>", methods=["POST"])
@login_required
def delete_workspace(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)

    workspace_user = WorkspaceUser.query.filter_by(
        user_id=current_user.id, workspace_id=workspace_id
    ).first()

    if not workspace_user or workspace_user.role != "admin":
        flash("You do not have permission to delete this workspace.", "danger")
        return redirect(url_for("settings.settings"))

    flash("Delete options are prohibited in this prototype.", "danger")
    # WorkspaceUser.query.filter_by(workspace_id=workspace_id).delete()
    # db.session.delete(workspace)
    # db.session.commit()

    flash("Workspace successfully deleted.", "success")
    return redirect(url_for("settings.settings"))


# Workspace settings (admin/editor access)
@settings_bp.route("/settings/workspace/<int:workspace_id>", methods=["GET", "POST"])
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
        # Update only Workspace model fields
        workspace.name = request.form.get("name", workspace.name)
        workspace.status = request.form.get("status", workspace.status)
        workspace.trino_url = request.form.get("trino_url", workspace.trino_url)
        workspace.trino_user = request.form.get("trino_user", workspace.trino_user)
        workspace.trino_password = request.form.get(
            "trino_password", workspace.trino_password
        )

        db.session.commit()
        flash("Workspace settings updated successfully!", "success")
        return redirect(
            url_for("settings.workspace_settings", workspace_id=workspace.id)
        )

    return render_template("settings/workspace_settings.html", workspace=workspace)


# -------------------- Bucket Management --------------------


# Add a new bucket
@settings_bp.route("/settings/<int:workspace_id>/add_bucket", methods=["GET", "POST"])
@login_required
def add_bucket(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)

    ws_user = WorkspaceUser.query.filter_by(
        user_id=current_user.id, workspace_id=workspace.id
    ).first()
    if not ws_user or ws_user.role not in ["admin", "editor"]:
        flash("You do not have permission to add a bucket.", "danger")
        return redirect(
            url_for("settings.workspace_settings", workspace_id=workspace.id)
        )

    if request.method == "POST":
        bucket_name = request.form.get("bucket_name")
        cloud_provider = request.form.get("cloud_provider")
        region = request.form.get("region")
        bucket_path = request.form.get("bucket_path")
        endpoint_url = request.form.get("endpoint_url")
        storage_access_key = request.form.get("storage_access_key")
        storage_secret_key = request.form.get("storage_secret_key")

        if not all([bucket_name, cloud_provider, region, bucket_path]):
            flash(
                "Bucket name, cloud provider, region, and bucket path are required.",
                "warning",
            )
            return redirect(url_for("settings.add_bucket", workspace_id=workspace_id))

        new_bucket = Bucket(
            name=bucket_name,
            cloud_provider=cloud_provider,
            region=region,
            bucket_path=bucket_path,
            endpoint_url=endpoint_url or None,
            storage_access_key=storage_access_key or None,
            storage_secret_key=storage_secret_key or None,
            workspace_id=workspace_id,
            status="active",
            storage_class="STANDARD",
        )

        try:
            db.session.add(new_bucket)
            db.session.commit()
            flash("Bucket added successfully.", "success")
            return redirect(
                url_for("settings.workspace_settings", workspace_id=workspace.id)
            )
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding bucket: {str(e)}", "danger")
            return redirect(url_for("settings.add_bucket", workspace_id=workspace_id))

    return render_template("settings/add_bucket.html", workspace=workspace)


# Edit an existing bucket
@settings_bp.route(
    "/settings/<int:workspace_id>/edit_bucket/<int:bucket_id>", methods=["GET", "POST"]
)
@login_required
def edit_bucket(workspace_id, bucket_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    bucket = Bucket.query.get_or_404(bucket_id)

    ws_user = WorkspaceUser.query.filter_by(
        user_id=current_user.id, workspace_id=workspace.id
    ).first()
    if not ws_user or ws_user.role not in ["admin", "editor"]:
        flash("You do not have permission to edit this bucket.", "danger")
        return redirect(
            url_for("settings.workspace_settings", workspace_id=workspace.id)
        )

    if bucket.workspace_id != workspace_id:
        flash("Bucket does not belong to this workspace.", "danger")
        return redirect(
            url_for("settings.workspace_settings", workspace_id=workspace.id)
        )

    if request.method == "POST":
        bucket.name = request.form.get("bucket_name", bucket.name)
        bucket.cloud_provider = request.form.get(
            "cloud_provider", bucket.cloud_provider
        )
        bucket.region = request.form.get("region", bucket.region)
        bucket.bucket_path = request.form.get("bucket_path", bucket.bucket_path)
        bucket.endpoint_url = (
            request.form.get("endpoint_url", bucket.endpoint_url) or None
        )
        bucket.storage_access_key = (
            request.form.get("storage_access_key", bucket.storage_access_key) or None
        )
        bucket.storage_secret_key = (
            request.form.get("storage_secret_key", bucket.storage_secret_key) or None
        )

        if not all(
            [bucket.name, bucket.cloud_provider, bucket.region, bucket.bucket_path]
        ):
            flash(
                "Bucket name, cloud provider, region, and bucket path cannot be empty.",
                "warning",
            )
            return redirect(
                url_for(
                    "settings.edit_bucket",
                    workspace_id=workspace_id,
                    bucket_id=bucket_id,
                )
            )

        try:
            db.session.commit()
            flash("Bucket details updated successfully.", "success")
            return redirect(
                url_for("settings.workspace_settings", workspace_id=workspace.id)
            )
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating bucket: {str(e)}", "danger")
            return redirect(
                url_for(
                    "settings.edit_bucket",
                    workspace_id=workspace_id,
                    bucket_id=bucket_id,
                )
            )

    # GET request: Render the edit bucket page
    return render_template(
        "settings/edit_bucket.html", workspace=workspace, bucket=bucket
    )


# Delete a bucket
@settings_bp.route(
    "/settings/<int:workspace_id>/delete_bucket/<int:bucket_id>", methods=["POST"]
)
@login_required
def delete_bucket(workspace_id, bucket_id):
    try:
        workspace = Workspace.query.get_or_404(workspace_id)
        bucket = Bucket.query.get_or_404(bucket_id)

        # Debug user permissions
        ws_user = WorkspaceUser.query.filter_by(
            user_id=current_user.id, workspace_id=workspace.id
        ).first()
        print(f"User: {current_user.id}, Role: {ws_user.role if ws_user else 'None'}")
        if not ws_user or ws_user.role not in ["admin", "editor"]:
            flash("You do not have permission to delete this bucket.", "danger")
            return redirect(
                url_for("settings.workspace_settings", workspace_id=workspace.id)
            )

        print(
            f"Bucket Workspace ID: {bucket.workspace_id}, Requested Workspace ID: {workspace_id}"
        )
        if bucket.workspace_id != workspace_id:
            flash("Bucket does not belong to this workspace.", "danger")
            return redirect(
                url_for("settings.workspace_settings", workspace_id=workspace.id)
            )

        tables = TableMetadata.query.filter_by(bucket_id=bucket_id).all()
        print(f"Related tables: {len(tables)}")

        flash("Delete options are prohibited in this prototype.", "danger")
        # db.session.delete(bucket)
        # db.session.commit()
        # flash("Bucket removed successfully.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting bucket: {str(e)}")
        flash(f"Failed to delete bucket: {str(e)}", "danger")

    return redirect(url_for("settings.workspace_settings", workspace_id=workspace.id))
