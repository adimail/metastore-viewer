from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Bucket, WorkspaceUser, Workspace, TableMetadata
from app.blueprints.core.metadata import fetch_all_metadata_s3fs
import boto3
from botocore.exceptions import ClientError
import s3fs
import json  # Add this import

explorer_bp = Blueprint('explorer', __name__, url_prefix='/explorer')

@explorer_bp.route("/")
@login_required
def explorer():
    """
    Shows all workspaces that the current user is part of,
    where they have admin or editor roles.
    """
    workspaces = (
        Workspace.query.join(WorkspaceUser)
        .filter(
            WorkspaceUser.user_id == current_user.id,
            WorkspaceUser.role.in_(["admin", "editor"]),
        )
        .all()
    )
    return render_template("core/explorer.html", workspaces=workspaces)

@explorer_bp.route("/bucket/<int:bucket_id>")
@login_required
def bucket_explorer(bucket_id):
    """
    Shows details for a specific bucket, including its tables and files.
    Updates the bucket's total size, object count, and syncs TableMetadata from MinIO.
    """
    bucket = Bucket.query.get_or_404(bucket_id)
    ws_user = WorkspaceUser.query.filter_by(user_id=current_user.id, workspace_id=bucket.workspace_id).first()
    if not ws_user or ws_user.role not in ["admin", "editor"]:
        flash("You do not have permission to view this bucket.", "danger")
        return redirect(url_for("settings.settings"))

    print(f"Bucket: {bucket.name}, Path: {bucket.bucket_path}, Endpoint: {bucket.endpoint_url}")

    files = []
    try:
        s3_client = get_s3_client(bucket)
        safe_bucket_name = ''.join(c for c in bucket.name if c.isalnum() or c == '-').lower()
        if safe_bucket_name != bucket.name:
            print(f"Warning: Bucket name '{bucket.name}' sanitized to '{safe_bucket_name}'")
        safe_prefix = bucket.bucket_path or ""
        if safe_prefix and not all(c.isalnum() or c in "-/._" for c in safe_prefix):
            print(f"Warning: Invalid prefix '{safe_prefix}', resetting to empty string")
            safe_prefix = ""
        response = s3_client.list_objects_v2(Bucket=safe_bucket_name, Prefix=safe_prefix)
        print("S3 Response:", response)
        files = [obj["Key"] for obj in response.get("Contents", [])]
        bucket.total_size = sum(obj.get("Size", 0) for obj in response.get("Contents", []))
        bucket.object_count = len(files)
        print(f"Files fetched: {files}")
        print(f"Total size: {bucket.total_size} bytes, Object count: {bucket.object_count}")
    except ClientError as e:
        flash(f"Error accessing bucket: {str(e)}", "danger")
        print("ClientError:", str(e))
    except Exception as e:
        flash(f"Unexpected error: {str(e)}", "danger")
        print("Error:", str(e))

    # Sync TableMetadata with bucket contents using s3fs
    try:
        fs = s3fs.S3FileSystem(
            key=bucket.storage_access_key,
            secret=bucket.storage_secret_key,
            client_kwargs={"endpoint_url": bucket.endpoint_url, "region_name": bucket.region}
        )
        bucket_path = bucket.name
        print(f"Scanning bucket: {bucket_path} at {bucket.endpoint_url}")

        # Get all items (files and directories)
        all_items = fs.ls(bucket_path, detail=True)
        print(f"Found {len(all_items)} items in bucket")

        for item in all_items:
            s3_path = item["Key"]
            item_name = s3_path.replace(f"{bucket_path}/", "")
            print(f"Processing item: {item_name}")

            # Handle directories
            if item["type"] == "directory":
                table = TableMetadata.query.filter_by(bucket_id=bucket_id, table_path=item_name).first()
                table_format = "directory"  # Default for folders
                metadata_json = {"type": "directory", "contents": []}

                # Check for Delta table by looking for .crc files in _delta_log
                delta_log_path = f"{s3_path}/_delta_log"
                if fs.exists(delta_log_path):
                    delta_files = fs.ls(delta_log_path, detail=True)
                    if any(f["Key"].endswith(".crc") for f in delta_files):
                        table_format = "delta"
                        metadata_json["type"] = "delta_table"
                        metadata_json["delta_log_files"] = [f["Key"].split("/")[-1] for f in delta_files]

                # Iterate through folder contents
                folder_contents = fs.ls(s3_path, detail=True)
                for content in folder_contents:
                    content_path = content["Key"]
                    content_name = content_path.replace(f"{s3_path}/", "")
                    if content["type"] == "file":
                        # Add file to folder's contents
                        metadata_json["contents"].append({
                            "file_path": content_name,
                            "size": content["Size"],
                            "last_modified": str(content["LastModified"])
                        })
                        # Skip creating separate TableMetadata for .snappy.parquet files in delta-table
                        if content_name.endswith(".snappy.parquet") and table_format == "delta":
                            continue
                        # Add individual file as a TableMetadata entry if it's a Parquet file and not in a Delta table
                        if content_name.endswith(".parquet"):
                            file_table = TableMetadata.query.filter_by(bucket_id=bucket_id, table_path=content_path.replace(f"{bucket_path}/", "")).first()
                            if not file_table:
                                file_table = TableMetadata(
                                    workspace_id=bucket.workspace_id,
                                    bucket_id=bucket_id,
                                    table_name=content_name,
                                    table_path=content_path.replace(f"{bucket_path}/", ""),
                                    table_format="parquet",
                                    metadata_json=json.dumps({"file_path": content_name, "size": content["Size"], "schema": "Fetched separately"})
                                )
                                db.session.add(file_table)

                if not table:
                    table = TableMetadata(
                        workspace_id=bucket.workspace_id,
                        bucket_id=bucket_id,
                        table_name=item_name,
                        table_path=item_name,
                        table_format=table_format,
                        metadata_json=json.dumps(metadata_json)  # Use json.dumps
                    )
                    db.session.add(table)
                else:
                    table.table_format = table_format
                    table.metadata_json = json.dumps(metadata_json)  # Use json.dumps
                    table.last_updated = db.func.current_timestamp()
                print(f"Updated {item_name} with contents: {metadata_json['contents']}")

            # Handle top-level files
            elif item["type"] == "file" and item_name.endswith(".parquet"):
                table = TableMetadata.query.filter_by(bucket_id=bucket_id, table_path=item_name).first()
                if not table:
                    table = TableMetadata(
                        workspace_id=bucket.workspace_id,
                        bucket_id=bucket_id,
                        table_name=item_name,
                        table_path=item_name,
                        table_format="parquet",
                        metadata_json=json.dumps({"file_path": item_name, "size": item["Size"], "schema": "Fetched separately"})  # Use json.dumps
                    )
                    db.session.add(table)
                else:
                    table.metadata_json = json.dumps({"file_path": item_name, "size": item["Size"], "schema": "Fetched separately"})  # Use json.dumps
                    table.last_updated = db.func.current_timestamp()

        # Sync additional metadata from fetch_all_metadata_s3fs for detailed schema
        metadata_list = fetch_all_metadata_s3fs(bucket)
        for meta in metadata_list:
            table = TableMetadata.query.filter_by(bucket_id=bucket_id, table_path=meta["file_path"]).first()
            if table:
                table.metadata_json = json.dumps(meta)  # Use json.dumps
                table.last_updated = db.func.current_timestamp()

        db.session.commit()
        print("TableMetadata synced successfully")
    except Exception as e:
        flash(f"Error syncing TableMetadata: {str(e)}", "danger")
        print(f"TableMetadata sync error: {e}")

    return render_template("core/bucket_details.html", bucket=bucket, files=files)

def get_s3_client(bucket):
    """
    Creates and returns a boto3 S3 client using credentials stored in the Bucket model.
    """
    print(f"Creating S3 client with Endpoint: {bucket.endpoint_url}, Bucket: {bucket.name}")
    return boto3.client(
        "s3",
        aws_access_key_id=bucket.storage_access_key,
        aws_secret_access_key=bucket.storage_secret_key,
        endpoint_url=bucket.endpoint_url,
        region_name=bucket.region,
    )