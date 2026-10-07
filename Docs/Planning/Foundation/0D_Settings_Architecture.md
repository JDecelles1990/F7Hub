# F7Hub Phase 0D

## Cross-Subsystem Planning Note

Define which DynamicHub preferences are settings versus runtime state; global/user/workflow settings; safe defaults; future AI/automation feature flags

# Settings & Configuration Architecture Planning Instructions
Existing config sources; Settings ownership; SQLite vs config file vs environment vs runtime decision matrix; SettingsService boundary; setting definitions vs values; type system; validation; defaults; precedence; effective-value semantics; module setting namespaces; runtime change propagation; restart-required behavior; privacy/security settings; secrets boundary; AHK configuration flow; PowerShell parameters; audit requirements; migration/evolution of setting keys.

I want a table such as:
Concept                         Classification
-------------------------------------------------------------
Clipboard retention days       SETTING
Mochi sidebar visible           SETTING
Diagnostic timeout             SETTING

Tag catalog                     NOT A SETTING
Entity types                    NOT A SETTING
Diagnostic registry            NOT A SETTING
PowerShell script registry      NOT A SETTING
JSON schema                     NOT A SETTING
Ticket status semantics         NOT A SETTING
Security invariant              NOT A SETTING


## Mode

`@ARCHITECT @PLAN`

Architecture and planning only.

Do not implement production code.

Do not create SQLite migrations.

Do not create configuration files.

Do not build the Settings GUI.

Do not modify existing settings or defaults.

Do not refactor unrelated components.

---

# 1. Objective

Design the global F7Hub Settings and Configuration Architecture.

The objective is to establish:

- settings ownership
- persistence strategy
- setting scopes
- default values
- validation
- sensitive-setting handling
- module registration
- change propagation
- audit expectations
- configuration precedence
- user-facing Settings organization

The architecture must support future F7Hub modules without allowing each module to invent its own configuration system.

---

# 2. Relationship to Foundation Phases

Phase 0D depends on:

```text
Phase 0A
Master Foundation Architecture

Phase 0B
Global JSON / Interoperability Contract

Phase 0C
Classification / Taxonomy Architecture
```

Before planning Settings:

1. Read approved Phase 0A.
2. Read approved Phase 0B.
3. Read approved Phase 0C.
4. Inspect existing F7Hub configuration files.
5. Inspect existing SQLite settings/configuration tables.
6. Inspect Python configuration loading.
7. Inspect AHK configuration.
8. Inspect PowerShell configuration.
9. Inspect GUI preferences.
10. Inspect application startup/bootstrap configuration.

Do not assume F7Hub currently has no Settings architecture.

---

# 3. Primary Principle

Settings configure behavior.

Settings must not define business semantics.

For example:

```text
Clipboard retention days = 7
```

is a Setting.

But:

```text
What is an Entity?
```

is architecture/taxonomy.

Similarly:

```text
Diagnostic timeout = 30 seconds
```

is a Setting.

But:

```text
What does diagnostic failure mean?
```

belongs to the diagnostic contract/domain.

---

# 4. Settings Must Not Become Business Logic

Avoid:

```text
if setting_x:
    ticket means something different
```

or:

```text
user-configurable entity semantics
```

unless explicitly designed.

Settings should influence:

```text
behavior
limits
preferences
feature presentation
retention
timeouts
UI options
optional automation
```

not redefine core domain meaning.

---

# 5. Required Architecture Layers

Evaluate a layered model:

```text
Settings GUI
     ↓
SettingsService
     ↓
SettingsRepository / Config Provider
     ↓
SQLite / Config Files / Environment
```

Modules should normally request settings through:

```text
SettingsService
```

rather than reading SQLite or config files directly.

---

# 6. Configuration Sources

Inspect and classify all current sources.

Potential sources:

```text
SQLite
JSON
YAML
INI
environment variables
command-line arguments
hard-coded defaults
Windows registry
runtime state
```

For each current source identify:

```text
purpose
owner
writer
reader
lifecycle
security sensitivity
```

---

# 7. Configuration Precedence

Define a consistent precedence model.

Possible example:

```text
Built-in Defaults
       ↓
Application Config
       ↓
Persisted User Settings
       ↓
Environment Overrides
       ↓
Command-Line Override
       ↓
Temporary Runtime Override
```

Do not adopt this exact order automatically.

Inspect existing conventions first.

The plan must define one clear precedence model.

---

# 8. Setting Categories

Every Setting should belong to a category such as:

```text
SYSTEM
USER_PREFERENCE
FEATURE
SECURITY
PRIVACY
PERFORMANCE
INTEGRATION
RUNTIME
```

These categories should influence:

```text
storage
editability
validation
visibility
restart requirements
auditability
```

---

# 9. Setting Scopes

Evaluate support for scopes such as:

```text
APPLICATION
USER
MODULE
SESSION
DEVICE
```

Potential future example:

