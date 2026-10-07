# F7Hub Agent Contract

F7Hub is a modular Windows IT support and technician-productivity platform.
Build the correct system through small, tested, documented, secure and reversible changes.
Canonical development root: `C:\Dev\F7Hub`; production paths must use approved path/configuration infrastructure.
This file owns project-wide agent behavior; detailed architecture and procedures belong to the owners below.

## Instruction precedence

- Explicit user requirements and approved architectural decisions take precedence over project guidance.
- Apply root guidance and every applicable scoped `AGENTS.md`; more specific guidance specializes its scope.
- Scoped guidance must preserve repository-wide safety, security and architecture requirements.
- Skills define procedures and must not override user scope, applicable agent instructions or approved F7Hub architecture.
- Reading a document or skill grants no implementation, execution, staging or integration authority.

## Entry point and progressive context

Read [ROOT.md](ROOT.md) for substantial new work, orientation, architecture decisions, major reviews or documentation-routing decisions. A focused edit with established context does not require rereading it.
Use [Docs/19_DocumentationIndex.md](Docs/19_DocumentationIndex.md) as the canonical documentation router.

Load context progressively, selecting the minimum sufficient material:

1. Root agent instructions.
2. `ROOT.md` when orientation is required.
3. `Docs/19_DocumentationIndex.md`.
4. Applicable scoped agent instructions.
5. Minimum relevant canonical/planning documents and necessary dependency contracts.
6. Relevant available project skills.
7. Repository evidence and existing functionality.
8. Relevant tests.

Do not load the entire documentation tree by default or copy the full documentation inventory here.
Inspect actual filenames, status and approval records; documented existence is not proof of availability.

## Scoped guidance and skills

- Planning work must apply [Docs/Planning/AGENTS.md](Docs/Planning/AGENTS.md).
- Foundation work must additionally apply [Docs/Planning/Foundation/AGENTS.md](Docs/Planning/Foundation/AGENTS.md).
- Any task reading, analyzing, modifying, testing, reviewing or documenting AltF7Hub or `AutoHotkey/Troubleshooting_Sections/**` MUST explicitly read [its AGENTS.md](AutoHotkey/Troubleshooting_Sections/AGENTS.md) first, including repository-root sessions.
- Apply [PowerShell/AGENTS.md](PowerShell/AGENTS.md) for work under `PowerShell/`; consult it and the execution architecture for F7Hub PowerShell execution-boundary work.
- Discover other scoped instructions under the target path; do not assume this list is exhaustive.
- Inspect `.agents/skills/` and use relevant existing skills; never assume a skill exists from its expected name.
- [vertical-slice-delivery](.agents/skills/vertical-slice-delivery/SKILL.md) owns slice lifecycle, evidence, continuity, independent review and controlled Git integration when applicable.
- Use canonical owners when optional skills are absent. Missing required guidance that would force guessing is a blocker.
- A skill named `pyqt6` does not authorize replacing PySide6.
- Do not mechanically apply implementation lifecycle machinery to documentation-only architecture work.

## Source of truth and evidence

Resolve project-information conflicts in this order:

1. Explicit user requirement.
2. Explicitly approved architectural decision.
3. Current canonical project documentation.
4. Validated implementation.
5. Executed passing tests.
6. Established project conventions.
7. Engineering inference.

Canonical documents define intended requirements; inspection establishes actual state.
Distinguish `FACT`, `ASSUMPTION`, `INFERENCE`, `RECOMMENDATION` and `NOT VERIFIED`.
Never invent files, tables, capabilities, approvals or test results.
Keep documentation approval, implementation and verification separate; `APPROVED` does not mean `IMPLEMENTED` or `VERIFIED`.
Archived material and research are not current approved architecture.
Verify current official documentation for changing external technologies/APIs before relying on them.

## Workflow and scope

For significant work: `UNDERSTAND → INSPECT → PLAN → IMPLEMENT → TEST → REVIEW → DOCUMENT`.
Use the smallest coherent, independently testable vertical slice.
Define objective, context, scope, exclusions, constraints, acceptance criteria, validation and deliverables.
Implement only the authorized scope and stop at the requested lifecycle gate.
Planning and independent review remain read-only for production unless the user explicitly changes scope.
Do not add unrelated refactoring, renaming, documentation cleanup, dependencies or neighboring features.
Record unrelated improvements as follow-ups; reading related documents does not expand authorization.

