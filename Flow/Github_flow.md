Voici un **workflow adapté pour une équipe composée de 2 étudiants et 1 professeur**, où **le professeur agit comme réviseur principal et approuve les Pull Requests** sur **GitHub**. Le modèle reste basé sur le **GitHub Flow**, mais avec un contrôle pédagogique.

------

# Workflow Git pour 2 étudiants + 1 professeur

## Rôles

| Rôle       | Responsabilité                               |
| ---------- | -------------------------------------------- |
| Étudiant 1 | développe des fonctionnalités                |
| Étudiant 2 | développe d'autres fonctionnalités           |
| Professeur | révise le code et approuve les Pull Requests |

Les étudiants **ne fusionnent pas directement dans `main`**.
Seul le professeur approuve et autorise la fusion.

------

# 1. Création du dépôt

Le professeur crée le dépôt sur GitHub et ajoute les étudiants comme **collaborateurs**.

Structure recommandée :

```
projet/
│
├── README.md
├── src/
├── docs/
└── .gitignore
```

Les étudiants récupèrent le dépôt :

```bash
git clone https://github.com/cours/projet.git
cd projet
```

------

# 2. Organisation des branches

La branche principale :

```
main
```

Chaque étudiant crée une branche pour son travail :

```
feature-interface
feature-database
```

Créer une branche :

```bash
git checkout -b feature-interface
```

------

# 3. Développement

Chaque étudiant travaille localement.

Cycle typique :

```bash
git add .
git commit -m "Ajout interface utilisateur"
```

Bonnes pratiques :

- commits fréquents
- messages clairs
- petites modifications

------

# 4. Envoyer les modifications

Quand une fonctionnalité est prête :

```bash
git push origin feature-interface
```

La branche apparaît sur GitHub.

------

# 5. Création d’une Pull Request

L’étudiant crée une Pull Request :

```
feature-interface → main
```

La Pull Request doit inclure :

- description du changement
- fichiers modifiés
- explication de la fonctionnalité

------

# 6. Révision par le professeur

Le professeur :

- lit les modifications
- commente le code
- demande des corrections si nécessaire
- approuve la Pull Request

Les étudiants peuvent devoir corriger :

```bash
git add .
git commit -m "Correction demandée dans la review"
git push
```

La Pull Request est mise à jour automatiquement.

------

# 7. Fusion

Après approbation :

Le professeur fusionne la Pull Request dans `main`.

------

# 8. Mise à jour des étudiants

Les étudiants récupèrent les nouvelles modifications :

```bash
git checkout main
git pull
```

Puis mettent leur branche à jour :

```bash
git checkout feature-database
git merge main
```

------

# Exemple concret

| Personne   | Branche           | Travail             |
| ---------- | ----------------- | ------------------- |
| Étudiant 1 | feature-interface | interface           |
| Étudiant 2 | feature-database  | base de données     |
| Professeur | main              | validation et merge |

------

# Diagramme du workflow

```
main
 │
 ├── feature-interface (étudiant 1)
 │        │
 │        └── Pull Request → prof → merge
 │
 └── feature-database (étudiant 2)
          │
          └── Pull Request → prof → merge
```

------

# Règles importantes

### 1. Les étudiants ne modifient jamais `main` directement

Toujours travailler dans une branche :

```
feature-...
```

------

### 2. Une fonctionnalité = une branche

Exemple :

```
feature-login
feature-api
fix-bug-affichage
```

------

### 3. Toujours mettre à jour `main`

Avant de commencer :

```bash
git checkout main
git pull
```

------

# Avantages pédagogiques

Ce modèle permet aux étudiants de pratiquer :

- collaboration avec Git
- gestion des branches
- Pull Requests
- code review

Et permet au professeur de :

- **contrôler la qualité du code**
- **voir l’historique du travail**
- **commenter directement dans le code**

------

✅ Si vous voulez, je peux aussi vous fournir :

- **un guide GitHub de 1 page pour étudiants (workflow + commandes)**
- **un exercice de laboratoire GitHub (45 min)**
- **un schéma visuel très clair du workflow Git pour projeter en classe**.