#Requires AutoHotkey v2.0
#SingleInstance Off
#NoTrayIcon
#Include ../../AutoHotkey/Helpers/ClipboardHotkeyPolicy.ahk
#Include fixtures/cp01_harness_support.ahk

; Noninteractive: hidden window only, no registration or input injection.
if A_Args.Length != 1
    ExitApp 2
DetectHiddenWindows true
global Evidence := A_Args[1], Passed := 0, FixturePid := 0, FixtureHwnd := 0
global Artifacts := [], Snapshots := []
exitCode := 0
try {
    token := DllCall("GetCurrentProcessId") "-" A_TickCount
    path := Evidence "\handshake-" token ".ready"
    Artifacts.Push(path, path ".pending")
    Cp01Ready.Publish(path, token, 123, 456)
    ready := Cp01Ready.Read(path, token, 456)
    Check(ready.Hwnd == 123 && ready.Pid == 456, "Complete readiness handshake")
    Check(!FileExist(path ".pending"), "Publication removes pending artifact")
    ExpectFailure(() => Cp01Ready.Publish(path, token, 999, 456), "READY_PUBLISH_IO")
    Check(Cp01Ready.Read(path, token, 456).Hwnd == 123 && !FileExist(path ".pending"), "No overwrite; failed publication cleans pending artifact")
    ExpectFailure(() => Cp01Ready.Read(path, "wrong-token", 456), "READY_IDENTITY_MISMATCH")
    ExpectFailure(() => Cp01Ready.Read(path, token, 457), "READY_IDENTITY_MISMATCH")
    FileDelete path

    ExpectFailure(() => Cp01Ready.Read(Evidence, token, 456), "READY_READ_IO")
    lock := FileOpen(path, "w-", "UTF-8-RAW")
    lock.Write(token "|123|456|READY`n")
    stats := {Sharing: 0, Missing: 0}
    SetTimer (() => lock.Close()), -80
    ready := Cp01Ready.Read(path, token, 456, 1000, stats)
    Check(stats.Sharing > 0 && ready.Hwnd == 123, "Real sharing violation then bounded recovery")
    lock := FileOpen(path, "r-", "UTF-8")
    started := A_TickCount
    try ExpectFailure(() => Cp01Ready.Read(path, token, 456, 80), "READY_TIMEOUT last=SHARING_ERROR_32")
    finally lock.Close()
    Check(A_TickCount - started < 1000, "Sharing timeout is finite")
    FileDelete path
    started := A_TickCount
    ExpectFailure(() => Cp01Ready.Read(path, token, 456, 80), "READY_TIMEOUT last=MISSING")
    Check(A_TickCount - started < 1000, "Missing artifact timeout is finite")
    for partial in ["", token "|123", token "|123|456|READY", token "|123|456|READY`ntrailing", token "|123|456|READY`n`n"] {
        stream := FileOpen(path, "w-", "UTF-8-RAW")
        stream.Write(partial), stream.Close()
        ExpectFailure(() => Cp01Ready.Read(path, token, 456), "READY_PARTIAL_OR_INVALID")
        FileDelete path
    }
    stream := FileOpen(path, "w-", "UTF-8-RAW")
    stream.Write(Format("{:0300}", 1)), stream.Close()
    ExpectFailure(() => Cp01Ready.Read(path, token, 456), "READY_INVALID size")
    FileDelete path

    Check(Cp01Classify(true, false, false, false, false, true) == "BLOCKED / INCONCLUSIVE - FOREGROUND INTERFERENCE", "External interference is BLOCKED, never PASS/policy failure")
    Check(Cp01Classify(false, true, false, false, false, false) == "SYNTHETIC TARGET NOT READY", "Readiness classification")
    Check(Cp01Classify(false, false, true, false, false, false) == "CALLBACK FAILURE", "Callback classification")
    Check(Cp01Classify(false, false, false, true, false, false) == "PRESS-CYCLE FAILURE", "Press-cycle classification")
    Check(Cp01Classify(false, false, false, false, true, true) == "EXPECTED STALE-TARGET REJECTION", "Intentional target change classification")
    Check(Cp01Classify(false, false, false, false, false, false) == "POLICY FAILURE", "Policy classification")
    Check(Cp01Classify(true, true, true, true, true, true) == "BLOCKED / INCONCLUSIVE - FOREGROUND INTERFERENCE", "Interference takes precedence")
    policy := ClipboardHotkeyPolicy()
    owned := {Hwnd: 10, Pid: 20, Exe: "allowed.exe"}, next := {Hwnd: 11, Pid: 21, Exe: "WINWORD2.EXE"}
    external := {Hwnd: 12, Pid: 22, Exe: "synthetic-external.exe"}
    Check(Cp01ExpectedForeground(policy, owned, owned), "Verified owned foreground accepted")
    Check(!Cp01ExpectedForeground(policy, external, owned), "External foreground invalidates attempt")
    Check(!Cp01ExpectedForeground(policy, 0, owned), "Unresolved foreground fails closed")
    Check(Cp01ExpectedForeground(policy, next, owned, {Old: owned, Next: next}), "Intentional acquisition permits verified destination")
    Check(!Cp01ExpectedForeground(policy, external, owned, {Old: owned, Next: next}), "Acquisition never permits external interference")
    fixture := DiagnosticFixture()
    fixture.Down()
    Check(fixture.Controller.InitialAllowed && fixture.Controller.Initial.Hwnd == 10, "Actual initial decision retained")
    fixture.Context := {Hwnd: 11, Pid: 21, Exe: "WINWORD2.EXE"}
    fixture.Up()
    Check(fixture.Count == 0 && fixture.Controller.Recheck == "target_changed" && fixture.Controller.Reason == "target_changed", "Stale rejection diagnostic")
    Check(fixture.Controller.LastContext.Pid == 21 && fixture.Controller.State == "IDLE", "Resolved target and press state diagnostic")
    Check(fixture.Controller.ObservedKeys["F23"] == false && fixture.Controller.ObservedKeys["Ctrl"] == false && fixture.Controller.ObservedKeys["Alt"] == false, "Consumed key-state diagnostics")
    diagnostic := Cp01DiagnosticLine(fixture.Controller, "release", "WAIT_RELEASE", 42,
        {Hwnd: 10, Pid: 20, Exe: "allowed.exe"}, fixture.Count)
    for field in ["scenario=42", "expected_exe=allowed.exe", "actual_exe=WINWORD2.EXE", "expected_hwnd=10", "expected_pid=20",
        "actual_hwnd=11", "actual_pid=21", "initial_allow=1", "state_after=IDLE", "F23=0", "Ctrl=0", "Alt=0",
        "recheck=target_changed", "callbacks=0", "suppression_reason=target_changed"]
        Check(InStr(diagnostic, field), "Diagnostic field " field)
    fixture.Throw := true
    fixture.Down()
    ExpectFailure(() => fixture.Up(), "Injected callback failure")
    Check(fixture.Controller.CallbackFailed && fixture.Controller.State == "IDLE" && fixture.Count == 1, "Callback error/count and cleanup diagnosed")
    Check(Snapshots.Length > 0 && Snapshots[1].Action == "clipboard.capture_selection", "Scenario diagnostic sink used")
    fixture.Throw := false
    fixture.Down(), fixture.Up()
    Check(fixture.Count == 2 && !fixture.Controller.CallbackFailed, "Fresh cycle after callback failure")

    ; Exercise the real fixture writer/reader without showing or activating it.
    readyPath := Evidence "\fixture-" token ".ready", inputPath := Evidence "\fixture-" token ".input"
    Artifacts.Push(readyPath, readyPath ".pending", inputPath)
    foreground := WinExist("A")
    Run('"' A_AhkPath '" /ErrorStdOut "' A_ScriptDir '\fixtures\clipboard_policy_target.ahk" "' readyPath '" "' inputPath '" "' token '"', , "Hide", &FixturePid)
    FileAppend(FixturePid "`n", Evidence "\owned-pids.txt", "UTF-8")
    ready := Cp01Ready.Read(readyPath, token, FixturePid)
    FixtureHwnd := ready.Hwnd
    Check(WinExist(FixtureHwnd) && WinGetPID(FixtureHwnd) == FixturePid, "Hidden fixture HWND/PID readiness")
    Check(!DllCall("IsWindowVisible", "Ptr", FixtureHwnd), "Default fixture window is hidden")
    Check(WinExist("A") == foreground, "Hidden fixture does not change foreground")
    Check(!FileExist(inputPath), "No fixture key input")
} catch Error as err {
    FileAppend("FAIL " err.Message " line=" err.Line " assertions=" Passed "`n", "*")
    exitCode := 1
} finally {
    if FixturePid && ProcessExist(FixturePid) {
        ProcessClose FixturePid
        ProcessWaitClose(FixturePid, 2)
    }
    if (FixturePid && ProcessExist(FixturePid)) || (FixtureHwnd && WinExist(FixtureHwnd))
        exitCode := 1
    for path in Artifacts {
        if FileExist(path)
            FileDelete path
    }
    for path in Artifacts {
        if FileExist(path)
            exitCode := 1
    }
    FileAppend("CLEANUP hidden_fixture_survivors=" (FixturePid && ProcessExist(FixturePid) ? 1 : 0) "`n", "*")
}
if exitCode == 0
    FileAppend("PASS assertions=" Passed "`n", "*")
