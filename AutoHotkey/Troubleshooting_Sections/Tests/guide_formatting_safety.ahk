#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../GuideCore.ahk

; Run under an external whole-run supervisor. All writes use a private fixture;
; dialogs are closed only for this PID. No keyboard input or child processes.
global Passed := 0, FailureMessage := ""
DataRoot := A_Temp "\Guide-formatting-safety-" DllCall("GetCurrentProcessId") "-" A_TickCount
DirCreate(DataRoot)
DirCreate(DataRoot "\Archive")
OnError(TestError)
OnExit(CloseTestWindows)
LoadSettings()
CreateGuide()
Check(DllCall("IsWindow", "Ptr", Guide.Hwnd) && IsObject(NotesBox), "Native guide and Rich Edit ready")

for scenario in ["title", "body", "both", "title-case", "body-case", "archive-title", "title-no-sidecar"] {
    item := LoadFixture(scenario = "archive-title")
    title := item.Title, body := item.Body
    if InStr(scenario, "title") || scenario = "both"
        title := scenario = "title-case" ? StrLower(title) : "OUTLOOK / EMAIL — VIP SUPPORT"
    if scenario = "body" || scenario = "both" || scenario = "body-case"
        body := scenario = "body-case" ? StrLower(body) : body "`nEXTERNAL — newer notes"
    if scenario = "title-no-sidecar"
        FileDelete(item.Path ".styles.ini")
    ; Title-only fixtures keep the exact loaded body, including authored blanks.
    Check((scenario != "title" && scenario != "title-case") || body == item.Body, scenario ": identical body precondition")
    WriteUtf8(item.Path, title "`r`n" StrReplace(body, "`n", "`r`n") "`r`n")
    textBefore := FileRead(item.Path, "RAW")
    stylesBefore := FileExist(item.Path ".styles.ini") ? FileRead(item.Path ".styles.ini", "RAW") : 0
    runsBefore := StylesText(item)
    SetSelection(NotesBox, 1, 6)
    ArmFailureDialog()
    formatted := FormatSelection(false, "color", "FF0000")
    SetTimer(DismissExpectedSaveFailure, 0)
    Check(!formatted, scenario ": stale formatting rejected")
    Check(InStr(FailureMessage, "changed outside the app") && InStr(FailureMessage, "before formatting"), scenario ": understandable stale-source message")
    Check(SameBytes(item.Path, textBefore), scenario ": external topic bytes preserved")
    after := ReadTopic(item.Path, ArchiveMode)
    Check(after.Title == title && after.Body == body, scenario ": external title and body preserved")
    Check(IsObject(stylesBefore) ? SameBytes(item.Path ".styles.ini", stylesBefore) : !FileExist(item.Path ".styles.ini"), scenario ": no sidecar commit")
    Check(StylesText(item) == runsBefore && GetBody(NotesBox) == item.Body, scenario ": loaded formatting and context retained")
    CheckNoPendingFiles(item.Path, scenario)
}

for newline in ["`n", "`r`n"] {
    item := LoadFixture()
    WriteUtf8(item.Path, item.Title newline StrReplace(item.Body, "`n", newline) newline)
    SetSelection(NotesBox, 1, 6)
    Check(FormatSelection(false, "color", "FF55AA"), "Unchanged normalized source accepts formatting")
    reloaded := ReadTopic(item.Path)
    Check(reloaded.Title == item.Title && reloaded.Body == item.Body, "Successful save preserves title, Unicode and authored blanks")
    Check(reloaded.Runs.Length = 2 && reloaded.Runs[2].Color = "FF55AA", "New personal range persisted")
    Check(reloaded.Runs[1].Start = item.Runs[1].Start && reloaded.Runs[1].Color = "FFCC00" && reloaded.Runs[1].Bold = 1, "Existing personal range survives save and reload")
    cf := CharacterFormat(NotesBox, InStr(item.Body, "DNS") - 1)
    Check(NumGet(cf, 20, "UInt") = ColorRef("FFCC00") && (NumGet(cf, 8, "UInt") & 1), "Existing personal formatting still renders")
    cf := CharacterFormat(NotesBox, InStr(item.Body, "STATUS") - 1)
    Check(NumGet(cf, 20, "UInt") = ColorRef(HeadingColor) && (NumGet(cf, 8, "UInt") & 1), "Automatic heading style unchanged")
    SetSelection(NotesBox, 1, 6)
    Check(FormatSelection(false, "reset"), "Reset formatting still saves")
    SetSelection(NotesBox, 1, 6)
    Check(FormatSelection(false, "bold"), "Bold formatting still saves")
    bytes := FileRead(item.Path, "RAW")
    Check(bytes.Size >= 3 && NumGet(bytes, 0, "UChar") = 0xEF && NumGet(bytes, 1, "UChar") = 0xBB && NumGet(bytes, 2, "UChar") = 0xBF, "Existing UTF-8 BOM serialization retained")
    Check(!InStr(FileRead(item.Path, "UTF-8"), "`r"), "Existing LF save serialization retained")
    CheckNoPendingFiles(item.Path, "unchanged")
}

