import sqlite3
import os
import json
import base64
import sys
import binascii
from pathlib import Path

try:
    import win32crypt
    from win32com.client import Dispatch
except ImportError:
    print("ERREUR : Ce script nécessite pywin32 et pywin32com")
    print("Installez avec : pip install pypiwin32")
    sys.exit(1)

try:
    from Crypto.Cipher import AES
except ImportError:
    print("ERREUR : Ce script nécessite pycryptodome")
    print("Installez avec : pip install pycryptodome")
    sys.exit(1)

def get_master_key():
    """Récupère la clé maître depuis Local State"""
    try:
        local_state_path = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Local State"
        
        if not os.path.exists(local_state_path):
            print(f"Local State introuvable : {local_state_path}")
            return None

        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())

        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Retire 'DPAPI'
        
        master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return master_key
    except Exception as e:
        print(f"Erreur lors de la récupération de la clé maître : {e}")
        return None

def decrypt_password_v10(encrypted_password, master_key):
    """Décryptage v10 standard"""
    try:
        iv = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload[:-16])
        return decrypted_pass.decode('utf-8')
    except Exception as e:
        return f"<Erreur v10: {e}>"

def decrypt_password_v20_elevation(encrypted_password):
    """Tentative de décryptage v20 via Elevation Service COM"""
    try:
        # Tentative d'accès au service d'élévation Chrome
        # CLSID du service (peut varier selon les versions)
        # {708860E0-F641-4611-8895-7D867DD3675B} est un exemple
        
        # Note: Cette approche nécessite que Chrome soit installé et que le service soit actif
        elevation_service = Dispatch("Elevation.ElevationService")
        
        # Appel de la méthode de décryptage
        # L'interface exacte dépend de la version de Chrome
        decrypted = elevation_service.DecryptData(encrypted_password)
        return decrypted
    except Exception as e:
        return f"<Service d'élévation non accessible: {e}>"

def decrypt_password_v20_fallback(encrypted_password, master_key):
    """Tentative de décryptage v20 comme v10 (peut échouer)"""
    try:
        # Structure similaire à v10 mais peut avoir une couche supplémentaire
        iv = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload[:-16])
        
        # Tentative de décodage
        return decrypted_pass.decode('utf-8')
    except Exception as e:
        return f"<Erreur v20: {e}>"

def main():
    print("=" * 60)
    print("DÉCRYPTEUR CHROME AVEC SUPPORT APP-BOUND ENCRYPTION (v20)")
    print("=" * 60)
    print()
    
    # Récupération de la clé maître
    print("[1/4] Récupération de la clé maître...")
    master_key = get_master_key()
    if not master_key:
        print("ÉCHEC : Impossible de récupérer la clé maître.")
        input("Appuyez sur Entrée pour quitter...")
        return
    print(f"✓ Clé maître récupérée ({len(master_key)} octets)")
    print()
    
    # Localisation du fichier Login Data
    print("[2/4] Localisation du fichier Login Data...")
    login_data_path = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Default\Login Data"
    
    # Copie du fichier car Chrome peut le verrouiller
    import shutil
    temp_db = "Login_Data_Copy.db"
    
    try:
        shutil.copy2(login_data_path, temp_db)
        print(f"✓ Fichier copié : {temp_db}")
    except Exception as e:
        print(f"ERREUR : Impossible de copier le fichier : {e}")
        print("Assurez-vous que Chrome est fermé.")
        input("Appuyez sur Entrée pour quitter...")
        return
    print()
    
    # Lecture de la base de données
    print("[3/4] Lecture de la base de données...")
    output_file = "passwords_decrypted_windows.txt"
    
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute('SELECT origin_url, action_url, username_value, password_value FROM logins')
        
        results = cursor.fetchall()
        print(f"✓ {len(results)} entrées trouvées")
        print()
        
        # Décryptage
        print("[4/4] Décryptage des mots de passe...")
        with open(output_file, 'w', encoding='utf-8') as f:
            success_count = 0
            v10_count = 0
            v20_count = 0
            empty_count = 0
            error_count = 0
            
            for result in results:
                origin_url = result[0]
                action_url = result[1]
                username = result[2]
                encrypted_password = result[3]
                
                site = origin_url if origin_url else action_url
                
                if not encrypted_password or len(encrypted_password) == 0:
                    password = "<Vide>"
                    empty_count += 1
                elif encrypted_password[:3] == b'v10':
                    password = decrypt_password_v10(encrypted_password, master_key)
                    v10_count += 1
                    if not password.startswith("<Erreur"):
                        success_count += 1
                elif encrypted_password[:3] == b'v20':
                    # Tentative 1 : Service d'élévation
                    password = decrypt_password_v20_elevation(encrypted_password)
                    
                    # Si échec, tentative 2 : méthode fallback
                    if password.startswith("<Service"):
                        password = decrypt_password_v20_fallback(encrypted_password, master_key)
                    
                    v20_count += 1
                    if not password.startswith("<"):
                        success_count += 1
                else:
                    password = f"<Format inconnu: {encrypted_password[:3]}>"
                    error_count += 1
                
                f.write(f"Site: {site}\n")
                f.write(f"Username: {username}\n")
                f.write(f"Password: {password}\n")
                f.write("-" * 50 + "\n")
        
        conn.close()
        
        print()
        print("=" * 60)
        print("RÉSULTAT DU DÉCRYPTAGE")
        print("=" * 60)
        print(f"Total d'entrées     : {len(results)}")
        print(f"Mots de passe vides : {empty_count}")
        print(f"Format v10 (ancien) : {v10_count}")
        print(f"Format v20 (App-Bound): {v20_count}")
        print(f"Formats inconnus    : {error_count}")
        print(f"Décryptés avec succès: {success_count}")
        print()
        print(f"Résultats sauvegardés dans : {output_file}")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERREUR : {e}")
    finally:
        # Nettoyage
        if os.path.exists(temp_db):
            os.remove(temp_db)
    
    input("\nAppuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main()
