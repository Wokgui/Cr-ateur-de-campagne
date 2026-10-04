# Lancement Windows du prototype

Le lanceur `tools/start_builder.ps1` prépare automatiquement la partie PC du Builder.

Il :

1. détecte Left 4 Dead 2 dans la bibliothèque Steam principale ou les bibliothèques déclarées dans `libraryfolders.vdf` ;
2. vérifie la présence de Python ;
3. indexe les assets installés de L4D2 dans `build/assets.json` au premier lancement ;
4. démarre le pont local sur `127.0.0.1:8765` ;
5. vérifie `/health` ;
6. lance L4D2 avec `-insecure`.

Depuis PowerShell à la racine du dépôt :

```powershell
.\tools\start_builder.ps1
```

Pour seulement préparer le Builder sans lancer le jeu :

```powershell
.\tools\start_builder.ps1 -NoLaunch
```

Pour forcer une nouvelle indexation après installation d'add-ons ou modification des fichiers du jeu :

```powershell
.\tools\start_builder.ps1 -ReindexAssets
```

Si la détection Steam échoue :

```powershell
.\tools\start_builder.ps1 -L4D2 "D:\SteamLibrary\steamapps\common\Left 4 Dead 2"
```

## DLL VR

La DLL Builder est construite automatiquement par GitHub Actions. Ne remplacez pas encore votre installation L4D2VR principale sans sauvegarde : le chargement réel, les contrôles Quest et le protocole avec le bridge doivent encore être validés dans le jeu.
