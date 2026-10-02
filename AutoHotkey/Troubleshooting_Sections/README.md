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

- **Opacity:** 70–100%, in 1% increments; default 85%. Lower values reveal more of the window behind the guide. The same opacity applies to the topic editor.
- **Always on top:** keep the guide above Teams or another call window; off by default.
- **Hide topics:** expand the notes area across the window. Search or Ctrl+L restores the sidebar.
- **Resize / maximize:** words wrap at the actual window width. Notes default to a fixed 12-point font. Optional **Auto-fit text** chooses the largest size from 12–24 points that fits the topic; long topics keep 12 points and scroll.

Opacity, pinning, sidebar visibility, auto-fit, heading color, and heading boldness persist in `GuideSettings.ini` beside the script. The overlay remains interactive; clicks on it interact with the guide.

## Formatting

Use **Heading color** and **Bold headings** for shared automatic formatting. The default is green, bold headings and light blue body text at 12 points. Auto-fit is off by default. A heading is the text before ` — ` on each line.

Select words in the guide or editor, then choose **Text color**, **Bold**, or **Reset formatting**. Color changes foreground text. Bold toggles the selected range. Reset removes personal overrides in that selection and restores shared styling. The selection is retained when clicking the controls.

Formatting in the guide is saved immediately. Formatting in the editor is saved with **Save**; **Cancel** discards editor changes. Explicit word formatting takes precedence over shared heading preferences. Automatic formatting does not fill the native text undo queue; Ctrl+Z and Ctrl+Y remain available for text editing.

## Navigation and topics

| Control | Action |
| --- | --- |
| Alt+F7 | Show / hide the guide; focus an open editor |
| Esc / window close | Hide the guide; cancel when in the editor |
| Ctrl+F | Show sidebar and focus search |
| Ctrl+L | Show sidebar and focus topic list |
| Ctrl+Page Up / Ctrl+Page Down | Previous / next visible topic |
| Up / Down, with notes/list focused | Previous / next visible topic; wrap at both ends |
| Left / Right, with notes/list focused | Lower / raise opacity by 1%; holding repeats; stop at 70–100% |
| Page Up / Page Down / mouse wheel | Scroll notes or use native topic-list page navigation |
| F7Hub toolbar/File: AltF7Hub Guide | Always show/focus; preserve workspace and ticket/editor drafts |
| Topic letter, with notes/list focused | Open assigned topic |
| C / E / A, with notes/list focused | Create / edit / open script |

Letter shortcuts do not intercept search, sliders, buttons, modified selection keys, or editor input. The displayed letter is optional: topics without a letter remain searchable and selectable. Duplicate imported letters are disabled and reported in the status area. A, C, and E are reserved; active and archived letters cannot be reused when creating or editing a topic.

Each topic has a distinct, readable color in the left list, derived from its stable ID. Colors stay consistent between active and archive views. Long labels use an ellipsis; the full title appears above the notes. Search covers titles, keyword reminders, IDs, and shortcuts in the current active/archive view. Troubleshooting and interview subjects share one alphabetically sorted list.

Use **Create** for a new topic: choose a stable ID (letters, digits, hyphens; starting with a letter), title, optional shortcut, and reminders. IDs cannot be changed while editing. **Archive topic** moves a topic out of the active library; **View archive** shows archived topics and enables **Restore topic**. Restore preserves its ID, shortcut, text, and formatting.

The library contains 31 topics in total. Active/archive counts follow your archive choices; Windows remains archived by default. It includes FortiGate, Linux, hardware, communication, ticketing, prioritization, escalation, technical interview prompts, STAR stories, and your personal motivation and interviewer questions. The library includes 580 additional keyword-only depth cues: scope matrices, diagnostic tools, logs, authentication, policy, dependencies, comparison tests, controlled recovery, and escalation evidence. Interview prompts invite real examples rather than supplying invented achievements.

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
