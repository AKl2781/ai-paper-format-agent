# Test Data Expansion Plan

## Current Gap

The existing regression corpus has a useful smoke set, but it is still too small for beta readiness:

- 10 manifest-driven synthetic DOCX samples.
- Real template files are present, but they are mostly template-only assets.
- Large stress files exist in runtime folders, not as a reproducible generated corpus.
- There is no single command to regenerate small, medium, and stress test samples.

## Expansion Strategy

Use `paper-ai/backend/generate_expanded_test_corpus.py` to generate local DOCX data under:

```text
paper-ai/backend/test_documents/generated/
```

Generated DOCX files are intentionally ignored by git through `test_documents/.gitignore`. The metadata file is:

```text
paper-ai/backend/test_documents/generated_manifest.csv
```

## Profiles

| Profile | Purpose | Output Scale |
| --- | --- | --- |
| quick | Fast local regression and UI sanity checks | 24 DOCX |
| medium | Broader beta compatibility checks | 53 DOCX |
| stress | Larger repeatability sweep before release | 100 DOCX |

## Covered Categories

| Category | Coverage |
| --- | --- |
| clean | Standard academic paper structure |
| messy | Mixed heading/body text, template residue, inconsistent structure |
| references | Number gaps, duplicate numbers, missing numbers, uncited patterns |
| figures_tables | Figure/table numbering, embedded images, Word tables |
| reports | Non-paper/lab-report style classification boundary |
| template_mismatch | Paper content with intentionally mismatched structure |
| medium | Larger paragraph, table, image, and reference volume |

## Usage

From `paper-ai/backend`:

```powershell
python .\generate_expanded_test_corpus.py --profile quick --clean
python .\generate_expanded_test_corpus.py --profile medium --clean
python .\generate_expanded_test_corpus.py --profile stress --clean
```

Recommended default for everyday work is `quick`. Use `medium` before beta demos, and `stress` before release candidates.

Run manifest-driven regression after generating or adding files:

```powershell
python .\run_real_doc_regression.py --manifest test_documents\generated_manifest.csv --mode local
python .\run_real_doc_regression.py --manifest test_documents\manifest.csv --mode local
```

For quick checks:

```powershell
python .\run_real_doc_regression.py --manifest test_documents\generated_manifest.csv --mode local --limit 3
python .\run_real_doc_regression.py --manifest test_documents\manifest.csv --mode local --category references
```

The regression script records `small`, `medium`, and `large` buckets based on file size.

## Real Source Intake

For CNKI journal submission and GB/T 7714 reference-format materials, use `CNKI_GBT7714_SOURCE_NOTES.md`.

Key rule: only public or authorized files may be stored locally. Login-only, paid, CAPTCHA-protected, or otherwise restricted full-text papers are not valid regression assets.

## Notes

- These are synthetic regression documents, not real user papers.
- Real user files must remain local unless fully desensitized.
- This data supports format Agent testing; it does not prove deep content rewriting quality.
