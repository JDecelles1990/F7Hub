# F7Hub AutoHotkey Magnetic Window Follower

## Scope

This focused AutoHotkey v2 feature extends the existing F7 shortcut without changing the Python/PySide6 application, repositories, database, IPC, or PowerShell layers.

## Behavior

- Tap F7: preserve the existing launch-or-focus behavior.
- Hold F7 for approximately 180 ms: launch/focus F7Hub if needed, then move the F7Hub window toward the current mouse position while F7 remains held.
- Release F7: stop the movement timer immediately and reset velocity.

## Implementation

`AutoHotkey/Helpers/MagneticWindowFollower.ahk` owns the movement behavior.

The follower:

- polls only while active using a 16 ms timer;
- reads the mouse in screen coordinates;
- computes a target position below the pointer when space permits and above it otherwise;
- accelerates proportionally toward the target;
- applies damping;
- limits maximum velocity;
- stops inside a small dead zone;
- clamps the window to the work area of the monitor containing the pointer;
- stops safely if the target window disappears.

`AutoHotkey/F7Hub.ahk` owns the tap-versus-hold decision and reuses `F7HubLauncher.LaunchOrFocus()`.

## Architecture Impact

This remains inside the approved AutoHotkey desktop-automation boundary. No business logic or persistence responsibility moves into AHK.

The feature does not use mouse-coordinate clicking, simulated mouse input, direct SQLite access, shell execution, elevation, or new IPC.

## Validation

`Tests/AutoHotkey/test_magnetic_window_follower.ahk` covers:

- invalid target rejection;
- start/stop lifecycle;
- one safe timer interval against a disposable test window;
- state and velocity reset;
- clamp boundary behavior.

The existing `Tests/AutoHotkey/test_f7hub_launcher.ahk` remains relevant because a short synthetic F7 keypress follows the tap path.

Test execution status at implementation time: NOT RUN. A native Windows AutoHotkey v2 runtime is required before marking PASS.

## Follow-up Documentation

`Docs/11_AHKArchitecture.md` remains the canonical AHK architecture document. This focused note records the implementation until the canonical document is next synchronized during review/merge.
