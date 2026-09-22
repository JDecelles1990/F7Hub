# F7Hub AutoHotkey Magnetic Window Follower

This supplemental note summarizes the feature; [11_AHKArchitecture.md](11_AHKArchitecture.md#79-current-implementation-status) owns the current behavior and validation status. See [18_ChangeLog.md](18_ChangeLog.md) for the review corrections.

- TAP uses `LaunchOrFocus()`.
- HOLD uses `LaunchOrFind()` after 180 ms, making the validated window visible without requesting focus.
- The follower uses a 16 ms timer, attraction, damping and a 32 px vector-speed cap. Actual integer displacement is bounded by 32 px plus approximately 0.71 px rounding tolerance.
- Targets follow the cursor monitor's work area. Intermediate movement crosses gaps without snapping to that area. Oversized axes settle at the work-area start edge without resizing.
- Release stops movement. Self-stop or startup failure consumes the HOLD attempt until release; key repeat cannot restart it.
- `F7HotkeyController.ahk` owns press state, and `MagneticWindowFollower.ahk` owns movement. Python/PySide6, database, IPC and PowerShell ownership are unchanged.

The follower and controller regression cases have been executed successfully on 2026-09-21. Fresh full live/physical validation status is recorded in the canonical document; earlier acceptance does not establish that the corrected edge cases were physically tested.

This note is retained because available Git history did not establish an intentional deletion from `main`. The documentation index routes AHK behavior to the canonical architecture document.
