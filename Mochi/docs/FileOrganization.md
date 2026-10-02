# Mochi file organization

This layout groups the existing Mochi scaffold and imported workflow assets by
purpose. It does not implement the planned pet, integrations or AI behavior.
The [MVP specification](Mochi_Luna_Light_MVP_Specification.md) is the populated
planning document previously at the Mochi root; its empty `docs` placeholder
was replaced. [Architecture](Architecture.md), [Roadmap](Roadmap.md) and the
[guide-generator README](../tools/guide_generator/README.md) now document
proposed responsibilities and future work. Source/test scaffolds and the empty
guide remain unchanged; documentation does not implement those capabilities.

## Folder responsibilities

- [Animation assets](../assets/animations/) contain the two final sprite atlases
  and 73 final frames. Both atlases are 1536 by 2288 pixels, with eight columns,
  eleven rows and 192 by 208 pixel cells. Existing frame filenames are preserved.
- [Previews](../assets/previews/) contain the final and standard GIF previews,
  final video and stills, plus contact and direction sheets under `sheets`.
- [References](../assets/references/) contain the canonical character reference,
  approved cardinal anchors and layout guides.
- [Source artwork](../assets/source/decoded/) contains the original decoded
  generation images. These are distinct from final transparent animation assets.
- [Archives](../assets/archives/) retain the original workflow ZIP unchanged.
- [Artwork documentation](artwork/) contains generation prompts, look mechanics
  and historical generation metadata. The metadata is provenance, not runtime
  settings or a configured asset loader.
- [Artwork evidence](../tests/evidence/artwork/) contains historical QA reports,
  intermediate artwork and review frames. It is separate from executable tests.
- [Configuration](../config/) and [source](../src/) retain the existing runtime
  settings and application scaffold.
- [Tools](../tools/) contains the relocated bootstrap script and the existing
  guide-generator placeholder. The bootstrap was not run during organization.

## Relocation map

All destinations below are relative to the Mochi root. In this table, `package/`
means the former `assets/Mochi-complete-workflow/mochi_pet/` directory. A trailing
slash maps every descendant and preserves its remaining relative path.

| Original path | Current path |
|---|---|
| `Mochi_Luna_Light_MVP_Specification.md` | `docs/Mochi_Luna_Light_MVP_Specification.md` |
| `Initialize-Mochi.ps1` | `tools/Initialize-Mochi.ps1` |
| `assets/Mochi-complete-workflow.zip` | `assets/archives/Mochi-complete-workflow.zip` |
| `package/decoded/` | `assets/source/decoded/` |
| `package/references/` | `assets/references/` |
| `package/final/spritesheet-extended.png` | `assets/animations/atlases/spritesheet-extended.png` |
| `package/final/spritesheet-extended-pre-despill.png` | `assets/animations/atlases/spritesheet-extended-pre-despill.png` |
| `package/final/contact-sheet.png` | `assets/previews/sheets/contact-sheet.png` |
| `package/final/direction-qa-sheet.png` | `assets/previews/sheets/direction-qa-sheet.png` |
| `package/previews/final/frames/` | `assets/animations/frames/` |
| Remaining `package/previews/` | `assets/previews/` |
| `package/prompts/` | `docs/artwork/prompts/` |
| `package/pet_request.json` | `docs/artwork/metadata/pet_request.json` |
| `package/imagegen-jobs.json` | `docs/artwork/metadata/imagegen-jobs.json` |
| `package/qa/look-mechanics.md` | `docs/artwork/look-mechanics.md` |
| Remaining `package/qa/` | `tests/evidence/artwork/qa/` |
| `package/final/validation-extended.json` | `tests/evidence/artwork/validation-extended.json` |

Specific file and frame mappings take precedence over the broader directory
rules. The emptied extraction wrapper was removed after every move was checked.

## Historical references

Imported prompts and JSON reports retain their original bytes, including paths
such as `/workspace/scratch/c7e8d42a27ac/mochi_pet/qa/frames/idle/00.png`.
Those paths describe the original generation environment. To locate an existing
artifact, take the suffix after `mochi_pet/` and apply the relocation map.
For example, that idle QA frame now lives under
`tests/evidence/artwork/qa/frames/idle/00.png`; it is not one of the final
animation frames under `assets/animations/frames/`.

Prompt references to `qa/look-mechanics.md` now correspond to
[look mechanics](artwork/look-mechanics.md). Historical references are not
rewritten into runtime configuration.

The following literal paths already lacked matching files in the extracted
package before organization:

- `decoded/look-anchors-approved.png`
- `decoded/look-anchors/000.png`, `090.png`, `180.png` and `270.png`
- `qa/contact-sheet.png`

Approved anchors do exist under `assets/references/` and cardinal review images
under `tests/evidence/artwork/qa/cardinals/`. They retain their original names
and are not silently substituted for missing historical references. The final
contact sheet is under `assets/previews/sheets/`.

The historical extended-atlas manifest also names
`spritesheet-extended-pre-despill.png` without its original `final/` folder.
The actual file was present there and is now under `assets/animations/atlases/`.
Relative path strings in historical manifests should be interpreted using the
map and provenance, rather than assumed to resolve beside the moved report.

## Duplicate exports and evidence

Six loose copies formerly under `assets/` were removed only after their sizes
and SHA-256 hashes matched these retained files:

| Removed filename | Retained location |
|---|---|
| `all-states.mp4` | `assets/previews/final/all-states.mp4` |
| `blind-review-validation.json` | `tests/evidence/artwork/qa/blind-review-validation.json` |
| `contact-sheet.png` | `assets/previews/sheets/contact-sheet.png` |
| `direction-qa-sheet.png` | `assets/previews/sheets/direction-qa-sheet.png` |
| `pet-quality.json` | `tests/evidence/artwork/qa/pet-quality.json` |
| `spritesheet-extended.png` | `assets/animations/atlases/spritesheet-extended.png` |

The original ZIP and all populated extracted files remain available. Artwork QA
reports are retained historical records; their PASS fields do not establish a
fresh artwork or runtime test. Organization checks verify inventory, byte
preservation, duplicate identity, atlas dimensions, final-frame count and links.
They do not verify animation rendering or the planned desktop application's
behavior.

The per-file relocation inventory, operation journal, candidate manifest and
fresh organization-validation report are stored outside the repository under
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Mochi-FileOrganization/`, in the dated
directory for this operation. No staging, commit or integration is performed.
