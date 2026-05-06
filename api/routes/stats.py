from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from api import db
from api.models import SaisieActivite, Participant, Equipe, Activite, ParticipationDefi, Defi

stats_bp = Blueprint("stats", __name__)


def _defi_participant_ids(did):
    """IDs des participants inscrits au défi."""
    rows = ParticipationDefi.query.filter_by(id_defi=did).all()
    return [r.id_participant for r in rows]


def _apply_defi_filter(query, did, defi):
    """Filtre les saisies sur la plage de dates du défi ET les participants inscrits."""
    pids = _defi_participant_ids(did)
    query = query.filter(
        SaisieActivite.id_participant.in_(pids),
        SaisieActivite.date_activite >= defi.date_debut,
        SaisieActivite.date_activite <= defi.date_fin,
    )
    return query


@stats_bp.route("/classement/participants", methods=["GET"])
@jwt_required()
def classement_participants():
    """Total points per participant, optionally filtered by defi."""
    did = request.args.get("id_defi", type=int)
    defi = Defi.query.get(did) if did else None

    query = db.session.query(
        Participant.id_participant,
        Participant.prenom,
        Participant.nom,
        Participant.sexe,
        Participant.id_equipe,
        func.coalesce(func.sum(SaisieActivite.points_obtenus), 0).label("total_points"),
        func.coalesce(func.sum(SaisieActivite.duree_minutes), 0).label("total_minutes"),
        func.coalesce(func.count(SaisieActivite.id_saisie), 0).label("nb_activites"),
    ).outerjoin(SaisieActivite, SaisieActivite.id_participant == Participant.id_participant)

    if did and defi:
        pids = _defi_participant_ids(did)
        query = query.filter(
            Participant.id_participant.in_(pids),
            (SaisieActivite.date_activite >= defi.date_debut) | (SaisieActivite.id_saisie == None),
            (SaisieActivite.date_activite <= defi.date_fin) | (SaisieActivite.id_saisie == None),
        )

    result = query.group_by(
        Participant.id_participant, Participant.prenom, Participant.nom, Participant.sexe, Participant.id_equipe
    ).order_by(func.coalesce(func.sum(SaisieActivite.points_obtenus), 0).desc()).all()

    classement = []
    for i, row in enumerate(result):
        equipe = Equipe.query.get(row.id_equipe) if row.id_equipe else None
        classement.append({
            "rang": i + 1,
            "id_participant": row.id_participant,
            "prenom": row.prenom,
            "nom": row.nom,
            "sexe": row.sexe,
            "equipe_nom": equipe.nom if equipe else None,
            "total_points": float(row.total_points),
            "total_minutes": int(row.total_minutes),
            "nb_activites": int(row.nb_activites),
        })
    return jsonify(classement), 200


@stats_bp.route("/classement/equipes", methods=["GET"])
@jwt_required()
def classement_equipes():
    """Total and average points per team."""
    did = request.args.get("id_defi", type=int)
    defi = Defi.query.get(did) if did else None
    defi_pids = set(_defi_participant_ids(did)) if did else None

    equipes = Equipe.query.order_by(Equipe.nom).all()
    result = []
    for equipe in equipes:
        membres = equipe.membres.all()
        if not membres:
            continue

        total_points = 0
        total_minutes = 0
        nb_activites = 0
        for m in membres:
            if defi_pids is not None and m.id_participant not in defi_pids:
                continue
            q = SaisieActivite.query.filter_by(id_participant=m.id_participant)
            if defi:
                q = q.filter(
                    SaisieActivite.date_activite >= defi.date_debut,
                    SaisieActivite.date_activite <= defi.date_fin,
                )
            saisies = q.all()
            total_points += sum(float(s.points_obtenus) for s in saisies)
            total_minutes += sum(s.duree_minutes for s in saisies)
            nb_activites += len(saisies)

        result.append({
            "id_equipe": equipe.id_equipe,
            "nom": equipe.nom,
            "nb_membres": len(membres),
            "total_points": round(total_points, 2),
            "moyenne_points": round(total_points / len(membres), 2) if membres else 0,
            "total_minutes": total_minutes,
            "nb_activites": nb_activites,
        })

    result.sort(key=lambda x: x["total_points"], reverse=True)
    for i, r in enumerate(result):
        r["rang"] = i + 1

    return jsonify(result), 200


