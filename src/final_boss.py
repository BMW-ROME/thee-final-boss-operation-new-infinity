"""Offline-only task ledger. No networking, subprocesses, inference or payments."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
import sqlite3
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]


def validate(value, schema, path="$", root=None):
    """Validate the deliberately small JSON Schema subset used in this repo."""
    root = root or schema
    if "$ref" in schema:
        target = root
        for key in schema["$ref"].removeprefix("#/").split("/"):
            target = target[key]
        return validate(value, target, path, root)
    types = {"object": dict, "array": list, "string": str, "integer": int,
             "number": (int, float), "boolean": bool}
    kind = schema.get("type")
    if kind and (not isinstance(value, types[kind]) or
                 kind in ("integer", "number") and isinstance(value, bool)):
        raise ValueError(f"{path}: expected {kind}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path}: invalid enum")
    if isinstance(value, dict):
        if set(schema.get("required", [])) - value.keys():
            raise ValueError(f"{path}: required fields missing")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and value.keys() - props.keys():
            raise ValueError(f"{path}: unknown fields")
        for key, item in value.items():
            if key in props:
                validate(item, props[key], f"{path}.{key}", root)
    if isinstance(value, list):
        for i, item in enumerate(value):
            validate(item, schema["items"], f"{path}[{i}]", root)
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        raise ValueError(f"{path}: empty string")
    if isinstance(value, str) and "pattern" in schema and not re.search(schema["pattern"], value):
        raise ValueError(f"{path}: invalid pattern")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not float("-inf") < value < float("inf"):
            raise ValueError(f"{path}: non-finite number")
        if value < schema.get("minimum", value) or value > schema.get("maximum", value):
            raise ValueError(f"{path}: out of bounds")


def schema(name):
    return json.loads((ROOT / "schemas" / f"{name}.v1.json").read_text())


def task(key="synthetic-demo"):
    return {"schema_version": "1", "task_id": str(uuid.uuid4()), "idempotency_key": key,
            "action": "offline_artifact", "state": "pending", "responsible_agent": "local-orchestrator",
            "environment": "local", "source": {"uri": "synthetic:demo", "observed_at": "2026-10-22", "method": "synthetic fixture"},
            "checkpoint": "not-started", "artifacts": [], "verification": "pending",
            "retry": {"max_attempts": 3, "base_seconds": 1, "cap_seconds": 8},
            "budget": {"currency": "USD", "approved_minor": 0, "spent_minor": 0},
            "approval": {"status": "not_requested", "reference": "none"},
            "customer_contact_key": "none", "recovery": "reclaim expired lease and resume checkpoint",
            "rollback": "discard synthetic output; preserve ledger"}


class Ledger:
    def __init__(self, path, clock=time.time):
        self.clock = clock
        self.db = sqlite3.connect(path, timeout=10, isolation_level=None)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
          id TEXT PRIMARY KEY, idem TEXT NOT NULL UNIQUE, digest TEXT NOT NULL,
          payload TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
          token TEXT, lease_until REAL NOT NULL DEFAULT 0, next_at REAL NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS events (
          sequence INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL UNIQUE,
          task_id TEXT NOT NULL, payload TEXT NOT NULL);
        """)

    def close(self):
        self.db.close()

    def _event(self, data, event, previous):
        e = {"schema_version": "1", "event_id": str(uuid.uuid4()), "task_id": data["task_id"],
             "event": event, "previous_state": previous, "state": data["state"],
             "timestamp": self.clock(), "responsible_agent": data["responsible_agent"],
             "environment": data["environment"], "checkpoint": data["checkpoint"]}
        validate(e, schema("event"))
        self.db.execute("INSERT INTO events(id,task_id,payload) VALUES(?,?,?)",
                        (e["event_id"], e["task_id"], json.dumps(e)))

    def _save(self, data, event, previous):
        validate(data, schema("task"))
        self.db.execute("UPDATE tasks SET payload=? WHERE id=?", (json.dumps(data), data["task_id"]))
        self._event(data, event, previous)

    def submit(self, data):
        validate(data, schema("task"))
        if data["state"] != "pending" or data["verification"] != "pending" or data["artifacts"]:
            raise ValueError("new tasks must be pending without artifacts")
        if data["budget"]["approved_minor"] or data["budget"]["spent_minor"]:
            raise ValueError("only zero-budget offline tasks supported")
        normalized = copy.deepcopy(data)
        normalized.pop("task_id")
        digest = hashlib.sha256(json.dumps(normalized, sort_keys=True).encode()).hexdigest()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            old = self.db.execute("SELECT id,digest FROM tasks WHERE idem=?", (data["idempotency_key"],)).fetchone()
            if old:
                if old[1] != digest:
                    raise ValueError("idempotency key reused with different payload")
                self.db.commit()
                return old[0]
            self.db.execute("INSERT INTO tasks(id,idem,digest,payload) VALUES(?,?,?,?)",
                            (data["task_id"], data["idempotency_key"], digest, json.dumps(data)))
            self._event(data, "submitted", "none")
            self.db.commit()
            return data["task_id"]
        except Exception:
            self.db.rollback()
            raise

    def get(self, task_id):
        row = self.db.execute("SELECT payload FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            raise ValueError("unknown task")
        return json.loads(row[0])

    def claim(self, task_id, lease_seconds=30):
        if type(lease_seconds) is not int or not 1 <= lease_seconds <= 300:
            raise ValueError("lease must be 1..300 seconds")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            data = self.get(task_id)
            attempts, lease, next_at = self.db.execute(
                "SELECT attempts,lease_until,next_at FROM tasks WHERE id=?", (task_id,)).fetchone()
            now = self.clock()
            previous = data["state"]
            if previous not in ("pending", "running") or next_at > now or previous == "running" and lease > now:
                self.db.commit()
                return None
            if attempts >= data["retry"]["max_attempts"]:
                data["state"] = "failed"
                self._save(data, "retry_exhausted", previous)
                self.db.commit()
                return None
            token = str(uuid.uuid4())
            data["state"] = "running"
            self.db.execute("UPDATE tasks SET attempts=attempts+1,token=?,lease_until=? WHERE id=?",
                            (token, now + lease_seconds, task_id))
            self._save(data, "claimed" if previous == "pending" else "recovered", previous)
            self.db.commit()
            return token
        except Exception:
            self.db.rollback()
            raise

    def update(self, task_id, token, operation, checkpoint=None, artifact=None):
        """Fenced writes: an expired or replaced worker cannot alter task state."""
        self.db.execute("BEGIN IMMEDIATE")
        try:
            data = self.get(task_id)
            stored, lease, attempts = self.db.execute(
                "SELECT token,lease_until,attempts FROM tasks WHERE id=?", (task_id,)).fetchone()
            if data["state"] != "running" or token != stored or lease <= self.clock():
                raise ValueError("inactive or expired worker")
            if operation not in ("checkpoint", "succeed", "retry", "fail", "cancel"):
                raise ValueError("invalid operation")
            if checkpoint is not None:
                data["checkpoint"] = checkpoint
            if artifact is not None:
                # This is a declared receipt. Caller must independently inspect the file.
                data["artifacts"].append(artifact)
            validate(data, schema("task"))
            if operation == "succeed":
                if not data["artifacts"] or any(a["verification"] != "passed" for a in data["artifacts"]):
                    raise ValueError("verified artifact receipt required")
                data["state"], data["verification"] = "succeeded", "passed"
            elif operation == "retry":
                data["state"] = "pending" if attempts < data["retry"]["max_attempts"] else "failed"
                delay = min(data["retry"]["cap_seconds"], data["retry"]["base_seconds"] * 2 ** (attempts - 1))
                self.db.execute("UPDATE tasks SET next_at=? WHERE id=?", (self.clock() + delay, task_id))
            elif operation in ("fail", "cancel"):
                data["state"] = "failed" if operation == "fail" else "cancelled"
            self._save(data, operation, "running")
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def events(self, task_id):
        return [json.loads(r[0]) for r in self.db.execute(
            "SELECT payload FROM events WHERE task_id=? ORDER BY sequence", (task_id,))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="local SQLite path (not a network drive)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="complete one synthetic task; safe to repeat")
    submit = sub.add_parser("submit"); submit.add_argument("file")
    show = sub.add_parser("show"); show.add_argument("task_id")
    args = parser.parse_args()
    ledger = Ledger(args.db)
    try:
        if args.command == "submit":
            print(ledger.submit(json.loads(Path(args.file).read_text(encoding="utf-8-sig"))))
        elif args.command == "show":
            print(json.dumps({"task": ledger.get(args.task_id), "events": ledger.events(args.task_id)}, indent=2))
        else:
            task_id = ledger.submit(task())
            token = ledger.claim(task_id)
            output = Path(args.db).resolve().with_suffix(".demo.txt")
            content = b"Synthetic offline delivery proof. No customer action performed.\n"
            if token:
                # Never clobber a file of unknown provenance, including after a crash.
                with output.open("xb") as handle:
                    handle.write(content)
                if output.read_bytes() != content:
                    raise ValueError("demo output failed read-back verification")
                receipt = {"uri": output.as_uri(), "sha256": hashlib.sha256(content).hexdigest(),
                           "verification": "passed", "method": "read-back byte equality"}
                ledger.update(task_id, token, "succeed", "demo-readback-complete", receipt)
            data = ledger.get(task_id)
            if data["state"] != "succeeded":
                raise ValueError("demo is incomplete; inspect its checkpoint before recovery")
            if not output.is_file() or output.read_bytes() != content:
                raise ValueError("historical completion exists but current artifact verification failed")
            print(json.dumps({"task": ledger.get(task_id), "event_count": len(ledger.events(task_id))}, indent=2))
    finally:
        ledger.close()


if __name__ == "__main__":
    main()
