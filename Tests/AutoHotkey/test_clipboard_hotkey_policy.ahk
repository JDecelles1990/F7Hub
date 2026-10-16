#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../../AutoHotkey/Helpers/ClipboardHotkeyPolicy.ahk
#Include ../../AutoHotkey/Hotkeys/ClipboardPressCycleController.ahk

passed := 0
try {
    policy := ClipboardHotkeyPolicy()
    actions := ["clipboard.capture_selection", "clipboard.paste_active", "clipboard.paste_latest"]
    for action in actions {
        for name in ["winword.exe", "WINWORD.EXE", "WinWord.Exe", "excel.exe", "EXCEL.EXE",
            "outlook.exe", "OUTLOOK.EXE", "olk.exe", "OLK.EXE", "powerpnt.exe", "POWERPNT.EXE", "PowerPnt.Exe"] {
            Check(!policy.Allows(action, name), action " excludes " name)
            Check(!policy.Allows(action, "C:\fixture\" name), "Path-independent " name)
        }
        for name in ["notepad.exe", "powershell.exe", "msedge.exe", "WINWORD2.EXE",
            "MYOUTLOOK.EXE", "OUTLOOK.EXE.BAK", "OLKHELPER.EXE", "POWERPNT2.EXE", "Synthetic App.exe"]
            Check(policy.Allows(action, name), action " allows " name)
        Check(!policy.Allows(action, "\\server\share\WiNwOrD.ExE"), "UNC path basename exclusion")
        Check(policy.Allows(action, "C:\office\WINWORD2.EXE"), "Path lookalike stays allowed")
        for identity in ["", " ", '"WINWORD.EXE"', "relative\winword.exe", "C:\fixture\",
            "winword.exe --arg", " winword.exe", "C:/fixture/winword.exe", "file:winword.exe",
            "C:\fixture:stream\winword.exe", "C:\fixture\..\winword.exe", 0, {}, ".."] {
            Check(!policy.Allows(action, identity), "Malformed identity rejected")
        }
        Check(!policy.AllowsContext(action, 0), "Unknown context")
        Check(!policy.AllowsContext(action, {Hwnd: 1, Pid: 0, Exe: "notepad.exe"}), "Invalid PID")
    }
    Check(!policy.Allows("unknown", "notepad.exe"), "Unknown action fails closed")
    policy.SetExclusions(actions[1], ["notepad.exe"])
    Check(!policy.Allows(actions[1], "notepad.exe"), "Capture owns replacement")
    Check(policy.Allows(actions[2], "notepad.exe"), "Paste policy independent")
    Check(!policy.Allows(actions[2], "WINWORD.EXE"), "Paste defaults preserved")
    Check(policy.Allows(actions[1], "WINWORD.EXE"), "Capture can diverge")
    Check(!policy.Allows(actions[3], "WINWORD.EXE"), "Latest paste exclusion independent")
    policy.SetExclusions(actions[3], ["notepad.exe"])
    Check(!policy.Allows(actions[3], "notepad.exe"), "Latest paste replacement independent")
    Check(policy.Allows(actions[2], "notepad.exe"), "Active paste unchanged by latest policy")
    Check(!policy.SameTarget({Hwnd: 10, Pid: 20, Exe: "notepad.exe", Creation: "A"},
        {Hwnd: 10, Pid: 20, Exe: "notepad.exe", Creation: "B"}), "PID reuse rejected")
    Check(!policy.SameTarget({Hwnd: 10, Pid: 20, Exe: "notepad.exe", Creation: "A"},
        {Hwnd: 10, Pid: 20, Exe: "notepad.exe"}), "Missing creation evidence rejected")
    try ClipboardChord("ANYTHING")
    catch ValueError
        Check(true, "Unknown chord rejected")
    else
        Check(false, "Unknown chord accepted")
    policy := ClipboardHotkeyPolicy()
    for action in [actions[1], actions[2]]
        TestCycles(action, policy)
    try ClipboardPressCycleController(actions[3], "V", policy, (*) => 0)
    catch ValueError
        Check(true, "Latest paste cannot use CP-01 default chord")
    else
        Check(false, "Latest paste accepted wrong chord")
    for pair in [["clipboard.capture_selection", "C"], ["clipboard.paste_latest", "V"]]
        TestWinCycles(pair[1], pair[2], policy)
    TestWinCorrections(policy)
    FileAppend("PASS assertions=" passed "`n", "*")
    ExitApp 0
} catch Error as err {
    FileAppend("FAIL " err.Message " line=" err.Line " assertions=" passed "`n", "*")
    ExitApp 1
}

Check(condition, message) {
    global passed
    if !condition
        throw Error(message)
    passed++
}

class CycleFixture {
    __New(action, policy) {
        this.Keys := Map("F23", false, "Ctrl", false, "Alt", false, "Shift", false, "LWin", false, "RWin", false)
        this.Context := {Hwnd: 10, Pid: 20, Exe: "notepad.exe"}
        this.Count := 0
        this.Throw := false
        this.ProviderThrows := false
        this.Controller := ClipboardPressCycleController(action, "F23", policy,
            ObjBindMethod(this, "Dispatch"), ObjBindMethod(this, "ReadContext"), (key) => this.Keys[key])
    }
    ReadContext() {
        if this.ProviderThrows
            throw Error("Injected foreground failure")
        return this.Context
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
        this.Keys["F23"] := false, this.Keys["Ctrl"] := false, this.Keys["Alt"] := false
        this.Controller.OnRelease()
    }
}

TestCycles(action, policy) {
    fixture := CycleFixture(action, policy), controller := fixture.Controller
    fixture.Down()
    Loop 20
        controller.OnDown()
    Check(fixture.Count == 0, "Held/repeated trigger has no early effect")
    fixture.Keys["Ctrl"] := false
    controller.OnRelease()
    fixture.Keys["Ctrl"] := true
    controller.OnDown()
    Check(fixture.Count == 0, "Modifier repress cannot rearm")
    fixture.Up()
    Check(fixture.Count == 1 && controller.State == "IDLE", "One complete cycle")
    Loop 5 {
        fixture.Down(), fixture.Up()
    }
    Check(fixture.Count == 6, "Rapid fresh cycles")
    fixture.Down()
    fixture.Keys["F23"] := false
    controller.OnRelease()
    Check(fixture.Count == 6, "Trigger-first release waits for modifiers")
    fixture.Keys["Alt"] := false
    controller.OnRelease()
    fixture.Keys["Ctrl"] := false
    controller.OnRelease()
    Check(fixture.Count == 7, "Last modifier dispatches once")
    for changed in [{Hwnd: 11, Pid: 20, Exe: "notepad.exe"}, {Hwnd: 10, Pid: 21, Exe: "notepad.exe"},
        {Hwnd: 10, Pid: 20, Exe: "msedge.exe"}, {Hwnd: 10, Pid: 20, Exe: "EXCEL.EXE"}, 0] {
        fixture.Down()
        fixture.Context := changed
        fixture.Up()
        Check(fixture.Count == 7 && controller.State == "IDLE", "Target change/unknown rejects and cleans")
        fixture.Context := {Hwnd: 10, Pid: 20, Exe: "notepad.exe"}
    }
    fixture.Down()
    policy.SetExclusions(action, ["notepad.exe"])
    fixture.Up()
    Check(fixture.Count == 7, "Policy rechecked before effect")
    policy.SetExclusions(action, [])
    for rejected in [0, {Hwnd: 0, Pid: 20, Exe: "notepad.exe"}] {
        fixture.Context := rejected
        fixture.Down()
        fixture.Context := {Hwnd: 10, Pid: 20, Exe: "notepad.exe"}
        controller.OnDown()
        fixture.Up()
        Check(fixture.Count == 7, "Initially unknown held cycle stays consumed")
    }
    fixture.Down()
    controller.Cancel()
    controller.OnDown()
    fixture.Up()
    Check(fixture.Count == 7 && controller.State == "IDLE", "Interrupted press cleanup")
    fixture.Throw := true
    fixture.Down()
    try fixture.Up()
    catch Error {
    }
    Check(fixture.Count == 8 && controller.State == "IDLE", "Callback exception releases busy state")
    fixture.Throw := false
    fixture.ProviderThrows := true
    fixture.Down()
    Check(controller.State == "WAIT_RELEASE", "Resolution error consumes cycle")
    fixture.ProviderThrows := false
    fixture.Up()
    Check(fixture.Count == 8 && controller.State == "IDLE", "Resolution error cleans")
    fixture.Down()
    fixture.ProviderThrows := true
    try fixture.Up()
    catch Error {
    }
    Check(controller.State == "IDLE" && fixture.Count == 8, "Final provider exception cleans")
    fixture.ProviderThrows := false
    fixture.Down(), fixture.Up()
    Check(fixture.Count == 9, "Valid fresh cycle after failures")
}

class WinFixture {
    __New(action, trigger, policy) {
        this.Keys := Map("C", false, "V", false, "Ctrl", false, "Alt", false,
            "Shift", false, "LWin", false, "RWin", false)
        this.Context := {Hwnd: 10, Pid: 20, Exe: "notepad.exe", Creation: "A"}
        this.Count := 0
        this.Async := false
        this.Throw := false
        this.CancelOnRead := false
        this.Trigger := trigger
        this.Controller := ClipboardPressCycleController(action, trigger, policy,
            ObjBindMethod(this, "Dispatch"), ObjBindMethod(this, "ReadContext"),
            (key) => this.Keys[key], ClipboardChord("WIN_ALT"))
    }
    ReadContext() {
        if this.CancelOnRead {
            this.CancelOnRead := false
            this.Controller.Cancel()
        }
        return this.Context
    }
    Dispatch(*) {
        this.Count++
        if this.Throw
            throw Error("Injected callback failure")
        return this.Async ? ClipboardAsyncPending() : 0
    }
    Down(side := "LWin") {
        this.Keys[side] := true, this.Keys["Alt"] := true, this.Keys[this.Trigger] := true
        return this.Controller.OnDown()
    }
    Up(side := "LWin") {
        this.Keys[this.Trigger] := false, this.Keys[side] := false, this.Keys["Alt"] := false
        return this.Controller.OnRelease()
    }
}

TestWinCycles(action, trigger, policy) {
    f := WinFixture(action, trigger, policy), c := f.Controller
    Check(f.Down(), "Win+Alt+" trigger " eligible")
    Loop 12
        c.OnDown()
    Check(f.Count == 0, "Held Win chord not dispatched")
    f.Keys[trigger] := false
    c.OnRelease()
    Check(f.Count == 0, "Trigger release waits for Win and Alt")
    f.Keys["Alt"] := false
    c.OnRelease()
    Check(f.Count == 0, "Alt release waits for Win")
    f.Keys["LWin"] := false
    c.OnRelease()
    Check(f.Count == 1 && c.State == "IDLE", "Win release dispatches once")
    Check(f.Down("RWin"), "Right Win recognized")
    f.Keys["RWin"] := false
    c.OnRelease()
    f.Keys[trigger] := false, f.Keys["Alt"] := false
    c.OnRelease()
    Check(f.Count == 2, "Right Win different release order")
    for extra in ["Ctrl", "Shift"] {
        f.Down(), f.Keys[extra] := true, c.ObserveModifiers()
        f.Keys[extra] := false, f.Up()
        Check(f.Count == 2, "Extra " extra " cancels pending Win chord")
    }
    f.Down(), f.Keys["RWin"] := true, c.ObserveModifiers()
    f.Keys["RWin"] := false, f.Up()
    Check(f.Count == 2, "New Win side cannot retarget held chord")
    f.Keys["Ctrl"] := true
    Check(!f.Down(), "Reserved Ctrl+Win+Alt+" trigger " pass-through")
    f.Up(), f.Keys["Ctrl"] := false, c.OnRelease()
    Check(f.Count == 2, "Reserved chord never dispatches")
    f.Keys["Ctrl"] := true, f.Keys["Alt"] := true
    Check(!c.IsEligible(), "AltGr-like Ctrl+Alt rejected")
    f.Keys["Ctrl"] := false, f.Keys["Alt"] := false
    f.Context := {Hwnd: 10, Pid: 20, Exe: "notepad.exe"}
    Check(!f.Down(), "Win chord needs creation identity")
    f.Up()
    Check(f.Count == 2, "Missing process creation stays denied")
    f.Context := {Hwnd: 10, Pid: 20, Exe: "notepad.exe", Creation: "A"}
    f.Down()
    f.Context := {Hwnd: 10, Pid: 20, Exe: "notepad.exe", Creation: "B"}
    f.Up()
    Check(f.Count == 2, "Same PID new process cannot retarget")
    f.Context := {Hwnd: 10, Pid: 20, Exe: "notepad.exe", Creation: "A"}
    f.Down(), c.Cancel(), f.Up()
    Check(f.Count == 2 && c.State == "IDLE", "Cancelled Win cycle cleans")
    f.Throw := true
    f.Down()
    try f.Up()
    catch Error
        Check(true, "Callback exception propagated")
    Check(f.Count == 3 && c.State == "IDLE", "Exception clears Win busy state")
    f.Throw := false, f.Async := true
    f.Down(), f.Up()
    Check(f.Count == 4 && c.State == "DISPATCHING", "Async return holds busy ownership")
    f.Down(), f.Up()
    Check(f.Count == 4, "Busy async cycle does not duplicate")
    c.Cancel()
    Check(c.Cancelled && c.State == "DISPATCHING", "Cancellation retains async ownership")
    Check(c.Complete() && c.State == "IDLE", "Completion releases async ownership")
    Check(!c.Complete(), "Duplicate completion rejected")
    f.Async := false
    f.Down(), f.Up()
    Check(f.Count == 5, "Fully rearmed new Win press")
}

TestWinCorrections(policy) {
    for side in ["LWin", "RWin"] {
        for triggerReleased in [false, true] {
            f := WinFixture("clipboard.capture_selection", "C", policy), c := f.Controller
            Check(f.Down(side), "Correction cycle starts with " side)
            Loop 3
                c.ObserveModifiers(side, true)
            Check(IsObject(c.Pending), "Held Win repeats retain pending cycle")
            if triggerReleased {
                f.Keys[f.Trigger] := false
                c.OnRelease()
                Check(f.Count == 0, "Trigger release awaits Win transition")
            }
            f.Keys[side] := false
            c.ObserveModifiers(side, false)
            f.Keys[side] := true
            Check(!c.ObserveModifiers(side, true), "Same-side " side " re-press invalidates pending")
            Check(!c.OnDown(), "Restored " side " cannot rearm while held")
            f.Up(side)
            Check(f.Count == 0 && c.State == "IDLE", "Restored modifier cannot dispatch stale cycle")
            Check(f.Down(side), "Fully released cycle rearms " side)
            f.Up(side)
            Check(f.Count == 1 && c.State == "IDLE", "Fresh " side " cycle dispatches once")
        }
    }
    f := WinFixture("clipboard.capture_selection", "C", policy), c := f.Controller
    Check(f.Down(), "Reentrant cancellation cycle starts")
    f.CancelOnRead := true
    f.Up()
    Check(f.Count == 0 && c.State == "IDLE" && c.Cancelled,
        "Cancellation inside target revalidation prevents callback")
    Check(f.Down(), "Reentrant cancellation fully rearms")
    f.Up()
    Check(f.Count == 1 && c.State == "IDLE", "Fresh cycle after reentrant cancellation")
}
