# Laboratoire : Collaboration avec GitHub

## Objectif

Apprendre à collaborer avec GitHub en utilisant :

- branches
- commits
- *Pull Requests*
- *code review*

------

# Contexte

Deux étudiants travaillent sur un petit projet Python contenant un programme simple.

Structure du projet :

```
/api/
│
├── main.py
├── README.md
└── fonctions.py
```

------

# Étape 1 – Cloner le projet

Chaque étudiant clone le dépôt :

```
git clone URL_DU_DEPOT
cd projet
```

------

# Étape 2 – Créer une branche

Étudiant 1 :

```
git checkout -b salutation-test-1-api
```

Étudiant 2 :

```
git checkout -b calcul-test-2-api
```

------

# Étape 3 – Modifier le code

Étudiant 1 :

Ajouter dans `fonctions.py` :

```python
def saluer(nom):
    return "Bonjour " + nom
```

Étudiant 2 :

Ajouter :

```python
def carre(nombre):
    return nombre * nombre
```

------

# Étape 4 – Commit

```
git add .
git commit -m "Ajout fonction saluer"
```

ou

```
git commit -m "Ajout fonction carre"
```

------

# Étape 5 – Push

```
git push origin salutation-test-1-api
git push origin calcul-test-2-api
```

------

# Étape 6 – *Pull Request*

Chaque étudiant :

1. ouvre GitHub
2. crée une ***Pull Request* vers main**

------

# Étape 7 – Révision par le professeur

Le professeur :

- vérifie le code
- ajoute un commentaire
- approuve la Pull Request

------

# Étape 8 – Fusion

Le professeur fusionne la *Pull Request* dans `main`.

------

# Étape 9 – Mise à jour

Les étudiants exécutent :

```
git checkout main
git pull
```

------

# Résultat attendu

Le fichier `fonctions.py` contient :

```python
def saluer(nom):
    return "Bonjour " + nom

def carre(nombre):
    return nombre * nombre
```
