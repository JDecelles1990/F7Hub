#Requires AutoHotkey v2.0
#Include ..\..\AutoHotkey\Helpers\MagneticWindowFollower.ahk

resultPath := A_Temp "\F7Hub-test_magnetic_window_follower.txt"
try FileDelete resultPath

follower := MagneticWindowFollower()
testExitCode := 0
window := 0

try {
    TestBoundedTransitions()
    Assert(!follower.Start(0), "Follower accepted an invalid window handle")

    window := Gui(, "F7Hub Magnetic Follower Test")
    window.Show("x100 y100 w320 h180 NoActivate")
    hwnd := window.Hwnd

    Assert(follower.Start(hwnd), "Follower did not start for a valid window")
    Assert(follower.Running, "Follower running state was not set")
    Assert(follower.Hwnd == hwnd, "Follower did not retain the target window")
    Assert(!follower.Start(hwnd), "Follower accepted a duplicate start")

    Sleep 120
    Assert(WinExist(hwnd), "Follower destroyed the target window")
    Assert(follower.LastError == "", "Follower timer failed: " follower.LastError)

    follower.Stop()
    Assert(!follower.Running, "Follower did not stop")
    Assert(follower.Hwnd == 0, "Follower retained a stale window handle")
    Assert(follower.VelocityX == 0 && follower.VelocityY == 0, "Follower retained velocity after stop")

    rejectingFollower := MagneticWindowFollower(RejectWindow)
    Assert(!rejectingFollower.Start(hwnd), "Follower accepted a window rejected by its validator")

    Assert(follower.Start(hwnd, "F24"), "Follower did not start physical-release test")
    follower.Tick()
    Assert(!follower.Running, "Follower ignored release of its physical hold key")

    Assert(follower.Start(hwnd), "Follower did not restart after release")
    window.Destroy()
    window := 0
    follower.Tick()
    Assert(!follower.Running, "Follower did not stop after its HWND disappeared")

    follower.VelocityX := follower.MaxSpeed * 4
    follower.VelocityY := follower.MaxSpeed * 3
    follower.LimitVelocity()
    speed := Sqrt(follower.VelocityX ** 2 + follower.VelocityY ** 2)
    Assert(Abs(speed - follower.MaxSpeed) < 0.001, "Follower did not clamp maximum velocity")
    Assert(follower.InsideDeadZone(follower.DeadZone), "Dead-zone boundary was excluded")
    Assert(!follower.InsideDeadZone(follower.DeadZone + 0.01), "Dead zone exceeded its boundary")

    Assert(follower.Clamp(5, 0, 10) == 5, "Clamp changed an in-range value")
    Assert(follower.Clamp(-5, 0, 10) == 0, "Clamp failed the lower boundary")
    Assert(follower.Clamp(15, 0, 10) == 10, "Clamp failed the upper boundary")

    Loop MonitorGetCount() {
        MonitorGet A_Index, &left, &top, &right, &bottom
        Assert(follower.MonitorFromPoint(left, top) == A_Index, "Monitor lookup failed at work-area coordinates")
    }

    Report("PASS: invalid/validator rejection, duplicate-start prevention, start/stop lifecycle, physical release, HWND disappearance, velocity reset, dead zone, maximum velocity and multi-monitor clamp helpers.")
} catch Error as testError {
    Report("FAIL: " testError.Message " | What=" testError.What " | Line=" testError.Line)
    testExitCode := 1
} finally {
    follower.Stop()
    if IsObject(window)
        window.Destroy()
}

ExitApp testExitCode

Assert(condition, message) {
    if !condition
        throw Error(message)
}

Report(message) {
    global resultPath
    FileAppend message "`n", resultPath, "UTF-8"
}

RejectWindow(*) {
    return false
}

