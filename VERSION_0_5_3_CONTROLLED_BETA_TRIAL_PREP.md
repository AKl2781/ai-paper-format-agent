# v0.5.3 Controlled Beta Trial Prep

Prep date: 2026-06-08

## Version Line

`v0.5.3 / controlled-beta-trial-prep`

This preparation follows `v0.5.2 / beta-readiness-audit`. It does not add product features and does not modify formatter, agent, API, frontend, or classifier business logic.

## Trial Positioning

The product should be introduced as a controlled beta format Agent:

- It can help normalize DOCX format, detect document type, generate a modification report, provide an HTML preview, and produce a downloadable DOCX.
- It includes repeated-risk detection and similarity precheck features.
- It is not yet a full thesis rewriting Agent.
- AI mode can provide language suggestions, but current content-level changes remain shallow and must be reviewed by the user.

Do not describe the product as a CNKI, VIP, or Wanfang plagiarism checker. Use only:

- 重复风险检测
- 相似度预检

## Trial Users

Recommended first group:

- 3 to 5 trusted users.
- Users who can provide non-sensitive or already-authorized DOCX samples.
- Users who understand the tool is currently a beta format Agent.
- Users willing to compare the output DOCX manually against their source document.

Avoid in this round:

- Users expecting final academic content rewriting.
- Users with only confidential, paid, or restricted full-text documents.
- Users who need pixel-perfect Word preview inside the browser.

## Document Eligibility

Allowed:

- Public, authorized, or user-owned DOCX files.
- Desensitized academic papers, course reports, lab reports, and template-mismatch samples.
- DOCX files below 100MB for the first controlled beta round.

Not allowed:

- Login-only, paid, captcha-protected, or authorization-restricted CNKI full-text documents.
- Documents containing sensitive personal, institutional, or unpublished research data unless the user explicitly authorizes testing.
- Non-DOCX formats for the core workflow.

## Trial Tasks

Each tester should run at least one document through this path:

1. Upload DOCX.
2. Confirm classification result.
3. Run local mode.
4. Review before/after score and modification report.
5. Open preview.
6. Download output DOCX.
7. Open output DOCX in Word/WPS.
8. Check whether formatting changes are useful and whether content was unexpectedly altered.

Optional second pass:

1. Upload a template DOCX.
2. Run local mode with the template.
3. Compare output format against the expected school or journal style.

Optional AI pass:

1. Run AI mode on a non-sensitive sample.
2. Confirm the main flow does not break if AI is unavailable.
3. Review whether language suggestions are useful enough to keep as beta behavior.

## Acceptance Criteria

Blocking failure if any of these occur:

- Upload fails for valid DOCX.
- Agent run crashes.
- local mode returns `ai_used=true`.
- local mode returns non-null `ai_score`.
- Output DOCX is missing.
- Modification report is missing.
- Preview endpoint fails.
- Download endpoint fails.
- Output DOCX cannot be opened.
- Formatting operation removes major content unexpectedly.

Non-blocking warning if:

- Classification lands in a known explainable boundary, such as `lab_report` / `academic_paper`.
- Preview differs from Word layout but still exposes readable structure.
- AI suggestions are shallow but the main flow remains stable.
- Report wording needs refinement but required fields exist.

## Feedback Form

Collect these fields per tester:

| Field | Description |
| --- | --- |
| Tester ID | Anonymous identifier |
| Document type | User-perceived type |
| File size | Approximate MB |
| Template used | Yes / No |
| Mode | local / ai |
| Upload result | PASS / FAIL |
| Classification result | Expected / Unexpected / Boundary |
| Report usefulness | 1-5 |
| Preview usefulness | 1-5 |
| Output DOCX openable | Yes / No |
| Formatting usefulness | 1-5 |
| Unexpected content change | Yes / No |
| Blocking issue | Yes / No |
| Notes | Free text |

## Trial Exit Criteria

The controlled beta round can be considered successful if:

- At least 5 valid DOCX runs complete.
- Blocking failures remain 0.
- local `ai_score=null` and `ai_used=false` hold for every local run.
- Every generated DOCX is downloadable and openable.
- At least 70% of runs receive formatting usefulness score >= 4.
- No tester reports misleading product positioning.

Pause the trial if:

- Any valid DOCX repeatedly crashes the Agent.
- Any local run violates AI score semantics.
- Output DOCX corruption appears.
- A tester reports unexpected removal of important content.
- Users repeatedly misunderstand the product as a deep content-rewriting Agent.

## Regression Baseline Before Trial

Use the existing v0.5.2 baseline:

- `manifest.csv`: 10 PASS / 0 boundary warning / 0 FAIL.
- `generated_manifest.csv`: 21 PASS / 3 boundary warning / 0 FAIL.
- `heavy_manifest.csv`: 1 PASS / 0 boundary warning / 0 FAIL.
- smoke: PASS.
- frontend build: PASS.
- blocking FAIL: 0.

## Next Step

After the first controlled beta round, create a short beta feedback audit:

```text
BETA_FEEDBACK_AUDIT.md
```

It should summarize trial sample count, blocking failures, user confusion points, report quality feedback, preview quality feedback, and whether v0.5.4 should focus on UI polish, report wording, or content-Agent capability.