```text
APPLICATION:
default diagnostic timeout

USER:
preferred theme

MODULE:
clipboard retention

SESSION:
temporary debug option
```

Avoid supporting scopes without a real use case.

---

# 10. Global vs Module Settings

Global settings:

```text
appearance
language
privacy
logging
general behavior
```

Module settings:

```text
Clipboard
Diagnostics
Tags
Analytics
Mochi
Automation
PowerShell
```

Architecture should allow modules to register settings without each module inventing a persistence mechanism.

---

# 11. Proposed Settings Navigation

Plan a future GUI structure such as:

```text
Settings
│
├── General
├── Appearance
├── Clipboard
├── Tags & Taxonomy
├── Diagnostics
├── Automation
├── PowerShell
├── Statistical Analytics
├── Mochi
├── Privacy & Security
└── Advanced
```

Do not finalize labels without checking existing GUI conventions.

---

# 12. Settings Descriptor Model

Evaluate whether every setting should have structured metadata.

Conceptually:

```text
setting_key
module_key
display_name
description
data_type
default_value
validation_rule
scope
is_sensitive
requires_restart
is_user_editable
```

Example:

```text
setting_key:
clipboard.retention_days

type:
integer

default:
7

minimum:
1

maximum:
90
```

---

# 13. Stable Setting Keys

Use stable machine keys.

Recommended style:

```text
module.setting_name
```

Examples:

```text
clipboard.retention_days
clipboard.auto_capture_enabled

diagnostics.default_timeout_seconds

mochi.speech_enabled

analytics.default_period_days
```

Do not use display labels as identifiers.

---

# 14. Setting Data Types

Evaluate support for:

```text
boolean
integer
float
string
enum
path
duration
list
JSON object
```

Avoid arbitrary JSON where a strongly typed setting would be clearer.

---

# 15. Typed Validation

Every setting should have validated semantics.

Examples:

```text
clipboard.retention_days

integer
minimum = 1
maximum = 365
```

```text
diagnostics.timeout_seconds

integer
minimum = 1
maximum = 300
```

```text
mochi.speech_enabled

boolean
```

Invalid configuration must fail safely.

---

# 16. Defaults

Every user-editable setting should have a documented default.

Defaults should live in one authoritative place.

Avoid:

```text
GUI default = 7
service default = 30
database default = 14
```

for the same setting.

Determine which layer owns defaults.

---

# 17. Default Strategy

Evaluate options:

```text
code-defined defaults
database seed defaults
config-file defaults
hybrid
```

Recommendation must minimize duplication.

The GUI should not independently define behavioral defaults.

---

# 18. SQLite vs Config Files

This is a major Phase 0D decision.

Evaluate which settings belong in SQLite.

Good SQLite candidates:

```text
user-editable persistent preferences
module options
retention policies
feature toggles
UI state that should persist
```

Potential config-file candidates:

```text
application startup configuration
installation-specific paths
developer/runtime configuration
bootstrap configuration
```

Potential environment-variable candidates:

```text
secrets
deployment overrides
development/testing values
```

Do not store a setting in SQLite simply because SQLite exists.

---

# 19. SQLite Settings Table

Do not design final SQL yet.

Evaluate a conceptual structure such as:

```text
settings
────────
setting_key
value
value_type
scope
updated_at
```

or a richer model.

Compare with any existing F7Hub settings structures.

Mark:

```text
REUSE
EXTEND
NEW
NOT NEEDED
NOT VERIFIED
```

---

# 20. Settings Metadata vs Values

Consider separating:

```text
setting definitions
```

from:

```text
setting values
```

Example:

```text
Setting Definition:
clipboard.retention_days
type=integer
default=7
min=1
max=90

Setting Value:
30
```

Definitions may belong in source code/schema.

User values may belong in SQLite.

Evaluate this model.

---

# 21. Configuration Schema

Consider whether F7Hub should maintain a programmatic Settings schema.

Potential responsibilities:

```text
data type
default
validation
scope
description
sensitivity
restart behavior
```

This could be used by:

```text
Settings GUI
validation
documentation
tests
```

Avoid duplicating definitions across layers.

---

# 22. SettingsService

Conceptually evaluate:

```text
SettingsService
│
├── get()
├── get_bool()
├── get_int()
├── set()
├── reset()
├── list_module_settings()
├── validate()
└── subscribe_to_change()
```

Exact API should follow current F7Hub conventions.

---

# 23. SettingsRepository

Repository responsibilities may include:

```text
load persisted values
write persisted values
delete override
transactional updates
```

Repository should not decide business behavior.

---

# 24. Effective Value

The architecture should distinguish:

```text
default value
persisted override
effective value
```

Example:

```text
Default:
7 days

Stored override:
30 days

Effective:
30 days
```

Resetting should remove or restore the override cleanly.

---

# 25. Reset Behavior

Plan:

```text
Reset Setting
Reset Section
Reset All User Preferences
```

Be careful with:

```text
security
privacy
integration
```

settings.

Reset must not silently destroy unrelated data.

---