item := LoadFixture()
textBefore := FileRead(item.Path, "RAW"), stylesBefore := FileRead(item.Path ".styles.ini", "RAW")
runsBefore := StylesText(item)
locked := FileOpen(item.Path, "r-d") ; permit reads/writes, deny replacement
try {
    SetSelection(NotesBox, 1, 6)
    ArmFailureDialog()
    formatted := FormatSelection(false, "color", "FF0000")
    SetTimer(DismissExpectedSaveFailure, 0)
} finally
    locked.Close()
Check(!formatted && InStr(FailureMessage, "Formatting could not be saved"), "Failed topic replacement reports save failure")
Check(SameBytes(item.Path, textBefore), "Failed formatting save preserves topic bytes")
Check(SameBytes(item.Path ".styles.ini", stylesBefore), "Failed formatting save rolls back already replaced sidecar bytes")
Check(StylesText(item) == runsBefore, "Failed formatting save retains loaded ranges")
Check(!FileExist(item.Path ".tmp") && !FileExist(item.Path ".styles.ini.tmp"), "Failed save cleans prepared files")

; Editor formatting is deferred until SaveEditor, which already guards both fields.
for scenario in ["title", "body", "both"] {
    item := LoadFixture()
    ShowEditor("edit")
    SetSelection(EditorBody, 1, 6)
    Check(FormatSelection(true, "color", "ABCDEF"), scenario ": editor draft formatting works")
    title := scenario = "body" ? item.Title : "External editor title"
    body := scenario = "title" ? item.Body : item.Body "`nEXTERNAL — newer notes"
    WriteUtf8(item.Path, title "`n" body "`n")
    textBefore := FileRead(item.Path, "RAW"), stylesBefore := FileRead(item.Path ".styles.ini", "RAW")
    ArmFailureDialog()
    saved := SaveEditor("edit")
    SetTimer(DismissExpectedSaveFailure, 0)
    Check(!saved && InStr(FailureMessage, "changed outside the app"), scenario ": stale editor save rejected")
    Check(SameBytes(item.Path, textBefore) && SameBytes(item.Path ".styles.ini", stylesBefore), scenario ": stale editor preserves topic and sidecar bytes")
    Check(IsObject(EditorGui) && GetBody(EditorBody) == item.Body && EditorRuns[-1].Color = "ABCDEF", scenario ": formatted editor draft retained")
    CloseEditor()
}
FileAppend("ALL CHECKS PASSED: " Passed "`n", "*")
ExitApp(0)

LoadFixture(isArchive := false) {
    global ArchiveMode, Topics, Archived
    ArchiveMode := isArchive
    path := DataRoot (isArchive ? "\Archive" : "") "\format-safety.txt"
    body := "`nSCOPE — café · 🧠`n`nSTATUS — DNS · VPN`n"
    item := {Id: "format-safety", Title: "OUTLOOK / EMAIL", Body: body, Path: path, Shortcut: "",
        Runs: [{Start: InStr(body, "DNS") - 1, Length: 9, Color: "FFCC00", Bold: 1}], IsArchive: isArchive}
    WriteTopic(item)
    item := ReadTopic(path, isArchive)
    Topics := Map(), Archived := Map()
    (isArchive ? Archived : Topics)[item.Id] := item
    ShowTopic(item.Id)
    return item
}
Check(condition, label) {
    global Passed
    if !condition
        throw Error(label)
    Passed++
    FileAppend("PASS " label "`n", "*")
}
SameBytes(path, before) {
    after := FileRead(path, "RAW")
    if before.Size != after.Size
        return false
    Loop before.Size
        if NumGet(before, A_Index - 1, "UChar") != NumGet(after, A_Index - 1, "UChar")
            return false
    return true
}
CheckNoPendingFiles(path, label) {
    for suffix in [".tmp", ".styles.ini.tmp", ".rollback", ".styles.ini.rollback"]
        Check(!FileExist(path suffix), label ": no pending " suffix)
}
CharacterFormat(control, index) {
    selection := GetSelection(control)
    SetSelection(control, index, index + 1)
    cf := Buffer(116, 0)
    NumPut("UInt", cf.Size, cf)
    SendMessage(0x43A, 1, cf.Ptr, control.Hwnd)
    SetSelection(control, selection.Start, selection.End)
    return cf
}
ArmFailureDialog() {
    global FailureMessage
    FailureMessage := ""
    SetTimer(DismissExpectedSaveFailure, -50)
}
DismissExpectedSaveFailure() {
    global FailureMessage
    title := "Save failed ahk_pid " DllCall("GetCurrentProcessId")
    if WinWait(title, , 3) {
        FailureMessage := WinGetText(title)
        WinClose(title)
    }
}
TestError(err, *) {
    FileAppend("FAIL " err.Message " at " err.File ":" err.Line "`n", "*")
    ExitApp(1)
}
CloseTestWindows(*) {
    if IsObject(EditorGui)
        EditorGui.Destroy()
    if IsObject(Guide)
        Guide.Destroy()
    ; Retain isolated fixtures for byte/recovery inspection; never clean user data.
}
