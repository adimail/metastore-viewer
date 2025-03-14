from app.extensions import db
from app.models import User, Workspace, WorkspaceUser, TableMetadata, Bucket
from werkzeug.security import generate_password_hash
import datetime

from app import create_app

app = create_app()
with app.app_context():
    db.create_all()
    db.session.begin()

    try:
        # Create Users
        adimail = User(
            username="adimail",
            password=generate_password_hash("adimail", method="pbkdf2:sha256"),
        )
        parth = User(
            username="parth",
            password=generate_password_hash("parth", method="pbkdf2:sha256"),
        )
        rohit = User(
            username="rohit",
            password=generate_password_hash("rohit", method="pbkdf2:sha256"),
        )
        prajwal = User(
            username="prajwal",
            password=generate_password_hash("prajwal", method="pbkdf2:sha256"),
        )
        admin = User(
            username="admin",
            password=generate_password_hash("admin", method="pbkdf2:sha256"),
            global_role="admin",
        )

        db.session.add_all([adimail, parth, rohit, prajwal, admin])
        db.session.commit()

        # Create Main Workspace
        main_workspace = Workspace(
            name="COEP Inspiron Workspace",
            status="active",
            region="us-east-1",
            cloud="AWS",
            catalog="Glue",
            clusters=4,
            description="Primary workspace for team collaboration and data analysis",
            trino_url="trino.mainworkspace.com",
            trino_user="admin",
            trino_password="main_secret",
            owner_id=admin.id,
            created_by_id=admin.id,
            created_at=datetime.datetime.utcnow(),
            updated_on=datetime.datetime.utcnow(),
        )

        # Create Dummy Workspace (Inactive)
        dummy_workspace = Workspace(
            name="DummyWorkspace",
            status="inactive",
            region="us-west-1",
            cloud="Azure",
            catalog="Data Catalog",
            clusters=1,
            description="Inactive dummy workspace for admin",
            trino_url="trino.dummy.com",
            trino_user="admin",
            trino_password="dummy_secret",
            owner_id=admin.id,
            created_by_id=admin.id,
            created_at=datetime.datetime.utcnow(),
            updated_on=datetime.datetime.utcnow(),
        )

        db.session.add_all([main_workspace, dummy_workspace])
        db.session.commit()

        # Assign Users to Main Workspace
        ws_users = [
            WorkspaceUser(
                user_id=adimail.id, workspace_id=main_workspace.id, role="admin"
            ),
            WorkspaceUser(
                user_id=parth.id, workspace_id=main_workspace.id, role="editor"
            ),
            WorkspaceUser(
                user_id=rohit.id, workspace_id=main_workspace.id, role="editor"
            ),
            WorkspaceUser(
                user_id=prajwal.id, workspace_id=main_workspace.id, role="editor"
            ),
            WorkspaceUser(
                user_id=admin.id, workspace_id=main_workspace.id, role="admin"
            ),
        ]

        # Assign Users to Dummy Workspace
        dummy_ws_users = [
            WorkspaceUser(
                user_id=admin.id, workspace_id=dummy_workspace.id, role="admin"
            ),
            WorkspaceUser(
                user_id=adimail.id, workspace_id=dummy_workspace.id, role="admin"
            ),
        ]

        db.session.add_all(ws_users + dummy_ws_users)
        db.session.commit()

        # Create Buckets for Main Workspace
        bucket1 = Bucket(
            name="main-raw-data",
            cloud_provider="AWS",
            region="us-east-1",
            endpoint_url="s3.amazonaws.com",
            storage_access_key="MAIN_ACCESS_KEY_1",
            storage_secret_key="MAIN_SECRET_KEY_1",
            bucket_path="s3://main-raw-data",
            status="active",
            storage_class="STANDARD",
            workspace_id=main_workspace.id,
            total_size=5242880,  # 5GB
            object_count=5000,
        )

        bucket2 = Bucket(
            name="main-processed-data",
            cloud_provider="AWS",
            region="us-east-1",
            endpoint_url="s3.amazonaws.com",
            storage_access_key="MAIN_ACCESS_KEY_2",
            storage_secret_key="MAIN_SECRET_KEY_2",
            bucket_path="s3://main-processed-data",
            status="active",
            storage_class="STANDARD",
            workspace_id=main_workspace.id,
            total_size=3145728,  # 3GB
            object_count=3000,
        )

        # Create Bucket for Dummy Workspace
        bucket3 = Bucket(
            name="dummy-data",
            cloud_provider="Azure",
            region="us-west-1",
            endpoint_url="azure.blob.core.windows.net",
            storage_access_key="DUMMY_ACCESS_KEY",
            storage_secret_key="DUMMY_SECRET_KEY",
            bucket_path="azure://dummy-data",
            status="inactive",  # Matching workspace status
            storage_class="STANDARD",
            workspace_id=dummy_workspace.id,
            total_size=1048576,  # 1GB
            object_count=1000,
        )

        db.session.add_all([bucket1, bucket2, bucket3])
        db.session.commit()

        # Create Multiple Tables with Data for Main Workspace
        tables = [
            TableMetadata(
                workspace_id=main_workspace.id,
                bucket_id=bucket1.id,
                table_name="customer_transactions",
                table_path="s3://main-raw-data/customer_transactions",
                table_format="parquet",
                metadata_json='{"columns": ["id", "customer_id", "amount", "date"], "num_rows": 2000000, "partitions": ["date"]}',
                last_updated=datetime.datetime.utcnow(),
            ),
            TableMetadata(
                workspace_id=main_workspace.id,
                bucket_id=bucket1.id,
                table_name="user_logs",
                table_path="s3://main-raw-data/user_logs",
                table_format="parquet",
                metadata_json='{"columns": ["user_id", "timestamp", "action"], "num_rows": 1500000}',
                last_updated=datetime.datetime.utcnow(),
            ),
            TableMetadata(
                workspace_id=main_workspace.id,
                bucket_id=bucket1.id,
                table_name="product_inventory",
                table_path="s3://main-raw-data/product_inventory",
                table_format="delta",
                metadata_json='{"columns": ["product_id", "name", "quantity", "price"], "num_rows": 500000}',
                last_updated=datetime.datetime.utcnow(),
            ),
            TableMetadata(
                workspace_id=main_workspace.id,
                bucket_id=bucket2.id,
                table_name="sales_analytics",
                table_path="s3://main-processed-data/sales_analytics",
                table_format="iceberg",
                metadata_json='{"columns": ["date", "region", "sales", "profit"], "num_rows": 1000000, "partitions": ["region"]}',
                last_updated=datetime.datetime.utcnow(),
            ),
            TableMetadata(
                workspace_id=main_workspace.id,
                bucket_id=bucket2.id,
                table_name="customer_insights",
                table_path="s3://main-processed-data/customer_insights",
                table_format="hudi",
                metadata_json='{"columns": ["customer_id", "segment", "lifetime_value"], "num_rows": 800000, "update_strategy": "merge"}',
                last_updated=datetime.datetime.utcnow(),
            ),
            TableMetadata(
                workspace_id=main_workspace.id,
                bucket_id=bucket2.id,
                table_name="daily_metrics",
                table_path="s3://main-processed-data/daily_metrics",
                table_format="parquet",
                metadata_json='{"columns": ["date", "views", "clicks", "conversions"], "num_rows": 1200000}',
                last_updated=datetime.datetime.utcnow(),
            ),
        ]

        db.session.add_all(tables)
        db.session.commit()

        print(
            "Database populated successfully with COEP Inspiron Workspace and DummyWorkspace!"
        )

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")

    finally:
        db.session.close()
