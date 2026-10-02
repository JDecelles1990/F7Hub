#Requires AutoHotkey v2.0

global DataRoot := A_ScriptDir, Topics := Map(), Archived := Map(), VisibleIds := []
global Guide := 0, SearchBox := 0, TopicList := 0, NotesBox := 0, TopicTitle := 0
global StatusText := 0, OpacitySlider := 0, OpacityLabel := 0, PinCheck := 0
global StatusHwnd := 0
global SettingsPending := false
global SidebarButton := 0, HeadingBoldCheck := 0, ArchiveButton := 0, ArchiveViewButton := 0
global CreateButton := 0, EditButton := 0, SidebarControls := [], ToolbarControls := []
global CurrentId := "", ArchiveMode := false, Shortcuts := Map(), ShortcutWarnings := ""
global Opacity := 85, Pinned := false, SidebarHidden := false, HeadingColor := "6BCB77", HeadingBold := true
global AutoFit := false, AutoFitCheck := 0, TopicColors := Map()
global CurrentFontSize := 12, EditorGui := 0, EditorBody := 0, EditorId := 0, EditorTitle := 0
global EditorShortcut := 0, EditorSave := 0, EditorCancel := 0, EditorToolbar := []
global EditorRuns := [], EditorLastText := "", EditorLoading := false
global EditorHistory := Map()
global FormattingBusy := false, LayoutBusy := false, SettingsWarning := "", StartupWarnings := ""
global NavigationPending := false, NavigationScheduled := false, NavigationRendering := false

NormalizeText(text) => StrReplace(StrReplace(text, "`r`n", "`n"), "`r", "`n")
EnglishText(body) {
    body := NormalizeText(body)
    if !RegExMatch(body, "im)^(EN|FR):")
        return body
    lines := [], lang := ""
    for line in StrSplit(body, "`n") {
        if RegExMatch(line, "i)^(EN|FR):\s*(.*)$", &m)
            lang := StrUpper(m[1]), line := m[2]
        if lang != "FR"
            lines.Push(line)
    }
    return Trim(JoinText(lines), "`n")
}
JoinText(lines) {
    result := ""
    for line in lines
        result .= (A_Index > 1 ? "`n" : "") line
    return result
}
LegacyIds() => Map("M", "methodology", "O", "outlook", "P", "power", "S", "onedrive-sync",
    "H", "phishing", "I", "identity", "W", "windows", "N", "network", "D", "sharepoint",
    "L", "performance", "G", "dns", "V", "vpn", "R", "printing", "T", "teams",
    "F", "services", "K", "accounts", "B", "applications", "Q", "interview-questions",
    "Y", "fortigate", "Z", "interview-personal")
