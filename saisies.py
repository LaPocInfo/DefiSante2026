from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date
from api import db
from api.models import SaisieActivite, Activite, Participant
from api.utils import calculer_points

saisies_bp = Blueprint("saisies", __name__)


@saisies_bp.route("/", methods=["GET"])
@jwt_required()
def mes_saisies():
    participant_id = int(get_jwt_identity())
    current = Participant.query.get(participant_id)
    pid_filter = request.args.get("id_participant", type=int)
    did_filter = request.args.get("id_defi", type=int)
    if pid_filter and current.role == "gestionnaire":
        query = SaisieActivite.query.filter_by(id_participant=pid_filter)
    else:
        query = SaisieActivite.query.filter_by(id_participant=participant_id)
    if did_filter:
        query = query.filter_by(id_defi=did_filter)
    saisies = query.order_by(SaisieActivite.date_activite.desc()).all()
    return jsonify([s.to_dict() for s in saisies]), 200


@saisies_bp.route("/", methods=["POST"])
@jwt_required()
def ajouter_saisie():
    participant_id = int(get_jwt_identity())
    participant = Participant.query.get(participant_id)
    data = request.get_json()
    required = ["id_activite", "duree_minutes"]
    for f in required:
        if f not in data:
            return jsonify({"erreur": f"Champ manquant: {f}"}), 400
    activite = Activite.query.get_or_404(data["id_activite"])
    duree = int(data["duree_minutes"])
    intensite = data.get("intensite", "moyenne").lower()
    if intensite not in ("faible", "moyenne", "intense"):
        return jsonify({"erreur": "Intensité invalide."}), 400
    sexe = participant.sexe
    if sexe == "homme":
        points_base = float(activite.points_homme)
    elif sexe == "femme":
        points_base = float(activite.points_femme)
    else:
        points_base = float(activite.points_mixte)
    points = calculer_points(points_base, duree, intensite)


    kwargs = dict(
        date_activite=date.fromisoformat(data["date_activite"]) if data.get("date_activite") else date.today(),
        duree_minutes=duree,
        points_obtenus=points,
        id_participant=participant_id,
        id_activite=data["id_activite"],
        id_defi=data.get("id_defi"),
    )
   
    try:
        saisie = SaisieActivite(**kwargs, intensite=intensite)
        db.session.add(saisie)
        db.session.commit()
    except Exception:
        db.session.rollback()
        saisie = SaisieActivite(**kwargs)
        db.session.add(saisie)
        db.session.commit()

    return jsonify(saisie.to_dict()), 201


@saisies_bp.route("/<int:sid>", methods=["GET"])
@jwt_required()
def get_saisie(sid):
    participant_id = int(get_jwt_identity())
    current = Participant.query.get(participant_id)
    s = SaisieActivite.query.get_or_404(sid)
    if s.id_participant != participant_id and current.role != "gestionnaire":
        return jsonify({"erreur": "Accès refusé."}), 403
    return jsonify(s.to_dict()), 200


@saisies_bp.route("/<int:sid>", methods=["DELETE"])
@jwt_required()
def supprimer_saisie(sid):
    participant_id = int(get_jwt_identity())
    current = Participant.query.get(participant_id)
    s = SaisieActivite.query.get_or_404(sid)
    if s.id_participant != participant_id and current.role != "gestionnaire":
        return jsonify({"erreur": "Accès refusé."}), 403
    db.session.delete(s)
    db.session.commit()
    return jsonify({"message": "Saisie supprimée."}), 200


@saisies_bp.route("/preview", methods=["POST"])
@jwt_required()
def preview_points():
    participant_id = int(get_jwt_identity())
    participant = Participant.query.get(participant_id)
    data = request.get_json()
    if not data.get("id_activite") or not data.get("duree_minutes"):
        return jsonify({"erreur": "id_activite et duree_minutes requis."}), 400
    activite = Activite.query.get_or_404(data["id_activite"])
    intensite = data.get("intensite", "moyenne").lower()
    duree = int(data["duree_minutes"])
    sexe = participant.sexe
    if sexe == "homme":
        points_base = float(activite.points_homme)
    elif sexe == "femme":
        points_base = float(activite.points_femme)
    else:
        points_base = float(activite.points_mixte)
    points = calculer_points(points_base, duree, intensite)
    return jsonify({"activite": activite.nom, "duree_minutes": duree, "intensite": intensite, "points_obtenus": points}), 200
