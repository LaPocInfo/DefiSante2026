from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api import db, bcrypt
from api.models import Participant

participants_bp = Blueprint("participants", __name__)


def _est_gestionnaire(participant_id: int) -> bool:
    p = Participant.query.get(participant_id)
    return p and p.role == "gestionnaire"


# ── GET /api/participants/ ─────────────────────────────────────────────────
@participants_bp.route("/", methods=["GET"])
@jwt_required()
def liste_participants():
    """
    Retourne la liste de tous les participants.
    Réservé aux gestionnaires.

    Exemple de requête :
      GET /api/participants/
      Authorization: Bearer <token>
    """
    current_id = int(get_jwt_identity())
    if not _est_gestionnaire(current_id):
        return jsonify({"erreur": "Accès réservé aux gestionnaires."}), 403

    participants = Participant.query.order_by(Participant.nom).all()
    return jsonify([p.to_dict() for p in participants]), 200


# ── GET /api/participants/<id> ─────────────────────────────────────────────
@participants_bp.route("/<int:pid>", methods=["GET"])
@jwt_required()
def get_participant(pid):
    """
    Retourne les infos d'un participant par son id.
    Un participant peut voir son propre profil ; un gestionnaire peut voir n'importe qui.

    Exemple de requête :
      GET /api/participants/3
      Authorization: Bearer <token>
    """
    current_id = int(get_jwt_identity())
    if current_id != pid and not _est_gestionnaire(current_id):
        return jsonify({"erreur": "Accès refusé."}), 403

    participant = Participant.query.get_or_404(pid)
    return jsonify(participant.to_dict()), 200


# ── PUT /api/participants/<id> ─────────────────────────────────────────────
@participants_bp.route("/<int:pid>", methods=["PUT"])
@jwt_required()
def modifier_participant(pid):
    """
    Modifie un participant.
    Un participant peut modifier son propre profil ; un gestionnaire peut modifier n'importe qui.

    Corps JSON accepté :
    {
        "prenom": "Alice",
        "nom": "Tremblay",
        "sexe": "femme",
        "mot_de_passe": "NouveauMdp1!",
        "role": "gestionnaire"   // gestionnaire seulement
    }
    """
    current_id = int(get_jwt_identity())
    if current_id != pid and not _est_gestionnaire(current_id):
        return jsonify({"erreur": "Accès refusé."}), 403

    participant = Participant.query.get_or_404(pid)
    data = request.get_json()

    if "prenom" in data:
        participant.prenom = data["prenom"]
    if "nom" in data:
        participant.nom = data["nom"]
    if "sexe" in data:
        if data["sexe"].lower() not in ("homme", "femme", "mixte"):
            return jsonify({"erreur": "Sexe invalide. Valeurs acceptées: homme, femme, mixte"}), 400
        participant.sexe = data["sexe"].lower()
    if "mot_de_passe" in data and data["mot_de_passe"]:
        participant.mot_de_passe = bcrypt.generate_password_hash(data["mot_de_passe"]).decode("utf-8")
    # Seul un gestionnaire peut changer le rôle
    if "role" in data and _est_gestionnaire(current_id):
        if data["role"] not in ("participant", "gestionnaire"):
            return jsonify({"erreur": "Rôle invalide. Valeurs acceptées: participant, gestionnaire"}), 400
        participant.role = data["role"]

    db.session.commit()
    return jsonify(participant.to_dict()), 200


# ── DELETE /api/participants/<id> ──────────────────────────────────────────
@participants_bp.route("/<int:pid>", methods=["DELETE"])
@jwt_required()
def supprimer_participant(pid):
    """
    Supprime un participant.
    Réservé aux gestionnaires.
    """
    current_id = int(get_jwt_identity())
    if not _est_gestionnaire(current_id):
        return jsonify({"erreur": "Accès réservé aux gestionnaires."}), 403

    participant = Participant.query.get_or_404(pid)
    db.session.delete(participant)
    db.session.commit()
    return jsonify({"message": "Participant supprimé."}), 200
