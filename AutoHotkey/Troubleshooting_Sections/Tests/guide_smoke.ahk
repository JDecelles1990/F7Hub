#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../GuideCore.ahk
#Include ../GuideRequest.ahk

global Passed := 0, Suite := "Startup", SourceRoot := A_ScriptDir "\.."
global Fixture := A_Temp "\HelpDeskGuide-test-" DllCall("GetCurrentProcessId") "-" A_TickCount
OnError(TestError)
DataRoot := Fixture
DirCreate(DataRoot)
DirCreate(DataRoot "\Archive")
Loop Files SourceRoot "\*.txt"
    FileCopy(A_LoopFileFullPath, DataRoot "\" A_LoopFileName)
Loop Files SourceRoot "\Archive\*.txt"
    FileCopy(A_LoopFileFullPath, DataRoot "\Archive\" A_LoopFileName)
LoadSettings()
LoadTopics()
OnMessage(0x100, HandleGuideKeys)
OnMessage(0x111, HandleEditorChange)
OnMessage(0x2B, DrawTopicItem)
OnMessage(0x2C, MeasureTopicItem)

Suite := "Library"
Check(Topics.Count > 26, "More than 26 active topics")
Check(Topics.Has("placeholder-active") || Archived.Has("placeholder-active"), "Original active X preserved, including subsequent user archive")
Check(Archived.Has("placeholder-archived"), "Archived X preserved")
Check(Archived.Has("windows") && !Topics.Has("windows"), "Windows stays archived")
Check(Topics.Has("mapped-drives") && Shortcuts["X"] = "mapped-drives", "Mapped drive X remains available")
Check(Topics["power"].Path = Fixture "\P.txt", "Sibling override loaded")
Check(Topics["interview-personal"].Body != "" && Topics.Has("linux") && Topics.Has("fortigate"), "Interview and expanded subjects loaded")
Check(StartupWarnings = "" && ShortcutWarnings = "", "No load errors or shortcut collisions")
for id, color in TopicColors {
    expected := BuiltInTopics()
    Check(!expected.Has(id) || color = expected[id].Color, "Curated sidebar color: " id)
}
for id, item in Topics {
    if InStr(id, "placeholder")
        continue
    Check(!RegExMatch(item.Body, "im)^(FR:|EN:|CASE \d|\d+[.-])"), "English keyword format: " id)
}
Check(EnglishText("EN:`nScope`nContinuation`nFR:`nFrench") = "Scope`nContinuation", "Legacy English block")
Check(EnglishText("EN: English`nFR: French`nEN: More") = "English`nMore", "Legacy inline language markers")
FileAppend("PASS Library`n", "*")

Suite := "Settings"
Check(Opacity = 85 && !Pinned && !SidebarHidden && HeadingBold && HeadingColor = "6BCB77", "Default appearance")
Check(!AutoFit, "Default notes stay at 12 points")
Opacity := 70, Pinned := true, SidebarHidden := true, HeadingColor := "FFCC00", HeadingBold := false
SaveSettings()
Opacity := 99, Pinned := false, SidebarHidden := false, HeadingColor := "000000", HeadingBold := true
LoadSettings()
Check(Opacity = 70 && Pinned && SidebarHidden && HeadingColor = "FFCC00" && !HeadingBold, "All settings persist")
IniWrite("wrong", DataRoot "\GuideSettings.ini", "appearance", "opacity")
IniWrite("invalid", DataRoot "\GuideSettings.ini", "appearance", "headingColor")
LoadSettings()
Check(Opacity = 85 && HeadingColor = "6BCB77", "Malformed settings default safely")
IniWrite("120", DataRoot "\GuideSettings.ini", "appearance", "opacity")
LoadSettings()
Check(Opacity = 100, "Opacity upper clamp")
IniWrite("20", DataRoot "\GuideSettings.ini", "appearance", "opacity")
LoadSettings()
Check(Opacity = 60, "Opacity lower clamp")
Opacity := 100, Pinned := false, SidebarHidden := false, HeadingBold := true
FileAppend("PASS Settings`n", "*")

Suite := "Formatting ranges"
runs := [{Start: 3, Length: 4, Color: "FFCC00", Bold: 1}]
shifted := RebaseRuns(runs, "abcWORDxyz", "ZZabcWORDxyz")
Check(shifted[1].Start = 5 && shifted[1].Length = 4, "Insertion before styled word shifts range")
inside := RebaseRuns(runs, "abcWORDxyz", "abcWO--RDxyz")
Check(inside[1].Start = 3 && inside[1].Length = 6, "Typing inside styled word inherits style")
deleted := RebaseRuns(runs, "abcWORDxyz", "abcxyz")
Check(deleted.Length = 0, "Deleted word removes range")
shorter := RebaseRuns(runs, "abcWORDxyz", "abcWDxyz")
Check(shorter[1].Length = 2, "Deletion inside styled word contracts range")
cut := RemoveRunsInRange([{Start: 0, Length: 10, Color: "FFFFFF", Bold: 0}], 3, 7)
Check(cut.Length = 2 && cut[1].Length = 3 && cut[2].Start = 7, "Partial reset retains both sides")
unicodeBody := "SCOPE — café · 🧠`nNETWORK — DNS · VPN`nVALIDATE — user"
item := {Id: "unicode-test", Title: "Unicode test", Body: unicodeBody, Path: DataRoot "\unicode-test.txt",
    Shortcut: "U", Runs: [{Start: InStr(unicodeBody, "DNS") - 1, Length: 9, Color: "FFCC00", Bold: 1}], IsArchive: false}
WriteTopic(item)
reloaded := ReadTopic(item.Path)
Check(reloaded.Body = item.Body && reloaded.Runs.Length = 1 && reloaded.Shortcut = "U", "Unicode formatting and metadata round trip")
Check(reloaded.Runs[1].Start = item.Runs[1].Start, "UTF-16 offsets persist")
WriteUtf8(item.Path, "Unicode test`nDifferent external content`n")
Check(ReadTopic(item.Path).Runs.Length = 0, "External changes invalidate stale formatting")
WriteTopic(item)
spaced := {Id: "blank-lines", Title: "Blank lines", Body: "`nFIRST — alpha`n`nSECOND — beta`n", Path: DataRoot "\blank-lines.txt",
    Shortcut: "", Runs: [{Start: 1, Length: 5, Color: "00FFFF", Bold: 1}], IsArchive: false}
WriteTopic(spaced)
spacedReload := ReadTopic(spaced.Path)
Check(spacedReload.Body = spaced.Body && spacedReload.Runs.Length = 1, "Authored blank lines preserve style fingerprint and offsets")
originalText := FileRead(item.Path, "UTF-8")
originalStyles := FileRead(item.Path ".styles.ini", "UTF-16")
locked := FileOpen(item.Path, "r-d") ; allow reads/writes, deny rename/delete
failure := false
candidate := {Id: item.Id, Title: "Changed title", Body: "REPLACED — content", Path: item.Path, Shortcut: "", Runs: []}
try WriteTopic(candidate)
catch
    failure := true
locked.Close()
Check(failure && FileRead(item.Path, "UTF-8") = originalText, "Locked text rejects save without losing original")
Check(FileRead(item.Path ".styles.ini", "UTF-16") = originalStyles, "Failed two-file commit rolls back sidecar")
MoveTopic(item, false)
Check(ReadTopic(item.Path, true).Runs.Length = 1, "Archive preserves styles")
MoveTopic(item, true)
Check(ReadTopic(item.Path).Runs.Length = 1 && !item.IsArchive, "Restore preserves styles")
; Different X placeholders remain distinct even when restored or archived.
placeholder := Archived["placeholder-archived"]
MoveTopic(placeholder, true)
Check(ReadTopic(placeholder.Path).Id = "placeholder-archived", "Placeholder ID survives restore")
MoveTopic(placeholder, false)
Check(ReadTopic(placeholder.Path, true).Id = "placeholder-archived", "Placeholder ID survives rearchive")
Topics[item.Id] := item
BuildShortcuts()
duplicate := {Id: "duplicate", Title: "Duplicate", Body: "TEST — collision", Shortcut: "U", Runs: [], Path: DataRoot "\duplicate.txt"}
Topics[duplicate.Id] := duplicate
BuildShortcuts()
Check(!Shortcuts.Has("U") && InStr(ShortcutWarnings, "U"), "Duplicate shortcuts disabled")
Topics.Delete("duplicate")
BuildShortcuts()
FileAppend("PASS Formatting ranges and persistence`n", "*")

Suite := "Native GUI"
CreateGuide()
Check(CurrentFontSize = 12, "Native default font is 12 points")
AutoFitCheck.Value := 1
ChangeAutoFit()
WinActivate("ahk_id " Guide.Hwnd)
Sleep(200)
Check(IsObject(NotesBox) && DllCall("IsWindow", "Ptr", Guide.Hwnd), "Usable native guide window")
Check(DllCall("GetDpiForWindow", "Ptr", Guide.Hwnd) >= 96, "Native DPI available")
ShowTopic("unicode-test")
Check(GetBody(NotesBox) = unicodeBody, "Rich Edit Unicode body matches canonical offsets")
dns := InStr(unicodeBody, "DNS") - 1
cf := CharacterFormat(NotesBox, dns)
Check(NumGet(cf, 20, "UInt") = ColorRef("FFCC00") && (NumGet(cf, 8, "UInt") & 1), "Manual color and bold at multiline Unicode offset")
cf := CharacterFormat(NotesBox, 0)
Check(NumGet(cf, 20, "UInt") = ColorRef(HeadingColor) && (NumGet(cf, 8, "UInt") & 1), "Automatic heading style")
Check(!(NumGet(cf, 8, "UInt") & 14), "No accidental italic underline or strikeout")
SetSelection(NotesBox, 0, 5)
ToolbarControls[2].Focus()
Check(GetSelection(NotesBox).End = 5, "Selection survives toolbar focus")
Check(FormatSelection(false, "color", "FF55AA"), "Formatting selected words saves")
cf := CharacterFormat(NotesBox, 0)
Check(NumGet(cf, 20, "UInt") = ColorRef("FF55AA"), "Manual heading override wins")
HeadingColor := "00FFFF"
RefreshFormatting()
cf := CharacterFormat(NotesBox, 0)
Check(NumGet(cf, 20, "UInt") = ColorRef("FF55AA"), "Heading preference preserves explicit override")
SetSelection(NotesBox, 0, 5)
FormatSelection(false, "reset")
cf := CharacterFormat(NotesBox, 0)
Check(NumGet(cf, 20, "UInt") = ColorRef(HeadingColor), "Reset restores automatic heading color")
SetSelection(NotesBox, dns, dns + 9)
FormatSelection(false, "bold")
cf := CharacterFormat(NotesBox, dns)
Check(!(NumGet(cf, 8, "UInt") & 1), "Explicit bold off overrides automatic and previous run")
saved := GetSelection(NotesBox)
Guide.Show("w860 h560")
Sleep(100)
Check(GetSelection(NotesBox).Start = saved.Start && GetSelection(NotesBox).End = saved.End, "Resize retains selection")
smallFont := CurrentFontSize
ToggleSidebar()
NotesBox.GetPos(&notesX)
Check(SidebarHidden && !TopicList.Visible && notesX = 16, "Sidebar collapses and notes expand")
Check(CurrentFontSize >= smallFont, "More space does not reduce font")
ShowSidebar()
Check(!SidebarHidden && TopicList.Visible, "Sidebar restores")
Guide.Maximize()
Sleep(150)
Check(CurrentFontSize >= smallFont && CurrentFontSize <= 24, "Maximized font scales within limits")
Guide.Restore()
Guide.Show("w860 h560")
longBody := ""
Loop 100
    longBody .= "STEP — DNS · gateway · VPN · proxy · known-good network · validation`n"
longBody := RTrim(longBody, "`n")
Topics["long-test"] := {Id: "long-test", Title: "Long topic", Body: longBody, Shortcut: "", Runs: [], Path: DataRoot "\long-test.txt"}
ShowTopic("long-test")
Check(CurrentFontSize = 12 && !TextFits(NotesBox), "Long topic keeps 12pt minimum and scrolls")
SendMessage(0x115, 3, 0, NotesBox.Hwnd) ; WM_VSCROLL SB_PAGEDOWN
scroll := GetScroll(NotesBox)
Check(NumGet(scroll, 4, "Int") > 0, "Native vertical scrolling works")
FitNotes()
Check(NumGet(GetScroll(NotesBox), 4, "Int") = NumGet(scroll, 4, "Int"), "Formatting preserves scroll")
ShowTopic("unicode-test")
ShowEditor("edit")
Check(IsObject(EditorBody) && GetBody(EditorBody) = unicodeBody, "Editor loads topic and styles")
for percent in [60, 85, 100] {
    OpacitySlider.Value := percent
    ChangeOpacity()
    expected := percent = 100 ? "" : Round(percent * 255 / 100)
    Check(WinGetTransparent(Guide.Hwnd) = expected, "Guide opacity " percent)
    Check(WinGetTransparent(EditorGui.Hwnd) = expected, "Editor opacity " percent)
}
EditorBody.Focus()
SetSelection(EditorBody, 0, 0)
SendMessage(0xC2, 1, StrPtr("PRELUDE`n"), EditorBody.Hwnd)
SyncEditorText()
Check(EditorRuns[1].Start >= dns + 8, "Native editor insertion rebases styles")
SendMessage(0xC7, 0, 0, EditorBody.Hwnd)
SyncEditorText()
Check(GetBody(EditorBody) = unicodeBody, "Native text undo is not polluted by automatic formatting")
SendMessage(0x454, 0, 0, EditorBody.Hwnd)
SyncEditorText()
Check(GetBody(EditorBody) = "PRELUDE`n" unicodeBody, "Native text redo retains style rebasing")
SetSelection(EditorBody, 0, 7)
EditorToolbar[2].Focus()
FormatSelection(true, "color", "ABCDEF")
Check(EditorRuns[-1].Color = "ABCDEF", "Editor selection formatting")
SetSelection(EditorBody, 0, 7)
FormatSelection(true, "bold")
EditorShortcut.Value := ""
Check(SaveEditor("edit"), "Editor save completes")
Check(!IsObject(EditorGui) && Topics["unicode-test"].Body = "PRELUDE`n" unicodeBody, "Edited topic is current")
reloadedTopic := ReadTopic(Topics["unicode-test"].Path)
Check(reloadedTopic.Body = Topics["unicode-test"].Body && reloadedTopic.Runs.Length = Topics["unicode-test"].Runs.Length, "Edited styles persist on reload")
ShowEditor("edit")
beforeFailure := Topics["unicode-test"].Body
SetSelection(EditorBody, 0, 0)
SendMessage(0xC2, 1, StrPtr("UNSAVED`n"), EditorBody.Hwnd)
SyncEditorText()
blockedTemp := Topics["unicode-test"].Path ".tmp"
DirCreate(blockedTemp)
SetTimer(DismissExpectedSaveFailure, -100)
saveResult := SaveEditor("edit")
Check(!saveResult && IsObject(EditorGui) && InStr(GetBody(EditorBody), "UNSAVED") = 1, "Failed save retains usable editor and unsaved content")
Check(ReadTopic(Topics["unicode-test"].Path).Body = beforeFailure, "Failed editor save preserves stored content")
DirDelete(blockedTemp)
CloseEditor()
ShowEditor("create")
EditorId.Value := "new-topic", EditorTitle.Value := "New keyword topic", EditorShortcut.Value := "J"
DllCall("SetWindowTextW", "Ptr", EditorBody.Hwnd, "Str", "CHECK — scope · evidence")
SyncEditorText()
Check(SaveEditor("create") && Topics.Has("new-topic"), "Create topic with stable ID and optional shortcut")
multiBody := "FIRST — alpha`nSECOND — beta"
Topics["multiline"] := {Id: "multiline", Title: "Multiline", Body: multiBody, Path: DataRoot "\multiline.txt", Shortcut: "", Runs: [], IsArchive: false}
WriteTopic(Topics["multiline"])
ShowTopic("multiline")
start := InStr(multiBody, "alpha") - 1
SetSelection(NotesBox, start, StrLen(multiBody))
FormatSelection(false, "color", "FF9900")
cf := CharacterFormat(NotesBox, InStr(multiBody, "SECOND") - 1)
Check(NumGet(cf, 20, "UInt") = ColorRef("FF9900"), "Selection formatting crosses native newline boundary")
ArchiveOrRestore()
Check(Archived.Has("multiline") && !Topics.Has("multiline"), "Archive action updates active view")
ToggleArchiveView()
Check(!CreateButton.Enabled && !EditButton.Enabled, "Archive view disables editing and creating")
ShowTopic("multiline")
cf := CharacterFormat(NotesBox, InStr(multiBody, "SECOND") - 1)
Check(NumGet(cf, 20, "UInt") = ColorRef("FF9900"), "Archived view renders persisted multiline style")
ArchiveOrRestore()
Check(Topics.Has("multiline") && !Archived.Has("multiline"), "Restore action updates archive view")
ToggleArchiveView()
SearchBox.Value := "zz-no-match"
FilterTopics()
Check(VisibleIds.Length = 0 && !EditButton.Enabled, "Search empty state")
SearchBox.Value := "journalctl"
FilterTopics()
Check(VisibleIds.Length >= 1 && InStr(JoinText(VisibleIds), "linux"), "Search title and body")
SearchBox.Focus()
Check(HandleGuideKeys(0x43, 0, 0x100, Guide.Hwnd) = "" && !IsObject(EditorGui), "Search typing does not trigger Create")
OpacitySlider.Focus()
Check(HandleGuideKeys(0x45, 0, 0x100, Guide.Hwnd) = "" && !IsObject(EditorGui), "Slider typing does not trigger Edit")
Check(HandleGuideKeys(0x26, 0, 0x100, Guide.Hwnd) = "", "Slider arrows remain native")
HeadingColor := "6BCB77", HeadingBold := true
Opacity := 85
ApplyOpacity()
ShowTopic("methodology")
FileAppend("PASS Native GUI, editing, opacity, fitting, keyboard`n", "*")
Suite := "Slice 046 navigation and requests"
ShowGuide()
WinWaitActive(Guide.Hwnd, , 3)
Check(DllCall("GetFocus", "Ptr") = NotesBox.Hwnd, "Show focuses notes for immediate keys")
SearchBox.Value := ""
FilterTopics()
TopicList.Choose(1)
SelectTopic()
Check(HandleGuideKeys(0x26, 0, 0x100, NotesBox.Hwnd) = 1 && CurrentId = VisibleIds[-1], "Up wraps first to last")
Check(HandleGuideKeys(0x28, 0, 0x100, NotesBox.Hwnd) = 1 && CurrentId = VisibleIds[1], "Down wraps last to first")
Check(HandleGuideKeys(0x28, 0x40000000, 0x100, NotesBox.Hwnd) = 1 && CurrentId = VisibleIds[2], "Repeated Down navigates once")
SearchBox.Value := "fortigate"
FilterTopics()
Check(VisibleIds.Length = 1, "Filtered single-topic fixture")
NotesBox.Focus()
savedId := CurrentId
NavigateTopic(1)
NavigateTopic(-1)
Check(CurrentId = savedId, "Single-topic arrows retain topic")
SearchBox.Value := "no-match-s046"
FilterTopics()
NavigateTopic(1)
NavigateTopic(-1)
Check(VisibleIds.Length = 0 && CurrentId = "", "Empty results do not navigate")
SearchBox.Value := ""
FilterTopics()
ToggleArchiveView()
TopicList.Choose(1)
SelectTopic()
NavigateTopic(-1)
Check(CurrentId = VisibleIds[-1], "Archive wraps within archive")
NavigateTopic(1)
Check(CurrentId = VisibleIds[1], "Archive wraps back to first")
ToggleArchiveView()
ShowTopic("methodology")
NotesBox.Focus()
SetGuideOpacity(85)
WinActivate(Guide.Hwnd)
WinWaitActive(Guide.Hwnd, , 3)
NotesBox.Focus()
Loop 5
    HandleGuideKeys(0x27, 0x40000000, 0x100, NotesBox.Hwnd)
Check(Opacity = 90 && OpacitySlider.Value = 90 && OpacityLabel.Text = "90%", "Repeated Right updates model, slider and label; opacity=" Opacity " active=" WinActive(Guide.Hwnd))
Check(WinGetTransparent(Guide.Hwnd) = Round(90 * 255 / 100), "Repeated Right updates native alpha")
Loop 100
    HandleGuideKeys(0x25, 0x40000000, 0x100, NotesBox.Hwnd)
Check(Opacity = 60, "Held Left clamps at lower bound")
Loop 100
    HandleGuideKeys(0x27, 0x40000000, 0x100, NotesBox.Hwnd)
Check(Opacity = 100 && WinGetTransparent(Guide.Hwnd) = "", "Held Right clamps at fully opaque")
SetGuideOpacity(83)
SaveSettings()
Opacity := 85
LoadSettings()
Check(Opacity = 83, "Arrow opacity persists on restart")
SearchBox.Focus()
HandleGuideKeys(0x27, 0, 0x100, SearchBox.Hwnd)
Check(Opacity = 83, "Search arrow remains native")
NotesBox.Focus()
SendEvent("{Ctrl down}")
try {
    before := CurrentId
    HandleGuideKeys(0x28, 0, 0x100, NotesBox.Hwnd)
    Check(CurrentId = before, "Modified Down remains native")
} finally
    SendEvent("{Ctrl up}")
ShowEditor("edit")
draft := GetBody(EditorBody) "`nUNSAVED S046"
DllCall("SetWindowTextW", "Ptr", EditorBody.Hwnd, "Str", draft)
Check(ShowGuide() = 2 && GetBody(EditorBody) = draft, "Show request preserves editor draft")
before := Opacity
HandleGuideKeys(0x27, 0, 0x100, EditorBody.Hwnd)
Check(Opacity = before, "Editor arrow stays native")
CloseEditor()
Check(CanUseGuideKeyboardFallback(false, true, false, false), "Fallback permits confirmed hidden ready guide")
for flags in [[true,true,false,false], [false,false,false,false], [false,true,true,false], [false,true,false,true]]
    Check(!CanUseGuideKeyboardFallback(flags*), "Fallback refuses dispatched, unready, visible or editor state")
SetGuideOpacity(85)
FileAppend("PASS Slice 046 navigation, opacity repeat, persistence, editor and fallback guards`n", "*")
FileAppend("ALL CHECKS PASSED: " Passed "`n", "*")
if A_Args.Length && A_Args[1] = "--preview" {
    ; Keep an isolated copy visible for screenshot inspection; never user data.
    FileAppend("PREVIEW_READY hwnd=" Guide.Hwnd " fixture=" Fixture "`n", "*")
    SetTimer(() => ExitApp(), -300000)
    Persistent()
} else {
    Guide.Destroy()
    ; Delete only this generated fixture beneath the system temp directory.
    if InStr(Fixture, A_Temp "\HelpDeskGuide-test-") = 1
        DirDelete(Fixture, true)
    ExitApp(0)
}

Check(condition, label) {
    global Passed
    if !condition
        throw Error("FAIL " Suite ": " label)
    Passed++
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
TestError(err, *) {
    FileAppend("FAIL " Suite ": " err.Message " at " err.File ":" err.Line "`n", "*")
    ExitApp(1)
}
DismissExpectedSaveFailure() {
    title := "Save failed ahk_pid " DllCall("GetCurrentProcessId")
    if WinWait(title, , 3)
        WinClose(title) ; Close the expected test-owned error dialog, independent of focus.
}
