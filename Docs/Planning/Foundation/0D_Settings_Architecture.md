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

---

# EXECUTION REPORT

## Summary

RECOMMENDATION: use one Python-owned Settings application boundary for future shared preferences, with module-owned typed definitions composed centrally and durable user overrides in SQLite. Reuse existing database infrastructure, composition and notification patterns. Keep bootstrap paths outside database-dependent resolution. Keep AltF7Hub appearance preferences subsystem-local and preserve Mochi's standalone read-only JSON loader. A global configuration file, universal configuration IPC, event bus and credential vault are not justified.

Date: 2026-10-07, America/Toronto. Mode: ARCHITECT / PLAN. Candidate authority: UNAPPROVED, UNSTAGED, UNCOMMITTED, NOT INTEGRATED. All new architectural choices below are RECOMMENDATION pending independent review and explicit USER approval. FACT identifies inspected source/documentation or executed documentation checks; it never implies runtime acceptance. INFERENCE identifies a derived conclusion. ASSUMPTION and NOT VERIFIED remain explicit.

FACT: approved 0A, 0B, 0C and the root Cloud / Windows-native Validation Contract are integrated ancestors of the verified baseline. Their historical report labels remain historical and do not reopen approval. The original statement that 0D "completes the foundation-planning sequence." is preserved exactly. Under current governance, 0D may become ready as a Settings input for downstream feature architecture after approval/integration, but 0E remains a separate NOT STARTED reconciliation phase. General feature-planning readiness still belongs to 0E. This report executes no 0E or feature plan.

No production implementation, operational database access, migration, configuration file, hotkey registration, GUI execution, provider call or Cloud configuration occurred.

## Baseline / Candidate Identity

| Item | Verified value / convention |
| --- | --- |
| Canonical checkout / starting branch | C:\Dev\F7Hub / main |
| HEAD / origin/main / live remote main | 8cf42d676b201390e96d451e61f027d32df2bc63 |
| Origin | https://github.com/JDecelles1990/F7Hub.git |
| Original target Git blob | 448355b67c9d552882b829f50f738afc75b27e92 |
| Original raw checkout SHA-256 | 01f60854b2e422e8f6fc3e9e0849179cd5d9cc1f81f169004f4d40819e60a255 |
| Original raw bytes | 45,567 |
| Original lines | 2,948 newline-terminated lines; 2,949 elements when splitting on LF and counting the terminal empty element |
| Original representation | UTF-8 without BOM; 2,948 CRLF terminators; zero bare LF |
| Initial tracked modifications / index | NONE / empty |
| Permitted unrelated untracked pathname | AutoHotkey/Troubleshooting_Sections/GuideSettings.ini |
| Candidate branch | docs/foundation-0d-execution-20261007 |
| Authorized tracked write | Docs/Planning/Foundation/0D_Settings_Architecture.md, append only |
| Final whole-file identity | Recorded in completion response after all edits; deliberately not embedded in this file |

FRESH initial checks: git branch --show-current; git rev-parse HEAD; git rev-parse origin/main; git status --short; git diff --name-only; git diff --cached --name-only; git ls-files --others --exclude-standard; git diff --check; git ls-tree HEAD -- target; git ls-remote origin refs/heads/main. All required identities matched. Remote identity, core.autocrlf=true and target attributes were inspected without changing Git configuration. Branch creation followed the passing gate; no additional worktree was needed.

The 2,949 requested line count and the 2,948 terminator count describe the same exact blob/checkout. Preservation is established by the first 45,567 bytes and their SHA-256, not by a line-count heuristic. The entire original document, including its empty final heading and historical wording, remains the exact candidate prefix in the original CRLF representation.

## Repository Areas Inspected

The following evidence IDs are reused throughout this report. Paths are repository-grounded, at the pinned HEAD. Named symbols and line anchors describe source locations; test sources were read, not executed.

