# sample_submission_sinkhole

Manages an exact-name list of public-analysis and sample-submission domains in
the Windows `hosts` file. Entries use `0.0.0.0` and a role-owned marker so
changes and cleanup preserve unrelated file content.

## Variables

- `sample_submission_sinkhole_enabled` (default `true`)
- `sample_submission_sinkhole_additional_domains` (default `[]`)
- `sample_submission_sinkhole_excluded_domains` (default `[]`)

The additional and exclusion lists customize the canonical 17-domain set
without changing the role. Disabling the role removes its marked entries.
Reapplying an already-correct set reports unchanged.

This exact-name safeguard complements broader network controls.
