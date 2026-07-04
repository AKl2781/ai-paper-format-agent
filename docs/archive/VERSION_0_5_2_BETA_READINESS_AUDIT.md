# v0.5.2 Beta Readiness Audit

Audit date: 2026-06-08

## Version Line

`v0.5.2 / beta-readiness-audit`

This audit follows the frozen `v0.5.1 / real-doc-regression-boundary-pass` baseline. It does not add product features and does not modify formatter, agent, API, frontend, or classifier business logic.

## Decision

Controlled beta remains ready for the current product scope: a format Agent with upload, classification, local formatting, report, preview, download, and regression coverage.

It should not be positioned as a full content-rewriting thesis Agent yet. AI mode still mainly provides shallow language suggestions and fallback-safe scoring.

## Verification Results

| Check | Result | Evidence |
| --- | --- | --- |
| `manifest.csv` local regression | PASS | 10 PASS / 0 boundary warning / 0 FAIL |
| `generated_manifest.csv` local regression | PASS with boundary warnings | 21 PASS / 3 boundary warning / 0 FAIL |
| `heavy_manifest.csv` local regression | PASS | 1 PASS / 0 boundary warning / 0 FAIL |
| Smoke Agent flow | PASS | `SMOKE PASS` |
| Frontend production build | PASS | `npm run build` completed successfully |

Blocking FAIL: 0

Boundary warnings: 3

## Regression Run Evidence

| Manifest | Run Directory | Result |
| --- | --- | --- |
| `test_documents/manifest.csv` | `paper-ai/backend/regression_results/20260608_002201/` | 10 PASS / 0 boundary warning / 0 FAIL |
| `test_documents/generated_manifest.csv` | `paper-ai/backend/regression_results/20260608_002215/` | 21 PASS / 3 boundary warning / 0 FAIL |
| `test_documents/heavy_manifest.csv` | `paper-ai/backend/regression_results/20260608_002419/` | 1 PASS / 0 boundary warning / 0 FAIL |

The 3 boundary warnings are the known `reports_001`, `reports_002`, and `reports_003` samples. They remain explainable `lab_report` / `academic_paper` classification boundary cases and are not blocking functional failures.

## Heavy DOCX Result

| Item | Result |
| --- | --- |
| Case | `heavy_001` |
| File | `test_documents/real/realistic_heavy_thesis.docx` |
| Size | 78,427,713 bytes |
| Size bucket | `large` |
| Expected type | `academic_paper` |
| Actual type | `academic_paper` |
| Status | PASS |
| Elapsed | 61.671s |
| Before / after score | 81 -> 84 |
| Output DOCX | generated |
| Report / preview / download | PASS |
| local `ai_score` | `null` |
| local `ai_used` | `false` |

## Beta Readiness Coverage

| Area | Status | Notes |
| --- | --- | --- |
| Upload flow | PASS | Covered by smoke and regression sample loading |
| Template flow | PASS | Covered by smoke template case |
| Local mode | PASS | `ai_score=null`, `ai_used=false` verified |
| AI fallback | PASS | Smoke fallback path completed without blocking |
| Report generation | PASS | Regression validates report presence |
| Preview | PASS | Regression and smoke validate preview endpoint |
| Download | PASS | Regression and smoke validate download endpoint |
| Frontend build | PASS | Next.js production build completed |
| Large DOCX handling | PASS | 74.79MB-class sample completed local regression |

## Remaining Risks

Medium:

- AI content modification remains shallow and should not be marketed as deep thesis rewriting.
- Report wording must continue to avoid overstating AI content improvement.
- Reference detection can still require manual review on complex papers.
- Complex Word elements such as TOC, headers/footers, footnotes, comments, equations, and image captions remain partially supported.
- Classification boundary cases remain possible between `lab_report`, `academic_paper`, and weak-structure papers.

Low:

- HTML preview is a structural preview, not pixel-perfect Word rendering.
- Runtime output directories under `regression_results/`, `uploads/`, and `outputs/` can accumulate.
- Terminal-side Chinese encoding display can still be confusing in some PowerShell views.

## Temporary Output Directories

This audit generated new untracked regression output directories:

- `paper-ai/backend/regression_results/20260608_002201/`
- `paper-ai/backend/regression_results/20260608_002215/`
- `paper-ai/backend/regression_results/20260608_002419/`

They are evidence artifacts and are not required for source control unless a later release policy chooses to keep representative snapshots.

## Final Conclusion

PASS.

`v0.5.2 / beta-readiness-audit` confirms that the frozen v0.5.1 baseline is suitable for controlled beta as a format Agent. There are no blocking failures. The next product step should focus on either controlled user trial preparation or the first narrow content-Agent capability, with clear product wording around current AI limitations.
