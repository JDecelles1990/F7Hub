# Help Desk & Interview Guide

An English AutoHotkey v2 reference overlay for help desk calls and interview preparation. Topics contain unnumbered keyword reminders. The app displays notes; it does not run troubleshooting commands.

## Start

Run the parent `AutoHotkey/F7Hub.ahk` with AutoHotkey v2 installed, then press **Alt+F7**. F7Hub's Python toolbar/File action **AltF7Hub Guide** also starts or reuses this host. The Python route expects the standard 64-bit v2 installation under Program Files.

Double-clicking `Troubleshooting_Quick_Guide.ahk` starts/reuses the same host without immediately showing the guide; `--show` shows/focuses it. Repeated launches preserve an open editor and its unsaved content. Keep this directory beneath the complete F7Hub `AutoHotkey` tree; the entry is now a request client, not a separate persistent GUI script. The parent host includes `GuideHost.ahk`, `GuideCore.ahk` and `GuideRequest.ahk` and supplies this directory explicitly.

To open the window immediately from PowerShell:

```powershell
& 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe' '.\Troubleshooting_Quick_Guide.ahk' --show
```

The program stays running when its window is closed or hidden. Exit the shared F7Hub shortcut host using its AutoHotkey tray icon when needed. Existing installed copies and Windows Startup entries are not changed; use the canonical host for the integrated behavior. No third-party production dependencies are required.

## Call overlay

- **Opacity:** 60–100%, in 1% increments; default 85%. Lower values reveal more of the window behind the guide. The same opacity applies to the topic editor.
- **Always on top:** keep the guide above Teams or another call window; off by default.
- **Hide topics:** expand the notes area across the window. Ctrl+F restores the sidebar and places the text cursor at the end of Search; Ctrl+L restores the topic list.
- **Resize / maximize:** words wrap at the actual window width. Notes default to a fixed 12-point font. Optional **Auto-fit text** chooses the largest size from 12–24 points that fits the topic; long topics keep 12 points and scroll.

Opacity, pinning, sidebar visibility, auto-fit, heading color, and heading boldness persist in `GuideSettings.ini` beside the script. The overlay remains interactive; clicks on it interact with the guide.

## Formatting

Built-in automatic headings use the same topic color as the list label and large title. **Heading color** supplies the fallback when topic color metadata is unavailable; **Bold headings** controls automatic boldness. Body text is light blue at 12 points. Auto-fit is off by default. A heading is the text before ` — ` on each line.

Select words in the guide or editor, then choose **Text color**, **Bold**, or **Reset formatting**. Color changes foreground text. Bold toggles the selected range. Reset removes personal overrides in that selection and restores automatic topic styling. The selection is retained when clicking the controls.

Formatting in the guide is saved immediately. Formatting in the editor is saved with **Save**; **Cancel** discards editor changes. Explicit word formatting takes precedence over automatic topic heading styling. Automatic formatting does not fill the native text undo queue; Ctrl+Z and Ctrl+Y remain available for text editing.

## Navigation and topics

| Control | Action |
| --- | --- |
| Alt+F7 | Show / hide the guide; focus an open editor |
| Esc / window close | Hide the guide; cancel when in the editor |
| Ctrl+F | Show sidebar, focus Search and place the caret at the end of its existing text |
| Ctrl+L | Show sidebar and focus topic list |
| Ctrl+Page Up / Ctrl+Page Down | Previous / next visible topic |
| Up / Down, with notes/list focused | Previous / next visible topic; wrap at both ends |
| Left / Right, with notes/list focused | Lower / raise opacity by 1%; holding repeats; stop at 60–100% |
| Page Up / Page Down / mouse wheel | Scroll notes or use native topic-list page navigation |
| F7Hub toolbar/File: AltF7Hub Guide | Always show/focus; preserve workspace and ticket/editor drafts |
| Topic letter / interview number, with notes/list focused | Open topic or cycle its explicit group; clear search |
| C / E, with notes/list focused | Create / edit |
| Script button | Open the entry script in Notepad |

Bare letter/number shortcuts require notes or list focus and no Ctrl, Alt, Shift or Win modifier. They do not intercept Search, sliders, buttons, editor fields or dialogs. C/E are reserved for create/edit; A now navigates Applications/Azure VM. User topics may omit a shortcut and remain searchable/selectable. Their shortcuts cannot reuse built-in keys or C/E. Accidental imported duplicate keys are disabled and reported; they do not create groups.

### Complete keyboard routing reference

[TopicCatalog.md](TopicCatalog.md) contains the complete stable identity, alias/keyword, related-product, default archive and future routing reference. Colors and keyboard keys aid human navigation; future automation must select an exact stable ID.

