import sqlite3
import os

# Nom des fichiers (entrée et sortie) dans le dossier courant
input_file = 'Login Data'
output_file = 'decryptedPasswords.txt'

# Vérification de la présence du fichier source
if not os.path.exists(input_file):
    print(f"Erreur : Le fichier '{input_file}' n'a pas été trouvé dans le dossier courant.")
    exit()

print(f"Lecture du fichier : {input_file}")
f = open(output_file, 'w')

try:
    # Connexion à la base de données locale
    conn = sqlite3.connect(input_file)
    cursor = conn.cursor()

    # Récupération des données (origin_url est souvent plus pertinent que action_url)
    cursor.execute('SELECT origin_url, action_url, username_value, password_value FROM logins')

    for result in cursor.fetchall():
        try:
            # Sur Linux/Codespaces, nous ne pouvons pas utiliser l'API Windows DPAPI pour décrypter
            # Nous allons donc récupérer ce qui est visible (URL et Username)
            
            origin_url = result[0]
            action_url = result[1]
            username = result[2]
            encrypted_password = result[3]
            
            # On privilégie origin_url, sinon action_url
            site = origin_url if origin_url else action_url
            
            password = "NON_DECHIFFRABLE_SUR_LINUX_SANS_CLE"

            # Si on était sur Windows, on ferait :
            # password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
            
            f.write('Site: ' + str(site) + '\n')
            f.write('Username: ' + str(username) + '\n')
            f.write('Password (Status): ' + str(password) + '\n')
            f.write('-' * 50 + '\n')
        except Exception as e:
            # Ignorer les erreurs de décryptage ou les consigner
            pass

    print(f"Décryptage terminé. Résultats sauvegardés dans '{output_file}'.")

except sqlite3.Error as e:
    print(f"Erreur SQLite : {e}")

finally:
    if 'conn' in locals():
        conn.close()
    f.close()
