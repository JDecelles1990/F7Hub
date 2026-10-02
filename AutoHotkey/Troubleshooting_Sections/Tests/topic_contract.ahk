#Requires AutoHotkey v2.0
#SingleInstance Off
#Include ../GuideCore.ahk

; Finite in-process assertions, isolated writes, no injected keys or child process.
; Run with the external supervisor; errors exit immediately.
global Passed := 0
global Fixture := A_Temp "\F7Hub-s047-contract-" DllCall("GetCurrentProcessId") "-" A_TickCount
OnError(TestError)
DataRoot := Fixture
DirCreate(Fixture "\Archive")
Loop Files A_ScriptDir "\..\*.txt"
    FileCopy(A_LoopFileFullPath, Fixture "\" A_LoopFileName)
Loop Files A_ScriptDir "\..\Archive\*.txt"
    FileCopy(A_LoopFileFullPath, Fixture "\Archive\" A_LoopFileName)
LoadTopics()
LoadSettings()
builtIns := BuiltInTopics()
Check(builtIns.Count = 34 && Topics.Count + Archived.Count = 34, "Every built-in ID exists exactly once")
Check(StartupWarnings = "" && ShortcutWarnings = "", "No duplicate identities or accidental shortcut collisions")
catalog := FileRead(A_ScriptDir "\..\TopicCatalog.md", "UTF-8")
readme := FileRead(A_ScriptDir "\..\README.md", "UTF-8")
for id, policy in builtIns {
    Check(Topics.Has(id) != Archived.Has(id), "Unique loaded identity: " id)
    item := Topics.Has(id) ? Topics[id] : Archived[id]
    Check(item.Shortcut = policy.Key && TopicColors[id] = policy.Color, "Runtime policy: " id)
    Check(RegExMatch(catalog, "s)## ``" id "``\R(.*?)(?=\R## |$)", &section), "Catalog entry exists: " id)
    expectedKey := policy.Key = "" ? "None" : policy.Key
    Check(InStr(section[1], "| Stable topic ID | ``" id "`` |")
        && InStr(section[1], "| Automation target | ``" id "`` |")
        && InStr(section[1], "| Shortcut key | " expectedKey " |")
        && InStr(section[1], "| Topic color | #" policy.Color " |"), "Exact documented identity/key/color: " id)
    Check(RegExMatch(readme, "m)^\| " expectedKey " \| [^\r\n]+ \| ``" id "`` \| [^\r\n]+ \| #" policy.Color " \|"), "Exact keyboard/color reference: " id)
    if InStr(id, "interview-") = 1
        Check(policy.Color = "C792EA", "Common interview color: " id)
}
Check(DefaultShortcut("outlook") = "O" && DefaultShortcut("azure-vm") = "A", "Direct versus grouped shortcut")
Check(DefaultShortcut("interview-technical") = "1" && DefaultShortcut("interview-behavioral") = "2"
    && DefaultShortcut("interview-star") = "3" && DefaultShortcut("interview-personal") = "4"
    && DefaultShortcut("interview-questions") = "5", "Actual numeric interview IDs")
expected := Map("A", "applications,azure-vm", "S", "sharepoint,phishing", "H", "hardware,power", "W", "windows-365,services,windows")
for key, ids in expected {
    Check(JoinIds(ShortcutGroups[key]) = ids, "Explicit group order: " key)
    global CurrentId := "outlook"
    members := ShortcutGroups[key]
    for id in members {
        if !Topics.Has(id)
            continue
        target := ShortcutTarget(key)
        Check(target = id, "Group selects in order: " key " / " id)
        for position, configuredId in members
            if configuredId = id
                Check(InStr(readme, "| ``" id "`` | " position " of " members.Length " | " members.Length " |"), "Documented group position: " id)
        CurrentId := target
    }
    Check(ShortcutTarget(key) = members[1], "Group wraps: " key)
}
; Reversed insertion/list titles must not determine cycle order.
reversed := Map()
ids := []
for id in Topics
    ids.Push(id)
Loop ids.Length
    reversed[ids[-A_Index]] := Topics[ids[-A_Index]]
Topics := reversed
BuildShortcuts()
for key, ids in expected
    Check(JoinIds(ShortcutGroups[key]) = ids, "Independent of Map/enumeration order: " key)
Check(LegacyIds()["S"] = "onedrive-sync" && DefaultShortcut("onedrive-sync") = "D", "Historical identity is separate from current shortcut")
Check(LegacyIds()["H"] = "phishing" && DefaultShortcut("phishing") = "S", "Legacy letters never define new groups")
; Unavailable members are skipped; archived Windows joins only its displayed view.
CurrentId := "windows-365"
Check(ShortcutTarget("W") = "services", "Default active W excludes archived Windows")
CurrentId := "services"
Check(ShortcutTarget("W") = "windows-365", "Active W wraps without Windows")
ArchiveMode := true
Check(ShortcutTarget("W") = "windows", "Archive view selects archived Windows without restore")
Check(Archived.Has("windows") && !Topics.Has("windows"), "Shortcut lookup never restores a topic")
ArchiveMode := false
savedAzure := Topics["azure-vm"]
Topics.Delete("azure-vm")
BuildShortcuts()
CurrentId := "applications"
Check(ShortcutTarget("A") = "applications", "One available group member wraps to itself")
Topics.Delete("applications")
BuildShortcuts()
Check(ShortcutTarget("A") = "", "No available group member is a no-op")
LoadTopics()
; An unexpected custom member disables, rather than extends, the whole group.
Topics["custom-collision"] := {Id: "custom-collision", Shortcut: "A"}
BuildShortcuts()
Check(!ShortcutGroups.Has("A") && !Shortcuts.Has("A") && InStr(ShortcutWarnings, "A"), "Accidental duplicate never becomes an intentional group")
Topics.Delete("custom-collision")
BuildShortcuts()
for id in ["custom-one", "custom-two"]
    Topics[id] := {Id: id, Shortcut: "J"}
BuildShortcuts()
Check(!Shortcuts.Has("J") && InStr(ShortcutWarnings, "J"), "Accidental direct duplicates disabled")
LoadTopics()
outlook := Topics["outlook"]
Topics.Delete("outlook")
Topics["custom-reserved-key"] := {Id: "custom-reserved-key", Shortcut: "O"}
BuildShortcuts()
Check(!Shortcuts.Has("O") && InStr(ShortcutWarnings, "O"), "Absent built-in still reserves its direct shortcut")
LoadTopics()
Check(DefaultShortcut("outlook-copy") = "" && ValidTopicShortcut("custom-topic", "")
    && !ValidTopicShortcut("custom-topic", "1"), "User topics have safe optional-letter fallback")
unknown := {Id: "custom-fallback", Title: "Outlook", Body: "NOTES — reference", Path: Fixture "\custom-fallback.txt", Shortcut: "", Runs: []}
WriteTopic(unknown)
Topics[unknown.Id] := ReadTopic(unknown.Path)
BuildTopicColors()
fallbackColor := TopicColors[unknown.Id]
Topics[unknown.Id].Title := "Changed title"
BuildTopicColors()
Check(TopicColors[unknown.Id] = fallbackColor && Topics[unknown.Id].Shortcut = "", "User fallback color and routing do not depend on title")
; Rename/title changes preserve explicit identity through paired metadata.
item := Topics["outlook"]
color := TopicColors[item.Id]
item.Title := "Completely different display title"
WriteTopic(item)
renamed := Fixture "\renamed-source.txt"
FileMove(item.Path, renamed)
FileMove(item.Path ".styles.ini", renamed ".styles.ini")
item.Path := renamed
Check(ReadTopic(renamed).Id = "outlook", "Identity does not depend on display title or renamed filename")
MoveTopic(item, false)
Topics.Delete(item.Id), Archived[item.Id] := item
BuildShortcuts()
BuildTopicColors()
Check(ReadTopic(item.Path, true).Id = "outlook" && TopicColors[item.Id] = color, "Archive preserves identity and color")
MoveTopic(item, true)
Archived.Delete(item.Id), Topics[item.Id] := item
BuildTopicColors()
Check(ReadTopic(item.Path).Id = "outlook" && TopicColors[item.Id] = color, "Restore preserves identity and color")
; Native rendering validates heading color; title/list both read the same policy.
CreateGuide()
ShowTopic("outlook")
cf := Buffer(116, 0)
NumPut("UInt", cf.Size, cf)
SetSelection(NotesBox, 0, 1)
SendMessage(0x43A, 1, cf.Ptr, NotesBox.Hwnd)
Check(NumGet(cf, 20, "UInt") = ColorRef("2B88D8"), "Native automatic Outlook heading uses topic color")
ShowTopic("teams")
ShowEditor("edit")
SetSelection(EditorBody, 0, 1)
SendMessage(0x43A, 1, cf.Ptr, EditorBody.Hwnd)
Check(NumGet(cf, 20, "UInt") = ColorRef("6264A7"), "Editor automatic heading uses its own topic ID")
CloseEditor()
; Built-in IDs stay reserved even when missing: actual save rejects and retains draft.
Topics.Delete("azure-vm")
ShowEditor("create")
EditorId.Value := "azure-vm", EditorTitle.Value := "Custom overwrite"
DllCall("SetWindowTextW", "Ptr", EditorBody.Hwnd, "Str", "NOTES — draft")
SetTimer(CloseOwnedDialog, -30)
Check(!SaveEditor("create") && IsObject(EditorGui) && !Topics.Has("azure-vm"), "User creation cannot overwrite an absent built-in ID")
CloseEditor()
Guide.Destroy()
FileAppend("ALL CHECKS PASSED: " Passed "`n", "*")
ExitApp(0)

JoinIds(ids) {
    result := ""
    for id in ids
        result .= (result = "" ? "" : ",") id
    return result
}
Check(value, label) {
    global Passed
    if !value
        throw Error(label)
    Passed++
    FileAppend("PASS " label "`n", "*")
}
TestError(err, *) {
    FileAppend("FAIL " err.Message " at " err.File ":" err.Line "`n", "*")
    ExitApp(1)
}
CloseOwnedDialog() {
    title := "ID already used ahk_pid " DllCall("GetCurrentProcessId")
    if WinWait(title, , 2)
        WinClose(title)
}
