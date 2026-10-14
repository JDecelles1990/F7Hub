#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../../../AutoHotkey/Troubleshooting_Sections/GuideRequest.ahk

if A_Args.Length != 2
    ExitApp(2)
global ResponseMode := A_Args[1], CounterPath := A_Args[2]
global Decoy := Gui(, ResponseMode = "decoy-guide" ? "Another Guide window" : "Unrelated topic")
if InStr(ResponseMode, "decoy")
    Decoy.Show("w240 h100")
message := DllCall("RegisterWindowMessageW", "Str", "F7Hub.AltF7Hub.Show.v1", "UInt")
OnMessage(message, FakeResponse)
global Endpoint := Gui(, GuideEndpointTitle(A_ScriptFullPath))
!F7::FileAppend("TOGGLE`n", CounterPath)

FakeResponse(*) {
    FileAppend("REQUEST`n", CounterPath)
    if ResponseMode = "slow"
        Sleep(4000)
    if ResponseMode = "decoy-guide" || ResponseMode = "wrong-process"
        return 1
    if ResponseMode = "decoy-editor"
        return 2
    return 0
}
