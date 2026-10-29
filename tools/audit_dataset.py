#!/usr/bin/env python3
"""Read-only audit of a W7CH-style Data/category/class/image tree.

Writes reports elsewhere; it never edits, removes or moves input files.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
from collections import Counter, defaultdict
from pathlib import Path
import subprocess
import sys
import warnings

from PIL import Image, UnidentifiedImageError

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'}
FIELDS = ['relative_path', 'category', 'label', 'sha256', 'status', 'width', 'height', 'format', 'mode', 'error']


def git_revision(path: Path) -> str:
    try:
        result = subprocess.run(['git', '-C', str(path), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True, timeout=10)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 'unknown (not a Git checkout or Git unavailable)'


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def safe_text(value: object) -> str:
    return str(value).replace('|', r'\|').replace('\n', ' ').replace('\r', ' ')


def audit(data_dir: Path, output_dir: Path) -> dict:
    data_dir = data_dir.resolve()
    output_dir = output_dir.resolve()
    if not data_dir.is_dir():
        raise ValueError(f'Dataset directory does not exist: {data_dir}')
    if output_dir == data_dir or data_dir in output_dir.parents:
        raise ValueError('The output directory must be outside the dataset directory.')
    # A W7CH clone includes its own .git directory. Never write reports anywhere
    # inside that original checkout, not just under its Data subdirectory.
    original_root = data_dir.parent if (data_dir.parent / '.git').exists() else data_dir
    if output_dir == original_root or original_root in output_dir.parents:
        raise ValueError('The output directory must be outside the original dataset checkout.')

    rows = []
    ignored = []
    labels_by_category = set()
    # Deterministic ordering makes repeated audits easy to compare.
    def walk_error(error):
        raise OSError(f'Cannot read dataset directory: {error}')
    for root, dirs, files in os.walk(data_dir, followlinks=False, onerror=walk_error):
        root_path = Path(root)
        for name in list(dirs):
            item = root_path / name
            if item.is_symlink():
                ignored.append((item.relative_to(data_dir).as_posix(), 'symlink directory skipped'))
                dirs.remove(name)
        dirs.sort()
        files.sort()
        parts = root_path.relative_to(data_dir).parts
        if len(parts) == 2:
            labels_by_category.add((parts[0], parts[1]))
        for filename in files:
            path = root_path / filename
            rel = path.relative_to(data_dir).as_posix()
            if path.is_symlink():
                ignored.append((rel, 'symlink file skipped'))
            elif path.suffix.lower() not in IMAGE_EXTENSIONS:
                ignored.append((rel, 'non-image extension'))
            elif len(parts) != 2:
                ignored.append((rel, 'image not directly inside category/class'))
            else:
                category, label = parts
                row = dict.fromkeys(FIELDS, '')
                row.update(relative_path=rel, category=category, label=label)
                try:
                    row['sha256'] = sha256_file(path)
                    # Verify checks structure; a fresh load also checks decoding.
                    with warnings.catch_warnings():
                        warnings.simplefilter('error', Image.DecompressionBombWarning)
                        with Image.open(path) as image:
                            image.verify()
                        with Image.open(path) as image:
                            image.load()
                            row.update(width=image.width, height=image.height, format=image.format or '', mode=image.mode)
                    row['status'] = 'readable'
                except (OSError, ValueError, SyntaxError, UnidentifiedImageError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
                    row.update(status='unreadable', error=f'{type(exc).__name__}: {exc}')
                rows.append(row)
    if not rows:
        raise ValueError('No images found directly under category/class folders; check --data-dir and the dataset layout.')

    counts = Counter((r['category'], r['label'], r['status']) for r in rows)
    class_rows = []
    for category, label in sorted(labels_by_category):
        good = counts[(category, label, 'readable')]
        bad = counts[(category, label, 'unreadable')]
        class_rows.append({'category': category, 'label': label, 'image_files': good + bad, 'readable': good, 'unreadable': bad})
    groups = defaultdict(list)
    for row in rows:
        if row['sha256']:
            groups[row['sha256']].append(row)
    duplicate_groups = {h: members for h, members in groups.items() if len(members) > 1}
    duplicates = []
    for digest, members in sorted(duplicate_groups.items()):
        cross_class = len({(r['category'], r['label']) for r in members}) > 1
        for member in members:
            duplicates.append({'sha256': digest, 'group_size': len(members), 'cross_class': str(cross_class).lower(), 'relative_path': member['relative_path'], 'category': member['category'], 'label': member['label'], 'status': member['status']})
    distinct_label_categories = defaultdict(set)
    for category, label in labels_by_category:
        distinct_label_categories[label].add(category)
    repeated_labels = {label: sorted(cats) for label, cats in distinct_label_categories.items() if len(cats) > 1}
    readable = [r for r in rows if r['status'] == 'readable']
    unreadable = [r for r in rows if r['status'] == 'unreadable']
    dimensions = Counter((r['width'], r['height']) for r in readable)
    cross_groups = sum(len({(r['category'], r['label']) for r in members}) > 1 for members in duplicate_groups.values())
    revision = git_revision(data_dir)
    size = [r['image_files'] for r in class_rows]
    lines = [
        '# W7CH dataset audit', '',
        'This is an automated, read-only audit, not a complete manual or linguistic review.', '',
        f'- Source data directory: `{data_dir}`',
        f'- Source Git revision: `{revision}`',
        '- Source: https://github.com/W7CH/First-ever-Tunisian-Sign-Language-Dataset',
        '- Class identity is the pair category / folder label; no translations are invented.',
        f'- Image files in the expected layout: **{len(rows)}**',
        f'- Class folders: **{len(class_rows)}**',
        f'- Categories: **{len({c for c, _ in labels_by_category})}**',
        f'- Fully decoded images: **{len(readable)}**; unreadable: **{len(unreadable)}**',
        f'- Ignored or misplaced files / symlinks: **{len(ignored)}**',
        f'- Exact SHA-256 duplicate groups: **{len(duplicate_groups)}**; files in those groups: **{len(duplicates)}**',
        f'- Duplicate groups spanning different category/class identities: **{cross_groups}**',
        f'- Label names appearing in multiple categories: **{len(repeated_labels)}**',
        f'- Smallest/largest class by file count: **{min(size)} / {max(size)}**', '',
        '## Image dimensions (readable files)', '', '| Width × height | Count |', '| --- | ---: |',
    ]
    for (width, height), count in sorted(dimensions.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f'| {width} × {height} | {count} |')
    lines += ['', '## Images per class', '', '| Category | Label (original folder) | All | Readable | Unreadable |', '| --- | --- | ---: | ---: | ---: |']
    for r in class_rows:
        lines.append(f"| {safe_text(r['category'])} | {safe_text(r['label'])} | {r['image_files']} | {r['readable']} | {r['unreadable']} |")
    lines += ['', '## Warnings and limitations', '',
              '- SHA-256 identifies byte-identical files only, not near-duplicates or visually similar frames. Investigate duplicates and potential split leakage before training.',
              '- Category/class folder names are used as labels; manual validation is needed. Empty class folders are included in the counts.',
              '- Signer identities are **not established by this script**. Determine them from trustworthy metadata or state that signer independence is unknown.',
              '- Lighting, background, framing, hand orientation, semantic correctness and license suitability require human review.',
              '- Unusual extensions and files outside the expected category/class/image layout are listed in ignored-files.csv and excluded from image counts.',
              '- The reported source revision is available only for a Git checkout; record your source, revision and license evidence independently.', '']
    if repeated_labels:
        lines.extend(['### Repeated label names across categories', ''])
        for label, cats in sorted(repeated_labels.items()):
            lines.append(f"- {safe_text(label)}: {safe_text(', '.join(cats))}")
        lines.append('')
    lines += ['## Files produced', '', '- `images.csv`: one row per audited image, including checksum and decoding status.', '- `class-counts.csv`: counts for each category/class folder.', '- `duplicates.csv`: one row per file in a duplicate group; `cross_class=true` flags differing folder identities.', '- `ignored-files.csv`: files or symlinks skipped by the auditor.', '', 'Write manual observations in a separate file, such as `reports/manual-review.md`; rerunning the audit replaces its generated reports.', '']
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / 'images.csv', FIELDS, rows)
    write_csv(output_dir / 'class-counts.csv', ['category', 'label', 'image_files', 'readable', 'unreadable'], class_rows)
    write_csv(output_dir / 'duplicates.csv', ['sha256', 'group_size', 'cross_class', 'relative_path', 'category', 'label', 'status'], duplicates)
    write_csv(output_dir / 'ignored-files.csv', ['relative_path', 'reason'], [{'relative_path': path, 'reason': reason} for path, reason in ignored])
    (output_dir / 'dataset-audit.md').write_text('\n'.join(lines), encoding='utf-8')
    return {'images': len(rows), 'classes': len(class_rows), 'readable': len(readable), 'unreadable': len(unreadable), 'duplicate_groups': len(duplicate_groups), 'output_dir': output_dir}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', required=True, type=Path, help='Path to W7CH Data folder (category/class/image)')
    parser.add_argument('--output-dir', required=True, type=Path, help='Report folder OUTSIDE original dataset')
    args = parser.parse_args()
    try:
        result = audit(args.data_dir, args.output_dir)
    except (ValueError, OSError) as exc:
        print(f'Audit failed: {exc}', file=sys.stderr)
        return 2
    print(f"Audited {result['images']} images in {result['classes']} class folders: {result['readable']} readable, {result['unreadable']} unreadable, {result['duplicate_groups']} exact duplicate groups.")
    print(f"Reports: {result['output_dir']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
