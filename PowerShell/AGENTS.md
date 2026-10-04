# F7Hub PowerShell Agent Instructions

These instructions apply to all work under `PowerShell/`, including inspecting,
planning, implementing, testing, reviewing and documenting scripts.

Root [AGENTS.md](../AGENTS.md), [ROOT.md](../ROOT.md), explicit user requirements
and approved architectural decisions remain authoritative. More specific nested
guidance may add stricter requirements within those boundaries.

## Authority and ownership

PowerShell owns Windows and Microsoft administration, diagnostics, approved
automation, data collection and reporting. Python/PySide6 application services
own application orchestration, execution authorization and cross-runtime
coordination. PowerShell does not own the primary GUI or core SQLite persistence.

Use [the documentation index](../Docs/19_DocumentationIndex.md) to select the
minimum relevant canonical documents. The execution and result contract belongs
to [PowerShell architecture](../Docs/12_PowerShellArchitecture.md); cross-language
ownership also belongs to [system architecture](../Docs/06_SystemArchitecture.md)
and [Python architecture](../Docs/13_PythonArchitecture.md).

Prefer predictable, structured, testable operations. Before creating helpers,
modules, result types, artifact/configuration mechanisms or execution conventions:

```text
SEARCH → IDENTIFY → REUSE/EXTEND → CREATE ONLY IF NECESSARY
```

## Legacy code and transition

Existing PowerShell code may predate this scoped guidance. Integrating this
file does not retroactively authorize or require unrelated changes to every
existing script. An existing script that does not yet meet a new rule may
remain unchanged until a dedicated compliance slice intentionally brings it
into scope, or a focused feature slice already materially changes that script
and compliance of the affected code is safe, relevant and within approved scope.

New production PowerShell scripts created after this guidance is integrated
MUST comply with the applicable guidance from creation unless an explicitly
reviewed exception exists. The strict-mode requirement below remains mandatory
for new production scripts; this transition rule is not a general exemption.

Do not expand a focused slice solely to clean up unrelated legacy PowerShell
files. If compliance changes registered source bytes, explicitly scope and
review all applicable downstream changes: source-byte hashes, execution-policy
digests, registry metadata, forward-only migrations, tests, documentation and
independent review evidence. Do not make these changes as incidental cleanup.
Record existing noncompliance found during unrelated work as follow-up work.
Root scope-control rules remain authoritative.

## Runtime and operation identity

Production operations MUST target the runtime approved by the current execution
architecture. Controlled diagnostic execution currently uses PowerShell 7.
Do not silently depend on Windows PowerShell 5.1-only behavior or introduce a
second runtime path inside a feature. A different version or host requires
architectural review before implementation.

Scripts MUST NOT depend on interactive profiles, profile-loaded modules,
interactive prompts, the current working directory or manually configured
environment state. Use `$PSScriptRoot` or approved F7Hub path infrastructure for
script-relative resources. The working directory is not necessarily the script
directory. For sealed execution, `$PSScriptRoot` identifies the private executing
copy; sibling source resources require an explicitly approved delivery contract.

A `.ps1` file on disk is not execution permission. Production operations MUST
participate in the approved registration and execution-identity model. Where
applicable, verify operation/script identity, enabled state, type, runtime, risk,
privilege, approved source location, manifest or literal policy membership,
version, digest and current file identity at the owning service/gateway boundary.
Availability, registration and an approved copy checksum alone do not authorize
execution. Do not bypass these checks or create alternate paths for unregistered
scripts. Higher-level features SHOULD use stable operation identifiers where
provided; filenames remain implementation details.

Changing registered source bytes, including comments or line endings, changes
integrity identity. Review affected execution-policy digests and registration
metadata together through the approved update procedure; never silently edit an
applied migration or weaken verification to accept the change.

## Execution boundary and diagnostic composition

Production execution initiated by F7Hub MUST pass through the approved
application service/gateway architecture. Preserve exact-byte verification,
sealed private execution, approved non-elevated runtime, bounded output/deadline,
owned-process containment and verified cleanup. Do not add direct GUI launches,
arbitrary commands/scripts, terminals, free-form execution or AI-triggered runs.

Individual scripts implement independently testable operations. They MUST NOT
launch sibling F7Hub scripts to construct workflows or packs. Composition and
cross-runtime orchestration belong to application services:

```text
Application service → validate approved operation/pack
                    → execute operation → collect structured result
                    → execute next approved operation → combine results
```

