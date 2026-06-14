# Fixed Demo Case

Version: `v0.6.2-demo-samples`

This document describes a recommended fixed interview demo case for the AI Paper Formatting Agent. It is a demo plan and sample specification, not proof that real DOCX files are already included in the repository.

## Demo Goal

Show the complete closed loop of the paper formatting Agent:

```text
upload -> agent_pipeline -> format/check/report -> output
```

The demo should make it clear that the project can:

- upload a DOCX paper sample;
- optionally upload a DOCX template sample;
- run the Agent through `agent_pipeline`;
- produce format/check/report results;
- expose `agent_trace`;
- preview and download the generated document.

## Input Sample Description

Recommended input path:

- Paper sample: `demo_inputs/messy_paper_sample.docx`
- Template sample: `demo_inputs/template_sample.docx`

These are recommended paths and file names. If the files do not actually exist in the repository, do not say they are built in.

### Paper Sample Should Show

The paper sample should be de-identified and small enough for a live demo. It should preferably include:

- inconsistent heading formats;
- body indentation or line spacing that needs cleanup;
- at least one reference/citation checkpoint;
- at least one figure/table numbering checkpoint;
- enough normal paper structure to be recognized as an academic paper.

### Template Sample Should Show

The template sample should be de-identified and simple. It can be used to show:

- optional template upload;
- how the system attempts template parsing;
- how the system can continue with fallback/default rules when template information is incomplete.

## Recommended Sample Features

Use a sample that includes several of these issues:

- title formats are inconsistent;
- body indentation or line spacing is not standard;
- reference numbering or citation has a checkable point;
- figure/table numbering has a checkable point;
- the document is still close enough to a real paper that classification can reasonably pass.

Avoid using:

- private or sensitive papers;
- final official submission papers;
- copyrighted full papers without permission;
- files that are too large for a short interview demo.

## Processing Flow

```mermaid
flowchart TD
    A["Upload paper sample"] --> B["Optional template sample"]
    B --> C["/agent/run"]
    C --> D["agent_pipeline.py"]
    D --> E["paper_agent.py"]
    E --> F["Format repair"]
    F --> G["Reference and figure/table checks"]
    G --> H["Modification report"]
    H --> I["agent_trace"]
    I --> J["Preview and download"]
```

## Key Outputs to Observe

During the demo, focus on these fields:

- `modification_report`
  - Explains what was automatically handled and what still needs manual review.
- `reference_check`
  - Shows reference section and citation checkpoints.
- `figure_table_check`
  - Shows figure/table numbering and reference checkpoints.
- `agent_trace`
  - Shows step, status, duration, fallback usage, and message.
- `before_score` / `after_score`
  - Shows the score before and after processing.

Recommended output paths after a real run:

- `demo_outputs/formatted_result_sample.docx`
- `demo_outputs/report_sample.json`
- `demo_outputs/agent_trace_sample.json`

These are recommended names only. Do not claim these files exist unless they are created by an actual run.

## One-Minute Interview Talk Track

> This demo shows the full loop of my paper formatting Agent. I upload a DOCX paper, optionally upload a template, and the backend routes the task through `agent_pipeline`. The core Agent then classifies the document, repairs formatting, checks references and figure/table numbering, runs local or AI-assisted review with fallback, and returns a structured report. The important part is that the result is not a black box: `agent_trace` records each step, status, duration, fallback usage, and message. The project is intentionally positioned as a formatting Agent, not a paper-writing or formal plagiarism-checking system.

## Current Limitations

- This document is only a demo case specification.
- If the repository does not contain real `.docx` files, do not claim real demo samples are built in.
- The next step is to add de-identified real paper/template samples and save one real output set.
- Current AI mode is still a language-review enhancement; it is not deep content rewriting.
- Similarity checking is only duplicate risk detection / similarity pre-check, not formal plagiarism checking.
