#Requires AutoHotkey v2.0

class MagneticWindowFollower {
    __New() {
        this.IntervalMs := 16
        this.Attraction := 0.018
        this.Damping := 0.84
        this.MaxSpeed := 32.0
        this.DeadZone := 18.0
        this.CursorGap := 28
        this.Hwnd := 0
        this.VelocityX := 0.0
        this.VelocityY := 0.0
        this.Running := false
        this.LastError := ""
        this.TickCallback := ObjBindMethod(this, "Tick")
    }

    Start(hwnd) {
        if !hwnd || !WinExist(hwnd)
            return false

        ; A maximized or minimized window cannot provide useful visible chase
        ; behavior. Restore it before movement begins.
        if WinGetMinMax(hwnd) != 0
            WinRestore hwnd

        this.Hwnd := hwnd
        this.VelocityX := 0.0
        this.VelocityY := 0.0
        this.LastError := ""
        this.Running := true
        SetTimer this.TickCallback, this.IntervalMs
        return true
    }

    Stop() {
        if this.Running
            SetTimer this.TickCallback, 0

        this.Running := false
        this.Hwnd := 0
        this.VelocityX := 0.0
        this.VelocityY := 0.0
    }

    Tick() {
        if !this.Running
            return

        hwnd := this.Hwnd
        if !hwnd || !WinExist(hwnd) {
            this.Stop()
            return
        }

        try {
            ; WinMove normally applies AutoHotkey's window-operation delay.
            ; This timer is already rate-limited, so remove that extra delay to
            ; avoid visible stutter/flicker while following the pointer.
            SetWinDelay -1
            CoordMode "Mouse", "Screen"

            if WinGetMinMax(hwnd) != 0 {
                this.Stop()
                return
            }

            MouseGetPos &mouseX, &mouseY
            WinGetPos &winX, &winY, &winWidth, &winHeight, hwnd

            monitorIndex := this.MonitorFromPoint(mouseX, mouseY)
            MonitorGetWorkArea monitorIndex, &workLeft, &workTop, &workRight, &workBottom

            targetX := mouseX - (winWidth / 2)
            if mouseY + this.CursorGap + winHeight <= workBottom
                targetY := mouseY + this.CursorGap
            else
                targetY := mouseY - this.CursorGap - winHeight

            targetX := this.Clamp(targetX, workLeft, Max(workLeft, workRight - winWidth))
            targetY := this.Clamp(targetY, workTop, Max(workTop, workBottom - winHeight))

            deltaX := targetX - winX
            deltaY := targetY - winY
            distance := Sqrt(deltaX * deltaX + deltaY * deltaY)

            if distance <= this.DeadZone {
                this.VelocityX := 0.0
                this.VelocityY := 0.0
                return
            }

            this.VelocityX := (this.VelocityX + deltaX * this.Attraction) * this.Damping
            this.VelocityY := (this.VelocityY + deltaY * this.Attraction) * this.Damping

            speed := Sqrt(this.VelocityX * this.VelocityX + this.VelocityY * this.VelocityY)
            if speed > this.MaxSpeed {
                scale := this.MaxSpeed / speed
                this.VelocityX *= scale
                this.VelocityY *= scale
            }

            nextX := this.Clamp(winX + this.VelocityX, workLeft, Max(workLeft, workRight - winWidth))
            nextY := this.Clamp(winY + this.VelocityY, workTop, Max(workTop, workBottom - winHeight))
            WinMove Round(nextX), Round(nextY), , , hwnd
        } catch Error as movementError {
            ; Desktop state can change between existence checks and a Win32
            ; operation. Never let a timer exception destabilize the shortcut.
            this.LastError := movementError.Message
            this.Stop()
        }
    }

    MonitorFromPoint(x, y) {
        monitorCount := MonitorGetCount()
        Loop monitorCount {
            MonitorGet A_Index, &left, &top, &right, &bottom
            if x >= left && x < right && y >= top && y < bottom
                return A_Index
        }
        return MonitorGetPrimary()
    }

    Clamp(value, minimum, maximum) {
        return Min(Max(value, minimum), maximum)
    }
}
