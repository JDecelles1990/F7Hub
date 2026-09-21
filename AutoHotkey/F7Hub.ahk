#Requires AutoHotkey v2.0
#SingleInstance Ignore
#MaxThreadsPerHotkey 1
#Include Launchers\F7HubLauncher.ahk
#Include Helpers\MagneticWindowFollower.ahk

SplitPath A_ScriptDir, , &projectRoot
launcher := F7HubLauncher(projectRoot)
follower := MagneticWindowFollower()
A_IconTip := "F7Hub - tap F7 to launch/focus, hold F7 to follow mouse"

F7:: {
    global launcher, follower

    holdThresholdSeconds := 0.18

    try {
        if !KeyWait("F7", "T" holdThresholdSeconds) {
            hwnd := launcher.LaunchOrFocus()
            follower.Start(hwnd)
            KeyWait "F7"
            follower.Stop()
            return
        }

        launcher.LaunchOrFocus()
    } catch Error as launchError {
        follower.Stop()
        MsgBox launchError.Message, "F7Hub launcher", "Icon!"
    }
}
