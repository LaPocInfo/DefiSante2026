import os
from flask import Flask, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
migrate = Migrate()


def create_app():
    app = Flask(__name__, static_folder="../frontend", static_url_path="/static_front")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "postgresql://defisante_user:defisante_pass@db:5432/defisante")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "jwt_secret_changez_moi")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "changez_moi_en_production")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    from api.routes.auth import token_blocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in token_blocklist

    # ── Gestionnaires d'erreurs → toujours retourner du JSON ──────────────────
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"erreur": "Requête invalide.", "detail": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"erreur": "Non autorisé."}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"erreur": "Accès refusé."}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erreur": "Ressource introuvable."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"erreur": "Méthode non permise."}), 405

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"erreur": "Erreur serveur interne.", "detail": str(e)}), 500
    # ─────────────────────────────────────────────────────────────────────────

    from api.routes.auth import auth_bp
    # from api.routes.participants import participants_bp   # TODO: à implémenter
    # from api.routes.equipes import equipes_bp             # TODO: à implémenter
    from api.routes.activites import activites_bp
    # from api.routes.defis import defis_bp                 # TODO: à implémenter
    # from api.routes.saisies import saisies_bp             # TODO: à implémenter
    from api.routes.stats import stats_bp

    app.register_blueprint(auth_bp,          url_prefix="/api/auth")
    # app.register_blueprint(participants_bp,   url_prefix="/api/participants")
    # app.register_blueprint(equipes_bp,        url_prefix="/api/equipes")
    app.register_blueprint(activites_bp,      url_prefix="/api/activites")
    # app.register_blueprint(defis_bp,          url_prefix="/api/defis")
    # app.register_blueprint(saisies_bp,        url_prefix="/api/saisies")
    app.register_blueprint(stats_bp,          url_prefix="/api/stats")

    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

    @app.route("/")
    def index():
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/pages/<path:filename>")
    def pages(filename):
        return send_from_directory(os.path.join(frontend_dir, "pages"), filename)

    @app.route("/css/<path:filename>")
    def css(filename):
        return send_from_directory(os.path.join(frontend_dir, "css"), filename)

    @app.route("/js/<path:filename>")
    def js(filename):
        return send_from_directory(os.path.join(frontend_dir, "js"), filename)

    with app.app_context():
        db.create_all()
        from api.utils.migrate import run_migrations
        run_migrations(db)
        from api.utils.seed import seed_activites
        seed_activites()
        _seed_admin(bcrypt)

    return app


def _seed_admin(bcrypt_ext):
    from api.models import Participant
    from datetime import date
    if Participant.query.filter_by(role="gestionnaire").first():
        return
    admin = Participant(
        prenom="Admin", nom="Défi Santé", courriel="admin@defisante.local",
        mot_de_passe=bcrypt_ext.generate_password_hash("Admin123!").decode("utf-8"),
        sexe="mixte", role="gestionnaire", date_inscription=date.today(),
    )
    db.session.add(admin)
    try:
        db.session.commit()
        print("✅ Compte gestionnaire créé: admin@defisante.local / Admin123!")
    except Exception:
        db.session.rollback()
