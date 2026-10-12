#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../../AutoHotkey/Helpers/ClipboardHotkeyPolicy.ahk
#Include ../../AutoHotkey/Hotkeys/ClipboardPressCycleController.ahk

passed := 0
try {
    policy := ClipboardHotkeyPolicy()
    actions := ["clipboard.capture_selection", "clipboard.paste_active"]
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
    policy := ClipboardHotkeyPolicy()
    for action in actions
        TestCycles(action, policy)
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
