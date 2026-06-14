# Demo Outputs

This directory is reserved for interview/demo output artifacts.

Recommended files to place here after running a real demo:

- `formatted_result_sample.docx`
  - The generated Word document after the Agent finishes formatting and checks.
- `report_sample.json`
  - A saved response or report excerpt containing fields such as `modification_report`, `reference_check`, `figure_table_check`, and scores.
- `agent_trace_sample.json`
  - A saved `agent_trace` example showing step, status, duration, fallback usage, and message.

Current note:

- This README does not mean these output files already exist.
- Do not claim a PASS result or generated sample output unless the files are actually created by a real run.
- Future work can place de-identified output examples here after running the demo sample through the current Agent.

Suggested usage:

1. Run the demo input through the existing `/agent/run` flow.
2. Save the generated DOCX as `demo_outputs/formatted_result_sample.docx`.
3. Save the report/response excerpt as `demo_outputs/report_sample.json`.
4. Save the trace excerpt as `demo_outputs/agent_trace_sample.json`.
