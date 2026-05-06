# 🏃 Défi Santé

Application web de gestion de défi sportif communautaire. Développée dans le cadre d'un stage en Techniques de l'informatique au Cégep La Pocatière.

---

## 🏗️ Architecture

```
defisante/
├── api/                        # Flask REST API (Python)
│   ├── models/                 # Modèles SQLAlchemy (BDD PostgreSQL)
│   ├── routes/                 # Endpoints REST
│   │   ├── auth.py             # Inscription, connexion, JWT
│   │   ├── participants.py     # CRUD participants
│   │   ├── equipes.py          # CRUD équipes + gestion membres
│   │   ├── activites.py        # CRUD 172 activités
│   │   ├── defis.py            # CRUD défis + inscription
│   │   ├── saisies.py          # Saisie d'activités + calcul points
│   │   └── stats.py            # Classements, statistiques
│   └── utils/
│       ├── __init__.py         # Calcul de points (durée × intensité)
│       └── seed.py             # 172 activités pré-chargées
├── frontend/                   # Interface web HTML/CSS/JS
│   ├── index.html              # Connexion / Inscription
│   ├── css/style.css           # Design complet
│   ├── js/app.js               # Client API, utilitaires
│   └── pages/
│       ├── tableau-de-bord.html
│       ├── saisie.html         # Saisir une activité
│       ├── mes-activites.html  # Historique personnel
│       ├── classement.html     # Classements + statistiques
│       ├── equipes.html        # Vue des équipes
│       └── gestion.html        # Administration (gestionnaires)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 🚀 Démarrage rapide

### 1. Cloner et configurer

```bash
git clone <repo>
cd defisante
cp .env.example .env
# Modifier .env selon vos besoins
```

### 2. Lancer avec Docker Compose

```bash
docker-compose up --build
```


### 2. Compte administrateur par défaut

Créé automatiquement au premier démarrage :
- **Courriel** : `admin@defisante.local`
- **Mot de passe** : `Admin123!`

---

## 📡 API REST — Endpoints

### Authentification
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/api/auth/inscription` | Créer un compte |
| POST | `/api/auth/connexion` | Se connecter (retourne JWT) |
| GET | `/api/auth/moi` | Mon profil |
| PUT | `/api/auth/moi` | Modifier mon profil |

### Participants (gestionnaire requis pour liste/suppression)
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/participants/` | Liste tous les participants |
| GET | `/api/participants/<id>` | Détails d'un participant |
| PUT | `/api/participants/<id>` | Modifier |
| DELETE | `/api/participants/<id>` | Supprimer |

### Équipes
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/equipes/` | Liste des équipes (avec membres) |
| POST | `/api/equipes/` | Créer une équipe |
| PUT | `/api/equipes/<id>` | Modifier |
| DELETE | `/api/equipes/<id>` | Supprimer |
| POST | `/api/equipes/<id>/membres` | Ajouter un membre |
| DELETE | `/api/equipes/<id>/membres/<pid>` | Retirer un membre |

### Activités
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/activites/?q=search` | Liste (172 activités) |
| POST | `/api/activites/` | Créer une activité |
| PUT | `/api/activites/<id>` | Modifier |
| DELETE | `/api/activites/<id>` | Supprimer |

### Défis
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/defis/` | Liste des défis |
| GET | `/api/defis/actif` | Défi actuellement actif |
| POST | `/api/defis/` | Créer un défi |
| POST | `/api/defis/<id>/inscrire` | S'inscrire à un défi |
| GET | `/api/defis/<id>/participants` | Participants d'un défi |

### Saisies
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/saisies/` | Mes saisies |
| POST | `/api/saisies/` | Enregistrer une activité |
| DELETE | `/api/saisies/<id>` | Supprimer une saisie |
| POST | `/api/saisies/preview` | Calculer points sans sauvegarder |

### Statistiques
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/stats/classement/participants` | Classement individuel |
| GET | `/api/stats/classement/equipes` | Classement par équipes |
| GET | `/api/stats/activites/populaires` | Activités les plus pratiquées |
| GET | `/api/stats/repartition/sexe` | Répartition par sexe |
| GET | `/api/stats/resume` | Résumé global |

> Tous les endpoints stats acceptent `?id_defi=<id>` pour filtrer par défi.

---

## 🔐 Sécurité

- Authentification par **JWT** (Bearer token)
- Mots de passe hashés avec **bcrypt**
- Deux rôles : `participant` et `gestionnaire`
- CORS configuré (à restreindre en production)

---

## 📊 Calcul des points

```
Points = Points_base × (Durée_minutes ÷ 30) × Multiplicateur_intensité

Multiplicateurs :
  🔵 Faible  : × 0.75
  🟡 Moyenne : × 1.00
  🔴 Intense : × 1.25
```

