#Requires AutoHotkey v2.0
#SingleInstance Ignore
#MaxThreadsPerHotkey 1
#Include Launchers\F7HubLauncher.ahk
#Include Helpers\MagneticWindowFollower.ahk
#Include Hotkeys\F7HotkeyController.ahk
#Include Troubleshooting_Sections\GuideHost.ahk

SplitPath A_ScriptDir, , &projectRoot
launcher := F7HubLauncher(projectRoot)
follower := MagneticWindowFollower(ObjBindMethod(launcher, "IsF7HubWindow"))
f7Controller := F7HotkeyController(launcher, follower)
InitializeGuideHost(A_ScriptDir "\Troubleshooting_Sections", A_ScriptFullPath)
A_IconTip := "F7Hub - F7: launch/follow; Alt+F7: Help Desk & Interview Guide"

F7:: {
    global f7Controller
    f7Controller.OnDown()
}

F7 up:: {
    global f7Controller
    f7Controller.OnUp()
}

; Use the hook so this host owns its shortcut while an older standalone copy
; is still registered. Requests still target the exact checkout endpoint.
$!F7::ToggleGuide()
#HotIf IsObject(Guide) && WinActive("ahk_id " Guide.Hwnd)
$^f::FocusSearch()
^l::ShowSidebar()
^PgUp::NavigateTopic(-1)
^PgDn::NavigateTopic(1)
Esc::Guide.Hide()
#HotIf

; ListBox's native dialog navigation can precede WM_KEYDOWN monitors. Scoped
; hotkeys consume physical arrows before native navigation, including repeats.
#HotIf GuideNavigationFocused()
Up::HandleGuideKeys(0x26, 0, 0x100, 0)
Down::HandleGuideKeys(0x28, 0, 0x100, 0)
Left::HandleGuideKeys(0x25, 0, 0x100, 0)
Right::HandleGuideKeys(0x27, 0, 0x100, 0)
#HotIf
