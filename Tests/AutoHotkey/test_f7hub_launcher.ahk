#Requires AutoHotkey v2.0
#Include ..\..\AutoHotkey\Launchers\F7HubLauncher.ahk
#Include ..\..\AutoHotkey\Helpers\MagneticWindowFollower.ahk
#Include ..\..\AutoHotkey\Hotkeys\F7HotkeyController.ahk

; Run with a NEW isolated database path. Refuse to interfere with a user's app.
SplitPath A_ScriptDir, , &testsRoot
SplitPath testsRoot, , &projectRoot
resultPath := A_Temp "\F7Hub-test_f7hub_launcher.txt"
try FileDelete resultPath
if (A_Args.Length != 1 && A_Args.Length != 2) || FileExist(A_Args[1]) {
    Report("BLOCKED: supply a new isolated database path and optional Python runtime path.")
    ExitApp 2
}
pythonPath := A_Args.Length == 2 ? A_Args[2] : ""
launcher := F7HubLauncher(projectRoot, A_Args[1], pythonPath)
DetectHiddenWindows true
existingShortcut := WinExist(projectRoot "\AutoHotkey\F7Hub.ahk ahk_class AutoHotkey")
DetectHiddenWindows false
if existingShortcut {
    Report("BLOCKED: exit the F7Hub shortcut from its tray menu before this live test.")
    ExitApp 2
}
if launcher.FindWindow() {
    Report("BLOCKED: close F7Hub before the live launcher test.")
    ExitApp 2
}
hwnd := 0
shortcutPid := 0
testExitCode := 0
testPid := DllCall("GetCurrentProcessId")
originalMouseX := 0
originalMouseY := 0
testF7Held := false
holdFollower := 0
holdController := 0
try {
    TestConsumedPress()
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
    CoordMode "Mouse", "Screen"
    MouseGetPos &originalMouseX, &originalMouseY
    Assert(!launcher.IsF7HubWindow(decoy.Hwnd), "Decoy passed F7Hub identity validation")
    Assert(launcher.LaunchOrFind() == hwnd, "Non-focusing lookup did not return the app window")
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

    ; Synthetic keyboard input is not physical key state in AutoHotkey. Drive
    ; the real controller through an injected test-only state provider while
    ; production continues to use GetKeyState("F7", "P").
    holdFollower := MagneticWindowFollower(ObjBindMethod(launcher, "IsF7HubWindow"))
    holdController := F7HotkeyController(launcher, holdFollower, ReadTestF7State)
    decoy.Show()
    holdController.OnDown()
    holdController.OnUp()
    Assert(WinWaitActive(hwnd, , 5), "Controller TAP did not focus the existing app")
    WinMinimize hwnd
    holdController.OnDown()
    holdController.OnUp()
    Assert(WinWaitActive(hwnd, , 5), "Controller TAP did not restore the minimized app")

    decoy.Show()
    Assert(WinWaitActive(decoy.Hwnd, , 2), "Decoy did not become active before HOLD")
    MoveMouseFarFromWindow(hwnd)
    WinGetPos &holdStartX, &holdStartY, , , hwnd
    testF7Held := true
    holdController.OnDown()
    Assert(WaitForMovement(hwnd, holdStartX, holdStartY, 2), "F7 HOLD did not move the app")
    Assert(WinActive(decoy.Hwnd), "F7 HOLD unnecessarily activated F7Hub")
    testF7Held := false
    holdController.OnUp()
    Sleep 50
    WinGetPos &releaseX, &releaseY, , , hwnd
    Sleep 100
    WinGetPos &stoppedX, &stoppedY, , , hwnd
    Assert(stoppedX == releaseX && stoppedY == releaseY, "F7 release did not stop movement")

    WinMinimize hwnd
    decoy.Show()
    MoveMouseFarFromWindow(hwnd)
    testF7Held := true
    holdController.OnDown()
    Assert(WaitForRestore(hwnd, 2), "F7 HOLD did not restore a minimized app")
    Assert(WinActive(decoy.Hwnd), "Minimized HOLD unnecessarily activated F7Hub")
    testF7Held := false
    holdController.OnUp()

    ; Exercise repeated hold sessions and confirm the launcher still resolves
    ; one validated window rather than starting a duplicate process.
    Loop 3 {
        MoveMouseFarFromWindow(hwnd)
        testF7Held := true
        holdController.OnDown()
        Sleep 260
        testF7Held := false
        holdController.OnUp()
        Sleep 50
        Assert(launcher.FindWindow() == hwnd, "Rapid HOLD lost or duplicated the F7Hub window")
    }

    if MonitorGetCount() > 1 {
        secondaryMonitor := MonitorGetPrimary() == 1 ? 2 : 1
        MonitorGetWorkArea secondaryMonitor, &workLeft, &workTop, &workRight, &workBottom
        MouseMove workLeft + (workRight - workLeft) // 2, workTop + (workBottom - workTop) // 2, 0
        ; Keep the cursor over the intended foreground window. Windows hover
        ; activation must not focus an unrelated app during the bounded chase.
        MouseGetPos &cursorX, &cursorY
        WinMove cursorX - 120, cursorY - 50, 240, 100, decoy.Hwnd
        decoy.Show()
        Assert(WinWaitActive(decoy.Hwnd, , 2), "Decoy did not become active before multi-monitor HOLD")
        testF7Held := true
        holdController.OnDown()
        Assert(WaitForWorkArea(hwnd, workLeft, workTop, workRight, workBottom, 4), "HOLD did not reach the secondary monitor work area")
        Assert(WinActive(decoy.Hwnd), "Multi-monitor HOLD changed foreground; active=" WinGetTitle("A"))
        testF7Held := false
        holdController.OnUp()
    }

    Run '"' A_AhkPath '" /ErrorStdOut "' projectRoot '\AutoHotkey\F7Hub.ahk"', projectRoot, , &duplicatePid
    Assert(!ProcessWaitClose(duplicatePid, 5), "Duplicate shortcut did not exit")
    Assert(ProcessExist(shortcutPid), "Original shortcut exited")
    decoy.Destroy()
    Report("PASS: missing runtime, timeout/retry guard, cold launch, environment restoration, validated non-focusing lookup, controller tap focus, hold without focus, release stop, minimized hold restore, rapid hold reuse, multi-monitor work-area movement, decoy rejection, shortcut registration and single shortcut instance.")
} catch Error as testError {
    Report("FAIL: " testError.Message " | What=" testError.What " | Line=" testError.Line)
    testExitCode := 1
} finally {
    testF7Held := false
    if IsObject(holdController)
        holdController.OnUp()
    if IsObject(holdFollower)
        holdFollower.Stop()
    if originalMouseX || originalMouseY
        MouseMove originalMouseX, originalMouseY, 0
    if shortcutPid && ProcessExist(shortcutPid)
        ProcessClose shortcutPid
    if hwnd && WinExist(hwnd) {
        WinClose hwnd
        WinWaitClose hwnd, , 5
    }
    for path in [A_Args[1], A_Args[1] "-wal", A_Args[1] "-shm"] {
        try FileDelete path
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

Report(message) {
    global resultPath
    FileAppend message "`n", resultPath, "UTF-8"
}

MoveMouseFarFromWindow(hwnd) {
    WinGetPos &winX, &winY, &winWidth, &winHeight, hwnd
    monitorIndex := MonitorGetPrimary()
    MonitorGetWorkArea monitorIndex, &left, &top, &right, &bottom
    windowCenterX := winX + winWidth / 2
    windowCenterY := winY + winHeight / 2
    targetX := Abs(windowCenterX - left) > Abs(windowCenterX - right) ? left + 20 : right - 20
    targetY := Abs(windowCenterY - top) > Abs(windowCenterY - bottom) ? top + 20 : bottom - 20
    MouseMove targetX, targetY, 0
}

WaitForMovement(hwnd, startX, startY, timeoutSeconds) {
    deadline := A_TickCount + timeoutSeconds * 1000
    while A_TickCount < deadline {
        WinGetPos &currentX, &currentY, , , hwnd
        if Abs(currentX - startX) >= 2 || Abs(currentY - startY) >= 2
            return true
        Sleep 16
    }
    return false
}

WaitForRestore(hwnd, timeoutSeconds) {
    deadline := A_TickCount + timeoutSeconds * 1000
    while A_TickCount < deadline {
        if WinGetMinMax(hwnd) != -1
            return true
        Sleep 16
    }
    return false
}

WaitForWorkArea(hwnd, left, top, right, bottom, timeoutSeconds) {
    deadline := A_TickCount + timeoutSeconds * 1000
    while A_TickCount < deadline {
        WinGetPos &x, &y, &width, &height, hwnd
        maxX := Max(left, right - width)
        maxY := Max(top, bottom - height)
        if x >= left && x <= maxX && y >= top && y <= maxY
            return true
        Sleep 16
    }
    return false
}

ReadTestF7State(*) {
    global testF7Held
    return testF7Held
}

class CountingLauncher {
    Calls := 0
    Fail := false
    LaunchOrFind() {
        this.Calls += 1
        if this.Fail
            throw Error("Injected launch/lookup failure")
        return 123
    }
}

class CountingFollower {
    Starts := 0
    Running := false
    Fail := false
    Start(*) {
        this.Starts += 1
        this.Running := !this.Fail
        return this.Running
    }
    Stop() {
        this.Running := false
    }
}

class QuietController extends F7HotkeyController {
    Errors := 0
    ReportError(*) {
        this.Errors += 1
    }
}

TestConsumedPress() {
    global testF7Held
    for failure in ["self-stop", "launcher", "follower"] {
        countedLauncher := CountingLauncher()
        countedFollower := CountingFollower()
        controller := QuietController(countedLauncher, countedFollower, ReadTestF7State)
        try {
            countedLauncher.Fail := failure == "launcher"
            countedFollower.Fail := failure == "follower"
            testF7Held := true
            controller.OnDown()
            Assert(controller.State == "PENDING", "Hold did not begin pending")
            Sleep controller.HoldThresholdMs + 100
            if failure == "self-stop" {
                Assert(controller.State == "HOLDING", "Controller did not enter HOLDING")
                countedFollower.Stop()
            }
            Loop 4
                controller.OnDown()
            Sleep controller.HoldThresholdMs + 100
            Assert(controller.State == "WAIT_RELEASE", "Consumed hold did not wait for release")
            Assert(countedLauncher.Calls == 1, "Same press relaunched after " failure)
            expectedStarts := failure == "launcher" ? 0 : 1
            Assert(countedFollower.Starts == expectedStarts, "Same press restarted follower after " failure)
            Assert(controller.Errors == (failure == "self-stop" ? 0 : 1), "Unexpected error count")
            Report("PASS: " failure " repeat: launcher=" countedLauncher.Calls "; follower=" countedFollower.Starts "; state=" controller.State)
            testF7Held := false
            controller.OnUp()
            Assert(controller.State == "IDLE", "Release did not reset consumed press")
            countedLauncher.Fail := false
            countedFollower.Fail := false
            testF7Held := true
            controller.OnDown()
            Sleep controller.HoldThresholdMs + 100
            Assert(controller.State == "HOLDING", "New press did not permit retry")
            Assert(countedLauncher.Calls == 2 && countedFollower.Starts == expectedStarts + 1, "New press counts incorrect")
            Report("PASS: " failure " new press: launcher=" countedLauncher.Calls "; follower=" countedFollower.Starts)
        } finally {
            testF7Held := false
            controller.OnUp()
            countedFollower.Stop()
        }
    }
}