Before creating a table, migration, component, service, gateway, registry, protocol or configuration mechanism:
`SEARCH → IDENTIFY → REUSE / EXTEND → CREATE ONLY IF NECESSARY`.
Search documentation, filenames, implementation, migrations and tests before claiming functionality is absent; create no table merely to meet an arbitrary count.
Justify dependencies against the standard library/current dependencies, maintenance, security and compatibility.
Detailed dependency and engineering principles belong to [Docs/14_DesignPrinciples.md](Docs/14_DesignPrinciples.md).
Report templates belong to the applicable delivery skill and scoped planning instructions; review findings should prioritize concrete defects over stylistic preferences.

## Architecture and technology ownership

Preserve the modular monolith and preferred dependency direction:
`PySide6 GUI → Application Services → Domain Logic → Repositories / Gateways → Infrastructure`.

| Technology | Ownership |
|---|---|
| Python / PySide6 | Primary desktop GUI, orchestration, application services, domain coordination, repositories and integrations |
| SQLite | Primary persistent relational store |
| PowerShell 7 | Windows/Microsoft administration, diagnostics, reporting and controlled automation |
| AutoHotkey v2 | Global hotkeys, hotstrings, clipboard helpers, launch/focus and lightweight desktop interaction |

AutoHotkey work uses v2 syntax; do not introduce AHK v1 syntax.
Do not move responsibilities between technologies for convenience or introduce speculative infrastructure.
GUI widgets collect input and render state; they do not own SQL, domain rules, credentials or shell-command construction.
Services own use cases; repositories own normal persistence; gateways isolate processes and external providers.
Domain logic must remain independent of GUI, SQLite implementation details and provider SDKs.
PowerShell and AHK must not independently own core SQLite writes or become a parallel primary application.
Plugins require an approved use case and must not receive unrestricted database access by default.
Mochi must preserve approved application-service, execution, persistence and security boundaries.
Detailed boundaries belong to [Docs/06_SystemArchitecture.md](Docs/06_SystemArchitecture.md); Python/GUI procedures belong to [Docs/13_PythonArchitecture.md](Docs/13_PythonArchitecture.md).
Do not block the PySide6 event loop with long operations; update widgets only from the GUI thread.

## Foundation routing and escalation

Before cross-cutting architectural decisions, read Foundation guidance and the relevant approved contract.
Use [Docs/Planning/Foundation/AGENTS.md](Docs/Planning/Foundation/AGENTS.md) to locate the owning phase:

| Concern | Foundation owner |
|---|---|
| Ownership, layers, technology responsibilities, trust and integration boundaries | 0A — Master Foundation Architecture |
| JSON, IPC, interoperability, serialization and versioning | 0B — Global JSON / Interoperability Contract |
| Taxonomy, Entity, Tag, provenance, confidence and vocabulary extension | 0C — Taxonomy / Information Vocabulary |
| Settings, defaults, overrides, precedence and configuration versus secrets | 0D — Settings / Configuration Architecture |
| Cross-document conflicts, reconciliation and feature-planning readiness | 0E — Foundation Architecture Reconciliation |

0E applies only after it exists and has been reviewed; do not infer phase execution or approval from a file's presence.
Features may extend approved catalogs, registries and configuration through their established extension mechanisms.
Features must not silently redefine Foundation semantics or create parallel shared infrastructure.
For an owning-contract conflict or missing Foundation decision: stop the local decision, record evidence, identify the owner and request architecture review rather than patching around it.

Explicit review is required before destructive migrations, core relationship changes, authentication/security redesign, major dependencies/frameworks, repository restructuring, plugin architecture, IPC/cross-language contracts, technology ownership/replacement or external-system ownership changes.
Describe current/proposed behavior, necessity, simpler alternatives, migration cost, risks and affected docs/tests.
Obtain required approval before action unless that exact change is already explicitly authorized.
Stop and report material authority conflicts before making a major architectural decision.

## SQLite and data integrity

