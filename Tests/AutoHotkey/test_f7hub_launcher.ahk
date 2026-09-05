#Requires AutoHotkey v2.0
#Include ..\..\AutoHotkey\Launchers\F7HubLauncher.ahk

; Run with a NEW isolated database path. Refuse to interfere with a user's app.
SplitPath A_ScriptDir, , &testsRoot
SplitPath testsRoot, , &projectRoot
if A_Args.Length != 1 || FileExist(A_Args[1]) {
    FileAppend "BLOCKED: supply a new isolated database path.`n", "*"
    ExitApp 2
}
launcher := F7HubLauncher(projectRoot, A_Args[1])
DetectHiddenWindows true
existingShortcut := WinExist(projectRoot "\AutoHotkey\F7Hub.ahk ahk_class AutoHotkey")
DetectHiddenWindows false
if existingShortcut {
    FileAppend "BLOCKED: exit the F7Hub shortcut from its tray menu before this live test.`n", "*"
    ExitApp 2
}
if launcher.FindWindow() {
    FileAppend "BLOCKED: close F7Hub before the live launcher test.`n", "*"
    ExitApp 2
}
hwnd := 0
shortcutPid := 0
testExitCode := 0
testPid := DllCall("GetCurrentProcessId")
try {
    missing := F7HubLauncher(A_Temp "\F7Hub-missing-" testPid)
    ExpectError(() => missing.LaunchOrFocus(), "not ready")

    pending := F7HubLauncher(projectRoot)
    pending.PendingPid := testPid
    ExpectError(() => pending.LaunchOrFocus(0), "No second instance")
    Assert(pending.PendingPid == testPid, "Timeout lost the pending process")
    ExpectError(() => pending.LaunchOrFocus(0), "No second instance")

    previousPath := EnvGet("PYTHONPATH")
    hwnd := launcher.LaunchOrFocus()
    Assert(WinActive(hwnd), "Cold launch did not focus F7Hub")
    Assert(EnvGet("PYTHONPATH") == previousPath, "Launch changed the parent environment")
    Assert(FileExist(A_Args[1]), "The isolated database was not created")

    ; Same-window identity must survive repeated calls, minimization and a
    ; decoy window whose title contains the project name.
    decoy := Gui(, "F7Hub documentation")
    decoy.Show("w240 h100")
    Assert(launcher.LaunchOrFocus() == hwnd, "Focus created another window")
    WinMinimize hwnd
    Assert(launcher.LaunchOrFocus() == hwnd, "Restore created another window")
    Assert(WinGetMinMax(hwnd) != -1 && WinActive(hwnd), "Minimized window was not restored and focused")
    Loop 5
        Assert(launcher.LaunchOrFocus() == hwnd, "Repeated launch duplicated the app")

    Run '"' A_AhkPath '" /ErrorStdOut "' projectRoot '\AutoHotkey\F7Hub.ahk"', projectRoot, , &shortcutPid
    DetectHiddenWindows true
    Assert(WinWait(projectRoot "\AutoHotkey\F7Hub.ahk ahk_class AutoHotkey", , 5), "Shortcut did not start")
    DetectHiddenWindows false
    WinActivate decoy.Hwnd
    SendEvent "{F7}"
    Assert(WinWaitActive(hwnd, , 5), "Global F7 did not focus the existing app")
    WinMinimize hwnd
    SendEvent "{F7}"
    Assert(WinWaitActive(hwnd, , 5), "Global F7 did not restore the minimized app")
    Run '"' A_AhkPath '" /ErrorStdOut "' projectRoot '\AutoHotkey\F7Hub.ahk"', projectRoot, , &duplicatePid
    Assert(!ProcessWaitClose(duplicatePid, 5), "Duplicate shortcut did not exit")
    Assert(ProcessExist(shortcutPid), "Original shortcut exited")
    decoy.Destroy()
    FileAppend "PASS: missing runtime, timeout/retry guard, cold launch, environment restoration, focus, minimized restoration, repeated calls, decoy rejection, global F7, single shortcut instance.`n", "*"
} catch Error as testError {
    FileAppend "FAIL: " testError.Message "`n", "*"
    testExitCode := 1
} finally {
    if shortcutPid && ProcessExist(shortcutPid)
        ProcessClose shortcutPid
    if hwnd && WinExist(hwnd) {
        WinClose hwnd
        WinWaitClose hwnd, , 5
    }
}
ExitApp testExitCode

Assert(condition, message) {
    if !condition
        throw Error(message)
}

ExpectError(action, expectedText) {
    try action()
    catch Error as testError {
        Assert(InStr(testError.Message, expectedText), "Unexpected error: " testError.Message)
        return
    }
    throw Error("Expected error containing: " expectedText)
}
