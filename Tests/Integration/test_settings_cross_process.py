"""AC-15: deterministic, bounded, independent-process Settings CAS integration.

Repeat this test during independent review and whenever Settings persistence,
revision, grouped updates, reset or transaction boundaries change. A read-only
GUI-only change does not by itself require the whole concurrency suite.
"""

from functools import partial
import multiprocessing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from f7hub.domain.clipboard_settings import (
    CLIPBOARD_SETTING_DEFINITIONS, WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED, SOURCE_TITLE_ENABLED,
)
from f7hub.infrastructure.database import bootstrap_database, database_connection, validate_database_integrity
from f7hub.repositories.settings_repository import (
    SettingsConflictError, SettingsContentionError, SettingsPersistenceError, SettingsRepository,
)
from f7hub.services.settings_service import SettingsService


ROOT = Path(__file__).resolve().parents[2]
KEYS = (WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED, SOURCE_TITLE_ENABLED)
BUSY_TIMEOUT_MS = 250
IPC_TIMEOUT_SECONDS = 10


def _snapshot_payload(snapshot):
    return dict(revision=snapshot.revision, values={entry.key: entry.value for entry in snapshot.values})


def _settings_process(database_path, channel, race_barrier):
    """Each child owns its own service/connections; the parent controls sequence."""
    held_connection = None
    try:
        with patch("f7hub.repositories.settings_repository.database_connection",
                   partial(database_connection, busy_timeout_ms=BUSY_TIMEOUT_MS)):
            service = SettingsService(SettingsRepository(database_path), CLIPBOARD_SETTING_DEFINITIONS)
            channel.send(dict(outcome="READY", **_snapshot_payload(service.get_snapshot())))
            # Finite command budget and IPC deadlines; no sleeps or retry loop.
            for _ in range(16):
                if not channel.poll(IPC_TIMEOUT_SECONDS):
                    raise TimeoutError("AC-15 parent command deadline exceeded")
                command = channel.recv()
                action = command["action"]
                if action == "STOP":
                    channel.send(dict(outcome="STOPPED"))
                    return
                try:
                    if action == "REFRESH":
                        snapshot = service.refresh()
                        if not snapshot.storage_available:
                            raise SettingsPersistenceError("AC-15 refresh storage unavailable")
                        reply = dict(outcome="REFRESHED", **_snapshot_payload(snapshot))
                    elif action in ("APPLY", "RACE"):
                        if action == "RACE":
                            race_barrier.wait(timeout=IPC_TIMEOUT_SECONDS)
                        result = service.apply(command["changes"], expected_revision=command["revision"])
                        reply = dict(outcome="COMMITTED", changed_keys=result.changed_keys,
                                     **_snapshot_payload(result.snapshot))
                    elif action == "RESET":
                        result = service.reset(command["keys"], expected_revision=command["revision"])
                        reply = dict(outcome="COMMITTED", changed_keys=result.changed_keys,
                                     **_snapshot_payload(result.snapshot))
                    elif action == "HOLD_LOCK":
                        # This is a test-only contention fixture, not a repository writer.
                        held_connection = database_connection(database_path, busy_timeout_ms=BUSY_TIMEOUT_MS)
                        connection = held_connection.__enter__()
                        connection.execute("BEGIN IMMEDIATE")
                        reply = dict(outcome="LOCK_HELD")
                    elif action == "RELEASE_LOCK":
                        held_connection.__exit__(None, None, None)
                        held_connection = None
                        reply = dict(outcome="LOCK_RELEASED")
                    else:
                        raise ValueError("Unknown AC-15 command")
                except SettingsConflictError:
                    reply = dict(outcome="STALE_REVISION", **_snapshot_payload(service.get_snapshot()))
                except SettingsContentionError:
                    reply = dict(outcome="DATABASE_CONTENTION", **_snapshot_payload(service.get_snapshot()))
                except Exception as error:
                    # Safe error class only; no raw exception/config value feedback.
                    reply = dict(outcome="UNEXPECTED_FAILURE", error_type=type(error).__name__)
                channel.send(reply)
            raise RuntimeError("AC-15 finite command budget exhausted")
    finally:
        if held_connection is not None:
            held_connection.__exit__(None, None, None)
        channel.close()