DefaultShortcut(id) {
    for key, value in LegacyIds()
        if value = id
            return key
    return id = "mapped-drives" ? "X" : ""
}
ReadTopic(path, isArchive := false) {
    parts := StrSplit(NormalizeText(FileRead(path, "UTF-8")), "`n", , 2)
    SplitPath(path, , , , &stem)
    old := LegacyIds()
    id := old.Has(StrUpper(stem)) ? old[StrUpper(stem)] : StrLower(stem)
    ; Preserve both legacy placeholders without hiding mapped drives.
    if StrUpper(stem) = "X"
        id := isArchive ? "placeholder-archived" : "placeholder-active"
    id := IniRead(path ".styles.ini", "topic", "id", id)
    if !RegExMatch(id, "^[a-z][a-z0-9-]{0,63}$") || RegExMatch(id, "i)^(con|prn|aux|nul|com[0-9]|lpt[0-9])$")
        throw Error("Invalid topic ID")
    body := parts.Length > 1 ? parts[2] : ""
    ; Remove the file's one terminating newline, preserving authored blank lines.
    if SubStr(body, -1) = "`n"
        body := SubStr(body, 1, -1)
    body := EnglishText(body)
    shortcut := IniRead(path ".styles.ini", "topic", "shortcut", DefaultShortcut(id))
    if !RegExMatch(shortcut, "^[A-Z]?$") || shortcut != "" && InStr("ACE", shortcut)
        shortcut := ""
    return {Id: id, Title: Trim(parts[1]), Body: body, Path: path,
        Shortcut: shortcut, Runs: ReadRuns(path, body), IsArchive: isArchive}
}
LoadTopics() {
    global Topics, Archived, StartupWarnings
    Topics := Map(), Archived := Map(), StartupWarnings := ""
    for folder in [DataRoot, DataRoot "\Archive"] {
        if !DirExist(folder)
            continue
        isArchive := folder != DataRoot
        Loop Files folder "\*.txt" {
            try {
                item := ReadTopic(A_LoopFileFullPath, isArchive)
                target := isArchive ? Archived : Topics
                if target.Has(item.Id)
                    throw Error("Duplicate topic ID: " item.Id)
                target[item.Id] := item
            } catch Error as err
                StartupWarnings .= (StartupWarnings = "" ? "" : " | ") A_LoopFileName ": " err.Message
        }
    }
    for id, item in Archived
        if Topics.Has(id)
            Topics.Delete(id)
    BuildShortcuts()
    BuildTopicColors()
}
BuildTopicColors() {
    global TopicColors
    TopicColors := Map(), used := Map()
    for collection in [Topics, Archived]
        for id, item in collection {
            hash := TextFingerprint(id)
            hue := Integer("0x" SubStr(hash, 1, 4)) / 65536 * 6
            saturation := 0.45 + Integer("0x" SubStr(hash, 5, 2)) / 255 * 0.25
            value := 0.90 + Integer("0x" SubStr(hash, 7, 2)) / 255 * 0.10
            sector := Floor(hue), fraction := hue - sector
            p := value * (1 - saturation), q := value * (1 - saturation * fraction), t := value * (1 - saturation * (1 - fraction))
            channels := [[value,t,p],[q,value,p],[p,value,t],[p,q,value],[t,p,value],[value,p,q]][sector + 1]
            color := Format("{:02X}{:02X}{:02X}", Round(channels[1]*255), Round(channels[2]*255), Round(channels[3]*255))
            while used.Has(color)
                color := SubStr(color,1,4) Format("{:02X}", Mod(Integer("0x" SubStr(color,5,2))+1,256))
            used[color] := true
            TopicColors[id] := color
        }
}
DrawTopicItem(wParam, lParam, *) {
    if !IsObject(TopicList) || NumGet(lParam, 0, "UInt") != 2
        return
    windowOffset := A_PtrSize = 8 ? 24 : 20
    if NumGet(lParam, windowOffset, "Ptr") != TopicList.Hwnd
        return
    dc := NumGet(lParam, windowOffset + A_PtrSize, "Ptr")
    rectOffset := windowOffset + A_PtrSize * 2
    rect := Buffer(16)
    DllCall("RtlMoveMemory", "Ptr", rect, "Ptr", lParam + rectOffset, "UPtr", 16)
    state := NumGet(lParam, 16, "UInt"), index := NumGet(lParam, 8, "UInt")
    brush := DllCall("CreateSolidBrush", "UInt", ColorRef(state & 1 ? "364557" : "25282C"), "Ptr")
    DllCall("FillRect", "Ptr", dc, "Ptr", rect, "Ptr", brush)
    DllCall("DeleteObject", "Ptr", brush)
    if index >= VisibleIds.Length
        return 1
    id := VisibleIds[index + 1], items := DisplayedTopics()
    if !items.Has(id)
        return 1
    item := items[id]
    validShortcut := Shortcuts.Has(item.Shortcut) && Shortcuts[item.Shortcut] = id
    label := (validShortcut ? "[" item.Shortcut "] " : "") item.Title
    color := TopicColors.Has(id) ? TopicColors[id] : "ADD8E6"
    font := SendMessage(0x31, 0, 0, TopicList.Hwnd)
    previousFont := DllCall("SelectObject", "Ptr", dc, "Ptr", font, "Ptr")
    previousColor := DllCall("SetTextColor", "Ptr", dc, "UInt", ColorRef(color), "UInt")
    previousMode := DllCall("SetBkMode", "Ptr", dc, "Int", 1)
    NumPut("Int", NumGet(rect, 0, "Int") + 5, rect, 0)
    try {
        DllCall("DrawTextW", "Ptr", dc, "Str", label, "Int", -1, "Ptr", rect, "UInt", 0x8824)
        if state & 0x10
            DllCall("DrawFocusRect", "Ptr", dc, "Ptr", rect)
    } finally {
        DllCall("SelectObject", "Ptr", dc, "Ptr", previousFont)
        DllCall("SetTextColor", "Ptr", dc, "UInt", previousColor)
        DllCall("SetBkMode", "Ptr", dc, "Int", previousMode)
    }
    return 1
}
MeasureTopicItem(wParam, lParam, *) {
    if NumGet(lParam, 0, "UInt") = 2 {
        NumPut("UInt", Round(24 * DllCall("GetDpiForSystem") / 96), lParam, 16)
        return 1
    }
}
BuildShortcuts() {
    global Shortcuts, ShortcutWarnings
    Shortcuts := Map(), ShortcutWarnings := "", counts := Map()
    for collection in [Topics, Archived]
        for id, item in collection
            if item.Shortcut != ""
                counts[item.Shortcut] := counts.Has(item.Shortcut) ? counts[item.Shortcut] + 1 : 1
    for collection in [Topics, Archived]
        for id, item in collection {
            key := item.Shortcut
            if key = ""
                continue
            if counts[key] = 1
                Shortcuts[key] := id
            else if !InStr(ShortcutWarnings, key)
                ShortcutWarnings .= key " "
        }
}
DisplayedTopics() => ArchiveMode ? Archived : Topics
LoadSettings() {
    global Opacity, Pinned, SidebarHidden, HeadingColor, HeadingBold
    path := DataRoot "\GuideSettings.ini"
    value := IniRead(path, "appearance", "opacity", "85")
    Opacity := IsInteger(value) ? Max(70, Min(100, Integer(value))) : 85
    Pinned := IniRead(path, "appearance", "pinned", "0") = "1"
    SidebarHidden := IniRead(path, "appearance", "sidebarHidden", "0") = "1"
    HeadingBold := IniRead(path, "appearance", "headingBold", "1") = "1"
    global AutoFit := IniRead(path, "appearance", "autoFit", "0") = "1"
    value := IniRead(path, "appearance", "headingColor", "6BCB77")
    HeadingColor := RegExMatch(value, "i)^[0-9a-f]{6}$") ? StrUpper(value) : "6BCB77"
}
SaveSettings() {
    path := DataRoot "\GuideSettings.ini", temp := path ".tmp"
    text := "[appearance]`nopacity=" Opacity "`npinned=" Integer(Pinned)
        . "`nsidebarHidden=" Integer(SidebarHidden) "`nheadingBold=" Integer(HeadingBold)
        . "`nheadingColor=" HeadingColor "`n"
        . "autoFit=" Integer(AutoFit) "`n"
    WriteIni(temp, text)
    FileMove(temp, path, true)
}
SaveSettingsQuietly() {
    global SettingsWarning, SettingsPending
    try {
        SaveSettings()
        SettingsPending := false
        SettingsWarning := ""
    } catch Error as err
        SettingsWarning := "Preferences not saved: " err.Message
    if IsObject(StatusText)
        UpdateStatus()
}
SavePendingGuideSettings(*) {
    if SettingsPending
        SaveSettingsQuietly()
}
WriteUtf8(path, text) {
    stream := FileOpen(path, "w", "UTF-8")
    try stream.Write(text)
    finally stream.Close()
}
WriteIni(path, text) {
    ; Windows INI APIs recognize UTF-16; UTF-8 BOM can obscure the first section.
    stream := FileOpen(path, "w", "UTF-16")
    try stream.Write(text)
    finally stream.Close()
}
TextFingerprint(text) {
    ; SHA-256 over UTF-16LE, excluding the terminating NUL.
    provider := 0, hash := 0, digest := Buffer(32), size := 32
    if !DllCall("advapi32\CryptAcquireContextW", "Ptr*", &provider, "Ptr", 0, "Ptr", 0, "UInt", 24, "UInt", 0xF0000000)
        throw OSError()
    try {
        if !DllCall("advapi32\CryptCreateHash", "Ptr", provider, "UInt", 0x800C, "Ptr", 0, "UInt", 0, "Ptr*", &hash)
            throw OSError()
        if !DllCall("advapi32\CryptHashData", "Ptr", hash, "Ptr", StrPtr(text), "UInt", StrLen(text) * 2, "UInt", 0)
            throw OSError()
        if !DllCall("advapi32\CryptGetHashParam", "Ptr", hash, "UInt", 2, "Ptr", digest, "UInt*", &size, "UInt", 0)
            throw OSError()
        result := ""
        Loop 32
            result .= Format("{:02X}", NumGet(digest, A_Index - 1, "UChar"))
        return result
    } finally {
        if hash
            DllCall("advapi32\CryptDestroyHash", "Ptr", hash)
        DllCall("advapi32\CryptReleaseContext", "Ptr", provider, "UInt", 0)
    }
}
ReadRuns(path, body) {
    sidecar := path ".styles.ini", runs := []
    if !FileExist(sidecar) || IniRead(sidecar, "format", "version", "0") != "1"
        return runs
    if IniRead(sidecar, "format", "fingerprint", "") != TextFingerprint(body)
        return runs
    count := IniRead(sidecar, "format", "count", "0")
    if !IsInteger(count) || count < 0 || count > 10000
        return runs
    Loop Integer(count) {
        section := "run" A_Index
        start := IniRead(sidecar, section, "start", "-1"), length := IniRead(sidecar, section, "length", "0")
        color := IniRead(sidecar, section, "color", ""), bold := IniRead(sidecar, section, "bold", "-1")
        if !IsInteger(start) || !IsInteger(length) || !IsInteger(bold)
            continue
        if start < 0 || length <= 0 || start + length > StrLen(body)
            continue
        if color != "" && !RegExMatch(color, "i)^[0-9a-f]{6}$")
            continue
        if bold < -1 || bold > 1
            continue
        runs.Push({Start: Integer(start), Length: Integer(length), Color: color, Bold: Integer(bold)})
    }
    return runs
}
StylesText(item) {
    text := "[topic]`nid=" item.Id "`nshortcut=" item.Shortcut "`n[format]`nversion=1`nfingerprint="
        . TextFingerprint(item.Body) "`ncount=" item.Runs.Length "`n"
    for i, run in item.Runs
        text .= "[run" i "]`nstart=" run.Start "`nlength=" run.Length
            . "`ncolor=" run.Color "`nbold=" run.Bold "`n"
    return text
}
WriteTopic(item, path := "") {
    if path = ""
        path := item.Path
    SplitPath(path, , &folder)
    DirCreate(folder)
    hadText := !!FileExist(path), hadStyles := !!FileExist(path ".styles.ini")
    textMoved := false, stylesMoved := false
    try {
        WriteUtf8(path ".tmp", item.Title "`n" item.Body "`n")
        WriteIni(path ".styles.ini.tmp", StylesText(item))
        if hadText
            FileCopy(path, path ".rollback", true)
        if hadStyles
            FileCopy(path ".styles.ini", path ".styles.ini.rollback", true)
        FileMove(path ".styles.ini.tmp", path ".styles.ini", true)
        stylesMoved := true
        FileMove(path ".tmp", path, true)
        textMoved := true
    } catch Error as err {
        try {
            if stylesMoved {
                if hadStyles
                    FileMove(path ".styles.ini.rollback", path ".styles.ini", true)
                else
                    FileDelete(path ".styles.ini")
            }
            if textMoved {
                if hadText
                    FileMove(path ".rollback", path, true)
                else
                    FileDelete(path)
            }
        } catch Error as rollbackError
            throw Error(err.Message "`nRecovery copy retained: " path ".rollback`n" rollbackError.Message)
        throw err
    } finally {
        for suffix in [".tmp", ".styles.ini.tmp"]
            if FileExist(path suffix) && !DirExist(path suffix)
                try FileDelete(path suffix)
    }
    for suffix in [".rollback", ".styles.ini.rollback"]
        if FileExist(path suffix)
            try FileDelete(path suffix)
}
CloneRuns(runs) {
    result := []
    for run in runs
        result.Push({Start: run.Start, Length: run.Length, Color: run.Color, Bold: run.Bold})
    return result
}
RebaseRuns(runs, oldText, newText) {
    if oldText = newText
        return CloneRuns(runs)
    oldLen := StrLen(oldText), newLen := StrLen(newText), prefix := 0, suffix := 0
    while prefix < Min(oldLen, newLen) && SubStr(oldText, prefix + 1, 1) = SubStr(newText, prefix + 1, 1)
        prefix++
    while suffix < Min(oldLen, newLen) - prefix && SubStr(oldText, oldLen - suffix, 1) = SubStr(newText, newLen - suffix, 1)
        suffix++
    oldEnd := oldLen - suffix, newEnd := newLen - suffix, delta := newLen - oldLen, result := []
    for run in runs {
        start := run.Start, finish := start + run.Length
        if finish <= prefix
            result.Push({Start: start, Length: run.Length, Color: run.Color, Bold: run.Bold})
        else if start >= oldEnd
            result.Push({Start: start + delta, Length: run.Length, Color: run.Color, Bold: run.Bold})
        else if start < prefix && finish > oldEnd
            result.Push({Start: start, Length: run.Length + delta, Color: run.Color, Bold: run.Bold})
        else {
            if start < prefix
                result.Push({Start: start, Length: prefix - start, Color: run.Color, Bold: run.Bold})
            if finish > oldEnd
                result.Push({Start: newEnd, Length: finish - oldEnd, Color: run.Color, Bold: run.Bold})
        }
    }
    return result
}
RemoveRunsInRange(runs, start, finish) {
    result := []
    for run in runs {
        runEnd := run.Start + run.Length
        if runEnd <= start || run.Start >= finish
            result.Push(run)
        else {
            if run.Start < start
                result.Push({Start: run.Start, Length: start - run.Start, Color: run.Color, Bold: run.Bold})
            if runEnd > finish
                result.Push({Start: finish, Length: runEnd - finish, Color: run.Color, Bold: run.Bold})
        }
    }
    return result
}
LoadRichEdit() {
    static module := DllCall("LoadLibraryW", "Str", "Msftedit.dll", "Ptr")
    if !module
        throw Error("Windows Rich Edit is unavailable.")
}
ColorRef(rgb) => Integer("0x" SubStr(rgb, 5, 2) SubStr(rgb, 3, 2) SubStr(rgb, 1, 2))
GetSelection(control) {
    buf := Buffer(8)
    SendMessage(0x434, 0, buf.Ptr, control.Hwnd)
    return {Start: NumGet(buf, 0, "Int"), End: NumGet(buf, 4, "Int")}
}
SetSelection(control, start, finish) {
    buf := Buffer(8)
    NumPut("Int", start, "Int", finish, buf)
    SendMessage(0x437, 0, buf.Ptr, control.Hwnd)
}
GetScroll(control) {
    point := Buffer(8)
    SendMessage(0x4DD, 0, point.Ptr, control.Hwnd)
    return point
}
RestoreScroll(control, point) => SendMessage(0x4DE, 0, point.Ptr, control.Hwnd)
GetBody(control) => NormalizeText(ControlGetText(control.Hwnd))
ApplyRange(control, start, length, color := "", bold := -1, points := 0) {
    if length <= 0
        return
    cf := Buffer(116, 0)
    mask := (color != "" ? 0x40000000 : 0) | (bold != -1 ? 1 : 0) | (points ? 0xA000000E : 0)
    NumPut("UInt", cf.Size, "UInt", mask, "UInt", bold = 1 ? 1 : 0, cf)
    if points {
        NumPut("Int", points * 20, cf, 12)
        StrPut("Segoe UI", cf.Ptr + 26, 32, "UTF-16")
    }
    if color != ""
        NumPut("UInt", ColorRef(color), cf, 20)
    SetSelection(control, start, start + length)
    SendMessage(0x444, 1, cf.Ptr, control.Hwnd)
}
FormatControl(control, body, runs, points := 12) {
    global FormattingBusy
    if FormattingBusy
        return
    FormattingBusy := true
    selection := GetSelection(control), scroll := GetScroll(control)
    doc := RichDocument(control)
    if doc
        ComCall(22, doc, "Int", -9999995, "Ptr", 0) ; ITextDocument::Undo(tomSuspend)
    SendMessage(0xB, 0, 0, control.Hwnd)
    try {
        ApplyRange(control, 0, StrLen(body), "ADD8E6", 0, points)
        offset := 0
        for line in StrSplit(body, "`n") {
            divider := InStr(line, " — ")
            if divider
                ApplyRange(control, offset, divider - 1, HeadingColor, Integer(HeadingBold))
            offset += StrLen(line) + 1
        }
        for run in runs
            ApplyRange(control, run.Start, run.Length, run.Color, run.Bold)
    } finally {
        SetSelection(control, selection.Start, selection.End)
        RestoreScroll(control, scroll)
        SendMessage(0xB, 1, 0, control.Hwnd)
        DllCall("InvalidateRect", "Ptr", control.Hwnd, "Ptr", 0, "Int", true)
        if doc {
            ComCall(22, doc, "Int", -9999994, "Ptr", 0) ; tomResume
            ObjRelease(doc)
        }
        FormattingBusy := false
        ScheduleTopicNavigationRender()
    }
}
RichDocument(control) {
    ptrBuffer := Buffer(A_PtrSize, 0)
    if !SendMessage(0x43C, 0, ptrBuffer.Ptr, control.Hwnd)
        return 0
    ole := NumGet(ptrBuffer, 0, "Ptr"), doc := 0, iid := Buffer(16)
    try {
        DllCall("ole32\CLSIDFromString", "WStr", "{8CC497C0-A1DF-11CE-8098-00AA0047BE5D}", "Ptr", iid)
        ComCall(0, ole, "Ptr", iid.Ptr, "Ptr*", &doc)
        return doc
    } finally
        ObjRelease(ole)
}
CreateRichControl(guiObj, options, readOnly := false) {
    LoadRichEdit()
    control := guiObj.Add("Custom", "ClassRICHEDIT50W " options " +0x4 +0x40 +0x1000 +0x200000" (readOnly ? " +0x800" : ""))
    control.SetFont("s12", "Segoe UI")
    SendMessage(0x443, 0, ColorRef("101214"), control.Hwnd)
    SendMessage(0x448, 0, 0, control.Hwnd) ; native wrapping at control width
    SendMessage(0x435, 0, 1000000, control.Hwnd)
    if !readOnly
        SendMessage(0x445, 0, 1, control.Hwnd) ; ENM_CHANGE
    return control
}
PickColor(initial, owner) {
    static custom := Buffer(64, 0)
    size := A_PtrSize = 8 ? 72 : 36, cc := Buffer(size, 0)
    NumPut("UInt", size, cc)
    NumPut("Ptr", owner, cc, A_PtrSize = 8 ? 8 : 4)
    NumPut("UInt", ColorRef(initial), cc, A_PtrSize = 8 ? 24 : 12)
    NumPut("Ptr", custom.Ptr, cc, A_PtrSize = 8 ? 32 : 16)
    NumPut("UInt", 3, cc, A_PtrSize = 8 ? 40 : 20)
    if !DllCall("comdlg32\ChooseColorW", "Ptr", cc)
        return ""
    value := NumGet(cc, A_PtrSize = 8 ? 24 : 12, "UInt")
    return Format("{:02X}{:02X}{:02X}", value & 255, (value >> 8) & 255, (value >> 16) & 255)
}
ToggleGuide(*) {
    ; Finish a toggle before another hotkey can hide or reopen its window.
    Critical()
    if !IsObject(EditorGui) && IsObject(Guide) && DllCall("IsWindowVisible", "Ptr", Guide.Hwnd) && WinActive("ahk_id " Guide.Hwnd)
        Guide.Hide()
    else
        ShowGuide()
}
ShowGuide(*) {
    if IsObject(EditorGui) {
        EditorGui.Show()
        WinActivate("ahk_id " EditorGui.Hwnd)
        return 2
    }
    if !IsObject(Guide)
        CreateGuide()
    else {
        LoadTopics()
        FilterTopics()
        Guide.Show()
    }
    WinActivate("ahk_id " Guide.Hwnd)
    selection := GetSelection(NotesBox), scroll := GetScroll(NotesBox)
    NotesBox.Focus()
    ; Native Rich Edit focus can select all and scroll to the end. Retain the
    ; rendered topic's selection and viewport while enabling immediate keys.
    SetSelection(NotesBox, selection.Start, selection.End)
    RestoreScroll(NotesBox, scroll)
    return 1
}
CreateGuide() {
    global Guide, SearchBox, TopicList, NotesBox, TopicTitle, StatusText, SidebarControls, ToolbarControls
    global OpacitySlider, OpacityLabel, PinCheck, SidebarButton, HeadingBoldCheck
    global ArchiveButton, ArchiveViewButton, CreateButton, EditButton
    global AutoFitCheck
    global StatusHwnd
    Guide := Gui("+Resize +MinSize860x560", "Help Desk & Interview Guide")
    Guide.BackColor := "151719"
    Guide.SetFont("s10 cF1F3F4", "Segoe UI")
    Guide.AddText("x16 y14 w55", "Opacity")
    OpacitySlider := Guide.AddSlider("x74 y8 w140 h28 Range70-100 ToolTip", Opacity)
    OpacitySlider.OnEvent("Change", ChangeOpacity)
    OpacityLabel := Guide.AddText("x220 y14 w42", Opacity "%")
    PinCheck := Guide.AddCheckbox("x272 y10 w124 h26", "Always on top")
    PinCheck.Value := Pinned
    PinCheck.OnEvent("Click", ChangePin)
    SidebarButton := Guide.AddButton("x408 y8 w110 h28", SidebarHidden ? "Show topics" : "Hide topics")
    SidebarButton.OnEvent("Click", ToggleSidebar)
    colorButton := Guide.AddButton("x530 y8 w116 h28", "Heading color")
    colorButton.OnEvent("Click", ChangeHeadingColor)
    HeadingBoldCheck := Guide.AddCheckbox("x660 y10 w145 h26", "Bold headings")
    HeadingBoldCheck.Value := HeadingBold
    HeadingBoldCheck.OnEvent("Click", ChangeHeadingBold)
    SearchBox := Guide.AddEdit("x16 y52 w264 h28 Background25282C cF1F3F4")
    SendMessage(0x1501, 1, StrPtr("Search topics..."), SearchBox.Hwnd)
    SearchBox.OnEvent("Change", FilterTopics)
    CreateButton := Guide.AddButton("x16 y90 w82 h30", "C - Create")
    CreateButton.OnEvent("Click", (*) => ShowEditor("create"))
    EditButton := Guide.AddButton("x105 y90 w82 h30", "E - Edit")
    EditButton.OnEvent("Click", (*) => ShowEditor("edit"))
    scriptButton := Guide.AddButton("x194 y90 w86 h30", "A - Script")
    scriptButton.OnEvent("Click", OpenScript)
    ArchiveButton := Guide.AddButton("x16 y130 w128 h30", "Archive topic")
    ArchiveButton.OnEvent("Click", ArchiveOrRestore)
    ArchiveViewButton := Guide.AddButton("x152 y130 w128 h30", "View archive")
    ArchiveViewButton.OnEvent("Click", ToggleArchiveView)
    TopicList := Guide.AddListBox("x16 y170 w264 h330 +0x10 Background25282C cF1F3F4")
    SendMessage(0x1A0, 0, Round(24 * DllCall("GetDpiForWindow", "Ptr", Guide.Hwnd) / 96), TopicList.Hwnd)
    TopicList.OnEvent("Change", SelectTopic)
    SidebarControls := [SearchBox, CreateButton, EditButton, scriptButton, ArchiveButton, ArchiveViewButton, TopicList]
    TopicTitle := Guide.AddText("x296 y54 w730 h32 c6BCB77")
    TopicTitle.SetFont("s14 bold")
    ToolbarControls := AddFormattingToolbar(Guide, "x296 y90", false)
    AutoFitCheck := Guide.AddCheckbox("x734 y90 w110 h28", "Auto-fit text")
    AutoFitCheck.Value := AutoFit
    AutoFitCheck.OnEvent("Click", ChangeAutoFit)
    NotesBox := CreateRichControl(Guide, "x296 y128 w730 h382", true)
    StatusText := Guide.AddText("x16 y524 w1010 h24 cB9C0C8")
    StatusHwnd := StatusText.Hwnd
    Guide.OnEvent("Close", (*) => Guide.Hide())
    Guide.OnEvent("Size", ResizeGuide)
    ApplyPin()
    Guide.Show("w1045 h620")
    EnableDarkTitleBar(Guide.Hwnd)
    ApplyOpacity()
    ApplySidebar()
    FilterTopics()
}
OpenScript(*) => Run('notepad.exe "' DataRoot '\Troubleshooting_Quick_Guide.ahk"')
AddFormattingToolbar(guiObj, position, editor) {
    controls := []
    controls.Push(guiObj.AddText(position " w120 h28 +0x200", "Selected words:"))
    color := guiObj.AddButton("x+4 yp w85 h28", "Text color")
    color.OnEvent("Click", (*) => FormatSelection(editor, "color"))
    controls.Push(color)
    bold := guiObj.AddButton("x+6 yp w65 h28", "Bold")
    bold.OnEvent("Click", (*) => FormatSelection(editor, "bold"))
    controls.Push(bold)
    reset := guiObj.AddButton("x+6 yp w132 h28", "Reset formatting")
    reset.OnEvent("Click", (*) => FormatSelection(editor, "reset"))
    controls.Push(reset)
    return controls
}
ApplyOpacity() {
    if IsObject(Guide)
        WinSetTransparent(Opacity = 100 ? "Off" : Round(Opacity * 255 / 100), Guide.Hwnd)
    if IsObject(EditorGui)
        WinSetTransparent(Opacity = 100 ? "Off" : Round(Opacity * 255 / 100), EditorGui.Hwnd)
    if IsObject(Guide)
        RedrawGui(Guide)
    if IsObject(EditorGui)
        RedrawGui(EditorGui)
}
RedrawGui(guiObj) => DllCall("RedrawWindow", "Ptr", guiObj.Hwnd, "Ptr", 0, "Ptr", 0, "UInt", 0x185)
ChangeOpacity(*) {
    SetGuideOpacity(OpacitySlider.Value)
}
SetGuideOpacity(value) {
    global Opacity, SettingsPending
    nextOpacity := Max(70, Min(100, value))
    changed := nextOpacity != Opacity
    Opacity := nextOpacity
    OpacitySlider.Value := Opacity
    OpacityLabel.Text := Opacity "%"
    if !changed
        return
    ApplyOpacity()
    SettingsPending := true
    SetTimer(SaveSettingsQuietly, -250)
}
ApplyPin() {
    if IsObject(Guide)
        Guide.Opt(Pinned ? "+AlwaysOnTop" : "-AlwaysOnTop")
    if IsObject(EditorGui)
        EditorGui.Opt(Pinned ? "+AlwaysOnTop" : "-AlwaysOnTop")
}
ChangePin(*) {
    global Pinned
    Pinned := !!PinCheck.Value
    ApplyPin()
    SaveSettingsQuietly()
}
ToggleSidebar(*) {
    global SidebarHidden
    SidebarHidden := !SidebarHidden
    ApplySidebar()
    SaveSettingsQuietly()
}
ApplySidebar() {
    for control in SidebarControls
        control.Visible := !SidebarHidden
    SidebarButton.Text := SidebarHidden ? "Show topics" : "Hide topics"
    Guide.GetClientPos(, , &width, &height)
    ResizeGuide(Guide, 0, width, height)
}
ShowSidebar(*) {
    global SidebarHidden
    SidebarHidden := false
    ApplySidebar()
    SaveSettingsQuietly()
    TopicList.Focus()
}
FocusSearch(*) {
    ShowSidebar()
    SearchBox.Focus()
}
ChangeHeadingColor(*) {
    global HeadingColor
    color := PickColor(HeadingColor, Guide.Hwnd)
    if color = ""
        return
    HeadingColor := color
    RefreshFormatting()
    SaveSettingsQuietly()
}
ChangeHeadingBold(*) {
    global HeadingBold
    HeadingBold := !!HeadingBoldCheck.Value
    RefreshFormatting()
    SaveSettingsQuietly()
}
RefreshFormatting() {
    FitNotes()
    if IsObject(EditorBody)
        FormatControl(EditorBody, EditorLastText, EditorRuns, 12)
}
ChangeAutoFit(*) {
    global AutoFit
    AutoFit := !!AutoFitCheck.Value
    FitNotes()
    UpdateStatus()
    SaveSettingsQuietly()
}
FilterTopics(*) {
    global VisibleIds, CurrentId
    items := DisplayedTopics(), query := StrLower(Trim(SearchBox.Value)), ordered := ""
    for id, item in items
        ordered .= item.Title "`t" id "`n"
    ordered := Sort(ordered)
    VisibleIds := [], labels := [], index := 1
    for row in StrSplit(Trim(ordered, "`n"), "`n") {
        if row = ""
            continue
        pair := StrSplit(row, "`t"), id := pair[-1], item := items[id]
        if query != "" && !InStr(StrLower(item.Title " " item.Body " " id " " item.Shortcut), query)
            continue
        VisibleIds.Push(id)
        validShortcut := Shortcuts.Has(item.Shortcut) && Shortcuts[item.Shortcut] = id
        labels.Push((validShortcut ? "[" item.Shortcut "] " : "") item.Title)
        if id = CurrentId
            index := VisibleIds.Length
    }
    TopicList.Delete()
    if labels.Length {
        TopicList.Add(labels)
        TopicList.Choose(index)
        SelectTopic()
    } else {
        CurrentId := ""
        TopicTitle.Text := ArchiveMode ? "Archive" : "Topics"
        DllCall("SetWindowTextW", "Ptr", NotesBox.Hwnd, "Str", "No matching topics. Clear the search to see all topics.")
        FormatControl(NotesBox, GetBody(NotesBox), [], 12)
    }
    ArchiveButton.Enabled := CurrentId != ""
    EditButton.Enabled := !ArchiveMode && CurrentId != ""
    UpdateStatus()
}
SelectTopic(*) {
    global CurrentId
    if TopicList.Value < 1 || TopicList.Value > VisibleIds.Length
        return
    id := VisibleIds[TopicList.Value], changed := id != CurrentId
    CurrentId := id
    RenderTopic(changed)
}
ShowTopic(id) {
    global CurrentId
    if !DisplayedTopics().Has(id)
        return
    CurrentId := id
    SearchBox.Value := ""
    FilterTopics()
    SetSelection(NotesBox, 0, 0)
    SendMessage(0xB7, 0, 0, NotesBox.Hwnd)
}
NavigateTopic(delta, deferRender := false) {
    global CurrentId
    if !VisibleIds.Length
        return
    if !deferRender {
        index := Mod(Mod(TopicList.Value - 1 + delta, VisibleIds.Length) + VisibleIds.Length, VisibleIds.Length) + 1
        TopicList.Choose(index)
        SelectTopic()
        return
    }
    ; Commit every input's selection before returning. Only painting may be
    ; coalesced: formatting inside this callback would lose subsequent inputs
    ; at the hotkey/OnMessage single-thread limit.
    previousCritical := A_IsCritical
    Critical()
    try {
        ; The ListBox may still show the previous paint. Advance the logical
        ; topic, without native control calls in this atomic input section.
        currentIndex := 1
        for i, id in VisibleIds
            if id = CurrentId {
                currentIndex := i
                break
            }
        index := Mod(Mod(currentIndex - 1 + delta, VisibleIds.Length) + VisibleIds.Length, VisibleIds.Length) + 1
        changed := VisibleIds[index] != CurrentId
        CurrentId := VisibleIds[index]
    } finally
        Critical(previousCritical)
    if changed
        QueueTopicNavigationRender()
}
QueueTopicNavigationRender() {
    global NavigationPending
    NavigationPending := true
    ScheduleTopicNavigationRender()
}
ScheduleTopicNavigationRender() {
    global NavigationScheduled
    if !NavigationPending || NavigationScheduled || NavigationRendering || FormattingBusy
        return
    NavigationScheduled := true
    SetTimer(RenderPendingTopicNavigation, -1)
}
RenderPendingTopicNavigation() {
    global NavigationPending, NavigationScheduled, NavigationRendering
    ; Painting must be interruptible, including a new timer's initial period.
    Critical("Off")
    NavigationScheduled := false
    if !NavigationPending || NavigationRendering || FormattingBusy
        return
    NavigationPending := false
    if !IsObject(Guide) || !DllCall("IsWindowVisible", "Ptr", Guide.Hwnd)
        return
    if CurrentId = "" || !DisplayedTopics().Has(CurrentId)
        return
    NavigationRendering := true
    try {
        ; Snapshot one topic for the whole paint. Inputs can still commit a
        ; newer selection; one subsequent paint then reads the latest state.
        RenderTopic(true, DisplayedTopics()[CurrentId])
    } finally {
        NavigationRendering := false
        ScheduleTopicNavigationRender()
    }
}
RenderTopic(resetPosition := false, item := 0) {
    global NavigationPending
    if NavigationRendering && !IsObject(item) {
        QueueTopicNavigationRender()
        return
    }
    if CurrentId = "" || !DisplayedTopics().Has(CurrentId)
        return
    if !IsObject(item) {
        item := DisplayedTopics()[CurrentId]
        NavigationPending := false
    }
    if NavigationRendering
        for i, id in VisibleIds
            if id = item.Id {
                TopicList.Choose(i)
                break
            }
    ; Native control calls can dispatch a filter/selection change. An older
    ; paint must not put its topic back after that change (including empty).
    if CurrentId != item.Id
        return
    TopicTitle.Text := item.Title
    body := GetBody(NotesBox)
    if CurrentId != item.Id
        return
    if body != item.Body {
        DllCall("SetWindowTextW", "Ptr", NotesBox.Hwnd, "Str", item.Body)
        resetPosition := true
    }
    if CurrentId != item.Id
        return
    FitNotes(item)
    if resetPosition {
        SetSelection(NotesBox, 0, 0)
        RestoreScroll(NotesBox, Buffer(8, 0))
    }
    UpdateStatus()
}
TextFits(control) {
    ; Measure real Rich Edit wrapping, including custom bold spans, in twips.
    rect := Buffer(16)
    SendMessage(0xB2, 0, rect.Ptr, control.Hwnd)
    width := NumGet(rect, 8, "Int") - NumGet(rect, 0, "Int")
    height := NumGet(rect, 12, "Int") - NumGet(rect, 4, "Int")
    dc := DllCall("GetDC", "Ptr", control.Hwnd, "Ptr")
    dpi := DllCall("GetDeviceCaps", "Ptr", dc, "Int", 90)
    fr := Buffer(A_PtrSize * 2 + 40, 0)
    NumPut("Ptr", dc, "Ptr", dc, fr)
    offset := A_PtrSize * 2
    for i in [offset, offset + 16]
        NumPut("Int", 0, "Int", 0, "Int", Round(width * 1440 / dpi), "Int", Round(height * 1440 / dpi), fr, i)
    NumPut("Int", 0, "Int", -1, fr, offset + 32)
    try {
        fitted := SendMessage(0x439, 0, fr.Ptr, control.Hwnd)
        return fitted >= StrLen(GetBody(control))
    } finally {
        SendMessage(0x439, 0, 0, control.Hwnd)
        DllCall("ReleaseDC", "Ptr", control.Hwnd, "Ptr", dc)
    }
}
FitNotes(item := 0) {
    global CurrentFontSize
    if !IsObject(NotesBox)
        return
    if !IsObject(item) {
        if CurrentId = "" || !DisplayedTopics().Has(CurrentId)
            return
        item := DisplayedTopics()[CurrentId]
    }
    saved := GetSelection(NotesBox), scroll := GetScroll(NotesBox)
    if !AutoFit {
        CurrentFontSize := 12
        FormatControl(NotesBox, item.Body, item.Runs, 12)
        return
    }
    low := 12, high := 24, best := 12
    while low <= high {
        candidate := Floor((low + high) / 2)
        FormatControl(NotesBox, item.Body, item.Runs, candidate)
        if TextFits(NotesBox)
            best := candidate, low := candidate + 1
        else
            high := candidate - 1
    }
    CurrentFontSize := best
    FormatControl(NotesBox, item.Body, item.Runs, best)
    SetSelection(NotesBox, saved.Start, saved.End)
    RestoreScroll(NotesBox, scroll)
}
MoveToolbar(controls, x, y) {
    for control in controls {
        control.GetPos(, , &width)
        control.Move(x, y)
        x += width + 6
    }
}
ResizeGuide(guiObj, minMax, width, height) {
    global LayoutBusy
    if minMax = -1 || LayoutBusy || !IsObject(NotesBox)
        return
    LayoutBusy := true
    try {
        x := SidebarHidden ? 16 : 296
        TopicList.Move(, , , Max(190, height - 222))
        TopicTitle.Move(x, , width - x - 16)
        MoveToolbar(ToolbarControls, x, 90)
        AutoFitCheck.Move(x + 438, 90)
        NotesBox.Move(x, 128, width - x - 16, Max(260, height - 180))
        StatusText.Move(16, height - 34, width - 32, 28)
        FitNotes()
        UpdateStatus()
        RedrawGui(guiObj)
    } finally
        LayoutBusy := false
}
UpdateStatus() {
    if !IsObject(StatusText) || !DllCall("IsWindow", "Ptr", StatusHwnd)
        return
    warning := SettingsWarning != "" ? SettingsWarning : StartupWarnings
    if ShortcutWarnings != ""
        warning .= " Duplicate shortcuts disabled: " ShortcutWarnings
    StatusText.Text := warning != "" ? warning : (ArchiveMode ? "Archive" : "Guide")
        . "  |  " CurrentFontSize " pt  |  Up/Down: topics  |  Left/Right: opacity  |  Alt+F7: show/hide  |  Ctrl+F: search"
}
HandleGuideKeys(wParam, lParam, msg, hwnd) {
    if !IsObject(Guide) || !WinActive("ahk_id " Guide.Hwnd)
        return
    focused := DllCall("GetFocus", "Ptr")
    if focused != NotesBox.Hwnd && focused != TopicList.Hwnd
        return
    for key in ["Ctrl", "Alt", "Shift", "LWin", "RWin"]
        if GetKeyState(key)
            return
    ; Held arrows follow normal keyboard repeat; consume list arrows once.
    if wParam = 0x26 || wParam = 0x28 {
        NavigateTopic(wParam = 0x26 ? -1 : 1, true)
        return 1
    }
    if wParam = 0x25 || wParam = 0x27 {
        SetGuideOpacity(Opacity + (wParam = 0x25 ? -1 : 1))
        return 1
    }
    if lParam & 0x40000000
        return
    if wParam >= 0x41 && wParam <= 0x5A {
        key := Chr(wParam)
        if key = "C" && !ArchiveMode
            ShowEditor("create")
        else if key = "E" && !ArchiveMode
            ShowEditor("edit")
        else if key = "A"
            OpenScript()
        else if Shortcuts.Has(key) && DisplayedTopics().Has(Shortcuts[key])
            ShowTopic(Shortcuts[key])
        else
            return
        return 1
    }
}
GuideNavigationFocused() {
    if !IsObject(Guide) || !WinActive("ahk_id " Guide.Hwnd)
        return false
    focused := DllCall("GetFocus", "Ptr")
    return focused = NotesBox.Hwnd || focused = TopicList.Hwnd
}
FormatSelection(editor, action, chosenColor := "") {
    global EditorRuns
    control := editor ? EditorBody : NotesBox
    if !IsObject(control)
        return false
    if editor
        SyncEditorText()
    else if CurrentId = "" || !DisplayedTopics().Has(CurrentId)
        return false
    selection := GetSelection(control)
    if selection.Start = selection.End {
        MsgBox("Select some words first.", "Text formatting", 64)
        return false
    }
    item := editor ? 0 : DisplayedTopics()[CurrentId]
    result := CloneRuns(editor ? EditorRuns : item.Runs)
    if action = "reset"
        result := RemoveRunsInRange(result, selection.Start, selection.End)
    else {
        color := "", bold := -1
        if action = "color" {
            color := chosenColor != "" ? chosenColor : PickColor(HeadingColor, editor ? EditorGui.Hwnd : Guide.Hwnd)
            if color = ""
                return false
        } else {
            cf := Buffer(116, 0)
            NumPut("UInt", cf.Size, cf)
            SendMessage(0x43A, 1, cf.Ptr, control.Hwnd)
            bold := (NumGet(cf, 4, "UInt") & 1) && (NumGet(cf, 8, "UInt") & 1) ? 0 : 1
        }
        result.Push({Start: selection.Start, Length: selection.End - selection.Start, Color: color, Bold: bold})
    }
    if editor {
        EditorRuns := result
        EditorHistory[EditorLastText] := CloneRuns(result)
        FormatControl(control, EditorLastText, EditorRuns, 12)
    } else {
        candidate := {Id: item.Id, Title: item.Title, Body: item.Body, Path: item.Path, Shortcut: item.Shortcut, Runs: result}
        try {
            if ReadTopic(item.Path, ArchiveMode).Body != item.Body
                throw Error("The text file changed outside the app. Reopen the guide to load the updated text before formatting.")
            WriteTopic(candidate)
        }
        catch Error as err {
            MsgBox("Formatting could not be saved.`n`n" err.Message, "Save failed", 48)
            return false
        }
        item.Runs := result
        FitNotes()
    }
    SetSelection(control, selection.Start, selection.End)
    control.Focus()
    return true
}
ShowEditor(mode) {
    global EditorGui, EditorBody, EditorId, EditorTitle, EditorShortcut, EditorSave, EditorCancel
    global EditorRuns, EditorLastText, EditorLoading, EditorToolbar, EditorHistory
    if ArchiveMode
        return
    if IsObject(EditorGui) {
        EditorGui.Show()
        return
    }
    if mode = "edit" && (CurrentId = "" || !Topics.Has(CurrentId))
        return
    EditorGui := Gui("+Owner" Guide.Hwnd " +Resize +MinSize700x520", mode = "edit" ? "Edit topic" : "Create topic")
    EditorGui.BackColor := "151719"
    EditorGui.SetFont("s10 cF1F3F4", "Segoe UI")
    EditorGui.AddText("x16 y16 w30", "ID")
    EditorId := EditorGui.AddEdit("x50 y12 w236 h28 Background25282C cF1F3F4")
    EditorGui.AddText("x302 y16 w64", "Shortcut")
    EditorShortcut := EditorGui.AddEdit("x374 y12 w42 h28 Uppercase Limit1 Background25282C cF1F3F4")
    EditorGui.AddText("x432 y16 w248", "Optional; A, C, E reserved")
    EditorGui.AddText("x16 y54 w40", "Title")
    EditorTitle := EditorGui.AddEdit("x66 y50 w614 h28 Background25282C c6BCB77")
    EditorToolbar := AddFormattingToolbar(EditorGui, "x16 y88", true)
    EditorBody := CreateRichControl(EditorGui, "x16 y130 w668 h310")
    EditorSave := EditorGui.AddButton("x496 y464 w86 h32", "Save")
    EditorSave.OnEvent("Click", (*) => SaveEditor(mode))
    EditorCancel := EditorGui.AddButton("x590 y464 w86 h32", "Cancel")
    EditorCancel.OnEvent("Click", CloseEditor)
    EditorGui.OnEvent("Close", CloseEditor)
    EditorGui.OnEvent("Escape", CloseEditor)
    EditorGui.OnEvent("Size", ResizeEditor)
    EditorLoading := true
    try {
        if mode = "edit" {
            item := Topics[CurrentId]
            EditorId.Value := item.Id
            EditorId.Opt("+ReadOnly")
            EditorTitle.Value := item.Title
            EditorShortcut.Value := item.Shortcut
            EditorLastText := item.Body
            EditorRuns := CloneRuns(item.Runs)
        } else
            EditorLastText := "", EditorRuns := []
        EditorHistory := Map(EditorLastText, CloneRuns(EditorRuns))
        DllCall("SetWindowTextW", "Ptr", EditorBody.Hwnd, "Str", EditorLastText)
        FormatControl(EditorBody, EditorLastText, EditorRuns, 12)
    } finally
        EditorLoading := false
    Guide.Opt("+Disabled")
    EditorGui.Show("w740 h580")
    EnableDarkTitleBar(EditorGui.Hwnd)
    ApplyOpacity()
    ApplyPin()
    SetTimer(SyncEditorText, 120)
    (mode = "edit" ? EditorTitle : EditorId).Focus()
}
HandleEditorChange(wParam, lParam, *) {
    if IsObject(EditorBody) && lParam = EditorBody.Hwnd && (wParam >> 16) = 0x300 && !FormattingBusy && !EditorLoading
        SyncEditorText()
}
SyncEditorText(*) {
    global EditorRuns, EditorLastText, EditorHistory
    if !IsObject(EditorBody) || EditorLoading || FormattingBusy
        return
    text := GetBody(EditorBody)
    if text = EditorLastText
        return
    EditorHistory[EditorLastText] := CloneRuns(EditorRuns)
    EditorRuns := EditorHistory.Has(text) ? CloneRuns(EditorHistory[text]) : RebaseRuns(EditorRuns, EditorLastText, text)
    if EditorHistory.Count > 128
        EditorHistory := Map(text, CloneRuns(EditorRuns))
    EditorLastText := text
    FormatControl(EditorBody, text, EditorRuns, 12)
}
SaveEditor(mode) {
    SyncEditorText()
    id := StrLower(Trim(EditorId.Value)), title := Trim(EditorTitle.Value)
    shortcut := StrUpper(Trim(EditorShortcut.Value)), body := EditorLastText
    if !RegExMatch(id, "^[a-z][a-z0-9-]{0,63}$") || RegExMatch(id, "i)^(con|prn|aux|nul|com[0-9]|lpt[0-9])$") {
        MsgBox("Use an ID starting with a letter, followed by letters, digits or hyphens (up to 64 characters).", "Invalid ID", 48)
        return false
    }
    if mode = "create" && (Topics.Has(id) || Archived.Has(id) || FileExist(DataRoot "\" id ".txt") || FileExist(DataRoot "\Archive\" id ".txt")) {
        MsgBox("That ID already belongs to an active or archived topic.", "ID already used", 48)
        return false
    }
    if !RegExMatch(shortcut, "^[A-Z]?$") || shortcut != "" && InStr("ACE", shortcut) {
        MsgBox("Choose one letter, excluding A, C and E, or leave the shortcut blank.", "Invalid shortcut", 48)
        return false
    }
    for collection in [Topics, Archived]
        for otherId, other in collection
            if shortcut != "" && otherId != id && other.Shortcut = shortcut {
                MsgBox("That shortcut belongs to another active or archived topic.", "Shortcut already used", 48)
                return false
            }
    if title = "" || Trim(body) = "" || InStr(title, "`t") || InStr(title, "`n") {
        MsgBox("Enter a single-line title and some keyword reminders.", "Missing content", 48)
        return false
    }
    path := mode = "edit" ? Topics[id].Path : DataRoot "\" id ".txt"
    item := {Id: id, Title: title, Body: body, Shortcut: shortcut, Runs: CloneRuns(EditorRuns), Path: path, IsArchive: false}
    try {
        if mode = "edit" && (ReadTopic(path).Body != Topics[id].Body || ReadTopic(path).Title != Topics[id].Title)
            throw Error("The text file changed outside the app. Your editor notes are retained; copy them before reopening the guide.")
        WriteTopic(item)
    }
    catch Error as err {
        MsgBox("The topic could not be saved. Your notes remain in the editor.`n`n" err.Message, "Save failed", 48)
        return false
    }
    Topics[id] := item
    BuildShortcuts()
    BuildTopicColors()
    CloseEditor()
    ShowTopic(id)
    return true
}
CloseEditor(*) {
    global EditorGui, EditorBody
    SetTimer(SyncEditorText, 0)
    if IsObject(EditorGui) {
        Guide.Opt("-Disabled")
        EditorGui.Destroy()
        EditorGui := 0, EditorBody := 0
        WinActivate("ahk_id " Guide.Hwnd)
    }
}
ResizeEditor(guiObj, minMax, width, height) {
    if minMax = -1 || !IsObject(EditorBody)
        return
    EditorTitle.Move(, , width - 82)
    EditorBody.Move(, , width - 32, height - 202)
    EditorSave.Move(width - 196, height - 48)
    EditorCancel.Move(width - 102, height - 48)
    RedrawGui(guiObj)
}
ToggleArchiveView(*) {
    global ArchiveMode, CurrentId
    ArchiveMode := !ArchiveMode
    CurrentId := ""
    SearchBox.Value := ""
    ArchiveButton.Text := ArchiveMode ? "Restore topic" : "Archive topic"
    ArchiveViewButton.Text := ArchiveMode ? "Back to guide" : "View archive"
    CreateButton.Enabled := !ArchiveMode
    EditButton.Enabled := !ArchiveMode
    FilterTopics()
}
MoveTopic(item, restore) {
    ; Stable-ID destinations also avoid the two legacy X filename collisions.
    target := DataRoot (restore ? "" : "\Archive") "\" item.Id ".txt"
    if FileExist(target)
        throw Error("Destination already exists; no file was overwritten.")
    WriteTopic(item, target)
    try FileDelete(item.Path)
    catch Error as err {
        try FileDelete(target)
        try FileDelete(target ".styles.ini")
        throw err
    }
    if FileExist(item.Path ".styles.ini")
        try FileDelete(item.Path ".styles.ini")
    item.Path := target
    item.IsArchive := !restore
}
ArchiveOrRestore(*) {
    if CurrentId = "" || !DisplayedTopics().Has(CurrentId)
        return
    item := DisplayedTopics()[CurrentId]
    try MoveTopic(item, ArchiveMode)
    catch Error as err {
        MsgBox("The topic could not be " (ArchiveMode ? "restored" : "archived") ".`n`n" err.Message, "Topic not moved", 48)
        return
    }
    if ArchiveMode
        Archived.Delete(item.Id), Topics[item.Id] := item
    else
        Topics.Delete(item.Id), Archived[item.Id] := item
    global CurrentId := ""
    BuildShortcuts()
    FilterTopics()
}
EnableDarkTitleBar(hwnd) {
    flag := Buffer(4)
    NumPut("Int", 1, flag)
    try DllCall("dwmapi\DwmSetWindowAttribute", "Ptr", hwnd, "Int", 20, "Ptr", flag, "Int", 4)
}
