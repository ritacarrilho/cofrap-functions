# COFRAP
Application Python pour COFRAP (Comité de Formation Professionnel) pour les fonctions Serverless.

## Prérequis
Ce projet nécessite Python 3.7 ou supérieur.

### **Dépendances** :
```
pip install -r requirements.txt
```
```
pip install -r requirements.txt
```
## Lancer le projet
```python XXXXX.py```

## Structure du projet

```
├── .github/
│   └── workflows/
│       └── main.yml                # Fichier de workflow GitHub Actions
├── authenticate-user/              # Dossier pour la fonction d'authentification
├── docs/                           # Documentation technique générée
├── faas-db-cofrap/                 # Fonction liée à la base de données Cofrap
├── generate-2fa/                   # Fonction pour générer une authentification à deux facteurs
├── generate-password/              # Fonction de génération de mot de passe
├── get-users/                      # Fonction pour récupérer les utilisateurs
├── sql/                            # Scripts SQL ou configuration base de données
├── test/                           # Tests unitaires ou d’intégration
├── .gitignore                      # Fichiers/dossiers ignorés par Git
├── README.md                       # Documentation principale du projet
├── faas-db-cofrap.yml              # Définition de la fonction faas-db-cofrap
├── stack.yaml                      # Définition de la stack OpenFaaS (ou similaire)
├── test.py                         # Script de test (authentification ici)
├── version.json                    # Fichier de versionnage du projet
```
## Tests
...
 
