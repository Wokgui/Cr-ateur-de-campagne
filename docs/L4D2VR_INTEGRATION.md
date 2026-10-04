# Intégration au mod L4D2VR

Le mod de référence est `sd805/l4d2vr`. Son code expose déjà dans `VR` les données
nécessaires à l'éditeur :

- `m_RightControllerPosAbs`
- `m_RightControllerForward`
- `m_RightControllerAngAbs`
- les actions SteamVR via `IVRInput`

L'éditeur n'a donc pas besoin d'un second système de tracking.

## Flux prévu dans le jeu

1. Un bouton active le mode **Builder**.
2. Le contrôleur droit sert de pointeur.
3. Un raycast Source calcule le point du décor visé.
4. Une commande vocale ou un bouton radial produit une intention.
5. Le mod envoie au pont local :
   `command`, `pointer`, et éventuellement `selected_id`.
6. Le pont met à jour la scène et le VMF.
7. **Compiler/Test** quitte/recharge la carte après compilation.

## Important

Le mod L4D2VR est injecté dans le processus du jeu. Le Builder doit rester local et
ne doit pas ouvrir son API sur le réseau. Le serveur Python écoute donc
`127.0.0.1` par défaut.

## Commandes du premier prototype

- « crée une pièce de 6 par 4 mètres »
- « mets une porte ici »
- « mets une arme ici »
- « mets une lumière 300 ici »
- « mets une voiture ici »
- « déclenche une horde ici »
- « déplace ça ici »
- « tourne ça de 90 degrés »
- « supprime ça »

## Étape C++ à intégrer au fork VR

À chaque frame Builder :

```cpp
Vector rayOrigin = vr->m_RightControllerPosAbs;
Vector rayDirection = vr->m_RightControllerForward;

// hitPoint = raycast Source(rayOrigin, rayDirection)
// selectedId = objet Builder éventuellement pointé
// SendBuilderCommand(spokenCommand, hitPoint, selectedId);
```

Le raycast doit utiliser le moteur Source du mod plutôt qu'une approximation
OpenVR : ainsi le point reçu par le générateur est directement dans le repère de
la carte L4D2.
