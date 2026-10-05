#pragma once
#include <string>
#include <vector>
#include <deque>
#include <mutex>
#include <condition_variable>
#include <thread>
class VR;
class BuilderClient {
public:
    explicit BuilderClient(VR* vr);
    ~BuilderClient();
    void Toggle();
    bool IsEnabled() const { return m_Enabled; }
    void Tick(int tool);
    bool SendCommand(const std::string& command, float maxDistance = 4096.0f);
private:
    struct Request { std::string command; float x, y, z; int tool; bool ok = false; };
    VR* m_VR = nullptr;
    void* m_Overlay = nullptr;
    bool m_Enabled = false;
    bool m_Stop = false;
    bool m_PreviewLogged = false;
    int m_Tool = 0;
    unsigned long long m_LastDraw = 0;
    std::mutex m_Mutex;
    std::condition_variable m_Wake;
    std::deque<Request> m_Queue, m_Results;
    std::vector<Request> m_Placed;
    std::thread m_Worker;
    void Worker();
    void Draw(const Request& item, bool ghost);
    bool ResolvePointer(float maxDistance, float& x, float& y, float& z) const;
    bool PostCommand(const std::string& command, float x, float y, float z) const;
};