; Override only desktop input. Every step runs the production Tick/WinMove
; path and measures the real HWND afterward, independent of monitor layout.
class GeometryFollower extends MagneticWindowFollower {
    ReadCursorWorkArea(&mouseX, &mouseY, &left, &top, &right, &bottom) {
        mouseX := this.Geometry[1], mouseY := this.Geometry[2]
        left := this.Geometry[3], top := this.Geometry[4]
        right := this.Geometry[5], bottom := this.Geometry[6]
    }
}

TestBoundedTransitions() {
    probe := Gui(, "F7Hub bounded displacement test")
    subject := GeometryFollower()
    subject.IntervalMs := 60000 ; Tick is driven explicitly, not by wall time.
    try {
        probe.Show("x100 y30 w320 h180 NoActivate")
        cases := [
            ["review disjoint negative oversized", 100, 30, 1180, 792, 2124, -800, 1599, -1680, 2649, -48],
            ["same monitor", 100, 30, 320, 180, 900, 500, 0, 0, 1600, 1000],
            ["disjoint right", 100, 30, 320, 180, 3500, 500, 3000, 0, 4600, 1000],
            ["disjoint above", 100, 30, 320, 180, -600, -2000, -1200, -2600, 400, -1600],
            ["oversized both axes", 100, 30, 1180, 792, 2400, -700, 2200, -900, 2600, -500],
            ["overlapping work areas", 100, 30, 320, 180, 700, 400, 400, -100, 1800, 900]]
        for geometry in cases {
            subject.Stop()
            WinMove geometry[2], geometry[3], geometry[4], geometry[5], probe.Hwnd
            WinGetPos &x, &y, &width, &height, probe.Hwnd
            Assert(x == geometry[2] && y == geometry[3] && width == geometry[4] && height == geometry[5], "Test geometry was not applied")
            subject.Geometry := [geometry[6], geometry[7], geometry[8], geometry[9], geometry[10], geometry[11]]
            left := geometry[8], top := geometry[9]
            maxX := Max(left, geometry[10] - width), maxY := Max(top, geometry[11] - height)
            targetX := Min(Max(geometry[6] - width / 2, left), maxX)
            rawY := geometry[7] + subject.CursorGap + height <= geometry[11]
                ? geometry[7] + subject.CursorGap : geometry[7] - subject.CursorGap - height
            targetY := Min(Max(rawY, top), maxY)
            Assert(subject.Start(probe.Hwnd), "Geometry follower failed to start")
            ; Include stale momentum opposite the new target on one geometry.
            if geometry[1] == "overlapping work areas"
                subject.VelocityX := -subject.MaxSpeed
            Loop 600 {
                previousDistance := Sqrt((targetX - x) ** 2 + (targetY - y) ** 2)
                subject.Tick()
                WinGetPos &nextX, &nextY, , , probe.Hwnd
                displacement := Sqrt((nextX - x) ** 2 + (nextY - y) ** 2)
                Assert(subject.Running && subject.LastError == "", "Production Tick stopped unexpectedly")
                Assert(displacement <= subject.MaxSpeed + Sqrt(0.5), geometry[1] ": actual step exceeded speed cap: " displacement)
                distance := Sqrt((targetX - nextX) ** 2 + (targetY - nextY) ** 2)
                Assert(distance <= previousDistance + 0.001, geometry[1] ": step moved away from target")
                if A_Index == 1 {
                    Assert(distance < previousDistance, geometry[1] ": first tick made no progress")
                    Report("PASS: " geometry[1] " first actual displacement=" displacement " px; cap=32; tolerance=" Sqrt(0.5))
                }
                x := nextX, y := nextY
            }
            Assert(x >= left && x <= maxX && y >= top && y <= maxY, geometry[1] ": did not settle inside destination bounds")
            if width > geometry[10] - left
                Assert(x == left, "Oversized width did not align to start edge")
            if height > geometry[11] - top
                Assert(y == top, "Oversized height did not align to start edge")
            subject.Tick()
            WinGetPos &settledX, &settledY, , , probe.Hwnd
            Assert(settledX == x && settledY == y, "Settled position oscillated")
        }
    } finally {
        subject.Stop()
        probe.Destroy()
    }
}
