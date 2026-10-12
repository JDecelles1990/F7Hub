#Requires AutoHotkey v2.0
#SingleInstance Off
#NoTrayIcon
#MaxThreadsPerHotkey 1
#Include ../../AutoHotkey/Helpers/ClipboardHotkeyPolicy.ahk
#Include ../../AutoHotkey/Hotkeys/ClipboardPressCycleController.ahk
#Include fixtures/cp01_harness_support.ahk

; Direct launches also fail closed. The supervisor obtains a typed confirmation.
if A_Args.Length != 3 || A_Args[2] != "native-interactive-confirmed"
    ExitApp 2
global Evidence := A_Args[1], Passed := 0, Owned := [], Targets := Map()
global Monitor := Integer(A_Args[3]), Expected := 0, ForegroundLost := false, Scenario := 0
global DiagnosticLines := [], ReadyFailure := false, StaleExpected := false
global Acquiring := 0, CurrentController := 0
DetectHiddenWindows true
if Monitor < 1 || Monitor > MonitorGetCount()
    ExitApp 2
MonitorGetWorkArea Monitor, &workLeft, &workTop, &workRight, &workBottom
global WindowX := workLeft + 20, WindowY := workTop + 20
global WorkArea := {Left: workLeft, Top: workTop, Right: workRight, Bottom: workBottom}
global Policy := ClipboardHotkeyPolicy(), Calls := Map("clipboard.capture_selection", 0, "clipboard.paste_active", 0)
global Unknown := false, CallbackThrows := false, CallbackErrors := 0, UnexpectedCallbackError := false
; Injected SendEvent is not physical GetKeyState(P). Substitute ONLY key-state
; observation; actual Windows hook routing and foreground identity remain native.
global Capture := Cp01ObservedController("clipboard.capture_selection", "F23", Policy, CountAction, ReadContext, (key) => GetKeyState(key), Diagnose)
global Paste := Cp01ObservedController("clipboard.paste_active", "F24", Policy, CountAction, ReadContext, (key) => GetKeyState(key), Diagnose)
SendMode "Event"
SendLevel 1
SetKeyDelay 15, 15
SetTimer RunTests, -50
SetTimer ObserveForeground, 10

#HotIf Capture.IsEligible()
$*F23::Capture.OnDown()
#HotIf
~$*F23::Capture.OnDown()
~$*F23 up::ReleaseControllers()
#HotIf Paste.IsEligible()
$*F24::Paste.OnDown()
#HotIf
~$*F24::Paste.OnDown()
~$*F24 up::ReleaseControllers()
~$*LControl up::ReleaseControllers()
~$*RControl up::ReleaseControllers()
~$*LAlt up::ReleaseControllers()
~$*RAlt up::ReleaseControllers()

