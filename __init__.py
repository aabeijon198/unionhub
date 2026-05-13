"""Flask app factory."""
import click
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import Config
from .models import db, User, Dma

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."

migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Blueprints
    from . import auth, admin, public
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(public.bp)

    # CLI commands
    @app.cli.command("init-db")
    def init_db():
        """Create tables (for local SQLite) + seed DMAs + bootstrap admin.

        On Railway, tables are created by `flask db upgrade` (Procfile release
        step). After deploy, run `flask seed` to add DMAs + admin.
        """
        db.create_all()
        seed_dmas()
        seed_admin(app)
        click.echo("✓ Database initialized.")

    @app.cli.command("seed")
    def seed_cmd():
        """Idempotent: seed DMAs + bootstrap admin. Safe to re-run."""
        seed_dmas()
        seed_admin(app)
        click.echo("✓ Seeded.")

    return app


def seed_dmas():
    """Insert the 7 DMAs we support. Idempotent."""
    defaults = [
        ("nyc", "New York", 10),
        ("la", "Los Angeles", 20),
        ("chicago", "Chicago", 30),
        ("boston", "Boston", 40),
        ("houston", "Houston", 50),
        ("dallas", "Dallas-Fort Worth", 60),
        ("miami", "Miami-Fort Lauderdale", 70),
    ]
    for slug, name, order in defaults:
        if not Dma.query.filter_by(slug=slug).first():
            db.session.add(Dma(slug=slug, name=name, display_order=order))
    db.session.commit()


def seed_admin(app):
    """Create the bootstrap admin user from env vars (only if no users exist)."""
    if User.query.count() > 0:
        click.echo("• Users already exist, skipping admin bootstrap.")
        return
    email = app.config.get("ADMIN_EMAIL", "admin@example.com").lower()
    password = app.config.get("ADMIN_PASSWORD", "changeme")
    u = User(email=email)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    click.echo(f"✓ Created admin user: {email}")
