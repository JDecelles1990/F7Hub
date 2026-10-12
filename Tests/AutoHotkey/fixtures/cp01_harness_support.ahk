#Requires AutoHotkey v2.0
#Include ../../../AutoHotkey/Hotkeys/ClipboardPressCycleController.ahk
; Test-only handshake and observational diagnostics. No hotkeys or Clipboard APIs.
class Cp01Ready {
    static Publish(path, token, hwnd, pid, timeout := 2000) {
        pending := path ".pending"
        deadline := A_TickCount + timeout
        try {
            stream := FileOpen(pending, "w-", "UTF-8-RAW")
            try stream.Write(token "|" hwnd "|" pid "|READY`n")
            finally stream.Close()
            loop {
                ; Same-directory rename publishes only a complete, closed artifact.
                if DllCall("MoveFileW", "Str", pending, "Str", path)
                    return
                code := A_LastError
                if code != 32 && code != 33
                    throw Error("READY_PUBLISH_IO code=" code)
                if A_TickCount >= deadline
                    throw Error("READY_PUBLISH_TIMEOUT code=" code)
                Sleep 10
            }
        } catch OSError as err {
            throw Error("READY_PUBLISH_IO code=" err.Number)
        } finally {
            if FileExist(pending)
                FileDelete pending
        }
    }
    static Read(path, token, pid, timeout := 2000, stats := 0) {
        if !IsObject(stats)
            stats := {Sharing: 0, Missing: 0}
        deadline := A_TickCount + timeout, last := "MISSING"
        loop {
            try {
                stream := FileOpen(path, "r-", "UTF-8")
                try {
                    if stream.Length > 256
                        throw Error("READY_INVALID size")
                    data := stream.Read()
                } finally stream.Close()
                if !RegExMatch(data, "\A([A-Za-z0-9-]+)\|([1-9][0-9]*)\|([1-9][0-9]*)\|READY\n\z", &match)
                    throw Error("READY_PARTIAL_OR_INVALID")
                if StrCompare(match[1], token, true) != 0 || Integer(match[3]) != pid
                    throw Error("READY_IDENTITY_MISMATCH")
                return {Hwnd: Integer(match[2]), Pid: Integer(match[3])}
            } catch OSError as err {
                code := err.Number
                if code == 32 || code == 33 {
                    stats.Sharing++, last := "SHARING_ERROR_" code
                } else if code == 2 || code == 3 {
                    stats.Missing++, last := "MISSING"
                } else
                    throw Error("READY_READ_IO code=" code)
            }
            if A_TickCount >= deadline
                throw Error("READY_TIMEOUT last=" last " sharing=" stats.Sharing " missing=" stats.Missing)
            Sleep 10
        }
    }
}

Cp01Classify(foregroundLost, readyFailure, callbackFailure, pressFailure, staleExpected, suppressed) {
    if foregroundLost
        return "BLOCKED / INCONCLUSIVE - FOREGROUND INTERFERENCE"
    if readyFailure
        return "SYNTHETIC TARGET NOT READY"
    if callbackFailure
        return "CALLBACK FAILURE"
    if pressFailure
        return "PRESS-CYCLE FAILURE"
    if staleExpected && suppressed
        return "EXPECTED STALE-TARGET REJECTION"
    return "POLICY FAILURE"
}

Cp01ExpectedForeground(policy, actual, expected, acquiring := 0) {
    if IsObject(acquiring)
        return policy.SameTarget(actual, acquiring.Old) || policy.SameTarget(actual, acquiring.Next)
    return !IsObject(expected) || policy.SameTarget(actual, expected)
}

Cp01DiagnosticLine(controller, event, before, scenario, expected, callbackCount) {
    actual := controller.LastContext, initial := controller.Initial
    line := "DIAGNOSTIC scenario=" scenario " action=" controller.Action " event=" event
        . " expected_exe=" (IsObject(expected) ? expected.Exe : "none")
        . " expected_hwnd=" (IsObject(expected) ? expected.Hwnd : 0) " expected_pid=" (IsObject(expected) ? expected.Pid : 0)
        . " actual_exe=" (IsObject(actual) ? actual.Exe : "unknown") " actual_hwnd=" (IsObject(actual) ? actual.Hwnd : 0)
        . " actual_pid=" (IsObject(actual) ? actual.Pid : 0) " initial_allow=" controller.InitialAllowed
        . " initial_hwnd=" (IsObject(initial) ? initial.Hwnd : 0) " initial_pid=" (IsObject(initial) ? initial.Pid : 0)
        . " state_before=" before " state_after=" controller.State " recheck=" controller.Recheck
        . " chord_valid=" controller.ChordResult " keys_released=" controller.KeysReleasedResult
        . " callbacks=" callbackCount " suppression_reason=" controller.Reason
    for key in [controller.TriggerKey, "Ctrl", "Alt", "Shift", "LWin", "RWin"]
        line .= " " key "=" (controller.ObservedKeys.Has(key) ? controller.ObservedKeys[key] : "not_read")
    return line
}

