from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api import db
from api.models import Activite, Participant

activites_bp = Blueprint("activites", __name__)


@activites_bp.route("/", methods=["GET"])
@jwt_required()
def liste_activites():
    q = request.args.get("q", "").strip()
    query = Activite.query
    if q:
        query = query.filter(Activite.nom.ilike(f"%{q}%"))
    activites = query.order_by(Activite.nom).all()
    return jsonify([a.to_dict() for a in activites]), 200


@activites_bp.route("/<int:aid>", methods=["GET"])
@jwt_required()
def get_activite(aid):
    a = Activite.query.get_or_404(aid)
    return jsonify(a.to_dict()), 200


@activites_bp.route("/", methods=["POST"])
@jwt_required()
def creer_activite():
    pid = int(get_jwt_identity())
    p = Participant.query.get(pid)
    if not p or p.role != "gestionnaire":
        return jsonify({"erreur": "Accès refusé."}), 403
    data = request.get_json()
    required = ["nom", "points_homme", "points_femme", "points_mixte"]
    for f in required:
        if f not in data:
            return jsonify({"erreur": f"Champ manquant: {f}"}), 400
    a = Activite(
        nom=data["nom"],
        description=data.get("description", ""),
        points_homme=data["points_homme"],
        points_femme=data["points_femme"],
        points_mixte=data["points_mixte"],
    )
    db.session.add(a)
    db.session.commit()
    return jsonify(a.to_dict()), 201


@activites_bp.route("/<int:aid>", methods=["PUT"])
@jwt_required()
def modifier_activite(aid):
    pid = int(get_jwt_identity())
    p = Participant.query.get(pid)
    if not p or p.role != "gestionnaire":
        return jsonify({"erreur": "Accès refusé."}), 403
    a = Activite.query.get_or_404(aid)
    data = request.get_json()
    for field in ["nom", "description", "points_homme", "points_femme", "points_mixte"]:
        if field in data:
            setattr(a, field, data[field])
    db.session.commit()
    return jsonify(a.to_dict()), 200


@activites_bp.route("/<int:aid>", methods=["DELETE"])
@jwt_required()
def supprimer_activite(aid):
    pid = int(get_jwt_identity())
    p = Participant.query.get(pid)
    if not p or p.role != "gestionnaire":
        return jsonify({"erreur": "Accès refusé."}), 403
    a = Activite.query.get_or_404(aid)
    db.session.delete(a)
    db.session.commit()
    return jsonify({"message": "Activité supprimée."}), 200
