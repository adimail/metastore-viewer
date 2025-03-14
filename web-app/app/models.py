from app.extensions import db
from flask_login import UserMixin
import datetime


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    global_role = db.Column(db.String(50), default="user")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_on = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    workspaces = db.relationship(
        "WorkspaceUser", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Catalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    object_store = db.Column(
        db.String(512), nullable=False
    )  # e.g., s3://bucket-name/path
    cloud_provider = db.Column(db.String(50), nullable=False)  # AWS, GCP, Azure
    access_key = db.Column(db.String(255), nullable=False)  # Store securely
    secret_key = db.Column(db.String(255), nullable=False)  # Store securely


class Workspace(db.Model):
    __tablename__ = "workspaces"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    status = db.Column(db.String(50), nullable=False, default="active")

    catalog = db.relationship("Catalog", backref=db.backref("workspaces", lazy=True))
    catalog_id = db.Column(db.Integer, db.ForeignKey("catalog.id"), nullable=False)

    description = db.Column(db.Text, nullable=True)

    # Trino credentials remain here as they are workspace-wide
    trino_url = db.Column(db.String(255), nullable=True)
    trino_user = db.Column(db.String(255), nullable=True)
    trino_password = db.Column(db.String(255), nullable=True)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_on = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    # Relationships
    owner = db.relationship("User", foreign_keys=[owner_id])
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    workspace_users = db.relationship(
        "WorkspaceUser", back_populates="workspace", cascade="all, delete-orphan"
    )
    tables = db.relationship(
        "TableMetadata", back_populates="workspace", cascade="all, delete-orphan"
    )
    buckets = db.relationship(
        "Bucket", back_populates="workspace", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Workspace {self.name}>"


class WorkspaceUser(db.Model):
    __tablename__ = "workspace_users"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    workspace_id = db.Column(
        db.Integer, db.ForeignKey("workspaces.id"), primary_key=True
    )
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'viewer', or 'editor'
    joined_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user = db.relationship("User", back_populates="workspaces")
    workspace = db.relationship("Workspace", back_populates="workspace_users")

    def __repr__(self):
        return f"<WorkspaceUser user_id={self.user_id}, workspace_id={self.workspace_id}, role={self.role}>"


class TableMetadata(db.Model):
    __tablename__ = "table_metadata"
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey("workspaces.id"), nullable=False)
    bucket_id = db.Column(db.Integer, db.ForeignKey("buckets.id"), nullable=False)
    table_name = db.Column(db.String(255), nullable=False)
    table_path = db.Column(db.String(512), nullable=False)
    table_format = db.Column(
        db.String(50), nullable=False
    )  # 'parquet', 'iceberg', 'delta', or 'hudi'

    # Optional: Add uniqueness constraint per workspace if needed
    # __table_args__ = (db.UniqueConstraint("workspace_id", "table_name", name="uniq_workspace_table"),)

    # Catalog-related details
    catalog_name = db.Column(db.String(255), nullable=True)
    schema_name = db.Column(db.String(255), nullable=True)  # Schema within the catalog
    table_metadata_json = db.Column(db.Text, nullable=True)  # JSON-serialized metadata

    # JSON-serialized metadata field
    # Consider db.JSONB if using PostgreSQL for better querying
    metadata_json = db.Column(db.Text, nullable=True)

    last_updated = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    workspace = db.relationship("Workspace", back_populates="tables")
    bucket = db.relationship("Bucket", back_populates="tables")

    def __repr__(self):
        return f"<TableMetadata {self.table_name} ({self.table_format})>"


class Bucket(db.Model):
    __tablename__ = "buckets"
    __table_args__ = (
        db.UniqueConstraint("cloud_provider", "name", name="uniq_cloud_name"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    cloud_provider = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    endpoint_url = db.Column(db.String(255), nullable=True)
    storage_access_key = db.Column(db.String(255), nullable=True)
    storage_secret_key = db.Column(db.String(255), nullable=True)

    bucket_path = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="active")
    storage_class = db.Column(db.String(50), nullable=False, default="STANDARD")
    total_size = db.Column(db.BigInteger, default=0)  # Update via background job
    object_count = db.Column(db.BigInteger, default=0)  # Update via background job

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_on = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
    )

    workspace_id = db.Column(db.Integer, db.ForeignKey("workspaces.id"), nullable=False)
    workspace = db.relationship("Workspace", back_populates="buckets")
    tables = db.relationship(
        "TableMetadata", back_populates="bucket", cascade="all, delete-orphan"
    )

    def get_path(self):
        """Helper method to derive bucket path dynamically."""
        return f"{self.cloud_provider}://{self.name}"

    def __repr__(self):
        return f"<Bucket {self.name} ({self.cloud_provider}) - Path: {self.get_path()}>"
