# mde_windows_host_prep

Prepares a Windows host's Microsoft Defender Antivirus components before any
Azure Arc or direct Microsoft Defender for Endpoint onboarding path runs.

The role:

- downloads Microsoft's current x64 KB4052623 `updateplatform.exe` package;
- verifies a valid Microsoft Corporation Authenticode signature before
  execution;
- executes Microsoft's current package and records its SHA-256 identity;
- refreshes signatures only when the engine or security intelligence is below
  Microsoft's documented streamlined-connectivity minimum;
- validates that the active platform did not regress and meets Microsoft's
  documented minimum versions; and
- removes the downloaded package in every success or failure path.

The monthly package URL is intentionally not pinned to a build because the
role's selected state is Microsoft's current signed x64 package at deployment
time. Its file version identifies Microsoft's update stub rather than the
platform payload, so the selected state is validated from the active Defender
versions after execution. A second immediate application reports unchanged
when those versions remain the same.

Its scope ends after local Defender version validation. Arc or direct MDE
onboarding and cloud-health validation follow in their dedicated roles and
operator gates. A current platform removes a demonstrated prerequisite gap;
it is not presented as a proven cure for the recurring SENSE Event 406 issue.

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `mde_windows_host_prep_enabled` | `true` | Apply the local Defender preparation |

Microsoft reference: [Manage Defender Antivirus protection update sources](https://learn.microsoft.com/en-us/defender-endpoint/manage-protection-updates-microsoft-defender-antivirus#enable-platform-updates-using-unc-share).