Les points de base varient selon :
- Le **type d'activité** (table de pondération)
- Le **sexe** du participant (points Homme / Femme / Mixte)

---

## Tests de requête

Voici quelques requêtes en utilisant `curl`, des commandes Powershell et l'application [httpie](https://httpie.io/).

Voici un exemple de *token* d'authentification.

```powershell
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3NjM3MjQ0OCwianRpIjoiMTZhODZjMjUtN2UzZS00ODBjLTg1NWQtYzk5YzM1MmEzZGViIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NzYzNzI0NDgsImNzcmYiOiI5NDU1ZTEzZi05NDViLTQxYjAtYjgxMS02Y2E5ZDdlNzUzOGEifQ.B-a-Fnim0Z3Xik36cSIKgeKCwOEEA3d30tIvkZ_9qeo"
```

### Connexion

```powershell
$resp = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/connexion" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"courriel":"admin@defisante.local","mot_de_passe":"Admin123!"}'
$token = $resp.token
```

```bash
# Génère une erreur de connexion (normal)
http POST http://localhost:5000/api/auth/connexion courriel="test" mot_de_passe="test"

# Connexion avec succès
http POST http://localhost:5000/api/auth/connexion courriel="admin@defisante.local" mot_de_passe="Admin123!""

# Obtenir les informations du profil
http http://localhost:5000/api/auth/moi Authorization:"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3NjM3MjQ0OCwianRpIjoiMTZhODZjMjUtN2UzZS00ODBjLTg1NWQtYzk5YzM1MmEzZGViIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NzYzNzI0NDgsImNzcmYiOiI5NDU1ZTEzZi05NDViLTQxYjAtYjgxMS02Y2E5ZDdlNzUzOGEifQ.B-a-Fnim0Z3Xik36cSIKgeKCwOEEA3d30tIvkZ_9qeo"
```

### Inscription

```bash
# Inscription incomplète
http POST http://localhost:5000/api/auth/inscription courriel="admin@defisante.local" mot_de_passe="Admin123!""

# Inscription complète
http POST http://localhost:5000/api/auth/inscription prenom=test nom=test sexe=homme courriel="admin@defisante.local2" mot_de_passe="Admin123!"

```

### Défi actif

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/defis/actif" `
  -Headers @{ Authorization = "Bearer $token" }
```

### Classement (défi 1)

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/stats/classement/participants?id_defi=1" `
  -Headers @{ Authorization = "Bearer $token" }
```

### Mes saisies

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/saisies/" `
  -Headers @{ Authorization = "Bearer $token" }
```

```bash
# Liste des activités saisies
http -F http://localhost:5000/api/saisies Authorization:"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3NjM3MjQ0OCwianRpIjoiMTZhODZjMjUtN2UzZS00ODBjLTg1NWQtYzk5YzM1MmEzZGViIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NzYzNzI0NDgsImNzcmYiOiI5NDU1ZTEzZi05NDViLTQxYjAtYjgxMS02Y2E5ZDdlNzUzOGEifQ.B-a-Fnim0Z3Xik36cSIKgeKCwOEEA3d30tIvkZ_9qeo"
```

### Mes défis

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/auth/moi/defis" `
  -Headers @{ Authorization = "Bearer $token" }
```

Exécution des scripts de démo — Défi Santé 2026
Prérequis

Docker et Docker Compose installés
Le projet lancé (docker-compose up --build)


1. seed_admin.py — Créer le compte administrateur
À exécuter une seule fois après le premier démarrage pour initialiser le compte gestionnaire par défaut.
bashdocker exec defisante_api python seed_admin.py
Compte créé :
ChampValeurCourrieladmin@defisante.localMot de passeAdmin123!RôleGestionnaire

⚠️ Si le compte existe déjà, le script l'indique et ne fait rien.


2. seed_demo.py — Remplir la base avec des données fictives
Peuple la base de données avec un jeu de données complet pour tester l'application.
bashdocker exec defisante_api python seed_demo.py
Ce que le script crée :

3 équipes (Les Cheetahs, Les Ours Polaires, Les Aigles)
10 participants dont 1 gestionnaire (alice@demo.com)
2 défis (un passé, un en cours)
~60 saisies d'activités réparties sur les dernières semaines

Mot de passe de tous les comptes demo : Demo123!

Ordre recommandé
bash# 1. Démarrer l'application
docker-compose up --build -d

# 2. Créer le compte admin (une seule fois)
docker exec defisante_api python seed_admin.py

# 3. Charger les données de démo
docker exec defisante_api python seed_demo.py
L'interface est ensuite accessible sur http://localhost:5000 et Adminer (gestion BDD) sur http://localhost:8888.