; Delegates to each production method exactly once. Retains the contexts/keys
; actually consumed by that method, rather than reconstructing missing callbacks.
class Cp01ObservedController extends ClipboardPressCycleController {
    __New(action, key, policy, callback, provider, keys, sink) {
        this.Provider := provider, this.Keys := keys, this.Sink := sink, this.Dispatch := callback
        this.LastContext := 0, this.Initial := 0, this.InitialAllowed := -1
        this.Recheck := "not_reached", this.Reason := "not_started"
        this.ObservedKeys := Map(), this.CallbackFailed := false
        this.KeysReleasedResult := -1, this.ChordResult := -1
        this.DownSerial := 0
        super.__New(action, key, policy, ObjBindMethod(this, "ObserveCallback"), ObjBindMethod(this, "ObserveContext"), ObjBindMethod(this, "ObserveKey"))
    }
    ObserveContext() {
        this.LastContext := this.Provider.Call()
        return this.LastContext
    }
    ObserveKey(key) {
        value := this.Keys.Call(key)
        this.ObservedKeys[key] := value
        return value
    }
    ObserveCallback(action, bound) {
        try return this.Dispatch.Call(action, bound)
        catch Error as err {
            this.CallbackFailed := true
            throw err
        }
    }
    ChordDown() {
        this.ChordResult := super.ChordDown()
        return this.ChordResult
    }
    KeysReleased() {
        this.KeysReleasedResult := super.KeysReleased()
        return this.KeysReleasedResult
    }
    OnDown() {
        this.DownSerial++
        before := this.State
        if before == "IDLE" {
            this.LastContext := 0, this.Recheck := "not_reached", this.CallbackFailed := false
            this.ObservedKeys := Map(), this.ChordResult := -1, this.KeysReleasedResult := -1
        }
        result := super.OnDown()
        if before == "IDLE" {
            this.Initial := this.LastContext
            this.InitialAllowed := this.Policy.AllowsContext(this.Action, this.Initial)
        }
        this.Reason := result ? "pending_target_established" : before != "IDLE" ? "cycle_already_consumed" : "initial_chord_or_policy_rejected"
        this.Sink.Call(this, "down", before)
        return result
    }
    OnRelease() {
        before := this.State, bound := this.Pending
        if before != "WAIT_RELEASE"
            return super.OnRelease()
        this.LastContext := 0
        try {
            result := super.OnRelease()
            current := this.LastContext
            if before != "WAIT_RELEASE"
                this.Reason := "cycle_not_waiting_release"
            else if this.State == "WAIT_RELEASE"
                this.Reason := "trigger_or_modifiers_not_released"
            else if !IsObject(bound)
                this.Reason := "pending_target_not_established"
            else if !IsObject(current)
                this.Reason := "foreground_identity_unknown"
            else if !this.Policy.SameTarget(bound, current)
                this.Reason := "target_changed"
            else if !this.Policy.AllowsContext(this.Action, bound) || !this.Policy.AllowsContext(this.Action, current)
                this.Reason := "policy_denied_at_recheck"
            else
                this.Reason := result ? "callback_completed" : "callback_not_reached"
            if IsObject(current)
                this.Recheck := this.Policy.SameTarget(bound, current) ? "same_target" : "target_changed"
            return result
        } catch Error as err {
            this.Reason := this.CallbackFailed ? "callback_exception" : "provider_exception"
            this.Recheck := IsObject(this.LastContext)
                ? (this.Policy.SameTarget(bound, this.LastContext) ? "same_target" : "target_changed") : "identity_unknown"
            throw err
        } finally
            this.Sink.Call(this, "release", before)
    }
}
