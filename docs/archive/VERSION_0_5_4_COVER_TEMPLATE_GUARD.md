# v0.5.4 Cover Template Guard Audit

Date: 2026-06-09

## Status

This is a v0.5.4 readiness audit for the cover-page preservation and template-instruction filtering fix.

No tag was created in this round. The existing v0.5.3 tag/status remains unchanged until the change is reviewed and committed.

## Problem

A real course-paper template exposed a layout regression:

- The first page was a course-paper cover with manually aligned form fields.
- The formatter treated the cover page as normal body text.
- Full-width spaces, left indents, and cover alignment were normalized away.
- The uploaded template was converted from legacy `.doc` to `.docx`; its cover and instruction paragraphs, such as `排版要求`, `内容要求`, and `以下为正文`, were sampled as body style.
- As a result, normal body paragraphs could become centered, producing visually distorted output.

## Modified Files

- `paper-ai/backend/services/docx_formatter.py`
- `paper-ai/backend/services/template_extractor.py`
- `paper-ai/backend/test_formatter_mixed_heading.py`

No frontend files were changed.

No API contract was changed.

## Fix Strategy

### Cover Protection

`docx_formatter.py` now detects a first-page course-paper cover when:

- The first page contains a page break.
- The first page contains course-paper cover markers such as course, name, student number, college, major, class, or teaching-office form text.
- The first page title matches common cover labels such as `课程论文`.

When detected, the cover page is protected from:

- Placeholder cleanup.
- Mixed-heading splitting.
- Long-paragraph splitting.
- Body-style normalization.

This preserves cover alignment, full-width spacing, and form-field layout.

### Template Instruction Filtering

`template_extractor.py` now skips template paragraphs that are not real body samples:

- Cover text and form fields.
- Paragraphs containing page breaks.
- Template instructions such as `排版要求`, `内容要求`, `以下为正文`, `提交最终稿`, font, size, line-spacing, or indent instructions.

If no valid body paragraph is found, the extractor falls back to the default paper body format instead of sampling a cover or instruction paragraph.

### Regression Coverage

`test_formatter_mixed_heading.py` now covers:

- Existing inline numbered-heading split behavior.
- Course-paper cover preservation.
- Prevention of template-cover or template-instruction style pollution.
- Direct execution via `python .\test_formatter_mixed_heading.py`.

## Regression Results

### Required Commands

```text
python -m py_compile services\docx_formatter.py services\template_extractor.py
python .\test_formatter_mixed_heading.py
python .\run_real_doc_regression.py --manifest test_documents\manifest.csv --mode local
python .\run_real_doc_regression.py --manifest test_documents\generated_manifest.csv --mode local
python .\run_real_doc_regression.py --manifest test_documents\heavy_manifest.csv --mode local
python .\test_smoke_agent_flow.py
npm run build
```

### Results

| Check | Result |
| --- | --- |
| `py_compile` for formatter/extractor | PASS |
| `python .\test_formatter_mixed_heading.py` | PASS |
| `manifest.csv` local regression | PASS: 10 PASS, 0 boundary warnings, 0 FAIL |
| `generated_manifest.csv` local regression | PASS: 21 PASS, 3 boundary warnings, 0 FAIL |
| `heavy_manifest.csv` local regression | PASS: 1 PASS, 0 boundary warnings, 0 FAIL |
| `test_smoke_agent_flow.py` | PASS |
| `npm run build` | PASS |

Regression run directories:

- `paper-ai/backend/regression_results/20260609_195337`
- `paper-ai/backend/regression_results/20260609_195358`
- `paper-ai/backend/regression_results/20260609_195444`

### Generated Manifest Boundary Check

`generated_manifest.csv` remains PASS with known classification boundary warnings:

- `reports_001`: expected `lab_report`, got `academic_paper`
- `reports_002`: expected `lab_report`, got `academic_paper`
- `reports_003`: expected `lab_report`, got `academic_paper`

These remain `BOUNDARY_WARNING`, not blocking `FAIL`.

### Heavy Document Preservation Check

`heavy_manifest.csv` remains PASS.

Heavy document structure audit:

| Metric | Before | After |
| --- | ---: | ---: |
| Paragraphs | 2489 | 2489 |
| Tables | 80 | 80 |
| Images | 100 | 100 |
| Sections | 1 | 1 |

No paragraph, table, or image count drop was observed.

### Lychee Course-Paper Real Sample

Real sample checked:

- Paper: `D:\新下载\荔枝果蔬营养与保健课程论文_未填个人信息版.docx`
- Template: legacy `.doc` course-paper template, temporarily converted to `.docx` for this audit.

Output checked:

- `paper-ai/backend/outputs/trial_lychee_paper_formatted_20260609195902.docx`

Audit result:

- Cover preserved: PASS.
- Full-width cover spacing preserved: PASS.
- Cover left indent preserved at about 3.0 cm: PASS.
- Template instructions did not leak into output: PASS.
- Body text no longer centered: PASS.
- Output DOCX opens with `python-docx`: PASS.
- Preview endpoint: PASS, HTTP 200.
- Download endpoint: PASS, HTTP 200.
- Local mode fields: preserved across full regression, `ai_score=null`, `ai_used=false`.

## Known Limitations

- Legacy `.doc` templates are still not accepted directly by the current upload API.
- A `.doc` template must still be converted to `.docx` before it can be used by the Agent.
- This round did not add automatic `.doc` conversion, did not change the frontend, and did not change API behavior.
- Complex templates with headers, footers, tables used as forms, footnotes, image captions, formula numbering, or unusual section layouts still require continued testing.

## Recommendation

No blocking FAIL was found in this audit.

This fix is suitable to submit as a focused v0.5.4 candidate after review.

Recommended v0.5.4 scope:

- Cover-page preservation guard.
- Template instruction filtering guard.
- Regression documentation only.