# 26. Change Propagation

Determine how modules learn that Settings changed.

Possible mechanisms:

```text
direct service notification
Qt signals
application event
reload-on-read
```

Avoid a global event bus unless justified.

Example:

```text
User changes:
clipboard.retention_days

SettingsService
       ↓
ClipboardService receives update
```

---

# 27. Immediate vs Restart-Required Settings

Classify settings.

Examples:

```text
Immediate:
theme
clipboard retention
Mochi speech

Potential restart:
startup integration
low-level IPC mode
certain runtime infrastructure
```

GUI should be able to show:

```text
Requires restart
```

when applicable.

---

# 28. Transactional Settings Updates

Some groups may need atomic changes.

Example:

```text
Clipboard privacy policy:
auto_capture
secret_detection
retention
```

If saving a settings section, evaluate whether changes should commit together.

Do not leave half-saved configurations after failure.

---

# 29. Security-Sensitive Settings

Identify settings that affect security boundaries.

Examples:

```text
PowerShell execution permissions
automation enablement
IPC listener behavior
AI/cloud integration
secret handling
logging verbosity
```

These should receive stricter treatment.

Potential requirements:

```text
explicit confirmation
audit trail
restricted UI
safe defaults
```

---

# 30. Secrets Are Not Normal Settings

Do not store:

```text
API keys
tokens
passwords
private keys
```

as ordinary SQLite settings.

Phase 0D must define the boundary between:

```text
configuration
```

and:

```text
secret storage
```

If secret management is required later, plan an appropriate secure mechanism.

Do not invent one without inspection.

---

# 31. Privacy Settings

Potential global privacy section:

```text
Clipboard capture enabled
Clipboard persistence enabled
Sensitive content blocking
Mochi context access
Analytics aggregation
Future AI data sharing
```

Privacy defaults should be conservative.

---

# 32. Clipboard Settings

Identify future Clipboard settings.

Potential:

```text
clipboard.capture_enabled
clipboard.manual_capture_hotkey
clipboard.auto_capture_enabled
clipboard.retention_days
clipboard.max_inline_size_kb
clipboard.url_auto_collect
clipboard.secret_detection_enabled
clipboard.deduplication_enabled
clipboard.fts_enabled
```

Do not finalize exact keys until Clipboard architecture is approved.

Phase 0D should define where such settings live.

---

# 33. Tag & Taxonomy Settings

Potential:

```text
tags.auto_assign_rules
tags.show_suggestions
tags.ai_suggestions_enabled
tags.user_tags_enabled
tags.max_suggestions
```

Core taxonomy semantics must not be configurable.

For example:

```text
ipv4 means something different
```

must not be a setting.

---

# 34. Diagnostic Settings

Potential:

```text
diagnostics.default_timeout_seconds
diagnostics.confirm_before_run
diagnostics.history_retention_days
diagnostics.save_evidence_by_default
diagnostics.read_only_default
```

Avoid settings that bypass security boundaries.

Example:

Bad:

```text
allow_arbitrary_powershell = true
```

if architecture prohibits arbitrary execution.

Settings cannot override foundational safety rules.

---

# 35. PowerShell Settings

Potential:

```text
powershell.preferred_runtime
powershell.execution_timeout
powershell.show_raw_output
```

Script authorization remains governed by the approved registry/security model.

---

# 36. Analytics Settings

Potential:

```text
analytics.default_period_days
analytics.aggregate_daily
analytics.raw_event_retention_days
analytics.show_personal_identifiers
```

Privacy-sensitive options need careful review.

Analytics should not create separate behavior that contradicts operational retention rules.

---

# 37. Mochi Settings

Potential:

```text
mochi.enabled
mochi.sidebar_visible
mochi.speech_enabled
mochi.voice
mochi.auto_suggest
mochi.notification_level
mochi.context_clipboard_enabled
mochi.context_diagnostics_enabled
mochi.context_analytics_enabled
```

Context access should be explicit.

---

# 38. AHK Settings

Potential areas:

```text
hotkeys
HUD enabled
HUD timeout
manual capture shortcut
launcher shortcuts
```

Determine whether AHK reads configuration directly or receives validated configuration from Python.

Preferred boundary should avoid multiple independent sources of truth.

---

# 39. Cross-Language Settings Delivery

If AHK or PowerShell requires settings, evaluate:

```text
Python sends effective settings through contract
```

versus:

```text
AHK reads a shared config file
```

or:

```text
PowerShell receives explicit parameters
```

Prefer explicit dependency injection over hidden configuration access where practical.

---

# 40. PowerShell Should Receive Parameters

For most diagnostics:

```text
Python
 ↓
validated parameters
 ↓
PowerShell
```

is preferable to PowerShell reading global F7Hub Settings itself.

This keeps PowerShell scripts portable and easier to test.

---

# 41. AHK Configuration Boundary

AHK may reasonably require some startup configuration.

Examples:

```text
hotkeys
IPC endpoint
HUD options
```

