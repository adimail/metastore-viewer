from app.extensions import db
from flask_login import UserMixin
import datetime


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    # Optional global role (could be used for system-wide permissions)
    global_role = db.Column(db.String(50), default="user")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Association with workspaces through WorkspaceUser
    workspaces = db.relationship(
        "WorkspaceUser", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Workspace(db.Model):
    __tablename__ = "workspaces"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    status = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    cloud = db.Column(db.String(100), nullable=False)
    catalog = db.Column(db.String(255), nullable=True)
    clusters = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_name = db.Column(db.String(255), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by_name = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_on = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    owner = db.relationship('User', foreign_keys=[owner_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    workspace_users = db.relationship("WorkspaceUser", back_populates="workspace", cascade="all, delete-orphan")
    tables = db.relationship("TableMetadata", back_populates="workspace", cascade="all, delete-orphan")



class WorkspaceUser(db.Model):
    __tablename__ = "workspace_users"
    # Composite primary key: a user can have only one role per workspace
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    workspace_id = db.Column(
        db.Integer, db.ForeignKey("workspaces.id"), primary_key=True
    )
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'viewer', or 'editor'
    joined_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships to the associated User and Workspace
    user = db.relationship("User", back_populates="workspaces")
    workspace = db.relationship("Workspace", back_populates="workspace_users")

    def __repr__(self):
        return f"<WorkspaceUser user_id={self.user_id}, workspace_id={self.workspace_id}, role={self.role}>"


class TableMetadata(db.Model):
    __tablename__ = "table_metadata"
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey("workspaces.id"), nullable=False)
    table_name = db.Column(db.String(255), nullable=False)
    table_path = db.Column(
        db.String(512), nullable=False
    )  # For example, an S3 bucket path
    table_format = db.Column(
        db.String(50), nullable=False
    )  # 'parquet', 'iceberg', 'delta', or 'hudi'

    # A JSON-serialized field that stores all extracted metadata.
    # For Parquet, this can include file-level metadata, row groups, and column details.
    # For Iceberg, it may store table-level metadata, snapshots, partition specs, etc.
    # For Delta, it can hold transaction logs, checkpoint metadata, etc.
    # For Hudi, it can capture commit timelines, incremental changes, and clustering metrics.
    metadata_json = db.Column(db.Text)

    # Automatically track when the metadata was last updated
    last_updated = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    workspace = db.relationship("Workspace", back_populates="tables")

    def __repr__(self):
        return f"<TableMetadata {self.table_name} ({self.table_format})>"
