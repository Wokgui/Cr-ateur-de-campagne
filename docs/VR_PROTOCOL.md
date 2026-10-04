# Protocole VR local

Le prototype sépare volontairement la VR du générateur Source.

## Serveur PC

```bash
python src/vr_bridge.py
```

Le pont écoute uniquement sur `127.0.0.1:8765` par défaut.

### POST /command

```json
{
  "command": "crée une pièce de 6 par 4 mètres",
  "pointer": [128, -64, 0]
}
```

`pointer` représente le point visé par le contrôleur VR en unités Source.

Commandes actuellement comprises :

- `crée une pièce de 6 par 4 mètres`
- `mets une porte ici`
- `déclenche une horde ici`
- `supprime`

Chaque commande met à jour `build/live_scene.json` et régénère
`build/live_scene.vmf`.

## Architecture cible

Le mod VR/OpenXR envoie seulement l'intention, le point visé et plus tard
l'identifiant de l'objet sélectionné. Le PC reste responsable de la scène,
de la génération VMF et de la compilation Source.

Cette séparation évite de modifier le moteur Source pour chaque nouvelle
fonction d'édition.