But AHK should not independently maintain business settings such as:

```text
clipboard retention
taxonomy behavior
diagnostic rules
```

---

# 42. Module Registration

Evaluate whether modules should register their setting definitions.

Conceptually:

```text
Clipboard module
→ registers clipboard.* definitions

Diagnostics
→ diagnostics.*

Mochi
→ mochi.*
```

This could allow the Settings GUI to be generated or partially driven by metadata.

Do not over-engineer plugin-style registration if a static modular registry is simpler.

---

# 43. Settings GUI Architecture

The GUI should not contain validation rules directly.

Conceptually:

```text
Settings Page
    ↓
ViewModel / Presentation Logic
    ↓
SettingsService
```

The service owns validation.

---

# 44. PySide6 Settings Layout

Potential layout:

```text
┌─────────────────────────────────────────────────┐
│ Settings                               Search   │
├────────────────┬────────────────────────────────┤
│ General        │ Clipboard                      │
│ Appearance     │                                │
│ Clipboard      │ Capture                        │
│ Tags           │ [✓] Enable clipboard feature  │
│ Diagnostics    │                                │
│ PowerShell     │ Retention                      │
│ Analytics      │ [ 7 ] days                    │
│ Mochi          │                                │
│ Privacy        │ Sensitive Data                 │
│ Advanced       │ [✓] Detect possible secrets   │
│                │                                │
│                │         [Reset] [Apply]        │
└────────────────┴────────────────────────────────┘
```

---

# 45. Searchable Settings

Consider a search field.

Example:

```text
Search:
retention
```

results:

```text
Clipboard → Retention
Diagnostics → History Retention
Analytics → Event Retention
```

Stable metadata enables this.

---

# 46. Validation Feedback

Invalid values should produce clear GUI feedback.

Example:

```text
Retention must be between 1 and 365 days.
```

Do not allow invalid data to reach persistence first.

---

# 47. Apply / Save Model

Evaluate:

```text
Save immediately per control
```

versus:

```text
Apply button per section
```

or a hybrid.

Consider:

```text
atomicity
user expectations
Qt conventions
error recovery
```

Recommend one consistent model.

---

# 48. Draft Settings State

If using Apply/Cancel:

```text
Persisted Settings
      ↓
Editable Draft
      ↓
Validate
      ↓
Apply
```

Failure should preserve the user's draft where practical.

---

# 49. Settings Concurrency

Even a desktop app may eventually have:

```text
main PySide6 app
AHK companion
background Python process
```

Determine whether concurrent settings changes are possible.

If so, plan:

```text
versioning
updated_at
conflict handling
```

without over-engineering.

---

# 50. Settings Audit

Not every preference needs audit history.

Changing:

```text
theme = dark
```

probably does not.

Changing:

```text
automation permissions
PowerShell safety policy
AI data-sharing policy
```

may deserve auditability.

Classify settings accordingly.

---

# 51. User Preferences vs Policy

Distinguish:

```text
Preference
```

from:

```text
Policy
```

Preference:

```text
Mochi sidebar visible
```

Policy:

```text
Secret-like Clipboard content cannot be auto-persisted
```

Policies may be non-editable or tightly constrained.

Settings must not weaken architectural safety invariants.

---

# 52. Hard Safety Invariants

Examples that likely should not become ordinary settings:

```text
AHK may directly write SQLite
Mochi may execute arbitrary commands
PowerShell may bypass approved registry
SQL may use unparameterized queries
```

Those are architecture/security rules.

Not preferences.

---

# 53. Feature Flags

Evaluate whether F7Hub needs internal feature flags.

Examples:

```text
clipboard_enabled
mochi_sidebar_enabled
analytics_enabled
```

Distinguish:

```text
user feature preference
```

from:

```text
development feature flag
```

Do not mix them in the same UI necessarily.

---

# 54. Advanced / Developer Settings

Potential developer settings:

```text
verbose logging
contract debug view
diagnostic tracing
test data
```

These should be isolated from ordinary user preferences.

Production defaults should remain safe.

---

# 55. Environment Configuration

Identify startup/environment values that should not live in user settings.

Examples may include:

```text
database location
application data directory
logging directory
development mode
```

Verify against current architecture.

---

# 56. Paths

Path settings require:

```text
normalization
existence validation where appropriate
access validation
Windows path handling
```

Do not silently create arbitrary directories from untrusted configuration.

---

# 57. Hotkey Settings

Future Settings may configure AHK shortcuts.

Plan conflict handling:

```text
duplicate hotkey
reserved shortcut
Windows shortcut collision
application shortcut collision
```

Example:

```text
Ctrl+Shift+C
```

may conflict with Windows/File Explorer behavior.

The Settings architecture should support validation before activation.

---

# 58. Hotkey Registry

Evaluate whether hotkeys deserve a structured registry rather than arbitrary strings.

Potential metadata:

```text
action_key
default_shortcut
current_shortcut
scope
owner
is_global
```

