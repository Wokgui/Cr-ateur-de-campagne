# Tester L4D2VR Campaign Builder sur PC

Prototype : les commandes creent un JSON et un VMF. Les objets apparaissent dans le jeu apres compilation et rechargement du BSP. Un panneau VR, une navigation NAV et une campagne complete restent a realiser.
Prerequis : Left 4 Dead 2, L4D2VR deja fonctionnel avec ses fichiers SteamVR et dependances, SteamVR, Python 3.12 ou plus recent (https://www.python.org/downloads/windows/). Pour compiler, installer Left 4 Dead 2 Authoring Tools depuis la section Outils de Steam.

Extraire tout le ZIP dans un dossier conserve. Fermer le jeu. Ouvrir PowerShell dans ce dossier. Remplacer ci-dessous le chemin du jeu par celui affiche par Steam > L4D2 > Gerer > Parcourir les fichiers locaux.

Installation a la racine du jeu (d3d9.dll, a cote de left4dead2.exe), avec sauvegarde automatique :
    powershell -NoProfile -ExecutionPolicy Bypass -File .\install_builder_dll.ps1 -BuilderDll .\d3d9.dll -L4D2 "D:\SteamLibrary\steamapps\common\Left 4 Dead 2"

Test PC sans ouvrir le jeu :
    powershell -NoProfile -ExecutionPolicy Bypass -File .\start_builder.ps1 -NoLaunch -L4D2 "D:\SteamLibrary\steamapps\common\Left 4 Dead 2"
    Invoke-RestMethod http://127.0.0.1:8765/health
    $body = @{command="cree une piece de 6 par 4 metres";pointer=@(0,0,0)} | ConvertTo-Json
    Invoke-RestMethod http://127.0.0.1:8765/command -Method Post -Body $body -ContentType "application/json"
Attendu : ok=True, build\live_scene.json et build\live_scene.vmf crees. /health donne le PID du pont. Pour l'arreter : Stop-Process -Id <PID>. Arreter le pont avant toute relance. Pour une nouvelle scene, arreter le pont puis sauvegarder/deplacer ces deux fichiers.

Compilation avec les Authoring Tools :
    powershell -NoProfile -ExecutionPolicy Bypass -File .\compile_l4d2_map.ps1 -Vmf .\build\live_scene.vmf -MapName vr_generated -L4D2 "D:\SteamLibrary\steamapps\common\Left 4 Dead 2"
Attendu : left4dead2\maps\vr_generated.bsp.

Arreter le pont de test, lancer SteamVR, puis :
    powershell -NoProfile -ExecutionPolicy Bypass -File .\start_builder.ps1 -L4D2 "D:\SteamLibrary\steamapps\common\Left 4 Dead 2"
Le jeu utilise -insecure pour les tests locaux. Activer la console developpeur puis entrer : map vr_generated

Bindings Oculus Touch par defaut : A+B a droite active/desactive Builder ; joystick droit haut/bas change d'outil (porte, arme, lumiere, voiture, horde) ; gachette droite place au point vise ; B supprime l'objet le plus proche. Verifier /scene et les fichiers pour confirmer chaque action. Il n'y a pas encore de panneau VR indiquant le mode ou l'outil. Les modifications s'affichent apres recompilation et rechargement de la carte.

Restauration, jeu ferme :
    powershell -NoProfile -ExecutionPolicy Bypass -File .\install_builder_dll.ps1 -BuilderDll .\d3d9.dll -L4D2 "D:\SteamLibrary\steamapps\common\Left 4 Dead 2" -Restore
Si aucune DLL n'existait avant installation, il n'y a pas de sauvegarde a restaurer.

Validation automatisee : Python, HTTP, persistance JSON/VMF, copie/restauration, empreinte DLL et lancement depuis un dossier avec espaces. Chargement dans L4D2, compilation Valve et interaction au casque restent a confirmer sur un PC equipe.

Apercu en direct : en mode Builder, un volume vert suit le point vise. La porte est representee par un volume vertical et une poignee jaune. Apres sauvegarde, un volume cyan reste dans la carte pour les objets places pendant cette session. Il s'agit d'une representation de volume, pas encore du modele final. Les apercus sont limites a 128 objets par session ; la scene complete reste sauvegardee dans le JSON. Les apercus de session ne sont pas restaures apres changement de carte/redemarrage.
Les commandes HTTP passent sur un worker dedie ; la visee et le rendu ne font aucun appel reseau. Aucune console ou fenetre n'est ouverte par les actions Builder. Locomotion et HUD restent actifs.