ExitApp exitCode

Check(condition, message) {
    global Passed
    if !condition
        throw Error(message)
    Passed++
}
ExpectFailure(operation, expected) {
    try operation.Call()
    catch Error as err {
        Check(InStr(err.Message, expected), "Expected error classification: " expected)
        return
    }
    throw Error("Expected failure missing: " expected)
}
Snapshot(controller, event, before) {
    global Snapshots
    Snapshots.Push({Action: controller.Action, Event: event, Before: before, After: controller.State})
}
class DiagnosticFixture {
    __New() {
        this.Keys := Map("F23", false, "Ctrl", false, "Alt", false, "Shift", false, "LWin", false, "RWin", false)
        this.Context := {Hwnd: 10, Pid: 20, Exe: "allowed.exe"}, this.Count := 0, this.Throw := false
        this.Controller := Cp01ObservedController("clipboard.capture_selection", "F23", ClipboardHotkeyPolicy(),
            ObjBindMethod(this, "Dispatch"), () => this.Context, (key) => this.Keys[key], Snapshot)
    }
    Dispatch(*) {
        this.Count++
        if this.Throw
            throw Error("Injected callback failure")
    }
    Down() {
        this.Keys["Ctrl"] := true, this.Keys["Alt"] := true, this.Keys["F23"] := true
        this.Controller.OnDown()
    }
    Up() {
        this.Keys["Ctrl"] := false, this.Keys["Alt"] := false, this.Keys["F23"] := false
        this.Controller.OnRelease()
    }
}
