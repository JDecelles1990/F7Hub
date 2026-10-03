# AltF7Hub Knowledge source

[AltF7Hub-Troubleshooting-Topics.yaml](AltF7Hub-Troubleshooting-Topics.yaml) is the supplied schema-version-2 reference corpus: **31 topics, 841 ordered sections and 3,089 prompts**. It includes technical troubleshooting, technician communication and interview preparation.

## Verified local import — 2026-10-03

The complete corpus was imported into the development application's `Database/Dev/f7hub_dev.db` through `KnowledgeService → KnowledgeRepository → SQLite`. Each topic became one **DRAFT, version 1** article, with a matching initial historical snapshot and a searchable FTS entry. The pre-existing article was preserved, bringing the local total to 32 at completion. The technician confirmed that it worked in the application.

In **Knowledge Base**, choose status **All** or **Draft** and search **ALTF7HUB** to read the imported articles.

This repository preserves the source corpus and import record. The completed import belongs to the local development database, which is ignored by Git. Cloning the repository does not populate another database automatically. No installed-runtime database or database migration was changed.

## Content mapping and ownership

| YAML field | Knowledge article mapping |
|---|---|
| `filename` | Stable code `ALTF7HUB-` plus the uppercase filename stem; for example, `accounts.txt` becomes `ALTF7HUB-ACCOUNTS` |
| `title` | Article title |
| `patterns[].category` | Ordered heading in the article body |
| `patterns[].prompts[]` | Ordered `- ` bullet text beneath that heading |
| `relative_path`, `sha256` | Source footer with the original path and the topic checksum declared by the YAML |
| Root source and schema metadata | Source footer with collection, schema version, import-file path and checksum |

The summary is `AltF7Hub reference prompts from <filename>.` All headings and prompts retain their source order and text. The existing Knowledge reader displays the body as plain text. Section headings are content; they do not create relational Knowledge categories or tags. Source checksums record YAML provenance; the original AutoHotkey topic files were not revalidated during this import.

The YAML SHA-256 at import was `9b99c345e2db3a2ba8080b8d7de0e4f11d50aea3a4fb957756144ce1505a9814`. The supplied YAML and AutoHotkey topics were left unchanged. Articles remain normal local Knowledge records and may evolve through existing editing/publishing workflows. No automatic synchronization with YAML or AutoHotkey was introduced.

## Validation and recovery record

A validated SQLite backup was created before live writes. Rehearsal and live validation checked all 31 article bodies, initial snapshots and search results; all original rows and unrelated relational tables were preserved. SQLite `integrity_check` returned `ok`, and `foreign_key_check` returned zero violations. A separate readback compared every ordered section and prompt against the YAML. Repeating the import created zero duplicates. Rehearsal rejected malformed counts, duplicate YAML keys and conflicting existing article content, and an injected historical-snapshot failure rolled back the article transaction.

Each article was committed atomically through the existing service/repository boundary. The entire corpus used individual transactions, so an interrupted operation requires inspecting committed state before resuming. Existing content was never overwritten. Do not replace the whole live database from the backup after later user edits merely to undo this import.

The one-time importer, rendered candidate, validated backup identity, per-article commit journal, rehearsal database, results and original implementation report are local evidence under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/KnowledgeImport-AltF7Hub-20261003-152725`. The backup is under `%LOCALAPPDATA%/F7Hub/Backups/`. These artifacts are outside Git. The one-time importer used PyYAML already available in the development environment; no application dependency or packaged importer was added.

The import validation is retained evidence for the source/documentation integration after checking unchanged relevant inputs. Technician confirmation supplies manual acceptance; no automated native UI run is claimed. Application code, schema and interaction behavior did not change, so a new full application regression was not required for this content/documentation integration.
