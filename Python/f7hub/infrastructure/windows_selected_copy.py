"""CP02-S4 delivery adapter; reuses the approved writer, never sends input."""

from f7hub.domain.clipboard import ClipboardCopyError
from f7hub.infrastructure.windows_latest_paste import WindowsPasteAPI, PasteEffectError


def write_selected_text(text, owner_hwnd, guard, *, api=None):
    """One write attempt, no retry/restoration/hotkeys/target activation.

    owner_hwnd is the retained F7Hub window, captured on the GUI thread. All
    allocation, ownership, privacy markers and readback belong to write_text.
    """
    entered_writer = False
    try:
        guard()
        writer = api if api is not None else WindowsPasteAPI()
        def checked():
            try:
                guard()
            except ClipboardCopyError as error:
                raise PasteEffectError(error.code) from None
        entered_writer = True
        writer.write_text(text, owner_hwnd, checked)
        return "WRITTEN"
    except ClipboardCopyError:
        raise
    except PasteEffectError as error:
        code = str(error) if str(error) in ClipboardCopyError.CODES else "CLIPBOARD_VERIFY_FAILED"
        raise ClipboardCopyError(code, error.clipboard) from None
    except Exception:
        raise ClipboardCopyError("UNAVAILABLE", "MAY_HAVE_CHANGED" if entered_writer else "UNCHANGED") from None
