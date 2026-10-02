#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../../../AutoHotkey/Troubleshooting_Sections/GuideRequest.ahk

if A_Args.Length != 2
    ExitApp(2)
global SlowResponse := A_Args[1] = "slow", CounterPath := A_Args[2]
message := DllCall("RegisterWindowMessageW", "Str", "F7Hub.AltF7Hub.Show.v1", "UInt")
OnMessage(message, FakeResponse)
global Endpoint := Gui(, GuideEndpointTitle(A_ScriptFullPath))
!F7::FileAppend("TOGGLE`n", CounterPath)

FakeResponse(*) {
    FileAppend("REQUEST`n", CounterPath)
    if SlowResponse
        Sleep(4000)
    return 0
}
