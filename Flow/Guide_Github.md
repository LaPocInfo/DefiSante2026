# Guide rapide GitHub pour travail en équipe

## 1. Cloner le projet

Récupérer le projet sur votre ordinateur :

```
git clone URL_DU_DEPOT
cd nom-du-projet
```

------

## 2. Mettre à jour le projet

Avant de commencer à travailler :

```
git checkout main
git pull
```

Cela récupère les dernières modifications.

------

## 3. Créer une branche

Ne jamais travailler directement dans `main`.

Créer une branche pour votre fonctionnalité :

```
git checkout -b feature-nom-fonctionnalite
```

Exemples :

```
feature-interface
feature-database
fix-bug-login
```

------

## 4. Modifier le code

Travaillez normalement dans vos fichiers.

Ensuite ajouter les modifications :

```
git add .
```

------

## 5. Faire un commit

Sauvegarder vos modifications dans Git :

```
git commit -m "Description claire de la modification"
```

Exemples :

```
git commit -m "Ajout fonction lecture fichier"
git commit -m "Correction bug affichage"
```

Bonnes pratiques :

- faire plusieurs petits commits
- écrire des messages clairs

------

## 6. Envoyer le travail sur GitHub

```
git push origin nom-de-branche
```

Exemple :

```
git push origin feature-interface
```

------

## 7. Créer une Pull Request

Sur GitHub :

1. ouvrir le dépôt
2. cliquer sur **Pull Requests**
3. cliquer sur **New Pull Request**
4. choisir :

```
feature-xxx → main
```

Ajouter :

- une description
- ce que vous avez modifié

------

## 8. Révision par le professeur

Le professeur :

- lit le code
- ajoute des commentaires
- demande des corrections si nécessaire
- approuve la Pull Request

------

## 9. Fusion du code

Après approbation :

La Pull Request est **fusionnée dans `main`**.

------

## 10. Mettre à jour votre projet

```
git checkout main
git pull
```

Puis mettre votre branche à jour :

```
git merge main
```

------

# Règles importantes

✔ Ne jamais modifier `main` directement
✔ Une branche par fonctionnalité
✔ Faire des commits fréquents
✔ Toujours faire une Pull Request

------

# Workflow résumé

```
git clone
git checkout -b feature-xxx
modifier le code
git add .
git commit
git push
Pull Request
review
merge
```