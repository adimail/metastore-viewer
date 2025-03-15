from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import Bucket, WorkspaceUser, Workspace, TableMetadata
import s3fs
from deltalake import DeltaTable
import pyarrow.dataset as ds

metadata_bp = Blueprint('metadata', __name__, url_prefix='/metadata')

def fetch_all_metadata_s3fs(bucket):
    """
    Fetch metadata for all tables/files in the bucket using s3fs.
    """
    try:
        fs = s3fs.S3FileSystem(
            key=bucket.storage_access_key,
            secret=bucket.storage_secret_key,
            client_kwargs={"endpoint_url": bucket.endpoint_url, "region_name": bucket.region}
        )
        bucket_path = bucket.name
        metadata_list = []

        for table in TableMetadata.query.filter_by(bucket_id=bucket.id).all():
            meta = {
                "file_path": table.table_path,
                "schema": [],
                "partitions": "Not available",
                "properties": "Not available",
                "snapshots": "Not available",
                "statistics": "Not available"
            }
            try:
                import json
                metadata_json = json.loads(table.metadata_json)
                if table.table_format == "delta":
                    delta_path = f"{bucket_path}/{table.table_path}"
                    delta_table = DeltaTable(delta_path, filesystem=fs)
                    schema = delta_table.schema.to_pyarrow()
                    meta["schema"] = [
                        {"name": field.name, "type": str(field.type), "nullable": field.nullable}
                        for field in schema
                    ]
                    meta["snapshots"] = str(delta_table.version())
                    meta["properties"] = str(delta_table.metadata().configuration)
                elif table.table_format == "parquet":
                    parquet_path = f"{bucket_path}/{table.table_path}"
                    dataset = ds.dataset(parquet_path, filesystem=fs, format="parquet")
                    schema = dataset.schema
                    meta["schema"] = [
                        {"name": field.name, "type": str(field.type), "nullable": field.nullable}
                        for field in schema
                    ]
                    meta["statistics"] = str(dataset.statistics()) if hasattr(dataset, 'statistics') else "Not available"
            except Exception as e:
                print(f"Error fetching metadata for {table.table_path}: {e}")
            metadata_list.append(meta)

        return metadata_list
    except Exception as e:
        print(f"Error in fetch_all_metadata_s3fs: {e}")
        return []

@metadata_bp.route("/")
@login_required
def metadata_landing():
    """
    Redirect to the metadata viewer for the first accessible bucket.
    """
    first_bucket = Bucket.query.join(Workspace, Bucket.workspace_id == Workspace.id).join(
        WorkspaceUser, Workspace.id == WorkspaceUser.workspace_id
    ).filter(
        WorkspaceUser.user_id == current_user.id,
        WorkspaceUser.role.in_(["admin", "editor"])
    ).first()
    if first_bucket:
        return redirect(url_for('metadata.view_metadata', bucket_id=first_bucket.id))
    flash("No accessible buckets found.", "danger")
    return redirect(url_for("explorer.explorer"))

@metadata_bp.route("/viewer/<int:bucket_id>")
@login_required
def view_metadata(bucket_id):
    """
    Display metadata for a specific bucket's tables/files.
    """
    bucket = Bucket.query.get_or_404(bucket_id)

    ws_user = WorkspaceUser.query.filter_by(user_id=current_user.id, workspace_id=bucket.workspace_id).first()
    if not ws_user or ws_user.role not in ["admin", "editor"]:
        flash("You do not have permission to view this bucket's metadata.", "danger")
        return redirect(url_for("settings.settings"))

    metadata_list = fetch_all_metadata_s3fs(bucket)

    if not metadata_list:
        flash("No metadata available for this bucket.", "warning")
        return render_template("core/table_metadata_viewer.html", bucket=bucket, metadata_list=[], selected_metadata={})

    selected_file = request.args.get('file', metadata_list[0]["file_path"])
    selected_metadata = next((item for item in metadata_list if item["file_path"] == selected_file), metadata_list[0])

    return render_template(
        "core/table_metadata_viewer.html",
        bucket=bucket,
        metadata_list=metadata_list,
        selected_metadata=selected_metadata
    )

@metadata_bp.route("/compare", methods=["GET", "POST"])
def compare_metadata():
    flash("Metadata comparison is not yet implemented.", "info")
    return redirect(url_for("explorer.explorer"))