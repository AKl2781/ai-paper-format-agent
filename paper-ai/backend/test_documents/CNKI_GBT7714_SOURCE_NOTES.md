# CNKI / GB/T 7714 Test Source Notes

## Purpose

This note defines how to expand the local DOCX regression corpus with CNKI journal submission and GB/T 7714 reference-format materials.

The goal is to improve real-world coverage for:

- Journal-style paper structure.
- GB/T 7714 reference formatting.
- Small, medium, and large DOCX handling.
- Template mismatch and reference-check edge cases.

## Legal and Data Rules

Use only materials that are legal to store and test locally:

1. Publicly downloadable journal templates, submission templates, author instructions, or sample DOCX files.
2. User-provided papers that the user is authorized to use.
3. Fully desensitized local copies with names, student IDs, phone numbers, email addresses, tutors, signatures, QR codes, and internal school numbers removed.

Do not add:

1. CNKI full-text papers behind login, payment, CAPTCHA, or other access controls.
2. CAJ/PDF copies obtained from unauthorized mirrors.
3. Any file that contains real personal information.
4. Any source that markets the local check as CNKI, VIP, or Wanfang plagiarism checking.

The product wording remains "重复风险检测" and "相似度预检".

## Recommended Size Buckets

| Bucket | File size | Purpose |
| --- | ---: | --- |
| small | < 1 MB | Fast smoke and UI upload/download checks |
| medium | 1-10 MB | Beta compatibility and common thesis/report files |
| large | >= 10 MB | Resource and performance regression checks |

## Recommended Categories

| Category | Examples |
| --- | --- |
| clean | Standard journal paper structure with title, abstract, keywords, body, references |
| messy | Mixed heading/body text, inconsistent font, template residue |
| references | GB/T 7714 examples, missing reference numbers, duplicate numbers, uncited entries |
| figures_tables | Figure/table numbering and caption edge cases |
| reports | Lab reports, course reports, proposal reports, literature reviews |
| template_mismatch | Paper content paired with a mismatched submission/thesis template |

## Public Source Candidates

These public pages can be used as source leads. Download only files that are publicly accessible and allowed for local testing.

| Source | URL | Use |
| --- | --- | --- |
| CNKI CBPT journal article/submission pages | `https://*.cbpt.cnki.net/portal/journal/portal/client/paper/...` | GB/T 7714 citation text and journal-style structure references |
| CNKI publishmedia public attachments | `https://publishmedia.cbpt.cnki.net/portal/minio/...` | Public submission instructions or formatting PDF attachments |
| Journal download centers | Journal-specific "论文模板", "投稿须知", "下载中心" pages | DOCX templates and author instructions |
| University official sites | `site:edu.cn filetype:docx 毕业论文 模板` | Public thesis/report templates |

## Suggested Search Queries

```text
site:cbpt.cnki.net "GB/T 7714-2015" "投稿须知"
site:cbpt.cnki.net "论文模板" "下载中心" "docx"
site:publishmedia.cbpt.cnki.net "GB/T 7714" "投稿须知"
site:edu.cn filetype:docx 毕业论文 模板
site:edu.cn filetype:docx 学术论文 模板
site:edu.cn filetype:docx 实验报告 模板
```

## Intake Workflow

1. Download only public or authorized files.
2. Desensitize the file if it contains real people or school-internal data.
3. Place it under the matching `test_documents/` category.
4. Add a row to `test_documents/manifest.csv`.
5. Run:

```powershell
python .\run_real_doc_regression.py --manifest test_documents\manifest.csv --mode local
```

6. Review `regression_results/<run_id>/summary.csv` and `summary.json`.

## Manifest Notes

When adding small/medium/large files, keep `known_risks` descriptive:

- `gbt7714_reference_format`
- `journal_submission_template`
- `large_docx_performance`
- `template_mismatch`
- `contains_figures_tables`
- `non_paper_confirmation`
