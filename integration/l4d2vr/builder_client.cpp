#include "builder_client.h"
#include "vr.h"
#include "game.h"
#include "sdk.h"
#include "trace.h"

#include <Windows.h>
#include <winhttp.h>
#include <sstream>
#include <string>
#include <algorithm>
#include <cmath>

#pragma comment(lib, "winhttp.lib")

// Prefix of Valve's VDebugOverlay003 interface; no virtual destructor slot.
class BuilderOverlay {
public:
    virtual void AddEntityTextOverlay(int, int, float, int, int, int, int, const char*, ...) = 0;
    virtual void AddBoxOverlay(const Vector&, const Vector&, const Vector&, const QAngle&, int, int, int, int, float) = 0;
};

BuilderClient::BuilderClient(VR* vr) : m_VR(vr)
{
    if (m_VR && m_VR->m_Game)
        m_Overlay = m_VR->m_Game->GetInterface("engine.dll", "VDebugOverlay003");
    Game::logMsg("Builder preview interface: %s", m_Overlay ? "ready" : "unavailable");
    m_Worker = std::thread(&BuilderClient::Worker, this);
}

BuilderClient::~BuilderClient()
{
    { std::lock_guard<std::mutex> lock(m_Mutex); m_Stop = true; }
    m_Wake.notify_one();
    if (m_Worker.joinable()) m_Worker.join();
}

void BuilderClient::Worker()
{
    for (;;) {
        Request item;
        {
            std::unique_lock<std::mutex> lock(m_Mutex);
            m_Wake.wait(lock, [this] { return m_Stop || !m_Queue.empty(); });
            if (m_Stop) return;
            item = m_Queue.front(); m_Queue.pop_front();
        }
        item.ok = PostCommand(item.command, item.x, item.y, item.z);
        {
            std::lock_guard<std::mutex> lock(m_Mutex);
            m_Results.push_back(item);
        }
    }
}

void BuilderClient::Draw(const Request& item, bool ghost)
{
    if (!m_Overlay) return;
    Vector mins(-16, -4, 0), maxs(16, 4, 80);
    switch (item.tool) {
    case 1: mins = Vector(-16,-5,0); maxs = Vector(16,5,8); break;
    case 2: mins = Vector(-6,-6,-6); maxs = Vector(6,6,6); break;
    case 3: mins = Vector(-90,-40,0); maxs = Vector(90,40,55); break;
    case 4: mins = Vector(-64,-64,0); maxs = Vector(64,64,128); break;
    }
    auto overlay = static_cast<BuilderOverlay*>(m_Overlay);
    const Vector origin(item.x,item.y,item.z);
    const QAngle angles(0,0,0);
    overlay->AddBoxOverlay(origin, mins, maxs, angles, ghost ? 90 : 0, ghost ? 255 : 170, ghost ? 90 : 255, ghost ? 35 : 70, 0.09f);
    // Door silhouette has a second small volume marking its handle.
    if (item.tool == 0)
        overlay->AddBoxOverlay(origin + Vector(11, -5, 40), Vector(-2,-2,-2), Vector(2,2,2), angles, 255,220,40,180,0.09f);
}

void BuilderClient::Tick(int tool)
{
    m_Tool = tool;
    std::deque<Request> results;
    { std::lock_guard<std::mutex> lock(m_Mutex); results.swap(m_Results); }
    for (const auto& item : results) {
        Game::logMsg("Builder command %s: %s", item.ok ? "saved" : "failed", item.command.c_str());
        if (!item.ok) continue;
        if (item.command == "supprime ca") {
            auto nearest = m_Placed.end(); float best = 1e30f;
            for (auto it = m_Placed.begin(); it != m_Placed.end(); ++it) {
                const float dx=it->x-item.x, dy=it->y-item.y, dz=it->z-item.z;
                const float d=dx*dx+dy*dy+dz*dz;
                if (d<best) {best=d;nearest=it;}
            }
            if (nearest != m_Placed.end()) m_Placed.erase(nearest);
        } else if (m_Placed.size() < 128) m_Placed.push_back(item);
    }
    if (!m_VR || !m_VR->m_Game || !m_VR->m_Game->m_EngineClient->IsInGame()) {
        m_Placed.clear(); return;
    }
    const auto now = GetTickCount64();
    if (now - m_LastDraw < 50) return; // 20 Hz, bounded and no network on this path.
    m_LastDraw = now;
    for (const auto& item : m_Placed) Draw(item, false);
    if (!m_Enabled) return;
    Request ghost; ghost.tool = tool;
    if (ResolvePointer(4096,ghost.x,ghost.y,ghost.z)) {
        Draw(ghost,true);
        if (!m_PreviewLogged) { Game::logMsg("Builder in-map preview drawing active"); m_PreviewLogged = true; }
    }
}

void BuilderClient::Toggle()
{
    m_Enabled = !m_Enabled;
    Game::logMsg("Builder mode: %s", m_Enabled ? "on" : "off");
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
    CGameTrace trace{};
    m_VR->m_Game->m_EngineTrace->TraceRay(
        ray,
        STANDARD_TRACE_MASK,
        &filter,
        &trace);

    if (trace.fraction <= 0.0f || trace.fraction >= 1.0f || trace.startsolid || trace.allsolid)
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
    WinHttpSetTimeouts(session, 500, 500, 1000, 1000);

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

    {
        std::lock_guard<std::mutex> lock(m_Mutex);
        if (m_Queue.size() >= 32) return false;
        Request item; item.command = command; item.x=x; item.y=y; item.z=z; item.tool=m_Tool;
        m_Queue.push_back(item);
    }
    m_Wake.notify_one();
    return true;
}
