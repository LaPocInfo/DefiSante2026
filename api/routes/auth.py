from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from api import db, bcrypt
from api.models import Participant, Defi, Equipe, ParticipationDefi

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/defis-publics", methods=["GET"])
def defis_publics():
    """Route publique pour lister les défis disponibles (sans JWT)."""
    defis = Defi.query.order_by(Defi.date_debut.desc()).all()
    return jsonify([d.to_dict() for d in defis]), 200


@auth_bp.route("/equipes-publiques", methods=["GET"])
def equipes_publiques():
    """Route publique pour lister les équipes disponibles (sans JWT)."""
    equipes = Equipe.query.order_by(Equipe.nom).all()
    return jsonify([e.to_dict() for e in equipes]), 200


@auth_bp.route("/inscription", methods=["POST"])
def inscription():
    data = request.get_json()
    required = ["prenom", "nom", "courriel", "mot_de_passe", "sexe"]
    for field in required:
        if not data.get(field):
            return jsonify({"erreur": f"Champ manquant: {field}"}), 400

    if Participant.query.filter_by(courriel=data["courriel"]).first():
        return jsonify({"erreur": "Ce courriel est déjà utilisé."}), 409

    SEXES_VALIDES = ("homme", "femme", "non-binaire", "autre")
    sexe = data["sexe"].lower()
    if sexe not in SEXES_VALIDES:
        return jsonify({"erreur": "Valeur invalide. Valeurs acceptées: homme, femme, non-binaire, autre"}), 400

    hash_mdp = bcrypt.generate_password_hash(data["mot_de_passe"]).decode("utf-8")

    # Gestion de l'équipe optionnelle
    id_equipe = data.get("id_equipe") or None
    if id_equipe:
        equipe = Equipe.query.get(id_equipe)
        if not equipe:
            return jsonify({"erreur": "Équipe introuvable."}), 400
        if equipe.membres.count() >= 4:
            return jsonify({"erreur": "Cette équipe est déjà complète (max 4 membres)."}), 400

    participant = Participant(
        prenom=data["prenom"],
        nom=data["nom"],
        courriel=data["courriel"],
        mot_de_passe=hash_mdp,
        sexe=sexe,
        role=data.get("role", "participant"),
        id_equipe=id_equipe,
    )
    db.session.add(participant)
    db.session.flush()  # Pour obtenir l'id_participant avant le commit

    # Inscription automatique au(x) défi(s) choisi(s)
    id_defis = data.get("id_defis", [])
    if isinstance(id_defis, int):
        id_defis = [id_defis]
    for id_defi in id_defis:
        defi = Defi.query.get(id_defi)
        if defi:
            participation = ParticipationDefi(
                id_defi=id_defi,
                id_participant=participant.id_participant,
                id_equipe=id_equipe,
            )
            db.session.add(participation)

    db.session.commit()

    token = create_access_token(identity=str(participant.id_participant))
    return jsonify({"token": token, "participant": participant.to_dict()}), 201


@auth_bp.route("/connexion", methods=["POST"])
def connexion():
    data = request.get_json()
    if not data.get("courriel") or not data.get("mot_de_passe"):
        return jsonify({"erreur": "Courriel et mot de passe requis."}), 400

    participant = Participant.query.filter_by(courriel=data["courriel"]).first()
    if not participant or not bcrypt.check_password_hash(participant.mot_de_passe, data["mot_de_passe"]):
        return jsonify({"erreur": "Identifiants invalides."}), 401

    token = create_access_token(identity=str(participant.id_participant))
    return jsonify({"token": token, "participant": participant.to_dict()}), 200


@auth_bp.route("/moi/defis", methods=["GET"])
@jwt_required()
def mes_defis():
    participant_id = int(get_jwt_identity())
    participations = ParticipationDefi.query.filter_by(id_participant=participant_id).all()
    result = []
    for p in participations:
        d = p.defi.to_dict()
        d["id_equipe_defi"] = p.id_equipe
        if p.id_equipe:
            eq = Equipe.query.get(p.id_equipe)
            d["equipe_nom_defi"] = eq.nom if eq else None
        else:
            d["equipe_nom_defi"] = None
        result.append(d)
    return jsonify(result), 200


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
        if data["sexe"].lower() not in ("homme", "femme", "non-binaire", "autre"):
            return jsonify({"erreur": "Valeur invalide. Valeurs acceptées: homme, femme, non-binaire, autre"}), 400
        participant.sexe = data["sexe"].lower()
    if "mot_de_passe" in data and data["mot_de_passe"]:
        participant.mot_de_passe = bcrypt.generate_password_hash(data["mot_de_passe"]).decode("utf-8")

    db.session.commit()
    return jsonify(participant.to_dict()), 200