| Key | Topic / Group | Stable Topic ID | Cycle Position | Group Size | Color | Purpose |
| --- | --- | --- | --- | --- | --- | --- |
| K | ACCOUNT ACCESS / LOCKOUT | `accounts` | Direct | 1 | #F7DC6F | Identity / Access |
| A | APPLICATIONS / CRASHES | `applications` | 1 of 2 | 2 | #7BC96F | Applications |
| A | AZURE VM | `azure-vm` | 2 of 2 | 2 | #0089D6 | Azure / Compute |
| None | CUSTOMER COMMUNICATION | `customer-communication` | None | 0 | #F8B195 | Support / Communication |
| G | DNS / INTERNET | `dns` | Direct | 1 | #4DD0E1 | Network / Internet |
| Y | FORTINET / FORTIGATE | `fortigate` | Direct | 1 | #EE3124 | Network / Firewall |
| H | HARDWARE / PERIPHERALS | `hardware` | 1 of 2 | 2 | #FF9F43 | Devices / Peripherals |
| I | IDENTITY / MICROSOFT 365 | `identity` | Direct | 1 | #B39DDB | Microsoft 365 / Identity |
| 2 | INTERVIEW / BEHAVIORAL ANSWERS | `interview-behavioral` | Direct | 1 | #C792EA | Interview preparation |
| 4 | INTERVIEW / PERSONAL MOTIVATION | `interview-personal` | Direct | 1 | #C792EA | Interview preparation |
| 5 | INTERVIEW / QUESTIONS TO ASK | `interview-questions` | Direct | 1 | #C792EA | Interview preparation |
| 3 | INTERVIEW / STAR STORY PROMPTS | `interview-star` | Direct | 1 | #C792EA | Interview preparation |
| 1 | INTERVIEW / TECHNICAL ANSWERS | `interview-technical` | Direct | 1 | #C792EA | Interview preparation |
| B | LINUX | `linux` | Direct | 1 | #FCC624 | Operating systems / Linux |
| U | MACOS | `macos` | Direct | 1 | #B0BEC5 | Operating systems / Apple |
| X | MAPPED DRIVES / SMB | `mapped-drives` | Direct | 1 | #81D4FA | Network / File shares |
| M | TROUBLESHOOTING METHODOLOGY | `methodology` | Direct | 1 | #6BCB77 | Support / Troubleshooting |
| N | NETWORK | `network` | Direct | 1 | #45B7D1 | Network / Connectivity |
| D | ONEDRIVE SYNC | `onedrive-sync` | Direct | 1 | #0078D4 | Microsoft 365 / Storage |
| O | OUTLOOK / EMAIL | `outlook` | Direct | 1 | #2B88D8 | Microsoft 365 / Messaging |
| L | PERFORMANCE / DISK SPACE | `performance` | Direct | 1 | #FFD93D | Devices / Performance |
| S | PHISHING / SECURITY TRIAGE | `phishing` | 2 of 2 | 2 | #FF5A5F | Security / Incident triage |
| None | XXX | `placeholder-active` | None | 0 | #90A4AE | Compatibility / Placeholder |
| None | XXX | `placeholder-archived` | None | 0 | #78909C | Compatibility / Placeholder |
| H | POWER / STARTUP / DISPLAY | `power` | 2 of 2 | 2 | #FF9F43 | Devices / Startup and display |
| R | PRINTING | `printing` | Direct | 1 | #A8DADC | Devices / Printing |
| None | PRIORITIZATION / ESCALATION | `prioritization` | None | 0 | #FFB4A2 | Support / Escalation |
| W | WINDOWS SERVICES | `services` | 2 of 3 | 3 | #00A4EF | Windows / Services |
| S | SHAREPOINT / FILE ACCESS | `sharepoint` | 1 of 2 | 2 | #1AA3A3 | Microsoft 365 / Collaboration |
| T | TEAMS / AUDIO / VIDEO | `teams` | Direct | 1 | #6264A7 | Microsoft 365 / Meetings |
| None | TICKETING / DOCUMENTATION | `ticketing` | None | 0 | #80CBC4 | Support / Documentation |
| V | VPN | `vpn` | Direct | 1 | #26A69A | Network / Remote access |
| W | WINDOWS | `windows` | 3 of 3 | 3 | #00A4EF | Operating systems / Windows |
| W | WINDOWS 365 / CLOUD PC | `windows-365` | 1 of 3 | 3 | #00A4EF | Microsoft cloud / Cloud PC |

A, S, H and W use the exact listed order. A repeated fresh press advances from the current topic and wraps; from outside the group it selects the first available member. Missing members are skipped. Windows is archived by default, so active W normally cycles Windows 365 then Services; Windows joins only when actually active. Held letter/number repeats are ignored. The five interview keys share #C792EA.

Shortcut selection clears Search and reaches topics excluded by its filter. Only the current active/archive collection participates. Archive view shortcuts select archived reference notes without restoring them. With no available target the key does nothing. Group order does not follow filesystem enumeration, Map iteration, list sorting or search results.

Search covers title, body, stable ID and shortcut in the current view. The list stays alphabetically sorted. Each topic's effective color matches its list label, large title and automatic heading text; personal word overrides retain precedence. Long list labels use an ellipsis. New user topics receive a stable ID-derived fallback color, which may coincide with other colors and never determines identity.

Use **Create** for a topic with a new stable ID, title, optional unused letter and reminders. Built-in IDs are reserved even if their files are absent; editor IDs cannot change. **Archive topic** and **Restore topic** preserve ID, effective color, content and paired formatting metadata; filenames may change to the stable ID. Local choices determine active/archive counts. The supplied library has 34 built-ins, including macOS, Azure VM, Windows 365 and preserved historical placeholders. Interview prompts invite real examples rather than inventing achievements.

