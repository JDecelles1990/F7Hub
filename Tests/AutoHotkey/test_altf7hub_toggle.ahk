#Requires AutoHotkey v2.0
#SingleInstance Off
; Focused regression in an external runtime copy supplied by the supervisor.
; Exercises the unchanged shared host's actual global Alt+F7 hook.
if A_Args.Length != 1
    ExitApp 2
root := A_Args[1], hostPid := 0, passed := 0, exitCode := 0
SendMode "Event"
SendLevel 1
SetKeyDelay 25, 25
try {
    Run('"' A_AhkPath '" /ErrorStdOut "' root '\AutoHotkey\F7Hub.ahk"', root, , &hostPid)
    DetectHiddenWindows true
    if !WinWait(root "\AutoHotkey\F7Hub.ahk ahk_class AutoHotkey", , 5)
        throw Error("Shared host startup timeout")
    DetectHiddenWindows false
    Loop 3 {
        SendEvent "!{F7}"
        hwnd := WinWait("Help Desk & Interview Guide ahk_pid " hostPid, , 3)
        if !hwnd || !WinWaitActive(hwnd, , 2)
            throw Error("Alt+F7 did not show/focus the owned guide")
        passed++
        currentPid := WinGetPID(hwnd)
        SendEvent "!{F7}"
        if !WinWaitClose("Help Desk & Interview Guide ahk_pid " hostPid, , 3)
            throw Error("Alt+F7 did not hide the owned guide")
        DetectHiddenWindows true
        if !WinExist(hwnd) || WinGetPID(hwnd) != currentPid
            throw Error("Toggle lost the retained guide")
        DetectHiddenWindows false
        passed += 2
    }
    FileAppend("PASS assertions=" passed " actual Alt+F7 show/focus/hide; retained shared host`n", "*")
} catch Error as err {
    FileAppend("FAIL " err.Message " assertions=" passed "`n", "*")
    exitCode := 1
} finally {
    SendEvent "{Blind}{F7 up}{LAlt up}{RAlt up}"
    if hostPid && ProcessExist(hostPid) {
        ProcessClose hostPid
        ProcessWaitClose(hostPid, 2)
        if ProcessExist(hostPid)
            exitCode := 1
    }
}
ExitApp exitCode
