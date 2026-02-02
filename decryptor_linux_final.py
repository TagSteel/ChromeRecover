import sqlite3
import os
import binascii
from Crypto.Cipher import AES
from dotenv import load_dotenv

# Chargement des variables depuis le fichier .env
load_dotenv()

# ==============================================================================
# La clé est maintenant récupérée depuis le fichier .env
# Assurez-vous d'avoir une ligne : MASTER_KEY_HEX=votre_cle dans le fichier .env
# ==============================================================================
MASTER_KEY_HEX = os.getenv("MASTER_KEY_HEX")
# ==============================================================================

# Nom des fichiers
input_file = 'Login Data'
output_file = 'decryptedPasswords.txt'

def decrypt_password(encrypted_password, master_key):
    try:
        # Vérifier si c'est le format v10 ou v20
        # v20 est souvent lié à l'App-Bound Encryption, mais on tente le même algorithme
        if encrypted_password[:3] in (b'v10', b'v20'):
            iv = encrypted_password[3:15]
            payload = encrypted_password[15:]
            
            # Création du chiffrage AES-GCM
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            
            # Décryptage
            decrypted_pass = cipher.decrypt(payload[:-16])
            
            # Le tag est normalement vérifié ici mais on veut juste essayer de lire
            # cipher.verify(payload[-16:])
            
            return decrypted_pass.decode()
        else:
            # On retourne le début du blob pour voir ce que c'est si ce n'est pas supporté
            return f"Format non supporté (header: {encrypted_password[:3]})"
    except Exception as e:
        return f"Erreur décryptage: {e}"

def main():
    if not MASTER_KEY_HEX:
        print("ERREUR : La clé 'MASTER_KEY_HEX' est introuvable !")
        print("Vérifiez que vous avez bien créé le fichier '.env' et ajouté votre clé dedans.")
        print("Exemple de contenu du fichier .env :")
        print("MASTER_KEY_HEX=a1b2c3d4...")
        return

    # Conversion de la clé hexadécimale en bytes
    try:
        master_key = binascii.unhexlify(MASTER_KEY_HEX)
    except Exception as e:
        print(f"ERREUR : La clé semble invalide (n'est pas de l'hexadécimal valide). {e}")
        return

    if not os.path.exists(input_file):
        print(f"Erreur : Le fichier '{input_file}' n'a pas été trouvé dans le dossier courant.")
        return

    print(f"Lecture du fichier : {input_file}")
    f = open(output_file, 'w', encoding='utf-8')

    try:
        conn = sqlite3.connect(input_file)
        cursor = conn.cursor()

        # Récupération des données
        cursor.execute('SELECT origin_url, action_url, username_value, password_value FROM logins')

        count = 0
        for result in cursor.fetchall():
            origin_url = result[0]
            action_url = result[1]
            username = result[2]
            encrypted_password = result[3]
            
            site = origin_url if origin_url else action_url
            
            # Décryptage
            password = decrypt_password(encrypted_password, master_key)
            
            f.write(f"Site: {site}\n")
            f.write(f"Username: {username}\n")
            f.write(f"Password: {password}\n")
            f.write('-' * 50 + '\n')
            count += 1

        print(f"Décryptage terminé. {count} comptes traités.")
        print(f"Résultats sauvegardés dans '{output_file}'.")

    except sqlite3.Error as e:
        print(f"Erreur SQLite : {e}")

    finally:
        if 'conn' in locals():
            conn.close()
        f.close()

if __name__ == "__main__":
    main()
