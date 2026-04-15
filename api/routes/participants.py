from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api import db, bcrypt
from api.models import Participant

participants_bp = Blueprint("participants", __name__)


def require_gestionnaire():
    pid = int(get_jwt_identity())
    p = Participant.query.get(pid)
    return p and p.role == "gestionnaire"


@participants_bp.route("/", methods=["GET"])
@jwt_required()
def liste_participants():
    if not require_gestionnaire():
        return jsonify({"erreur": "Accès refusé."}), 403
    participants = Participant.query.order_by(Participant.nom).all()
    return jsonify([p.to_dict() for p in participants]), 200


@participants_bp.route("/<int:pid>", methods=["GET"])
@jwt_required()
def get_participant(pid):
    current_id = int(get_jwt_identity())
    current = Participant.query.get(current_id)
    if current_id != pid and current.role != "gestionnaire":
        return jsonify({"erreur": "Accès refusé."}), 403
    p = Participant.query.get_or_404(pid)
    return jsonify(p.to_dict()), 200


@participants_bp.route("/<int:pid>", methods=["PUT"])
@jwt_required()
def modifier_participant(pid):
    current_id = int(get_jwt_identity())
    current = Participant.query.get(current_id)
    if current_id != pid and current.role != "gestionnaire":
        return jsonify({"erreur": "Accès refusé."}), 403

    p = Participant.query.get_or_404(pid)
    data = request.get_json()

    for field in ["prenom", "nom", "sexe"]:
        if field in data:
            setattr(p, field, data[field])
    if "mot_de_passe" in data and data["mot_de_passe"]:
        p.mot_de_passe = bcrypt.generate_password_hash(data["mot_de_passe"]).decode("utf-8")
    if "id_equipe" in data:
        p.id_equipe = data["id_equipe"]
    if "role" in data and current.role == "gestionnaire":
        p.role = data["role"]

    db.session.commit()
    return jsonify(p.to_dict()), 200


@participants_bp.route("/<int:pid>", methods=["DELETE"])
@jwt_required()
def supprimer_participant(pid):
    if not require_gestionnaire():
        return jsonify({"erreur": "Accès refusé."}), 403
    p = Participant.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Participant supprimé."}), 200
