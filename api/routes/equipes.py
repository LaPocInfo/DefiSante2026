from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api import db
from api.models import Equipe, Participant

equipes_bp = Blueprint("equipes", __name__)


def require_gestionnaire():
    pid = int(get_jwt_identity())
    p = Participant.query.get(pid)
    return p and p.role == "gestionnaire"


@equipes_bp.route("/", methods=["GET"])
@jwt_required()
def liste_equipes():
    equipes = Equipe.query.order_by(Equipe.nom).all()
    result = []
    for e in equipes:
        d = e.to_dict()
        d["membres"] = [m.to_dict() for m in e.membres.all()]
        result.append(d)
    return jsonify(result), 200


@equipes_bp.route("/", methods=["POST"])
@jwt_required()
def creer_equipe():
    if not require_gestionnaire():
        return jsonify({"erreur": "Accès refusé."}), 403
    data = request.get_json()
    if not data.get("nom"):
        return jsonify({"erreur": "Le nom de l'équipe est requis."}), 400
    equipe = Equipe(nom=data["nom"], description=data.get("description", ""))
    db.session.add(equipe)
    db.session.commit()
    return jsonify(equipe.to_dict()), 201


@equipes_bp.route("/<int:eid>", methods=["GET"])
@jwt_required()
def get_equipe(eid):
    e = Equipe.query.get_or_404(eid)
    d = e.to_dict()
    d["membres"] = [m.to_dict() for m in e.membres.all()]
    return jsonify(d), 200


@equipes_bp.route("/<int:eid>", methods=["PUT"])
@jwt_required()
def modifier_equipe(eid):
    if not require_gestionnaire():
        return jsonify({"erreur": "Accès refusé."}), 403
    e = Equipe.query.get_or_404(eid)
    data = request.get_json()
    if "nom" in data:
        e.nom = data["nom"]
    if "description" in data:
        e.description = data["description"]
    db.session.commit()
    return jsonify(e.to_dict()), 200


@equipes_bp.route("/<int:eid>", methods=["DELETE"])
@jwt_required()
def supprimer_equipe(eid):
    if not require_gestionnaire():
        return jsonify({"erreur": "Accès refusé."}), 403
    e = Equipe.query.get_or_404(eid)
    db.session.delete(e)
    db.session.commit()
    return jsonify({"message": "Équipe supprimée."}), 200


@equipes_bp.route("/<int:eid>/membres", methods=["POST"])
@jwt_required()
def ajouter_membre(eid):
    if not require_gestionnaire():
        return jsonify({"erreur": "Accès refusé."}), 403
    data = request.get_json()
    pid = data.get("id_participant")
    if not pid:
        return jsonify({"erreur": "id_participant requis."}), 400
    p = Participant.query.get_or_404(pid)
    # Validate team size (max 4 per spec)
    equipe = Equipe.query.get_or_404(eid)
    if equipe.membres.count() >= 4:
        return jsonify({"erreur": "Une équipe ne peut pas avoir plus de 4 membres."}), 400
    p.id_equipe = eid
    db.session.commit()
    return jsonify({"message": f"{p.prenom} {p.nom} ajouté à l'équipe.", "participant": p.to_dict()}), 200


@equipes_bp.route("/<int:eid>/membres/<int:pid>", methods=["DELETE"])
@jwt_required()
def retirer_membre(eid, pid):
    if not require_gestionnaire():
        return jsonify({"erreur": "Accès refusé."}), 403
    p = Participant.query.get_or_404(pid)
    if p.id_equipe != eid:
        return jsonify({"erreur": "Ce participant n'est pas dans cette équipe."}), 400
    p.id_equipe = None
    db.session.commit()
    return jsonify({"message": "Membre retiré de l'équipe."}), 200
