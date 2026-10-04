# Créateur de campagne L4D2 VR

Prototype d'un éditeur de campagnes **Left 4 Dead 2 directement en VR**.

## Ce qui fonctionne dans le prototype

- scène persistante JSON ;
- génération automatique d'un VMF Source ;
- pièces fermées ;
- portes ;
- déclencheurs de hordes ;
- armes ;
- lumières ;
- props (premier exemple : voiture) ;
- commandes françaises simples ;
- positionnement au point visé par le contrôleur ;
- sélection par identifiant ou objet le plus proche ;
- déplacer / tourner / supprimer ;
- pont HTTP local pour le mod VR ;
- compilation Windows VBSP -> VVIS -> VRAD -> dossier maps ;
- tests automatiques GitHub Actions.

## Démarrage du pont Builder

```bash
python src/vr_bridge.py
```

Puis une commande spatiale peut être envoyée à `POST /command` :

```json
{
  "command": "crée une pièce de 6 par 4 mètres",
  "pointer": [128, -64, 0]
}
```

Le pont régénère automatiquement :

- `build/live_scene.json`
- `build/live_scene.vmf`

## Génération hors VR

```bash
python src/main.py examples/room_horde.json --out build/room_horde.vmf
```

## Compilation L4D2 sous Windows

PowerShell :

```powershell
.\tools\compile_l4d2_map.ps1 -Vmf .\build\live_scene.vmf -MapName vr_generated
```

Le script utilise les outils Source de Left 4 Dead 2, compile le BSP puis le copie
dans `left4dead2/maps`.

## Intégration VR

Voir :

- `docs/VR_PROTOCOL.md`
- `docs/L4D2VR_INTEGRATION.md`

Le mod `sd805/l4d2vr` possède déjà le tracking OpenVR du contrôleur droit.
Le Builder doit réutiliser sa position/direction, faire un raycast Source puis envoyer
le point obtenu au pont local.

## Architecture

```text
voix / menu VR / contrôleur
          |
          v
   L4D2VR Builder
          |
    raycast Source
          |
          v
   pont local Python
          |
 commande + position
          |
          v
    scène structurée
          |
          v
     générateur VMF
          |
          v
 VBSP -> VVIS -> VRAD
          |
          v
        L4D2
```

Le générateur est volontairement indépendant de l'IA : une couche IA pourra ensuite
convertir des demandes beaucoup plus libres (« fais une pharmacie abandonnée ici »)
en opérations structurées sans rendre le format de carte dépendant d'un modèle.