class SettingsCrossProcessTests(unittest.TestCase):
    def test_ac15_ordered_stale_group_reset_absent_race_contention_refresh_and_cleanup(self):
        context = multiprocessing.get_context("spawn")
        with tempfile.TemporaryDirectory() as temporary:
            database = Path(temporary) / "ac15-synthetic.db"
            bootstrap_database(database, ROOT / "Database/Migrations")
            channels = [context.Pipe(duplex=True) for _ in range(2)]
            barrier = context.Barrier(2)
            processes = [context.Process(target=_settings_process, args=(str(database), pair[1], barrier))
                         for pair in channels]

            def receive(index):
                self.assertTrue(channels[index][0].poll(IPC_TIMEOUT_SECONDS), "AC-15 child response deadline exceeded")
                reply = channels[index][0].recv()
                self.assertNotEqual(reply["outcome"], "UNEXPECTED_FAILURE", reply)
                return reply

            def request(index, action, **arguments):
                channels[index][0].send(dict(action=action, **arguments))
                return receive(index)

            def state():
                current = SettingsRepository(database).load_state()
                with database_connection(database, read_only=True) as connection:
                    self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
                return current

            try:
                for process in processes:
                    process.start()
                for _, child in channels:
                    child.close()
                initial = [receive(index) for index in (0, 1)]
                self.assertEqual(initial[0], initial[1])
                self.assertEqual(initial[0]["revision"], 0)
                self.assertTrue(all(value is False for value in initial[0]["values"].values()))

                # B commits a coherent group. A still holds revision 0.
                b = request(1, "APPLY", changes=dict.fromkeys(KEYS, True), revision=0)
                self.assertEqual((b["outcome"], b["revision"]), ("COMMITTED", 1))
                self.assertEqual(set(b["changed_keys"]), set(KEYS))
                committed = state()
                a = request(0, "APPLY", changes={WORKFLOW_ENABLED: True, SOURCE_PROCESS_ENABLED: False,
                                                SOURCE_TITLE_ENABLED: True}, revision=0)
                self.assertEqual(a["outcome"], "STALE_REVISION")
                self.assertEqual(state(), committed)  # No partial write or revision advance.
                a = request(0, "RESET", keys=(WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED), revision=0)
                self.assertEqual(a["outcome"], "STALE_REVISION")
                self.assertEqual(state(), committed)  # Stale delete cannot erase B's changes.

                a = request(0, "REFRESH")
                self.assertEqual(a["revision"], 1)
                self.assertEqual(a["values"], b["values"])
                a = request(0, "APPLY", changes={WORKFLOW_ENABLED: False, SOURCE_TITLE_ENABLED: False}, revision=1)
                self.assertEqual((a["outcome"], a["revision"]), ("COMMITTED", 2))
                self.assertEqual(a["values"], dict(zip(KEYS, (False, True, False))))

                # Empty all overrides, then both processes explicitly read revision 3.
                self.assertEqual(request(0, "RESET", keys=KEYS, revision=2)["revision"], 3)
                self.assertEqual(state().overrides, ())
                self.assertEqual(request(0, "REFRESH")["revision"], 3)
                self.assertEqual(request(1, "REFRESH")["revision"], 3)
                contenders = ({WORKFLOW_ENABLED: True, SOURCE_PROCESS_ENABLED: True},
                              {WORKFLOW_ENABLED: True, SOURCE_TITLE_ENABLED: True})
                for index in (0, 1):
                    channels[index][0].send(dict(action="RACE", changes=contenders[index], revision=3))
                race = [receive(index) for index in (0, 1)]
                self.assertCountEqual([reply["outcome"] for reply in race], ("COMMITTED", "STALE_REVISION"))
                winner = next(index for index in (0, 1) if race[index]["outcome"] == "COMMITTED")
                after_race = state()
                self.assertEqual(after_race.revision, 4)
                self.assertEqual({entry.key: entry.value_text for entry in after_race.overrides},
                                 {key: "true" for key in contenders[winner]})
                for index in (0, 1):
                    self.assertEqual(request(index, "REFRESH")["revision"], 4)

                # Distinguish a genuine SQLite writer-lock deadline from stale CAS.
                self.assertEqual(request(1, "HOLD_LOCK")["outcome"], "LOCK_HELD")
                busy = request(0, "APPLY", changes={WORKFLOW_ENABLED: False}, revision=4)
                self.assertEqual(busy["outcome"], "DATABASE_CONTENTION")
                self.assertEqual(state(), after_race)
                self.assertEqual(request(1, "RELEASE_LOCK")["outcome"], "LOCK_RELEASED")
                self.assertEqual(request(0, "REFRESH")["revision"], 4)
                recovered = request(0, "APPLY", changes={WORKFLOW_ENABLED: False}, revision=4)
                self.assertEqual((recovered["outcome"], recovered["revision"]), ("COMMITTED", 5))
                self.assertFalse(recovered["values"][WORKFLOW_ENABLED])
                self.assertEqual(state().revision, 5)

                for index in (0, 1):
                    self.assertEqual(request(index, "STOP")["outcome"], "STOPPED")
                for process in processes:
                    process.join(timeout=5)
                    self.assertFalse(process.is_alive(), "AC-15 test-owned child survived")
                    self.assertEqual(process.exitcode, 0)
            finally:
                for process in processes:
                    if process.is_alive():
                        process.terminate()
                        process.join(timeout=5)
                    if process.is_alive():
                        process.kill()
                        process.join(timeout=5)
                    self.assertFalse(process.is_alive(), "AC-15 cleanup failed")
                    if process.pid is not None:
                        process.close()
                for parent, child in channels:
                    parent.close()
                    child.close()
