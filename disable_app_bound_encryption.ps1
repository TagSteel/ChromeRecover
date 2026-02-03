# Script PowerShell pour désactiver App-Bound Encryption
# À exécuter en tant qu'Administrateur

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DÉSACTIVATION APP-BOUND ENCRYPTION CHROME" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérification des privilèges administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERREUR: Ce script doit être exécuté en tant qu'Administrateur!" -ForegroundColor Red
    Write-Host "Faites un clic droit > Exécuter en tant qu'administrateur" -ForegroundColor Yellow
    pause
    exit
}

Write-Host "[INFO] Privilèges administrateur détectés" -ForegroundColor Green
Write-Host ""

# Méthode 1 : Politique de groupe locale (GPO)
Write-Host "[1/3] Configuration de la politique de groupe Chrome..." -ForegroundColor Yellow

# Chemin de la clé de registre pour les politiques Chrome
$chromePolicyPath = "HKLM:\SOFTWARE\Policies\Google\Chrome"

# Créer la clé si elle n'existe pas
if (-not (Test-Path $chromePolicyPath)) {
    New-Item -Path $chromePolicyPath -Force | Out-Null
    Write-Host "  - Clé de politique Chrome créée" -ForegroundColor Gray
}

# Désactiver App-Bound Encryption
try {
    Set-ItemProperty -Path $chromePolicyPath -Name "ApplicationBoundEncryptionEnabled" -Value 0 -Type DWord -Force
    Write-Host "  ✓ ApplicationBoundEncryptionEnabled = 0 (Désactivé)" -ForegroundColor Green
} catch {
    Write-Host "  × Erreur lors de la modification du registre: $_" -ForegroundColor Red
}

Write-Host ""

# Méthode 2 : Arrêt du service Elevation
Write-Host "[2/3] Tentative d'arrêt du service Elevation..." -ForegroundColor Yellow

$elevationServices = Get-Service -Name "*Elevation*" -ErrorAction SilentlyContinue

if ($elevationServices) {
    foreach ($service in $elevationServices) {
        Write-Host "  - Service trouvé: $($service.Name) (Status: $($service.Status))" -ForegroundColor Gray
        
        if ($service.Status -eq "Running") {
            try {
                Stop-Service -Name $service.Name -Force -ErrorAction Stop
                Set-Service -Name $service.Name -StartupType Disabled -ErrorAction Stop
                Write-Host "  ✓ Service $($service.Name) arrêté et désactivé" -ForegroundColor Green
            } catch {
                Write-Host "  × Impossible d'arrêter le service: $_" -ForegroundColor Red
            }
        }
    }
} else {
    Write-Host "  - Aucun service Elevation trouvé" -ForegroundColor Gray
}

Write-Host ""

# Méthode 3 : Instructions pour le flag Chrome
Write-Host "[3/3] Configuration du raccourci Chrome avec flag..." -ForegroundColor Yellow
Write-Host ""
Write-Host "INSTRUCTIONS MANUELLES:" -ForegroundColor Cyan
Write-Host "1. Localisez votre raccourci Chrome (Bureau ou Menu Démarrer)" -ForegroundColor White
Write-Host "2. Faites un clic droit > Propriétés" -ForegroundColor White
Write-Host "3. Dans le champ 'Cible', ajoutez à la fin (après les guillemets):" -ForegroundColor White
Write-Host "   --disable-features=EncryptionKeySystemIntegration" -ForegroundColor Yellow
Write-Host ""
Write-Host "Exemple de ligne Cible complète:" -ForegroundColor White
Write-Host '"C:\Program Files\Google\Chrome\Application\chrome.exe" --disable-features=EncryptionKeySystemIntegration' -ForegroundColor Gray
Write-Host ""
Write-Host "4. Cliquez sur Appliquer puis OK" -ForegroundColor White
Write-Host "5. Redémarrez Chrome avec ce raccourci modifié" -ForegroundColor White
Write-Host ""

# Vérification finale
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RÉSUMÉ DES ACTIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (Get-ItemProperty -Path $chromePolicyPath -Name "ApplicationBoundEncryptionEnabled" -ErrorAction SilentlyContinue) {
    $value = (Get-ItemProperty -Path $chromePolicyPath).ApplicationBoundEncryptionEnabled
    if ($value -eq 0) {
        Write-Host "✓ Politique de groupe : App-Bound Encryption DÉSACTIVÉ" -ForegroundColor Green
    } else {
        Write-Host "× Politique de groupe : Échec" -ForegroundColor Red
    }
} else {
    Write-Host "× Politique de groupe : Non configurée" -ForegroundColor Red
}

Write-Host ""
Write-Host "PROCHAINES ÉTAPES:" -ForegroundColor Yellow
Write-Host "1. Fermez complètement Chrome (vérifiez dans le Gestionnaire des tâches)" -ForegroundColor White
Write-Host "2. Redémarrez Chrome" -ForegroundColor White
Write-Host "3. Réessayez le script de décryptage" -ForegroundColor White
Write-Host ""
Write-Host "Note: Ces modifications peuvent être réinitialisées par les mises à jour de Chrome." -ForegroundColor Gray
Write-Host ""

pause
