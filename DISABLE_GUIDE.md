# GUIDE DE DÉSACTIVATION APP-BOUND ENCRYPTION

## MÉTHODE 1 : Script PowerShell Automatique (RECOMMANDÉ)

### Prérequis
- Droits Administrateur Windows

### Instructions
1. Cliquez droit sur `disable_app_bound_encryption.ps1`
2. Sélectionnez "Exécuter avec PowerShell" (en tant qu'Administrateur)
3. Si vous voyez une erreur de stratégie d'exécution :
   - Ouvrez PowerShell en tant qu'Administrateur
   - Exécutez : `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process`
   - Puis : `.\disable_app_bound_encryption.ps1`

---

## MÉTHODE 2 : Modification Manuelle du Registre

### Via l'Éditeur de Registre (regedit)
1. Appuyez sur `Win + R`, tapez `regedit` et Entrée
2. Naviguez vers : `HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Google\Chrome`
3. Si le dossier `Chrome` n'existe pas, créez-le (clic droit sur `Google` > Nouveau > Clé)
4. Dans le dossier `Chrome`, clic droit > Nouveau > Valeur DWORD (32 bits)
5. Nommez-la : `ApplicationBoundEncryptionEnabled`
6. Double-clic > Définir la valeur à `0`
7. Cliquez OK
8. Fermez regedit et redémarrez Chrome

---

## MÉTHODE 3 : Flag de ligne de commande Chrome

### Modification du raccourci Chrome
1. Trouvez le raccourci Chrome (Bureau ou Menu Démarrer)
2. Clic droit > Propriétés
3. Dans le champ **Cible**, ajoutez à la fin (APRÈS les guillemets) :
   ```
   --disable-features=EncryptionKeySystemIntegration
   ```
4. La ligne complète devrait ressembler à :
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --disable-features=EncryptionKeySystemIntegration
   ```
5. Cliquez Appliquer > OK
6. Lancez Chrome uniquement via ce raccourci modifié

### Autres flags utiles (optionnels)
```
--disable-features=EncryptionKeySystemIntegration,WinUseBrowserSpellChecker
--user-data-dir="C:\ChromeCustomProfile"
```

---

## MÉTHODE 4 : Fichier de Politique d'Entreprise (GPO)

### Pour les environnements d'entreprise
1. Téléchargez les modèles de stratégie de groupe Chrome :
   https://chromeenterprise.google/browser/download/
2. Extrayez et copiez les fichiers `.admx` dans :
   `C:\Windows\PolicyDefinitions`
3. Ouvrez `gpedit.msc` (Éditeur de stratégie de groupe locale)
4. Naviguez vers :
   `Configuration ordinateur > Modèles d'administration > Google > Google Chrome`
5. Trouvez "Enable Application-Bound Encryption"
6. Définissez sur **Désactivé**
7. Appliquez et redémarrez

---

## VÉRIFICATION DE LA DÉSACTIVATION

### Comment vérifier que c'est désactivé

1. Ouvrez Chrome
2. Allez dans : `chrome://policy`
3. Recherchez `ApplicationBoundEncryptionEnabled`
4. La valeur devrait être `false` ou `0`

### Test avec le décrypteur
1. Fermez complètement Chrome (vérifiez le Gestionnaire des tâches)
2. Supprimez l'ancien fichier `Login Data`
3. Rouvrez Chrome et reconnectez-vous sur un site
4. Copiez le nouveau fichier `Login Data`
5. Exécutez `decryptor_elevation_windows.py`
6. Les nouveaux mots de passe devraient être en format `v10` (décryptables)

---

## DÉPANNAGE

### Le registre ne se modifie pas
- Vérifiez que vous avez les droits Administrateur
- Certaines entreprises bloquent les modifications via GPO

### Chrome ignore les flags
- Assurez-vous qu'aucune instance Chrome n'est en cours d'exécution
- Vérifiez le Gestionnaire des tâches (Ctrl+Shift+Échap)
- Tuez tous les processus `chrome.exe`

### Les mots de passe restent en v20
- Les ANCIENS mots de passe resteront en v20
- Seuls les NOUVEAUX mots de passe (après désactivation) seront en v10
- Solution : Supprimez et ré-enregistrez les mots de passe dans Chrome

---

## AVERTISSEMENTS

⚠️ **Sécurité** : La désactivation d'App-Bound Encryption réduit la protection de vos mots de passe contre les malwares.

⚠️ **Mises à jour** : Chrome peut réactiver cette fonctionnalité lors de mises à jour majeures.

⚠️ **Entreprise** : Si vous êtes dans un environnement d'entreprise géré, ces modifications peuvent être bloquées ou annulées par les administrateurs.

---

## FICHIERS CRÉÉS

1. `disable_app_bound_encryption.ps1` - Script PowerShell automatique
2. `decryptor_elevation_windows.py` - Décrypteur avec support v20
3. `DISABLE_GUIDE.md` - Ce guide (documentation)

---

## SUPPORT

Si après toutes ces méthodes les mots de passe restent indécryptables :
- Utilisez la fonction intégrée de Chrome : `chrome://settings/passwords`
- Cliquez sur l'œil pour voir chaque mot de passe (nécessite PIN/mot de passe Windows)
- Exportez les mots de passe : Menu (⋮) > Exporter les mots de passe
