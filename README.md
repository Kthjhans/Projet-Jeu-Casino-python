#  PyCasino : The Number Guessing Game

Un mini-jeu de casino interactif en ligne de commande (CLI) développé en Python. Le joueur doit deviner un nombre aléatoire généré par l'ordinateur à travers 3 niveaux de difficulté croissante. Le jeu intègre un système de mise, un chronomètre pour chaque essai, et une sauvegarde cloud des scores permettant de conserver son historique et de participer au classement général.

---

##  Fonctionnalités Principales

*   **Jeu de devinette à 3 niveaux** : Le joueur a un nombre d'essais limités (chronométrés à 10s) pour trouver le nombre caché, avec des gains qui s'adaptent selon sa rapidité.
*   **Système de Profil & Sauvegarde** : Le joueur est reconnu par son pseudo, permettant de conserver son solde entre les parties.
*   **Base de Données Cloud** : Toutes les parties (mises, gains, statistiques) sont sauvegardées de manière sécurisée via **MongoDB**.
*   **Leaderboard Intégré** : Affichage d'un classement (Top 5) des meilleurs joueurs à la fin de chaque partie.
*   **Interface Colorée** : Utilisation du package `colorama` pour une expérience de jeu agréable dans le terminal.

---

##  Prérequis et Architecture

Le projet est construit en utilisant **Python 3** et utilise **`uv`**, un gestionnaire de paquets ultra-rapide, pour gérer ses dépendances.

*   `main.py` : Contient la logique du jeu, la boucle principale, et la gestion du chronomètre via des threads.
*   `bd.py` : Gère la connexion et les requêtes vers la base de données MongoDB (Atlas).
*   `pyproject.toml` : Fichier de configuration du projet.

**Dépendances clés :**
*   `pymongo` (pour MongoDB)
*   `colorama` (pour l'affichage en couleurs)

---

##  Installation & Démarrage

### 1. Cloner ou télécharger le projet
Puis ouvrez un terminal dans le dossier du projet :
```powershell
cd /chemin/vers/casino-Project
```

### 2. Installer `uv` (si ce n'est pas déjà fait)
Si vous n'avez pas encore `uv` (Gestionnaire de paquets Python par Astral) :
```powershell
pip install uv
```

### 3. Installer les dépendances
Synchronisez votre environnement pour installer `pymongo` et `colorama` :
```powershell
uv sync
```
*(Si besoin, vous pouvez aussi les installer manuellement avec `uv add pymongo colorama`)*

### 4. Lancer le jeu
Lancez directement le projet via `uv` :
```powershell
uv run python main.py
```

---

##  Comment y jouer ?

1. Au lancement, choisissez `1` pour vous connecter avec un pseudo.
2. Vos statistiques commenceront (ou seront récupérées si vous avez déjà joué). Vous commencez avec 10€.
3. Regardez les règles si c'est votre première fois : vous devez deviner un nombre, en un certain nombre d'essais pour chaque niveau.
4. **Attention au temps !** Vous n'avez que **10 secondes** par essai, au-delà, l'essai est perdu.
5. Vos gains varient selon la vitesse à laquelle vous trouvez la réponse (1er coup = double de la mise, 2e = égal à la mise, etc.).
6. Une fois le jeu terminé (ou solde vide), vos statistiques s'affichent et la partie est sauvegardée en ligne dans le classement.

Amusez-vous bien ! 