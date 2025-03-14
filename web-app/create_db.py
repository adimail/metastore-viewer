from app.extensions import db
from app.models import User, Workspace, WorkspaceUser, TableMetadata, Bucket, Catalog
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

        aws_catalog = Catalog(
            name="Company catalog",
            object_store="s3://myCatalog-bucket",
            cloud_provider="AWS",
            access_key="AWS_ACCESS_KEY",
            secret_key="AWS_SECRET_KEY",
        )

        azure_catalog = Catalog(
            name="Azure Data Catalog",
            object_store="azure://data-catalog",
            cloud_provider="Azure",
            access_key="AZURE_ACCESS_KEY",
            secret_key="AZURE_SECRET_KEY",
        )

        db.session.add_all([aws_catalog, azure_catalog])
        db.session.commit()

        # Create Workspaces
        main_workspace = Workspace(
            name="COEP Inspiron Workspace",
            status="active",
            catalog_id=aws_catalog.id,
            description="Primary workspace for team collaboration and data analysis",
            trino_url="trino.mainworkspace.com",
            trino_user="admin",
            trino_password="main_secret",
            owner_id=admin.id,
            created_by_id=admin.id,
            created_at=datetime.datetime.utcnow(),
            updated_on=datetime.datetime.utcnow(),
        )

        dummy_workspace = Workspace(
            name="DummyWorkspace",
            status="inactive",
            catalog_id=azure_catalog.id,
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

        workspace_users = [
            WorkspaceUser(
                user_id=admin.id, workspace_id=main_workspace.id, role="admin"
            ),
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
                user_id=admin.id, workspace_id=dummy_workspace.id, role="admin"
            ),
            WorkspaceUser(
                user_id=adimail.id, workspace_id=dummy_workspace.id, role="admin"
            ),
        ]

        db.session.add_all(workspace_users)
        db.session.commit()

        # Create Buckets
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

        bucket3 = Bucket(
            name="dummy-data",
            cloud_provider="Azure",
            region="us-west-1",
            endpoint_url="azure.blob.core.windows.net",
            storage_access_key="DUMMY_ACCESS_KEY",
            storage_secret_key="DUMMY_SECRET_KEY",
            bucket_path="azure://dummy-data",
            status="inactive",
            storage_class="STANDARD",
            workspace_id=dummy_workspace.id,
            total_size=1048576,  # 1GB
            object_count=1000,
        )

        db.session.add_all([bucket1, bucket2, bucket3])
        db.session.commit()

        # Create Tables
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
        ]

        db.session.add_all(tables)
        db.session.commit()

        print("Database successfully initialized with sample data!")

    except Exception as e:
        db.session.rollback()
        print(f"Error occurred: {e}")

    finally:
        db.session.close()