Detailed hotkey architecture can be deferred.

---

# 59. Retention Settings

Several modules may use retention.

Examples:

```text
clipboard
diagnostics
logs
analytics events
Mochi conversations
```

Do not create one generic global retention value unless semantics truly match.

Use explicit keys.

---

# 60. Retention Policy Ownership

Settings defines:

```text
configured duration
```

Domain service defines:

```text
what may actually be deleted
```

Example:

```text
clipboard.retention_days = 7
```

does not mean:

```text
delete ticket-linked evidence after 7 days
```

Domain retention rules remain authoritative.

---

# 61. Reset vs Data Deletion

Resetting settings must not automatically delete operational data.

Example:

```text
Reset Clipboard retention to 7 days
```

should not immediately purge data unless explicitly designed.

Configuration mutation and data cleanup are separate operations.

---

# 62. Settings Migration

Settings definitions will evolve.

Plan handling of:

```text
renamed setting keys
removed settings
changed defaults
changed enum values
```

Avoid leaving stale orphaned configuration forever.

---

# 63. Setting Key Renames

Machine keys should be stable.

If rename is unavoidable:

```text
old_key
→ migration
→ new_key
```

Do not silently treat them as unrelated settings.

---

# 64. Removed Settings

When a feature disappears:

```text
deprecated
```

then:

```text
removed
```

with migration/cleanup strategy.

Do not reuse the old key for unrelated meaning later.

---

# 65. Settings Versioning

Evaluate whether:

```text
settings schema version
```

is needed independently from database migration version.

Do not add versioning layers without a concrete need.

---

# 66. Settings Export / Import

Consider future capability:

```text
Export Preferences
Import Preferences
```

Potential benefits:

```text
backup
migration
lab systems
```

Potential risks:

```text
secrets
machine-specific paths
unsafe policies
```

Likely defer.

---

# 67. Settings and Statistical Analytics

Analytics may inspect operational configuration for explanation.

Example:

```text
Clipboard history dropped
because retention changed from 30 to 7 days.
```

But Analytics should not treat every preference change as a metric automatically.

---

# 68. Settings and Mochi

Mochi may read safe assistant preferences:

```text
speech enabled
sidebar enabled
context sources
```

Mochi should not receive:

```text
secret values
security tokens
internal authentication credentials
```

---

# 69. Settings and Tags

Tag Management belongs in Settings UI.

But:

```text
Tags
```

are domain data/taxonomy.

They are not ordinary key/value Settings.

Important distinction:

```text
Settings → Tags & Taxonomy
```

is a GUI/navigation location.

It does not mean Tags are stored in the Settings table.

---

# 70. Settings and Categories

Same principle.

Category management may appear under Settings.

Categories remain taxonomy/domain records.

Do not serialize them as:

```text
settings.category_1 = ...
```

---

# 71. Settings and Diagnostics

Settings may determine:

```text
timeout
history retention
confirm-before-run
```

but the Diagnostic Engine defines:

```text
what diagnostic exists
what findings mean
what scripts are approved
```

---

# 72. Settings and JSON Contracts

Settings may influence operational behavior.

But the JSON schema must remain stable.

Bad:

```text
user setting changes contract field names
```

Good:

```text
setting changes timeout value used by service
```

---

# 73. Configuration Snapshot

Consider whether long-running operations should capture relevant effective settings at start.

Example:

```text
Diagnostic Session
started with timeout = 30 seconds
```

If setting changes to 60 seconds mid-run, the running execution probably keeps the original value.

This may be useful for reproducibility.

---

# 74. Settings Dependency Direction

Preferred:

```text
Feature Service
     ↓
SettingsService
```

Avoid:

```text
SettingsService
     ↓
ClipboardService
     ↓
SettingsService
```

Settings should not depend on feature business logic.

---

# 75. Circular Dependency Prevention

Explicitly review:

```text
Settings
Tags
Clipboard
Diagnostics
Mochi
```

for circular service dependencies.

Settings should remain infrastructure/shared application support.

---

# 76. Settings Test Categories

Plan future tests for:

```text
default resolution
stored override
invalid value
range validation
enum validation
reset
section apply
persistence failure
transaction rollback
unknown setting
deprecated setting
sensitive setting
restart-required setting
concurrent update
```

---

# 77. GUI Tests

Future GUI tests should cover:

```text
section navigation
load current values
dirty-state detection
validation message
apply
cancel
reset
restart indicator
search
disabled policy control
```

---

# 78. Cross-Language Tests

Future tests may verify:

```text
Python setting
→ AHK receives effective hotkey configuration
```

or:

```text
Python timeout setting
→ PowerShell execution receives expected parameter
```

without AHK/PowerShell reading the DB themselves.

---

# 79. Database Tests

If SQLite is used for settings:

```text
foreign-key behavior where relevant
unique setting keys
transactionality
data type/value validation strategy
migration behavior
```

---

# 80. Security Tests

Future tests should cover attempts to:

