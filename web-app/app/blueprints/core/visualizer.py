from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required

visualizer_bp = Blueprint("visualizer", __name__, template_folder="templates")


@visualizer_bp.route("/visualizer")
@login_required
def visualizer():
    """Main visualizer dashboard"""
    return render_template("visualizer/visualizer.html")


@visualizer_bp.route("/schema-explorer")
@login_required
def schema_explorer():
    """View schema versions and evolution"""
    return render_template("visualizer/schema_explorer.html")


@visualizer_bp.route("/visualizer/partition-explorer")
@login_required
def partition_explorer():
    """View partition structure of the selected table"""
    return render_template("visualizer/partition_explorer.html")


@visualizer_bp.route("/visualizer/snapshot-viewer")
@login_required
def snapshot_viewer():
    """View snapshot history of Iceberg/Delta tables"""
    return render_template("visualizer/snapshot_viewer.html")


@visualizer_bp.route("/visualizer/snapshot-viewer")
@login_required
def data_preview():
    return render_template("visualizer/snapshot_viewer.html")


@visualizer_bp.route("/visualizer/data-lineage")
@login_required
def data_lineage():
    """View data dependencies and transformations"""
    return render_template("visualizer/data_lineage.html")


@visualizer_bp.route("/visualizer/api/get-tables")
@login_required
def get_tables():
    """API endpoint to fetch available tables (mock response for now)"""
    tables = ["customers", "orders", "products", "inventory"]
    return jsonify({"tables": tables})


@visualizer_bp.route("/visualizer/api/get-schema")
@login_required
def get_schema():
    """API endpoint to fetch schema details of a selected table"""
    table = request.args.get("table", "customers")
    schema = {
        "customers": [
            {"name": "id", "type": "INTEGER"},
            {"name": "name", "type": "STRING"},
            {"name": "email", "type": "STRING"},
            {"name": "created_at", "type": "TIMESTAMP"},
        ],
        "orders": [
            {"name": "order_id", "type": "INTEGER"},
            {"name": "customer_id", "type": "INTEGER"},
            {"name": "amount", "type": "DECIMAL"},
            {"name": "order_date", "type": "TIMESTAMP"},
        ],
    }
    return jsonify(schema.get(table, []))
