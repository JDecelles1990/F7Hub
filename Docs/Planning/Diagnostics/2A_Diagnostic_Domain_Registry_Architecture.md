## Execution Gate
Clarify that DynamicHub can request diagnostics and consume structured results, but PowerShell execution remains behind the established diagnostic/service/gateway architecture; stable diagnostic/action IDs should bridge the systems

This planning document may be prepared before its dependencies are approved.

It MUST NOT be executed as an authoritative architecture phase until:

Phase 0A  APPROVED
Phase 0B  APPROVED
Phase 0C  APPROVED
Phase 0D  APPROVED
Phase 1A  APPROVED

Phase 1B and 1C should also be reviewed where their decisions
materially affect Diagnostic integration or deep-link behavior.

If an upstream dependency remains unresolved:

STOP
record dependency
return BLOCKED or REQUIRES_DECISION

Do not invent replacement architecture locally.

0A → 0B → 0C → 0D
              ↓
       1A → 1B → 1C
              ↓
             2A