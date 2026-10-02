#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../../AutoHotkey/Troubleshooting_Sections/GuideRequest.ahk

global Passed := 0, HostPid := 0
global Fixture := A_Temp "\F7Hub-s046-native-" DllCall("GetCurrentProcessId") "-" A_TickCount
SplitPath(A_ScriptDir, , &testsRoot)
SplitPath(testsRoot, , &projectRoot)
DirCreate(Fixture)
DirCopy(projectRoot "\AutoHotkey", Fixture "\AutoHotkey")
host := Fixture "\AutoHotkey\F7Hub.ahk"
client := Fixture "\AutoHotkey\Troubleshooting_Sections\Troubleshooting_Quick_Guide.ahk"
SendMode("Event")
SendLevel(1)
SetKeyDelay(25, 25)
try {
    Check(RunClient(client) = 0, "Cold client shows guide")
    endpoint := FindGuideEndpoint(host)
    Check(endpoint != 0, "Checkout-specific endpoint published")
    HostPid := WinGetPID(endpoint)
    hwnd := WinWait("Help Desk & Interview Guide ahk_pid " HostPid, , 3)
    Check(hwnd != 0, "Guide visible after acknowledged cold request")
    WinActivate(hwnd)
    Check(WinWaitActive(hwnd, , 3), "Guide becomes active")
    controls := FindControls(hwnd)
    notes := controls.Notes, list := controls.List, slider := controls.Slider, search := controls.Search
    Check(notes && list && slider && search, "Actual entry constructs guide controls")
    Check(ControlGetFocus(hwnd) = notes, "Actual opening focuses notes")
    Check(SendMessage(0xB0, 0, 0, notes) = 0, "Initial notes focus does not select all text")
    Send("m")
    WaitFor(() => InStr(ControlGetText(notes), "DEFINE —") = 1)
    Check(InStr(ControlGetText(notes), "DEFINE —") = 1, "Letter works immediately after opening")
    Check(RunClient(client) = 0 && WinGetPID(FindGuideEndpoint(host)) = HostPid, "Warm request reuses host")
    Check(WinExist(hwnd), "Warm show does not toggle guide off")
    WinActivate(hwnd)
    Check(WinWaitActive(hwnd, , 3), "Warm request window is active before keyboard validation")
    ControlFocus(list)
    Send("{Home}")
    Sleep(80)
    count := SendMessage(0x18B, 0, 0, list)
    Send("{Up}")
    WaitFor(() => SendMessage(0x188, 0, 0, list) = count - 1)
    Check(SendMessage(0x188, 0, 0, list) = count - 1, "Native Up wraps list first to last")
    Send("{Down}")
    WaitFor(() => SendMessage(0x188, 0, 0, list) = 0)
    Check(SendMessage(0x188, 0, 0, list) = 0, "Native Down wraps last to first once; index=" SendMessage(0x188, 0, 0, list) " active=" WinActive(hwnd) " focus=" ControlGetFocus(hwnd))
    ControlFocus(notes)
    before := SendMessage(0x400, 0, 0, slider)
    ; Native WM_KEYDOWN messages include the keyboard-repeat bit. This verifies
    ; held-key message handling without claiming a physical hardware key press.
    Loop 6
        PostMessage(0x100, 0x27, 0x40000001, notes)
    WaitFor(() => SendMessage(0x400, 0, 0, slider) = Min(100, before + 6))
    Check(SendMessage(0x400, 0, 0, slider) = Min(100, before + 6), "Native repeated Right increments opacity")
    Check(WinGetTransparent(hwnd) = Round((before + 6) * 255 / 100), "Native repeated Right updates alpha")
    ControlFocus(search)
    before := SendMessage(0x400, 0, 0, slider)
    Send("{Left}")
    Sleep(80)
    Check(SendMessage(0x400, 0, 0, slider) = before, "Search Left retains opacity")
    ControlFocus(notes)
    Send("e")
    editor := WinWait("Edit topic ahk_pid " HostPid, , 3)
    Check(editor != 0, "Editor opens through actual host")
    body := 0
    for control in WinGetControlsHwnd(editor)
        if WinGetClass(control) = "RICHEDIT50W"
            body := control
    draft := ControlGetText(body) "`r`nUNSAVED S046 NATIVE"
    ControlSetText(draft, body)
    Check(RunClient(client) = 0 && WinActive(editor), "Repeated request focuses editor")
    Check(ControlGetText(body) = draft, "Repeated request preserves unsaved content")
    ControlFocus(body)
    Send("{Left}{Right}")
    Check(SendMessage(0x400, 0, 0, slider) = before, "Editor arrows do not change guide opacity")
    Send("{Escape}")
    WaitFor(() => !WinExist(editor))
    Check(!WinExist(editor), "Editor Escape cancels normally")
    WinActivate(hwnd)
    Send("{Escape}")
    WaitFor(() => !DllCall("IsWindowVisible", "Ptr", hwnd))
    Check(!DllCall("IsWindowVisible", "Ptr", hwnd), "Main Escape hides guide")
    Send("!{F7}")
    WaitFor(() => DllCall("IsWindowVisible", "Ptr", hwnd))
    Check(DllCall("IsWindowVisible", "Ptr", hwnd), "Actual global Alt+F7 reopens")
    WaitFor(() => WinActive(hwnd) && ControlGetFocus(hwnd) = notes)
    Check(ControlGetFocus(hwnd) = notes, "Alt+F7 restores notes focus")
    message := DllCall("RegisterWindowMessageW", "Str", "F7Hub.AltF7Hub.Show.v1", "UInt")
    Check(SendMessage(message, 999, 0, endpoint) = 0, "Unknown command rejected")
    Check(SendMessage(message, 1, 999, endpoint) = 0, "Unexpected payload rejected")
    WinActivate(hwnd)
    Send("{Escape}")
    WaitFor(() => !DllCall("IsWindowVisible", "Ptr", hwnd))
    Check(GuideKeyboardFallback(HostPid, false, true) = "SHOWN", "Guarded native keyboard fallback opens hidden guide")
    ; Launch two independent clients before waiting for either to finish.
    Run('"' A_AhkPath '" /ErrorStdOut=UTF-8 "' client '" --show', , "Hide", &client1)
    handle1 := DllCall("OpenProcess", "UInt", 0x101000, "Int", false, "UInt", client1, "Ptr")
    Run('"' A_AhkPath '" /ErrorStdOut=UTF-8 "' client '" --show', , "Hide", &client2)
    handle2 := DllCall("OpenProcess", "UInt", 0x101000, "Int", false, "UInt", client2, "Ptr")
    Check(ClientExitCode(handle1) = 0 && ClientExitCode(handle2) = 0, "Concurrent clients both acknowledge success")
    Check(WinGetPID(FindGuideEndpoint(host)) = HostPid && DllCall("IsWindowVisible", "Ptr", hwnd), "Concurrent requests retain one visible host")
    FileAppend("ALL CHECKS PASSED: " Passed "`n", "*")
    exitCode := 0
} catch Error as err {
    FileAppend("FAIL Native host: " err.Message " at " err.File ":" err.Line "`n", "*")
    exitCode := 1
} finally {
    if HostPid && ProcessExist(HostPid) {
        DetectHiddenWindows(true)
        PostMessage(0x111, 65405, 0, , "ahk_pid " HostPid " ahk_class AutoHotkey")
        if ProcessWaitClose(HostPid, 3)
            ProcessClose(HostPid)
    }
    ; Only the generated fixture beneath A_Temp is eligible for recursive removal.
    if InStr(Fixture, A_Temp "\F7Hub-s046-native-") = 1
        DirDelete(Fixture, true)
}
ExitApp(exitCode)

