# W7CH dataset audit

This is an automated, read-only audit, not a complete manual or linguistic review.

- Source data directory during the audit: `data/original/w7ch/Data` (reference copy not included in this ZIP; path shortened for portability)
- Source Git revision: `632ac7d309062c0df4c6512c2c968a01ba0b1232`
- Source: https://github.com/W7CH/First-ever-Tunisian-Sign-Language-Dataset
- Class identity is the pair category / folder label; no translations are invented.
- Image files in the expected layout: **4423**
- Class folders: **57**
- Categories: **5**
- Fully decoded images: **4423**; unreadable: **0**
- Ignored or misplaced files / symlinks: **0**
- Exact SHA-256 duplicate groups: **16**; files in those groups: **33**
- Duplicate groups spanning different category/class identities: **0**
- Label names appearing in multiple categories: **0**
- Smallest/largest class by file count: **15 / 224**

## Image dimensions (readable files)

| Width × height | Count |
| --- | ---: |
| 224 × 224 | 4423 |

## Images per class

| Category | Label (original folder) | All | Readable | Unreadable |
| --- | --- | ---: | ---: | ---: |
| Demandes | 3aslema | 51 | 51 | 0 |
| Demandes | 5adamet | 28 | 28 | 0 |
| Demandes | assam | 35 | 35 | 0 |
| Demandes | barnamjk | 91 | 91 | 0 |
| Demandes | chabeb | 53 | 53 | 0 |
| Demandes | cv | 56 | 56 | 0 |
| Demandes | demande | 34 | 34 | 0 |
| Demandes | enti | 57 | 57 | 0 |
| Demandes | labes | 21 | 21 | 0 |
| Demandes | lyoum | 50 | 50 | 0 |
| Demandes | mar7ba | 15 | 15 | 0 |
| Demandes | n3awnek | 87 | 87 | 0 |
| Demandes | nekteblk | 56 | 56 | 0 |
| Demandes | non | 78 | 78 | 0 |
| Demandes | oui | 94 | 94 | 0 |
| Demandes | radio | 120 | 120 | 0 |
| Demandes | se7a | 118 | 118 | 0 |
| Demandes | siye7a | 64 | 64 | 0 |
| Demandes | t7eb | 45 | 45 | 0 |
| Demandes | ta3lim | 76 | 76 | 0 |
| Demandes | ta3raf | 32 | 32 | 0 |
| Demandes | ta9ra | 39 | 39 | 0 |
| Demandes | telvza | 30 | 30 | 0 |
| Demandes | tha9afa | 70 | 70 | 0 |
| Destinations | baladya | 109 | 109 | 0 |
| Destinations | banka | 87 | 87 | 0 |
| Destinations | bousta | 50 | 50 | 0 |
| Destinations | dar | 79 | 79 | 0 |
| Destinations | ma7kma | 44 | 44 | 0 |
| Destinations | mostawsaf | 111 | 111 | 0 |
| Destinations | sbitar | 47 | 47 | 0 |
| Destinations | wzara | 81 | 81 | 0 |
| Famille | 3ayla | 81 | 81 | 0 |
| Famille | 5al-3am | 191 | 191 | 0 |
| Famille | 5ou | 186 | 186 | 0 |
| Famille | bent | 224 | 224 | 0 |
| Famille | bou | 138 | 138 | 0 |
| Famille | eben | 164 | 164 | 0 |
| Famille | jad | 172 | 172 | 0 |
| Famille | jadda | 154 | 154 | 0 |
| Famille | mar2a | 143 | 143 | 0 |
| Famille | o5t | 161 | 161 | 0 |
| Famille | om | 46 | 46 | 0 |
| Famille | tfol | 88 | 88 | 0 |
| Jours | 5mis | 54 | 54 | 0 |
| Jours | a7ad | 39 | 39 | 0 |
| Jours | erb3a | 66 | 66 | 0 |
| Jours | jom3a | 56 | 56 | 0 |
| Jours | sebt | 36 | 36 | 0 |
| Jours | thleth | 67 | 67 | 0 |
| Jours | thnin | 47 | 47 | 0 |
| Transport | car | 33 | 33 | 0 |
| Transport | karhba | 27 | 27 | 0 |
| Transport | louage | 38 | 38 | 0 |
| Transport | métro | 52 | 52 | 0 |
| Transport | taxi | 96 | 96 | 0 |
| Transport | train | 56 | 56 | 0 |

## Warnings and limitations

- SHA-256 identifies byte-identical files only, not near-duplicates or visually similar frames. Investigate duplicates and potential split leakage before training.
- Category/class folder names are used as labels; manual validation is needed. Empty class folders are included in the counts.
- Signer identities are **not established by this script**. Determine them from trustworthy metadata or state that signer independence is unknown.
- Lighting, background, framing, hand orientation, semantic correctness and license suitability require human review.
- Unusual extensions and files outside the expected category/class/image layout are listed in ignored-files.csv and excluded from image counts.
- The reported source revision is available only for a Git checkout; record your source, revision and license evidence independently.

## Files produced

- `images.csv`: one row per audited image, including checksum and decoding status.
- `class-counts.csv`: counts for each category/class folder.
- `duplicates.csv`: one row per file in a duplicate group; `cross_class=true` flags differing folder identities.
- `ignored-files.csv`: files or symlinks skipped by the auditor.

Write manual observations in a separate file, such as `reports/manual-review.md`; rerunning the audit replaces its generated reports.
