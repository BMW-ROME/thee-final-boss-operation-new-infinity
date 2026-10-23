import concurrent.futures
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from final_boss import Ledger, schema, task, validate


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / "ledger.sqlite")
        self.now = 1000
        self.ledger = Ledger(self.path, lambda: self.now)
        self.id = self.ledger.submit(task())

    def tearDown(self):
        self.ledger.close()
        self.temp.cleanup()

    def test_duplicate_and_conflicting_submission(self):
        self.assertEqual(self.id, self.ledger.submit(task()))
        changed = task(); changed["checkpoint"] = "different"
        with self.assertRaises(ValueError): self.ledger.submit(changed)
        self.assertEqual(1, len(self.ledger.events(self.id)))

    def test_concurrent_claims_have_one_winner(self):
        def claim(_):
            db = Ledger(self.path, lambda: 1000)
            try: return db.claim(self.id)
            finally: db.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(claim, range(8)))
        self.assertEqual(1, sum(r is not None for r in results))
        self.assertEqual(2, len(self.ledger.events(self.id)))

    def test_process_interruption_and_stale_worker_fencing(self):
        self.ledger.close()
        source = str(Path(__file__).resolve().parents[1] / "src")
        code = ('import sys,os;sys.path.insert(0,sys.argv[1]);from final_boss import Ledger;'
                'd=Ledger(sys.argv[2],lambda:1000);t=d.claim(sys.argv[3],1);'
                'd.update(sys.argv[3],t,"checkpoint","durable-before-crash");os._exit(23)')
        result = subprocess.run([sys.executable, "-c", code, source, self.path, self.id], timeout=15)
        self.assertEqual(23, result.returncode)
        self.now = 1002
        self.ledger = Ledger(self.path, lambda: self.now)
        old = self.ledger.db.execute("SELECT token FROM tasks WHERE id=?", (self.id,)).fetchone()[0]
        token = self.ledger.claim(self.id)
        self.assertTrue(token)
        self.assertEqual("durable-before-crash", self.ledger.get(self.id)["checkpoint"])
        with self.assertRaises(ValueError): self.ledger.update(self.id, old, "fail")
        self.ledger.update(self.id, token, "cancel")
        self.assertEqual("cancelled", self.ledger.get(self.id)["state"])
        self.assertIn("recovered", [e["event"] for e in self.ledger.events(self.id)])

    def test_retry_backoff_and_limit(self):
        for attempt in range(3):
            token = self.ledger.claim(self.id)
            self.assertTrue(token)
            self.ledger.update(self.id, token, "retry")
            self.assertIsNone(self.ledger.claim(self.id))
            self.now += 2 ** attempt
        self.assertEqual("failed", self.ledger.get(self.id)["state"])
        self.assertIsNone(self.ledger.claim(self.id))

    def test_crash_reclaims_are_bounded(self):
        for _ in range(3):
            self.assertTrue(self.ledger.claim(self.id, 1))
            self.now += 2
        self.assertIsNone(self.ledger.claim(self.id))
        self.assertEqual("failed", self.ledger.get(self.id)["state"])

    def test_invalid_transition_and_artifact_roll_back(self):
        token = self.ledger.claim(self.id)
        for operation, artifact in [("publish", None), ("succeed", None),
                                    ("succeed", {"uri": "missing required fields"})]:
            with self.assertRaises(ValueError):
                self.ledger.update(self.id, token, operation, "must-not-persist", artifact)
        self.assertEqual("not-started", self.ledger.get(self.id)["checkpoint"])
        self.assertEqual(2, len(self.ledger.events(self.id)))
        receipt = {"uri": "synthetic:output", "sha256": "a" * 64,
                   "verification": "passed", "method": "synthetic fixture only"}
        self.ledger.update(self.id, token, "succeed", artifact=receipt)
        with self.assertRaises(ValueError): self.ledger.update(self.id, token, "retry")
        self.assertIsNone(self.ledger.claim(self.id))

    def test_schema_rejects_unknown_version_side_effects_and_budget(self):
        for key, value in [("schema_version", "2"), ("action", "contact_customer"),
                           ("action", "charge"), ("unknown", "x"), ("task_id", "")]:
            data = task(); data[key] = value
            with self.assertRaises(ValueError): self.ledger.submit(data)
        for value in [1, -1, True, float("nan")]:
            data = task(); data["budget"]["approved_minor"] = value
            with self.assertRaises(ValueError): self.ledger.submit(data)
        data = task(); del data["source"]
        with self.assertRaises(ValueError): self.ledger.submit(data)
        for event in self.ledger.events(self.id): validate(event, schema("event"))

    def test_demo_repeat_is_idempotent_and_artifact_exists(self):
        script = Path(__file__).resolve().parents[1] / "src" / "final_boss.py"
        path = Path(self.temp.name) / "demo.sqlite"
        command = [sys.executable, str(script), "--db", str(path), "demo"]
        first = json.loads(subprocess.check_output(command, timeout=15))
        second = json.loads(subprocess.check_output(command, timeout=15))
        self.assertEqual(first, second)
        self.assertEqual("succeeded", first["task"]["state"])
        self.assertTrue(path.with_suffix(".demo.txt").is_file())


if __name__ == "__main__":
    unittest.main()
