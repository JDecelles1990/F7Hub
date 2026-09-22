#Requires AutoHotkey v2.0

class F7HotkeyController {
    __New(launcher, follower, keyStateProvider := "") {
        this.Launcher := launcher
        this.Follower := follower
        this.KeyStateProvider := keyStateProvider
        this.HoldThresholdMs := 180
        this.State := "IDLE"
        this.HoldCallback := ObjBindMethod(this, "BeginHold")
    }

    OnDown() {
        ; Auto-repeat and a still-finishing prior action must not create a
        ; second threshold timer or follower session.
        if this.State == "HOLDING" && !this.Follower.Running
            this.State := "WAIT_RELEASE"
        if this.State != "IDLE"
            return

        this.State := "PENDING"
        SetTimer this.HoldCallback, -this.HoldThresholdMs
    }

    OnUp() {
        if this.State == "PENDING" {
            SetTimer this.HoldCallback, 0
            this.RunTap()
            return
        }

        if this.State == "HOLD_STARTING" || this.State == "HOLDING" || this.State == "WAIT_RELEASE" {
            this.State := "IDLE"
            this.Follower.Stop()
        }
    }

    BeginHold() {
        if this.State != "PENDING"
            return
        if !this.IsF7PhysicallyDown() {
            ; The key-up hotkey normally resolves TAP immediately. This timer
            ; fallback prevents a missed release callback from stranding the
            ; controller in PENDING state.
            this.RunTap()
            return
        }

        this.State := "HOLD_STARTING"
        try {
            ; HOLD needs a visible, validated HWND, not foreground focus.
            hwnd := this.Launcher.LaunchOrFind()
            if this.State != "HOLD_STARTING" || !this.IsF7PhysicallyDown() {
                this.Follower.Stop()
                this.State := "IDLE"
                return
            }
            physicalHoldKey := IsObject(this.KeyStateProvider) ? "" : "F7"
            if !this.Follower.Start(hwnd, physicalHoldKey)
                throw Error("F7Hub could not start magnetic window movement.")
            this.State := "HOLDING"
        } catch Error as holdError {
            this.Follower.Stop()
            ; Failure consumes this press too. Repeats cannot retry until release.
            this.State := this.IsF7PhysicallyDown() ? "WAIT_RELEASE" : "IDLE"
            this.ReportError(holdError)
        }
    }

    IsF7PhysicallyDown() {
        if IsObject(this.KeyStateProvider)
            return !!this.KeyStateProvider.Call()
        return GetKeyState("F7", "P")
    }

    RunTap() {
        this.State := "TAPPING"
        try this.Launcher.LaunchOrFocus()
        catch Error as tapError
            this.ReportError(tapError)
        finally
            this.State := "IDLE"
    }

    ReportError(actionError) {
        MsgBox actionError.Message, "F7Hub launcher", "Icon!"
    }
}
