http://localhost:5000

Récupérer le token ==== f12 ==== Application ==== ds_token ==== Prendre le token*

Insérer le token : 

$headers = @{
    Authorization = "Bearer TOKEN_ICI"
}

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/moi" -Headers $headers


Devrait sortir : 

courriel         : mathisthedark@gmail.com
date_inscription : 2026-04-09
equipe_nom       : 
id_equipe        : 
id_participant   : 2
nom              : DUVIVÉ
prenom           : Mathis
role             : participant
sexe             : homme
