# Lolprono

Bienvenu, lolprono est un projet de webapp de pronostic sur les matchs compétitifs du jeu League of Legends.

La motivation initiale de ce projet était de créer une application fiable de pronostic utilisable entre amis à la
manière d'un "mon petit prono".

L'application permet :
 - de s'inscrire en tant qu'utilisateur
 - de suivre différentes compétitions
 - d'ajouter/modifier ses pronostics jusqu'à l'heure de début du match/bo
 - de suivre le classement des compétitions suivies

## Installation
```git clone https://github.com/ask1a/lolprono.git```

```cd lolprono```

```pip install virtualenv```

```python -m virtualenv venv```

```source venv/bin/activate```

```pip install -r requirements.txt```

## Créer les variables d'env necessaires
Windows:

```$Env:FLASK_APP = "project"```

```$Env:FLASK_DEBUG = 1```

Linux:

```export FLASK_APP="project"```

```export FLASK_DEBUG=1```

## Lancer l'application

```flask run```

puis ouvrir dans un navigateur l'url:
http://127.0.0.1:5000/index