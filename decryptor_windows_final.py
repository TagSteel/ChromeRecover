import sqlite3
import os
import sys

# IMPORTANT : Ce script DOIT être lancé sur Windows.
try:
    import win32crypt
except ImportError:
    print("ERREUR CRITIQUE: Ce script necessite Windows et le module 'pywin32'.")
    print("Installez-le avec : pip install pypiwin32")
    sys.exit(1)

# Nom des fichiers
input_file = 'Login Data'
output_file = 'decryptedPasswords_Windows.txt'

if not os.path.exists(input_file):
    print(f"Erreur : Le fichier '{input_file}' est introuvable.")
    print("Assurez-vous de copier le fichier 'Login Data' dans le meme dossier que ce script.")
    input("Appuyez sur Entree pour quitter...")
    sys.exit(1)

print(f"Lecture du fichier : {input_file}...")
f = open(output_file, 'w', encoding='utf-8')

try:
    conn = sqlite3.connect(input_file)
    cursor = conn.cursor()
    
    # On selectionne origin_url en priorite
    cursor.execute('SELECT origin_url, action_url, username_value, password_value FROM logins')

    count = 0
    for result in cursor.fetchall():
        origin_url = result[0]
        action_url = result[1]
        username = result[2]
        encrypted_password = result[3]
        
        site = origin_url if origin_url else action_url
        
        try:
            # TENTATIVE DE DECRYPTAGE WINDOWS (DPAPI)
            # Cette fonction appelle Windows pour demander : "Puis-je avoir la clé pour déchiffrer ceci ?"
            # Windows répondra OUI seulement si vous êtes l'utilisateur qui a créé ce fichier.
            decrypted_data = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
            password = decrypted_data.decode('utf-8') # tentative de lecture en texte
        except Exception as e:
            # Si cela echoue, cela peut etre du au nouveau format de chiffrement de Chrome (v80+)
            # qui necessite une cle AES supplementaire, ou parce que vous n'etes pas sur le bon user.
            password = f"<ECHEC DECRYPTAGE: {e}>"

        if password:
            f.write(f"Site: {site}\n")
            f.write(f"Username: {username}\n")
            f.write(f"Password: {password}\n")
            f.write("-" * 50 + "\n")
            count += 1

    print(f"Termine ! {count} entrees traitees.")
    print(f"Resultats dans : {output_file}")

except Exception as e:
    print(f"Une erreur est survenue : {e}")
finally:
    if 'conn' in locals():
        conn.close()
    f.close()
    input("Appuyez sur Entree pour quitter...")
