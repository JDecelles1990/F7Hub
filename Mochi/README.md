# Mochi Luna Light

Mochi Luna Light is a Windows desktop companion within the F7Hub repository.
Slice 001 implements an independent Python/PySide6 pet window using existing
idle artwork. Local guidance and optional Luna assistance remain planned.

## Run Slice 001

Use the repository's Python environment with its existing PySide6 dependency.
The current candidate is in the isolated worktree; the original workspace is unchanged:

```powershell
& C:\Dev\F7Hub\.venv\Scripts\python.exe -B C:\Dev\F7Hub-Mochi-S001\Mochi\src\main.py
```

The launcher works from any working directory. For the module entry point, set
`PYTHONPATH` to the checkout's `Mochi/src` directory and run `python -m mochi`.
Distribution packaging and a Windows executable are deferred.

Left-drag the pet to move it. Right-click for **Pause**, **Resume**, and **Exit**.
Pause freezes the current frame; Resume continues it. Exit ends the process.
The window starts without activating itself; direct clicks and menus may activate
it. No global hotkeys or click-through mode are introduced.

## Settings and failures

`config/settings.json` is resolved from the Mochi installation directory, never
from the current working directory. Existing app name/enabled and pet topmost/
opacity settings are supported. Optional `animation` values select the relative
`frame_directory`, `idle_row`, and `frame_interval_ms`; defaults are
`assets/animations/frames`, `0`, and `120`. Frame columns sort numerically.

Invalid/missing settings use logged safe defaults without rewriting the file.
Opacity must be finite and between 0.1 and 1.0; interval must be an integer between
20 and 2000 ms, and row an integer between 0 and 10. Frame directories must remain
inside Mochi. Unreadable/corrupt frames or inconsistent dimensions stop startup
with a useful stderr diagnostic and exit 1. Loading is bounded to 128 frames of
at most 2048×2048 pixels each. Disabled applications exit 0 without a window.

Privacy, clipboard, OCR, capture, F7Hub integration, and click-through settings
cannot enable capabilities in this slice. Configuration is never secret storage.
Logs live under ignored `logs/mochi.log`, with 1 MiB rotation and two backups;
file-logging failure falls back to stderr. Only Mochi's logger is configured.

## Planned MVP

- A movable animated pet with a short hint bubble, hide and exit controls.
- Local recognition of a few verified screens using approved window/control metadata.
- Reviewed hints that work offline; safe manual help for unknown screens.
- Optional advisory answers through a provider adapter once Luna details are confirmed.

The MVP excludes screenshots, OCR, clipboard monitoring, ticket/customer-data collection and automated clicks, typing or commands. Future selected-text assistance requires separate scope and privacy design.

## Architecture

F7Hub remains the primary Python/PySide6 application and system of record. The
pet renderer uses PySide6 Widgets; it imports no F7Hub application code, reads no
SQLite database and starts no external commands. Settings, frame loading, pure
state/playback behavior, and presentation are separate. Packaging, recognition,
providers and any future IPC contract remain decisions for later reviewed slices.

## Current status

| Component | Inspected status |
|---|---|
| Animation assets | Two atlases and 73 final frames are present; artwork QA is historical |
| Python entry point | `src/main.py` and `python -m mochi` launch the standalone pet |
| Runtime and tests | Named `src/mochi` package; 41 focused automated tests PASS |
| Settings | Validated, read-only loader with safe defaults; excluded capabilities unavailable |
| Screen guide | `config/guide.json` is empty; schema, entries and resolver are planned |
| Pet UI | Slice 001 implemented; native Windows validation PASS at 96 DPI |
| Recognition, F7Hub adapter, Luna, generator | PLANNED |

Fresh Slice 001 checks exercised compositor transparency, animation, topmost
behavior, startup focus, menu actions, dragging, cross-monitor movement and clean
exit using bounded OS-injected inputs. Both standalone launch routes exited 0.
Screenshots were inspected separately from process results. Physical-user input
and DPI scales above 100% were NOT RUN. These are implementation self-checks;
independent review remains pending. Evidence and the candidate manifest are
outside the worktree under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Mochi-Slice-001/`.

Run focused tests from `Mochi` with `PYTHONPATH` pointing to its `src` folder and
`QT_QPA_PLATFORM=offscreen`: `python -B -m unittest discover -s tests -v`.
Tests use synthetic temporary configuration/images, not desktop settings.
The [MVP specification](docs/Mochi_Luna_Light_MVP_Specification.md) remains the
broader planning baseline; it does not authorize subsequent slices.

## File layout

| Folder | Purpose |
|---|---|
| [assets/animations](assets/animations/) | Final sprite atlases and 73 individual frames |
| [assets/previews](assets/previews/) | GIF/video previews, stills and contact sheets |
| [assets/references](assets/references/) | Character references and layout guides |
| [assets/source](assets/source/) | Original decoded generation images |
| [assets/archives](assets/archives/) | Original workflow ZIP |
| [config](config/) | Initial settings and empty guide placeholder |
| [docs](docs/) | MVP, proposed architecture, roadmap, organization and artwork generation records |
| [src](src/) | Runtime package, compatibility launcher and preserved initial scaffolds |
| [tests/evidence/artwork](tests/evidence/artwork/) | Historical artwork QA reports and supporting images |
| [tools](tools/) | Bootstrap script and documentation for a planned guide generator |

Read [File organization](docs/FileOrganization.md) for the original-to-current
path mapping, duplicate policy and historical-report limitations.
The [bootstrap script](tools/Initialize-Mochi.ps1) retains its original contents
and fixed Mochi root; it was relocated without being executed. It writes scaffold
files and is not needed to read the documentation or view existing assets.

## Documentation and development

Read [AGENTS.md](AGENTS.md) before work. Use the [Architecture](docs/Architecture.md) for component boundaries and unresolved decisions, [Roadmap](docs/Roadmap.md) for proposed slices, and [guide-generator contract](tools/guide_generator/README.md) for future source/output restrictions. For AltF7Hub work, first read [its instructions](../AutoHotkey/Troubleshooting_Sections/AGENTS.md) and [user guide](../AutoHotkey/Troubleshooting_Sections/README.md).

No provider endpoint, credentials or recognition contract has been selected.
Historical generation metadata and artwork QA remain unchanged and are separate
from fresh desktop-runtime evidence. Suggested Slice 002 scope is hide/show and
one additional reviewed animation; it has not started.