Future Ticket → AltF7Hub automation remains deferred. Its semantic target is a stable ID (`outlook`, `azure-vm`), through a later approved extension of the existing shared host boundary. Never simulate repeated shortcut presses or identify topics by filename/title/list position/color. Aliases are non-authoritative future classification hints. Specific validated product evidence takes precedence over generic topics; ambiguity requires more evidence or technician selection. See the catalog for the complete future contract and exclusions.

## Text files and compatibility

Active topics are UTF-8 `*.txt` files directly beside the script; archived topics are in `Archive`. Only those two directories are scanned. The first line is the title; the remaining lines are the reminders. Example:

```text
NETWORK
SCOPE — device · user · site · outage
CONNECTIVITY — DNS · gateway · VPN · proxy · known-good network
VALIDATE — original workflow · user confirmation
```

New topic filenames use their stable IDs. Existing letter files retain compatibility: P is power, Q is interviewer questions, Y is FortiGate, Z is personal interview motivation, and Archive/W is Windows. Legacy EN/FR content is read through its English portions.

Both original X placeholder contents containing XXX/XXXX were preserved. Archive/restore may move them to filenames based on their distinct IDs. Their IDs are `placeholder-active` and `placeholder-archived`, with no assigned letter. Mapped drives is a separate topic using X. Windows remains archived until restored through the app.

Each `topic.txt.styles.ini` sidecar contains the stable ID, optional shortcut, format version, text fingerprint, and selected-word ranges. Keep the sidecar with its text file when copying topics. Sidecars and settings use UTF-16 for Windows INI compatibility; topic text stays UTF-8. Ranges use Rich Edit's UTF-16 character coordinates, with one character per line break.

External text edits that no longer match the formatting fingerprint discard incompatible personal formatting on load; automatic headings still apply. Hide and show the guide with Alt+F7 to reload external changes. The app refuses to overwrite externally changed text when saving a stale editor or applying stale selection formatting. Copy unsaved editor content before reopening in that case.

Saves prepare both text and formatting before replacing existing files. Save failures keep the editor open; recoverable commit failures restore the previous files. If rollback itself fails, the error identifies the retained recovery copy.

## F7Hub integration and future macros

The Python action calls AltF7HubService through the existing worker, then a fixed Windows gateway and this request client. The client coordinates concurrent requests, waits at most ten seconds for its checkout-specific host, sends one fixed show/focus message and waits at most three seconds for acknowledgement. It confirms a visible guide/editor before success. A dispatched timeout remains unconfirmed and never triggers a second send or keyboard toggle. Before dispatch only, a verified hidden guide without an editor may use one guarded Alt+F7 fallback; held modifier keys reject that fallback. No ticket content or executable command is transferred.

Later ticket-to-topic macros are **DEFERRED**. Existing stable topic IDs and assigned letters remain available for a separately designed ticket-context/matching workflow; there is no automatic issue detection or topic selection now.

## Backup and verification

Before the earlier standalone-guide implementation, the original script, README, five active text files, and two archive files were copied to `Backups/20261001-094226`. Copied top-level files were hash-verified before editing. Backups are never loaded as topics.

Run the isolated native smoke suite from this folder:

```powershell
& 'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe' /ErrorStdOut '.\Tests\guide_smoke.ahk' | Out-String
```

The test uses a temporary topic copy and does not edit your live library. The supplied `Tests/Evidence/VALIDATION.md` and screenshots record the earlier standalone guide and are preserved historical evidence. Current Slice 046 manifests, suite results, implementation report and three inspected native captures are under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\Slice-046`. Current validation includes 162 guide checks, 29 shared-host checks, 7 request-failure checks, 13 Python/native checks, GUI 181 and Integration 156, plus existing F7 launcher/follower regressions. On resume, regression execution evidence is retained with unchanged relevant inputs; the native Python checks were freshly rerun and all 18 current AHK files passed fresh v2.0.26 parser validation. Validation was performed on Windows at 96 DPI (100% scaling); automated repeated-key messages do not establish physical hardware acceptance. Camera/Teams verification is separate from the simulated-call overlay inspection.

## Technical references

Depth cues draw on general diagnostic practice and the following vendor references; commands remain reminders, with version-specific syntax and change approval handled by the technician.

- [Microsoft 365 troubleshooting](https://learn.microsoft.com/en-us/troubleshoot/microsoft-365-apps/)
- [Microsoft DNS troubleshooting guidance](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/troubleshoot-dns-guidance)
- [Active Directory troubleshooting](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/ad-ds-troubleshooting)
- [FortiGate CLI troubleshooting reference](https://docs.fortinet.com/document/fortigate/7.4.0/cli-troubleshooting-cheat-sheet/420966)

`Tools/expand_topics.py` is a maintenance utility used to append the depth cues without duplicating lines. It preserves existing text as a prefix and matching formatting ranges. Python is used only for that utility, not for running the GUI.
