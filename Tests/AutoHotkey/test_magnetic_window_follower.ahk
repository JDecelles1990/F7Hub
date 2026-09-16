#Requires AutoHotkey v2.0
#Include ..\..\AutoHotkey\Helpers\MagneticWindowFollower.ahk

follower := MagneticWindowFollower()
testExitCode := 0
window := 0

try {
    Assert(!follower.Start(0), "Follower accepted an invalid window handle")

    window := Gui(, "F7Hub Magnetic Follower Test")
    window.Show("x100 y100 w320 h180 NoActivate")
    hwnd := window.Hwnd

    Assert(follower.Start(hwnd), "Follower did not start for a valid window")
    Assert(follower.Running, "Follower running state was not set")
    Assert(follower.Hwnd == hwnd, "Follower did not retain the target window")

    Sleep 80
    Assert(WinExist(hwnd), "Follower destroyed the target window")

    follower.Stop()
    Assert(!follower.Running, "Follower did not stop")
    Assert(follower.Hwnd == 0, "Follower retained a stale window handle")
    Assert(follower.VelocityX == 0 && follower.VelocityY == 0, "Follower retained velocity after stop")

    Assert(follower.Clamp(5, 0, 10) == 5, "Clamp changed an in-range value")
    Assert(follower.Clamp(-5, 0, 10) == 0, "Clamp failed the lower boundary")
    Assert(follower.Clamp(15, 0, 10) == 10, "Clamp failed the upper boundary")

    FileAppend "PASS: invalid target rejection, start/stop lifecycle, safe timer tick, velocity reset and clamp boundaries.`n", "*"
} catch Error as testError {
    FileAppend "FAIL: " testError.Message "`n", "*"
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
