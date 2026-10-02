# Mochi Luna Light

Mochi Luna Light is a planned Windows desktop companion within the F7Hub repository. Its first useful role is local guidance for explicitly supported F7Hub and AltF7Hub screens. Optional Luna answers require a user question, an exact payload preview and an explicit Send action.

## Planned MVP

- A movable animated pet with a short hint bubble, hide and exit controls.
- Local recognition of a few verified screens using approved window/control metadata.
- Reviewed hints that work offline; safe manual help for unknown screens.
- Optional advisory answers through a provider adapter once Luna details are confirmed.

The MVP excludes screenshots, OCR, clipboard monitoring, ticket/customer-data collection and automated clicks, typing or commands. Future selected-text assistance requires separate scope and privacy design.

## Architecture

F7Hub remains the primary Python/PySide6 application and system of record. Mochi must use approved service/adaptor boundaries and preserve the shared F7/Alt+F7 AHK host. Window Spy helps developers inspect identifiers; it is not a runtime navigation engine. The pet renderer, packaging and any new IPC contract remain decisions for review.

## Current status

| Component | Inspected status |
|---|---|
| Animation assets | Two atlases and 73 final frames are present; artwork QA is historical |
| Python entry point | `src/main.py` prints a startup message; it does not create a window |
| Source packages and tests | Empty scaffolds; no executable feature tests |
| Settings | Initial JSON values; no loader or privacy enforcement implemented |
| Screen guide | `config/guide.json` is empty; schema, entries and resolver are planned |
| Pet UI, recognition, F7Hub adapter, Luna, generator | PLANNED |

There is no desktop-pet launch command or functioning integration yet. The [MVP specification](docs/Mochi_Luna_Light_MVP_Specification.md) is the accepted planning baseline, not implementation authorization or runtime validation.

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
| [src](src/) | Existing application scaffold |
| [tests/evidence/artwork](tests/evidence/artwork/) | Historical artwork QA reports and supporting images |
| [tools](tools/) | Bootstrap script and documentation for a planned guide generator |

Read [File organization](docs/FileOrganization.md) for the original-to-current
path mapping, duplicate policy and historical-report limitations.
The [bootstrap script](tools/Initialize-Mochi.ps1) retains its original contents
and fixed Mochi root; it was relocated without being executed. It writes scaffold
files and is not needed to read the documentation or view existing assets.

## Documentation and development

Read [AGENTS.md](AGENTS.md) before work. Use the [Architecture](docs/Architecture.md) for component boundaries and unresolved decisions, [Roadmap](docs/Roadmap.md) for proposed slices, and [guide-generator contract](tools/guide_generator/README.md) for future source/output restrictions. For AltF7Hub work, first read [its instructions](../AutoHotkey/Troubleshooting_Sections/AGENTS.md) and [user guide](../AutoHotkey/Troubleshooting_Sections/README.md).

No provider endpoint, credentials, renderer or recognition contract has been selected here. Historical generation metadata and QA reports establish asset provenance; they do not configure Luna or prove desktop behavior.
