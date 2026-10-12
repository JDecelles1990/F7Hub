"""CP-00 preference meanings; storing these never activates Clipboard effects."""

from f7hub.domain.settings import SettingDefinition


WORKFLOW_ENABLED = "clipboard.workflow_enabled"
SOURCE_PROCESS_ENABLED = "clipboard.source_process_persistence_enabled"
SOURCE_TITLE_ENABLED = "clipboard.source_window_title_persistence_enabled"

CLIPBOARD_SETTING_DEFINITIONS = tuple(
    SettingDefinition(key=key, owner="clipboard", default=False)
    for key in (WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED, SOURCE_TITLE_ENABLED)
)
