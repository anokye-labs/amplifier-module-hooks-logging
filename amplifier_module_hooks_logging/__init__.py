"""
Unified JSONL logging hook.
Writes structured logs via app-initialized logger or fallback.
"""

import json
import logging
from datetime import UTC
from datetime import datetime
from typing import Any

from amplifier_core import HookResult
from amplifier_core import ModuleCoordinator

logger = logging.getLogger(__name__)

SCHEMA = {"name": "amplifier.log", "ver": "1.0.0"}


def _ts() -> str:
    from datetime import timezone

    return datetime.now(UTC).isoformat(timespec="milliseconds")


async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None):
    config = config or {}
    priority = int(config.get("priority", 100))
    path = config.get("path", "./amplifier.log.jsonl")

    # Fallback file when no app logger is present
    class _Fallback:
        def __init__(self, path: str):
            from pathlib import Path

            self.path = Path(path)
            self.path.parent.mkdir(parents=True, exist_ok=True)

        def write(self, rec: dict[str, Any]):
            try:
                with self.path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            except Exception:
                pass

    fallback = _Fallback(path)

    async def handler(event: str, data: dict[str, Any]) -> HookResult:
        rec = {
            "ts": _ts(),
            "lvl": "INFO" if "error" not in event else "ERROR",
            "schema": SCHEMA,
            "event": event,
        }
        # Merge data (ensure serializable)
        payload = {}
        try:
            for k, v in (data or {}).items():
                if k in (
                    "redaction",
                    "data",
                    "status",
                    "duration_ms",
                    "module",
                    "component",
                    "error",
                    "request_id",
                    "span_id",
                    "parent_span_id",
                    "session_id",
                ):
                    payload[k] = v
            rec.update(payload)
        except Exception as e:
            rec["error"] = {"type": type(e).__name__, "msg": str(e)}

        # Prefer app logger if present
        app_logger = logging.getLogger()
        used_app_logger = False
        for h in app_logger.handlers:
            # Detect JSONL handler by checking for path attribute (specific to JsonlHandler)
            # We can't check type across packages, but JsonlHandler has a unique 'path' attribute
            if hasattr(h, "path") and hasattr(h, "emit"):
                used_app_logger = True
                break

        try:
            if used_app_logger:
                # attach as structured msg to root
                logger.debug(f"Logging event {event} via app logger")
                app_logger.info(rec)
            else:
                logger.debug(f"Logging event {event} via fallback")
                fallback.write(rec)
        except Exception as e:
            logger.error(f"Failed to log event {event}: {e}")
            fallback.write(rec)

        return HookResult(action="continue")

    events = [
        "session:start",
        "session:end",
        "prompt:submit",
        "prompt:complete",
        "plan:start",
        "plan:end",
        "provider:request",
        "provider:response",
        "provider:error",
        "tool:pre",
        "tool:post",
        "tool:error",
        "context:pre_compact",
        "context:post_compact",
        "artifact:write",
        "artifact:read",
        "policy:violation",
        "approval:required",
        "approval:granted",
        "approval:denied",
        "content_block:start",
        "content_block:delta",
        "content_block:end",
    ]
    for ev in events:
        coordinator.hooks.register(ev, handler, priority=priority, name="hooks-logging")

    logger.info("Mounted hooks-logging (JSONL)")
    return
