#Requires AutoHotkey v2.0

; Dormant CP-01 primitive. No registration, Clipboard access or Settings.
class ClipboardHotkeyPolicy {
    __New() {
        initial := ["WINWORD.EXE", "EXCEL.EXE", "OUTLOOK.EXE", "OLK.EXE", "POWERPNT.EXE"]
        this.Exclusions := Map()
        for action in ["clipboard.capture_selection", "clipboard.paste_active", "clipboard.paste_latest"]
            this.SetExclusions(action, initial)
    }

    SetExclusions(action, names) {
        if action != "clipboard.capture_selection" && action != "clipboard.paste_active"
            && action != "clipboard.paste_latest"
            throw ValueError("Unknown Clipboard action")
        excluded := Map()
        for name in names {
            basename := this.NormalizeExecutable(name)
            if basename == ""
                throw ValueError("Invalid executable identity")
            excluded[basename] := true
        }
        ; Construct first, replace atomically; the action maps never alias.
        this.Exclusions[action] := excluded
    }

    NormalizeExecutable(identity) {
        if Type(identity) != "String" || identity == "" || StrLen(identity) > 32767
            return ""
        ; Accept a basename or an absolute Windows path, never a relative path,
        ; command line, quoted name, trailing separator or ambiguous whitespace.
        if InStr(identity, "\") || InStr(identity, "/") {
            if !RegExMatch(identity, "^(?:[A-Za-z]:\\|\\\\[^\\]+\\[^\\]+\\)")
                return ""
            if RegExMatch(identity, '[<>"|?*\x00-\x1F/]')
                return ""
            pathPart := RegExMatch(identity, "^[A-Za-z]:") ? SubStr(identity, 3) : identity
            if InStr(pathPart, ":") || RegExMatch(pathPart, "(?:^|\\)\.{1,2}(?:\\|$)")
                return ""
            SplitPath identity, &basename
        } else
            basename := identity
        if !RegExMatch(basename, '^[^\\/:<>"|?*\x00-\x1F]+$')
            return ""
        if basename != Trim(basename) || SubStr(basename, -1) == "." || RegExMatch(basename, "\s+[-/]")
            return ""
        return StrLower(basename)
    }

    Allows(action, identity) {
        basename := this.NormalizeExecutable(identity)
        return this.Exclusions.Has(action) && basename != "" && !this.Exclusions[action].Has(basename)
    }

    ReadForeground() {
        try {
            hwnd := WinExist("A")
            if !hwnd
                return 0
            pid := WinGetPID(hwnd)
            exe := this.NormalizeExecutable(WinGetProcessName(hwnd))
            ; Refuse a foreground race during resolution. No window titles.
            if !pid || exe == "" || WinExist("A") != hwnd || WinGetPID(hwnd) != pid
                return 0
            creation := this.ProcessCreation(pid)
            if creation == ""
                return 0
            return {Hwnd: hwnd, Pid: pid, Exe: exe, Creation: creation}
        } catch Error {
            return 0
        }
    }

    ProcessCreation(pid) {
        ; A PID can be reused while a press is pending. Retain the creation FILETIME.
        handle := DllCall("OpenProcess", "UInt", 0x1000, "Int", 0, "UInt", pid, "Ptr")
        if !handle
            return ""
        try {
            created := Buffer(8, 0), exited := Buffer(8, 0)
            kernel := Buffer(8, 0), user := Buffer(8, 0)
            if !DllCall("GetProcessTimes", "Ptr", handle, "Ptr", created, "Ptr", exited,
                "Ptr", kernel, "Ptr", user, "Int")
                return ""
            return Format("{:08X}{:08X}", NumGet(created, 4, "UInt"), NumGet(created, 0, "UInt"))
        } finally DllCall("CloseHandle", "Ptr", handle)
    }

    AllowsContext(action, context) {
        try return IsObject(context) && IsInteger(context.Hwnd) && context.Hwnd > 0
            && IsInteger(context.Pid) && context.Pid > 0 && this.Allows(action, context.Exe)
        catch Error
            return false
    }

    SameTarget(first, second) {
        try {
            if first.Hwnd != second.Hwnd || first.Pid != second.Pid
                || this.NormalizeExecutable(first.Exe) != this.NormalizeExecutable(second.Exe)
                return false
            firstHas := HasProp(first, "Creation"), secondHas := HasProp(second, "Creation")
            return firstHas == secondHas && (!firstHas || (first.Creation != ""
                && first.Creation == second.Creation))
        }
        catch Error
            return false
    }
}
