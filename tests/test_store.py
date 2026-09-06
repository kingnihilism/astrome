import tempfile
import unittest
from pathlib import Path

from app import Store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tempdir.name) / "astro_me.json")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_add_update_duplicate_delete(self):
        self.store.add("natal", {"name": "Moon", "position": "Taurus", "house": "8", "notes": ""})
        original = self.store.records("natal")[0]
        self.store.update("natal", original["id"], {"notes": "Core placement"})
        self.assertEqual(self.store.find("natal", original["id"])["notes"], "Core placement")

        self.store.duplicate("natal", original["id"])
        self.assertEqual(len(self.store.records("natal")), 2)
        self.assertTrue(self.store.records("natal")[1]["name"].endswith("(Copy)"))

        self.store.delete("natal", original["id"])
        self.assertEqual(len(self.store.records("natal")), 1)


if __name__ == "__main__":
    unittest.main()
