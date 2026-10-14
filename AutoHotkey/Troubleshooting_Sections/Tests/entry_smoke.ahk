#Requires AutoHotkey v2.0
#SingleInstance Off
SetTitleMatchMode(3)
global Passed := 0
CoordMode("Mouse", "Screen")
MouseGetPos(&originalMouseX, &originalMouseY)
OnExit((*) => MouseMove(originalMouseX, originalMouseY, 0))
OnError((err, *) => (FileAppend("FAIL Entry: " err.Message "`n", "*"), ExitApp(1)))
if !A_Args.Length
    throw Error("Pass the launched entry-script process ID.")
targetPid := Integer(A_Args[1])
if A_Args.Length > 1 && A_Args[2] = "--check-editor" {
    activeEditor := WinExist("Edit topic ahk_pid " targetPid) || WinExist("Create topic ahk_pid " targetPid)
    FileAppend(activeEditor ? "EDITOR_ACTIVE`n" : "NO_EDITOR_ACTIVE`n", "*")
    ExitApp(activeEditor ? 2 : 0)
}
SendMode("Event")
SendLevel(1) ; Allow generated keys to trigger another AHK script's scoped hooks.
SetKeyDelay(30, 30)
if A_Args.Length > 1 {
    ; Dismiss only the native chooser owned by our optional preview process.
    previewPid := Integer(A_Args[2])
    chooser := WinExist("Colour ahk_pid " previewPid)
    if chooser
        WinClose(chooser)
    Sleep(300)
}
title := "Guide ahk_pid " targetPid
hwnd := WinWait(title, , 4)
Assert(hwnd != 0, "Entry creates the actual guide")
Assert(WinGetTransparent(hwnd) = 217, "Actual default opacity is 85%")
Assert(!(WinGetExStyle(hwnd) & 8), "Actual default pin is off")
slider := 0, list := 0, notes := 0, search := 0
for controlHwnd in WinGetControlsHwnd(hwnd) {
    className := WinGetClass(controlHwnd)
    if className = "msctls_trackbar32"
        slider := controlHwnd
    else if className = "ListBox"
        list := controlHwnd
    else if className = "RICHEDIT50W"
        notes := controlHwnd
    else if className = "Edit"
        search := controlHwnd
}
Assert(slider && list && notes && search, "Native controls loaded through entry script")
; WM_USER pointer messages are process-local. Query the visible status instead;
; the isolated in-process suite verifies actual Rich Edit character formatting.
hasDefaultSize := false
for controlHwnd in WinGetControlsHwnd(hwnd)
    if RegExMatch(ControlGetText(controlHwnd), "^Guide\s+\|\s+12 pt")
        hasDefaultSize := true
Assert(hasDefaultSize, "Actual default font is 12 points")
Assert(ControlGetStyle(list) & 0x10, "Actual sidebar draws individual topic colors")
; Slice 047 already established the current 60-100 bounds; Slice 046 was 70-100.
Assert(SendMessage(0x401, 0, 0, slider) = 60 && SendMessage(0x402, 0, 0, slider) = 100, "Actual slider has 60-100 range")
expectedCount := 0
Loop Files A_ScriptDir "\..\*.txt"
    expectedCount++
Assert(SendMessage(0x18B, 0, 0, list) = expectedCount, "Actual library loads all current active topics")
; Match the F7 native harness's foreground protection: hover activation must
; remain over the owned window during keyboard checks. Restore on every exit.
WinGetPos(&guideX, &guideY, &guideWidth, &guideHeight, hwnd)
MouseMove(guideX + guideWidth // 2, guideY + guideHeight // 2, 0)
WinActivate(hwnd)
if !WinActive(hwnd) {
    ; A separately launched observer may lack Windows foreground authority.
    ; Acquire it with a transient test-owned window before activating the host.
    driver := Gui("+ToolWindow", "S003 native test driver")
    driver.Show("x" guideX " y" guideY " w240 h100")
    Assert(WinWaitActive(driver.Hwnd, , 3), "Entry driver is foreground-ready")
    WinActivate(hwnd)
    driver.Destroy()
}
Assert(WinWaitActive(hwnd, , 3), "Entry owned guide is foreground-ready")
ControlFocus(notes)
Assert(ControlGetFocus(hwnd) = notes, "Entry notes input is ready before Ctrl+F")
Send("^f")
Assert(WaitFor(() => ControlGetFocus(hwnd) = search), "Entry Ctrl+F focuses search; actual=" ControlGetFocus(hwnd) " expected=" search)
before := ControlGetText(notes)
Send("^{PgDn}")
Assert(WaitFor(() => ControlGetText(notes) != before), "Entry Ctrl+PageDown changes topic")
ControlFocus(notes) ; Topic letters are scoped to notes/list, not Search.
Assert(ControlGetFocus(hwnd) = notes, "Entry notes focus is ready for topic letters")
ControlFocus(notes)
Send("m")
Assert(WaitFor(() => InStr(ControlGetText(notes), "DEFINE —") = 1), "Entry letter shortcut opens methodology")
Send("{Escape}")
DetectHiddenWindows(false)
Assert(WaitFor(() => !WinExist(title)), "Entry Esc hides guide")
DetectHiddenWindows(true)
Send("!{F7}")
DetectHiddenWindows(false)
Assert(WaitFor(() => WinExist(title)), "Global Alt+F7 reopens hidden guide")
FileAppend("PASS Entry launch, defaults, colored sidebar, topic loading, keyboard shortcuts, global Alt+F7 (" Passed " checks)`n", "*")
ExitApp()
Assert(condition, label) {
    global Passed
    if !condition
        throw Error(label)
    Passed++
}

WaitFor(predicate) {
    deadline := A_TickCount + 3000
    while A_TickCount < deadline {
        if predicate.Call()
            return true
        Sleep(20)
    }
    return false
}
