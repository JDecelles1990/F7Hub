#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../../AutoHotkey/Helpers/ClipboardHotkeyPolicy.ahk
#Include ../../AutoHotkey/Hotkeys/ClipboardPressCycleController.ahk

; Observe only already-running visible Office windows. Never launch a document,
; read window text, send a chord, or close a user-owned application.
policy := ClipboardHotkeyPolicy(), original := WinExist("A"), count := 0
keys := Map("F23", true, "Ctrl", true, "Alt", true, "Shift", false, "LWin", false, "RWin", false)
exitCode := 0
try {
    for name in ["WINWORD.EXE", "EXCEL.EXE", "OUTLOOK.EXE", "OLK.EXE", "POWERPNT.EXE"] {
        hwnd := 0
        for candidate in WinGetList("ahk_exe " name) {
            if DllCall("IsWindowVisible", "Ptr", candidate) {
                hwnd := candidate
                break
            }
        }
        if !hwnd {
            FileAppend("NOT RUN " name " - NO SAFE EXISTING WINDOW; installation availability reported separately`n", "*")
            continue
        }
        wasMinimized := WinGetMinMax(hwnd) == -1
        try {
            WinActivate hwnd
            if !WinWaitActive(hwnd, , 2)
                throw Error("Office foreground not confirmed: " name)
            context := policy.ReadForeground()
            if !IsObject(context) || context.Hwnd != hwnd || StrUpper(context.Exe) != name
                throw Error("Office executable identity mismatch: " name)
            for action in ["clipboard.capture_selection", "clipboard.paste_active"] {
                keys["F23"] := true, keys["Ctrl"] := true, keys["Alt"] := true
                controller := ClipboardPressCycleController(action, "F23", policy, RejectCallback, , (key) => keys[key])
                if controller.IsEligible() || controller.OnDown()
                    throw Error("Office was eligible: " name)
                keys["F23"] := false, keys["Ctrl"] := false, keys["Alt"] := false
                if controller.OnRelease() || controller.State != "IDLE"
                    throw Error("Office dispatched or did not clean up: " name)
            }
        } finally {
            if wasMinimized && WinExist(hwnd)
                WinMinimize hwnd
        }
        count++
        FileAppend("PASS " name " foreground identity; both fixture actions blocked; no native keys sent`n", "*")
    }
} catch Error as err {
    FileAppend("FAIL " err.Message "`n", "*")
    exitCode := 1
} finally {
    if original && WinExist(original)
        WinActivate original
}
if count == 0 && exitCode == 0
    exitCode := 2
FileAppend((exitCode == 0 ? "PASS" : exitCode == 2 ? "NOT RUN" : "FAIL") " accepted_applications=" count "`n", "*")
ExitApp exitCode
RejectCallback(*) {
    throw Error("Office fixture callback must not execute")
}
