"""Jeu de casino simple en un seul fichier.

Organisation :
- Plusieurs fonctions couvrent chaque bloc de logique (accueil, règles, mise,
  niveau, devinette, statistiques, etc.).
- Toutes les fonctions sont définies en haut du fichier et appelées depuis
  la fonction `main` en bas.
- Le script reste monolithique : pas de modules externes, tout est dans ce
  fichier comme demandé.

Chaque variable importante (name_user, nb_python, nb_user, nb_coup, level,
mise, dotation, gain, solde, etc.) est gérée dans son propre code et/ou
stockée dans le dictionnaire de statistiques.
"""
from bd import save_party, get_player_history, get_top_scores
import random
import threading
import time
import sys
import os
from colorama import init, Fore, Style

# Initialiser colorama pour que les couleurs s'affichent bien sous Windows
init()

def clear_console():
    """Efface le contenu de la console pour un rendu plus propre."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Couleurs pour faciliter l'affichage
C_INFO = Fore.CYAN + Style.BRIGHT
C_SUCCESS = Fore.GREEN + Style.BRIGHT
C_WARNING = Fore.YELLOW + Style.BRIGHT
C_ERROR = Fore.RED + Style.BRIGHT
C_RESET = Style.RESET_ALL

# helper for slow output

def slow_print(lines, delay=0.5):
    """Imprime chaque ligne de la liste `lines` avec une pause de `delay` secondes."""
    for l in lines:
        print(l)
        time.sleep(delay)


# --- utilitaire de saisie temporisée --------------------------------------
def timed_input(prompt, timeout=10):
    """Demande une saisie à l'utilisateur pendant `timeout` secondes.
    Retourne la chaîne saisie ou None si le délai est dépassé.  Cette
    implémentation utilise un thread pour ne pas bloquer le programme.
    """
    result = [None]

    def worker():
        try:
            result[0] = input(prompt)
        except Exception:
            pass

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        return None
    return result[0]

# --- fonctions de dialogue -------------------------------------------------

def get_user_name():
    """Demande et retourne le pseudo du joueur."""
    name = input(f"{C_INFO}Je suis le Croupier. Quel est votre pseudo ? {C_RESET}")
    return name.strip() or "Joueur"


def ask_show_rules():
    """Propose d'afficher les règles ; renvoie True si oui."""
    while True:
        resp = input(f"{C_INFO}Voulez-vous voir les règles du jeu ? (O/N) {C_RESET}").strip().upper()
        if resp in ("O", "N"):
            return resp == "O"
        print(f"{C_WARNING}Je ne comprends pas votre réponse. Répondez par O ou N.{C_RESET}")


def display_rules():
    """Affiche les règles détaillées du jeu une ligne à la fois avec
    une petite pause pour que l'utilisateur puisse lire."""
    lines = [
        f"\n{C_WARNING}--- Règles du Casino ---{C_RESET}",
        "Le jeu comporte 3 niveaux. Le joueur commence au niveau 1 et peut",
        "choisir de monter de niveau seulement après avoir réussi le niveau",
        "courant. Chaque niveau fait deviner un nombre aléatoire entre :",
        f"  * {C_INFO}niveau 1 :{C_RESET} 1 à 10 (3 essais)",
        f"  * {C_INFO}niveau 2 :{C_RESET} 1 à 20 (5 essais)",
        f"  * {C_INFO}niveau 3 :{C_RESET} 1 à 30 (7 essais)",
        f"{C_WARNING}Attention :{C_RESET} Chaque essai doit être fait en moins de 10 secondes,",
        "sinon il est comptabilisé comme perdu.",
        "Les gains sont :",
        f"  * {C_SUCCESS}1er coup :{C_RESET} double de la mise",
        f"  * {C_SUCCESS}2ème coup :{C_RESET} égal à la mise",
        f"  * {C_SUCCESS}3ème coup :{C_RESET} demi-mise\n"
    ]
    for line in lines:
        print(line)
        time.sleep(0.5)



# --- gestion des statistiques --------------------------------------------

def init_stats():
    return {
        "niveaux_atteints": [],
        "gains": [],
        "mises": [],
        "coups": [],
        "premier_coup": 0,
    }


