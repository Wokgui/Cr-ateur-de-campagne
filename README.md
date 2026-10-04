# Créateur de campagne L4D2 VR

Prototype d'un éditeur de campagnes Left 4 Dead 2 pensé pour être piloté en VR.

## Objectif du prototype

Transformer une scène structurée en fichier VMF Source exploitable dans Hammer / Left 4 Dead 2.

Exemple visé :

- une pièce ;
- une porte ;
- une zone de déclenchement ;
- une horde associée.

Le flux cible est :

VR / voix -> description de scène -> VMF -> compilation Source -> test dans L4D2 VR.

## État actuel

Première brique : générateur VMF autonome en Python.

Lancer :

```bash
python src/main.py examples/room_horde.json --out build/room_horde.vmf
```

Le fichier généré se trouve dans `build/room_horde.vmf`.

## Prochaine étape

Brancher un éditeur spatial VR qui produit le JSON de scène automatiquement.
