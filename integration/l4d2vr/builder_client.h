#pragma once

#include <string>

class VR;

class BuilderClient
{
public:
    explicit BuilderClient(VR* vr);

    void Toggle();
    bool IsEnabled() const { return m_Enabled; }

    // Sends a command using the current right-controller ray.
    // maxDistance is expressed in Source map units.
    bool SendCommand(const std::string& command, float maxDistance = 4096.0f);

private:
    VR* m_VR = nullptr;
    bool m_Enabled = false;

    bool ResolvePointer(float maxDistance, float& x, float& y, float& z) const;
    bool PostCommand(const std::string& command, float x, float y, float z) const;
};