def show_stats(stats):
    print("\n" + "="*50)
    print("--- STATISTIQUES DÉTAILLÉES DE LA PARTIE ---")
    
    nb_parties = len(stats["niveaux_atteints"])
    
    if nb_parties == 0:
        print(" Aucun niveau réussi.")
    else:
        for i in range(nb_parties):
            niv = stats["niveaux_atteints"][i]
            mise = stats["mises"][i]
            gain = stats["gains"][i]
            coups = stats["coups"][i]
            print(f" Manche {i+1} | Niveau {niv} | Mise : {mise}€ | Tentatives : {coups} | Gain : {gain}€")
            
        print("-" * 50)
        print(f" Total des mises : {sum(stats['mises'])}€")
        print(f" Total des gains (bruts) : {sum(stats['gains'])}€")
        
    if stats["premier_coup"] > 0:
        print(f" Coups de maître (1er essai) : {stats['premier_coup']} fois !")
        
    print("="*50 + "\n")

# --- fonctions de jeu -----------------------------------------------------

def get_bet(solde):
    """Demande une mise valide entre 1 et solde inclus."""
    while True:
        saisie = input(f"{C_INFO}Entrez votre mise (1-{solde}) : {C_RESET}")
        try:
            mise = int(saisie)
        except ValueError:
            print(f"{C_ERROR}Montant non valide, entrez un entier.{C_RESET}")
            continue
        if 1 <= mise <= solde:
            return mise
        print(f"{C_ERROR}Erreur, votre mise doit être entre 1 et {solde}.{C_RESET}")


def play_level(level, solde, stats):
    """Joue un niveau, retourne (nouveau_solde, action)."""
    limites = {1: 10, 2: 20, 3: 30}
    essais_max = {1: 3, 2: 5, 3: 7}
    limite = limites[level]
    essais_restants = essais_max[level]

    print(f"\n* Level {level} : je pense à un nombre entre 1 et {limite}.")
    nb_python = random.randint(1, limite)
    mise = get_bet(solde)
    solde -= mise

    while essais_restants > 0:
        prompt = f"Entrez un nombre (il vous reste {essais_restants} essai(s)) : "
        nb_user_str = timed_input(prompt, timeout=10)
        if nb_user_str is None:
            print("Vous avez dépassé le délai de 10 secondes !")
            essais_restants -= 1
            continue
        try:
            nb_user = int(nb_user_str)
        except ValueError:
            print("Je ne comprends pas ! Entrez un nombre valide.")
            continue
        if nb_user > nb_python:
            print("Votre nbre est trop grand !")
        elif nb_user < nb_python:
            print("Votre nbre est trop petit !")
        else:
            coups_utilises = essais_max[level] - essais_restants + 1
            if coups_utilises == 1:
                gain = mise * 2
                stats["premier_coup"] += 1
            elif coups_utilises == 2:
                gain = mise
            else:
                gain = mise // 2
            solde += gain
            stats["gains"].append(gain)
            stats["mises"].append(mise)
            stats["coups"].append(coups_utilises)
            stats["niveaux_atteints"].append(level)
            print(f"Bingo ! Vous avez gagné en {coups_utilises} coup(s) et emporté {gain} € !")
            # niveau réussi
            if level < 3:
                while True:
                    rep = input("Souhaitez-vous continuer au niveau suivant ? (O/N) ").strip().upper()
                    if rep in ("O", "N"):
                        return (solde, "next_level" if rep == "O" else "stop")
                    print("Je ne comprends pas votre réponse.")
            return (solde, "stop")  # niveau 3 gagné, fin
        essais_restants -= 1
        if essais_restants == 1:
            print("Il vous reste une chance !")
    else:
        print(f"Vous avez perdu ! Mon nombre était {nb_python}.")
        # proposer de rejouer le même niveau ou quitter
        while True:
            rep = input("Souhaitez-vous retenter ce level ? (O/N) ").strip().upper()
            if rep in ("O", "N"):
                return (solde, "retry_level" if rep == "O" else "stop")
            print("Je ne comprends pas votre réponse.")

