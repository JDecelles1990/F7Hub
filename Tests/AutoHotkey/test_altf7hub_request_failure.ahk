#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../../AutoHotkey/Troubleshooting_Sections/GuideRequest.ahk

global Passed := 0
fixtureHost := A_ScriptDir "\fixtures\guide_request_host.ahk"
counter := A_Temp "\F7Hub-s046-requests-" DllCall("GetCurrentProcessId") ".txt"
pid := 0
try {
    for mode in ["reject", "slow"] {
        if FileExist(counter)
            FileDelete(counter)
        Run('"' A_AhkPath '" /ErrorStdOut=UTF-8 "' fixtureHost '" ' mode ' "' counter '"', , "Hide", &pid)
        deadline := A_TickCount + 3000
        while !FindGuideEndpoint(fixtureHost) && A_TickCount < deadline
            Sleep(25)
        Check(FindGuideEndpoint(fixtureHost) != 0, "Fake host ready")
        start := A_TickCount
        failed := false
        try RequestGuide(fixtureHost)
        catch Error as err
            failed := InStr(err.Message, "not confirmed") != 0
        Check(failed, "Rejected or timed-out presentation is unconfirmed")
        if mode = "slow"
            Check(A_TickCount - start >= 2900 && A_TickCount - start < 3800, "Dispatched request has bounded three-second wait")
        Sleep(mode = "slow" ? 1200 : 50)
        events := FileRead(counter)
        Check(events = "REQUEST`n", "No retry or keyboard fallback after dispatch")
        ProcessClose(pid)
        ProcessWaitClose(pid, 3)
        pid := 0
    }
    FileAppend("ALL CHECKS PASSED: " Passed "`n", "*")
    code := 0
} catch Error as err {
    FileAppend("FAIL Request failure: " err.Message " at " err.File ":" err.Line "`n", "*")
    code := 1
} finally {
    if pid && ProcessExist(pid)
        ProcessClose(pid)
    if FileExist(counter)
        FileDelete(counter)
}
ExitApp(code)
Check(condition, label) {
    global Passed
    if !condition
        throw Error(label)
    Passed++
}
