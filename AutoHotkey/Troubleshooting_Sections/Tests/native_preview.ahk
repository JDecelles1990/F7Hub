#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../GuideCore.ahk

global EvidenceRoot := A_ScriptDir "\Evidence", SourceRoot := A_ScriptDir "\.."
global PreviewFixture := A_Temp "\HelpDeskGuide-preview-" DllCall("GetCurrentProcessId") "-" A_TickCount
global LastCommand := "", BackgroundGui := 0, PreviewClock := 0
DirCreate(EvidenceRoot)
DataRoot := PreviewFixture
DirCreate(DataRoot)
DirCreate(DataRoot "\Archive")
Loop Files SourceRoot "\*.txt"
    FileCopy(A_LoopFileFullPath, DataRoot "\" A_LoopFileName)
Loop Files SourceRoot "\Archive\*.txt"
    FileCopy(A_LoopFileFullPath, DataRoot "\Archive\" A_LoopFileName)
LoadTopics()
OnMessage(0x100, HandleGuideKeys)
OnMessage(0x111, HandleEditorChange)
OnMessage(0x2B, DrawTopicItem)
OnMessage(0x2C, MeasureTopicItem)
OnError(PreviewError)
BackgroundGui := Gui("-Caption +ToolWindow", "Simulated video call backdrop")
BackgroundGui.BackColor := "E3EEF4"
BackgroundGui.SetFont("s22 c172A38", "Segoe UI")
BackgroundGui.AddText("x40 y24 w1100", "SIMULATED CALL • animated backdrop • no camera access")
BackgroundGui.SetFont("s140", "Segoe UI Emoji")
BackgroundGui.AddText("x90 y160 w320 h280 BackgroundBCDCD1 Center", "🧑")
BackgroundGui.AddText("x680 y160 w320 h280 BackgroundC7D8EF Center", "👩")
BackgroundGui.SetFont("s24 c172A38", "Segoe UI")
BackgroundGui.AddText("x100 y470 w320 Center", "Caller")
BackgroundGui.AddText("x680 y470 w320 Center", "Colleague")
PreviewClock := BackgroundGui.AddText("x40 y620 w1100", "Preview")
BackgroundGui.Show("x0 y0 w" A_ScreenWidth " h" A_ScreenHeight)
CreateGuide()
ShowTopic("methodology")
Pinned := true
PinCheck.Value := 1
ApplyPin()
SetTimer(PreviewCommand, 100)
SetTimer(() => PreviewClock.Text := "Simulated video frame • " FormatTime(, "HH:mm:ss"), 500)
SetTimer(StopPreview, -300000)
FileAppend("NATIVE_PREVIEW_READY`n", "*")

PreviewCommand() {
    global LastCommand, Opacity, HeadingColor, HeadingBold
    commandPath := EvidenceRoot "\preview-command.txt"
    if !FileExist(commandPath)
        return
    request := Trim(FileRead(commandPath, "UTF-8"))
    if request = LastCommand
        return
    LastCommand := request
    command := StrSplit(request, "|")[1]
    if command = "stop" {
        StopPreview()
        return
    }
    if IsObject(EditorGui)
        CloseEditor()
    if command = "picker" {
        ; Open the actual Windows color chooser, with a real text selection.
        SetSelection(NotesBox, 0, 6)
        SetTimer(() => WritePreviewState(command), -500)
        ChangeHeadingColor()
        return
    }
    if command = "editor" {
        ShowTopic("methodology")
        ShowEditor("edit")
        WritePreviewState(command)
        return
    }
    if InStr(command, "max")
        Guide.Maximize()
    else {
        Guide.Restore()
        Guide.Show("x40 y70 w" (InStr(command, "small") ? 860 : 1045) " h" (InStr(command, "small") ? 560 : 620))
    }
    if RegExMatch(command, "^(70|85|100)", &m) {
        OpacitySlider.Value := Integer(m[1])
        ChangeOpacity()
    }
    shouldHide := !!InStr(command, "hidden")
    AutoFitCheck.Value := !!InStr(command, "auto")
    ChangeAutoFit()
    if SidebarHidden != shouldHide
        ToggleSidebar()
    ShowTopic(InStr(command, "interview") ? "interview-personal" : InStr(command, "fortigate") ? "fortigate" : "methodology")
    WinActivate("ahk_id " Guide.Hwnd)
    Sleep(150)
    WritePreviewState(command)
}
WritePreviewState(command) {
    Guide.GetPos(&x, &y, &w, &h)
    state := "command=" command "`nrequest=" LastCommand "`nhwnd=" Guide.Hwnd "`nx=" x "`ny=" y "`nwidth=" w "`nheight=" h
        . "`nfont=" CurrentFontSize "`nopacity=" Opacity "`ndpi=" DllCall("GetDpiForWindow", "Ptr", Guide.Hwnd)
        . "`nscreen=" A_ScreenWidth "x" A_ScreenHeight "`nfixture=" PreviewFixture "`n"
    WriteUtf8(EvidenceRoot "\preview-state.txt", state)
}
StopPreview(*) {
    if IsObject(EditorGui)
        CloseEditor()
    Guide.Destroy()
    BackgroundGui.Destroy()
    if InStr(PreviewFixture, A_Temp "\HelpDeskGuide-preview-") = 1
        DirDelete(PreviewFixture, true)
    ExitApp()
}
PreviewError(err, *) {
    FileAppend("FAIL " err.Message " at " err.File ":" err.Line "`n", "*")
    ExitApp(1)
}
