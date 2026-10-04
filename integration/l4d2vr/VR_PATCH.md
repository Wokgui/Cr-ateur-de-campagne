# Intégration complète dans `VR`

Les changements suivants sont destinés au fork de `sd805/l4d2vr`.

## vr.h

Ajouter :

```cpp
#include "builder_client.h"
```

Dans `class VR` :

```cpp
BuilderClient* m_Builder = nullptr;

vr::VRActionSetHandle_t m_BuilderActionSet;
vr::VRActiveActionSet_t m_BuilderActiveActionSet;

vr::VRActionHandle_t m_ActionBuilderToggle;
vr::VRActionHandle_t m_ActionBuilderPlace;
vr::VRActionHandle_t m_ActionBuilderDelete;
vr::VRActionHandle_t m_ActionBuilderNextTool;
vr::VRActionHandle_t m_ActionBuilderPrevTool;

int m_BuilderTool = 0;
```

## Constructeur VR

Après l'initialisation du système VR :

```cpp
m_Builder = new BuilderClient(this);
```

## SetActionManifest

Après les actions existantes :

```cpp
m_Input->GetActionHandle("/actions/builder/in/ToggleBuilder", &m_ActionBuilderToggle);
m_Input->GetActionHandle("/actions/builder/in/Place", &m_ActionBuilderPlace);
m_Input->GetActionHandle("/actions/builder/in/Delete", &m_ActionBuilderDelete);
m_Input->GetActionHandle("/actions/builder/in/NextTool", &m_ActionBuilderNextTool);
m_Input->GetActionHandle("/actions/builder/in/PrevTool", &m_ActionBuilderPrevTool);

m_Input->GetActionSetHandle("/actions/builder", &m_BuilderActionSet);
m_BuilderActiveActionSet = {};
m_BuilderActiveActionSet.ulActionSet = m_BuilderActionSet;
```

Le manifeste principal doit contenir les actions du fichier
`builder_action_manifest.fragment.json`.

## ProcessInput

Le Builder intercepte les entrées avant les commandes de combat :

```cpp
if (PressedDigitalAction(m_ActionBuilderToggle, true))
    m_Builder->Toggle();

if (m_Builder && m_Builder->IsEnabled())
{
    static const char* tools[] = {
        "mets une porte ici",
        "mets une arme ici",
        "mets une lumière ici",
        "mets une voiture ici",
        "déclenche une horde ici"
    };
    constexpr int toolCount = sizeof(tools) / sizeof(tools[0]);

    if (PressedDigitalAction(m_ActionBuilderNextTool, true))
        m_BuilderTool = (m_BuilderTool + 1) % toolCount;

    if (PressedDigitalAction(m_ActionBuilderPrevTool, true))
        m_BuilderTool = (m_BuilderTool + toolCount - 1) % toolCount;

    if (PressedDigitalAction(m_ActionBuilderPlace, true))
        m_Builder->SendCommand(tools[m_BuilderTool]);

    if (PressedDigitalAction(m_ActionBuilderDelete, true))
        m_Builder->SendCommand("supprime ça");

    // Ne pas envoyer les mêmes boutons au jeu pendant l'édition.
    return;
}
```

## Action sets

`UpdateActionState` doit recevoir l'action set Builder en plus de l'action set
principal. Il est préférable de désactiver/prioriser le set principal lorsque
Builder est actif afin qu'une pression de placement ne déclenche pas simultanément
un tir.

## Pointeur

`BuilderClient::ResolvePointer` utilise désormais directement :

```cpp
m_Game->m_EngineTrace->TraceRay(...)
```

avec `EngineTraceClient003`, interface déjà chargée par L4D2VR. L'impact
`trace.endpos` est donc exprimé directement en coordonnées Source de la carte.