A diagnostic pack is an application-level composition of approved identities,
not a giant script, dynamic discovery of sibling scripts, arbitrary filesystem
paths or free-form shell commands. Validation, ordering, execution, cancellation,
aggregation and result composition belong to the application/service layer.
Do not invent pack infrastructure while changing an individual diagnostic.
Any orchestration exception requires explicit architectural review.

## Script structure, parameters and helper functions

Production scripts SHOULD have comment-based help/metadata, explicit parameters
where applicable, strict/error configuration, small private helpers when useful,
main collection, structured-result construction and explicit completion. Use
top-level `try/catch/finally` where appropriate; `finally` is required when owned
resources need cleanup after failure.

Prefer the following declaration, retaining parameterless contracts where
required:

```powershell
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
```

Production scripts MUST establish `Set-StrictMode -Version Latest`. Limit
preference changes to the current script/process scope; do not change global or
machine-level preferences or unrelated session state. Use terminating errors
where failure must interrupt an operation.

Parameters MUST be explicit, typed where useful and validated near the boundary.
Use `ValidateSet`, `ValidateRange`, `ValidatePattern`, `ValidateNotNull` and
`ValidateNotNullOrEmpty` when they improve safety. Use `ValidateScript` only when
its behavior is clear and safe. Normalize and validate paths, identifiers,
hostnames, addresses, URLs and other external input before use. Do not accept
command fragments or executable expressions, dynamically construct executable
code from input, or add generic registry parameter execution without explicit
architectural approval. These conventions do not authorize adding parameters to
currently parameterless diagnostics or extending the execution interface.

Function output is pipeline output: unassigned expressions and command results
can enter a function's return value. Explicitly capture, suppress or return each
result according to intent. Do not assume only `return` produces output. Helpers
SHOULD return one defined object or collection appropriate to their contract.

Use full cmdlet names, approved Verb-Noun function naming and named parameters
where they improve clarity/safety. Avoid aliases such as `%`, `?`, `ls`, `cat`,
`gc`, `select` and `sort`, unnecessary globals, hidden mutable state and deeply
nested control flow. Comments should explain intent, constraints, security
boundaries or unusual behavior. Prefer maintainability over concise syntax.

## Machine results, streams and errors

Scripts invoked by F7Hub MUST preserve the approved structured-result contract.
JSON is the preferred application serialization unless that contract specifies
otherwise. Do not invent a result schema or script-specific exit-code semantics.

When stdout carries the machine result, it MUST contain only that result. Capture
or suppress incidental output, for example `$null = New-Item ...` or
`$value = Get-Something ...`. Do not use `Write-Host`, `Write-Output`,
`Format-Table` or `Format-List` for the primary machine result. Do not emit banners,
progress narration, decorative separators or debug text into that stream.
Verbose, warning, information, debug and error streams MUST follow the approved
gateway/result contract; being outside the intended stdout stream is not proof
that output is safe. An operation SHOULD produce one deterministic, schema-valid
machine result unless its established contract explicitly defines otherwise.

Keep structured objects intact through collection, transformation and validation,
then construct the result and optionally export approved artifacts. Formatting
cmdlets are presentation-only; never use display-formatted output as machine input.
Machine timestamps SHOULD use ISO 8601 and UTC unless a requirement specifies
local time. Use deterministic or approved run identifiers as appropriate.

Distinguish valid diagnostic results, diagnostic-reported problems, script
failures, execution/infrastructure failures, timeout and malformed output.
A valid diagnostic `ERROR` with its approved exit code is a collection outcome;
do not fabricate a diagnostic result for an execution-boundary failure.

Catch errors only to add meaningful context, translate them into the approved
result, clean up deterministically or recover safely. Do not suppress unexpected
errors or catch exceptions merely to ignore them. Preserve useful information
without exposing secrets or raw provider exception details. Intentional mapping
to a fixed safe `ERROR` result or documented unavailable value is error handling,
not permission to silently report success.

Retries MUST be bounded, deterministic, observable, appropriately delayed and
tested, and limited to plausibly transient failures. Never retry validation,
permission, malformed-input or deterministic script defects; never retry forever.

## Dependencies and native commands

Required modules, executables, APIs and Windows components MUST be documented,
detectable, validated before use and handled safely when absent. Validation may
belong to the approved gateway or script boundary as the contract specifies.
Do not assume developer-machine dependencies exist on production machines.

Diagnostics MUST NOT silently install dependencies. Do not execute
`Install-Module`, `Install-Package`, `winget install`, `choco install`, provider
installation or repository trust changes unless explicitly required and approved
by the focused feature.

