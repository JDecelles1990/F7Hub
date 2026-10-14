#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../../AutoHotkey/Troubleshooting_Sections/GuideRequest.ahk

global Passed := 0
fixtureHost := A_ScriptDir "\fixtures\guide_request_host.ahk"
counter := A_Temp "\F7Hub-s046-requests-" DllCall("GetCurrentProcessId") ".txt"
pid := 0
try {
    ; An exact-title Guide in another process and substring decoys in the host
    ; must never satisfy a positive ACK. The test's Guide is deliberately visible.
    otherGuide := Gui(, "Guide")
    otherGuide.Show("w240 h100")
    ownPid := DllCall("GetCurrentProcessId")
    Check(FindGuideWindow(ownPid, "Guide") = otherGuide.Hwnd, "Exact owned title accepted")
    Check(!FindGuideWindow(ownPid, "guide"), "Title comparison is case-sensitive")
    otherGuide.Hide()
    Check(!FindGuideWindow(ownPid, "Guide"), "Hidden window cannot confirm visible presentation")
    DetectHiddenWindows(true)
    Check(FindGuideWindow(ownPid, "Guide", false) = otherGuide.Hwnd, "Hidden exact window available to guarded fallback")
    DetectHiddenWindows(false)
    otherGuide.Show()
    for mode in ["reject", "slow", "decoy-guide", "decoy-editor", "wrong-process"] {
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
