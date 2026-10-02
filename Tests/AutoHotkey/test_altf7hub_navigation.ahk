#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../../AutoHotkey/Troubleshooting_Sections/GuideRequest.ahk
#Include ../../AutoHotkey/Troubleshooting_Sections/GuideCore.ahk

; Exercise the actual shared host, scoped hotkeys and WM_KEYDOWN monitor.
; No production navigation function is called by this harness.
global Passed := 0, HostPid := 0
global Fixture := A_Temp "\F7Hub-s046-navigation-" DllCall("GetCurrentProcessId") "-" A_TickCount
SplitPath(A_ScriptDir, , &testsRoot)
SplitPath(testsRoot, , &projectRoot)
DirCreate(Fixture)
DirCopy(projectRoot "\AutoHotkey", Fixture "\AutoHotkey")
host := Fixture "\AutoHotkey\F7Hub.ahk"
client := Fixture "\AutoHotkey\Troubleshooting_Sections\Troubleshooting_Quick_Guide.ahk"
DataRoot := Fixture "\AutoHotkey\Troubleshooting_Sections"
LoadTopics() ; Read-only expectations; the GUI under test is in another process.
SendMode("Event")
SendLevel(1)
SetKeyDelay(20, 10)
try {
    Check(RunWait('"' A_AhkPath '" /ErrorStdOut=UTF-8 "' client '" --show', , "Hide") = 0, "Host starts and acknowledges show")
    endpoint := FindGuideEndpoint(host)
    HostPid := WinGetPID(endpoint)
    hwnd := WinWait("Help Desk & Interview Guide ahk_pid " HostPid, , 3)
    WinActivate(hwnd)
    Check(WinWaitActive(hwnd, , 3), "Native guide foreground ready")
    notes := 0, list := 0, search := 0
    for control in WinGetControlsHwnd(hwnd) {
        switch WinGetClass(control) {
            case "RICHEDIT50W": notes := control
            case "ListBox": list := control
            case "Edit": search := control
        }
    }
    count := SendMessage(0x18B, 0, 0, list)
    Check(count > 14 && notes && list && search, "Enough topics and actual native controls")

    SelectFirst(hwnd, list, notes)
    Send("{Down}")
    AwaitIndex(list, 1)
    Record("single Down", 1, 1, Index(list), hwnd, list, notes)

    SelectFirst(hwnd, list, notes)
    Loop 7 {
        Send("{Down}")
        Sleep(100)
    }
    AwaitIndex(list, 7)
    Record("rapid discrete Down", 7, 7, Index(list), hwnd, list, notes)
    AssertReleased(list, 7, "discrete Down release")
    Loop 7 {
        Send("{Up}")
        Sleep(100)
    }
    AwaitIndex(list, 0)
    Record("rapid discrete Up", 7, 7, Mod(7 - Index(list) + count, count), hwnd, list, notes)
    AssertReleased(list, 0, "discrete Up release")

    SelectFirst(hwnd, list, notes)
    Loop 7 {
        Send("{Down down}")
        Sleep(100)
    }
    Send("{Down up}")
    AwaitIndex(list, 7)
    Record("held hotkey Down", 7, 7, Index(list), hwnd, list, notes)
    AssertReleased(list, 7, "held hotkey Down release")
    Loop 7 {
        Send("{Up down}")
        Sleep(100)
    }
    Send("{Up up}")
    AwaitIndex(list, 0)
    Record("held hotkey Up", 7, 7, Mod(7 - Index(list) + count, count), hwnd, list, notes)
    AssertReleased(list, 0, "held hotkey Up release")

    SelectFirst(hwnd, list, notes)
    NativeRepeat(0x28, 0x50, 7, notes)
    PostMessage(0x101, 0x28, 0xC1500001, notes)
    AwaitIndex(list, 7)
    Record("native repeat Down", 7, 7, Index(list), hwnd, list, notes)
    AssertReleased(list, 7, "native Down keyup")

    NativeRepeat(0x26, 0x48, 7, notes)
    PostMessage(0x101, 0x26, 0xC1480001, notes)
    AwaitIndex(list, 0)
    Record("native repeat Up", 7, 7, Mod(7 - Index(list) + count, count), hwnd, list, notes)
    AssertReleased(list, 0, "native Up keyup")

    SelectFirst(hwnd, list, notes)
    Send("{Up}")
    AwaitIndex(list, count - 1)
    Record("first boundary wraps Up", 1, 1, Index(list) = count - 1 ? 1 : 0, hwnd, list, notes)
    Send("{Down}")
    AwaitIndex(list, 0)
    Record("last boundary wraps Down", 1, 1, Index(list) = 0 ? 1 : 0, hwnd, list, notes)
    NativeRepeat(0x26, 0x48, 7, notes)
    AwaitIndex(list, count - 7)
    Record("repeated Up across first boundary", 7, 7, Mod(count - Index(list), count), hwnd, list, notes)
    NativeRepeat(0x28, 0x50, 7, notes)
    AwaitIndex(list, 0)
    Record("repeated Down across last boundary", 7, 7, Mod(count - (count - 7) + Index(list), count), hwnd, list, notes)

    SelectFirst(hwnd, list, notes)
    NativeRepeat(0x28, 0x50, 7, notes, 35)
    NativeRepeat(0x26, 0x48, 3, notes, 35)
    PostMessage(0x101, 0x28, 0xC1500001, notes)
    PostMessage(0x101, 0x26, 0xC1480001, notes)
    AwaitIndex(list, 4)
    Record("direction reversal: 7 Down then 3 Up", 10, 4, Index(list), hwnd, list, notes)
    AssertReleased(list, 4, "direction reversal release")

    SelectFirst(hwnd, list, notes)
    NativeRepeat(0x28, 0x50, 3, notes, 35)
    ControlFocus(search)
    NativeRepeat(0x28, 0x50, 4, notes, 35)
    AwaitIndex(list, 3)
    Check(Index(list) = 3, "Mid-sequence focus loss accepts first three and rejects next four")
    AssertReleased(list, 3, "focus-loss release")
    CheckSynchronized(hwnd, list, notes)

    before := Index(list)
    ControlFocus(search)
    NativeRepeat(0x28, 0x50, 7, notes, 35)
    Sleep(100)
    Check(Index(list) = before, "Focus change rejects subsequent repeat events")
    ControlFocus(notes)
    Send("^{Down}")
    Sleep(100)
    Check(Index(list) = before, "Modified Down retains native behavior")

    ControlSetText("fortigate", search)
    WaitFor(() => SendMessage(0x18B, 0, 0, list) = 1 && Index(list) = 0)
    ControlFocus(notes)
    NativeRepeat(0x28, 0x50, 7, notes, 35)
    Check(Index(list) = 0, "Single-topic repeat remains on its sole topic")
    CheckSynchronized(hwnd, list, notes)
    ControlSetText("", search)
    WaitFor(() => SendMessage(0x18B, 0, 0, list) = count && Index(list) >= 0)
    CheckSynchronized(hwnd, list, notes)
    ControlFocus(notes)
    NativeRepeat(0x28, 0x50, 7, notes, 35)
    ControlSetText("fortigate", search)
    WaitFor(() => SendMessage(0x18B, 0, 0, list) = 1 && Index(list) = 0)
    Check(Index(list) = 0, "New filter invalidates older navigation selection")
    CheckSynchronized(hwnd, list, notes)
    ControlSetText("", search)
    WaitFor(() => SendMessage(0x18B, 0, 0, list) = count && Index(list) >= 0)
    CheckSynchronized(hwnd, list, notes)
    ControlFocus(notes)
    NativeRepeat(0x28, 0x50, 7, notes, 35)
    PostMessage(0x101, 0x28, 0xC1500001, notes)
    ControlSetText("no-navigation-test-match", search)
    WaitFor(() => SendMessage(0x18B, 0, 0, list) = 0 && InStr(ControlGetText(notes), "No matching topics"))
    AssertReleased(list, -1, "Empty filter cancels older paint selection")
    NativeRepeat(0x26, 0x48, 7, notes, 35)
    Check(Index(list) = -1 && InStr(ControlGetText(notes), "No matching topics"), "Empty-result repeat remains a no-op")
    FileAppend("ALL CHECKS PASSED: " Passed "`n", "*")
    code := 0
} catch Error as err {
    FileAppend("FAIL Navigation: " err.Message " at " err.File ":" err.Line "`n", "*")
    code := 1
} finally {
    Send("{Down up}{Up up}{Ctrl up}")
    if HostPid && ProcessExist(HostPid) {
        DetectHiddenWindows(true)
        PostMessage(0x111, 65405, 0, , "ahk_pid " HostPid " ahk_class AutoHotkey")
        if ProcessWaitClose(HostPid, 3)
            ProcessClose(HostPid)
    }
    if InStr(Fixture, A_Temp "\F7Hub-s046-navigation-") = 1
        DirDelete(Fixture, true)
}
ExitApp(code)

