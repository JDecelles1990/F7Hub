#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../../AutoHotkey/Troubleshooting_Sections/GuideRequest.ahk

global Passed := 0, HostPid := 0
global Fixture := A_Temp "\F7Hub-s046-native-" DllCall("GetCurrentProcessId") "-" A_TickCount
SplitPath(A_ScriptDir, , &testsRoot)
SplitPath(testsRoot, , &projectRoot)
DirCreate(Fixture)
; Copy runtime inputs only; historical evidence/backups are not fixtures.
Loop Files projectRoot "\AutoHotkey\*", "FR" {
    relative := SubStr(A_LoopFileFullPath, StrLen(projectRoot "\AutoHotkey\") + 1)
    if relative = "Troubleshooting_Sections\GuideSettings.ini" || InStr(relative, "Troubleshooting_Sections\Backups\") = 1 || InStr(relative, "Troubleshooting_Sections\Tests\Evidence\") = 1
        continue
    target := Fixture "\AutoHotkey\" relative
    SplitPath(target, , &folder)
    DirCreate(folder)
    FileCopy(A_LoopFileFullPath, target)
}
if EnvGet("S047_TRACE") = "1" {
    corePath := Fixture "\AutoHotkey\Troubleshooting_Sections\GuideCore.ahk"
    core := StrReplace(FileRead(corePath, "UTF-8"), "`r`n", "`n")
    core := StrReplace(core, '    FormattingBusy := true', '    FileAppend("TRACE format-begin id=" topicId " critical=" A_IsCritical " tick=" A_TickCount "``n", DataRoot "\trace.log")' "`n" '    FormattingBusy := true')
    core := StrReplace(core, '        FormattingBusy := false', '        FileAppend("TRACE format-end id=" topicId " visible=" DllCall("IsWindowVisible", "Ptr", control.Hwnd) " tick=" A_TickCount "``n", DataRoot "\trace.log")' "`n" '        FormattingBusy := false')
    core := StrReplace(core, '    NavigationRendering := true', '    FileAppend("TRACE render-begin current=" CurrentId " tick=" A_TickCount "``n", DataRoot "\trace.log")' "`n" '    NavigationRendering := true')
    core := StrReplace(core, '        NavigationRendering := false', '        FileAppend("TRACE render-end current=" CurrentId " tick=" A_TickCount "``n", DataRoot "\trace.log")' "`n" '        NavigationRendering := false')
    FileDelete(corePath)
    FileAppend(core, corePath, "UTF-8")
}
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
    FileAppend("OWNED_HOST pid=" HostPid " fixture=" Fixture "`n", "*")
    hwnd := WinWait("Help Desk & Interview Guide ahk_pid " HostPid, , 3)
    Check(hwnd != 0, "Guide visible after acknowledged cold request")
    WinActivate(hwnd)
    Check(WinWaitActive(hwnd, , 3), "Guide becomes active")
    controls := FindControls(hwnd)
    notes := controls.Notes, list := controls.List, slider := controls.Slider, search := controls.Search
    Check(notes && list && slider && search, "Actual entry constructs guide controls")
    Check(ControlGetFocus(hwnd) = notes, "Actual opening focuses notes")
    Check(SendMessage(0xB0, 0, 0, notes) = 0, "Initial notes focus does not select all text")
    ; Exercise the actual scoped Ctrl+F hotkey and native text caret.
    ControlSetText("out", search)
    ControlFocus(notes)
    Send("^f")
    WaitFor(() => ControlGetFocus(hwnd) = search)
    selection := SendMessage(0xB0, 0, 0, search)
    Check((selection & 0xFFFF) = 3 && (selection >> 16) = 3, "Ctrl+F places a collapsed caret after the existing search")
    Send("look")
    WaitFor(() => ControlGetText(search) = "outlook")
    Check(ControlGetText(search) = "outlook", "Ctrl+F typing goes into Search")
    WaitFor(() => HasTopicTitle(hwnd, "OUTLOOK / EMAIL") && SendMessage(0x18B, 0, 0, list) = 1 && DllCall("IsWindowVisible", "Ptr", notes))
    Check(HasTopicTitle(hwnd, "OUTLOOK / EMAIL"), "Search filter is rendered before hiding sidebar")
    hide := 0
    for control in WinGetControlsHwnd(hwnd)
        if ControlGetText(control) = "Hide topics"
            hide := control
    Check(hide && DllCall("IsWindowVisible", "Ptr", hide), "Hide topics button is ready")
    ; Native button message avoids ControlClick limitations on AHK GUI controls.
    SendMessage(0xF5, 0, 0, hide)
    WaitFor(() => !DllCall("IsWindowVisible", "Ptr", search))
    ControlFocus(notes)
    Send("^f")
    WaitFor(() => ControlGetFocus(hwnd) = search && DllCall("IsWindowVisible", "Ptr", search))
    Check(ControlGetText(search) = "outlook", "Hidden sidebar Ctrl+F restores Search without clearing query")
    ; Bare group keys clear filters and follow explicit order in the live host.
    ControlFocus(notes)
    for pair in [["a","APPLICATIONS / CRASHES"],["a","AZURE VM"],["a","APPLICATIONS / CRASHES"],
        ["s","SHAREPOINT / FILE ACCESS"],["s","PHISHING / SECURITY TRIAGE"],
        ["h","HARDWARE / PERIPHERALS"],["h","POWER / STARTUP / DISPLAY"],
        ["w","WINDOWS 365 / CLOUD PC"],["w","WINDOWS SERVICES"],["w","WINDOWS 365 / CLOUD PC"],
        ["1","INTERVIEW / TECHNICAL ANSWERS"],["2","INTERVIEW / BEHAVIORAL ANSWERS"],
        ["3","INTERVIEW / STAR STORY PROMPTS"],["4","INTERVIEW / PERSONAL MOTIVATION"],
        ["5","INTERVIEW / QUESTIONS TO ASK"]] {
        ControlFocus(notes)
        Check(ControlGetFocus(hwnd) = notes, "Notes focused before key " pair[1])
        vk := Ord(StrUpper(pair[1]))
        scan := DllCall("MapVirtualKeyW", "UInt", vk, "UInt", 0, "UInt")
        PostMessage(0x100, vk, 1 | (scan << 16), notes)
        PostMessage(0x101, vk, 0xC0000001 | (scan << 16), notes)
        WaitFor(() => HasTopicTitle(hwnd, pair[2]) && DllCall("IsWindowVisible", "Ptr", notes))
        FileAppend("STATE key=" pair[1] " focus=" ControlGetFocus(hwnd) " notes=" notes " query=" ControlGetText(search) " title=" NativeTitle(hwnd) " ctrl=" GetKeyState("Ctrl") "`n", "*")
        Check(HasTopicTitle(hwnd, pair[2]), "Native key " pair[1] " selects " pair[2])
    }
    Check(ControlGetText(search) = "", "Topic shortcut clears the filter")
    ; Search and buttons retain native key input.
    ControlFocus(search)
    Send("a1")
    WaitFor(() => ControlGetText(search) = "a1")
    Check(ControlGetText(search) = "a1", "Search letters and numbers remain text input")
    ControlSetText("no-match-s047-capture", search)
    WaitFor(() => SendMessage(0x18B, 0, 0, list) = 0 && DllCall("IsWindowVisible", "Ptr", notes))
    Check(SendMessage(0x18B, 0, 0, list) = 0, "Search filter completes before reset")
    ControlSetText("", search)
    WaitFor(() => SendMessage(0x18B, 0, 0, list) > 0 && HasTopicTitle(hwnd, "ACCOUNT ACCESS / LOCKOUT") && DllCall("IsWindowVisible", "Ptr", notes))
    ControlFocus(notes)
    Check(ControlGetFocus(hwnd) = notes, "Notes focus ready after filter reset")
    Send("o")
    WaitFor(() => HasTopicTitle(hwnd, "OUTLOOK / EMAIL") && DllCall("IsWindowVisible", "Ptr", notes))
    Check(HasTopicTitle(hwnd, "OUTLOOK / EMAIL"), "Outlook visible before native capture")
    WinGetPos(&x, &y, &width, &height, hwnd)
    FileAppend("NATIVE width=" width " height=" height " ready=visible-Outlook-title-and-notes dpi=" DllCall("GetDpiForWindow", "Ptr", hwnd) "`n", "*")
    captureScript := EnvGet("S047_CAPTURE_SCRIPT")
    captureOutput := EnvGet("S047_CAPTURE_OUTPUT")
    if captureScript != "" && captureOutput != ""
        Check(RunWait('powershell.exe -NoProfile -File "' captureScript '" -WindowHandle ' hwnd ' -OutputPath "' captureOutput '"', , "Hide") = 0, "Native Outlook capture saved")
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
    tracePath := Fixture "\AutoHotkey\Troubleshooting_Sections\trace.log"
    if FileExist(tracePath)
        FileAppend(FileRead(tracePath), "*")
    if EnvGet("S047_TRACE") = "1" && IsSet(hwnd) && WinExist(hwnd)
        RunWait('powershell.exe -NoProfile -File "' EnvGet("S047_CAPTURE_SCRIPT") '" -WindowHandle ' hwnd ' -OutputPath "' EnvGet("S047_CAPTURE_OUTPUT") '"', , "Hide")
    FileAppend("FAIL Native host: " err.Message " at " err.File ":" err.Line "`n", "*")
    exitCode := 1
} finally {
    Send("{Ctrl up}{Alt up}{Shift up}{LWin up}{RWin up}{Up up}{Down up}{Left up}{Right up}")
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
    FileAppend("PASS " description "`n", "*")
}
WaitFor(predicate) {
    deadline := A_TickCount + 8000
    while !predicate.Call() && A_TickCount < deadline
        Sleep(20)
    if !predicate.Call() {
        FileAppend("TIMEOUT foreground=" WinActive(hwnd) " focus=" ControlGetFocus(hwnd) " query=" ControlGetText(search) " title=" NativeTitle(hwnd) "`n", "*")
        throw Error("Native observable readiness timed out")
    }
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

HasTopicTitle(hwnd, title) {
    for control in WinGetControlsHwnd(hwnd)
        if WinGetClass(control) = "Static" && ControlGetText(control) = title
            return true
    return false
}

NativeTitle(hwnd) {
    value := ""
    for control in WinGetControlsHwnd(hwnd)
        if WinGetClass(control) = "Static"
            value .= ControlGetText(control) " | "
    return value
}
