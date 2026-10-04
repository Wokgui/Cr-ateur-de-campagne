# Actions SteamVR Builder

Ce manifeste est un **fragment de référence** : il ne doit pas remplacer le manifeste
principal de L4D2VR tel quel. Les actions `/actions/builder` doivent être fusionnées
dans son `action_manifest.json` et liées au Quest/Oculus Touch.

Commandes prévues :

- ToggleBuilder : entrer/sortir du mode construction ;
- Place : placer l'outil sélectionné au point visé ;
- Delete : supprimer l'objet Builder pointé ;
- NextTool / PrevTool : pièce, porte, arme, lumière, voiture, horde.

Le mode Builder utilisera son propre action set afin d'éviter de tirer/recharger
accidentellement pendant l'édition.
