http://localhost:5000/api/activites/

[System.IO.File]::WriteAllText("body.json", '{"nom":"Yoga","description":"Cours de yoga","points_homme":10,"points_femme":12,"points_mixte":11}')

curl.exe -X POST http://localhost:5000/api/activites/ -H "Content-Type: application/json" -d "@body.json"
