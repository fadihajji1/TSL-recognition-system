# Tunisian Sign Language recognition — Phase 1 starter

This is the first implementation phase of a research prototype for **isolated** Tunisian Sign Language image recognition. It includes a read-only dataset auditor and tests. It does **not** include a trained model, a web app, or the dataset itself.

**Full phase-by-phase guide:** [https://app.notion.com/p/b691b46b1a5640d6b1804a140b3f6e87](https://app.notion.com/p/b691b46b1a5640d6b1804a140b3f6e87)

## What's inside?

- `tools/audit_dataset.py` — checks a W7CH-style dataset without modifying it.
- `tests/test_audit_dataset.py` — automated tests for the audit code.
- `requirements.txt` — the Python library needed now (Pillow).
- `reports/verified-w7ch-audit/` — a reference audit of the source version mentioned below. Re-run it on your own copy.
- `docs/manual-review-template.md` — prompts for checking things a script cannot reliably judge.
- `data/original/` — where you will place the original dataset.

## Step 1: Install the tools

1. Install [Python 3.12](https://www.python.org/downloads/), [Git](https://git-scm.com/downloads), and [VS Code](https://code.visualstudio.com/). Python 3.11 also works as the recommended alternative. On Windows, check **Add Python to PATH** in the installer.
2. Open VS Code. Choose **File → Open Folder** and choose the extracted `tsl-recognition-starter` folder (the one containing this README).
3. Select **Terminal → New Terminal**. Keep the terminal open in that folder. Windows commands below assume PowerShell, not Command Prompt.

## Step 2: Create a virtual environment and run tests

A virtual environment is a private folder for this project's Python packages. You don't need to activate it; the commands call its Python directly.

**Windows PowerShell:**

```powershell
py -3.12 --version
git --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

If you installed Python 3.11 instead, replace `py -3.12` with `py -3.11`.

**macOS/Linux:**

```bash
python3 --version
git --version
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m unittest discover -s tests -v
```

Check that `python3 --version` shows 3.11 or 3.12, and use that interpreter if a different version is the default. The tests should finish with `OK`. In the reference environment, five tests passed using Python 3.13 and Pillow 13; Windows, macOS, and Python 3.11/3.12 were not independently tested here. If a command fails, stop and share the complete error.

## Step 3: Download the dataset

In the same terminal, run this once (both Windows and macOS/Linux):

```bash
git clone --depth 1 https://github.com/W7CH/First-ever-Tunisian-Sign-Language-Dataset.git data/original/w7ch
```

Wait for it to finish. You should now see `data/original/w7ch/Data/`, with category and sign subfolders. This download requires internet and disk space. If the destination already exists, inspect it instead of cloning over it. Don't edit, rename, or delete original dataset files.

Record your exact source revision:

```bash
git -C data/original/w7ch rev-parse HEAD
```

The repository states CC0-1.0; the supplied project documents note a different license for a Mendeley copy. Record where you obtained the data and independently verify license conditions before use or redistribution. Cite the dataset creators.

## Step 4: Run the audit

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe tools/audit_dataset.py --data-dir data/original/w7ch/Data --output-dir reports/dataset-audit
```

**macOS/Linux:**

```bash
./.venv/bin/python tools/audit_dataset.py --data-dir data/original/w7ch/Data --output-dir reports/dataset-audit
```

Open `reports/dataset-audit/dataset-audit.md` in VS Code. Other outputs are `images.csv`, `class-counts.csv`, `duplicates.csv`, and `ignored-files.csv`. CSV files can be opened in a spreadsheet application. Output folders must be outside the original dataset checkout. Rerunning overwrites the generated files in that output folder.

The auditor checks folder layout, image decoding, dimensions, per-class counts and byte-identical SHA-256 duplicates. It cannot identify signers, detect visually similar but non-identical frames, validate meaning, or assess lighting/background reliably. Copy `docs/manual-review-template.md` to `reports/manual-review.md` and fill it in after looking at the data. Do not guess signer identities. Investigate duplicates before splitting; preserve or group identical files so no identical image appears in multiple splits.

## Reference results from the first real audit

At Git revision `632ac7d309062c0df4c6512c2c968a01ba0b1232`, the audit found 4,423 readable images, 57 class folders, no unreadable images and 16 exact duplicate groups containing 33 files. No exact duplicate groups crossed class folders; class sizes ranged from 15 to 224. This does not establish signer-independent evaluation or guarantee the quality of the images or labels. Source: [https://github.com/W7CH/First-ever-Tunisian-Sign-Language-Dataset](https://github.com/W7CH/First-ever-Tunisian-Sign-Language-Dataset)

## What comes next? (not yet implemented)

1. Finish manual review and establish whether signer metadata is trustworthy.
2. Design a reproducible train/validation/test split, ideally by signer; prevent duplicate and near-duplicate leakage and document any unknowns.
3. Create a derived dataset, deterministic validation/inference preprocessing and training-only conservative augmentation.
4. Train and evaluate a ResNet18 baseline, record metrics and experiment details, then compare models.
5. Build a Python FastAPI service and a React camera interface. Test real-time performance.
6. Investigate video/temporal recognition and a browser extension only later. Static images alone do not support continuous TSL translation.

For the detailed checkpoints and explanations, use the full Notion guide linked at the top. Once Phase 1 is complete, share your operating system, GPU information, and the report (or your first complete error) for the next phase.