#Requires AutoHotkey v2.0

; Events must observe trigger-down and releases even in ineligible contexts.
; The future host owns registration; CP-01 includes this only in test fixtures.
class ClipboardChord {
    __New(kind := "CTRL_ALT") {
        if kind != "CTRL_ALT" && kind != "WIN_ALT"
            throw ValueError("Unsupported Clipboard chord")
        this.Kind := kind
    }
}

; A callback may return this marker after starting bounded asynchronous work.
; The owner must call Complete() once that work has ended.
class ClipboardAsyncPending {
}

class ClipboardPressCycleController {
    __New(action, triggerKey, policy, callback, contextProvider := "", keyProvider := "", chord := "") {
        if !policy.Exclusions.Has(action)
            throw ValueError("Unknown Clipboard action")
        if chord == ""
            chord := ClipboardChord()
        if Type(chord) != "ClipboardChord"
            throw ValueError("Invalid Clipboard chord")
        chord := ClipboardChord(chord.Kind)
        if action == "clipboard.paste_latest" && chord.Kind != "WIN_ALT"
            throw ValueError("Latest paste requires Win+Alt chord")
        this.Action := action
        this.TriggerKey := triggerKey
        this.Policy := policy
        this.Callback := callback
        this.ContextProvider := IsObject(contextProvider) ? contextProvider : ObjBindMethod(policy, "ReadForeground")
        this.KeyProvider := IsObject(keyProvider) ? keyProvider : (key) => GetKeyState(key, "P")
        this.Chord := chord
        this.State := "IDLE"
        this.Pending := 0
        this.Cancelled := false
        this.WinMask := 0
        this.ObservedWinMask := 0
    }

    IsEligible() {
        ; Contextual suppression only for an eligible chord. Does not latch.
        try return this.ChordDown()
            && this.Policy.AllowsContext(this.Action, this.ContextProvider.Call())
        catch Error
            return false
    }

    ChordDown() {
        if this.Chord.Kind == "WIN_ALT"
            return this.KeyProvider.Call("Alt")
                && (this.KeyProvider.Call("LWin") || this.KeyProvider.Call("RWin"))
                && !this.KeyProvider.Call("Ctrl") && !this.KeyProvider.Call("Shift")
        return this.KeyProvider.Call("Ctrl") && this.KeyProvider.Call("Alt")
            && !this.KeyProvider.Call("Shift") && !this.KeyProvider.Call("LWin")
            && !this.KeyProvider.Call("RWin")
    }

    HasExtraModifier() {
        if this.KeyProvider.Call("Shift")
            return true
        if this.Chord.Kind == "WIN_ALT" {
            current := (this.KeyProvider.Call("LWin") ? 1 : 0)
                | (this.KeyProvider.Call("RWin") ? 2 : 0)
            return this.KeyProvider.Call("Ctrl") || (current & ~this.WinMask) != 0
        }
        return this.KeyProvider.Call("LWin") || this.KeyProvider.Call("RWin")
    }

    ObserveModifiers(key := "", isDown := true) {
        ; The future host forwards both Win transitions. A key-state snapshot
        ; alone cannot distinguish a held Win key from its release/re-press.
        Critical "On"
        try {
            if this.State == "WAIT_RELEASE" && this.Chord.Kind == "WIN_ALT"
                && (key == "LWin" || key == "RWin") {
                bit := key == "LWin" ? 1 : 2
                if isDown {
                    if !(this.ObservedWinMask & bit)
                        this.Pending := 0
                    this.ObservedWinMask |= bit
                } else
                    this.ObservedWinMask &= ~bit
            }
            if this.State == "WAIT_RELEASE" && this.HasExtraModifier() {
                this.Pending := 0
                return false
            }
            return this.State == "WAIT_RELEASE" && IsObject(this.Pending)
        } finally Critical "Off"
    }

    OnDown() {
        Critical "On"
        try {
            if this.State != "IDLE" {
                if this.State == "WAIT_RELEASE" && this.HasExtraModifier()
                    this.Pending := 0
                return false
            }
            ; Every observed trigger press is consumed, including rejection.
            this.State := "WAIT_RELEASE"
            this.Cancelled := false
            this.WinMask := (this.KeyProvider.Call("LWin") ? 1 : 0)
                | (this.KeyProvider.Call("RWin") ? 2 : 0)
            this.ObservedWinMask := this.WinMask
            if !this.ChordDown()
                return false
            context := this.ContextProvider.Call()
            if this.Cancelled || this.State != "WAIT_RELEASE"
                return false
            if !this.Policy.AllowsContext(this.Action, context)
                return false
            if this.Chord.Kind == "WIN_ALT"
                && (!HasProp(context, "Creation") || context.Creation == "")
                return false
            ; Copy identity fields so a provider cannot retarget the pending cycle.
            this.Pending := {Hwnd: context.Hwnd, Pid: context.Pid, Exe: context.Exe}
            if HasProp(context, "Creation")
                this.Pending.Creation := context.Creation
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
            && !this.KeyProvider.Call("Alt") && !this.KeyProvider.Call("LWin")
            && !this.KeyProvider.Call("RWin") && !this.KeyProvider.Call("Shift")
    }

    OnRelease() {
        Critical "On"
        try {
            if this.State != "WAIT_RELEASE"
                return false
            if this.HasExtraModifier()
                this.Pending := 0
            if !this.KeysReleased()
                return false
            bound := this.Pending
            this.Pending := 0
            this.State := "DISPATCHING"
            this.WinMask := 0
            this.ObservedWinMask := 0
        } finally
            Critical "Off"
        asyncPending := false
        try {
            current := this.ContextProvider.Call()
            if !this.Policy.AllowsContext(this.Action, bound)
                || !this.Policy.AllowsContext(this.Action, current)
                || !this.Policy.SameTarget(bound, current)
                return false
            ; Cancellation during a reentrant context/policy check must win.
            ; Keep the final validity check and dispatch in one critical region.
            Critical "On"
            try {
                if this.State != "DISPATCHING" || this.Cancelled || !IsObject(bound)
                    return false
                outcome := this.Callback.Call(this.Action, bound)
            } finally Critical "Off"
            if Type(outcome) == "ClipboardAsyncPending" {
                asyncPending := true
                return true
            }
            return true
        } finally {
            Critical "On"
            try {
                if !asyncPending {
                    this.State := this.KeysReleased() ? "IDLE" : "WAIT_RELEASE"
                }
            }
            finally
                Critical "Off"
        }
    }

    Complete() {
        Critical "On"
        try {
            if this.State != "DISPATCHING"
                return false
            this.State := this.KeysReleased() ? "IDLE" : "WAIT_RELEASE"
            this.Cancelled := false
            return true
        } finally Critical "Off"
    }

    Cancel() {
        ; Cancellation clears work, never rearms a still-held physical cycle.
        Critical "On"
        try {
            this.Pending := 0
            this.WinMask := 0
            this.ObservedWinMask := 0
            this.Cancelled := true
            if this.State == "DISPATCHING"
                return
            else {
                this.State := "WAIT_RELEASE"
                this.State := this.KeysReleased() ? "IDLE" : "WAIT_RELEASE"
            }
        } finally
            Critical "Off"
    }
}
