from api import db
from datetime import date


class Participant(db.Model):
    __tablename__ = "participant"

    id_participant = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    courriel = db.Column(db.String(200), nullable=False, unique=True)
    mot_de_passe = db.Column(db.String(200), nullable=False)
    sexe = db.Column(db.String(10), nullable=False)  # homme, femme, mixte
    role = db.Column(db.String(20), nullable=False, default="participant")  # participant, gestionnaire
    date_inscription = db.Column(db.Date, nullable=False, default=date.today)
    id_equipe = db.Column(db.Integer, db.ForeignKey("equipe.id_equipe"), nullable=True)

    saisies = db.relationship("SaisieActivite", back_populates="participant", lazy="dynamic")
    participations = db.relationship("ParticipationDefi", back_populates="participant", lazy="dynamic")
    equipe = db.relationship("Equipe", back_populates="membres")

    def to_dict(self):
        return {
            "id_participant": self.id_participant,
            "prenom": self.prenom,
            "nom": self.nom,
            "courriel": self.courriel,
            "sexe": self.sexe,
            "role": self.role,
            "date_inscription": self.date_inscription.isoformat() if self.date_inscription else None,
            "id_equipe": self.id_equipe,
            "equipe_nom": self.equipe.nom if self.equipe else None,
        }


class Equipe(db.Model):
    __tablename__ = "equipe"

    id_equipe = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    membres = db.relationship("Participant", back_populates="equipe", lazy="dynamic")
    participations = db.relationship("ParticipationDefi", back_populates="equipe", lazy="dynamic")

    def to_dict(self):
        return {
            "id_equipe": self.id_equipe,
            "nom": self.nom,
            "description": self.description,
            "nb_membres": self.membres.count(),
        }


class Activite(db.Model):
    __tablename__ = "activite"

    id_activite = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    points_homme = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    points_femme = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    points_mixte = db.Column(db.Numeric(5, 2), nullable=False, default=0)

    saisies = db.relationship("SaisieActivite", back_populates="activite", lazy="dynamic")

    def to_dict(self):
        return {
            "id_activite": self.id_activite,
            "nom": self.nom,
            "description": self.description,
            "points_homme": float(self.points_homme),
            "points_femme": float(self.points_femme),
            "points_mixte": float(self.points_mixte),
        }


class Defi(db.Model):
    __tablename__ = "defi"

    id_defi = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)

    participations = db.relationship("ParticipationDefi", back_populates="defi", lazy="dynamic")

    @property
    def actif(self):
        today = date.today()
        return self.date_debut <= today <= self.date_fin

    def to_dict(self):
        return {
            "id_defi": self.id_defi,
            "nom": self.nom,
            "date_debut": self.date_debut.isoformat(),
            "date_fin": self.date_fin.isoformat(),
            "actif": self.actif,
            "nb_participants": self.participations.count(),
        }


class ParticipationDefi(db.Model):
    __tablename__ = "participation_defi"

    id_participation = db.Column(db.Integer, primary_key=True)
    id_defi = db.Column(db.Integer, db.ForeignKey("defi.id_defi"), nullable=False)
    id_participant = db.Column(db.Integer, db.ForeignKey("participant.id_participant"), nullable=False)
    id_equipe = db.Column(db.Integer, db.ForeignKey("equipe.id_equipe"), nullable=True)

    defi = db.relationship("Defi", back_populates="participations")
    participant = db.relationship("Participant", back_populates="participations")
    equipe = db.relationship("Equipe", back_populates="participations")

    def to_dict(self):
        return {
            "id_participation": self.id_participation,
            "id_defi": self.id_defi,
            "id_participant": self.id_participant,
            "id_equipe": self.id_equipe,
        }


class SaisieActivite(db.Model):
    __tablename__ = "saisie_activite"

    id_saisie = db.Column(db.Integer, primary_key=True)
    date_activite = db.Column(db.Date, nullable=False, default=date.today)
    duree_minutes = db.Column(db.Integer, nullable=False)
    intensite = db.Column(db.String(20), nullable=False, default="moyenne")  # faible, moyenne, intense
    points_obtenus = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    id_participant = db.Column(db.Integer, db.ForeignKey("participant.id_participant"), nullable=False)
    id_activite = db.Column(db.Integer, db.ForeignKey("activite.id_activite"), nullable=False)
    id_defi = db.Column(db.Integer, db.ForeignKey("defi.id_defi"), nullable=True)

    participant = db.relationship("Participant", back_populates="saisies")
    activite = db.relationship("Activite", back_populates="saisies")

    def to_dict(self):
        return {
            "id_saisie": self.id_saisie,
            "date_activite": self.date_activite.isoformat(),
            "duree_minutes": self.duree_minutes,
            "intensite": self.intensite,
            "points_obtenus": float(self.points_obtenus),
            "id_participant": self.id_participant,
            "participant_nom": f"{self.participant.prenom} {self.participant.nom}" if self.participant else None,
            "id_activite": self.id_activite,
            "activite_nom": self.activite.nom if self.activite else None,
            "id_defi": self.id_defi,
        }