For native executables, intentionally resolve the approved executable, pass
structured arguments, validate user-derived arguments, capture meaningful exit
codes and required stdout/stderr, enforce bounded execution, handle missing
executables and treat returned content as untrusted. Translate meaningful native
exit codes into the approved result contract. Successful launch alone does not
mean success. Do not invoke `cmd.exe` to compose command strings or add shell
indirection where direct invocation suffices.

## Filesystem, artifacts, concurrency and logging

Runtime artifacts MUST NOT be written into tracked source directories. Use
approved F7Hub runtime storage, creating required directories safely when the
feature permits. Use `Join-Path` and literal paths rather than unsafe path-string
concatenation; use `-LiteralPath` where applicable. Validate paths before reads,
writes, moves, copies or deletion. Do not overwrite user data without explicit
authorization or recursively delete broad parent directories.

Scripts MUST NOT assume exclusive execution. Use approved run identifiers or
isolated run directories where concurrency could collide; avoid fixed names such
as `temp.csv`, `result.json` or `output.txt`. Every temporary resource SHOULD have
an identifiable owner and MUST have a retention/cleanup policy. Cleanup MUST
affect only current-operation resources. Do not delete another run's files or
terminate processes by name. Child-process ownership and termination must be
deterministic under the approved execution architecture.

CSV is an optional artifact, not the default application IPC format. When
approved, export structured objects with `Export-Csv -NoTypeInformation
-Encoding utf8` unless an established artifact contract requires another encoding.
Preserve established columns and schemas; identify schema/version when long-term
consumption needs stable interpretation. Do not use CSV as intermediate IPC when
the approved structured-result contract is available.

Keep machine results, artifacts, logging and human presentation separate. Scripts
SHOULD return structured diagnostics for application logging rather than invent
log-file locations. Script-owned log artifacts require explicit feature scope;
never write logs into the source tree. Logs MUST NOT contain secrets or
unnecessary personal data.

## Security, diagnostics and Microsoft administration

Treat parameters, clipboard data, paths, filenames, URLs, native output, JSON,
CSV, API responses and AI-generated content as untrusted. Never embed or expose
passwords, keys, tokens, private keys or tenant secrets. Do not use
`Invoke-Expression` for dynamic execution, bypass execution policy, disable
security controls or self-elevate. Elevation must be explicitly governed by
approved architecture. Use least privilege.

Diagnostics SHOULD be read-only. They MUST NOT quietly become remediation.
Changes to system/network configuration, registry, services, files outside
approved runtime storage, Microsoft 365/Entra/Intune configuration, permissions,
accounts or security controls require mutating/remediation classification,
explicit feature scope and security review. Future mutating operations SHOULD
provide applicable technician confirmation, precondition checks, least privilege,
precise change records, post-change validation and recovery/rollback. Do not add
these capabilities preemptively to read-only diagnostics.

Microsoft 365, Entra ID, Exchange Online, Intune, Graph, Azure and related work
MUST use approved authentication and permission boundaries. Authentication belongs
to F7Hub integration architecture. Scripts MUST NOT embed credentials, persist
tokens independently, request excessive scopes, silently authenticate interactively,
create secret stores or weaken tenant security. Keep read-only diagnostics
distinguishable from mutating administration.

## Validation, documentation and completion

Design scripts for deterministic automated testing. Test applicable success,
expected negative diagnostic results, invalid parameters, missing dependencies,
access denied, malformed external data, timeout, cleanup and structured output.
Use isolated fixtures; test application execution through its approved boundary.
Do not claim `PASS` without execution. Report `PASS`, `FAIL`, `NOT RUN` or `BLOCKED`
and distinguish current evidence from retained evidence.

Changes to execution behavior require review of PowerShell architecture; changes
across runtimes also require system/Python architecture review. Feature changes
may affect Features, User Workflows, Roadmap, Todo and ChangeLog documents selected
through the documentation index. Only document verified behavior as verified;
clearly label planned or unverified capabilities. Update only affected owners.

Keep focused work within its approved slice. Record unrelated improvements as
follow-ups. Require explicit architectural review before changing execution or
result contracts, process boundaries, authentication, credentials, elevation,
remote administration, generic execution or destructive administration.

Before completion, verify approved behavior, preserved output contracts,
security, applicable cleanup, executed required tests, synchronized documentation
and absence of unrelated changes. Root Git safety and delivery-skill lifecycle,
candidate identity, independent review and integration gates still apply.
