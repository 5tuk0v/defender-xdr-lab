# mde_client_onboard

Onboards the explicitly selected disposable Windows client to Microsoft
Defender for Endpoint using the Windows 10 and 11 local script downloaded from
the Defender portal. The role validates local `OnboardingState=1` and a running
`Sense` service. Portal convergence is the following operator validation gate.

## Setup

Verify the selected test user has an enabled qualifying MDE entitlement. In
the Defender portal, download the **Windows 10 and 11** local onboarding package
and extract `WindowsDefenderATPLocalOnboardingScript.cmd`.

Use the WKS02 staging procedure in [Client MDE](../../../docs/labs/client-mde.md#stage-wks02-onboarding),
[Standard](../../../docs/labs/standard.md#stage-wks02-onboarding), or
[Complete](../../../docs/labs/complete.md#stage-wks02-onboarding) to place the
script outside installed roles in the protected staging directory.

Treat the package as protected service material: keep it out of Git, Source
archives, range YAML, templates, reports, and logs. The role stages it in the
guest, suppresses command output, executes it, and removes the guest copy even
on failure.

The role validates an existing healthy onboarding, reports `not_configured`
when the script is absent, or performs onboarding when the script is present.
Assigning the role to a host and placing the protected artifact are the
operator gates.

The selected runbook owns cloud acceptance and retired-device cleanup.
