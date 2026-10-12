#Requires AutoHotkey v2.0

; Events must observe trigger-down and releases even in ineligible contexts.
; The future host owns registration; CP-01 includes this only in test fixtures.
class ClipboardPressCycleController {
    __New(action, triggerKey, policy, callback, contextProvider := "", keyProvider := "") {
        if !policy.Exclusions.Has(action)
            throw ValueError("Unknown Clipboard action")
        this.Action := action
        this.TriggerKey := triggerKey
        this.Policy := policy
        this.Callback := callback
        this.ContextProvider := IsObject(contextProvider) ? contextProvider : ObjBindMethod(policy, "ReadForeground")
        this.KeyProvider := IsObject(keyProvider) ? keyProvider : (key) => GetKeyState(key, "P")
        this.State := "IDLE"
        this.Pending := 0
    }

    IsEligible() {
        ; Contextual suppression only for an eligible chord. Does not latch.
        try return this.ChordDown()
            && this.Policy.AllowsContext(this.Action, this.ContextProvider.Call())
        catch Error
            return false
    }

    ChordDown() {
        return this.KeyProvider.Call("Ctrl") && this.KeyProvider.Call("Alt")
            && !this.KeyProvider.Call("Shift") && !this.KeyProvider.Call("LWin")
            && !this.KeyProvider.Call("RWin")
    }

    OnDown() {
        Critical "On"
        try {
            if this.State != "IDLE"
                return false
            ; Every observed trigger press is consumed, including rejection.
            this.State := "WAIT_RELEASE"
            if !this.ChordDown()
                return false
            context := this.ContextProvider.Call()
            if !this.Policy.AllowsContext(this.Action, context)
                return false
            ; Copy identity fields so a provider cannot retarget the pending cycle.
            this.Pending := {Hwnd: context.Hwnd, Pid: context.Pid, Exe: context.Exe}
            return true
        } catch Error {
            this.Pending := 0
            return false
        } finally
            Critical "Off"
    }

    KeysReleased() {
        ; Generic modifier states cover both sides and either release order.
        return !this.KeyProvider.Call(this.TriggerKey) && !this.KeyProvider.Call("Ctrl")
            && !this.KeyProvider.Call("Alt")
    }

    OnRelease() {
        Critical "On"
        try {
            if this.State != "WAIT_RELEASE" || !this.KeysReleased()
                return false
            bound := this.Pending
            this.Pending := 0
            this.State := "DISPATCHING"
        } finally
            Critical "Off"
        try {
            current := this.ContextProvider.Call()
            if !this.Policy.AllowsContext(this.Action, bound)
                || !this.Policy.AllowsContext(this.Action, current)
                || !this.Policy.SameTarget(bound, current)
                return false
            ; Immediate pre-effect recheck seam. CP-01 callbacks are counters only.
            this.Callback.Call(this.Action, bound)
            return true
        } finally {
            Critical "On"
            this.State := "WAIT_RELEASE"
            try this.State := this.KeysReleased() ? "IDLE" : "WAIT_RELEASE"
            finally
                Critical "Off"
        }
    }

    Cancel() {
        ; Cancellation clears work, never rearms a still-held physical cycle.
        Critical "On"
        try {
            this.Pending := 0
            if this.State != "DISPATCHING" {
                this.State := "WAIT_RELEASE"
                this.State := this.KeysReleased() ? "IDLE" : "WAIT_RELEASE"
            }
        } finally
            Critical "Off"
    }
}
