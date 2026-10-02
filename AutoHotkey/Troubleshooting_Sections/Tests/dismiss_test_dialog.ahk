#Requires AutoHotkey v2.0
if A_Args.Length {
    dialog := WinExist("Save failed ahk_pid " Integer(A_Args[1]))
    if dialog {
        FileAppend(ControlGetText("Static1", dialog) "`n", "*")
        WinClose(dialog)
    }
}
ExitApp()