@stats_bp.route("/activites/populaires", methods=["GET"])
@jwt_required()
def activites_populaires():
    """Most practiced activities with point totals."""
    did = request.args.get("id_defi", type=int)
    defi = Defi.query.get(did) if did else None

    query = db.session.query(
        Activite.id_activite,
        Activite.nom,
        func.count(SaisieActivite.id_saisie).label("nb_saisies"),
        func.coalesce(func.sum(SaisieActivite.points_obtenus), 0).label("total_points"),
        func.coalesce(func.sum(SaisieActivite.duree_minutes), 0).label("total_minutes"),
    ).outerjoin(SaisieActivite, SaisieActivite.id_activite == Activite.id_activite)

    if did and defi:
        pids = _defi_participant_ids(did)
        query = query.filter(
            (SaisieActivite.id_participant.in_(pids)) | (SaisieActivite.id_saisie == None),
            (SaisieActivite.date_activite >= defi.date_debut) | (SaisieActivite.id_saisie == None),
            (SaisieActivite.date_activite <= defi.date_fin) | (SaisieActivite.id_saisie == None),
        )

    result = query.group_by(Activite.id_activite, Activite.nom)\
        .order_by(func.count(SaisieActivite.id_saisie).desc()).limit(20).all()

    return jsonify([{
        "id_activite": r.id_activite,
        "nom": r.nom,
        "nb_saisies": int(r.nb_saisies),
        "total_points": float(r.total_points),
        "total_minutes": int(r.total_minutes),
    } for r in result]), 200


@stats_bp.route("/repartition/sexe", methods=["GET"])
@jwt_required()
def repartition_sexe():
    """Point distribution by sex."""
    did = request.args.get("id_defi", type=int)
    defi = Defi.query.get(did) if did else None

    query = db.session.query(
        Participant.sexe,
        func.count(Participant.id_participant.distinct()).label("nb_participants"),
        func.coalesce(func.sum(SaisieActivite.points_obtenus), 0).label("total_points"),
    ).outerjoin(SaisieActivite, SaisieActivite.id_participant == Participant.id_participant)

    if did and defi:
        pids = _defi_participant_ids(did)
        query = query.filter(
            Participant.id_participant.in_(pids),
            (SaisieActivite.date_activite >= defi.date_debut) | (SaisieActivite.id_saisie == None),
            (SaisieActivite.date_activite <= defi.date_fin) | (SaisieActivite.id_saisie == None),
        )

    result = query.group_by(Participant.sexe).all()

    return jsonify([{
        "sexe": r.sexe,
        "nb_participants": int(r.nb_participants),
        "total_points": float(r.total_points),
    } for r in result]), 200


@stats_bp.route("/resume", methods=["GET"])
@jwt_required()
def resume_global():
    """Global summary stats."""
    did = request.args.get("id_defi", type=int)
    defi = Defi.query.get(did) if did else None

    q = SaisieActivite.query
    if did and defi:
        pids = _defi_participant_ids(did)
        q = q.filter(
            SaisieActivite.id_participant.in_(pids),
            SaisieActivite.date_activite >= defi.date_debut,
            SaisieActivite.date_activite <= defi.date_fin,
        )

    saisies = q.all()
    total_points = sum(float(s.points_obtenus) for s in saisies)
    total_minutes = sum(s.duree_minutes for s in saisies)
    nb_saisies = len(saisies)

    nb_participants = Participant.query.count()
    nb_equipes = Equipe.query.count()

    if did:
        nb_participants = ParticipationDefi.query.filter_by(id_defi=did).count()

    return jsonify({
        "total_points": round(total_points, 2),
        "total_minutes": total_minutes,
        "nb_saisies": nb_saisies,
        "nb_participants": nb_participants,
        "nb_equipes": nb_equipes,
        "heures_activite": round(total_minutes / 60, 1),
    }), 200
