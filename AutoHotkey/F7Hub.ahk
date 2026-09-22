#Requires AutoHotkey v2.0
#SingleInstance Ignore
#MaxThreadsPerHotkey 1
#Include Launchers\F7HubLauncher.ahk
#Include Helpers\MagneticWindowFollower.ahk
#Include Hotkeys\F7HotkeyController.ahk

SplitPath A_ScriptDir, , &projectRoot
launcher := F7HubLauncher(projectRoot)
follower := MagneticWindowFollower(ObjBindMethod(launcher, "IsF7HubWindow"))
f7Controller := F7HotkeyController(launcher, follower)
A_IconTip := "F7Hub - tap F7 to launch/focus, hold F7 to follow mouse"

F7:: {
    global f7Controller
    f7Controller.OnDown()
}

F7 up:: {
    global f7Controller
    f7Controller.OnUp()
}