Check(value, label) {
    global Passed
    if !value
        throw Error(label)
    Passed++
    FileAppend("PASS " label "`n", "*")
}
WaitFor(predicate) {
    deadline := A_TickCount + 3000
    while !predicate.Call() && A_TickCount < deadline
        Sleep(20)
    if !predicate.Call()
        throw Error("Native state readiness timed out")
}
Index(list) => SendMessage(0x188, 0, 0, list)
AwaitIndex(list, expected) {
    try WaitFor(() => Index(list) = expected)
    catch Error {
        parent := DllCall("GetParent", "Ptr", list, "Ptr")
        FileAppend("STATE expected_index=" expected " observed_index=" Index(list)
            " foreground=" WinActive("ahk_id " parent) " focus=" ControlGetFocus(parent) "`n", "*")
        throw
    }
}
SelectFirst(hwnd, list, notes) {
    WinActivate(hwnd)
    Check(WinWaitActive(hwnd, , 3), "Guide foreground before sequence")
    ControlFocus(list)
    Send("{Home}")
    AwaitIndex(list, 0)
    Check(Index(list) = 0, "Sequence begins at first topic")
    CheckSynchronized(hwnd, list, notes)
    ControlFocus(notes)
}
NativeRepeat(vk, scan, count, target, cadence := 100) {
    Loop count {
        PostMessage(0x100, vk, (A_Index = 1 ? 0x01000001 : 0x41000001) | (scan << 16), target)
        Sleep(cadence)
    }
}
Record(label, inputs, expected, observed, hwnd, list, notes) {
    FileAppend("COUNT " label ": inputs=" inputs " expected=" expected " observed=" observed " final_index=" Index(list) "`n", "*")
    Check(observed = expected, label " expected=" expected " observed=" observed)
    CheckSynchronized(hwnd, list, notes)
}
AssertReleased(list, expected, label) {
    Check(Index(list) = expected, label " selection settled before wait")
    Sleep(350)
    Check(Index(list) = expected, label " has no trailing navigation")
}
CheckSynchronized(hwnd, list, notes) {
    search := 0
    for control in WinGetControlsHwnd(hwnd)
        if WinGetClass(control) = "Edit"
            search := control
    query := StrLower(Trim(ControlGetText(search))), ordered := ""
    for id, item in Topics
        if query = "" || InStr(StrLower(item.Title " " item.Body " " id " " item.Shortcut), query)
            ordered .= item.Title "`t" id "`n"
    rows := StrSplit(Trim(Sort(ordered), "`n"), "`n")
    pair := StrSplit(rows[Index(list) + 1], "`t"), expected := Topics[pair[-1]]
    matches() {
        titleFound := false
        for control in WinGetControlsHwnd(hwnd)
            if WinGetClass(control) = "Static" && ControlGetText(control) = expected.Title
                titleFound := true
        ; Formatting disables native redraw (and WS_VISIBLE) until complete.
        ; Body text alone becomes readable before the filter handler is ready.
        return DllCall("IsWindowVisible", "Ptr", notes) && titleFound
            && NormalizeText(ControlGetText(notes)) = expected.Body
    }
    WaitFor(matches)
    Check(matches(), "Selection/title/exact body synchronized: " expected.Id)
}
