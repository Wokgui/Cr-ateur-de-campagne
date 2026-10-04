#include "builder_client.h"
#include "vr.h"
#include "game.h"
#include "sdk/sdk.h"\n#include "sdk/trace.h"

#include <Windows.h>
#include <winhttp.h>
#include <sstream>
#include <string>

#pragma comment(lib, "winhttp.lib")

BuilderClient::BuilderClient(VR* vr) : m_VR(vr) {}

void BuilderClient::Toggle()
{
    m_Enabled = !m_Enabled;
}

bool BuilderClient::ResolvePointer(float maxDistance, float& x, float& y, float& z) const
{
    if (!m_VR)
        return false;

    if (!m_VR->m_Game || !m_VR->m_Game->m_EngineTrace)
        return false;

    const Vector origin = m_VR->m_RightControllerPosAbs;
    const Vector forward = m_VR->m_RightControllerForward;
    const Vector end = origin + forward * maxDistance;

    Ray_t ray;
    ray.Init(origin, end);

    // sdk/sdk.h provides the entity declarations required by trace.h.
    // Skip NPCs/players so Builder placement targets map geometry and props.
    CTraceFilterSkipNPCsAndPlayers filter(nullptr, 0);
    trace_t trace{};
    m_VR->m_Game->m_EngineTrace->TraceRay(
        ray,
        MASK_STATICWORLD | CONTENTS_MOVEABLE,
        &filter,
        &trace);

    if (!trace.DidHit() || trace.startsolid || trace.allsolid)
        return false;

    x = trace.endpos.x;
    y = trace.endpos.y;
    z = trace.endpos.z;
    return true;
}

static std::string EscapeJson(const std::string& value)
{
    std::string out;
    out.reserve(value.size() + 8);
    for (char c : value)
    {
        switch (c)
        {
        case '\\': out += "\\\\"; break;
        case '"': out += "\\\""; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        default: out += c; break;
        }
    }
    return out;
}

bool BuilderClient::PostCommand(const std::string& command, float x, float y, float z) const
{
    HINTERNET session = WinHttpOpen(
        L"L4D2VR-Builder/0.1",
        WINHTTP_ACCESS_TYPE_NO_PROXY,
        WINHTTP_NO_PROXY_NAME,
        WINHTTP_NO_PROXY_BYPASS,
        0);

    if (!session)
        return false;

    // Hard-coded loopback by design: the Builder API must never be exposed
    // outside the local PC.
    HINTERNET connection = WinHttpConnect(session, L"127.0.0.1", 8765, 0);
    if (!connection)
    {
        WinHttpCloseHandle(session);
        return false;
    }

    HINTERNET request = WinHttpOpenRequest(
        connection, L"POST", L"/command", nullptr,
        WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES, 0);

    if (!request)
    {
        WinHttpCloseHandle(connection);
        WinHttpCloseHandle(session);
        return false;
    }

    std::ostringstream json;
    json << "{\"command\":\"" << EscapeJson(command)
         << "\",\"pointer\":[" << x << "," << y << "," << z << "]}";
    const std::string body = json.str();

    const wchar_t* headers = L"Content-Type: application/json\r\n";
    BOOL ok = WinHttpSendRequest(
        request,
        headers,
        static_cast<DWORD>(-1L),
        (LPVOID)body.data(),
        static_cast<DWORD>(body.size()),
        static_cast<DWORD>(body.size()),
        0);

    if (ok)
        ok = WinHttpReceiveResponse(request, nullptr);

    if (ok)
    {
        DWORD status = 0;
        DWORD size = sizeof(status);
        WinHttpQueryHeaders(
            request,
            WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
            WINHTTP_HEADER_NAME_BY_INDEX,
            &status,
            &size,
            WINHTTP_NO_HEADER_INDEX);
        ok = status >= 200 && status < 300;
    }

    WinHttpCloseHandle(request);
    WinHttpCloseHandle(connection);
    WinHttpCloseHandle(session);
    return ok == TRUE;
}

bool BuilderClient::SendCommand(const std::string& command, float maxDistance)
{
    if (!m_Enabled)
        return false;

    float x = 0, y = 0, z = 0;
    if (!ResolvePointer(maxDistance, x, y, z))
        return false;

    return PostCommand(command, x, y, z);
}
