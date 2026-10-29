import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

from PIL import Image

MODULE_PATH = Path(__file__).resolve().parents[1] / 'tools' / 'audit_dataset.py'
spec = importlib.util.spec_from_file_location('audit_dataset', MODULE_PATH)
audit_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_module)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = self.root / 'Data'
        self.out = self.root / 'reports'
        (self.data / 'cat' / 'hello').mkdir(parents=True)
        (self.data / 'other' / 'otherlabel').mkdir(parents=True)
        self.original = self.data / 'cat' / 'hello' / 'one.png'
        Image.new('RGB', (8, 9), color='red').save(self.original)

    def tearDown(self):
        self.temp.cleanup()

    def read_csv(self, name):
        with (self.out / name).open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))

    def test_counts_unreadable_duplicates_and_ignored(self):
        duplicate = self.data / 'other' / 'otherlabel' / 'copy.png'
        duplicate.write_bytes(self.original.read_bytes())
        (self.data / 'cat' / 'hello' / 'bad.jpg').write_bytes(b'not a real jpeg')
        (self.data / 'cat' / 'hello' / 'notes.txt').write_text('ignored')
        (self.data / 'loose.jpg').write_bytes(self.original.read_bytes())
        result = audit_module.audit(self.data, self.out)
        self.assertEqual((result['images'], result['classes'], result['readable'], result['unreadable'], result['duplicate_groups']), (3, 2, 2, 1, 1))
        duplicates = self.read_csv('duplicates.csv')
        self.assertEqual(len(duplicates), 2)
        self.assertTrue(all(row['cross_class'] == 'true' for row in duplicates))
        self.assertEqual(len(self.read_csv('ignored-files.csv')), 2)
        self.assertEqual(self.original.read_bytes(), duplicate.read_bytes())

    def test_output_inside_source_rejected(self):
        with self.assertRaisesRegex(ValueError, 'outside'):
            audit_module.audit(self.data, self.data / 'reports')

    def test_missing_or_wrong_layout_fails(self):
        with self.assertRaisesRegex(ValueError, 'does not exist'):
            audit_module.audit(self.root / 'missing', self.out)
        empty = self.root / 'empty'
        empty.mkdir()
        with self.assertRaisesRegex(ValueError, 'No images'):
            audit_module.audit(empty, self.out)

    def test_same_name_multiple_categories_and_empty_class(self):
        (self.data / 'other' / 'hello').mkdir()
        result = audit_module.audit(self.data, self.out)
        self.assertEqual(result['classes'], 3)
        report = (self.out / 'dataset-audit.md').read_text(encoding='utf-8')
        self.assertIn('Repeated label names across categories', report)
        self.assertEqual(len(self.read_csv('class-counts.csv')), 3)

    @unittest.skipUnless(hasattr(__import__('os'), 'symlink'), 'symlinks unavailable')
    def test_symlink_file_not_followed(self):
        link = self.data / 'cat' / 'hello' / 'link.png'
        try:
            link.symlink_to(self.original)
        except OSError:
            self.skipTest('symlink creation not permitted')
        result = audit_module.audit(self.data, self.out)
        self.assertEqual(result['images'], 1)
        self.assertEqual(self.read_csv('ignored-files.csv')[0]['reason'], 'symlink file skipped')


if __name__ == '__main__':
    unittest.main()
