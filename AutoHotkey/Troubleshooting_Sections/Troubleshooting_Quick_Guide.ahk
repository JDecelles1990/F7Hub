#Requires AutoHotkey v2.0
#SingleInstance Off
#Include GuideRequest.ahk

; Short-lived client: only F7Hub.ahk owns hotkeys and guide data.
try {
    if A_Args.Length > 1 || (A_Args.Length = 1 && A_Args[1] != "--show")
        throw Error("Usage: Troubleshooting_Quick_Guide.ahk [--show]")
    SplitPath(A_ScriptDir, , &ahkRoot)
    result := RequestGuide(ahkRoot "\F7Hub.ahk", A_Args.Length = 1)
    WriteGuideClientOutput(result)
    ExitApp(0)
} catch Error as requestError {
    if A_Args.Length
        WriteGuideClientOutput(requestError.Message, "**")
    else
        MsgBox(requestError.Message, "AltF7Hub could not start", 48)
    ExitApp(1)
}
