# Patch C++ L4D2VR Builder

Ce dossier contient la première couche C++ destinée au mod `sd805/l4d2vr`.

## Fichiers

- `builder_client.h`
- `builder_client.cpp`

Ils réutilisent directement :

- `VR::m_RightControllerPosAbs`
- `VR::m_RightControllerForward`

et envoient les commandes au pont local du Créateur de campagne sur
`127.0.0.1:8765`.

## Intégration dans L4D2VR

Ajouter les deux fichiers au projet Visual Studio, puis créer un
`BuilderClient` associé à l'instance `VR`.

Exemple conceptuel :

```cpp
BuilderClient builder(this);
builder.Toggle();
builder.SendCommand("mets une porte ici");
```

## Raycast

La version actuelle du client sait déjà calculer un rayon à partir du contrôleur,
mais utilise provisoirement son extrémité à distance fixe. Pour une édition précise,
`ResolvePointer` doit être relié au trace/raycast Source du mod afin de renvoyer
l'intersection réelle avec mur, sol ou prop.

Ce choix est volontaire : la communication et le format sont fonctionnels sans
introduire une dépendance à une interface de trace Source dont la signature doit
être vérifiée dans la version exacte du mod compilée.

## Sécurité

Le client utilise WinHTTP vers `127.0.0.1` uniquement. Aucun serveur distant,
clé API ou accès Internet n'est nécessaire.
