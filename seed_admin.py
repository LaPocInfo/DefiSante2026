from api import create_app, db, bcrypt
from api.models import Participant
from datetime import date

app = create_app()

with app.app_context():
    if Participant.query.filter_by(courriel="admin@defisante.local").first():
        print("Compte admin existe déjà.")
    else:
        admin = Participant(
            prenom="Admin",
            nom="Défi Santé",
            courriel="admin@defisante.local",
            mot_de_passe=bcrypt.generate_password_hash("Admin123!").decode("utf-8"),
            sexe="mixte",
            role="gestionnaire",
            date_inscription=date.today(),
        )
        db.session.add(admin)
        db.session.commit()
        print("Compte gestionnaire créé: admin@defisante.local / Admin123!")
