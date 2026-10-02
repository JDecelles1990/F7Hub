# Planned Mochi guide generator

**Status:** Documentation only. No generator, command, guide schema or output loader is implemented. `config/guide.json` is currently empty.

This proposed development tool would produce reviewed local screen guidance from a narrow source/documentation allowlist. It is separate from Mochi's runtime window recognition. Read [Mochi AGENTS.md](../../AGENTS.md), the [MVP specification](../../docs/Mochi_Luna_Light_MVP_Specification.md) and [Architecture](../../docs/Architecture.md) before implementation.

## Proposed input/output contract

- Read only explicitly selected F7Hub source/docs containing verified labels, workflows, shortcuts and identifiers. Resolve paths and reject traversal or links outside approved roots.
- Exclude databases, live ticket/customer records, clipboard, credentials, logs, local guide topics/settings, backups and unrelated files. Repository membership alone is not inclusion approval.
- For AltF7Hub source inspection, read [its instructions](../../../AutoHotkey/Troubleshooting_Sections/AGENTS.md) first. Reuse verified host/shortcut definitions without modifying the host or topic library.
- Write only to explicitly approved paths under `Mochi/`. Produce reviewable output and preserve the last approved guide on failure; do not silently overwrite authored entries or activate generated output.
- Record source revision, actual selected sources and content identities for dirty inputs, plus generator/schema version. A commit SHA alone cannot describe uncommitted source bytes.
- Treat generated guidance as untrusted. Review screen matching, hints and shortcuts against implementation before adoption.

The entry example in the MVP is illustrative; its executable names and identifiers are not an implemented contract. First prove a small manual guide, then define the generator schema and invocation within a separately authorized slice.

## Required validation when implemented

Test missing/malformed inputs, excluded files, path/link escapes, stale/dirty-source provenance, unknown identifiers, deterministic output, write containment and failure-safe replacement. Use synthetic fixtures and external validation artifacts. Do not run the bootstrap script to simulate a generator or claim historical artwork QA validates guide content.
