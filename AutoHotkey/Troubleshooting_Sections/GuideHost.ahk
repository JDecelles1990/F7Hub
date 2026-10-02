#Requires AutoHotkey v2.0
#Include GuideCore.ahk
#Include GuideRequest.ahk

global GuideEndpoint := 0

InitializeGuideHost(dataDirectory, hostPath) {
    global DataRoot, GuideEndpoint
    DataRoot := dataDirectory
    LoadSettings()
    LoadTopics()
    OnMessage(0x100, HandleGuideKeys)
    OnMessage(0x111, HandleEditorChange)
    OnMessage(0x2B, DrawTopicItem)
    OnMessage(0x2C, MeasureTopicItem)
    OnExit(SavePendingGuideSettings)
    message := DllCall("RegisterWindowMessageW", "Str", "F7Hub.AltF7Hub.Show.v1", "UInt")
    if message
        OnMessage(message, HandleGuideShowRequest)
    GuideEndpoint := Gui(, GuideEndpointTitle(hostPath))
}

HandleGuideShowRequest(wParam, lParam, msg, hwnd) {
    if !IsObject(GuideEndpoint) || hwnd != GuideEndpoint.Hwnd || wParam != 1 || lParam != 0
        return 0
    try {
        result := ShowGuide()
        window := result = 2 ? EditorGui.Hwnd : Guide.Hwnd
        return DllCall("IsWindowVisible", "Ptr", window) ? result : 0
    } catch Error {
        return 0
    }
}