```text
insert invalid settings
disable hard safety policy
inject command content through settings
use unsafe paths
store secrets in ordinary settings
```

---

# 81. Performance

Settings volume is likely small.

Do not prematurely optimize.

However:

```text
get setting
```

may be called frequently.

Evaluate caching.

Potential:

```text
load effective settings
→ memory cache
→ invalidate on change
```

Avoid repeated SQL queries for every UI repaint.

---

# 82. Cache Ownership

If caching is used:

```text
SettingsService
```

should own it.

Individual modules should not maintain inconsistent copies.

---

# 83. Startup Behavior

Plan:

```text
Application starts
    ↓
Load defaults
    ↓
Load persisted settings
    ↓
Validate
    ↓
Calculate effective settings
    ↓
Start modules
```

Invalid stored values should not make F7Hub unusable.

Fallback behavior must be defined.

---

# 84. Invalid Persisted Value

Potential policy:

```text
log warning
ignore invalid override
use safe default
surface issue in Settings
```

Do not crash the entire app for a cosmetic preference.

Security-sensitive invalid values may require stronger handling.

---

# 85. Missing Setting

If an older database lacks a newly introduced setting:

```text
use current default
```

rather than requiring every possible default to be physically persisted.

Evaluate based on architecture.

---

# 86. Settings Documentation

Every setting should eventually document:

```text
key
display name
purpose
type
default
allowed values
scope
security sensitivity
restart requirement
consumer
```

This should be derivable from the authoritative setting definition where possible.

---

# 87. Module Settings Inventory

Phase 0D must produce an inventory.

At minimum:

```text
General
Appearance
Clipboard
Tags
Diagnostics
PowerShell
Automation
Analytics
Mochi
Privacy
Advanced
```

For each potential setting classify:

```text
CORE
LIKELY
FUTURE
REJECTED
NEEDS REVIEW
```

---

# 88. Avoid Settings Explosion

Do not expose every internal constant as a user setting.

Bad examples:

```text
regex timeout
SQL batch size
internal parser threshold #7
widget margin
```

unless a legitimate user/developer need exists.

A setting should justify its existence.

---

# 89. Setting Creation Criteria

Create a setting when:

```text
users reasonably need control
environments legitimately differ
security/privacy policy needs explicit configuration
operational behavior needs safe tuning
```

Do not create a setting merely to avoid making an architectural decision.

---

# 90. Safe Defaults

Phase 0D must explicitly prioritize safe defaults.

Examples:

```text
automatic clipboard persistence:
conservative

secret handling:
protective

arbitrary execution:
disabled / impossible

AI/cloud context sharing:
disabled until explicitly configured
```

---

# 91. User Experience Principle

Settings should describe user intent.

Prefer:

```text
Keep temporary clipboard items for:
[7 days]
```

over:

```text
clipboard_retention_ttl_seconds
```

Machine key remains internal.

---

# 92. Advanced Details

Technical fields may exist under:

```text
Advanced
```

but should still be understandable.

Avoid turning Settings into an `.ini` editor.

---

# 93. Settings Search Metadata

Structured descriptors may include:

```text
keywords
```

Example:

```text
clipboard.retention_days

keywords:
history
expire
cleanup
clipboard
```

Useful for future search.

---

# 94. Bilingual Settings

Because F7Hub may support English/French UI, evaluate:

```text
stable language-neutral key
localized label
localized description
```

Example:

```text
key:
clipboard.retention_days

EN:
Retention period

FR:
Durée de conservation
```

Do not store translated labels as machine identifiers.

---

# 95. Values Should Remain Locale-Neutral

Example:

```text
30
```

not:

```text
30 jours
```

Persistence should use canonical values.

Presentation handles localization.

---

# 96. Date / Duration Settings

Prefer explicit units in keys or typed descriptors.

Good:

```text
clipboard.retention_days
diagnostics.timeout_seconds
```

Avoid ambiguous:

```text
timeout = 30
```

without defined units.

---

# 97. Boolean Naming

Use positive, explicit keys.

Prefer:

```text
clipboard.auto_capture_enabled
```

rather than:

```text
disable_clipboard_auto_capture
```

to reduce double-negative confusion.

---

# 98. Enum Settings

Example:

```text
mochi.notification_level

quiet
normal
detailed
```

Enum values require stable machine keys and user-friendly labels.

---

# 99. Paths and Executables

Do not permit arbitrary executable paths where an approved registry should be used.

Settings must not become a backdoor around PowerShell/script safety.

---

# 100. Settings vs Registries

Important distinction:

```text
Settings
```

configure behavior.

```text
Script Registry
```

defines approved scripts.

```text
Tag Catalog
```

defines taxonomy.

```text
Diagnostic Registry
```

defines available diagnostics.

Do not collapse these into Settings.

---

# 101. Settings Page Ownership

Settings UI should orchestrate shared components.

Potential pages:

```text
GeneralSettingsPage
ClipboardSettingsPage
TaxonomySettingsPage
DiagnosticSettingsPage
MochiSettingsPage
```

