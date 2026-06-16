"""
seed_demo.py — Remplit la BDD avec des données fictives pour tester l'application.

Usage :
    python seed_demo.py
    docker exec -it defisante_api python seed_demo.py
Le script crée :
  - 3 équipes
  - 10 participants (dont 1 gestionnaire) répartis dans les équipes
  - 2 défis (un passé, un en cours)
  - Des participations aux défis
  - ~60 saisies d'activités réparties sur les dernières semaines
"""

# from api import create_app, db, bcrypt
from api import bcrypt
import os, sys, random
from datetime import date, timedelta

# ── Charger l'app Flask ────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

from api import create_app, db
from api.models import Participant, Equipe, Activite, Defi, ParticipationDefi, SaisieActivite
from api.utils.seed import seed_activites
from werkzeug.security import generate_password_hash

app = create_app()

# ── Données fictives ───────────────────────────────────────────────────────────
EQUIPES = [
    {"nom": "Les Cheetahs",      "description": "Vitesse et endurance avant tout."},
    {"nom": "Les Ours Polaires",  "description": "Solides comme la glace."},
    {"nom": "Les Aigles",        "description": "Toujours plus haut."},
]

PARTICIPANTS = [
    # (prenom, nom, courriel, sexe, role)
    ("Alice",   "Tremblay",  "alice@demo.com",   "femme",  "gestionnaire"),
    ("Bob",     "Gagnon",    "bob@demo.com",      "homme",  "participant"),
    ("Camille", "Roy",       "camille@demo.com",  "femme",  "participant"),
    ("David",   "Côté",      "david@demo.com",    "homme",  "participant"),
    ("Emma",    "Bouchard",  "emma@demo.com",     "femme",  "participant"),
    ("François","Lavoie",    "francois@demo.com", "homme",  "participant"),
    ("Gina",    "Fortin",    "gina@demo.com",     "mixte",  "participant"),
    ("Hugo",    "Gauthier",  "hugo@demo.com",     "homme",  "participant"),
    ("Iris",    "Morin",     "iris@demo.com",     "femme",  "participant"),
    ("Julien",  "Pelletier", "julien@demo.com",   "homme",  "participant"),
]

DEFIS = [
    {
        "nom": "Défi Printemps 2025",
        "date_debut": date.today() - timedelta(days=90),
        "date_fin":   date.today() - timedelta(days=10),
    },
    {
        "nom": "Défi Santé Été 2026",
        "date_debut": date.today() - timedelta(days=5),
        "date_fin":   date.today() + timedelta(days=55),
    },
]

MOT_DE_PASSE = "demo1234"
INTENSITES   = ["faible", "moyenne", "intense"]
MULTIPLICATEURS = {"faible": 0.75, "moyenne": 1.0, "intense": 1.25}


def calculer_points(base, duree, intensite):
    return round(base * (duree / 30) * MULTIPLICATEURS[intensite], 2)


def run():
    with app.app_context():
        # 1. Activités (utilise le seed existant)
        seed_activites()
        activites = Activite.query.all()
        print(f"📦 {len(activites)} activités disponibles.")

        # 2. Équipes
        equipes = []
        for e_data in EQUIPES:
            existing = Equipe.query.filter_by(nom=e_data["nom"]).first()
            if existing:
                equipes.append(existing)
                print(f"   équipe déjà présente : {existing.nom}")
            else:
                e = Equipe(**e_data)
                db.session.add(e)
                db.session.flush()
                equipes.append(e)
        db.session.commit()
        print(f"✅ {len(equipes)} équipes.")

        # 3. Participants
        participants = []
        # mdp_hash = generate_password_hash(MOT_DE_PASSE)
        mdp_hash = bcrypt.generate_password_hash(MOT_DE_PASSE).decode("utf-8"),
        equipe_cycle = equipes * 4           # 3 équipes pour 10 participants
        for i, (prenom, nom, courriel, sexe, role) in enumerate(PARTICIPANTS):
            existing = Participant.query.filter_by(courriel=courriel).first()
            if existing:
                participants.append(existing)
                print(f"   participant déjà présent : {courriel}")
                continue
            p = Participant(
                prenom=prenom,
                nom=nom,
                courriel=courriel,
                mot_de_passe=mdp_hash,
                sexe=sexe,
                role=role,
                date_inscription=date.today() - timedelta(days=random.randint(10, 100)),
                id_equipe=equipe_cycle[i].id_equipe,
            )
            db.session.add(p)
            db.session.flush()
            participants.append(p)
        db.session.commit()
        print(f"✅ {len(participants)} participants  (mot de passe : {MOT_DE_PASSE})")

        # 4. Défis
        defis = []
        for d_data in DEFIS:
            existing = Defi.query.filter_by(nom=d_data["nom"]).first()
            if existing:
                defis.append(existing)
            else:
                d = Defi(**d_data)
                db.session.add(d)
                db.session.flush()
                defis.append(d)
        db.session.commit()
        print(f"✅ {len(defis)} défis.")

        # 5. Participations aux défis (tous les participants participent au défi en cours)
        defi_actif = defis[1]
        defi_passe = defis[0]
        nb_part = 0
        for p in participants:
            # Défi actif : tous
            if not ParticipationDefi.query.filter_by(id_defi=defi_actif.id_defi, id_participant=p.id_participant).first():
                db.session.add(ParticipationDefi(
                    id_defi=defi_actif.id_defi,
                    id_participant=p.id_participant,
                    id_equipe=p.id_equipe,
                ))
                nb_part += 1
            # Défi passé : 6 premiers seulement
            if participants.index(p) < 6:
                if not ParticipationDefi.query.filter_by(id_defi=defi_passe.id_defi, id_participant=p.id_participant).first():
                    db.session.add(ParticipationDefi(
                        id_defi=defi_passe.id_defi,
                        id_participant=p.id_participant,
                        id_equipe=p.id_equipe,
                    ))
                    nb_part += 1
        db.session.commit()
        print(f"✅ {nb_part} participations aux défis.")

        # 6. Saisies d'activités
        nb_saisies = 0
        # Période du défi actif + quelques semaines avant
        date_min = defi_actif.date_debut - timedelta(days=14)
        date_max = date.today()

        for p in participants:
            nb = random.randint(4, 10)       # entre 4 et 10 saisies par participant
            for _ in range(nb):
                act = random.choice(activites)
                duree = random.choice([20, 30, 45, 60, 90])
                intensite = random.choice(INTENSITES)
                delta = (date_max - date_min).days
                date_act = date_min + timedelta(days=random.randint(0, delta))

                sexe = p.sexe
                base = float(act.points_homme if sexe == "homme" else
                             act.points_femme if sexe == "femme" else
                             act.points_mixte)
                points = calculer_points(base, duree, intensite)

                s = SaisieActivite(
                    date_activite=date_act,
                    duree_minutes=duree,
                    intensite=intensite,
                    points_obtenus=points,
                    id_participant=p.id_participant,
                    id_activite=act.id_activite,
                )
                db.session.add(s)
                nb_saisies += 1

        db.session.commit()
        print(f"✅ {nb_saisies} saisies d'activités.")

        print("\n🎉 Base de données remplie avec succès !")
        print(f"   Connectez-vous avec n'importe quel courriel ci-dessus")
        print(f"   et le mot de passe : {MOT_DE_PASSE}")
        print(f"\n   Exemple gestionnaire : alice@demo.com / {MOT_DE_PASSE}")
        print(f"   Exemple participant  : bob@demo.com   / {MOT_DE_PASSE}")


if __name__ == "__main__":
    run()
