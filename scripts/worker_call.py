"""Submit one issued worker request and return its observation in one call."""

import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path


def read(path):
    return json.loads(path.read_text()) if path.exists() else None


def compact(value):
    result = dict(value)
    if "observation" in result:
        page = result["observation"]
        result["observation"] = {k: page[k] for k in ("url", "title", "fingerprint", "text", "actions") if k in page}
        result["observation"]["actions"] = [
            {k: a[k] for k in ("id", "node", "kind", "label", "role", "value", "options",
                               "checked", "selected", "disabled") if k in a}
            for a in page.get("actions", [])
        ]
    return result


def call(folder, command=None, timeout=40, _observe=True):
    """Never resubmit a command, including after a timeout or uncertain execution."""
    folder = Path(folder)
    if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or not 0 < timeout <= 60:
        raise ValueError("Use a timeout above zero and at most 60 seconds")
    deadline = time.monotonic() + timeout
    ready = None
    while time.monotonic() < deadline:
        stopped = read(folder / "stopped.json")
        if stopped:
            return {"status": "stopped", **stopped}
        ready = read(folder / "ready.json")
        if ready:
            break
        time.sleep(0.025)
    if not ready:
        return {"status": "not_ready", "action_submitted": False}
    if command is None:
        return {"status": "ready", **compact(ready)}
    if (command.get("request_id") != ready["request_id"]
            or command.get("fingerprint") != ready["observation"]["fingerprint"]):
        return {"status": "request_mismatch", "action_submitted": False, "ready": compact(ready)}
    payload = json.dumps(command).encode()
    if len(payload) > 16384:
        raise ValueError("Action request exceeds size limit")
    sequence = ready["sequence"]
    target = folder / f"action-{sequence}.json"
    # Publish complete bytes atomically. A repeated call cannot replace an issued action.
    fd, temporary = tempfile.mkstemp(prefix=".request-", dir=folder)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError:
            return {"status": "already_submitted", "unresolved_execution": True,
                    "reason": "Read the original result. Do not replay the action."}
    finally:
        os.unlink(temporary)
    while time.monotonic() < deadline:
        result = read(folder / f"result-{sequence}.json")
        if result:
            following = read(folder / "ready.json")
            if result.get("stop") or (following and following["sequence"] > sequence):
                response = {"status": "returned", "result": compact(result)}
                if not result.get("stop"):
                    response["ready"] = compact(following)
                    response["result"].pop("observation", None)
                    remaining = deadline - time.monotonic()
                    if _observe and following.get("observation_required") and remaining > 0:
                        observed = call(folder, {
                            "request_id": following["request_id"],
                            "fingerprint": following["observation"]["fingerprint"],
                            "mode": "observe",
                        }, timeout=remaining, _observe=False)
                        response.pop("ready", None)
                        response["automatic_observation"] = observed
                        if "ready" in observed:
                            response["ready"] = observed.pop("ready")
                        response["status"] = observed["status"]
                return response
        stopped = read(folder / "stopped.json")
        if stopped:
            return {"status": "stopped", **stopped,
                    "result": compact(result) if result else None}
        time.sleep(0.025)
    return {"status": "response_timeout", "action_submitted": True,
            "unresolved_execution": True, "sequence": sequence,
            "reason": "Read the original result before any further action. Do not replay."}


if __name__ == "__main__":
    command = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
    print(json.dumps(call(sys.argv[1], command), separators=(",", ":")))
