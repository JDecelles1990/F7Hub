#Requires AutoHotkey v2.0

class MagneticWindowFollower {
    __New(windowValidator := "") {
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
        this.PhysicalHoldKey := ""
        this.WindowValidator := windowValidator
        this.TickCallback := ObjBindMethod(this, "Tick")
    }

    Start(hwnd, physicalHoldKey := "") {
        if this.Running || !this.IsValidTarget(hwnd)
            return false

        ; A maximized or minimized window cannot provide useful visible chase
        ; behavior. Normalize it without requesting foreground activation.
        try {
            if WinGetMinMax(hwnd) != 0
                DllCall("ShowWindow", "Ptr", hwnd, "Int", 4) ; SW_SHOWNOACTIVATE
        } catch Error as startError {
            this.LastError := startError.Message
            return false
        }

        this.Hwnd := hwnd
        this.VelocityX := 0.0
        this.VelocityY := 0.0
        this.LastError := ""
        this.PhysicalHoldKey := physicalHoldKey
        this.Running := true
        SetTimer this.TickCallback, this.IntervalMs
        return true
    }

    Stop() {
        SetTimer this.TickCallback, 0

        this.Running := false
        this.Hwnd := 0
        this.VelocityX := 0.0
        this.VelocityY := 0.0
        this.PhysicalHoldKey := ""
    }

    Tick() {
        if !this.Running
            return

        if this.PhysicalHoldKey != "" && !GetKeyState(this.PhysicalHoldKey, "P") {
            this.Stop()
            return
        }

        hwnd := this.Hwnd
        if !this.IsValidTarget(hwnd) {
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

            WinGetPos &winX, &winY, &winWidth, &winHeight, hwnd
            this.ReadCursorWorkArea(&mouseX, &mouseY, &workLeft, &workTop, &workRight, &workBottom)

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

            if this.InsideDeadZone(distance) {
                contained := winX >= workLeft && winX <= Max(workLeft, workRight - winWidth)
                    && winY >= workTop && winY <= Max(workTop, workBottom - winHeight)
                if contained {
                    this.VelocityX := 0.0
                    this.VelocityY := 0.0
                    return
                }
                ; Finish a short approach to an edge instead of settling outside.
                this.VelocityX := deltaX
                this.VelocityY := deltaY
            } else {
                this.VelocityX := (this.VelocityX + deltaX * this.Attraction) * this.Damping
                this.VelocityY := (this.VelocityY + deltaY * this.Attraction) * this.Damping
            }
            this.LimitVelocity()

            ; Clamp only the target to the destination monitor. Intermediate
            ; steps may cross gaps; restricting each axis to current..target
            ; prevents overshoot without ever increasing the bounded step.
            nextX := this.Clamp(winX + this.VelocityX, Min(winX, targetX), Max(winX, targetX))
            nextY := this.Clamp(winY + this.VelocityY, Min(winY, targetY), Max(winY, targetY))
            nextPixelX := Round(nextX)
            nextPixelY := Round(nextY)
            if nextPixelX != winX || nextPixelY != winY
                WinMove nextPixelX, nextPixelY, , , hwnd
        } catch Error as movementError {
            ; Desktop state can change between existence checks and a Win32
            ; operation. Never let a timer exception destabilize the shortcut.
            this.LastError := movementError.Message
            this.Stop()
        }
    }

    ReadCursorWorkArea(&mouseX, &mouseY, &left, &top, &right, &bottom) {
        MouseGetPos &mouseX, &mouseY
        monitorIndex := this.MonitorFromPoint(mouseX, mouseY)
        MonitorGetWorkArea monitorIndex, &left, &top, &right, &bottom
    }

    IsValidTarget(hwnd) {
        if !hwnd || !WinExist(hwnd)
            return false
        if !IsObject(this.WindowValidator)
            return true

        try return !!this.WindowValidator.Call(hwnd)
        catch Error
            return false
    }

    InsideDeadZone(distance) {
        return distance <= this.DeadZone
    }

    LimitVelocity() {
        speed := Sqrt(this.VelocityX * this.VelocityX + this.VelocityY * this.VelocityY)
        if speed > this.MaxSpeed {
            scale := this.MaxSpeed / speed
            this.VelocityX *= scale
            this.VelocityY *= scale
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