Exact class names must follow project conventions.

Do not create them during Phase 0D.

---

# 102. Settings Registry

Evaluate a shared settings-definition registry.

Conceptually:

```text
SettingsRegistry
├── General
├── Clipboard
├── Diagnostics
├── Analytics
└── Mochi
```

This is not necessarily a plugin registry.

It may simply be static modular composition.

---

# 103. Module Isolation

A feature should be able to own its own Setting definitions while using shared infrastructure.

Example:

```text
Clipboard
owns:
clipboard.retention_days

Settings system
owns:
validation/persistence/access
```

---

# 104. Feature Removal

If Clipboard were disabled or removed, its settings should not destabilize other modules.

Avoid cross-module settings that create hidden dependency webs.

---

# 105. Privacy & Security Section

Proposed Settings section should centralize policy visibility.

Potential controls:

```text
Clipboard sensitive-content handling
Diagnostic evidence retention
Mochi context sources
Future AI/cloud integration
Logging sensitivity
```

Some items may link to module-specific pages rather than duplicate controls.

---

# 106. Advanced Diagnostics

The Settings UI could eventually expose a diagnostic view of effective configuration:

```text
Setting
Default
Override
Effective
Source
```

Example:

```text
clipboard.retention_days
7
30
30
SQLite user override
```

This can make troubleshooting configuration much easier.

Likely Advanced-only.

---

# 107. Import / Export Deferred

Unless inspection identifies a requirement, defer:

```text
settings profile import/export
cloud synchronization
multi-user policy deployment
```

These add substantial complexity.

---

# 108. Multi-User Consideration

F7Hub is currently primarily a local technician application.

Determine whether user-scoped settings need actual multi-user database semantics now.

Avoid premature enterprise policy architecture.

---

# 109. Future Plugin Settings

Do not redesign Settings around hypothetical plugins.

However, ensure the architecture does not make future module-owned setting definitions impossible.

---

# 110. Settings and Background Services

If Mochi or clipboard processing later uses a background process, define how it obtains effective settings safely.

Potential:

```text
startup config snapshot
```

plus:

```text
change notification
```

Do not allow every process to maintain unrelated copies.

---

# 111. Settings and Startup Failure

If an optional module's settings fail to load:

```text
disable/degrade that module safely
```

rather than corrupting unrelated application startup where possible.

---

# 112. Required Settings Matrix

Produce a matrix:

| Setting Area | Owner | Persistence | Sensitive | Runtime Update | Restart |
|---|---|---|---|---|---|
| Appearance | TBD | TBD | No | Yes | No |
| Clipboard | TBD | TBD | Some | Usually | Maybe |
| Diagnostics | TBD | TBD | Some | Usually | Maybe |
| Mochi | TBD | TBD | Some | Usually | Maybe |

Do not populate unknown architecture as FACT.

---

# 113. Required Persistence Decision Matrix

For each setting family recommend:

```text
SQLite
Config File
Environment
Runtime only
Not a Setting
```

Examples to evaluate:

```text
theme
clipboard retention
database path
API secret
diagnostic timeout
hotkey
Mochi speech
tag catalog
PowerShell script registry
```

This matrix is a required Phase 0D output.

---

# 114. Important Example

The matrix should make distinctions such as:

```text
Clipboard retention
→ SQLite setting

Tag catalog
→ NOT a Setting
→ taxonomy tables

API key
→ NOT ordinary Settings persistence
→ secure secret mechanism

Diagnostic definition
→ NOT a Setting
→ diagnostic registry

Diagnostic timeout
→ Setting
```

This prevents architecture blur.

---

# 115. Required Dependency Diagram

Produce:

```text
                     Settings GUI
                         │
                         ▼
                  SettingsService
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        SettingsRepository      Defaults Registry
              │
              ▼
            SQLite

Feature Services
Clipboard / Diagnostics / Analytics / Mochi
              │
              └──── read effective settings
```

Refine based on existing architecture.

---

# 116. Required Configuration Precedence Diagram

Document clearly:

```text
Default
 ↓
Persisted Override
 ↓
Environment / Startup Override
 ↓
Runtime Override
 ↓
Effective Value
```

or the recommended alternative.

---

# 117. Required Settings Lifecycle Diagram

Example:

```text
Definition
   ↓
Default
   ↓
Load Override
   ↓
Validate
   ↓
Effective Value
   ↓
Feature Uses Value
   ↓
User Changes
   ↓
Validate
   ↓
Persist
   ↓
Notify
```

---

# 118. Required Decision Register

At minimum decide/evaluate:

```text
SQLite vs config responsibilities
setting definitions source of truth
precedence model
setting scopes
typed validation
defaults ownership
effective-value model
SettingsService caching
change notifications
restart-required metadata
sensitive-setting handling
hotkey storage
audit strategy
bilingual labels
module registration
```

For each:

```text
Decision
Options
Recommendation
Reason
Consequences
Status
```

