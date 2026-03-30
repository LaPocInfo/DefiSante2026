from flask import Blueprint, request, jsonify
from api import db
from api.models import Activite

activites_bp = Blueprint("activites", __name__)


# 📋 Liste toutes les activités
@activites_bp.route("/", methods=["GET"])
def liste_activites():
    q = request.args.get("q", "").strip()
    query = Activite.query

    if q:
        query = query.filter(Activite.nom.ilike(f"%{q}%"))

    activites = query.order_by(Activite.nom).all()
    return jsonify([a.to_dict() for a in activites]), 200


# 🔍 Obtenir une activité par ID
@activites_bp.route("/<int:aid>", methods=["GET"])
def get_activite(aid):
    a = Activite.query.get_or_404(aid)
    return jsonify(a.to_dict()), 200


# ➕ Créer une activité
@activites_bp.route("/", methods=["POST"])
def creer_activite():
    data = request.get_json()

    required = ["nom", "points_homme", "points_femme", "points_mixte"]
    for field in required:
        if field not in data:
            return jsonify({"erreur": f"Champ manquant: {field}"}), 400

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


# ✏️ Modifier une activité
@activites_bp.route("/<int:aid>", methods=["PUT"])
def modifier_activite(aid):
    a = Activite.query.get_or_404(aid)
    data = request.get_json()

    for field in [
        "nom",
        "description",
        "points_homme",
        "points_femme",
        "points_mixte",
    ]:
        if field in data:
            setattr(a, field, data[field])

    db.session.commit()
    return jsonify(a.to_dict()), 200


# ❌ Supprimer une activité
@activites_bp.route("/<int:aid>", methods=["DELETE"])
def supprimer_activite(aid):
    a = Activite.query.get_or_404(aid)

    db.session.delete(a)
    db.session.commit()

    return jsonify({"message": "Activité supprimée."}), 200