import sqlite3
import os

input_file = 'Login Data'

if not os.path.exists(input_file):
    print(f"Fichier {input_file} introuvable.")
    exit()

conn = sqlite3.connect(input_file)
cursor = conn.cursor()

cursor.execute('SELECT origin_url, password_value FROM logins LIMIT 5')

print("--- Analyse des 5 premiers mots de passe ---")
for result in cursor.fetchall():
    url = result[0]
    blob = result[1]
    
    print(f"\nSite: {url}")
    print(f"Taille du blob: {len(blob)} octets")
    
    if len(blob) > 0:
        # Affiche les 10 premiers octets en hexadécimal
        prefix = blob[:10]
        print(f"Début (HEX): {prefix.hex()}")
        print(f"Début (ASCII): {prefix}")
        
        if blob.startswith(b'v10'):
            print("=> Format: v10 (Récent, devrait fonctionner avec la clé)")
        else:
            print("=> Format: INCONNU ou ANCIEN (DPAPI)")
    else:
        print("=> Blob vide !")

conn.close()
