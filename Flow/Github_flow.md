# Workflow Git proposé

## Rôles

| Rôle       | Responsabilité                                               |
| ---------- | ------------------------------------------------------------ |
| Étudiant 1 | développe des fonctionnalités                                |
| Étudiant 2 | développe d'autres fonctionnalités                           |
| Professeur | révise le code et approuve les *Pull Requests* chaque semaine |

Les étudiants **ne fusionnent pas directement dans `main`**.  Seul le professeur approuve et autorise la fusion.

------

## 1. Création du dépôt

Voir le dépôt sur GitHub https://github.com/LaPocInfo/DefiSante2026 et vous serez ajouté comme collaborateurs.

Structure recommandée pour le développement

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
git clone https://github.com/LaPocInfo/DefiSante2026
```

------

## 2. Organisation des branches

La branche principale :

```
main
```

Chaque étudiant crée une branche pour son travail, pour chaque fonctionnalité:

```
fonctionnalite-n-web
fonctionnalite-n-api
```

Chaque branche a son nom et son numéro `n`.  Par exemple, `depart-1-api` ou `bd_creationtables_1-api`

Pour créer une branche :

```bash
git checkout -b fonctionnalite-n-api
```

------

## 3. Développement

Chaque étudiant travaille localement.

Cycle typique :

```bash
git add .
git commit -m "Ajout interface utilisateur"
```

Bonnes pratiques :

- *commits* fréquents
- messages clairs
- petites modifications

------

## 4. Envoyer les modifications

Quand une fonctionnalité est prête :

```bash
git push origin fonctionnalite-n-api
```

La branche apparaît sur GitHub.

------

## 5. Création d’une *Pull Request*

L’étudiant crée une *Pull Request* :

```
fonctionnalite-n-web → main
```

La *Pull Request* doit inclure :

- description du changement
- fichiers modifiés
- explication de la fonctionnalité

Voici comment réaliser un *Pull Request*

1. Rendez‑vous sur la page du dépôt sur GitHub.
2. Vous verrez un bandeau « Compare & pull request ». Cliquez dessus, ou choisissez **Pull requests → New pull request**.
3. Sélectionnez votre branche comme *head* (source) et la branche cible du dépôt d’origine ( `main`).
4. Ajoutez un titre, une description détaillée, puis cliquez sur **Create pull request**.

Durant la semaine ou le plus vite posssible, je vais

- lire les modifications proposées dans les *Pull requests*
- commenter le code
- demander des corrections si nécessaire
- approuver la *Pull Request*

Les étudiants peuvent devoir corriger :

```bash
git add .
git commit -m "Correction demandée dans la review"
git push
```

La *Pull Request* est mise à jour automatiquement.

------

## 7. Fusion

Après approbation d'un *Pull request*, c'est le prof. qui fusionne dans `main`.

------

## 8. Mise à jour des étudiants

Les étudiants récupèrent les nouvelles modifications à chaque début de travail:

```bash
git checkout main
git pull
```

Puis mettent leurs branches de travail à jour :

```bash
git checkout fonctionnalite-n-web
git merge main
```

------

## Diagramme du workflow

```
main
 │
 ├── fonctionnalite-n-web (étudiant 1)
 │        │
 │        └── Pull Request → prof → merge
 │
 └── fonctionnalite-n-api (étudiant 2)
          │
          └── Pull Request → prof → merge
```

------

## Règles importantes

### 1. Les étudiants ne modifient jamais `main` directement

Toujours travailler dans une branche :

```
fonctionnalite-...
```

------

### 2. Une fonctionnalité = une branche

Exemple :

```
login-5-api
fonctionnalite-n-web
fix-bug-affichage-10-api
```

------

### 3. Toujours mettre à jour `main`

Avant de commencer :

```bash
git checkout main
git pull
```

------

## Avantages

Ce modèle permet de pratiquer :

- collaboration avec Git
- gestion des branches
- *Pull Requests*
- *code review*
