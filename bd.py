

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

uri = "mongodb+srv://hans:x7a1SMmlZhv4Lq6V@cluster0.gnbr9pu.mongodb.net/?appName=Cluster0"

# Create a new client and connect to the server (lazy connection)
client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
db = client["casino"]

# Ping will be done only when saving data
def test_connection():
    try:
        client.admin.command('ping')
        print("✓ Connexion MongoDB réussie !")
        return True
    except Exception as e:
        print(f"✗ Erreur de connexion MongoDB : {e}")
        return False




def save_party(party_data):
    """Enregistre une partie dans la base de données."""
    try:
        # Test connection before saving
        if not test_connection():
            return False
        
        db = client.get_database("casino")
        parties = db.parties
        party_data["date"] = datetime.now()  # ajoute la date
        parties.insert_one(party_data)
        print("✓ Partie sauvegardée dans la base de données.")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de la sauvegarde : {e}")
        return False

def get_all_parties():
    """Récupère toutes les parties."""
    try:
        if not test_connection():
            return []
        db = client.get_database("casino")
        return list(db.parties.find().sort("date", -1))
    except Exception as e:
        print(f"✗ Erreur lors de la récupération : {e}")
        return []

def get_player_history(name):
    """Récupère l'historique des parties d'un joueur par son pseudo."""
    try:
        if not test_connection():
            return []
        db = client.get_database("casino")
        return list(db.parties.find({"name_user": name}).sort("date", -1))
    except Exception as e:
        print(f"✗ Erreur lors de la récupération de l'historique : {e}")
        return []

def get_top_scores(limit=5):
    """Récupère les meilleurs scores (solde_final) de tous les joueurs."""
    try:
        if not test_connection():
            return []
        db = client.get_database("casino")
        return list(db.parties.find({"solde_final": {"$exists": True}}).sort("solde_final", -1).limit(limit))
    except Exception as e:
        print(f"✗ Erreur lors de la récupération des meilleurs scores : {e}")
        return []