Preserve normalization, keys, foreign keys, constraints, transactions and versioned migrations.
Always parameterize externally influenced SQL values; never concatenate untrusted input into SQL.
Every application connection must enable `PRAGMA foreign_keys = ON`.
Use the documented `busy_timeout` default (5000 ms) unless approved configuration changes it.
Released/applied migration history is immutable; use a new migration unless revision is explicitly permitted and provably unreleased.
Preserve `schema_migrations` authority and checksum validation; never mark failed migrations applied.
Destructive schema/data changes require explicit approval; do not disable foreign keys to force success.
Use transactions for logical units of work; do not hold them open while waiting on PowerShell, networks or AI.
Business workflows belong in services, not SQLite triggers; derived FTS indexes do not replace relational source data.
Before persistence changes, inspect [Docs/07_Database.md](Docs/07_Database.md) for strategy/procedures,
[Docs/08_ERD.md](Docs/08_ERD.md) for conceptual relationships and
[Docs/09_SQLSchema.md](Docs/09_SQLSchema.md) for the exact physical schema.
Migration, indexing, FTS, trigger and integrity-test details belong to those owners.
Do not claim database validity without applicable executed checks:
`PRAGMA integrity_check` must return `ok`; `PRAGMA foreign_key_check` must return zero violations.

## Security, secrets and employer/customer data

Use least privilege, secure defaults and explicit technician intent.
Treat user, external, AI, clipboard, file/path, URL, configuration, imported and process output as untrusted.
Validate at the owning boundary; prevent traversal and silent overwrite, and protect user files and metadata.
Never hard-code, expose, log or commit passwords, keys, tokens, cookies, recovery codes or other authentication material.
Secrets are not ordinary Settings, SQLite data, clipboard history, Case Journal, Analytics, Mochi context, docs, fixtures or logs.
Credential integrations require approved secure references/transient retrieval and a reviewed secret-management boundary.
Use synthetic data for development, documentation, examples and tests; do not require real employer/customer data.
Minimize collection, persistence and external transmission when sensitivity or employer policy is uncertain; record unknown policy as `NOT VERIFIED` rather than inventing it.
Keep unrestricted clipboard content, unnecessary API responses and sensitive AI context out of normal logs.
Use centralized application logging; keep technical logs separate from meaningful audit events.
Detailed security/privacy ownership is routed by the documentation index and Foundation guidance.

## Offline behavior and integrations

F7Hub must remain useful without internet connectivity or external API availability.
Distinguish `LOCAL_REQUIRED`, `ONLINE_OPTIONAL` and `ONLINE_REQUIRED`.
Locally required workflows must not depend on remote PSA, RMM, AI, credential managers or cloud APIs.
External integrations must not become accidental prerequisites for unrelated local functionality.
Keep integration architecture vendor-neutral until an approved provider is verified.
Preserve external systems of record unless explicitly designed otherwise.
Prefer read-only integration first; do not begin with automatic bidirectional synchronization.
Verify supported API/module, authentication, permissions, least privilege, token handling and failure behavior.
A configured provider does not establish every capability or permission; never request broad tenant access for convenience.

## AI and automation safety

AI may explain, summarize, suggest and draft; AI is not an execution authority.
AI output, including generated code and commands, remains untrusted until reviewed and validated.
No direct AI execution, arbitrary shell endpoint or GUI-to-process shortcut may bypass normal services/gateways and technician control.
Destructive administration and data deletion require authorized, controlled execution with reviewed safeguards.
F7Hub PowerShell execution follows `GUI → Service → PowerShellService → PowerShellGateway → approved operation`.
Use approved runtime, registered identity, validated arguments and structured results; availability/checksum alone is not execution permission.
Read [PowerShell/AGENTS.md](PowerShell/AGENTS.md) and [Docs/12_PowerShellArchitecture.md](Docs/12_PowerShellArchitecture.md) for execution and result contracts.
Do not use untrusted `Invoke-Expression`, command fragments or unnecessary shell indirection.
Prefer APIs, supported CLI/PowerShell and documented integrations before UI automation.
Preserve/restore temporary clipboard replacement where appropriate and respect newer intentional clipboard changes.
Persistent clipboard history must remain optional and privacy-aware.
Detailed AHK procedures belong to [Docs/11_AHKArchitecture.md](Docs/11_AHKArchitecture.md) and applicable scoped guidance.
Do not silently turn diagnostics into remediation, elevate privileges or introduce credential handling.

## Git and worktree safety

