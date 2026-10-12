#Requires AutoHotkey v2.0
#SingleInstance Off
#NoTrayIcon
#Include cp01_harness_support.ahk
; Test-owned empty window. Observe native F23/F24 delivery without forwarding.
if A_Args.Length != 3
    ExitApp 2
readyPath := A_Args[1], inputPath := A_Args[2], token := A_Args[3]
Persistent true
target := Gui("+ToolWindow", "CP-01 synthetic target")
target.AddEdit("w300 h100", "Synthetic target; no Clipboard data")
target.Show("Hide w330 h150")
OnExit (*) => target.Destroy()
OnMessage(0x100, RecordKey)
OnMessage(0x104, RecordKey)
Cp01Ready.Publish(readyPath, token, target.Hwnd, DllCall("GetCurrentProcessId"))
RecordKey(wParam, *) {
    global inputPath
    if wParam == 0x86 || wParam == 0x87
        FileAppend(wParam "`n", inputPath, "UTF-8")
}