| ID | Inspected evidence | Architectural purpose / limit |
| --- | --- | --- |
| G | Root AGENTS.md, ROOT.md, [documentation router](../../19_DocumentationIndex.md), Planning/Foundation scoped instructions; Git gate and log | Scope, approval, phase ownership and validation vocabulary |
| F-A | [Approved 0A](<0A_Master_Foundation_Architectural_Contract.md#execution-report>), summary, ownership matrices, security/configuration model, decisions and downstream contract | Layering; DynamicHub coordination; optional Ticket association; no secret/settings authority in companions |
| F-B | [Approved 0B](<0B_Global_JSON_Contract_Interoperability_Grammar.md#execution-report>), envelope, identity, missing/null, validation, security, retained contracts and downstream inputs | Communication grammar; legacy compatibility; structural validity does not authorize effects |
| F-C | [Approved 0C](0C_Taxonomy_Information_Vocabulary.md#execution-report), summary, privacy, retention, compatibility and Settings inputs | Meaning versus preference; taxonomy and retention authority |
| E01 | [main](../../../Python/f7hub/app/main.py), main; [bootstrap](../../../Python/f7hub/app/bootstrap.py), bootstrap_application/ApplicationContext | Explicit --database, project-root injection, composition; no global Settings composition |
| E02 | [database paths](../../../Python/f7hub/infrastructure/database_paths.py), both resolvers; [database](../../../Python/f7hub/infrastructure/database.py), open_database/database_connection; [migrations](../../../Python/f7hub/infrastructure/migrations.py) | Development/installed path distinction; 5000 ms default; connection and migration ownership |
| E03 | [application logger](../../../Python/f7hub/app/logging_config.py); [backup service](../../../Python/f7hub/services/database_backup_service.py) | LocalAppData logging/backup paths, INFO, bounded rotation, safe logging fallback |
| E04 | [migration directory](../../../Database/Migrations/), tracked 0001 through 0012; 0001_core, 0002_taxonomy and 0007_script_registry; later diagnostic seed/update SQL | Actual migrated objects; no Settings or generic audit table |
| E05 | [ScriptRepository](../../../Python/f7hub/repositories/script_repository.py), [ScriptService](../../../Python/f7hub/services/script_service.py), [PowerShellService](../../../Python/f7hub/services/powershell_service.py), eligibility and execution | Registry metadata and literal execution policy differ from user preferences |
| E06 | [PowerShellGateway](../../../Python/f7hub/infrastructure/powershell_gateway.py), execute/_runtime/_environment; [Windows execution](../../../Python/f7hub/infrastructure/windows_execution.py); three tracked PowerShell/Diagnostics scripts | Fixed runtime/environment, parameterless diagnostics, process/output bounds; native behavior NOT RUN |
| E07 | [AHK host](../../../AutoHotkey/F7Hub.ahk), [launcher](../../../AutoHotkey/Launchers/F7HubLauncher.ahk), [F7 controller](../../../AutoHotkey/Hotkeys/F7HotkeyController.ahk), [Alt gateway](../../../Python/f7hub/infrastructure/altf7hub_gateway.py) | Static hotkeys; startup paths/timings; fixed show/focus bridge |
| E08 | Explicitly read [Alt guidance](../../../AutoHotkey/Troubleshooting_Sections/AGENTS.md), [README](../../../AutoHotkey/Troubleshooting_Sections/README.md), [GuideCore](../../../AutoHotkey/Troubleshooting_Sections/GuideCore.ahk), LoadSettings/SaveSettings/change handlers, [GuideHost](../../../AutoHotkey/Troubleshooting_Sections/GuideHost.ahk) | Local preferences and sidecars from tracked source only; protected live INI never opened |
| E09 | Explicitly read [Mochi guidance](../../../Mochi/AGENTS.md), [README](../../../Mochi/README.md), [Architecture](../../../Mochi/docs/Architecture.md), relevant MVP privacy/configuration requirements | Standalone compatibility and planned features versus current code |
| E10 | [Mochi config](../../../Mochi/src/mochi/core/config.py), Settings/load_settings; [tracked JSON](../../../Mochi/config/settings.json); [app](../../../Mochi/src/mochi/app.py); core/logging.py | Typed immutable defaults, read-only config loading, app-root paths and local logger |
| E11 | [PetRuntime](../../../Mochi/src/mochi/services/pet_runtime.py); [MochiService](../../../Python/f7hub/services/mochi_service.py); [gateway](../../../Python/f7hub/infrastructure/mochi_gateway.py); [channel](../../../Python/f7hub/infrastructure/mochi_channel.py); [protocol](../../../Python/f7hub/domain/mochi_protocol.py) | Cosmetic state, session/attachment identities, callbacks/signals, fixed v1 limits |
| E12 | [MainWindow](../../../Python/f7hub/gui/main_window.py), Settings menu/show_mochi_settings; [Mochi dialog](../../../Python/f7hub/gui/mochi_settings_dialog.py) | One modeless runtime-control dialog, no preference persistence |
| E13 | [Mochi config tests](../../../Mochi/tests/test_config.py); [path tests](../../../Tests/Database/test_database_paths.py); [logging tests](../../../Tests/Integration/test_application_logging.py); application bootstrap tests; [Mochi GUI tests](../../../Tests/GUI/test_mochi_controls.py); [guide fixture smoke](../../../AutoHotkey/Troubleshooting_Sections/Tests/guide_smoke.ahk); registry/management and diagnostic-pack tests | Test assertions substantiate intended boundaries; all runtime suites NOT RUN |
| E14 | Relevant Docs 02/05/06/07/08/09/10/11/12/13/15 sections, including Settings, metadata, persistence, logging, paths and naming | Canonical intent distinguished from migrated implementation |
| E15 | Tracked-file searches across Python, AutoHotkey, PowerShell, Database, Config, Docs, Tests and Mochi | Settings/config/preferences/defaults/environment/LocalAppData/timeouts/retention/hotkeys/feature flags/paths/startup/runtime/QSettings/JSON/YAML/INI/CLI; bounded source and filename inventory |

SEARCH used rg for document/symbol discovery and git grep/git ls-files for tracked subsystem inventory, so untracked protected state was excluded. No Config files, generic Settings classes, QSettings consumer, YAML/configparser settings loader, Windows-registry preference reader or tracked DynamicHub implementation was found in the relevant tracked source. This is a bounded repository finding, not a statement about installed copies or external prototypes. External DynamicHub material, historical artwork/evidence, real customer content and mutable operational database rows were excluded.

The only project skill discovered was [vertical-slice-delivery](../../../.agents/skills/vertical-slice-delivery/SKILL.md). Its candidate/Git-preservation guidance was applied; implementation lifecycle machinery and independent review were not executed.

## Verified Current-State Configuration

FACT E01-E04: F7Hub currently composes repositories/services around an explicit database path. Bootstrap defaults to Database/Dev/f7hub_dev.db. resolve_runtime_database_path exists for LocalAppData/F7Hub/Data/f7hub.db but is not the default called by current bootstrap. Logging initializes before database composition and independently uses LOCALAPPDATA, INFO and 1 MiB rotation with two backups. Manual backups use LOCALAPPDATA/F7Hub/Backups. Current connections default to 5000 ms and enable foreign keys.

FACT E04/E15: tracked migrations 0001-0012 create core metadata, taxonomy, business records/associations, Knowledge FTS and scripts; later migrations register/update three diagnostics. There is no migrated generic Settings/value structure or generic audit store. application_metadata is database/application lifecycle metadata, explicitly not user preferences in Docs/09_SQLSchema.md. No generic SettingsService/SettingsRepository implementation was found. Their canonical mentions are planned architecture, not current classes. Canonical SQL for other future objects is not evidence of a migration.

FACT E05/E06: scripts.timeout_seconds has a 120-second schema default for generic registration; the three approved diagnostics have 60-second registrations and a literal maximum_timeout of 60. Registry enablement is catalog state; eligibility also requires exact identity, path, version, type, runtime, risk, privilege, structured output and digest. The gateway owns the trusted non-elevated runtime, private copy, restricted child environment, output/deadline bounds and cleanup quarantine. These scripts are parameterless today. An internal CIM timeout or output cap is not automatically a user setting.

FACT E08: GuideCore owns built-in appearance defaults and INI reads/writes. Opacity defaults to 85 and is clamped to 60-100 by current source; pinning/sidebar-hidden/auto-fit default false; heading bold true and fallback color 6BCB77. Appearance changes update local runtime; opacity saves are debounced and pending changes flush at exit. SaveSettings constructs a known-field INI replacement: unlike Mochi's read-only loader, it does not establish preservation of unknown INI keys. Topic sidecars carry identity/formatting, not a global preference store. The live INI was not read, hashed, statted or managed.

FACT E14: Docs/11_AHKArchitecture.md's summary still says opacity bounds 70-100, while tracked GuideCore and the local README say 60-100. This is a bounded documentation/source discrepancy. Current native behavior is NOT VERIFIED. This report does not change either source, approve new bounds, or choose a global range; AltF7Hub's owner must resolve the discrepancy in separately scoped work.

FACT E10/E13: Mochi's frozen Settings owns defaults: enabled true, always_on_top true, opacity 1.0, idle_row 0, wave_row 3 and frame interval 120 ms. The loader bounds input, validates supported fields and contained frame paths, falls back on invalid values and does not write the JSON. Unknown fields remain in the file because no write occurs; they are not returned as effective typed settings. Unsupported capture/OCR/clipboard/integration/click-through flags cannot enable capabilities. f7hub.read_only is not an implemented write-mode switch.

FACT E11/E12: MainWindow's Settings -> Mochi dialog invokes cosmetic runtime commands through MochiService and existing IPC. It neither writes settings.json nor persists pause, visibility, animation selection, attachment, greeting consumption or connection generation. The app loads JSON at startup; no implemented reload/save path exists. No implemented speech, context-sharing, global theme/language preference or central hotkey editor was found.

INFERENCE: existing local loaders and application composition are useful precedents, but none provides shared persisted override resolution. A future bounded SettingsService/Repository is necessary for shared durable preferences; simply renaming Mochi's loader or using application_metadata would duplicate or misuse ownership.

ASSUMPTION: the initial shared-preference use case is one local technician preference set for an application profile and its selected database. No approved enterprise multi-user preference hierarchy was found. Shared-database/multiple-actor policy is deferred rather than inferred from Contacts or ticket assignees.

NOT VERIFIED: live desktop behavior, operational database validity/rows, installed distribution defaults, employer privacy policy, secret provider and future feature implementation. Historical PASS prose in inspected documents is not fresh evidence.

## Existing Configuration Source Inventory

Each source has two joined rows keyed by Cxx. Together the tables cover source, purpose, current owner, reader, writer, lifecycle, persistence, scope, sensitivity, defaults, mutability, restart, implementation status and recommended treatment.

| ID / source / evidence | Current purpose | Current owner / readers | Current writer | Persistence / scope | Status / recommended treatment |
| --- | --- | --- | --- | --- | --- |
| C01 Python main --database and bootstrap project_root/database_path; E01 | Select active database and checkout dependencies | Python composition / bootstrap | Caller or launch arguments | Startup input; process/application instance | Implemented / REUSE |
| C02 database_paths, LOCALAPPDATA; E02 | Resolve development and installed database locations | Path infrastructure / composition or explicit caller | Host environment or injected caller | Environment/startup; local profile/device | Implemented resolver; installed default not wired / REUSE |
| C03 database.py connection options; E02 | Foreign keys and busy timeout | Database infrastructure / repositories/migrations | Reviewed code or validated caller argument | Code default/per-connection runtime | Implemented / NOT A SETTING |
| C04 logging_config.py; E03 | Process-local F7Hub handler/path/level/rotation | Application logging / f7hub loggers | Reviewed code; LOCALAPPDATA from host | Startup environment and code; process/local profile | Implemented / REUSE |
| C05 DatabaseBackupService; E03 | Manual backup target root and collision-safe filename | Backup service / explicit backup workflow | Code/host path environment | Startup-derived target; per-operation filename | Implemented / REUSE |
| C06 migrations/application_metadata; E04 | Schema history and database lifecycle identity | Migration/database infrastructure / bootstrap | Versioned migrations; authorized metadata owner | SQLite; database instance | Implemented / NOT A SETTING |
| C07 scripts registry metadata; E04/E05 | Registered identity, visibility, timeout and verification metadata | ScriptService/Repository / catalog and PowerShellService | Approved registration management or versioned reference-data migrations | SQLite; script identity | Implemented / NOT A SETTING |
| C08 literal diagnostic policy, gateway environment/runtime/caps; E05/E06 | Authorize narrowly approved collection and bound execution | PowerShellService/Gateway / gateway and child launcher | Reviewed source; gateway constructs explicit child environment | Code plus ephemeral child environment; operation/process | Implemented / NOT A SETTING |
| C09 GuideCore appearance INI mechanism; E08 | Opacity/topmost/sidebar/heading/auto-fit preferences | AltF7Hub GuideCore / GuideHost and GUI | Local guide controls via SaveSettings | Optional subsystem-local INI; guide data root | Implemented mechanism, live values NOT VERIFIED / KEEP SUBSYSTEM-LOCAL |
| C10 topic styles sidecars and TopicRouting; E08 | Topic identity, shortcut metadata and personal formatting | Guide/editor/topic owner / topic loader | Authored metadata and guarded editor save | Paired topic files; library/topic | Implemented / NOT A SETTING |
| C11 F7Hub.ahk, F7 launcher/controller; E07 | Static action bindings, Python launch/path/timing and hold state | Shared AHK host / hotkey handlers/launcher | Reviewed source; injected launcher arguments | Code/startup inputs plus transient runtime state | Implemented / KEEP SUBSYSTEM-LOCAL |
| C12 Mochi/config/settings.json with core/config.py; E10 | Standalone pet startup configuration | Mochi config core / app and PetWindow | Tracked author/manual file editor; runtime writes NONE | JSON; standalone installation | Implemented / KEEP SUBSYSTEM-LOCAL |
| C13 PetRuntime, MochiService and Settings dialog; E11/E12 | Playback/visibility/attachment/application-session control | Runtime/service / local renderer and control UI | Approved cosmetic commands, runtime callbacks | Memory only; process/application session | Implemented / NOT A SETTING |
| C14 mochi_protocol/channel identity/limits; E11 | Fixed v1 grammar, local endpoint identity and transport bounds | Protocol/gateway/controller / both peers | Reviewed source; endpoint identity derived at runtime | Code plus per-user/checkout cache lock | Implemented / NOT A SETTING |
| C15 Mochi core/logging.py; E10 | Bounded standalone technical logging | Mochi composition/logger / mochi loggers | Runtime handler writes logs, not preferences | Root/logs/mochi.log; process/installation | Implemented / ADAPT for future installed-path composition |
| C16 Mochi/config/guide.json; E09 | Empty future local-guidance placeholder | Future guide owner / no current populated-guide consumer | Future reviewed author/generator | Tracked empty file; planned guide content | Placeholder / NOT RELATED to Settings values |
| C17 AltF7Hub gateway ProgramFiles and fixed timeout; E07 | Locate approved AHK v2 and bound fixed client | Python Alt gateway / guide-open service | Host environment and reviewed code | Environment/code; local operation | Implemented / REUSE |
| C18 PYTHONPATH/Qt test and development launch environment; E07/E13 | Module discovery and validation presentation backend | Launcher/test harness / Python/Qt | Explicit launcher or isolated test harness | Session/test environment | Implemented support / NOT RELATED to product preferences |
| C19 Canonical Settings classes/navigation/config examples; E14 | Intended future shared architecture | Canonical owners / planners | Documentation authors | Documentation only | Planned / ADAPT into bounded later shared implementation |

| ID | Lifecycle / current defaults | Sensitivity | Runtime mutability / restart implications |
| --- | --- | --- | --- |
| C01 | Resolve before repositories; default development database unless explicit path | Paths can identify user/customer environment | No live database-switch mechanism; use next process; no automatic migration or data relocation |
| C02 | Resolve when requested; installed resolver requires LOCALAPPDATA | Local machine/profile paths; not credentials | Host/injected values are bootstrap inputs; do not hot-swap services |
| C03 | Each connection: foreign_keys ON, busy timeout 5000 ms | Integrity/availability control | Caller timeout validated; FK enforcement invariant; no UI control established |
| C04 | Install/close owned handler; INFO, 1 MiB, two backups; stderr fallback | Logs may contain operational metadata | Reconfiguration function exists, user live-level feature absent; path change is composition work |
| C05 | Explicit backup; fixed LocalAppData root, timestamp/UUID filename | Backup contains application data | Per-operation derivation; no preference/restart feature |
| C06 | Bootstrap/versioned schema lifecycle; no preference defaults | Application identity/schema history | Forward-only migration discipline; no user edit/reset |
| C07 | Catalog management; generic timeout 120, default disabled, approved diagnostic registrations 60 | Paths/definitions may be operationally sensitive | Current manager changes visibility; no Settings-based timeout edit; execution rechecks metadata |
| C08 | Each execution; approved timeout ceiling 60, stdout 1 MiB/stderr 64 KiB, fixed trusted runtime | Security controls/internal path references | Not user-overridable; private env not imported global preferences; policy/source changes need reviewed slice |
| C09 | Load at host initialization, save local edits, pending exit flush; defaults listed above | Cosmetic, usually low sensitivity | Appearance applies locally; no restart ordinarily; bounds discrepancy remains with Alt owner |
| C10 | Topic load/edit/paired save; built-in routing fallbacks | Authored notes/formatting may be sensitive | Metadata and content lifecycle; not a Settings reset target |
| C11 | Host startup/static F7 and Alt+F7; Pythonw in checkout .venv, launch 15 s, hold 180 ms | Launch paths and focused-window state | Hard-coded bindings remain; registration changes need later native plan; held state never persisted |
| C12 | Startup read; frozen Settings defaults listed above | Ordinary cosmetic config; unsupported privacy flags require scrutiny | Runtime loader has no reload or save; editing JSON takes effect on next renderer start |
| C13 | Fresh process/session; runtime starts visible and STARTING then IDLE | IDs/snapshot are bounded cosmetic metadata | Runtime commands apply through current service; reopening dialog does not restart/reset/persist pet |
| C14 | Endpoint/cache identity at composition; fixed message 4096 bytes, command 2000 ms, startup 5000 ms | Endpoint identity is routing, not privilege authority | Derived/cache/lock state; no user-editable IPC mode or live grammar changes |
| C15 | Standalone app start/close; INFO, 1 MiB, two backups, stderr fallback | Technical log content remains minimized | Startup-selected root/log path; installed log-path governance remains future composition work |
| C16 | Future local guide authoring; no valid populated guide/defaults yet | Future guidance may contain source context | No current live guide reload; not a preference or IPC document |
| C17 | Each show/focus request; standard ProgramFiles AHK v2, 16 s client deadline | Executable/path trust-sensitive | No arbitrary interpreter setting; no runtime elevation or generic command input |
| C18 | Explicit launch/test lifetime; inherited PYTHONPATH restored by launcher | Harness environment, no production secrets | Test-only Qt backend does not redefine native-validation authority |
| C19 | Planning lifecycle; examples do not seed values or implement a GUI | Secrets explicitly excluded | No implemented save/reload/default hierarchy; later reviewed slices required |

## Existing Architecture Reuse Matrix

| Component / mechanism | Responsibility / layer / owner | Readers / writers | Persistence | Tests/evidence | Fitness / treatment / reason |
| --- | --- | --- | --- | --- | --- |
| Python bootstrap / ApplicationContext | Application composition | main and services / explicit composition | Startup memory | E01, bootstrap test source E13 | REUSE; inject future Settings boundary without moving bootstrap paths into SQLite preferences |
| database_connection / migrations / backup | Infrastructure and guarded persistence | Repositories/bootstrap / authorized owners | SQLite and explicit backup | E02-E04, database test sources | REUSE; common transactions/checksums/FKs; no second database engine or direct GUI SQL |
| application_metadata | Core database lifecycle metadata | Infrastructure / owning metadata workflow | SQLite | E04, Doc09 | NOT RELATED; existing key/value shape does not justify storing user settings here |
| ScriptService/Repository and literal PowerShell policy | Registry persistence, verification and execution eligibility | Catalog/execution / reviewed management and migrations | SQLite plus source policy | E05/E06/E13 | REUSE unchanged; future bounded timeout input must not redefine authorization |
| F7Hub logger | Process-owned bounded technical log | f7hub loggers / app handler | LocalAppData rotating files | E03/E13 | EXTEND only for an approved verbosity use case; not an audit ledger |
| Shared AHK host and fixed Alt gateway | Desktop/hotkey ownership and guide presentation | Host/client / explicit request | Static code; runtime memory | E07/E08/E13 | REUSE; no configuration transport through the show/focus message |
| GuideCore optional INI | Local appearance preferences, lightweight subsystem | Host/GUI / GuideCore | Optional local INI | E08 and fixture smoke source | KEEP SUBSYSTEM-LOCAL; no cross-feature business values, standalone defaults sufficient |
| Topic sidecars | Topic ID/ranges/shortcut integrity | Guide/editor / guarded topic save | Paired metadata | E08 | NOT RELATED; preserve content/formatting authority |
| Mochi Settings/load_settings | Standalone typed startup config | app/PetWindow / runtime writer NONE | Read-only JSON | E10/E13 | KEEP SUBSYSTEM-LOCAL; ADAPT at integration boundary only when shared preference use case is approved |
| MochiService callbacks and gateway Qt signals | Application-owned cosmetic control/notification | Dialog/service/renderer / runtime outcomes | Memory | E11-E13 | REUSE notification pattern; do not use pet state as persisted preferences |
| Mochi v1 protocol/channel | Bounded cosmetic process agreement | Both peers / explicit commands | Runtime IPC/lock | E11 and local-control test sources | REUSE unchanged; any new configuration payload requires reviewed 0B-compatible profile |
| Mochi standalone logger | Process-local technical logging | Mochi logger / handler | Installation-root logs | E10 | ADAPT only during future distribution/path work; no runtime rewrite in 0D |
| Canonical SettingsService/Repository concept | Intended shared application/persistence responsibility | Future features / future service | Planned | E14/E15 | ADAPT into NEW bounded components later; no equivalent shared implementation currently exists |

## Settings / Non-Settings Classification

CONFIGURATION is the broad class of permitted deployment/behavior inputs. SETTING is a registered, typed, supported variation of behavior; USER PREFERENCE is its user-controlled presentation/behavior subset. A configuration file's format alone determines none of these classes.

| Representative concept | Classification | Owner / boundary |
| --- | --- | --- |
| Theme | USER PREFERENCE / SETTING candidate | Appearance; does not alter domain meaning; global feature unimplemented |
| Display language | USER PREFERENCE / SETTING candidate | Localization; machine identities remain stable |
| Clipboard retention duration | SETTING candidate | Clipboard service owns eligible expiry/deletion; durable evidence follows its domain |
| Diagnostic timeout preference | SETTING candidate, within reviewed ceilings | Diagnostics use-case input; current registry timeout/policy are distinct |
| Diagnostic definitions/pack membership | REGISTRY / NOT A SETTING | Diagnostics feature and reviewed literal contracts |
| PowerShell script registry | REGISTRY / NOT A SETTING | ScriptService/Repository, migration/security owners |
| Tag catalog | REFERENCE DATA / NOT A SETTING | Existing taxonomy catalog/approved stewardship |
| Entity Type and Category/Type/Kind meaning | ARCHITECTURAL CONTRACT / NOT A SETTING | 0C and domain owners |
| Ticket status/priority semantics | DOMAIN DATA vocabulary / ARCHITECTURAL CONTRACT | Ticket workflow; presentation filters may be preferences |
| JSON schemas, versions and missing/null grammar | ARCHITECTURAL CONTRACT / NOT A SETTING | 0B and feature contract owners |
| Database path, application-data root and log path | ENVIRONMENT / DEPLOYMENT CONFIGURATION | Bootstrap/path infrastructure; not normal preference overrides |
| Logging verbosity | CONFIGURATION; possible restricted SETTING | Logger owns safe content/rotation independent of verbosity |
| Existing F7/Alt+F7 shortcut | NOT A SETTING today; possible future USER PREFERENCE binding | Stable action identity and AHK registration are separate |
| Alt opacity/pinning/sidebar/heading/auto-fit | USER PREFERENCE, subsystem-local | GuideCore; no automatic centralization |
| Mochi app enabled/topmost/opacity/timing | CONFIGURATION / local USER PREFERENCE | Mochi startup loader; future integrated keys need explicit adapter |
| Mochi current visibility/pause/frame/animation | SESSION / RUNTIME STATE | PetRuntime; future initial-visibility preference would be a separate definition |
| Mochi attachment/connection generation/greeting history | SESSION / RUNTIME STATE / DERIVED STATE | Service/gateway/runtime; not user overrides |
| AI/automation presentation or availability flag | SETTING candidate | Can disable permitted workflow, cannot create permission/capability |
| Execution authorization, elevation restrictions, validation, secret exclusion | SECURITY INVARIANT / NOT A SETTING | Services/gateways/security architecture |
| API credential/password/token/cookie/private key | SECRET / NOT A SETTING | Future approved secret-management boundary |
| Opaque approved credential handle | SECRET REFERENCE, conditionally non-secret configuration | Owning integration resolves transiently; reference must itself be safe; mechanism NOT VERIFIED |
| Current ticket/company/contact selection | SESSION / RUNTIME STATE | Application selected context; records themselves are DOMAIN DATA |
| DynamicHub workflow position/current case context | SESSION / RUNTIME STATE or feature-owned DOMAIN DATA if a resumable case is later designed | 0A coordination owner; not generic Settings |
| Search index, effective-value snapshot, endpoint hash | DERIVED STATE / NOT A SETTING | Rebuild from authoritative inputs; not separate user truth |
| Guide topic contents and formatting sidecar identity | DOMAIN/REFERENCE DATA / NOT A SETTING | Topic/content owner; location under an INI does not make it Settings |
| Qt offscreen test backend, artwork QA and guide placeholder | NOT RELATED to ordinary Settings | Validation/development/reference-content owners |

No ambiguous runtime state is converted to a preference merely to persist it.

## Settings Principles

RECOMMENDATION, constrained by F-A/F-B/F-C and root invariants:

1. Define one stable machine identity and one authoritative typed default per admitted setting. A feature must justify genuine user/environment variation before contributing a key.
2. Separate definition, source value, persisted override, startup input, explicit session override, desired effective value and currently applied consumer value.
3. Python's application boundary owns common validation, resolution, authorized changes and transactional persistence. Features own setting meaning/use and domain policy; GUI owns drafts/display only.
4. Taxonomy, registries, capabilities, authorization, architectural contracts and secrets stay outside ordinary value precedence.
5. Defaults are usable without physically persisting every key. Missing ordinary overrides do not create writes; reset deletes eligible overrides.
6. Bootstrap configuration precedes database-backed preferences. Companion-local appearance sources remain local unless a real shared-use case justifies one explicit owner/adapter.
7. Changes are atomic within their persistence boundary. Notifications follow success; active operations retain their start snapshot. Restart/activation failures are visible.
8. Optional privacy-sensitive collection/sharing defaults are conservative and cannot gain authority through fallbacks, import, feature flags or configuration corruption.
9. Offline local work uses local definitions/overrides; optional providers cannot become startup prerequisites. No automatic configuration network fetch.
10. Never expose every constant, use translated identities, create a generic JSON dumping ground, or introduce an event bus/IPC/vault for completeness.

## Recommended Configuration Architecture

RECOMMENDATION: add a bounded Settings application service and override repository only in separately reviewed implementation work. Module-owned pure definitions are composed explicitly at application startup. Shared resolution produces immutable typed snapshots for feature services; repositories only persist approved overrides. SQLite is recommended for centrally owned durable local preferences because section changes, conflict detection and backup recovery share the current transactional application boundary. It is not the authoritative definition/default source.

Keep current startup arguments, path resolution and logging composition as bootstrap inputs. Do not introduce an application config file or environment-variable fan-out without a concrete deployment need. Preserve standalone Mochi JSON and guide INI ownership. A future F7Hub-to-Mochi adapter may replace specific preferences for an explicitly attached integrated session; it must not rewrite the standalone JSON or make Mochi a database client.

NEW concepts are proposed, not implemented: shared SettingsService, SettingsRepository and statically composed definition provider. REUSE: current composition, database infrastructure, finite service runner, owned callbacks/signals, registry/execution boundaries and retained process contracts. No new dependency is selected.

## Settings Ownership

| Responsibility | Recommended owner | Does not own |
| --- | --- | --- |
| Common definition admission, typed validation and resolution | Shared Python Settings application support; pure validation/definition models | Feature operations, taxonomy, permissions or provider SDKs |
| Individual setting meaning, bounds and safe use | Owning module's definition contribution and feature service | Separate persistence, independent defaults or bypass authorization |
| Definition composition | Application bootstrap, explicit static imports/contributions | Dynamic plugin discovery, network catalog loading |
| Persisted override CRUD/transactions/conflict preconditions | SettingsRepository through current database infrastructure | Defaults, editability, privacy decisions or GUI messages |
| Bootstrap inputs/environment admission | Composition/path infrastructure | Arbitrary preference overrides or secrets vault |
| Explicit temporary override lifetime | SettingsService, authorized caller/session | Active workflow records or durable business state |
| Draft/Apply/Cancel/search/localized feedback | Settings presentation | SQL, independent semantic validation or shell construction |
| Applying immediate/next-operation/restart changes | Feature service/consumer under its own lifecycle | Granting authority merely because a value exists |

Feature services receive a validated snapshot/access boundary via composition. They do not open SQLite or parse config files for shared settings. Pure definition contributions cannot import application services or GUI widgets. Settings does not call feature operations during validation; owning services retain runtime effect and authorization checks.

## Setting Definition Model

RECOMMENDATION: immutable module-owned definitions composed into one authoritative static map. The source of truth is versioned Python definitions following existing dataclass/explicit-validator conventions; no definition table or new schema file is selected. Optional documentation/GUI metadata may be derived from these definitions.

| Definition field | Meaning / rule |
| --- | --- |
| setting_key | Stable language-neutral module.setting_name; lower_snake_case segments; unique globally |
| module / owner | One accountable feature/shared owner; module namespace is not a separate scope hierarchy |
| type / units / allowed values | Canonical type plus explicit duration units or closed enum tokens where required |
| default | One validated authoritative value; no GUI/database seed duplicate |
| scope / allowed sources | USER or approved APPLICATION startup use, with SESSION override only when explicitly admitted |
| validation | Type/range/length/enum and pure cross-field rules; owner use-case checks remain separate |
| description metadata | Localization message IDs for display name, section, help, keywords and validation messages |
| sensitivity | Ordinary, privacy/security-sensitive behavioral input, or deployment/path input; never secret |
| user_editability | Whether this key may be edited/reset, with required confirmation/context restrictions |
| update behavior / restart requirement | IMMEDIATE, NEXT_OPERATION or RESTART_REQUIRED; precise restart target |
| persistence class | SQLite, subsystem-local, startup or runtime-only, explicitly selected per definition |
| audit expectation | None for routine cosmetic choice or meaningful safe evidence required for sensitive changes |
| deprecation/evolution metadata | Introduced/deprecated/replacement information when lifecycle requires it; no speculative global schema-version layer |

FACT E14: Doc15 recommends snake_case config keys, while approved 0B and existing diagnostic codes use dotted names. RECOMMENDATION: dotted namespace plus snake_case leaf makes ownership explicit without translating labels. This adopts no new environment convention and does not rename existing GuideCore camel-case INI fields or Mochi nested JSON.

A duplicate key, invalid default, contradictory persistence/scope/update metadata or module-owned security-bypass key fails definition admission. Optional module failure degrades that module safely; a malformed shared/core definition cannot be silently accepted.

## Type and Validation Model

RECOMMENDATION: minimum shared scalar model below. Each admitted key has explicit bounds and units. A generic string is never a shell fragment, executable selector or secret container.

| Type / canonical representation | Validation / serialization | Invalid behavior / ordinary Settings suitability |
| --- | --- | --- |
| boolean | Actual bool; canonical true/false at a JSON boundary; explicit SQLite encoding chosen in later schema design | Reject 0/1 strings or Python integer coercion at service boundary; suitable enable/display preference |
| integer | Exact integer excluding bool; finite definition-specific bounds; decimal numeric value | Reject fractions, overflow and out-of-range input; suitable count/limit |
| float | Finite numeric value excluding bool; bounded domain, such as opacity | Reject NaN/infinity/invalid types; suitable only when justified, no arbitrary precision requirement |
| enum | Closed stable string tokens, locale-neutral; translated labels belong to presentation | Reject unknown token; suitable language/theme choice once feature defines supported set |
| bounded string | Length/content restrictions and purpose-specific validator, e.g. future shortcut binding | Reject malformed input before persistence; not an arbitrary object/string execution escape hatch |
| duration | Validated integer with definition/key units (ms, seconds or days), serialized without localized suffix | Reject ambiguous/negative/out-of-range units; zero only if explicitly meaningful, never automatically "unlimited" |
| path | Bootstrap-specific validated path input, not a generic user-editable scalar | Owner validates containment/allowed roots/trust/existence/access as appropriate; native path behavior separately tested |

Lists and structured objects are DEFER UNTIL FEATURE PLAN: no demonstrated central preference needs arbitrary nested JSON. Frame bundles/routing maps remain feature-owned configuration, not generic list settings. Secret references require a reviewed purpose-specific descriptor and secure owner, not today's generic string type.

GUI parsing converts localized user text to a candidate canonical value and displays field feedback, but service/pure descriptor validation is authoritative. Persistence values are untrusted and revalidated on load. Cross-field validation occurs for the complete prospective group before a transaction. Consumer security, authorization and semantic checks still run at actual use.

## Defaults Model

RECOMMENDATION: defaults belong to the immutable authoritative definition for each shared key. Definitions are validated during composition; GUI, service and repository read the same descriptor. An absent override uses the default without inserting a row. Changing a default changes only inherited desired values; explicit overrides retain their values unless a separately reviewed evolution step requires conversion.

Subsystem-local defaults remain authoritative within their existing standalone boundary: GuideCore for guide appearance; Mochi Settings for standalone pet startup. These are not duplicate global defaults because no shared keys own those values today. A future integrated adapter must map a named centrally owned value explicitly and distinguish the standalone defensive fallback.

Future tests compare descriptor/default admission, GUI-displayed defaults, service resolution, serialization and adapter fallback fixtures. Legacy numeric fallbacks may remain to support standalone/unavailable integration, but are labeled defensive fallback and tested against the owning definition for mapped shared keys. Do not seed defaults into SQLite, generate multiple independent metadata catalogs, or invent default values for deferred features.

## Setting Scopes

| Scope / disposition | Identity / owner | Persistence / precedence / consumers |
| --- | --- | --- |
| USER, accepted for future shared preferences | One local technician preference set in the application's selected profile/database; no Contact/Ticket user FK or invented enterprise actor identity | SQLite overrides; session override only per allowed key; feature services and GUI |
| APPLICATION, accepted for bootstrap configuration | One application process/installation composition | Code/startup inputs; no editable policy hierarchy; composition/path/logging owners |
| SESSION, accepted for explicitly permitted temporary setting override | Settings application session and authorized use case, not pet IPC session or diagnostic run ID | Memory only; cleared explicitly/end of session; consumer snapshot binds lifetime |
| MODULE, rejected as separate precedence tier | Module is namespace/meaning owner and GUI organization | Its keys still declare USER/APPLICATION/SESSION participation; no module-wide store override |
| DEVICE, deferred | No current central device preference domain or enterprise policy use case | Machine-dependent paths stay deployment configuration; concrete identity/schema later |
| Workflow/case, rejected as generic Settings scope | DynamicHub/Case owner | Active/resumable workflow state is feature state/domain data, not a configuration hierarchy |

ASSUMPTION: one local preference set per selected application database/profile is sufficient initially. Selecting --database selects that database's future overrides for the next process; it is not a live preference-profile switch. Multi-user sharing, enterprise policy and OS-identity partitioning require a later actual requirement and review. Merely having Contacts or tenant concepts does not establish a configuration actor model.

## Persistence Strategy

RECOMMENDATION:

- SQLite: shared durable user behavior/preferences, with one repository/service writer boundary, atomic group updates, explicit conflict detection and existing backup infrastructure. Definitions/defaults stay in code; no redundant default rows or JSON preferences in application_metadata.
- ENVIRONMENT / STARTUP: database root, project/runtime roots, approved executable discovery and initial logging composition. Reuse current CLI/constructor inputs; environment participation is per admitted deployment field, not automatic arbitrary key mapping.
- CONFIG FILE: retain Mochi's existing validated read-only standalone JSON. No new central app configuration file is necessary at this baseline.
- SUBSYSTEM-LOCAL PREFERENCE: retain guide INI and bounded standalone cosmetic ownership. No direct shared business values/core SQLite writes from AHK.
- RUNTIME ONLY: explicit session override and ephemeral execution/attachment/selection/workflow state, with separate ownership. A runtime fact is not a setting just because it changes.
- NOT A SETTING: registries/catalogs/contracts/domain records/security rules and secrets. Their existing/future owners retain storage authority.

Transactionality and recovery justify SQLite for shared overrides more than querying preference values does. Small value count does not require a relational definition catalog. Reuse the selected database rather than introducing a second preference database. Backups may eventually include non-secret overrides with that database; machine-specific paths remain excluded. Restoring/copying preferences must not transfer provider authorization or privacy consent to a different profile silently.

Availability: if cosmetic overrides are unavailable, expose a safe default with a diagnostic and disable saving until persistence recovers. Never announce a failed persisted save as success. Optional capture/sharing stays disabled when required privacy configuration/consent cannot be established. Do not rewrite corruption or open operational data during planning.

## Persistence Decision Matrix

| Concept | Recommended persistence | Reason / boundary |
| --- | --- | --- |
| Theme | SQLite | Future durable local user choice; definitions in code; no global implementation yet |
| Language | SQLite | Stable language preference; translation resource choices belong to localization plan |
| Clipboard retention | SQLite | Future typed behavior input; Clipboard owns actual deletion/eligible evidence |
| Database path | ENVIRONMENT / STARTUP | Needed before database service; reuse explicit --database/path infrastructure |
| Log path / LocalAppData root | ENVIRONMENT / STARTUP | Logging precedes DB; not a SettingsRepository dependency |
| API secret | NOT A SETTING | Secure mechanism NOT VERIFIED; no ordinary SQLite/file/environment-vault commitment |
| Approved opaque secret reference | NOT VERIFIED | Only future reviewed integration can establish a safely stored non-secret reference |
| Diagnostic timeout preference | SQLite | Future bounded input; current registry value/ceiling remains separate and authoritative |
| Existing registry timeout | NOT A SETTING | Script metadata owned by registry; do not duplicate current 60-second policy into hidden preferences |
| Configurable global hotkey binding | SQLite | Future central user binding for approved stable action; registration/native conflict handling separate |
| Existing hard-coded F7/Alt+F7 | NOT A SETTING | Keep current source bindings; no registration migration now |
| Mochi speech preference | SQLite | Future integrated assistant preference only after speech architecture; unavailable today |
| Mochi local cosmetic preference | CONFIG FILE | Preserve current standalone JSON/read-only loader and startup semantics |
| Alt appearance preference | SUBSYSTEM-LOCAL PREFERENCE | Existing guide-owned optional INI, no shared business meaning |
| Tag catalog | NOT A SETTING | Reuse existing taxonomy tables/controlled extension, not key/value overrides |
| Entity Type semantics | NOT A SETTING | Approved 0C definition and domain/producer vocabulary |
| Diagnostic registry | NOT A SETTING | Feature definitions and literal pack/approval policy |
| PowerShell script registry | NOT A SETTING | Existing scripts repository/migrations/service |
| Security invariant | NOT A SETTING | Reviewed architecture/service rules outside precedence |
| Runtime session state | RUNTIME ONLY | Selection, pet pause/frame/attachment and current operation remain transient owner state |
| DynamicHub active workflow position | RUNTIME ONLY | Any later resumable-case storage belongs to workflow/Case domain design |
| Logging verbosity | ENVIRONMENT / STARTUP initially | Current INFO/code ownership; future restricted UI option requires explicit logger plan |
| Qt layout restoration | NOT VERIFIED | No central persistence currently found; actual workspace restoration use case must choose bounded opaque/state storage |

## Precedence Model

RECOMMENDATION: one resolution rule over each key's admitted sources: select the highest eligible valid source; never admit a source merely because it exists. The ranks below are low to high. Security invariants, domain authorization, provider capabilities and secrets are outside all ranks.

| Rank / layer | Purpose / scope / writer | Visibility / persistence / restrictions / reset |
| --- | --- | --- |
| 0 definition default | Versioned safe baseline; definition owner | Exposed as default; not a stored override; cannot override invariants |
| 1 installation/startup baseline | Only APPLICATION/deployment fields or a specifically justified key whose descriptor permits it; composition owner | Show source when meaningful; external startup input, not automatically persisted; restart/relaunch removes it |
| 2 persisted user override | Only admitted USER keys; SettingsService via repository | Visible override/effective source; SQLite; reset deletes selected override |
| 3 explicit startup override | Only allowlisted deployment fields; explicit caller; CLI overrides admitted environment input, then installation baseline | Visible source/lock; not a preference write; remove argument/environment input on next process to reset |
| 4 explicit temporary session override | Only keys admitting temporary override; authorized application use case | Visible temporary source/lifetime; memory only; clear session override/end session |

For ordinary USER preferences the eligible chain is default -> persisted user override -> explicitly permitted session override. Installation/environment/CLI layers do not participate unless a concrete per-key feature/deployment decision admits them. There is no F7HUB_<arbitrary setting key> mapping and no new CLI preference option.

For current deployment fields the chain is built-in/path default -> admitted environment input -> explicit CLI/constructor input, with constructor input representing the already-resolved composition value, not another independent competing source. Persisted user and session preference tiers do not apply to the database path or trusted runtime executable. Current --database is the only generic F7Hub CLI configuration option found; Qt arguments remain Qt-owned.

No policy may be lowered through precedence. Invalid required explicit startup configuration fails that bootstrap/use case clearly rather than silently selecting a different database or executable. Existing logging stderr fallback remains an explicitly bounded behavior. Privacy-sensitive invalid input uses the fail-closed handling below, not a lower opt-in value.

## Effective-Value Semantics

RECOMMENDATION: resolve deterministically in a validated immutable snapshot. Each value carries safe source provenance and resolution diagnostics. Distinguish desired effective value from currently applied value when activation is delayed.

| Input state | Defined behavior |
| --- | --- |
| No override / missing value | Use admitted next lower source/default; preserve false, zero and permitted empty values as real values |
| Valid stored override | Use it only for its defined key/type/scope; no default duplication |
| Valid temporary override | Use highest admitted session source for its lifetime; do not persist implicitly |
| Invalid ordinary stored override | Ignore for resolution, preserve original row/source for explicit repair, use next valid source/default, surface safe field issue |
| Invalid privacy/security-sensitive override | Disable affected optional collection/sharing or refuse unsafe workflow; do not fall through to a permissive lower value; expose degraded state |
| Invalid explicit required deployment override | Fail affected bootstrap/use case with safe error; no silent data-path switch |
| Unknown key | No consumer access or automatic key creation; preserve unrecognized persisted row/file content for reviewed evolution, ignore for effective use, never echo raw value into logs |
| Caller requests undefined key | Typed definition/access error; never return an arbitrary caller-supplied default that invents a second authority |
| Deprecated key | Read only under an explicit owner-approved compatibility mapping; show replacement; writes use new key only after reviewed evolution |
| Removed key / invalid range after upgrade | Inert retained value or explicit forward evolution; not reassigned to new semantics or silently clamped |
| Invalid definition default | Definition-admission failure; no runtime substitution invented by GUI/repository |
| Persistence temporarily unavailable | Safe degradation and visible save-disabled state; privacy-sensitive operations fail closed; no false durable success |

Null means explicit absence only if a definition permits it; reset is an operation removing an override, not a null/empty/false sentinel. Current Mochi's local fallback/clamping behavior and GuideCore bounds remain their existing implementation; the proposed shared loader rejects invalid values and reports fallback rather than retroactively rewriting legacy behavior.

## Reset Semantics

RECOMMENDATION: Reset Setting removes that eligible persisted override in a transaction, revealing the next valid admitted source. Reset Section removes an explicit allowlist of eligible user overrides atomically. Reset All User Preferences is restricted to the current profile/database's eligible keys, requires a clear preview, and excludes deployment inputs, subsystem-local files, registry/catalog/domain rows and secrets.

A temporary session override is cleared separately; resetting a stored value may leave it effective until that temporary source is removed. An environment/CLI source cannot be "reset" by writing SQLite. Desired/applied/restart status is recomputed and displayed after reset.

Sensitive reset must not increase capture/sharing without the owner-required explicit confirmation/consent. Reset changes configuration only: no immediate clipboard purge, ticket/evidence deletion, registry disablement, topic formatting reset or operational data cleanup. Retention effects are separate authorized feature operations. Do not silently write the default as an override.

## SettingsService / Repository Boundary

RECOMMENDATION: SettingsService admits definitions, resolves values, returns typed snapshots/source diagnostics, validates proposed groups, checks editability/context/confirmation, coordinates override write/delete transactions and publishes successful changes. Exact API names are DESIGN NEXT and must fit current service conventions; the planning example's method list is not an implementation commitment.

SettingsRepository loads/writes/deletes overrides with parameterized SQL, the current database connection boundary, short transactions and stale-write checks. It cannot decide defaults, behavior, visibility, secret handling or localization. It returns classified persistence/conflict failures, not raw values/errors suitable for logs.

Definition provider is pure/static module composition. Startup provider is a narrow composition input, not a new provider framework. Session overrides are bounded service-owned memory, not a second mutable configuration store. Shared feature consumers receive Settings through injection; specialized domain eligibility still belongs to their services.

Search result E15 supports NEW later shared service/repository/definitions; E01-E04 support REUSE for composition/connections/transactions. No existing generic service is replaced and no code is created now.

## Bootstrap / Environment Configuration Boundary

FACT E01-E03/E07/E14: current startup --database and explicit project root, LOCALAPPDATA readers, ProgramFiles for AHK and gateway-created child environment exist. Doc15's F7HUB_LOG_LEVEL/F7HUB_DATA_DIR/F7HUB_ENVIRONMENT are naming examples, not implemented general override readers.

RECOMMENDATION: resolve logging, installation root, database location and approved runtime discovery before composing database-backed Settings. Inject the resolved immutable startup configuration where needed. Validate allowed path purpose, absolute/relative interpretation, containment, access and executable trust at the owning path/gateway boundary. Existing deployed-path wiring remains future distribution work; no new configuration file, variable reader or executable selector is authorized here.

Bootstrap configuration is user-visible diagnostically where safe but not an ordinary Settings GUI field. Do not relocate databases/data by resetting a path. A later distribution slice may select installed defaults using current path infrastructure without requiring a settings table to open itself.

No environment variable becomes a credential vault. Inherited process variables do not replace the gateway's controlled child environment. QT_QPA_PLATFORM and test environment injection affect the validation environment only; they cannot configure away the root WINDOWS_NATIVE evidence gate. Codex Cloud setup is DEFERRED and outside 0D.

## Caching Decision

RECOMMENDATION: keep a small immutable effective snapshot owned by SettingsService, loaded during composition and replaced after successful changes. This is coherence/operation-binding support rather than a theoretical performance cache. Do not read SQL during every GUI repaint or let each module keep independent mutable defaults/overrides.

Snapshot has an opaque local revision plus safe source/diagnostic metadata. A change recomputes affected keys/cross-field groups and atomically replaces the service snapshot before notifying consumers. Async operations capture their relevant values/revision at start. A runtime/session change uses the same validation/recompute path without a false durable-save claim.

One process owns this snapshot. Other processes receive only approved projections or use their established local configuration. No distributed cache invalidation, file watch, shared mutable map or polling loop. Stale drafts are detected against repository state at save; new operation reads must refresh when cross-process changes are detected. Supporting simultaneous independent F7Hub writers requires the explicit consistency design described next, not a claim that local revision alone protects SQLite.

## Change Propagation

RECOMMENDATION: targeted SettingsService subscribers receive changed-key/group identifiers and a new immutable snapshot/revision after successful persistence and recompute. A presentation adapter may translate the notification into Qt signals on the GUI thread. Reuse MochiService's owned subscribe/unsubscribe and gateway signal patterns (E11/E12) as precedents; do not couple shared Settings to the Mochi runtime.

Consumer failure does not undo an already committed value by pretending the save never occurred. Isolate observer failures, expose desired versus applied state, keep the last safe applied value where appropriate, and provide bounded explicit retry/restart. Features acknowledge activation when needed. An operation already in progress continues with its start snapshot unless its separately approved safety/cancellation contract requires another behavior.

NEXT_OPERATION consumers read the snapshot at the next operation boundary. RESTART_REQUIRED consumers retain applied values until their named restart boundary. No global event bus, automatic generic remediation, or notification before commit. Transient notification is not a durable audit/application event.

## Immediate / Next-Operation / Restart-Required Semantics

| Behavior | Recommended consumer rule | Examples / limitation |
| --- | --- | --- |
| IMMEDIATE | Apply safely after commit; UI adapter on GUI thread; record activation failure separately | Future theme or permitted display option only after actual live-update support is tested |
| NEXT_OPERATION | New work binds current revision; active work retains start values | Future diagnostic deadline or retention-cleanup schedule input; changing duration does not purge records |
| RESTART_REQUIRED | Persist desired value, show applied value and pending restart target; no automatic restart | Startup-only module configuration; language until live localization is designed |
| RUNTIME COMMAND | Existing use-case effects with truthful outcomes; not preference Apply | Mochi Hide/Pause/Exit; command success/uncertainty stays in its own protocol |

A definition names the target: whole F7Hub process, standalone Mochi renderer or another approved consumer. "Restart required" is not permission to restart it. Pending status clears only when the consumer demonstrably starts/applies the desired revision; switching back to the currently applied value cancels an unnecessary pending restart.

Do not persist current playback/attachment/selection as a restart preference. Current Mochi JSON fields are read at renderer startup; no live opacity/timing delivery is claimed.

## Transaction and Draft Semantics

RECOMMENDATION: one consistent draft + explicit Apply/Cancel model for future persistent Settings, with one atomic save for an explicit coherent group/section. Preview is draft-only unless a later feature supplies a safe reversible preview contract; it must restore the prior applied view on Cancel without changing stored values.

Load values/source/revision into an editable draft. Apply validates every changed key and relevant cross-field prospective values, confirms sensitive changes, checks stale state, writes/deletes overrides in one short transaction, then recomputes snapshot and notifies. Failure at validation/conflict/persistence rolls back all group writes, preserves the complete draft and field feedback, and emits no success/change notification. Unrelated valid edits remain in the draft; users may explicitly submit a smaller coherent group rather than silently getting half a section saved.

No transaction waits on IPC, PowerShell, network or a Qt callback. For mixed immediate/restart keys, persist the group atomically; immediate eligible consumers apply after commit while restart keys remain desired/pending. Runtime-only actions remain separately labeled commands/session overrides and do not pretend to be part of a durable transaction.

No-op Apply changes no revision/row or notification. Reset uses the same atomic service path. Cancelling/closing a draft does not undo an already committed Apply or cancel unrelated feature operations.

## Concurrency / Stale-Write Semantics

RECOMMENDATION: one modeless Settings editor per F7Hub process, following current MainWindow dialog lifetime precedent. This prevents duplicate local editors but is not a cross-process database lock.

At load, capture a repository-backed expected-state token for the edited group. At Apply, compare expected rows/revision inside the same transaction as the write, including absent-key insert/delete cases. On mismatch return a classified conflict, preserve the user's draft, show changed keys/source metadata and permit explicit reload/reapply. No blind last-writer-wins or timestamp-only assumption. Exact revision column/token mechanism is DESIGN NEXT in the implementation slice; no SQL/migration is specified here.

Multiple F7Hub processes targeting one DB can exist in principle; NOT VERIFIED as a supported preference-sharing mode. Any shared implementation must either enforce the reviewed single-writer deployment or provide repository CAS plus refresh before new-operation reads when another writer changes values. An in-memory revision alone cannot protect concurrent persistent writes. Ordinary AHK/Mochi processes remain nonwriters of shared overrides and cannot create a second authority.

Async operations retain immutable start snapshots, so dialog changes do not retarget a running diagnostic/case or mutate worker inputs. Parent/dialog closure removes subscriptions, not application-owned service connections.

## Security-Sensitive Settings

RECOMMENDATION: privacy, external integration enablement, AI/context access, persistent clipboard capture, diagnostic resource limits and verbose logging require conservative definitions, restricted source admission, safe error feedback and explicit intent where the affected feature requires it.

Collection/sharing escalation needs an owning-service confirmation/consent workflow and independent authorization/capability checks; a saved bool is not provider permission or a lifetime grant. Invalid/unavailable sensitive configuration disables the optional effect. A UI-disabled control is not sufficient enforcement. Imports/backup restoration cannot manufacture fresh consent or authority in another profile.

Diagnostic preferences can only request supported behavior within reviewed registry/policy ceilings; they cannot increase time/output bounds, disable cleanup, substitute runtime or turn collection into remediation. Verbosity cannot authorize secret/raw-customer logging. Changing optional integration availability cannot request broad tenant permissions automatically.

Sensitive change evidence records safe key/scope/outcome/context/restart metadata when meaningful. If durable audit is required for a feature, that feature cannot activate the sensitive setting until its reviewed evidence path exists. 0D does not invent a generic audit store to satisfy that obligation.

## Secrets Boundary

Ordinary Settings must exclude passwords, API keys, bearer/refresh tokens, private keys, recovery codes, authentication cookies/session secrets, Microsoft 365 credentials and HaloPSA/NinjaRMM/Keeper credentials. They also stay out of config examples/files, SQLite preferences, logs, Clipboard history, Case Journal, Analytics and Mochi context under approved boundaries.

RECOMMENDATION: a normal configuration value may eventually contain a purpose-bound opaque non-secret reference only if a reviewed credential/integration architecture establishes that the identifier itself is safe and cannot grant access by possession. The owning secure mechanism validates the reference/permissions and retrieves secrets transiently; Settings never resolves/logs/exports secret material. Do not assume every path/provider label is non-sensitive.

NOT VERIFIED: the actual future secret-management mechanism, provider, authentication and storage implementation. No vault, broker API, .env store, environment-secret convention or secret-reference schema is created/selected by 0D. A future credential requirement returns to the security/integration owner for explicit review; existing cosmetic JSON flags are not approval.

## Privacy Settings Boundary

RECOMMENDATION: optional automatic capture, persistence, context sharing and external AI transmission use conservative off defaults until their feature plan defines eligibility, exclusions, retention, user intent and enforcement. Manual local technician workflows remain usable when optional features are disabled/unavailable. Employer/customer policy is NOT VERIFIED, not inferred from a developer preference.

A capture preference controls a permitted feature; secret exclusion is an invariant and cannot be exposed as an "off" option. Secret-pattern detection can supplement filtering but cannot certify content safe. Redaction before storage/export/context belongs to the source and outbound service boundaries, not merely display masking.

Clipboard retention does not delete promoted Ticket/Case/Knowledge evidence. Analytics aggregates have no automatic exemption from deletion/privacy policy. Mochi receives only approved minimal safe projections; enabling a context source does not mean unrestricted history, screenshots, raw diagnostics, window titles or all business records. A future provider request still requires preview and explicit Send under its own contract.

No privacy feature or exact retention duration is implemented/approved here.

## Feature Flag Boundary

RECOMMENDATION: distinguish optional feature presentation/preference from discovered capability, provider permission, execution authorization and security invariants. Flags may hide/show UI or disable a permitted workflow. They cannot make an unavailable feature implemented or enable arbitrary PowerShell, elevation, unregistered scripts, bypassed validation, unrestricted IPC/filesystem access, automatic AI execution, secret disclosure or unsafe customer-data export.

Developer/test switches remain explicit deployment/testing configuration, not hidden production user preferences. Unknown flags are inert. Admitting a future flag in a definition requires one owner, safe default and actual feature enforcement. Existing Mochi unsupported flags remain incapable of enabling capture/integration; changing their JSON never expands the current runtime contract.

## Cross-Language Settings Delivery

| Consumer | Recommended source/boundary | Compatibility / limitation |
| --- | --- | --- |
| Python feature services | Inject validated typed Settings snapshot/access boundary | No direct feature SQL/config reads for shared keys; bootstrap exception explicit |
| PowerShell | Approved operation-specific typed parameters from owning Python service when separately supported; current deadline remains gateway input | Scripts do not read shared Settings DB; current three operations remain parameterless |
| AHK / AltF7Hub | Keep guide-local appearance INI and static host behavior; future shared hotkeys via explicit approved values at owning host boundary | No business Settings authority/SQLite writes; existing show/focus bridge unchanged |
| Standalone Mochi | Current validated read-only local JSON | No F7Hub database/service prerequisite; unknown JSON remains untouched |
| Future integrated Mochi | Minimal mapped effective preference projection from application-owned adapter | Separate reviewed 0B-compatible profile when needed; cosmetic v1 cannot carry undeclared fields |

Configuration documents are not automatically IPC messages. No universal transport/profile is designed in 0D. A new actual process projection must consume approved 0B identity/version/error/correlation/missing/null semantics, closed field validation, size bounds and trust rules, plus owner-specific allowlisted payload. Do not fetch remote schemas or treat schema validity/producer identity as permission.

Cross-process activation uses desired/applied revision acknowledgment where the feature needs it. A lost response is unconfirmed; it does not prove cancellation or permit automatic replay. Settings must not enlarge existing v1 payloads, reuse attach session IDs as USER scope, or convert protocol safety maxima into editable settings.

## AHK / AltF7Hub Configuration Boundary

RECOMMENDATION: KEEP SUBSYSTEM-LOCAL for existing guide opacity/pinning/sidebar/heading/auto-fit preferences. The guide has a bounded local use case, built-in defaults and lightweight standalone ownership. Centralizing them would add cross-process ownership/conflict/migration work without a demonstrated shared business need. Preserve current file mechanism and host/editor drafts; no INI conversion, reset or imported bytes.

Tracked source shows immediate local appearance update and debounced/save-on-exit behavior; this is distinct from the proposed shared draft/Apply model. Source tests use a temporary DataRoot for preferences. Their presence does not establish fresh native PASS.

If a later unified appearance feature justifies adapting a particular guide preference, it must select one writer/default authority, define local standalone fallback and update/restart behavior, address unknown-key handling and resolve the documented bounds discrepancy. Until then no mirrored central key silently overrides GuideCore. Topic identity, formatting, shortcuts and current selection stay with their owners.

Only the protected INI pathname was observed through ordinary Git commands. Its bytes/content/metadata are NOT VERIFIED by design.

## PowerShell Configuration Boundary

FACT E05/E06: registry timeout is passed explicitly by PowerShellService to PowerShellGateway; the child script reads no generic Settings database. Gateway's F7HUB_MODULE_ROOT/F7HUB_DIAGNOSTIC_PATH are controlled per-execution inputs, not user environment overrides. The literal approval policy, trusted runtime, digest, standard-user requirement, bounded output and cleanup remain outside Settings.

RECOMMENDATION: a future diagnostics timeout preference may reduce an operation deadline only under a separately reviewed service/gateway change. Effective requested deadline must remain positive and no greater than the current operation's registered timeout and literal policy ceiling. Do not patch registry rows or introduce parameter support to realize this recommendation during planning.

Future supported collection parameters are validated by the owning service and by the PowerShell parameter boundary; no command fragments, Invoke-Expression, arbitrary executable path or global Settings reader. Script-definition semantics, authorization and safety caps remain reviewed owner contracts. A settings change applies to the next operation; active run retains start values and produces its truthful execution/collection result.

## Mochi Configuration Boundary

RECOMMENDATION: preserve the current standalone JSON loader/defaults and runtime control distinction. Read-only file ownership means unknown values survive on disk, not that they become effective values or that future writers may discard them safely. Existing app.enabled true enables the local pet only, never capture/AI/business access.

Current JSON pet opacity/topmost and animation rows/timing are startup-local configuration. Current visibility, pause, greeting consumption, manual-exit suppression, attachment/session/controller IDs and frame/animation playback are runtime facts. No speech/voice/context feature is proven. The Settings-named control dialog remains a runtime command view.

A future F7Hub-owned preference such as integrated speech/assistant availability may use central SQLite while standalone cosmetics remain local. For a specifically approved mapped cosmetic preference, choose a clear mode: standalone uses its JSON; an attached integrated session uses an explicitly supplied central projection for only admitted fields, with effective source visible and a documented disconnect/restart fallback. Do not merge competing writers or rewrite settings.json. Current IPC has no such projection and is unchanged.

Standalone defaults must remain safe when F7Hub is absent/offline. Startup-only changes show renderer restart requirements; no automatic renderer shutdown/relaunch or unsupported live opacity/timing update. Installed log-path adaptation belongs to a future distribution slice, preserving today's logger and source bytes here.

## DynamicHub Settings vs Runtime-State Boundary

FACT F-A/E15: approved 0A makes DynamicHub interactive troubleshooting workflow coordination through approved owning services/gateways. No tracked current DynamicHub implementation was found. External prototypes/backups were not inspected/restored/imported.

RECOMMENDATION: potential user preferences may eventually control permitted presentation, prompt density or explicitly designed workflow-display defaults. Exact keys/defaults are NOT VERIFIED and DEFER UNTIL FEATURE PLAN. Such choices cannot redefine diagnostic meaning, sequencing authority, execution permission or domain identity.

Active workflow position, chosen case/context, pending action, run/result references and session progress are runtime/workflow state. If a future resumable Case workflow needs durable storage, its feature service and reviewed domain persistence own it; it is not a Settings override. Current Ticket/Company/Contact selection likewise remains context rather than Settings. Restoration must revalidate identity/freshness/authorization and cannot replay stale actions.

## Hotkey Configuration Boundary

RECOMMENDATION: preserve stable action identity separately from user binding, host registration and runtime pressed/held state. Current F7/Alt+F7 and scoped topic/editor shortcuts remain static/local. Not every hard-coded shortcut, reserved topic letter or key-repeat threshold deserves a setting.

For an approved future configurable global action, centrally owned durable binding can use SQLite and a purpose-specific canonical binding validator. AHK remains registration/input owner. Validate duplicates, supported combinations, reserved OS/application bindings and action scope before activation; native registration conflict remains possible even after static validation.

A persisted desired binding is not proof the host registered it. Future Apply cannot hold a DB transaction across IPC/OS registration. After commit, host activation must report applied/failed/uncertain state; retain the last safe binding where possible and preserve explicit repair feedback without reporting the new binding active. Exact staging/compensation/native recovery is DESIGN NEXT for that feature. No hotkey registry/service/transport is created here.

## Bilingual / Localization Model

RECOMMENDATION: one language-neutral machine key and locale-neutral canonical value. Definition metadata references display_name/description/section/search-keyword/validation message identities; presentation resources supply English/French text. Enum display labels are localized independently of stable enum tokens. Persist a number/bool/token, not "30 jours" or translated setting names.

Service returns safe key/error-category/structured parameters; GUI localizes feedback. Translation cannot change bounds, default, scope, permissions or taxonomy. Setting search uses localized descriptive metadata plus stable key, without indexing secrets/raw sensitive values.

FACT E12/E14: current Settings menu and Mochi controls have English source labels; a complete shared localization catalog/runtime language switch was not found. Exact resource tooling and reload implementation are DESIGN NEXT; no new localization dependency or French duplicate key is proposed. Until live switching is implemented and validated, language changes are conservatively restart-required.

## Settings GUI Architecture

RECOMMENDATION: presentation edits a service-provided draft with explicit Apply/Cancel, field feedback, source/default/effective information and desired/applied/restart indicators. It does not read SQLite/config files, construct shell commands, own domain validation or invent defaults. One modeless editor per process, preserving draft/lifetime/subscription ownership. Sections/search are metadata-driven organization, not final widget/screens.

Reset setting/section/eligible user preferences uses previewed allowlists and the same service validation/transaction path. Sensitive values receive clear restricted controls and required intent workflow; secret-entry controls are not part of ordinary Settings. Configuration held by CLI/environment can be shown read-only with safe source context.

The planned General/Appearance/Clipboard/Tags & Taxonomy/Diagnostics/PowerShell/Automation/Statistical Analytics/Mochi/Privacy & Security/Advanced groupings are conceptual. Taxonomy management may be reached there but still calls its domain service and never stores catalogs in Settings. Mochi runtime buttons remain separately identified commands, with their existing lifetime/uncertainty behavior.

No final layout labels, PySide6 screens, widget classes or cosmetic design is committed.

## Module Settings Inventory

All rows are RECOMMENDATION candidates; status CORE/LIKELY/FUTURE/REJECTED/NEEDS REVIEW is planning relevance, not approval/implementation. Proposed exact keys are illustrative names for owner review. "Deferred" default means the feature must choose and validate it before admitting the definition; it is not an executable default. USER identifies the initial local preference set. Restart/update promises remain conditional on actual consumer implementation.

| Area / candidate key | Purpose / owner | Type | Default candidate | Scope | Persistence recommendation | Sensitive? | Update behavior | Restart? | Status | Evidence / dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| General / general.language | Display language; localization owner | enum | en proposed; supported EN/FR resources to be designed | USER | SQLite | No | Restart until live localization verified | F7Hub initially | CORE | E12/E14; localization plan |
| Appearance / appearance.theme | Global appearance; GUI owner | enum | Preserve current appearance; supported choices deferred | USER | SQLite | No | Immediate only after safe theme consumer exists | Conditional | LIKELY | E12/E14; GUI plan |
| Clipboard / clipboard.auto_capture_enabled | Optional automatic capture; Clipboard owner | boolean | false proposed | USER | SQLite | Yes | Next capture; stop/teardown contract owner-defined | Conditional | FUTURE | F-A/F-C; Clipboard architecture |
| Clipboard / clipboard.persistence_enabled | Optional durable history; Clipboard owner | boolean | false proposed | USER | SQLite | Yes | Next eligible capture; no silent migration of history | Conditional | FUTURE | F-A privacy/offline boundary |
| Clipboard / clipboard.retention_days | Temporary item lifetime input; Clipboard owner | duration, days | Deferred; no operational TTL selected | USER | SQLite | Yes | Next authorized cleanup operation | No by proposed operation snapshot | FUTURE | F-C retention; Clipboard domain plan |
| Clipboard / clipboard.secret_detection_enabled | Proposed bypass of mandatory secret exclusion | boolean | No default admitted | None | NOT A SETTING | Yes | No consumer | N/A | REJECTED | Security invariant; a detector feature cannot weaken exclusion |
| Tags & Taxonomy / tags.show_suggestions | Optional presentation of eligible suggestions; taxonomy/module owner | boolean | false until suggestion feature exists | USER | SQLite | Some | Next view/request | No if consumer supports | LIKELY | F-C Settings inputs |
| Tags & Taxonomy / tags.ai_suggestions_enabled | Optional advisory suggestion presentation; taxonomy/AI owner | boolean | false proposed | USER | SQLite | Yes | Next permitted request; explicit Send independent | Conditional | FUTURE | F-C; provider/privacy review |
| Tags & Taxonomy / tags.entity_type_meaning | User rewrite of semantic identity | string | No default admitted | None | NOT A SETTING | N/A | No consumer | N/A | REJECTED | 0C owns meaning; catalog editing separate |
| Diagnostics / diagnostics.default_timeout_seconds | Requested operation deadline; Diagnostics owner | duration, seconds | 60 candidate for existing operations; cannot exceed approved per-operation registration/ceiling | USER | SQLite | Yes, bounded operational input | Next run only | No | NEEDS REVIEW | E05/E06; no current preference support |
| Diagnostics / diagnostics.history_retention_days | Future durable-history lifetime input; Diagnostics owner | duration, days | Deferred | USER | SQLite | Yes | Next explicit eligible cleanup | Conditional | FUTURE | Current results memory-only; feature plan |
| Diagnostics / diagnostics.confirm_before_run | Optional additional confirmation | boolean | true proposal for later UI; mandatory confirmations cannot be disabled | USER | SQLite | Yes | Next request | No | NEEDS REVIEW | Execution/technician-intent owner |
| PowerShell / powershell.preferred_runtime | Arbitrary runtime selection | string/path | No default admitted | None | NOT A SETTING | Yes | No consumer | N/A | REJECTED | E06 trusted runtime; different runtime requires review |
| PowerShell / powershell.show_raw_output | Future permitted diagnostic display detail; PowerShell/GUI owner | boolean | false proposal | USER | SQLite | Yes | Next result view; eligibility/redaction independent | Conditional | NEEDS REVIEW | E05/E06; safe-output presentation plan |
| PowerShell / powershell.allow_unregistered_scripts | Execution-policy bypass | boolean | No default admitted | None | NOT A SETTING | Yes | No consumer | N/A | REJECTED | F-A/F-B, E05/E06 |
| Automation / automation.show_suggestions | Optional approved action suggestions; Automation owner | boolean | false proposal | USER | SQLite | Some | Next view | Conditional | FUTURE | F-A/F-B; action/advisory plan |
| Automation / automation.auto_execute_ai | AI-generated arbitrary automatic action | boolean | No default admitted | None | NOT A SETTING | Yes | No consumer | N/A | REJECTED | AI is not execution authority |
| Statistical Analytics / analytics.default_period_days | Initial analysis window; Analytics owner | duration, days | Deferred; metric grain/period owner decides | USER | SQLite | No, eligible facts independently sensitive | Next query | No | FUTURE | F-C Analytics boundary; no metrics implemented here |
| Statistical Analytics / analytics.include_personal_identifiers | Expanded identifiers in analytics | boolean | false conservative candidate | USER | SQLite | Yes | Next eligible analysis/export with independent policy | Conditional | NEEDS REVIEW | Employer policy NOT VERIFIED; source/Analytics owners |
| Mochi / mochi.enabled | Future F7Hub assistant availability preference; Mochi application owner | boolean | Deferred; preserve standalone app.enabled=true for existing local pet | USER | SQLite only for separately defined integrated meaning | Some | Next approved start; does not stop active pet automatically | Consumer-defined | NEEDS REVIEW | E10-E12; avoid two owners of same flag |
| Mochi / mochi.speech_enabled | Future speech choice; Mochi owner | boolean | false proposed | USER | SQLite | Some | Consumer behavior deferred | Conditional | FUTURE | Speech unimplemented; Mochi feature plan |
| Mochi / local pet.opacity | Current standalone cosmetic preference; Mochi core | float | 1.0 current local default, not new global key | Local installation | CONFIG FILE | No | Next renderer start | Renderer | CORE | E10/E13; 0.1-1.0 finite bounds |
| Mochi / local pet.always_on_top | Current standalone window preference; Mochi core | boolean | true current local default | Local installation | CONFIG FILE | No | Next renderer start | Renderer | CORE | E10 |
| Mochi / local animation.frame_interval_ms | Local animation timing; Mochi core | duration, ms | 120 current local default | Local installation | CONFIG FILE | No | Next renderer start | Renderer | CORE | E10; integer 20-2000 |
| Mochi / mochi.initial_visibility | Distinct potential startup preference; Mochi owner | boolean | Deferred; current runtime starts visible | USER | SQLite only if feature justified | No | Next approved start | Renderer or next start | FUTURE | Current visibility is runtime fact E11 |
| Privacy & Security / mochi.context_clipboard_enabled | Future bounded context source preference; source/Mochi service | boolean | false proposed | USER | SQLite | Yes | Next explicit eligible context request | Conditional | FUTURE | F-A/F-B/F-C; no unrestricted history |
| Privacy & Security / privacy.ai_data_sharing_enabled | Optional provider workflow availability; integration owner | boolean | false proposed | USER | SQLite | Yes | Next preview/Send; not blanket consent | Conditional | FUTURE | Provider/policy/secret mechanism NOT VERIFIED |
| Privacy & Security / privacy.allow_secret_export | Secret-disclosure bypass | boolean | No default admitted | None | NOT A SETTING | Yes | No consumer | N/A | REJECTED | Root/F-A/F-C invariant |
| Advanced / deployment.database_path | Startup database input; composition/path owner | validated path | Existing development default or explicit --database; installed default deferred | APPLICATION | ENVIRONMENT / STARTUP | Path-sensitive | Next F7Hub start | F7Hub | CORE | E01/E02; not ordinary editable preference |
| Advanced / logging.level | Restricted verbosity configuration; logging owner | enum | INFO current baseline | APPLICATION initially | ENVIRONMENT / STARTUP; no new reader selected | Yes | Startup initially | F7Hub initially | NEEDS REVIEW | E03; optional UI use case later |
| Advanced / shortcuts.open_guide | Potential configurable stable action binding; AHK/application owner | validated binding | Alt+F7 current binding; no change recommended | USER | SQLite if approved configurable feature | No, action authority independent | After native activation ACK; failure visible | Host-specific/deferred | FUTURE | E07; hotkey feature plan |
| Advanced / altf7hub.appearance | Existing local opacity/pin/sidebar/heading/auto-fit family, not a new global key | bounded local scalars | Source defaults E08; range discrepancy with Doc11 unresolved | Guide data root | SUBSYSTEM-LOCAL PREFERENCE | No | Existing local immediate/debounced save | No ordinarily | CORE | E08/E14; KEEP SUBSYSTEM-LOCAL |
| Advanced / dynamic_hub.workflow_position | Attempt to store active workflow in generic Settings | No Settings type | No default admitted | Workflow/session | RUNTIME ONLY; later Case domain if justified | Potentially | Owner runtime flow | N/A | REJECTED | F-A; concrete DynamicHub preferences deferred |

## Database Impact Assessment

No operational database was opened; no SQLite writes, schema changes, default seeds or migration-number reservation occurred.

| Concept | Current mechanism | Classification | Potential future persistence / reason | Migration required later? | Status |
| --- | --- | --- | --- | --- | --- |
| Shared durable user overrides | No migrated Settings structure; E04/E15 | NEW | SQLite overrides for central transactional ownership; not application_metadata | Yes if approved implementation introduces structure; final shape deferred | RECOMMENDATION |
| Setting definitions/defaults | Proposed canonical concept, no shared implementation | NOT NEEDED in SQLite | Versioned pure source definitions; DB does not define behavior | No definition-table migration justified | RECOMMENDATION |
| Existing connection/transactions/backup | database infrastructure and feature repository patterns | REUSE | Existing configured SQLite/short atomic units/backup service | No for reuse; test later preference backup semantics | FACT current, proposed reuse |
| application_metadata/schema_migrations | Core metadata/version history | NOT NEEDED for Settings | Preserve current responsibilities; not a preference or key-evolution dumping ground | No Settings repurposing | FACT / RECOMMENDATION |
| scripts timeout/visibility/identity | Existing scripts table and literal eligibility | REUSE | Registry remains; future requested deadline separate without identity changes | Not implied by 0D; affected feature reviews exact impact | FACT / RECOMMENDATION |
| Tags/categories/Entity Type meaning | Existing taxonomy and approved 0C | NOT NEEDED for Settings | Existing catalog/domain extension mechanisms | Taxonomy feature decides its own structural changes | RECOMMENDATION |
| Generic durable sensitive-change audit | No generic audit repository/table found | NOT VERIFIED | Feature-required meaningful safe evidence path, not technical logs | Deferred only if a real reviewed durable use case requires it | NOT VERIFIED |
| Stale-write token | Existing updated_at-style feature guards; no Settings persistence yet | EXTEND | Reuse conflict principle; exact CAS/revision design later | May accompany future override structure; no final columns here | RECOMMENDATION |
| Mochi/guide local cosmetics | Read-only JSON / optional local INI | NOT NEEDED in core DB | Preserve standalone/subsystem boundaries | No centralization migration now | RECOMMENDATION |
| Workflow/selected-context/pet state | Current memory or future feature state | NOT NEEDED for Settings | Runtime/Case/workflow-owned persistence if justified | Feature owner, not generic Settings | RECOMMENDATION |
| Secrets / approved reference | Secure mechanism unresolved | NOT VERIFIED | Secrets excluded; non-secret reference conditional on future reviewed owner | No credential schema in 0D | NOT VERIFIED |

Canonical service/navigation/configuration prose describes intended architecture. Doc09's application_metadata is an actual migrated object with explicit metadata purpose; broader schema examples such as tool state/events do not prove current tables or Settings implementation. Future structural change must undergo a separate scoped design, migration/constraint review and isolated integrity/foreign-key checks.

## Migration / Setting-Key Evolution

RECOMMENDATION: distinguish physical schema migration from key/value evolution. The former uses immutable migration history and checksums; the latter maps specific meaning/types/defaults/overrides under an explicit versioned owner decision.

| Evolution | Required behavior |
| --- | --- |
| New key | Add validated definition/default; absent override inherits without seeding |
| Changed default | Inherited users receive new desired default; explicit overrides remain; sensitive effects still require valid intent/consent |
| Rename | Explicit old -> new compatibility mapping/conversion; if both exist, detect conflict rather than silently lose intent |
| Deprecation | Read under documented compatibility window; reject new legacy writes and show replacement |
| Removal | Stop consumer access; retain inert bounded old data until authorized cleanup; never reuse key for unrelated meaning |
| Type/unit/range change | Validate against new definition; explicit reviewed conversion, preserve unsupported original for repair, safe fallback/fail closed |
| Enum change | Compatibility assessment for closed tokens and any real cross-process profile; no automatic 0B-compatible claim |

Evolution runs transactionally where persistent conversion is justified, with backups/rollback and unrelated-key preservation. Unknown fields cannot authorize behavior. Bulk deletion/export/import/cloud sync is deferred and never incidental upgrade cleanup. No separate universal Settings schema-version layer is necessary now; key mapping design is scoped to actual evolution. No migrations are implemented.

## Audit / Logging Requirements

FACT E03/E04/E15: bounded application/Mochi technical loggers and feature-owned Ticket activity exist; no generic Settings audit repository or migrated generic audit ledger was found. A transient notification and a log line do not prove durable meaningful audit.

RECOMMENDATION: cosmetic theme/display changes ordinarily need no separate durable ledger. Sensitive changes need the evidence specified by their owning use case: safe setting key, scope, UTC timestamp, validated actor/application context where meaningful, change outcome and pending restart/activation state. Do not invent a user identity because Contacts exist.

Never log raw old/new sensitive values, secrets/references that expose credentials, rejected payloads, paths/customer content, clipboard text or full config snapshots. Technical logs record safe classified errors and identifiers only. A log-level setting cannot weaken those exclusions.

If a sensitive feature requires durable audit and none is available, the feature slice must design a suitable owner/reuse path and its failure behavior before enabling that key. It may not silently substitute technical logs. No new generic ledger/table/event bus is mandated by 0D.

## Dependency Diagram

RECOMMENDATION diagram: NEW denotes a future component, not implemented infrastructure. Solid arrows are dependency/read/injection direction; activation stays with feature owners. Notification arrows describe runtime flow, not a Settings-to-feature construction/import dependency.

~~~mermaid
flowchart TD
    Boot["Existing Python bootstrap / composition"]
    Start["Existing startup inputs and path infrastructure"]
    Defs["NEW pure module definition contributions"]
    Compose["NEW static definition composition"]
    GUI["Future Settings presentation / draft"]
    S["NEW SettingsService / typed resolution"]
    Repo["NEW SettingsRepository / overrides only"]
    DB["Existing configured SQLite / future override structure"]
    Session["Proposed explicit session override mechanism"]
    F["Owning feature services"]
    Qt["Targeted observer / Qt presentation adapter"]
    PS["Existing PowerShellService / Gateway"]
    Ops["Approved parameterless operations today"]
    AHK["Existing AHK host / local guide preferences"]
    MJ["Existing standalone Mochi JSON loader"]
    MA["Future explicit Mochi preference adapter"]
    MP["Mochi renderer / reviewed process profile"]
    Boot --> Start
    Boot --> Compose
    Defs --> Compose
    Boot --> S
    GUI --> S
    S --> Compose
    S --> Repo
    Repo --> DB
    S --> Session
    F --> S
    S -. "post-commit changed-key notification" .-> Qt
    F --> PS
    PS --> Ops
    F --> MA
    MA -. "separate approved 0B profile if needed" .-> MP
    MJ --> MP
    Boot --> AHK
~~~

AHK's existing bridge is show/focus only; Boot -> AHK represents current integration composition, not a shared Settings transport. Standalone JSON and a future integrated projection are explicitly different modes/sources, never two implicit simultaneous writer authorities. No companion arrow reaches core SQLite.

## Configuration Precedence Diagram

Only sources admitted by a definition participate. The diagram specializes the single ranked resolution rule into current useful families; it does not grant arbitrary environment preference overrides.

~~~mermaid
flowchart TD
    UD["USER key: validated definition default"]
    UP["Eligible persisted user override"]
    US["Eligible explicit session override"]
    DD["DEPLOYMENT field: built-in path/default"]
    DE["Admitted environment input"]
    DC["Explicit CLI / constructor input"]
    V["Validate admitted sources / type / scope"]
    E["Desired effective value + safe source provenance"]
    A["Applied consumer snapshot or pending restart"]
    I["Security invariants / authorization / capabilities outside ranks"]
    X["Secrets outside ordinary Settings"]
    Fail["Safe classified fallback or fail-closed affected workflow"]
    UD --> UP
    UP --> US
    US --> V
    DD --> DE
    DE --> DC
    DC --> V
    I -. "constrains admissibility and use" .-> V
    X -. "excluded" .-> V
    V -->|"valid eligible highest source"| E
    V -->|"invalid sensitive or required deployment input"| Fail
    V -->|"invalid ordinary source: next valid source"| E
    E --> A
~~~

The USER family omits environment/CLI by default; DEPLOYMENT omits persisted preferences/session overrides. A missing layer simply leaves the next lower admitted source eligible. Secret references are conditional future secure integration inputs, not a secret-value tier.

## Settings Lifecycle Diagram

~~~mermaid
flowchart TD
    Def["Definition + authoritative default"]
    Admit["Validate definition metadata/default"]
    Load["Load only admitted override/startup/session sources"]
    Resolve["Validate and resolve immutable effective snapshot"]
    Use["Consumer uses applied value / operation captures revision"]
    Draft["Editable draft with expected persistent state"]
    Check["Apply: validate complete group / editability / intent"]
    Tx["Short repository transaction / stale check / write or delete"]
    Commit["Durable success"]
    Refresh["Recompute desired snapshot and changed keys"]
    Notify["Notify after success on correct thread"]
    Live["Immediate or next-operation activation"]
    Pending["Restart required: retain applied value; show pending target"]
    Restart["Explicit approved restart / verified activation"]
    Error["Preserve draft + classified field/conflict/save error"]
    Temp["Explicit permitted session change: validate; memory only"]
    Def --> Admit
    Admit --> Load
    Load --> Resolve
    Resolve --> Use
    Use --> Draft
    Draft --> Check
    Check -->|"valid"| Tx
    Check -->|"invalid"| Error
    Tx -->|"failure / stale: rollback"| Error
    Error --> Draft
    Tx --> Commit
    Commit --> Refresh
    Temp --> Refresh
    Refresh --> Notify
    Notify --> Live
    Notify --> Pending
    Live --> Use
    Pending --> Restart
    Restart --> Use
~~~

Post-commit activation failure reports desired/applied mismatch; it is not a pre-commit rollback or completed cancellation. Session changes produce no durable-save claim. Reset uses the same validation/transaction/recompute path and never deletes operational data.

## Planning Depth Classification

| Topic | Depth | Bound / downstream owner |
| --- | --- | --- |
| Ownership, definition/value distinction, semantic/registry/security/secrets exclusions | DECIDE NOW | Stable 0D boundary constrained by 0A/0B/0C |
| SQLite versus startup/local sources, per-key precedence and reset | DECIDE NOW | No final SQL/file/env convention; shared Settings implementation later |
| Minimal types/default ownership, USER/APPLICATION/SESSION meaning | DECIDE NOW | Descriptor admission and safe resolution; no enterprise scope hierarchy |
| Immutable snapshots, post-commit change flow, desired/applied distinction | DECIDE NOW | One service owner, active-operation snapshot and explicit restart target |
| Common transaction/draft/stale-write principles | DECIDE NOW | Exact repository token/revision mechanism DESIGN NEXT |
| SettingsService/Repository API and physical override structure | DESIGN NEXT | Separately reviewed bounded implementation; no migration number now |
| Presentation metadata, Apply/Cancel, search/localization ownership | DECIDE NOW | Final widget/resource design DESIGN NEXT |
| Exact defaults/ranges/key sets for Clipboard/Diagnostics/Analytics/Mochi | DEFER UNTIL FEATURE PLAN | Feature owns semantics/eligibility and proves consumers |
| Privacy consent/evidence, provider references, meaningful durable audit | DEFER UNTIL FEATURE PLAN | Security/source/integration owners; exclusions decided now |
| Hotkey canonical format, native activation/compensation and delivery | DEFER UNTIL FEATURE PLAN | Host/action owner; later WINDOWS_NATIVE validation |
| Specific cross-process config profile/transport | DEFER UNTIL FEATURE PLAN | Reuse 0B; existing contracts unchanged |
| Mochi integrated projection/fallback mode | DEFER UNTIL FEATURE PLAN | Retain standalone loader; no centralization now |
| AltF7Hub bounds documentation discrepancy | DEFER UNTIL FEATURE PLAN | Alt owner follows canonical/source conflict process; no range redefinition here |
| Installed-default/path/logging wiring and packaging | DESIGN NEXT | Existing path infrastructure; distribution composition |
| Actual key rename/type conversion | DEFER UNTIL FEATURE PLAN | Reviewed real evolution/use case before migration |
| SQL indexes, exact serialization columns and revision implementation | DEFER UNTIL IMPLEMENTATION | After approved bounded design; isolated DB validation |
| Performance tuning and notification threading mechanics | DEFER UNTIL IMPLEMENTATION | Validate actual workloads and GUI thread behavior |
| Profiles/import/export/cloud synchronization/plugin discovery/enterprise policy | DEFER UNTIL FEATURE PLAN | No current need or new shared infrastructure |
| DynamicHub concrete preferences/resumable-case state | DEFER UNTIL FEATURE PLAN | Approved 0A workflow authority; external prototypes excluded |
| 0E reconciliation / general Foundation feature readiness | DESIGN NEXT | Separate NOT STARTED Foundation phase after 0D review/approval/integration; requires new task authorization |

## Decision Register

All statuses are candidate recommendations/deferred decisions, never new approvals. Planning depth indicates when the owning detail should be settled, not authorization to execute that phase.

| ID / decision | Options | Recommendation | Evidence | Reason | Consequences | Status | Planning Depth | Downstream owner |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D01 Persistence responsibilities | All SQLite; all files; bounded split | SQLite shared user overrides, startup inputs outside DB, existing companions local | E01-E10, F-A | Transactions/shared writer for central preferences; preserve bootstrap and standalone needs | Future NEW override structure; no consolidation/migration now | RECOMMENDED | DECIDE NOW | Shared Settings / distribution / companion owners |
| D02 Definition authority | SQLite metadata; one monolithic map; module contributions | Pure module definitions, explicit central static composition | E10/E14/E15 | No implemented global registry; local typed defaults are precedent | One admission/default source; no definition table or plugin discovery | RECOMMENDED | DECIDE NOW | Settings / module owners |
| D03 Precedence | Arbitrary env overrides; no overrides; per-key source admission | Ranked eligible sources, USER default/stored/session; deployment default/env/explicit | E01-E03/E06, F-B | Existing CLI/path use, no preference env reader | No arbitrary F7HUB_* expansion; source visibility/reset clear | RECOMMENDED | DECIDE NOW | Composition / Settings |
| D04 Scopes | All five example scopes; enterprise policy; minimum | USER preference set, APPLICATION bootstrap, explicit SESSION; module is namespace | E01/E11, F-A | Actual local use; no multi-user/device settings authority | Shared/multi-user semantics deferred; no Contact FK | RECOMMENDED | DECIDE NOW | Settings / future multi-user owner |
| D05 Typed validation | Untyped JSON; new validation framework; explicit scalars | Existing-style pure typed bounded validators; list/object only for real use | E10/E13, F-B | Current implementation patterns; no new dependency need | Reject bool-as-int/nonfinite/unknown enum; revalidate load | RECOMMENDED | DECIDE NOW | Settings / module definitions |
| D06 Defaults | GUI/service seeds; config file; single descriptor | One authoritative descriptor default; standalone fallback explicitly local | E08/E10/E14 | Prevent drift without rewriting local systems | Missing overrides create no rows; fixture parity later | RECOMMENDED | DECIDE NOW | Definition / companion owners |
| D07 Effective model | Raw stored values; mutable map; typed snapshot | Desired typed/source-aware snapshot plus applied consumer value | E11/E12, plan | Explain delayed activation and corruption safely | Unknown inactive; sensitive invalid fails closed; no silent clamp | RECOMMENDED | DECIDE NOW | Settings / feature consumers |
| D08 Cache | Per-read SQL; module caches; shared snapshot | One small immutable service snapshot with revision | E01/E11, plan | Coherence and operation binding; small workload | Post-success replacement; cross-process refresh separately required | RECOMMENDED | DECIDE NOW | Settings |
| D09 Notifications | Global event bus; polling; targeted observers/Qt adapter | Owned targeted subscribers after commit/recompute | E11/E12 | Existing callback/signal precedent; no global bus evidence | GUI thread adapter; observer failure not false rollback | RECOMMENDED | DECIDE NOW | Settings / GUI / consumers |
| D10 Restart metadata | Assume live; blanket restart; per-key lifecycle | IMMEDIATE/NEXT_OPERATION/RESTART_REQUIRED with target and desired/applied status | E10-E12 | JSON loads at startup; operation snapshots needed | No automatic restart; actual live support tested later | RECOMMENDED | DECIDE NOW | Definition / consumer lifecycle |
| D11 Sensitive settings | Ordinary edit; UI-only guard; service restrictions | Conservative defaults, per-key source/intent/evidence restrictions; invariants outside | F-A/F-B/F-C, E06/E10 | Bool cannot create authority; corrupt config not opt-in | Sensitive features wait for approved consent/audit path | RECOMMENDED | DECIDE NOW | Security / source feature |
| D12 Hotkey storage | Hardcode forever; local/central duplicates; central approved bindings | Future shared binding in SQLite; existing static/local keys retained | E07/E08 | Action identity differs from registration/runtime key state | Native activation/conflict design not chosen now | RECOMMENDED | DECIDE NOW | AHK / action feature |
| D13 Audit strategy | All prefs in ledger; logs as audit; purpose-bound evidence | Routine cosmetic no new audit; meaningful sensitive evidence owner-defined | E03/E04/E15, F-A/F-B | No generic audit store proven; avoid speculative subsystem | Required durability blocks activation until feature evidence exists | RECOMMENDED | DECIDE NOW | Sensitive feature / audit owner |
| D14 Bilingual labels | Translated keys; duplicated definitions; resource metadata | One stable key/token plus localized display/error/search metadata | E12/E14, F-C | Translation must not alter semantics | Resource tooling/live language reload DESIGN NEXT | RECOMMENDED | DECIDE NOW | GUI / localization |
| D15 Module registration | Dynamic plugins; separate module stores; static composition | Module-owned pure contributions composed explicitly | E01/E15 | Modular monolith, no plugin setting requirement | Duplicate definition admission failure; no circular service imports | RECOMMENDED | DECIDE NOW | Composition / module owners |
| D16 GUI save/draft | Immediate-save everywhere; hybrid; draft Apply | Explicit atomic coherent group Apply/Cancel/reset | E12/E14, plan | Recovery and partial-section consistency | Failed save retains draft, no notification; layout deferred | RECOMMENDED | DECIDE NOW | Settings GUI / service |
| D17 Stale writes | Last writer wins; distributed machinery; repository preconditions | One local editor plus transaction-level expected-state comparison | E13 registry management tests | Desktop can still have stale/multiple writers | Exact CAS/revision/token and refresh mechanism later, not final SQL | RECOMMENDED | DECIDE NOW | Settings repository design |
| D18 Bootstrap configuration | DB owns its path; new global file; current composition | Reuse path/CLI/logger initialization before Settings | E01-E03/E07 | Avoid bootstrapping cycle and unnecessary source | Installed default wiring/distribution separate | RECOMMENDED | DECIDE NOW | App/distribution |
| D19 Companion treatment | Centralize all; ignore integration; preserve local plus explicit future adapter | Guide local; Mochi standalone JSON; shared projections only by approved use case | E08-E12, F-B | No business-settings sharing requirement today | No file rewrite or v1 payload expansion; per-field authority explicit later | RECOMMENDED | DECIDE NOW | Alt/Mochi integration |
| D20 Security/secret scope | Ordinary flags/values; new vault; exclusion + secure owner | Exclude secrets/invariants; conditional reviewed non-secret references only | F-A/F-B/F-C | No approved credential implementation | Actual provider/vault/schema outside 0D | RECOMMENDED | DECIDE NOW | Security / integration |
| D21 Exact feature keys/defaults/retention | Adopt every plan example; bounded candidates | Feature plans decide exact supported definitions/defaults before admission | F-C/E05/E10, inventory | No evidence for many proposed features; duration doesn't define deletion | Stable shared boundary without speculative active keys | DEFERRED | DEFER UNTIL FEATURE PLAN | Clipboard / Diagnostics / Analytics / Mochi |
| D22 Key evolution | Silent rename/clamp; universal version layer; explicit real mappings | Stable keys, reviewed forward conversion and unknown preservation | E04/E08/E10, F-B | Prevent lost intent/drift, protect existing file compatibility | No version framework/migration number now | RECOMMENDED | DECIDE NOW | Setting owner / migration owner |
| D23 Alt bounds reconciliation | Change source; change canonical doc; leave source evidence explicit | Preserve both, record discrepancy; owner resolves in scoped follow-up | E08/E14 | 60-100 source versus 70-100 Doc11; no 0D redesign authority | No mapped global range until resolved | DEFERRED | DEFER UNTIL FEATURE PLAN | AltF7Hub/canonical AHK owner |
| D24 Secret mechanism details | Provider broker/local vault/OS secure store | No mechanism selected; require actual approved security/integration design | F-A/E09/E15 | Provider/auth/policy unresolved | No credential implementation commitment | NOT_VERIFIED | DEFER UNTIL FEATURE PLAN | Security / provider owner |

## Requires User Decision

NONE blocking the bounded Settings architecture recommendation.

The recommended choices require independent Phase 0D architecture review and USER approval before becoming authoritative; this is distinct from an unresolved choice that prevents writing a stable candidate. Exact feature defaults, secret mechanism, physical SQL/CAS, native hotkey activation and companion projection details remain with their later owners and do not grant implementation authority.

If review rejects the recommended active-database preference boundary or single-local-profile assumption, revise D01/D04/D17 together before approval; do not introduce an unreviewed second preference store. The Alt opacity discrepancy constrains a future shared adapter, not the current KEEP SUBSYSTEM-LOCAL decision.

## Risk Register

Likelihood is an architectural estimate, not measured operational probability. UNKNOWN is used where repository evidence does not justify an estimate. Residual risks remain pending future implementation validation.

| ID / risk | Trigger / cause | Likelihood | Impact | Mitigation | Residual risk | Owner / Downstream Phase | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R01 Duplicate sources | Same key mirrored in SQLite, JSON, INI and environment | UNKNOWN | Conflicting behavior and lost edits | Per-key source admission/single writer; keep local sources distinct | Future adapter mapping can still drift | Settings / integration feature | OPEN, architectural mitigation proposed |
| R02 Conflicting defaults | GUI/service/config seed defines independent baseline | UNKNOWN | Non-deterministic reset/load | One descriptor default, named defensive fallback, parity fixtures | Legacy local defaults need explicit mapping tests | Settings / companion owner | OPEN |
| R03 Business-logic coupling | Settings changes domain meaning or deletion eligibility | UNKNOWN | Corrupt workflow/semantic truth | Taxonomy/domain/retention authority outside Settings | Consumer misuse needs future tests/review | 0C / feature services | OPEN |
| R04 Unsafe user overrides | Paths/runtime/flags treated as execution permission | UNKNOWN | Arbitrary execution/elevation/disclosure | Invariants outside ranks; typed inputs; gateway rechecks | Actual use-case enforcement must be tested | Security / execution owner | OPEN |
| R05 Secret leakage | Sensitive config values/reference/payload logged/exported | UNKNOWN | Credential/customer disclosure | Secrets excluded, safe metadata only, purpose-bound future broker | Policy/provider/reference secrecy NOT VERIFIED | Security / integration | OPEN |
| R06 Stale snapshot | Module mutable cache or cross-process save goes unseen | UNKNOWN | Wrong new-operation behavior | One immutable service owner; start snapshots; CAS plus refresh design | Concurrent-process refresh not implemented | Settings implementation | OPEN |
| R07 Cross-process inconsistency | Lost config ACK, incompatible payload, competing standalone mode | UNKNOWN | Desired/applied mismatch or unsafe replay | Explicit mode/profile, 0B validation, acknowledge activation; no replay | No current preference projection exists | AHK/Mochi feature / 0B | OPEN |
| R08 Invalid persisted values | Manual edit/corruption/type/range change | UNKNOWN | Startup failure or unsafe default | Revalidate load; repair visibility; ordinary fallback; sensitive fail closed | UI/repair path unimplemented | Settings implementation | OPEN |
| R09 Settings explosion | Expose every constant or speculative feature | UNKNOWN | Support burden and policy confusion | Admission needs use case/owner/consumer; small scalar model | Feature plans must prune candidate matrix | Feature planners / 0D owner | OPEN |
| R10 Key/schema drift | Silent rename/default/range conversion or released migration edit | UNKNOWN | Lost intent/integrity mismatch | Stable keys, explicit forward mappings, backup/rollback, immutable history | Exact future conversion needs review | Settings / migration owner | OPEN |
| R11 Circular dependencies | Descriptor imports service/GUI; Settings invokes features for validation | UNKNOWN | Bootstrap cycles and hidden orchestration | Pure module contributions, injection, observer flow distinct from dependency | Composition/API not implemented | Python architecture / Settings | OPEN |
| R12 Hidden restart/activation | UI claims saved value already active | UNKNOWN | Unexpected current behavior | Desired/applied snapshots, named restart target, activation feedback | Native consumer support must be verified | GUI / consumer lifecycle | OPEN |
| R13 Stale editor overwrite | Two dialogs/processes save old values | UNKNOWN | Silent lost updates | One local editor, repository preconditions inside transaction, draft retention | CAS/absent-row handling design pending | Settings repository | OPEN |
| R14 Restoration transfers consent | DB backup/copy carries opt-in flags into another profile | UNKNOWN | Unauthorized collection/transmission | Consent/permission revalidated by owner; paths excluded; restore/import review | Profile provenance/consent enforcement future feature work | Privacy / backup/integration | OPEN |
| R15 Alt bounds/unknown INI drift | Canonical 70-100 differs from source 60-100; known-field replacement loses extensions | UNKNOWN | Adapter incorrect assumptions/user preference loss | Keep local unchanged; owner reconciliation before mapping/writer changes | Local runtime values not inspected | AltF7Hub owner | OPEN, bounded follow-up |
| R16 Bootstrap/path cycle | DB setting selects own DB or arbitrary executable | UNKNOWN | Wrong data target/startup failure/trust bypass | Resolve outside Settings, reuse approved paths/runtime discovery | Installed distribution choices deferred | Distribution / execution | OPEN |
| R17 False evidence/readiness | Source/tests read labeled runtime PASS, or 0D completion starts 0E/features | UNKNOWN | Premature unsafe integration/implementation | Environment/result/provenance explicit; review/approval gates separate | Independent review still pending | Reviewer / Foundation owner | OPEN |
| R18 Protected-state damage | Broad filesystem scan/test/cleanup reads or mutates live INI/database | UNKNOWN | User state loss/privacy breach | Tracked allowlist searches; no runtime/db opening; target-only append | User/runtime may independently change outside candidate; contents unverified | Agent / review/integration task | MITIGATED for this task by scope checks |
| R19 Post-commit effect failure | Theme/hotkey/companion cannot apply after DB commit | UNKNOWN | Saved-but-inactive behavior mistaken for rollback | Separate activation status; last safe applied value; bounded explicit recovery | Feature-specific activation/compensation needs native design | Consumer / Settings GUI | OPEN |

## 0A Compatibility

Architecture comparison: PASS. Evidence: F-A, E01-E12 and recommended boundaries; not runtime verification.

| Approved 0A concern | Candidate alignment |
| --- | --- |
| GUI -> services -> domain -> repositories/gateways -> infrastructure | Draft/display only in GUI; pure definitions/validation; repository persistence; effects remain owning services |
| AHK interaction / PowerShell administration | Neither reads/writes shared business DB settings; AHK local UI prefs preserved; explicit execution inputs |
| Mochi advisory/cosmetic boundary | Standalone loader/current control contract retained; no core DB, unrestricted context or executor |
| Registries/authorization/capabilities | Outside ordinary Settings; no flag grants authority |
| Local/offline workflows | Local definitions/persistence; provider/credential availability not a startup prerequisite |
| Selected context / pending work | Start-bound snapshots and runtime selection, not persisted generic preference |
| DynamicHub workflow authority | Coordinates owner services; workflow position is runtime/feature state |
| Optional-ticket local Case Journal | No mandatory Ticket identity/scope, no competing timeline or settings-based Case storage |

No new framework/provider/process or technology ownership is selected.

## 0B Compatibility

Architecture comparison: PASS. Evidence: F-B, E06/E11 and Cross-Language Settings Delivery.

New actual projections must specialize approved 0B contracts, not invent a competing envelope or redefine identity, message/correlation IDs, per-contract versioning, error grammar, missing/null/empty/false/zero or domain references. Local definition keys are configuration identity, not request/run/session IDs.

Standalone JSON/INI are configuration documents, not automatically IPC. Existing PowerShell schemaVersion 1, Mochi cosmetic v1 and Alt show/focus v1 remain unchanged. No configuration transport/profile/schema file is implemented. Post-commit local callback is a notification, not a new universal EVENT grammar. Timeout/uncertainty never proves effects undone or permits replay.

Settings resolution restrictions supplement input/domain validation without granting authorization or increasing 0B safety maxima.

## 0C Compatibility

Architecture comparison: PASS. Evidence: F-C and classification/persistence matrices.

Settings may configure permitted label language, visibility, suggestion behavior and source-owned retention inputs. They do not redefine Tag/Entity/Entity Type/Category/Type/Kind/Status/Priority/Relationship/Provenance/Confidence meanings, catalog identity, normalization equivalence or workflow eligibility. Catalog management uses taxonomy services/records even when reached through Settings navigation.

Transient Clipboard expiry cannot delete promoted durable evidence by itself; Analytics eligibility/aggregate retention is owner policy; Mochi consumes minimal approved projections. Optional AI suggestions remain advisory, provenance-bearing and subject to source/target freshness checks. No new taxonomy catalog/entity store or semantic edit flag is proposed.

## Testing Strategy

Future tests below are requirements for separately authorized implementation; Result now: NOT RUN. Existing test source E13 was inspected, not rerun. Portable and Windows-specific portions must be separated.

| Future checks | Category / environment | Required observation |
| --- | --- | --- |
| Descriptor admission, duplicate keys, default/type/range/enum/unit validation | unit, security / CLOUD_PORTABLE eligible | Invalid definitions/bool-as-int/nonfinite/unbounded input rejected; pure modules independent of GUI/DB |
| Per-key allowed-source precedence/default/missing/false/zero/null/reset | unit, contract / CLOUD_PORTABLE eligible | Deterministic effective source; arbitrary env source cannot override user key |
| Invalid/unknown/deprecated stored value and unavailable persistence | unit, database, security / CLOUD_PORTABLE eligible | Original value preserved for repair; ordinary safe fallback; sensitive fail closed; no secrets/raw-value logs |
| Override rows/constraints, insert/update/delete CAS, atomic section save and rollback | database / CLOUD_PORTABLE eligible | No partial group change/stale overwrite; integrity_check=ok and zero foreign_key_check on isolated DB |
| Concurrent absent-key writes/stale reset/drafts/second process change | database, integration / CLOUD_PORTABLE eligible for platform-independent parts | Expected-state comparison atomic; refreshed new-operation snapshot; conflicts preserve draft |
| Snapshot revision/notification timing/no-op/observer failure | unit, integration / CLOUD_PORTABLE eligible | Notify only after successful commit/recompute; old active work retains values; committed success not falsely cancelled |
| Restart desired/applied value and failed activation | unit, GUI, integration / portable portions separately | Pending target visible; no automatic restart; activation outcome truthful |
| Draft Apply/Cancel/Reset/search/restricted controls/bilingual metadata identity | GUI, contract / CLOUD_PORTABLE eligible for headless portable behavior | Draft preserved on failures; same machine key in EN/FR; GUI does not duplicate validation/defaults |
| Actual desktop presentation/live language/theme/native window lifetime | GUI / WINDOWS_NATIVE | Applicable focus/DPI/rendering/activation checks; headless tests cannot establish these |
| Hotkey parsing/action allowlists and actual OS registration/recovery | unit portable part; integration / WINDOWS_NATIVE for host input | Collisions/held keys/reserved bindings/ACK failure handled; finite supervised native validation |
| Diagnostic next-operation deadline and registry/policy bounds | unit/security/contract portable part; WINDOWS_NATIVE PowerShell execution | Current identities/private-copy/cleanup/digests protected; no arbitrary parameters or elevation |
| Key rename/type/default/range evolution and restore consent boundary | database, regression, security / applicable portable plus native path portions | No released migration edit/unknown-value loss; explicit conflict/conversion/recovery; no transferred authority |
| Companion standalone loader/local preference compatibility | unit/contract portable Mochi loader; WINDOWS_NATIVE AHK/Mochi behavior | Files/defaults preserved; no IPC expansion or standalone F7Hub DB requirement |
| New actual cross-process projection | contract/integration fixtures; WINDOWS_NATIVE when native session-dependent | Approved 0B profile, bounded validation, minimal data and desired/applied acknowledgment |
| Offline/config startup/optional provider failure | unit/integration / environment-specific | Local workflow remains available; unavailable optional sensitive feature stays disabled |

No full regression, application, database, GUI/native, PowerShell, AHK or Mochi runtime suite was required or executed for this documentation-only task. No SQLite integrity result is claimed for operational data.

## Documentation Impact

Future approved work should update only affected canonical owners; none is edited now.

| Owner | Actual likely downstream impact / condition |
| --- | --- |
| Docs/05_GUI.md | New Settings drafts/Apply/reset/source/restart/localization behavior after implementation |
| Docs/06_SystemArchitecture.md | Approved shared Settings ownership/source boundaries; no implemented claim until code exists |
| Docs/07_Database.md, Docs/08_ERD.md, Docs/09_SQLSchema.md | Only if override/CAS structure or relationships are actually designed/implemented; metadata purpose retained |
| Docs/13_PythonArchitecture.md | Settings composition, pure definitions, repository/service contracts and notifications |
| Docs/11_AHKArchitecture.md | Alt bounds discrepancy owner reconciliation; later hotkey/config delivery if approved |
| Docs/12_PowerShellArchitecture.md | Only a separately reviewed timeout/input feature; invariant/registry distinction and retained contracts |
| Docs/15_NamingConventions.md | Only if approved definition/key conventions need canonical clarification; existing names not mechanically renamed |
| Docs/18_ChangeLog.md, Docs/Status/CURRENT_STATE.md | Record approved/integrated planning or actual future implementation at their proper gates |
| Mochi/README.md and Mochi/docs/Architecture.md | Only if standalone/integrated preference mode, restart behavior or installed-path composition actually changes |

Roadmap/Todo/design-principles owners need updates only if a separately authorized prioritization/policy change occurs; 0D does not rewrite them automatically. This report owns candidate architecture evidence; canonical documents are inputs, not output scope. Historical approval/candidate prose in 0A/0B/0C/Mochi docs is not silently rewritten.

## Downstream Contract / Inputs for Feature Plans

After independent Phase 0D review -> USER approval -> authorized integration, the bounded Settings contract may serve as an input below. This availability is not feature-task authorization or general Foundation reconciliation readiness. 0E remains a separate NOT STARTED phase; its readiness decision is preserved.

| Future owner | MAY rely on approved 0D input | MAY NOT silently redefine |
| --- | --- | --- |
| Clipboard | Typed central behavior inputs, optional history/capture, safe defaults, source-aware reset and next-operation snapshots | Secret exclusion, durable evidence eligibility, retention/deletion authority, 0C semantics or shared persistence/default rules |
| Diagnostics | Bounded requested deadlines, start snapshots, desired/applied change rules | Registry identities/results/permissions, policy ceilings, parameterless retained contracts or execution gateway safeguards |
| Analytics | Configured presentation/query periods over eligible facts and safe change metadata when available | Operational authority, grain/provenance meaning, privacy/deletion obligations or logs as universal durable truth |
| Mochi | Standalone local loader compatibility; future centrally owned integrated preferences through reviewed minimal adapter | Direct DB/business state, unsupported capture/AI, v1 payload limits, runtime attachment/pause as user preferences |
| Automation | Optional permitted-workflow presentation preferences and independent capability/authorization checks | AI execution authority, remediation safeguards, elevation or replay permission |
| Settings GUI | Descriptor metadata, service-owned validation, explicit draft Apply/Cancel/reset, restart/source information | SQL, behavioral defaults, translations as identifiers or no-failure immediate-activation claims |
| Cross-language consumers | Approved per-use-case typed values/projections and 0B contract ownership | Universal configuration transport, hidden global DB reads, arbitrary environment overrides or new wire grammar |
| DynamicHub | Potential display preferences within existing 0A workflow authority, if feature justified | Active case/context/workflow state as generic Settings, competing executor/persistence/identity |

Feature plans own exact admitted keys/defaults/ranges, actual consumer support, privacy/audit intent, resource limits and data lifecycle. Shared mechanism/API/physical schema must follow a separately reviewed bounded slice. A genuine Foundation ownership/meaning/security conflict returns to its owner rather than creating a local replacement.

## Phase 0D Acceptance Criteria

PASS here means the architecture-planning criterion is satisfied by this candidate/evidence, not implemented functionality or runtime PASS. This is the one execution mapping of all 24 original criteria.

| # | Original criterion | Result | Evidence / limitation |
| --- | --- | --- | --- |
| 1 | Current F7Hub configuration mechanisms have been inspected. | PASS | E01-E15, scoped instructions, tracked repository search; operational state excluded |
| 2 | Current config sources have been inventoried. | PASS | C01-C19 paired source/lifecycle tables; protected INI values NOT VERIFIED |
| 3 | Settings ownership is explicit. | PASS | Ownership and service/repository/bootstrap boundaries |
| 4 | Settings and business semantics are separated. | PASS | Classification, feature flags and retained service/domain authority |
| 5 | Settings and taxonomy are separated. | PASS | F-C, classification, rejected semantic keys and 0C compatibility |
| 6 | Settings and registries are separated. | PASS | E04-E06; diagnostic/script registration distinct from requested inputs |
| 7 | Persistence responsibilities are defined. | PASS | Persistence Strategy, source inventory and ownership |
| 8 | SQLite vs config-file decisions are documented. | PASS | D01, decision matrix and local-companion boundaries |
| 9 | Setting scopes are defined. | PASS | USER/APPLICATION/explicit SESSION; module namespace/device/workflow treatment |
| 10 | Default ownership is defined. | PASS | Descriptor defaults versus local defensive fallbacks; no seeding |
| 11 | Precedence is defined. | PASS | Ranked admitted sources, specialized USER/deployment chains and diagram |
| 12 | Validation ownership is defined. | PASS | Pure typed descriptors/service, repository structural checks and owning consumer authorization |
| 13 | Effective-value semantics are defined. | PASS | Missing/invalid/unknown/deprecated/reset and desired/applied behavior |
| 14 | Sensitive values are handled safely. | PASS | Restricted source/intent/evidence, fail-closed effects and safe feedback; future tests NOT RUN |
| 15 | Secrets are excluded from ordinary settings storage. | PASS | Explicit exclusion and conditional secure-reference boundary; actual mechanism NOT VERIFIED |
| 16 | Security invariants cannot be weakened casually by settings. | PASS | Outside precedence; rejected bypass flags/runtime paths and service/gateway checks |
| 17 | Module integration rules are defined. | PASS | Pure contributions/static composition/injected snapshots; no independent store/default authority |
| 18 | Change propagation is planned. | PASS | Post-commit targeted observers, snapshot refresh and consumer-owned activation |
| 19 | Restart-required semantics are planned. | PASS | Named targets, desired/applied state, no automatic restart |
| 20 | Bilingual display concerns are considered. | PASS | One stable key/locale-neutral value and localized resource metadata; exact tooling deferred |
| 21 | Initial module setting inventories exist. | PASS | General through Advanced candidate matrix; exact unsupported feature keys/defaults not approved |
| 22 | Database impact is assessed without migrations. | PASS | Conceptual impact matrix, verified migrated objects and no final SQL/numbers |
| 23 | No production implementation has occurred. | PASS | Target-only appended documentation diff; production/config/database/index changes NONE |
| 24 | Clipboard, Diagnostic, Analytics, and Mochi plans can now depend on a stable configuration architecture. | PASS | Bounded input contract complete for review; authority follows approval/integration and general feature readiness remains 0E-owned |

## Validation

Environment: WINDOWS_NATIVE host (local Windows/PowerShell). Provenance: FRESH for repository inspection, static architecture comparison and document/Git checks. The checks below are documentation/scope checks; source inspection does not establish native runtime behavior. No historical runtime suite is carried forward as a fresh PASS.

| Check | Result | Evidence / limit |
| --- | --- | --- |
| Current configuration inspection | PASS | E01-E15 and source-search scope |
| Config-source inventory | PASS | C01-C19, current reader/writer/default/lifecycle treatment |
| Settings ownership | PASS | Explicit application/service/repository/module/GUI/bootstrap owners |
| Persistence architecture | PASS | D01 and persistence/database impact matrices; no schema implementation |
| Precedence model | PASS | Per-key source admission; USER/deployment specialization |
| Defaults model | PASS | One definition source and distinct local compatibility fallbacks |
| Validation architecture | PASS | Minimal typed model, strict admission, load/change/use boundaries |
| Effective-value semantics | PASS | Ordinary fallback, sensitive fail closed, unknown/evolution/source handling |
| Security/privacy review | PASS | Architecture self-review against root/F-A/F-B/F-C; independent review pending |
| Secrets boundary | PASS | Values excluded; conditional references only; provider NOT VERIFIED |
| Cross-module integration | PASS | Static pure contributions/injection and owned consumer effects |
| Settings/taxonomy separation | PASS | Classification and 0C comparison |
| Settings/registry separation | PASS | Current timeout/approval distinctions and rejected escape hatches |
| Cross-language boundary | PASS | Explicit use-case delivery; retained contracts unchanged |
| DynamicHub state/settings separation | PASS | Approved 0A role; exact preference keys deferred; external material excluded |
| Bilingual model | PASS | Stable identities/value semantics; localized presentation metadata |
| Migration impact review | PASS | Conceptual only; no final SQL, number or migration |
| 0A compatibility | PASS | Architecture ownership comparison only |
| 0B compatibility | PASS | Grammar/retained contract comparison only |
| 0C compatibility | PASS | Semantic/retention/privacy comparison only |
| All 24 acceptance criteria mapped | PASS | One ordered execution mapping, no duplicate IDs |
| Original planning prefix preservation | PASS | First 45,567 bytes match recorded SHA-256; baseline Git blob unchanged |
| Scope control | PASS | Only target tracked modification; unchanged HEAD; empty index |
| Production changes | NONE | No source/config/test/dependency/contract changes |
| Database changes | NONE | No operational DB opened; no SQLite writes or migrations |
| Document sections/fences/tables/local references | PASS | Final bounded structural check and complete appended diff inspection |
| Mermaid diagrams | PASS | Static source/architecture consistency review only |
| Mermaid rendering | NOT RUN | No renderer/installation needed under task contract |
| Runtime application tests | NOT RUN | Documentation-only task |
| Database runtime tests / operational integrity checks | NOT RUN | No mutable data opened; no applicable new schema |
| GUI/native runtime | NOT RUN | No display/interaction change |
| PowerShell runtime | NOT RUN | No script/execution change |
| AHK runtime | NOT RUN | No host/input/preferences execution |
| Mochi runtime | NOT RUN | No renderer/config/control change |
| Independent Phase 0D architecture review | NOT RUN | Next authorized gate; self-review is not independent review |

The final complete target diff is inspected for append-only scope, required structure, matrices/registers, all 24 mappings, FACT/RECOMMENDATION/NOT VERIFIED separation and 0A/0B/0C/0E boundaries. Final branch/HEAD/status/index/untracked/diff-check evidence and whole-file identities are reported separately after edits close, avoiding a self-referential hash.

## Recommended Next Planning Steps

1. STOP at this unapproved, unstaged Phase 0D candidate.
2. Next gate: INDEPENDENT PHASE 0D ARCHITECTURE REVIEW of exact final raw/Git identities, immutable prefix, source evidence, assumptions, matrices and decisions.
3. USER approval and separately authorized controlled Git integration follow a successful review; review completion alone grants neither.
4. Foundation 0E remains a separate NOT STARTED reconciliation task, to be explicitly authorized later. General feature readiness stays with that owner.
5. Later approved feature/Settings slices may resolve exact defaults, repository CAS/schema, localization, hotkey activation, sensitive evidence/consent and specific companion projections. None starts now.

## Result

READY_FOR_FEATURE_ARCHITECTURE
