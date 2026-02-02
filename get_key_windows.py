import os
import json
import base64
import sys

# Ce script DOIT être lancé sur Windows pour récupérer la clé
try:
    import win32crypt
except ImportError:
    print("Erreur : Ce script a besoin du module 'pypiwin32'.")
    print("Installez-le sur votre PC avec : pip install pypiwin32")
    sys.exit(1)

def get_master_key():
    # Chemin vers le fichier 'Local State' de Chrome où la clé est stockée
    local_state_path = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Local State"
    
    if not os.path.exists(local_state_path):
        print(f"Erreur : Impossible de trouver le fichier Local State ici : {local_state_path}")
        return None

    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    # La clé est encryptée en base64 dans le JSON
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    
    # On retire les 5 premiers octets qui sont 'DPAPI'
    encrypted_key = encrypted_key[5:]
    
    # On utilise l'API Windows pour décrypter cette clé
    master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return master_key

if __name__ == "__main__":
    print("Tentative de récupération de la clé de chiffrement Chrome...")
    key = get_master_key()
    
    if key:
        print("\n" + "="*50)
        print("SUCCÈS ! VOICI VOTRE CLÉ (en hexadécimal) :")
        print("\n" + key.hex())
        print("\n" + "="*50)
        print("Copiez cette chaîne de caractères (chiffres et lettres) et donnez-la à l'agent.")
    else:
        print("Échec de la récupération de la clé.")
    
    input("\nAppuyez sur Entrée pour fermer la fenêtre...")
