# Fait par Mathis Duvivé et Alexandre Pech-Rossell
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from api import db
from api.models import Defi, ParticipationDefi, Participant, Equipe

defis_bp = Blueprint("defis", __name__)


def require_gestionnaire():
    pid = int(get_jwt_identity())
    p = Participant.query.get(pid)
    return p and p.role == "gestionnaire"


@defis_bp.route("/", methods=["GET"])
@jwt_required()
def liste_defis():
    defis = Defi.query.order_by(Defi.date_debut.desc()).all()
    return jsonify([d.to_dict() for d in defis]), 200


@defis_bp.route("/actif", methods=["GET"])
@jwt_required()
def defi_actif():
    today = date.today()
    defi = Defi.query.filter(Defi.date_debut <= today, Defi.date_fin >= today).first()
    if not defi:
        return jsonify({"message": "Aucun défi actif en ce moment."}), 404
    return jsonify(defi.to_dict()), 200


@defis_bp.route("/", methods=["POST"])
@jwt_required()
def creer_defi():
    if not require_gestionnaire():
        return jsonify({"erreur": "Accès refusé."}), 403
    data = request.get_json()
    required = ["nom", "date_debut", "date_fin"]
    for f in required:
        if not data.get(f):
            return jsonify({"erreur": f"Champ manquant: {f}"}), 400
    defi = Defi(
        nom=data["nom"],
        date_debut=date.fromisoformat(data["date_debut"]),
        date_fin=date.fromisoformat(data["date_fin"]),
    )
    db.session.add(defi)
    db.session.commit()
    return jsonify(defi.to_dict()), 201


@defis_bp.route("/<int:did>", methods=["GET"])
@jwt_required()
def get_defi(did):
    d = Defi.query.get_or_404(did)
    return jsonify(d.to_dict()), 200


@defis_bp.route("/<int:did>", methods=["PUT"])
@jwt_required()
def modifier_defi(did):
    if not require_gestionnaire():
        return jsonify({"erreur": "Accès refusé."}), 403
    d = Defi.query.get_or_404(did)
    data = request.get_json()
    if "nom" in data:
        d.nom = data["nom"]
    if "date_debut" in data:
        d.date_debut = date.fromisoformat(data["date_debut"])
    if "date_fin" in data:
        d.date_fin = date.fromisoformat(data["date_fin"])
    db.session.commit()
    return jsonify(d.to_dict()), 200


@defis_bp.route("/<int:did>", methods=["DELETE"])
@jwt_required()
def supprimer_defi(did):
    if not require_gestionnaire():
        return jsonify({"erreur": "Accès refusé."}), 403
    d = Defi.query.get_or_404(did)
    db.session.delete(d)
    db.session.commit()
    return jsonify({"message": "Défi supprimé."}), 200


@defis_bp.route("/<int:did>/inscrire", methods=["POST"])
@jwt_required()
def inscrire_defi(did):
    participant_id = int(get_jwt_identity())
    defi = Defi.query.get_or_404(did)
    data = request.get_json() or {}

    # Check already registered
    existing = ParticipationDefi.query.filter_by(id_defi=did, id_participant=participant_id).first()
    if existing:
        return jsonify({"erreur": "Vous êtes déjà inscrit à ce défi."}), 409

    participant = Participant.query.get(participant_id)
    part = ParticipationDefi(
        id_defi=did,
        id_participant=participant_id,
        id_equipe=data.get("id_equipe") or participant.id_equipe,
    )
    db.session.add(part)
    db.session.commit()
    return jsonify({"message": "Inscription réussie.", "participation": part.to_dict()}), 201


@defis_bp.route("/<int:did>/participants", methods=["GET"])
@jwt_required()
def participants_defi(did):
    defi = Defi.query.get_or_404(did)
    parts = ParticipationDefi.query.filter_by(id_defi=did).all()
    result = []
    for p in parts:
        d = p.participant.to_dict()
        d["id_equipe_defi"] = p.id_equipe
        result.append(d)
    return jsonify(result), 200