ReadContext() {
    global Unknown, Policy, Expected, ForegroundLost, Acquiring
    actual := Policy.ReadForeground()
    if !Cp01ExpectedForeground(Policy, actual, Expected, Acquiring)
        ForegroundLost := true
    return Unknown ? 0 : actual
}
CountAction(action, bound) {
    global Calls, CallbackThrows
    ; The callback must never count a dispatch bound to an unintended window.
    GuardForeground()
    global Expected, Policy
    if !Policy.SameTarget(bound, Expected)
        throw Error("Callback bound to unintended synthetic target")
    Calls[action]++
    if CallbackThrows
        throw Error("Injected callback error")
}
ReleaseControllers(*) {
    global Capture, Paste, CallbackErrors, CallbackThrows, UnexpectedCallbackError
    for controller in [Capture, Paste] {
        try controller.OnRelease()
        catch Error {
            CallbackErrors++
            if !CallbackThrows
                UnexpectedCallbackError := true
        }
    }
}
Check(condition, message) {
    global Passed, ForegroundLost, Capture, Paste, StaleExpected, UnexpectedCallbackError
    GuardForeground()
    if UnexpectedCallbackError
        throw Error("CALLBACK FAILURE unexpected exception")
    if !condition {
        Diagnose(Capture, "failed_assertion", Capture.State)
        Diagnose(Paste, "failed_assertion", Paste.State)
        throw Error(message)
    }
    Passed++
    FileAppend("PASS " message "`n", "*")
    if StaleExpected {
        FileAppend("CLASSIFICATION EXPECTED STALE-TARGET REJECTION`n", "*")
        StaleExpected := false
    }
}
WaitFor(predicate, message, timeout := 2000) {
    deadline := A_TickCount + timeout
    while A_TickCount < deadline {
        GuardForeground()
        if predicate.Call()
            return
        Sleep 10
    }
    throw Error("Readiness timeout: " message)
}
Activate(name) {
    global Targets, Expected, WindowX, WindowY, Policy, WorkArea
    ; Never recover focus after an external change: that attempt is invalid.
    if IsObject(Expected)
        GuardForeground()
    target := Targets[name], hwnd := target.Hwnd
    if !WinExist(hwnd) || WinGetPID(hwnd) != target.Pid
        || StrLower(WinGetProcessName(hwnd)) != StrLower(name)
        throw Error("SYNTHETIC TARGET NOT READY identity=" name)
    old := Expected
    ; Only the verified previous and destination HWND may occur during acquisition.
    global Acquiring
    Acquiring := {Old: Policy.ReadForeground(), Next: target}
    try {
        WinGetPos(, , &width, &height, hwnd)
        if width > WorkArea.Right - WorkArea.Left || height > WorkArea.Bottom - WorkArea.Top
            throw Error("SYNTHETIC TARGET NOT READY selected monitor too small")
        WindowX := Min(WindowX, WorkArea.Right - width), WindowY := Min(WindowY, WorkArea.Bottom - height)
        WinMove WindowX, WindowY, , , hwnd
        WinShow hwnd
        GuardForeground()
        WinActivate hwnd
        if !WinWaitActive(hwnd, , 2)
            throw Error("FOREGROUND ACQUISITION TIMEOUT")
        Expected := target
        if IsObject(old) && old.Hwnd != hwnd
            WinHide old.Hwnd
    } finally
        Acquiring := 0
    Check(true, "Target active " name)
}
NativeInputCount(name) {
    global Targets
    path := Targets[name].Input
    deadline := A_TickCount + 2000
    loop {
        try {
            stream := FileOpen(path, "r-", "UTF-8")
            try {
                if stream.Length > 4096
                    throw Error("INPUT_LOG_LIMIT")
                data := stream.Read()
            } finally stream.Close()
            if data != "" && SubStr(data, -1) != "`n"
                throw Error("INPUT_LOG_PARTIAL")
            return data == "" ? 0 : StrSplit(Trim(data, "`r`n"), "`n").Length
        } catch OSError as err {
            if err.Number == 2
                return 0
            if err.Number != 32 && err.Number != 33
                throw err
            if A_TickCount >= deadline
                throw Error("INPUT_LOG_SHARING_TIMEOUT")
            Sleep 10
        }
    }
}
Down(key) {
    global Scenario, Capture, Paste, CurrentController
    GuardForeground()
    WaitFor(() => Capture.State == "IDLE" && Paste.State == "IDLE"
        && !GetKeyState("Ctrl") && !GetKeyState("Alt") && !GetKeyState("F23") && !GetKeyState("F24"), "released keys and IDLE before fresh cycle")
    Scenario++
    CurrentController := key == "F23" ? Capture : Paste
    downSerial := CurrentController.DownSerial
    GuardForeground()
    SendEvent "{Blind}{LControl down}{LAlt down}{" key " down}"
    Sleep 40
    GuardForeground()
    WaitFor(() => CurrentController.DownSerial > downSerial, "PRESS-CYCLE FAILURE trigger handler not observed")
}
Up(key, order := 0) {
    global Capture, Paste
    GuardForeground()
    if order == 0
        SendEvent "{Blind}{" key " up}{LAlt up}{LControl up}"
    else
        SendEvent "{Blind}{LControl up}{LAlt up}{" key " up}"
    Sleep 60
    GuardForeground()
    WaitFor(() => Capture.State == "IDLE" && Paste.State == "IDLE"
        && !GetKeyState("Ctrl") && !GetKeyState("Alt") && !GetKeyState(key), "complete release and controller IDLE")
}