RunClient(path) => RunWait('"' A_AhkPath '" /ErrorStdOut=UTF-8 "' path '" --show', , "Hide")
Check(condition, description) {
    global Passed
    if !condition
        throw Error(description)
    Passed++
}
WaitFor(predicate) {
    deadline := A_TickCount + 3000
    while !predicate.Call() && A_TickCount < deadline
        Sleep(20)
}
FindControls(hwnd) {
    result := {Notes:0, List:0, Slider:0, Search:0}
    for control in WinGetControlsHwnd(hwnd) {
        switch WinGetClass(control) {
            case "RICHEDIT50W": result.Notes := control
            case "ListBox": result.List := control
            case "msctls_trackbar32": result.Slider := control
            case "Edit": result.Search := control
        }
    }
    return result
}
ClientExitCode(handle) {
    if !handle
        throw Error("Could not retain concurrent client process identity")
    try {
        if DllCall("WaitForSingleObject", "Ptr", handle, "UInt", 15000) != 0
            throw Error("Concurrent client did not finish")
        code := 0
        if !DllCall("GetExitCodeProcess", "Ptr", handle, "UInt*", &code)
            throw Error("Concurrent client completion was not confirmed")
        return code
    } finally
        DllCall("CloseHandle", "Ptr", handle)
}
