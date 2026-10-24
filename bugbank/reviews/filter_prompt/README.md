# Human-feedback criteria for the corpus audit

These two saved documents show how comments from the initial human review informed a subsequent automated audit of 425 dossiers. The audit guidance identifies checks derived from those comments; the schema specifies the evidence and decisions that the automated audit had to record.

- [Audit guidance](audit_guidance.md): ten checks, with concrete examples and additional reservations recorded alongside positive human judgments.
- [Audit schema](FINAL_AUDIT_SCHEMA.md): required evidence fields, retention criteria, and rules for correcting a witness or its description.

The initial human answers are available in [original100/answers.json](../original100/answers.json). These documents preserve the criteria used at that stage. They do not replace the saved human answers or the current membership decisions. The later human reviews and author-confirmed continuity are represented in the [current membership ledger](../../core/membership.json) and [continuity receipt](../../core/author_continuity_receipt.json).

Both documents are copied byte for byte from the saved audit materials. Inspection found no human-reviewer names, email addresses, private absolute paths, or credentials in either document, so the redaction map is empty. Record IDs, scientific examples, evidence-field names, and the original instructions are preserved. Model-dispatch notes and operational handoff material are outside this export.

| File | Original SHA-256 | Public SHA-256 | Redactions |
| --- | --- | --- | --- |
| `audit_guidance.md` | `57e378d08fb7844ed3506746a227202357b07165a7e1254cd7760a6df981d1b4` | `57e378d08fb7844ed3506746a227202357b07165a7e1254cd7760a6df981d1b4` | None |
| `FINAL_AUDIT_SCHEMA.md` | `5ca7191fc2b166ffebd328fa251dfd920167bc1269bc7c8108ace582c238b44b` | `5ca7191fc2b166ffebd328fa251dfd920167bc1269bc7c8108ace582c238b44b` | None |

`EXPORT_MANIFEST.json` records the same source-to-public hashes and the hash of this README. This directory is intended for `reviews/initial100/feedback_filter/` in the anonymous supplement. The documents can be inspected directly; they require no private workbook or unpublished file.