ObserveForeground(*) {
    global Expected, ForegroundLost, Policy
    global Acquiring
    if ForegroundLost || (!IsObject(Expected) && !IsObject(Acquiring))
        return
    actual := Policy.ReadForeground()
    if Cp01ExpectedForeground(Policy, actual, Expected, Acquiring)
        return
    ForegroundLost := true
}
GuardForeground() {
    global ForegroundLost
    ObserveForeground()
    if ForegroundLost
        throw Error("BLOCKED / INCONCLUSIVE - FOREGROUND INTERFERENCE")
}
Diagnose(controller, event, before) {
    global DiagnosticLines, Scenario, Expected, Calls, Policy
    DiagnosticLines.Push(Cp01DiagnosticLine(controller, event, before, Scenario, Expected, Calls[controller.Action]))
    if DiagnosticLines.Length > 600
        DiagnosticLines.RemoveAt(1)
}
RunTests() {
    global Evidence, Targets, Owned, Capture, Paste, Policy, Calls, Unknown, CallbackThrows, CallbackErrors, Passed
    global ReadyFailure, ForegroundLost, DiagnosticLines, StaleExpected, CurrentController, UnexpectedCallbackError
    exitCode := 0
    try {
        for name in ["allowed.exe", "WINWORD.EXE", "EXCEL.EXE", "OUTLOOK.EXE", "OLK.EXE", "POWERPNT.EXE",
            "WinWord.Exe", "WINWORD2.EXE", "MYOUTLOOK.EXE", "OUTLOOK.EXE.BAK", "OLKHELPER.EXE", "POWERPNT2.EXE"] {
            ; Each runtime copy is prepared by the external supervisor.
            tag := name == "WinWord.Exe" ? "mixed-case" : name
            token := DllCall("GetCurrentProcessId") "-" A_TickCount "-" Owned.Length
            ready := Evidence "\targets\" tag "-" token ".ready", input := Evidence "\targets\" tag "-" token ".input"
            exe := Evidence "\targets\" tag "\" name
            Run('"' exe '" /ErrorStdOut "' A_ScriptDir '\fixtures\clipboard_policy_target.ahk" "' ready '" "' input '" "' token '"', , "Hide", &pid)
            Owned.Push({Pid: pid, Exe: exe})
            FileAppend(pid "`n", Evidence "\owned-pids.txt", "UTF-8")
            try handshake := Cp01Ready.Read(ready, token, pid)
            catch Error as err {
                ReadyFailure := true
                throw err
            }
            hwnd := handshake.Hwnd
            if !WinExist(hwnd) || WinGetPID(hwnd) != pid {
                ReadyFailure := true
                throw Error("SYNTHETIC TARGET NOT READY HWND/PID " name)
            }
            Check(true, "Owned window ready " name)
            WinGetPos(, , &width, &height, hwnd)
            FileAppend("READY target=" name " width=" width " height=" height " condition=owned-HWND-PID`n", "*")
            Targets[name] := {Hwnd: hwnd, Pid: pid, Exe: name, Input: input, Ready: ready}
        }
        for actionKey in [["clipboard.capture_selection", "F23"], ["clipboard.paste_active", "F24"]] {
            action := actionKey[1], key := actionKey[2]
            Activate("allowed.exe")
            before := Calls[action]
            Down(key)
            Loop 12
                RepeatDown(key)
            Check(Calls[action] == before, "No callback during hold/autorepeat " action)
            Up(key)
            Check(Calls[action] == before + 1, "Hold executes once after complete release " action)
            Loop 4 {
                Down(key), Up(key, Mod(A_Index, 2))
            }
            Check(Calls[action] == before + 5, "Fresh cycles and both release orders " action)
            for name in ["WINWORD.EXE", "EXCEL.EXE", "OUTLOOK.EXE", "OLK.EXE", "POWERPNT.EXE", "WinWord.Exe"] {
                Activate(name)
                context := Policy.ReadForeground()
                Check(StrLower(context.Exe) == StrLower(name), "Native executable basename " name)
                before := Calls[action], nativeBefore := NativeInputCount(name)
                Down(key), Up(key)
                Check(Calls[action] == before, "Excluded no callback " name " " action)
                Check(NativeInputCount(name) > nativeBefore, "Excluded native shortcut delivered " name)
            }
            for name in ["WINWORD2.EXE", "MYOUTLOOK.EXE", "OUTLOOK.EXE.BAK", "OLKHELPER.EXE", "POWERPNT2.EXE"] {
                Activate(name)
                before := Calls[action]
                Down(key), Up(key)
                Check(Calls[action] == before + 1, "Lookalike allowed " name " " action)
            }
            for destination in ["EXCEL.EXE", "WINWORD2.EXE"] {
                Activate("allowed.exe")
                before := Calls[action]
                Down(key)
                Activate(destination)
                StaleExpected := true
                Up(key)
                Check(Calls[action] == before, "Bound target change prevents dispatch " destination)
            }
            Activate("EXCEL.EXE")
            before := Calls[action]
            Down(key)
            Activate("allowed.exe")
            RepeatDown(key)
            Up(key)
            Check(Calls[action] == before, "Excluded-to-allowed held cycle cannot activate")
            Unknown := true
            nativeBefore := NativeInputCount("allowed.exe")
            Down(key)
            Unknown := false
            RepeatDown(key)
            Up(key)
            Check(Calls[action] == before, "Unknown-to-allowed held cycle cannot activate")
            Check(NativeInputCount("allowed.exe") > nativeBefore, "Unknown native shortcut delivered")
            Down(key)
            Unknown := true
            Up(key)
            Unknown := false
            Check(Calls[action] == before, "Allowed-to-unknown recheck prevents dispatch")
            Down(key)
            Policy.SetExclusions(action, ["allowed.exe"])
            Up(key)
            Check(Calls[action] == before, "Final policy change prevents dispatch")
            Policy := ClipboardHotkeyPolicy()
            Capture.Policy := Policy, Paste.Policy := Policy
            Down(key)
            GuardForeground()
            SendEvent "{Blind}{LControl up}{LControl down}{" key " down}"
            Up(key)
            Check(Calls[action] == before + 1, "Modifier release/repress stays one cycle")
            Down(key)
            Capture.Cancel(), Paste.Cancel()
            RepeatDown(key)
            Up(key)
            Check(Calls[action] == before + 1, "Cancellation consumes held cycle")
            CallbackThrows := true
            Down(key), Up(key)
            CallbackThrows := false
            Check(CallbackErrors > 0 && Capture.State == "IDLE" && Paste.State == "IDLE", "Callback exception cleans busy state")
            before := Calls[action]
            Down(key), Up(key)
            Check(Calls[action] == before + 1, "Fresh valid cycle after all rejection paths")
        }
        Check(!GetKeyState("Ctrl") && !GetKeyState("Alt") && !GetKeyState("F23") && !GetKeyState("F24"), "No stuck injected keys")
        FileAppend("PASS assertions=" Passed "`n", "*")
    } catch Error as err {
        pressFailure := InStr(err.Message, "PRESS-CYCLE FAILURE") || InStr(err.Message, "released keys") || InStr(err.Message, "complete release")
            || (IsObject(CurrentController) && CurrentController.State != "IDLE")
            || (IsObject(CurrentController) && CurrentController.ChordResult == 0)
        classification := Cp01Classify(ForegroundLost, ReadyFailure || InStr(err.Message, "SYNTHETIC TARGET NOT READY"),
            UnexpectedCallbackError || (IsObject(CurrentController) && CurrentController.CallbackFailed), pressFailure, false, false)
        FileAppend("RESULT " classification " detail=" err.Message " line=" err.Line " assertions=" Passed "`n", "*")
        Diagnose(Capture, "suite_failure", Capture.State)
        Diagnose(Paste, "suite_failure", Paste.State)
        exitCode := ForegroundLost || ReadyFailure ? 2 : 1
    } finally {
        SetTimer ObserveForeground, 0
        ; Recovery only releases synthetic keys; never sends another press after loss.
        for vk in [0x86, 0x87, 0xA2, 0xA3, 0xA4, 0xA5]
            DllCall("keybd_event", "UChar", vk, "UChar", 0, "UInt", 2, "UPtr", 0)
        for process in Owned {
            try {
                if ProcessExist(process.Pid) {
                    if StrLower(ProcessGetPath(process.Pid)) != StrLower(process.Exe)
                        throw Error("Owned PID identity changed; refusing termination")
                    ProcessClose process.Pid
                    ProcessWaitClose(process.Pid, 2)
                }
                if ProcessExist(process.Pid)
                    exitCode := 1
            } catch Error {
                exitCode := 1
                FileAppend("CLEANUP FAIL owned process identity/termination`n", "*")
            }
        }
        for name, target in Targets {
            for path in [target.Ready, target.Ready ".pending", target.Input] {
                try {
                    if FileExist(path)
                        FileDelete path
                } catch Error {
                    exitCode := 1
                    FileAppend("CLEANUP FAIL owned artifact`n", "*")
                }
            }
        }
        for line in DiagnosticLines
            FileAppend(line "`n", "*")
        FileAppend("CLEANUP owned=" Owned.Length " hotkeys=end-with-process`n", "*")
    }
    ExitApp exitCode
}

RepeatDown(key) {
    GuardForeground()
    SendEvent "{Blind}{" key " down}"
    GuardForeground()
}
