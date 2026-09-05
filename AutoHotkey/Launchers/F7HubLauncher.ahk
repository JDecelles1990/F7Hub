#Requires AutoHotkey v2.0

class F7HubLauncher {
    __New(projectRoot, databasePath := "") {
        this.ProjectRoot := projectRoot
        this.DatabasePath := databasePath
        this.PendingPid := 0
    }

    FindWindow() {
        ; Exact title plus Qt/Python identity avoids matching editors or browsers
        ; whose document titles happen to contain F7Hub.
        for hwnd in WinGetList("F7Hub") {
            try {
                if WinGetTitle(hwnd) == "F7Hub"
                    && RegExMatch(WinGetClass(hwnd), "^Qt.*QWindowIcon$")
                    && RegExMatch(WinGetProcessName(hwnd), "i)^pythonw?\.exe$")
                    return hwnd
            } catch TargetError {
                ; The window may close during enumeration.
                continue
            }
        }
        return 0
    }

    LaunchOrFocus(timeoutSeconds := 15) {
        if hwnd := this.FindWindow()
            return this.Focus(hwnd)

        ; Retain an unfinished launch after timeout. Another F7 must not start
        ; a second process while the original is still initializing.
        if !this.PendingPid || !ProcessExist(this.PendingPid) {
            python := this.ProjectRoot "\.venv\Scripts\pythonw.exe"
            entry := this.ProjectRoot "\Python\f7hub\__main__.py"
            if !FileExist(python) || !FileExist(entry)
                throw Error("F7Hub is not ready to launch. Check the project .venv and Python files; see ROOT.md for setup.")

            previousPath := EnvGet("PYTHONPATH")
            try {
                EnvSet "PYTHONPATH", this.ProjectRoot "\Python"
                command := '"' python '" -m f7hub'
                if this.DatabasePath != "" {
                    if InStr(this.DatabasePath, '"')
                        throw Error("The database path must not contain quotation marks.")
                    command .= ' --database "' this.DatabasePath '"'
                }
                Run command, this.ProjectRoot, , &launchedPid
                this.PendingPid := launchedPid
            } catch OSError {
                throw Error("Windows could not launch F7Hub. Check the Python environment and try again.")
            } finally {
                EnvSet "PYTHONPATH", previousPath
            }
        }

        deadline := A_TickCount + timeoutSeconds * 1000
        loop {
            if hwnd := this.FindWindow()
                return this.Focus(hwnd)
            if !ProcessExist(this.PendingPid) {
                this.PendingPid := 0
                throw Error("F7Hub exited before its window opened. Run the development launch command in ROOT.md to inspect the startup error.")
            }
            if A_TickCount >= deadline
                throw Error("F7Hub has not opened its window yet. Check for a startup error dialog, then press F7 to retry. No second instance was launched.")
            Sleep 50
        }
    }

    Focus(hwnd) {
        if WinGetMinMax(hwnd) == -1
            WinRestore hwnd
        WinActivate hwnd
        if !WinWaitActive(hwnd, , 2)
            throw Error("F7Hub is running, but Windows did not allow it to take focus. Select its window from the taskbar.")
        this.PendingPid := 0
        return hwnd
    }
}