# --- fonction principale --------------------------------------------------

def display_welcome_menu():
    """Affiche le menu principal et retourne le choix de l'utilisateur."""
    clear_console()
    while True:
        print(f"\n{C_SUCCESS}{'='*40}")
        print(f"      🎰 BIENVENUE AU CASINO PYTHON 🎰")
        print(f"{'='*40}{C_RESET}")
        print(f"{C_INFO}1.{C_RESET} Jouer (Se connecter)")
        print(f"{C_INFO}2.{C_RESET} Quitter le jeu")
        print(f"{C_SUCCESS}{'-'*40}{C_RESET}")
        
        choix = input(f"{C_WARNING}Que voulez-vous faire (1 ou 2) ? {C_RESET}").strip()
        
        if choix in ("1", "2"):
            return choix
        print(f"{C_ERROR}Choix invalide. Veuillez entrer 1 ou 2.{C_RESET}")


def main():
    while True:
        choix_menu = display_welcome_menu()
        
        if choix_menu == "2":
            print(f"\n{C_INFO}Merci d'avoir visité le Casino Python. À bientôt ! 👋{C_RESET}\n")
            break
            
        # Si le joueur choisit 1 : On lance la boucle de jeu
        name = get_user_name()
        
        print(f"\n{C_INFO}Connexion à la base de données en cours pour récupérer votre historique...{C_RESET}")
        history = get_player_history(name)
        if history:
            print(f"\n{C_SUCCESS}Heureux de vous revoir {name} !{C_RESET} Vous avez déjà joué {len(history)} partie(s) ici.")
            last_score = history[0].get("solde_final", 10)
            print(f"Votre dernier solde final enregistré était de {C_SUCCESS}{last_score} €{C_RESET}.\n")
        else:
            print(f"\n{C_SUCCESS}Bienvenue pour votre toute première partie, {name} !{C_RESET}\n")

        solde = 10
        stats = init_stats()

        if ask_show_rules():
            clear_console()
            display_rules()


        continuer = True
        while continuer:
            level = 1
            solde = 10
            stats = init_stats()
            # boucle de niveaux tant que le joueur a des crédits
            while level <= 3 and solde > 0:
                clear_console()
                solde, action = play_level(level, solde, stats)
                if action == "next_level":
                    level += 1
                elif action == "retry_level":
                    pass  # reste au même niveau
                else:  # "stop"
                    break
            if solde <= 0:
                slow_print([
                    f"{C_ERROR}Désolé, vous n'avez plus de crédit.{C_RESET}",
                    f"{C_INFO}La partie va redémarrer avec 10 € de départ.{C_RESET}"
                ])
                time.sleep(2)
                continue  # recommence la partie depuis le début
            
            # sinon sortie normale
            clear_console()
            print(f"{C_SUCCESS}Au revoir {name}, vous finissez la partie avec {solde} €.{C_RESET}")
            # préparer les données de la partie et sauvegarder
            party_data = {
                "name_user": name,
                "niveaux_atteints": stats["niveaux_atteints"],
                "gains": stats["gains"],
                "mises": stats["mises"],
                "coups": stats["coups"],
                "premier_coup": stats["premier_coup"],
                "solde_final": solde
            }
            save_party(party_data)
            show_stats(stats)
            
            # Affichage du classement (Leaderboard)
            print("\n" + "="*50)
            print(f"{C_WARNING}--- CLASSEMENT DES MEILLEURS JOUEURS (TOP 5) ---{C_RESET}")
            tops = get_top_scores(5)
            if tops:
                for i, p in enumerate(tops):
                    p_name = p.get('name_user', 'Inconnu')
                    p_solde = p.get('solde_final', 0)
                    print(f" {i+1}. {C_INFO}{p_name}{C_RESET} - {C_SUCCESS}{p_solde} €{C_RESET}")
            else:
                print(" Aucun score enregistré pour le moment.")
            print("="*50 + "\n")
            
            # Après la fin de la partie du joueur, on sort de la boucle `continuer` 
            # pour retourner au menu principal (demander "1. Jouer" ou "2. Quitter")
            continuer = False


if __name__ == "__main__":
    main()
