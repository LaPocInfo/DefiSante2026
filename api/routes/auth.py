from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from api import db, bcrypt
from api.models import Participant

auth_bp = Blueprint("auth", __name__)

# Blocklist en mémoire pour la déconnexion
token_blocklist = set()


@auth_bp.route("/inscription", methods=["POST"])
def inscription():
    data = request.get_json()
    required = ["prenom", "nom", "courriel", "mot_de_passe", "sexe"]
    for field in required:
        if not data.get(field):
            return jsonify({"erreur": f"Champ manquant: {field}"}), 400

    if Participant.query.filter_by(courriel=data["courriel"]).first():
        return jsonify({"erreur": "Ce courriel est déjà utilisé."}), 409

    sexe = data["sexe"].lower()
    if sexe not in ("homme", "femme", "mixte"):
        return jsonify({"erreur": "Sexe invalide. Valeurs acceptées: homme, femme, mixte"}), 400

    hash_mdp = bcrypt.generate_password_hash(data["mot_de_passe"]).decode("utf-8")

    participant = Participant(
        prenom=data["prenom"],
        nom=data["nom"],
        courriel=data["courriel"],
        mot_de_passe=hash_mdp,
        sexe=sexe,
        role=data.get("role", "participant"),
    )
    db.session.add(participant)
    db.session.commit()

    access_token = create_access_token(identity=str(participant.id_participant))
    refresh_token = create_refresh_token(identity=str(participant.id_participant))
    return jsonify({
        "token": access_token,
        "refresh_token": refresh_token,
        "participant": participant.to_dict()
    }), 201


@auth_bp.route("/connexion", methods=["POST"])
def connexion():
    data = request.get_json()
    if not data.get("courriel") or not data.get("mot_de_passe"):
        return jsonify({"erreur": "Courriel et mot de passe requis."}), 400

    participant = Participant.query.filter_by(courriel=data["courriel"]).first()
    if not participant or not bcrypt.check_password_hash(participant.mot_de_passe, data["mot_de_passe"]):
        return jsonify({"erreur": "Identifiants invalides."}), 401

    access_token = create_access_token(identity=str(participant.id_participant))
    refresh_token = create_refresh_token(identity=str(participant.id_participant))
    return jsonify({
        "token": access_token,
        "refresh_token": refresh_token,
        "participant": participant.to_dict()
    }), 200


@auth_bp.route("/deconnexion", methods=["POST"])
@jwt_required()
def deconnexion():
    jti = get_jwt()["jti"]
    token_blocklist.add(jti)
    return jsonify({"message": "Déconnexion réussie."}), 200


@auth_bp.route("/refresh-token", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    participant_id = get_jwt_identity()
    new_token = create_access_token(identity=participant_id)
    return jsonify({"token": new_token}), 200


@auth_bp.route("/moi", methods=["GET"])
@jwt_required()
def moi():
    participant_id = int(get_jwt_identity())
    participant = Participant.query.get_or_404(participant_id)
    return jsonify(participant.to_dict()), 200


@auth_bp.route("/moi", methods=["PUT"])
@jwt_required()
def modifier_moi():
    participant_id = int(get_jwt_identity())
    participant = Participant.query.get_or_404(participant_id)
    data = request.get_json()

    if "prenom" in data:
        participant.prenom = data["prenom"]
    if "nom" in data:
        participant.nom = data["nom"]
    if "sexe" in data:
        if data["sexe"].lower() not in ("homme", "femme", "mixte"):
            return jsonify({"erreur": "Sexe invalide."}), 400
        participant.sexe = data["sexe"].lower()
    if "mot_de_passe" in data and data["mot_de_passe"]:
        participant.mot_de_passe = bcrypt.generate_password_hash(data["mot_de_passe"]).decode("utf-8")

    db.session.commit()
    return jsonify(participant.to_dict()), 200
