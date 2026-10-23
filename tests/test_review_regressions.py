"""Independent artifact-integrity regressions; only temporary synthetic files."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'src' / 'final_boss.py'

class ReviewRegressions(unittest.TestCase):
    def invoke(self, path):
        return subprocess.run([sys.executable, str(SCRIPT), '--db', str(path), 'demo'],
                              capture_output=True, text=True, timeout=15)

    def test_completed_demo_detects_missing_or_tampered_artifact(self):
        for tamper in (False, True):
            with self.subTest(tamper=tamper), tempfile.TemporaryDirectory() as directory:
                db = Path(directory) / 'review.sqlite'
                self.assertEqual(self.invoke(db).returncode, 0)
                output = db.with_suffix('.demo.txt')
                if tamper:
                    output.write_text('tampered synthetic text')
                else:
                    output.unlink()
                rerun = self.invoke(db)
                self.assertNotEqual(rerun.returncode, 0,
                                    'Completed demo must fail current verification when artifact is absent or altered')
                if tamper:
                    self.assertEqual(output.read_text(), 'tampered synthetic text')

    def test_first_demo_does_not_overwrite_existing_unrelated_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / 'review.sqlite'
            output = db.with_suffix('.demo.txt')
            output.write_text('pre-existing unrelated synthetic file')
            run = self.invoke(db)
            self.assertEqual(output.read_text(), 'pre-existing unrelated synthetic file',
                             'First demo must preserve a pre-existing artifact of unknown provenance')
            self.assertNotEqual(run.returncode, 0)

if __name__ == '__main__':
    unittest.main()
