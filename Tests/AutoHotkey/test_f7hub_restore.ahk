#Requires AutoHotkey v2.0
#Include ..\..\AutoHotkey\Launchers\F7HubLauncher.ahk
#Include ..\..\AutoHotkey\Helpers\MagneticWindowFollower.ahk
#Include ..\..\AutoHotkey\Hotkeys\F7HotkeyController.ahk

; External supervisor supplies a unique data-free fixture root/title, runtime,
; known fixture PID (0 only for cold launch), and a NEW result pathname.
; No global hotkey registration, injected keys, production database or host exit.
if A_Args.Length != 6
    ExitApp 2
fixtureRoot := A_Args[1]
python := A_Args[2]
fixtureTitle := A_Args[3]
mode := A_Args[4]
expectedPid := Integer(A_Args[5])
resultPath := A_Args[6]
if !InStr(fixtureTitle, "F7Hub Restore Fixture ") || FileExist(resultPath)
    ExitApp 3

class FixtureLauncher extends F7HubLauncher {
    IsF7HubWindow(hwnd) {
        global fixtureTitle, expectedPid
        try {
            return hwnd && WinExist(hwnd) && WinGetTitle(hwnd) == fixtureTitle
                && (!expectedPid || WinGetPID(hwnd) == expectedPid)
                && RegExMatch(WinGetClass(hwnd), "^Qt.*QWindowIcon$")
                && RegExMatch(WinGetProcessName(hwnd), "i)^pythonw?\.exe$")
        } catch Error {
            return false
        }
    }
}

launcher := FixtureLauncher(fixtureRoot, , python)
follower := MagneticWindowFollower(ObjBindMethod(launcher, "IsF7HubWindow"))
held := true
controller := F7HotkeyController(launcher, follower, (*) => held)
sentinel := 0
exitCode := 0
try {
    if mode == "tap" {
        controller.OnDown()
        controller.OnUp()
        hwnd := launcher.FindWindow()
        if !hwnd || !WinActive(hwnd)
            throw Error("TAP did not focus the owned fixture")
    } else if mode == "close" {
        hwnd := launcher.FindWindow()
        if !hwnd || !launcher.IsF7HubWindow(hwnd)
            throw Error("Native X target is not the owned fixture")
        WinClose hwnd
    } else if mode == "hold" {
        CoordMode "Mouse", "Screen"
        MouseGetPos &cursorX, &cursorY
        sentinel := Gui(, "F7 Restore Test Focus Sentinel")
        sentinel.AddText(, "Synthetic HOLD focus target")
        sentinel.Show("x" (cursorX - 70) " y" (cursorY - 30) " w140 h60")
        WinActivate sentinel.Hwnd
        if !WinWaitActive(sentinel.Hwnd, , 2)
            throw Error("Owned HOLD focus sentinel did not activate")
        controller.OnDown()
        controller.BeginHold()
        Sleep 120
        hwnd := launcher.FindWindow()
        if controller.State != "HOLDING" || !follower.Running || follower.LastError != ""
            throw Error("HOLD/follower did not remain active")
        if !WinActive(sentinel.Hwnd)
            throw Error("HOLD stole foreground activation")
        if WinGetMinMax(hwnd) != 0
            throw Error("HOLD did not normalize the fixture")
        controller.OnDown()
        held := false
        controller.OnUp()
        if follower.Running || controller.State != "IDLE"
            throw Error("HOLD release did not stop the follower")
    } else {
        throw Error("Unknown bounded fixture mode")
    }
    FileAppend "PASS " mode " hwnd=" hwnd " pid=" WinGetPID(hwnd) "`n", resultPath, "UTF-8"
} catch Error as failure {
    FileAppend "FAIL " failure.Message "`n", resultPath, "UTF-8"
    exitCode := 1
} finally {
    held := false
    controller.OnUp()
    follower.Stop()
    if IsObject(sentinel)
        sentinel.Destroy()
}
ExitApp exitCode
