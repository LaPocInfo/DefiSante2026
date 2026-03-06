# Laboratoire : Collaboration avec GitHub

## Objectif

Apprendre à collaborer avec GitHub en utilisant :

- branches
- commits
- Pull Requests
- code review

------

# Contexte

Deux étudiants travaillent sur un petit projet Python contenant un programme simple.

Structure du projet :

```
projet/
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
git checkout -b feature-salutation
```

Étudiant 2 :

```
git checkout -b feature-calcul
```

------

# Étape 3 – Modifier le code

Étudiant 1 :

Ajouter dans `fonctions.py` :

```
def saluer(nom):
    return "Bonjour " + nom
```

Étudiant 2 :

Ajouter :

```
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
git push origin feature-salutation
git push origin feature-calcul
```

------

# Étape 6 – Pull Request

Chaque étudiant :

1. ouvre GitHub
2. crée une **Pull Request vers main**

------

# Étape 7 – Révision par le professeur

Le professeur :

- vérifie le code
- ajoute un commentaire
- approuve la Pull Request

------

# Étape 8 – Fusion

Le professeur fusionne la Pull Request dans `main`.

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

```
def saluer(nom):
    return "Bonjour " + nom

def carre(nombre):
    return nombre * nombre
```

------

# Questions de réflexion

1. Pourquoi utilise-t-on des branches ?
2. À quoi sert une Pull Request ?
3. Pourquoi est-il utile de faire des commits fréquents ?
4. Quels problèmes pourraient arriver si deux personnes modifient le même fichier ?