from flask import Blueprint, render_template, jsonify, request, jsonify
from flask_login import login_required
from datetime import datetime

visualizer_bp = Blueprint("visualizer", __name__, template_folder="templates")


@visualizer_bp.route("/visualizer")
@login_required
def visualizer():
    """Main visualizer dashboard"""

    dashboard_summary = {"total_tables": 12, "total_snapshots": 143}

    schema_explorer = {
        "current_version": "v5",
        "last_updated": datetime(2025, 3, 12).strftime("%b %d, %Y"),
    }

    partition_explorer = {"partition_count": 32, "total_size": "128 GB"}

    snapshot_viewer = {
        "latest_snapshot": "#143",
        "created_at": datetime(2025, 3, 15, 8, 23).strftime("Today, %H:%M"),
    }

    lineage_graph = {"linked_tables": 5, "upstream_count": 3}

    data_preview = {"row_count": "1.2M", "column_count": 24}

    query_panel = {"recent_queries": 12, "saved_queries": 5}

    recent_activity = [
        {
            "timestamp": datetime(2025, 3, 15, 8, 23).strftime("%b %d, %H:%M"),
            "table_name": "customers",
            "event_type": "New Snapshot",
            "event_class": "bg-green-100 text-green-800",
            "user": "Aditya",
            "action_url": "#",
        },
        {
            "timestamp": datetime(2025, 3, 14, 18, 42).strftime("%b %d, %H:%M"),
            "table_name": "orders",
            "event_type": "Schema Change",
            "event_class": "bg-yellow-100 text-yellow-800",
            "user": "Rohit",
            "action_url": "#",
        },
        {
            "timestamp": datetime(2025, 3, 13, 11, 30).strftime("%b %d, %H:%M"),
            "table_name": "inventory",
            "event_type": "Branch Created",
            "event_class": "bg-purple-100 text-purple-800",
            "user": "Parth",
            "action_url": "#",
        },
        {
            "timestamp": datetime(2025, 3, 12, 15, 45).strftime("%b %d, %H:%M"),
            "table_name": "sales",
            "event_type": "Table Dropped",
            "event_class": "bg-red-100 text-red-800",
            "user": "Sarthak Pawar",
            "action_url": "#",
        },
        {
            "timestamp": datetime(2025, 3, 11, 10, 10).strftime("%b %d, %H:%M"),
            "table_name": "employees",
            "event_type": "Data Updated",
            "event_class": "bg-orange-100 text-orange-800",
            "user": "Suyog",
            "action_url": "#",
        },
        {
            "timestamp": datetime(2025, 3, 10, 22, 30).strftime("%b %d, %H:%M"),
            "table_name": "logistics",
            "event_type": "New Snapshot",
            "event_class": "bg-green-100 text-green-800",
            "user": "Aditya",
            "action_url": "#",
        },
    ]

    return render_template(
        "visualizer/visualizer.html",
        dashboard_summary=dashboard_summary,
        schema_explorer=schema_explorer,
        partition_explorer=partition_explorer,
        snapshot_viewer=snapshot_viewer,
        lineage_graph=lineage_graph,
        data_preview=data_preview,
        query_panel=query_panel,
        recent_activity=recent_activity,
    )


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


@visualizer_bp.route("/api/get-tables")
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


@visualizer_bp.route("/api/get-lineage")
@login_required
def get_lineage():
    """API endpoint to fetch lineage data for a selected table"""
    table = request.args.get("table", "customers")
    lineage_data = {
        "nodes": [
            {
                "id": "customers",
                "name": "customers",
                "type": "table",
                "attributes": [
                    {"name": "id", "type": "INTEGER"},
                    {"name": "name", "type": "STRING"},
                    {"name": "email", "type": "STRING"},
                    {"name": "created_at", "type": "TIMESTAMP"},
                ],
            },
            {
                "id": "orders",
                "name": "orders",
                "type": "table",
                "attributes": [
                    {"name": "order_id", "type": "INTEGER"},
                    {"name": "customer_id", "type": "INTEGER"},
                    {"name": "amount", "type": "DECIMAL"},
                    {"name": "order_date", "type": "TIMESTAMP"},
                ],
            },
            {
                "id": "customer_orders_view",
                "name": "customer_orders_view",
                "type": "view",
                "attributes": [
                    {"name": "customer_id", "type": "INTEGER"},
                    {"name": "total_amount", "type": "DECIMAL"},
                ],
            },
            {
                "id": "external_data",
                "name": "external_data",
                "type": "external",
                "attributes": [],
            },
        ],
        "links": [
            {
                "source": "customers",
                "target": "customer_orders_view",
                "type": "derives",
            },
            {"source": "orders", "target": "customer_orders_view", "type": "derives"},
            {
                "source": "customer_orders_view",
                "target": "external_data",
                "type": "exports",
            },
        ],
    }
    return jsonify(lineage_data)
