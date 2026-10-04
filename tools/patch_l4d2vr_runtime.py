from pathlib import Path
import json, sys

root=Path(sys.argv[1]).resolve()
p=root/"L4D2VR"
h=p/"vr.h"; c=p/"vr.cpp"; m=p/"SteamVRActionManifest"/"action_manifest.json"
hs=h.read_text(encoding="utf-8-sig")
if "class BuilderClient;" not in hs: hs=hs.replace("class Game;","class Game;\nclass BuilderClient;")
if "m_Builder = nullptr" not in hs:
    hs=hs.replace("Game *m_Game = nullptr;","Game *m_Game = nullptr;\n\tBuilderClient *m_Builder = nullptr;\n\tvr::VRActionHandle_t m_ActionBuilderToggle = 0;\n\tvr::VRActionHandle_t m_ActionBuilderPlace = 0;\n\tvr::VRActionHandle_t m_ActionBuilderDelete = 0;\n\tint m_BuilderTool = 0;")
h.write_text(hs,encoding="utf-8")

cs=c.read_text(encoding="utf-8-sig")
if '#include "builder_client.h"' not in cs: cs=cs.replace('#include "vr.h"','#include "vr.h"\n#include "builder_client.h"',1)
if "m_Builder = new BuilderClient" not in cs: cs=cs.replace("m_Game = game;","m_Game = game;\n    m_Builder = new BuilderClient(this);",1)
needle='m_Input->GetActionHandle("/actions/main/in/Pause", &m_Pause);'
if "/actions/main/in/BuilderToggle" not in cs:
    cs=cs.replace(needle,needle+'\n    m_Input->GetActionHandle("/actions/main/in/BuilderToggle", &m_ActionBuilderToggle);\n    m_Input->GetActionHandle("/actions/main/in/BuilderPlace", &m_ActionBuilderPlace);\n    m_Input->GetActionHandle("/actions/main/in/BuilderDelete", &m_ActionBuilderDelete);',1)
marker='vr::VROverlay()->SetOverlayFlag(m_HUDHandle, vr::VROverlayFlags_MakeOverlaysInteractiveIfVisible, false);'
block='''\n\n    if (m_Builder && PressedDigitalAction(m_ActionBuilderToggle, true)) m_Builder->Toggle();
    // Builder mode owns gameplay input while active.
    if (m_Builder && m_Builder->IsEnabled()) {
        static const char *tools[] = {"mets une porte ici","mets une arme ici","mets une lumiere ici","mets une voiture ici","declenche une horde ici"};
        const int n = sizeof(tools)/sizeof(tools[0]);
        if (PressedDigitalAction(m_ActionNextItem,true)) m_BuilderTool=(m_BuilderTool+1)%n;
        if (PressedDigitalAction(m_ActionPrevItem,true)) m_BuilderTool=(m_BuilderTool+n-1)%n;
        if (PressedDigitalAction(m_ActionBuilderPlace,true)) m_Builder->SendCommand(tools[m_BuilderTool]);
        if (PressedDigitalAction(m_ActionBuilderDelete,true)) m_Builder->SendCommand("supprime ca");
        return;
    }'''
if "Builder mode owns gameplay input" not in cs: cs=cs.replace(marker,marker+block,1)
c.write_text(cs,encoding="utf-8")

data=json.loads(m.read_text(encoding="utf-8-sig"))
names={a["name"] for a in data["actions"]}
for name in ("/actions/main/in/BuilderToggle","/actions/main/in/BuilderPlace","/actions/main/in/BuilderDelete"):
    if name not in names: data["actions"].append({"name":name,"type":"boolean","requirement":"optional"})
m.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
print("Builder runtime integration applied")
