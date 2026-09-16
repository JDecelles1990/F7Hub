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
        this.TickCallback := ObjBindMethod(this, "Tick")
    }

    Start(hwnd) {
        if !hwnd || !WinExist(hwnd)
            return false

        if WinGetMinMax(hwnd) == -1
            WinRestore hwnd

        this.Hwnd := hwnd
        this.VelocityX := 0.0
        this.VelocityY := 0.0
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
            if WinGetMinMax(hwnd) == -1 {
                this.Stop()
                return
            }

            ; Timer callbacks are separate AHK threads, so set screen coordinates
            ; explicitly before reading the pointer position.
            CoordMode "Mouse", "Screen"
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
        } catch TargetError {
            ; The window may disappear between WinExist and a subsequent call.
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
