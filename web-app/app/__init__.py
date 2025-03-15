from flask import Flask, render_template, g, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, current_user
from app.extensions import db
from app.blueprints.admin import admin_bp
from app.models import WorkspaceUser, Workspace
import json
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)

def create_app():
    # Create Flask application instance
    app = Flask(__name__)
    CORS(app)
    app.config["SECRET_KEY"] = "nqMt+o1BxO2Wkaj4ogmFtg=="
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Initialize database
    db.init_app(app)
    cache.init_app(app)

    # Initialize login manager
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"

    # Add custom Jinja2 filter for JSON decoding
    app.jinja_env.filters['json_decode'] = json.loads

    # Optional: Add safe JSON decoding to handle invalid JSON
    def safe_json_decode(value):
        if value is None or not value.strip():
            return {}
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            print(f"Invalid JSON in metadata_json: {value}")
            return {}

    app.jinja_env.filters['safe_json_decode'] = safe_json_decode

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    @app.before_request
    def load_global_user_workspace():
        g.user = current_user if current_user.is_authenticated else None
        g.workspaces = []

        if g.user:
            g.workspaces = (
                db.session.query(Workspace)
                .join(WorkspaceUser, Workspace.id == WorkspaceUser.workspace_id)
                .filter(WorkspaceUser.user_id == g.user.id)
                .all()
            )

        # Safely set g.bucket_id, defaulting to 1 if not present or if view_args is None
        g.bucket_id = request.view_args.get('bucket_id', 1) if request.view_args is not None else 1

    # Register blueprints
    from app.blueprints.home import home_bp
    from app.blueprints.api import api_bp
    from app.blueprints.auth.auth import auth_bp
    from app.blueprints.core.explorer import explorer_bp
    from app.blueprints.core.metadata import metadata_bp
    from app.blueprints.core.query_editor import query_editor_bp
    from app.blueprints.core.settings import settings_bp
    from app.blueprints.core.workspace import workspace_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp)
    app.register_blueprint(explorer_bp)
    app.register_blueprint(query_editor_bp)
    app.register_blueprint(metadata_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(workspace_bp)

    # Apply rate limits to blueprints
    limiter.limit("200 per hour")(home_bp)
    limiter.limit("200 per hour")(api_bp)
    limiter.limit("200 per hour")(auth_bp)
    limiter.limit("200 per hour")(admin_bp)
    limiter.limit("200 per hour")(explorer_bp)
    limiter.limit("200 per hour")(query_editor_bp)
    limiter.limit("200 per hour")(metadata_bp)
    limiter.limit("200 per hour")(settings_bp)

    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def handle_errors(error):
        return (
            render_template(
                "errors/error.html",
                error_code=error.code,
                error_message=error.name,
                error_description=error.description,
            ),
            error.code,
        )

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return render_template("errors/429.html", error=e.description), 400

    # Initialize database tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)