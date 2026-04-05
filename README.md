# CRM-minimal
CRM minimal

## Environnement
### Création de l'environnement virtuel
```sh
python3 -m venv venv
```

Un fichier ``.env doit être créé à la racine du projet afin d’y stocker la clé secrète utilisée pour la gestion des sessions :

```
SECRET_KEY="mettre_cle_secrete_ici"
```

### Activation de l'environnement virtuel
```sh
source venv/bin/activate
```

## Dépendances
Les dépendances du projet sont définies dans le fichier requirements.txt.

Pour les installer :

```sh
pip install -r requirements.txt
```


## Exécution du programme

En local, l'application s'exécute toujours en mode debug.

### Avec `make` (si installé) :
Lancer l'application :

```sh
make run
```

### Sans make
Lancer l'application en local :
```sh
python3 index.py
```