Statuses:

```text
RECOMMENDED
REQUIRES_USER_DECISION
DEFERRED
NOT_VERIFIED
```

---

# 119. Required Risk Register

Include:

```text
duplicate config sources
conflicting defaults
settings/business logic coupling
unsafe user overrides
secret leakage
stale caches
cross-process inconsistency
invalid stored values
settings explosion
migration drift
circular module dependencies
hidden restart requirements
```

Provide mitigations.

---

# 120. Planning Depth Classification

Classify every topic:

```text
DECIDE NOW
DESIGN NEXT
DEFER UNTIL FEATURE PLAN
DEFER UNTIL IMPLEMENTATION
```

Likely `DECIDE NOW`:

```text
SettingsService ownership
persistence strategy
precedence
typed definitions
security boundary
Settings vs taxonomy/registry distinction
```

Likely `DESIGN NEXT`:

```text
exact Clipboard settings
exact Diagnostic settings
exact Mochi settings
```

Likely `DEFER`:

```text
cloud sync
settings profiles
enterprise policy distribution
plugin settings marketplace
```

---

# 121. Required Module Settings Inventory

Produce proposed inventories for:

## General

## Appearance

## Clipboard

## Tags & Taxonomy

## Diagnostics

## PowerShell

## Automation

## Statistical Analytics

## Mochi

## Privacy & Security

## Advanced

Each setting candidate should include:

```text
key
purpose
type
default candidate
scope
persistence recommendation
sensitive?
restart?
status
```

Status:

```text
CORE
LIKELY
FUTURE
REJECTED
NEEDS REVIEW
```

---

# 122. Phase 0D Acceptance Criteria

Phase 0D is acceptable when:

1. Current F7Hub configuration mechanisms have been inspected.
2. Current config sources have been inventoried.
3. Settings ownership is explicit.
4. Settings and business semantics are separated.
5. Settings and taxonomy are separated.
6. Settings and registries are separated.
7. Persistence responsibilities are defined.
8. SQLite vs config-file decisions are documented.
9. Setting scopes are defined.
10. Default ownership is defined.
11. Precedence is defined.
12. Validation ownership is defined.
13. Effective-value semantics are defined.
14. Sensitive values are handled safely.
15. Secrets are excluded from ordinary settings storage.
16. Security invariants cannot be weakened casually by settings.
17. Module integration rules are defined.
18. Change propagation is planned.
19. Restart-required semantics are planned.
20. Bilingual display concerns are considered.
21. Initial module setting inventories exist.
22. Database impact is assessed without migrations.
23. No production implementation has occurred.
24. Clipboard, Diagnostic, Analytics, and Mochi plans can now depend on a stable configuration architecture.

---

# 123. Validation

Return:

```text
Current configuration inspection       PASS / FAIL / BLOCKED
Config-source inventory                PASS / FAIL / BLOCKED
Settings ownership                     PASS / FAIL / BLOCKED
Persistence architecture               PASS / FAIL / BLOCKED
Precedence model                       PASS / FAIL / BLOCKED
Defaults model                         PASS / FAIL / BLOCKED
Validation architecture                PASS / FAIL / BLOCKED
Security/privacy review                PASS / FAIL / BLOCKED
Secrets boundary                       PASS / FAIL / BLOCKED
Cross-module integration               PASS / FAIL / BLOCKED
Settings/taxonomy separation           PASS / FAIL / BLOCKED
Settings/registry separation           PASS / FAIL / BLOCKED
Migration impact review                PASS / FAIL / BLOCKED
Scope control                          PASS / FAIL / BLOCKED
Production changes                     MUST BE NONE
Database changes                       MUST BE NONE
```

---

# 124. Required Final Report

Return in this order:

## Summary

Recommended configuration architecture.

## Current-State Configuration

What exists and where.

## Settings Principles

Global invariants.

## Configuration Sources

Current and recommended responsibilities.

## Settings Ownership

Service/repository/module boundaries.

## Persistence Strategy

SQLite vs config vs environment vs runtime.

## Precedence Model

Effective-value resolution.

## Setting Definition Model

Types, defaults, scopes, validation and metadata.

## Security & Secrets

Safe configuration boundary.

## Module Settings Inventory

General through Advanced.

## GUI Architecture

Settings navigation and interaction model.

## Change Propagation

How modules receive changes.

## Migration & Evolution

Setting-key lifecycle.

## Testing Strategy

Future validation.

## Decision Register

Recommendations and unresolved decisions.

## Risk Register

Configuration-specific risks.

## Inputs for Feature Plans

Explicitly state what Clipboard, Diagnostics, Analytics, and Mochi can now assume.

## Result

Return exactly one:

```text
READY_FOR_FEATURE_ARCHITECTURE
REQUIRES_SETTINGS_DECISIONS
BLOCKED
```

Do not return:

```text
READY_FOR_IMPLEMENTATION
```

Phase 0D completes the foundation-planning sequence.

---

# 125. Offline settings and secrets

