from app.extensions import db
from app.models import User, Workspace, WorkspaceUser, TableMetadata
from werkzeug.security import generate_password_hash
import datetime

# Create a Flask application context
from app import create_app

app = create_app()
with app.app_context():
    db.create_all()
    db.session.begin()

    try:
        # Create Users
        adimail = User(username="adimail", password=generate_password_hash("adimail", method="pbkdf2:sha256"))
        LhaseParth2610 = User(username="LhaseParth2610", password=generate_password_hash("LhaseParth2610", method="pbkdf2:sha256"))
        prajwalkumbhar29 = User(username="prajwalkumbhar29", password=generate_password_hash("prajwalkumbhar29", method="pbkdf2:sha256"))
        rohitkshirsagar19 = User(username="rohitkshirsagar19", password=generate_password_hash("rohitkshirsagar19", method="pbkdf2:sha256"))
        
        # Additional users
        alice = User(username="alice", password=generate_password_hash("alice", method="pbkdf2:sha256"), global_role="admin")
        bob = User(username="bob", password=generate_password_hash("bob", method="pbkdf2:sha256"))
        charlie = User(username="charlie", password=generate_password_hash("charlie", method="pbkdf2:sha256"))

        db.session.add_all([adimail, LhaseParth2610, prajwalkumbhar29, rohitkshirsagar19, alice, bob, charlie])
        db.session.commit()  # Commit to generate IDs

        # Create Workspaces
        workspace1 = Workspace(
            name="DataLake",
            status="active",
            region="us-east-1",
            cloud="AWS",
            catalog="Glue",
            clusters=3,
            description="Centralized Data Lake for analytics",
            endpoint_url="s3.amazonaws.com",
            storage_access_key="ACCESS_KEY",
            storage_secret_key="SECRET_KEY",
            default_bucket_name="datalake-bucket",
            trino_url="trino.aws.com",
            trino_user="admin",
            trino_password="trino_secret",
            owner_id=adimail.id,
            owner_name=adimail.username,
            created_by_id=alice.id,
            created_by_name=alice.username,
        )

        workspace2 = Workspace(
            name="MLPlatform",
            status="active",
            region="eu-west-1",
            cloud="Azure",
            catalog="Data Catalog",
            clusters=5,
            description="Machine Learning Platform",
            endpoint_url="azure.blob.core.windows.net",
            storage_access_key="AZURE_ACCESS_KEY",
            storage_secret_key="AZURE_SECRET_KEY",
            default_bucket_name="ml-data",
            trino_url="trino.azure.com",
            trino_user="ml_admin",
            trino_password="ml_secret",
            owner_id=LhaseParth2610.id,
            owner_name=LhaseParth2610.username,
            created_by_id=bob.id,
            created_by_name=bob.username,
        )

        db.session.add_all([workspace1, workspace2])
        db.session.commit()  # Commit to generate IDs

        # Assign Users to Workspaces
        workspace_user1 = WorkspaceUser(user_id=adimail.id, workspace_id=workspace1.id, role="admin")
        workspace_user2 = WorkspaceUser(user_id=LhaseParth2610.id, workspace_id=workspace1.id, role="viewer")
        workspace_user3 = WorkspaceUser(user_id=prajwalkumbhar29.id, workspace_id=workspace2.id, role="admin")
        workspace_user4 = WorkspaceUser(user_id=rohitkshirsagar19.id, workspace_id=workspace2.id, role="editor")

        db.session.add_all([workspace_user1, workspace_user2, workspace_user3, workspace_user4])
        db.session.commit()

        # Create Table Metadata for Workspaces
        table1 = TableMetadata(
            workspace_id=workspace1.id,
            table_name="customer_data",
            table_path="s3://datalake-bucket/customer_data",
            table_format="parquet",
            metadata_json='{"columns": ["id", "name", "email"], "num_rows": 1000000}',
        )

        table2 = TableMetadata(
            workspace_id=workspace1.id,
            table_name="sales_records",
            table_path="s3://datalake-bucket/sales",
            table_format="iceberg",
            metadata_json='{"columns": ["date", "amount", "customer_id"], "partitions": ["date"]}',
        )

        table3 = TableMetadata(
            workspace_id=workspace2.id,
            table_name="ml_models",
            table_path="azure://ml-data/models",
            table_format="delta",
            metadata_json='{"version": "1.0", "columns": ["model_id", "accuracy", "timestamp"]}',
        )

        table4 = TableMetadata(
            workspace_id=workspace2.id,
            table_name="training_data",
            table_path="azure://ml-data/training",
            table_format="hudi",
            metadata_json='{"columns": ["feature1", "feature2", "label"], "update_strategy": "merge"}',
        )

        db.session.add_all([table1, table2, table3, table4])
        db.session.commit()

        print("Database populated successfully!")

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")

    finally:
        db.session.close()