Before substantial edits or branch movement, inspect branch, HEAD, status, remotes and staged/untracked paths.
Classify and preserve all unrelated user work; prefer an isolated worktree from verified current `origin/main` when canonical is dirty.
Never reset, clean, restore, stash or force-checkout unrelated work to obtain cleanliness.
Destructive Git recovery, force push and history rewriting require specific explicit approval after impact review.
Do not stage or commit unrelated paths/hunks; use an explicit path allowlist when staging is authorized.
Commit, push, PR creation and merge require their own task authorization; review approval alone does not authorize integration.
For detailed baseline, candidate identity and integration gates use the delivery skill's [Git safety reference](.agents/skills/vertical-slice-delivery/references/git-safety.md).
Naming details belong to [Docs/15_NamingConventions.md](Docs/15_NamingConventions.md).

## Cloud and Windows-native validation

F7Hub may be validated in a Linux-based cloud or sandbox environment.
Validation evidence must identify the environment in which it was produced.
Use the existing result vocabulary `PASS`, `FAIL`, `NOT RUN` and `BLOCKED`
together with an environment qualifier such as `CLOUD_PORTABLE` or
`WINDOWS_NATIVE` (for example, Environment: `CLOUD_PORTABLE`; Result: `PASS`).

`CLOUD_PORTABLE` may establish genuinely platform-independent behavior:
portable Python logic; platform-independent SQLite schema, migrations,
constraints, repositories and queries; headless Qt behavior that does not
depend on Windows-native presentation or window management; portable
integration tests; documentation/schema/contract validation; portable Mochi
Python behavior; and static/platform-independent checks. Existing
`QT_QPA_PLATFORM=offscreen` checks provide headless evidence within this scope.

Cloud validation is not authoritative for AutoHotkey runtime behavior, Windows
global hotkeys/hotstrings, native window management, Window Spy, Windows shell,
registry, service, COM or process integration, Windows-native PowerShell
administration, Windows tray behavior, native DPI/display scaling/rendering,
Windows-specific filesystem/path/locking behavior, native Mochi desktop
interaction or other Windows desktop/session-dependent behavior.

A `CLOUD_PORTABLE` `PASS` must never be reported or summarized as a
`WINDOWS_NATIVE` `PASS`. A slice that changes or depends on Windows-native
behavior requires separate `WINDOWS_NATIVE` validation before integration
unless the applicable approved architecture or test contract explicitly
establishes that native validation is not required.

Mixed suites must classify and report portable and Windows-native portions
separately. Unsupported Windows behavior in Linux is `NOT RUN`, not `FAIL`;
a genuine platform-independent failure remains `FAIL`.

Cloud Git/network evidence is environment-specific. A GitHub operation
succeeding or failing in a cloud sandbox does not by itself establish local
Windows Git, local authentication, local repository health or Windows-native
integration state.

Do not modify production source merely to accommodate cloud-environment
limitations. Prefer environment configuration unless validation identifies a
genuine platform-independent product defect.

Never configure or expose production secrets, MSP or customer credentials,
Microsoft 365 credentials, API keys, HaloPSA, NinjaRMM or Keeper credentials,
or customer data for portable cloud validation.

## Validation, documentation and completion

Run appropriate required checks for the actual change; cover success, failure, cancellation and recovery where applicable.
Define safe failure behavior; do not suppress unexpected errors or report a completed action as cancelled.
Use isolated fixtures and protect operational data; bound native automation, retries and process cleanup.
Use `PASS`, `FAIL`, `NOT RUN` or `BLOCKED`; never claim tests passed unless they actually ran and passed.
Report exact executed checks and distinguish fresh evidence from retained/historical results and unverified areas.
Database, GUI and PowerShell test matrices belong to their canonical owners selected through the documentation index.

Canonical numbered docs are living specifications; assess impact and update only affected owners after approved, validated changes.
Do not rewrite requirements to legitimize incorrect implementation or present planned behavior as implemented/verified.
Keep current implementation status in [Docs/Status/CURRENT_STATE.md](Docs/Status/CURRENT_STATE.md), supported by repository/test evidence.
Keep history in [Docs/18_ChangeLog.md](Docs/18_ChangeLog.md), Git, review/integration records or archived planning artifacts.
Preserve historical meaning; do not rewrite it as though later decisions always existed.
Prefer one authoritative detailed owner plus short root safety reminders; do not create competing full policy copies.

Before completion, verify requested scope, architecture, security, data integrity, required validation, documentation synchronization, unrelated-work preservation and remaining risks.
Report changed files, evidence/results, architecture/security impacts, risks, documentation and next required gate.
Disclose incomplete work and blockers; completion/readiness never grants additional approval or integration authority.
