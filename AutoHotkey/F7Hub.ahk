#Requires AutoHotkey v2.0
#SingleInstance Ignore
#MaxThreadsPerHotkey 1
#Include Launchers\F7HubLauncher.ahk

SplitPath A_ScriptDir, , &projectRoot
launcher := F7HubLauncher(projectRoot)
A_IconTip := "F7Hub - press F7 to launch or focus"

F7:: {
    global launcher
    try launcher.LaunchOrFocus()
    catch Error as launchError
        MsgBox launchError.Message, "F7Hub launcher", "Icon!"
}
