#Requires AutoHotkey v2.0

GuideEndpointTitle(hostPath) {
    pathBuffer := Buffer(65536, 0)
    if !DllCall("GetFullPathNameW", "Str", hostPath, "UInt", 32768, "Ptr", pathBuffer, "Ptr", 0)
        throw Error("The guide host path could not be resolved.")
    return "F7Hub.AltF7Hub.Ready.v1|" StrLower(StrGet(pathBuffer))
}

FindGuideEndpoint(hostPath) => DllCall("FindWindowW", "Str", "AutoHotkeyGUI", "Str", GuideEndpointTitle(hostPath), "Ptr")

CanUseGuideKeyboardFallback(dispatched, ready, visible, editorOpen) => !dispatched && ready && !visible && !editorOpen

WriteGuideClientOutput(text, stream := "*") {
    try FileAppend(text "`n", stream, "UTF-8")
    catch OSError as outputError {
        ; Double-click and AHK RunWait clients can lack console handles.
        if outputError.Number != 6
            throw outputError
    }
}

RequestGuide(hostPath, show := true) {
    deadline := A_TickCount + 10000
    ; Serialize clients for this checkout. AHK message monitors do not reenter
    ; an already-running show handler; concurrent sends would lose the ACK.
    mutexName := "Local\" StrReplace(GuideEndpointTitle(hostPath), "\", "|")
    mutex := DllCall("CreateMutexW", "Ptr", 0, "Int", false, "Str", mutexName, "Ptr")
    if !mutex
        throw Error("The guide request could not be coordinated. Retry opening it.")
    acquired := false
    try {
        wait := DllCall("WaitForSingleObject", "Ptr", mutex, "UInt", 10000)
        acquired := wait = 0 || wait = 0x80
        if !acquired
            throw Error("Another guide request is finishing. Retry opening it.")
        return RequestGuideUnlocked(hostPath, show, deadline)
    } finally {
        if acquired
            DllCall("ReleaseMutex", "Ptr", mutex)
        DllCall("CloseHandle", "Ptr", mutex)
    }
}
RequestGuideUnlocked(hostPath, show, deadline) {
    endpoint := FindGuideEndpoint(hostPath)
    if !endpoint
        Run('"' A_AhkPath '" /ErrorStdOut=UTF-8 "' hostPath '"', , "Hide")
    while !endpoint && A_TickCount < deadline {
        Sleep(25)
        endpoint := FindGuideEndpoint(hostPath)
    }
    if !endpoint
        throw Error("The guide host did not become ready. An open request was not confirmed.")
    if !show
        return "STARTED"
    pid := WinGetPID(endpoint)
    if StrLower(WinGetProcessPath(endpoint)) != StrLower(A_AhkPath)
        throw Error("The guide host uses a different AutoHotkey interpreter.")
    DllCall("AllowSetForegroundWindow", "UInt", pid)
    message := DllCall("RegisterWindowMessageW", "Str", "F7Hub.AltF7Hub.Show.v1", "UInt")
    if !message
        return GuideKeyboardFallback(pid, false, true)
    response := 0
    ; Delivery may complete after timeout: never follow a dispatch with a toggle.
    sent := DllCall("SendMessageTimeoutW", "Ptr", endpoint, "UInt", message,
        "UPtr", 1, "Ptr", 0, "UInt", 0x23, "UInt", 3000, "UPtr*", &response, "Ptr")
    if !sent || (response != 1 && response != 2)
        throw Error("The guide open request was not confirmed. Retry or use Alt+F7.")
    title := response = 2 ? "topic" : "Help Desk & Interview Guide"
    found := false
    for window in WinGetList("ahk_pid " pid)
        if DllCall("IsWindowVisible", "Ptr", window) && InStr(WinGetTitle(window), title)
            found := true
    if !found
        throw Error("The guide open request was not confirmed. Retry or use Alt+F7.")
    return response = 2 ? "FOCUSED_EDITOR" : "SHOWN"
}

GuideKeyboardFallback(pid, dispatched, ready) {
    oldHidden := A_DetectHiddenWindows
    DetectHiddenWindows(true)
    try {
        guide := WinExist("Help Desk & Interview Guide ahk_pid " pid)
        editor := WinExist("Edit topic ahk_pid " pid) || WinExist("Create topic ahk_pid " pid)
        visible := guide && DllCall("IsWindowVisible", "Ptr", guide)
        if !CanUseGuideKeyboardFallback(dispatched, ready, visible, editor != 0)
            throw Error("The guide open request was not confirmed. Use Alt+F7.")
        for key in ["Ctrl", "Alt", "Shift", "LWin", "RWin"]
            if GetKeyState(key, "P")
                throw Error("Release modifier keys and retry opening the guide.")
        SendLevel(1)
        SendEvent("!{F7}")
        deadline := A_TickCount + 3000
        while A_TickCount < deadline {
            guide := WinExist("Help Desk & Interview Guide ahk_pid " pid)
            if guide && DllCall("IsWindowVisible", "Ptr", guide)
                return "SHOWN"
            Sleep(25)
        }
        throw Error("The guide keyboard open request was not confirmed.")
    } finally
        DetectHiddenWindows(oldHidden)
}
