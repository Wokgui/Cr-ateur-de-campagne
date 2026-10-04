from pathlib import Path
import json, sys

root=Path(sys.argv[1]).resolve()
p=root/"L4D2VR"
h=p/"vr.h"; c=p/"vr.cpp"
hs=h.read_text(encoding="utf-8-sig")
if "class BuilderClient;" not in hs: hs=hs.replace("class Game;","class Game;\nclass BuilderClient;")
if "m_Builder = nullptr" not in hs:
    hs=hs.replace("Game *m_Game = nullptr;","Game *m_Game = nullptr;\n\tBuilderClient *m_Builder = nullptr;\n\tint m_BuilderTool = 0;\n\tbool m_BuilderToggleLatch = false;")
h.write_text(hs,encoding="utf-8")

cs=c.read_text(encoding="utf-8-sig")
if '#include "builder_client.h"' not in cs: cs=cs.replace('#include "vr.h"','#include "vr.h"\n#include "builder_client.h"',1)
if "m_Builder = new BuilderClient" not in cs: cs=cs.replace("m_Game = game;","m_Game = game;\n    m_Builder = new BuilderClient(this);",1)

marker='vr::VROverlay()->SetOverlayFlag(m_HUDHandle, vr::VROverlayFlags_MakeOverlaysInteractiveIfVisible, false);'
block=r'''

    // Quest/Oculus Touch: touch the right stick up + down cannot happen physically,
    // so use both inventory edge actions in the same frame as a deliberate Builder chord.
    // This keeps the normal manifest/bindings untouched and Builder cannot steal controls
    // until explicitly enabled.
    const bool builderChord =
        PressedDigitalAction(m_ActionPrevItem) &&
        PressedDigitalAction(m_ActionNextItem);
    if (m_Builder && builderChord && !m_BuilderToggleLatch)
        m_Builder->Toggle();
    m_BuilderToggleLatch = builderChord;

    if (m_Builder && m_Builder->IsEnabled()) {
        static const char *tools[] = {
            "mets une porte ici",
            "mets une arme ici",
            "mets une lumiere ici",
            "mets une voiture ici",
            "declenche une horde ici"
        };
        const int n = sizeof(tools) / sizeof(tools[0]);

        // Existing Quest controls are remapped only inside Builder mode:
        // right trigger = place, B = delete, stick up/down = previous/next tool.
        if (PressedDigitalAction(m_ActionPrevItem, true))
            m_BuilderTool = (m_BuilderTool + n - 1) % n;
        if (PressedDigitalAction(m_ActionNextItem, true))
            m_BuilderTool = (m_BuilderTool + 1) % n;
        if (PressedDigitalAction(m_ActionPrimaryAttack, true))
            m_Builder->SendCommand(tools[m_BuilderTool]);
        if (PressedDigitalAction(m_ActionUse, true))
            m_Builder->SendCommand("supprime ca");

        // Stop held gameplay actions when entering Builder.
        m_Game->ClientCmd_Unrestricted("-attack");
        m_Game->ClientCmd_Unrestricted("-attack2");
        m_Game->ClientCmd_Unrestricted("-use");
        m_Game->ClientCmd_Unrestricted("-reload");
        return;
    }'''
if "const bool builderChord" not in cs: cs=cs.replace(marker,marker+block,1)
c.write_text(cs,encoding="utf-8")
print("Builder runtime integration applied using existing Quest/Oculus Touch actions")
